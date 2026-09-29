"""Tests for pawpal_system.py."""

from pawpal_system import Task, Pet, Scheduler


def test_sort_tasks_returns_chronological_order():
    scheduler = Scheduler(available_minutes=120)
    tasks = [
        Task("Play time", 20, "medium"),
        Task("Feeding", 10, "high"),
        Task("Litter box", 5, "high"),
    ]

    plan = scheduler.generate_plan(tasks)
    start_times = [entry["start_time"] for entry in plan]

    assert start_times == sorted(start_times)


def test_completing_daily_task_creates_next_occurrence():
    pet = Pet("Mochi", "dog")
    daily_task = Task("Feeding", 10, "high", recurrence="daily")
    pet.add_task(daily_task)

    next_task = pet.complete_task(daily_task)

    assert daily_task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.title == daily_task.title
    assert next_task.id != daily_task.id
    assert next_task in pet.get_tasks()


def test_scheduler_flags_duplicate_times():
    scheduler = Scheduler(available_minutes=60)
    walk = Task("Walk", 15, "high", preferred_time="08:00")
    feeding = Task("Feeding", 10, "high", preferred_time="08:00")
    grooming = Task("Grooming", 20, "medium", preferred_time="09:00")

    conflicts = scheduler.detect_conflicts([walk, feeding, grooming])

    assert len(conflicts) == 1
    conflicting_ids = {conflicts[0][0].id, conflicts[0][1].id}
    assert conflicting_ids == {walk.id, feeding.id}


def test_mark_complete_changes_status():
    task = Task("Morning walk", 30, "high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet("Mochi", "dog")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Feeding", 10, "high"))

    assert len(pet.get_tasks()) == 1
