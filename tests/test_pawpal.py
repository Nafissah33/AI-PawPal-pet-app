"""Tests for pawpal_system.py."""

from datetime import date

from pawpal_system import Task, Pet, Owner, Scheduler


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


def test_sort_tasks_orders_by_priority_then_by_time():
    scheduler = Scheduler(available_minutes=120)
    evening_walk = Task("Evening walk", 20, "high", preferred_time="18:00")
    morning_walk = Task("Morning walk", 20, "high", preferred_time="07:00")
    grooming = Task("Grooming", 15, "medium", preferred_time="10:00")
    play_time = Task("Play time", 30, "low")

    ordered = scheduler.sort_tasks([evening_walk, grooming, morning_walk, play_time])

    assert [t.title for t in ordered] == ["Morning walk", "Evening walk", "Grooming", "Play time"]


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


def test_completing_weekly_task_schedules_due_date_a_week_later():
    pet = Pet("Mochi", "dog")
    weekly_task = Task("Grooming", 30, "medium", recurrence="weekly")
    pet.add_task(weekly_task)

    next_task = pet.complete_task(weekly_task, completed_on=date(2026, 9, 29))

    assert next_task is not None
    assert next_task.due_date == "2026-10-06"
    assert next_task.completed is False


def test_scheduler_excludes_tasks_not_yet_due():
    scheduler = Scheduler(available_minutes=60)
    not_due_yet = Task("Grooming", 30, "medium", due_date="2026-10-06")
    due_today = Task("Feeding", 10, "high")

    plan_today = scheduler.generate_plan([not_due_yet, due_today], today=date(2026, 9, 29))
    scheduled_titles_today = [entry["task"].title for entry in plan_today]
    assert "Feeding" in scheduled_titles_today
    assert "Grooming" not in scheduled_titles_today

    plan_next_week = scheduler.generate_plan([not_due_yet, due_today], today=date(2026, 10, 6))
    scheduled_titles_next_week = [entry["task"].title for entry in plan_next_week]
    assert "Grooming" in scheduled_titles_next_week


def test_scheduler_flags_duplicate_times():
    scheduler = Scheduler(available_minutes=60)
    walk = Task("Walk", 15, "high", preferred_time="08:00")
    feeding = Task("Feeding", 10, "high", preferred_time="08:00")
    grooming = Task("Grooming", 20, "medium", preferred_time="09:00")

    conflicts = scheduler.detect_conflicts([walk, feeding, grooming])

    assert len(conflicts) == 1
    conflicting_ids = {conflicts[0][0].id, conflicts[0][1].id}
    assert conflicting_ids == {walk.id, feeding.id}


def test_find_next_available_slot_skips_busy_time():
    scheduler = Scheduler(available_minutes=120)
    existing_plan = [{"start_time": "08:00", "end_time": "08:30"}]

    slot = scheduler.find_next_available_slot(existing_plan, duration_minutes=15, preferred_time="08:00")

    assert slot == "08:30"


def test_save_and_load_json_round_trips_owner(tmp_path):
    owner = Owner("Jordan")
    pet = Pet("Mochi", "dog", breed="Golden Retriever")
    pet.add_task(Task("Morning walk", 30, "high", preferred_time="08:00"))
    owner.add_pet(pet)

    filepath = tmp_path / "data.json"
    owner.save_to_json(str(filepath))
    loaded = Owner.load_from_json(str(filepath))

    assert loaded.name == owner.name
    assert len(loaded.pets) == 1
    assert loaded.pets[0].name == "Mochi"
    assert loaded.pets[0].breed == "Golden Retriever"
    assert len(loaded.pets[0].tasks) == 1
    loaded_task = loaded.pets[0].tasks[0]
    assert loaded_task.title == "Morning walk"
    assert loaded_task.preferred_time == "08:00"
    assert loaded_task.id == pet.tasks[0].id


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
