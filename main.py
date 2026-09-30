"""
Temporary testing ground for pawpal_system.py.

Run with: python main.py
"""

from tabulate import tabulate

from pawpal_system import PRIORITY_ICONS, Task, Pet, Owner, Scheduler

CATEGORY_ICONS = {
    "walk": "🚶 Walk",
    "feeding": "🍽️ Feeding",
    "litter": "🐾 Litter",
    "grooming": "🧼 Grooming",
    "play": "🎾 Play",
}


def _category_label(category: str) -> str:
    return CATEGORY_ICONS.get(category, f"📌 {category}" if category else "📌 General")


def _status_label(task: Task) -> str:
    return "✅ Done" if task.completed else "⏳ Pending"


def print_task_table(tasks: list[Task], title: str) -> None:
    print(f"\n{title}")
    rows = [
        [
            _status_label(t),
            t.title,
            _category_label(t.category),
            PRIORITY_ICONS.get(t.priority, t.priority),
            f"{t.duration_minutes} min",
        ]
        for t in tasks
    ]
    print(tabulate(rows, headers=["Status", "Task", "Category", "Priority", "Duration"], tablefmt="rounded_outline"))


def print_schedule_table(plan: list[dict], available_minutes: int) -> None:
    rows = [
        [
            entry["start_time"],
            entry["end_time"],
            entry["task"].title,
            PRIORITY_ICONS.get(entry["task"].priority, entry["task"].priority),
            f"{entry['task'].duration_minutes} min",
        ]
        for entry in plan
    ]
    print(tabulate(rows, headers=["Start", "End", "Task", "Priority", "Duration"], tablefmt="rounded_outline"))
    total_used = sum(entry["task"].duration_minutes for entry in plan)
    print(f"\nTotal time used: {total_used}/{available_minutes} minutes.")


def main():
    mochi = Pet("Mochi", "dog", breed="Golden Retriever")
    mochi.add_task(Task("Morning walk", 30, "high", category="walk"))
    mochi.add_task(Task("Feeding", 10, "high", category="feeding"))

    luna = Pet("Luna", "cat")
    luna.add_task(Task("Litter box", 5, "high", category="litter"))

    jordan = Owner("Jordan", pets=[mochi, luna])

    scheduler = Scheduler(available_minutes=60)
    plan = scheduler.generate_plan_for_owner(jordan)

    print("Today's Schedule")
    print_schedule_table(plan, available_minutes=60)


def demo_priority_scheduling():
    """Show priority-first sorting, tie-broken by preferred time, not just duration."""
    scheduler = Scheduler(available_minutes=90)
    tasks = [
        Task("Evening walk", 20, "high", preferred_time="18:00", category="walk"),
        Task("Morning walk", 20, "high", preferred_time="07:00", category="walk"),
        Task("Grooming", 15, "medium", preferred_time="10:00", category="grooming"),
        Task("Play time", 30, "low", category="play"),
    ]

    print("\n--- Priority-Based Scheduling Demo ---")
    print("Sort order (priority first, then by preferred time):")
    for t in scheduler.sort_tasks(tasks):
        when = t.preferred_time or "no preferred time"
        print(f"  {PRIORITY_ICONS.get(t.priority, t.priority):<12} | {when:>17} | {t.title}")

    plan = scheduler.generate_plan(tasks)
    print()
    print_schedule_table(plan, available_minutes=90)

    # Demonstrate the status indicator by completing one task after scheduling.
    tasks[3].mark_complete()  # Play time
    print_task_table(tasks, 'Task list after marking "Play time" complete')


if __name__ == "__main__":
    main()
    demo_priority_scheduling()
