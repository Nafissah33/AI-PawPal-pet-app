import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

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
# rerun (e.g. clicking a button) would wipe it out and start over.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name, pets=[Pet(name=pet_name, species=species)])

owner: Owner = st.session_state.owner

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

if st.button("Add task"):
    pet.add_task(Task(title=task_title, duration_minutes=int(duration), priority=priority))

if pet.get_tasks():
    st.write("Current tasks:")
    st.table(
        [
            {"title": t.title, "duration_minutes": t.duration_minutes, "priority": t.priority}
            for t in pet.get_tasks()
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
available_minutes = st.number_input("Minutes available today", min_value=1, max_value=600, value=60)

if st.button("Generate schedule"):
    scheduler = Scheduler(available_minutes=int(available_minutes))
    plan = scheduler.generate_plan_for_owner(owner)
    st.text(scheduler.explain_plan(plan))
