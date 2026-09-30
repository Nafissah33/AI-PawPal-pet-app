import os

import streamlit as st

from pawpal_system import DEFAULT_DATA_FILE, PRIORITY_ICONS, Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Only build the Owner (and its Pet) once per session — otherwise every
# rerun (e.g. clicking a button) would wipe it out and start over. If a
# data.json from a previous run exists, load it instead of starting fresh.
if "owner" not in st.session_state:
    if os.path.exists(DEFAULT_DATA_FILE):
        st.session_state.owner = Owner.load_from_json(DEFAULT_DATA_FILE)
    else:
        st.session_state.owner = Owner(name=owner_name, pets=[Pet(name=pet_name, species=species)])

owner: Owner = st.session_state.owner

save_col, load_col = st.columns(2)
with save_col:
    if st.button("💾 Save data"):
        owner.save_to_json(DEFAULT_DATA_FILE)
        st.success(f"Saved to {DEFAULT_DATA_FILE}.")
with load_col:
    if st.button("📂 Reload from file"):
        if os.path.exists(DEFAULT_DATA_FILE):
            st.session_state.owner = Owner.load_from_json(DEFAULT_DATA_FILE)
            st.rerun()
        else:
            st.warning(f"No {DEFAULT_DATA_FILE} found yet — save first.")

st.divider()

st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    new_pet_name = st.text_input("New pet's name")
    new_species = st.selectbox("New pet's species", ["dog", "cat", "other"], key="new_species")
    new_breed = st.text_input("Breed (optional)")
    if st.form_submit_button("Add pet") and new_pet_name:
        owner.add_pet(Pet(name=new_pet_name, species=new_species, breed=new_breed))
        st.success(f"Added {new_pet_name}.")

pet_names = [p.name for p in owner.pets]
selected_pet_name = st.selectbox("Manage tasks for", pet_names)
pet: Pet = next(p for p in owner.pets if p.name == selected_pet_name)

st.markdown("### Tasks")
st.caption(f"Tasks for {pet.name}.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    preferred_time = st.text_input("Preferred time (HH:MM, optional)", value="")
with col5:
    recurrence = st.selectbox("Recurrence", ["", "daily", "weekly"])

if st.button("Add task"):
    pet.add_task(
        Task(
            title=task_title,
            duration_minutes=int(duration),
            priority=priority,
            recurrence=recurrence,
            preferred_time=preferred_time or None,
        )
    )
    st.success(f"Added \"{task_title}\" for {pet.name}.")

tasks = pet.get_tasks()
if tasks:
    st.write("Current tasks:")
    header = st.columns([3, 2, 2, 2, 2])
    for col, label in zip(header, ["Task", "Duration", "Priority", "Preferred time", ""]):
        col.markdown(f"**{label}**")
    for t in tasks:
        row = st.columns([3, 2, 2, 2, 2])
        row[0].write(f"~~{t.title}~~" if t.completed else t.title)
        row[1].write(f"{t.duration_minutes} min")
        row[2].write(PRIORITY_ICONS.get(t.priority, t.priority))
        row[3].write(t.preferred_time or "—")
        if t.completed:
            row[4].write("✅ done")
        elif row[4].button("Mark complete", key=f"complete-{t.id}"):
            pet.complete_task(t)
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
available_minutes = st.number_input("Minutes available today", min_value=1, max_value=600, value=60)
scheduler = Scheduler(available_minutes=int(available_minutes))

all_tasks = owner.get_all_tasks()
pet_name_by_task_id = {t.id: p.name for p in owner.pets for t in p.get_tasks()}

conflicts = scheduler.detect_conflicts(all_tasks)
if conflicts:
    st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) found — you may want to adjust these times:")
    for task_a, task_b in conflicts:
        pet_a = pet_name_by_task_id.get(task_a.id, "?")
        pet_b = pet_name_by_task_id.get(task_b.id, "?")
        task_a_slot = scheduler.generate_plan([task_a], start_time=task_a.preferred_time)
        suggested_time = scheduler.find_next_available_slot(
            task_a_slot, task_b.duration_minutes, preferred_time=task_b.preferred_time
        )
        st.warning(
            f"**{task_a.preferred_time}** — \"{task_a.title}\" ({pet_a}) and "
            f"\"{task_b.title}\" ({pet_b}) are both set for this time. "
            f"Try moving \"{task_b.title}\" to **{suggested_time}** instead."
        )

with st.expander("All tasks, sorted by priority"):
    sorted_tasks = scheduler.sort_tasks(all_tasks)
    if sorted_tasks:
        st.table(
            [
                {
                    "pet": pet_name_by_task_id.get(t.id, ""),
                    "title": t.title,
                    "priority": PRIORITY_ICONS.get(t.priority, t.priority),
                    "duration_minutes": t.duration_minutes,
                }
                for t in sorted_tasks
            ]
        )
    else:
        st.info("No tasks yet.")

if st.button("Generate schedule"):
    plan = scheduler.generate_plan_for_owner(owner)
    if plan:
        st.success(f"Schedule generated for {owner.name}'s pets!")
        st.table(
            [
                {
                    "start": entry["start_time"],
                    "end": entry["end_time"],
                    "pet": pet_name_by_task_id.get(entry["task"].id, ""),
                    "task": entry["task"].title,
                    "reason": entry["reason"],
                }
                for entry in plan
            ]
        )
        total_used = sum(entry["task"].duration_minutes for entry in plan)
        st.caption(f"Total time used: {total_used}/{available_minutes} minutes.")
    else:
        st.info(scheduler.explain_plan(plan))
