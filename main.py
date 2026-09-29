"""
Temporary testing ground for pawpal_system.py.

Run with: python main.py
"""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    mochi = Pet("Mochi", "dog", breed="Golden Retriever")
    mochi.add_task(Task("Morning walk", 30, "high"))
    mochi.add_task(Task("Feeding", 10, "high"))

    luna = Pet("Luna", "cat")
    luna.add_task(Task("Litter box", 5, "high"))

    jordan = Owner("Jordan", pets=[mochi, luna])

    scheduler = Scheduler(available_minutes=60)
    plan = scheduler.generate_plan_for_owner(jordan)

    print("Today's Schedule")
    print(scheduler.explain_plan(plan))


if __name__ == "__main__":
    main()
