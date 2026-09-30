"""
PawPal+ logic layer.

Backend classes for PawPal+: Owner, Pet, Task, and Scheduler.
Mirrors diagrams/uml.mmd.
"""

from __future__ import annotations

import dataclasses
import json
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

DEFAULT_START_TIME = "08:00"
DEFAULT_DATA_FILE = "data.json"
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
_RECURRENCE_INTERVAL_DAYS = {"daily": 1, "weekly": 7}
PRIORITY_ICONS = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def _next_due_date(recurrence: str, from_date: date) -> date | None:
    """Compute the next due date for a recurrence value, or None if it doesn't recur."""
    interval_days = _RECURRENCE_INTERVAL_DAYS.get(recurrence)
    if interval_days is None:
        return None
    return from_date + timedelta(days=interval_days)


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str = ""
    recurrence: str = ""
    preferred_time: str | None = None
    due_date: str | None = None
    completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def edit(self, **fields) -> None:
        """Update the given attributes in place, rejecting unknown field names."""
        valid_fields = {f.name for f in dataclasses.fields(self)}
        for name, value in fields.items():
            if name not in valid_fields:
                raise ValueError(f"Unknown Task field: {name!r}")
            setattr(self, name, value)

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark this task as not completed."""
        self.completed = False

    def to_dict(self) -> dict:
        """Convert this task to a plain, JSON-serializable dict."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Reconstruct a Task from a dict produced by to_dict()."""
        return cls(**data)


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet's task list by its id."""
        self.tasks = [t for t in self.tasks if t.id != task.id]

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def complete_task(self, task: Task, completed_on: date | None = None) -> Task | None:
        """Mark a task complete; if it recurs, schedule its next occurrence on the correct future date."""
        completed_on = completed_on or date.today()
        task.mark_complete()

        next_due = _next_due_date(task.recurrence, completed_on)
        if next_due is None:
            return None

        next_task = Task(
            title=task.title,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            category=task.category,
            recurrence=task.recurrence,
            preferred_time=task.preferred_time,
            due_date=next_due.isoformat(),
        )
        self.add_task(next_task)
        return next_task

    def to_dict(self) -> dict:
        """Convert this pet (and its tasks) to a plain, JSON-serializable dict."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Reconstruct a Pet (and its tasks) from a dict produced by to_dict()."""
        return cls(
            name=data["name"],
            species=data["species"],
            breed=data.get("breed", ""),
            tasks=[Task.from_dict(t) for t in data.get("tasks", [])],
        )


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def update_preferences(self, prefs: dict) -> None:
        """Merge the given preferences into this owner's existing preferences."""
        self.preferences.update(prefs)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Tasks across every pet this owner has, for scheduling all of them together."""
        return [task for pet in self.pets for task in pet.get_tasks()]

    def to_dict(self) -> dict:
        """Convert this owner (and all pets/tasks) to a plain, JSON-serializable dict."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Reconstruct an Owner (and all pets/tasks) from a dict produced by to_dict()."""
        return cls(
            name=data["name"],
            preferences=data.get("preferences", {}),
            pets=[Pet.from_dict(p) for p in data.get("pets", [])],
        )

    def save_to_json(self, filepath: str = DEFAULT_DATA_FILE) -> None:
        """Persist this owner, and all of their pets and tasks, to a JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = DEFAULT_DATA_FILE) -> "Owner":
        """Load an owner, and all of their pets and tasks, from a JSON file."""
        with open(filepath) as f:
            data = json.load(f)
        return cls.from_dict(data)


class Scheduler:
    def __init__(self, available_minutes: int):
        """Store the total minutes of time available to schedule tasks into."""
        self.available_minutes = available_minutes

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Highest priority first. Within the same priority, tasks with a set preferred_time
        are ordered chronologically; tasks without one are tie-broken by shortest duration."""
        return sorted(
            tasks,
            key=lambda t: (
                _PRIORITY_RANK.get(t.priority, len(_PRIORITY_RANK)),
                0 if t.preferred_time else 1,
                t.preferred_time or "",
                t.duration_minutes,
            ),
        )

    def filter_tasks(self, tasks: list[Task], today: date | None = None) -> list[Task]:
        """Greedily keep not-yet-completed, already-due tasks that still fit in the remaining time."""
        today = today or date.today()
        selected = []
        remaining = self.available_minutes
        for task in tasks:
            if task.completed:
                continue
            if task.due_date and date.fromisoformat(task.due_date) > today:
                continue
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes
        return selected

    def generate_plan(
        self, tasks: list[Task], start_time: str = DEFAULT_START_TIME, today: date | None = None
    ) -> list[dict]:
        """Sort and filter the given tasks, then lay them out sequentially starting at start_time."""
        ordered = self.sort_tasks(tasks)
        selected = self.filter_tasks(ordered, today=today)

        plan = []
        current = datetime.strptime(start_time, "%H:%M")
        for task in selected:
            end = current + timedelta(minutes=task.duration_minutes)
            plan.append(
                {
                    "task": task,
                    "start_time": current.strftime("%H:%M"),
                    "end_time": end.strftime("%H:%M"),
                    "reason": (
                        f"{task.priority} priority, {task.duration_minutes} min — "
                        "fit within the available time after higher/equal-priority tasks."
                    ),
                }
            )
            current = end
        return plan

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Flag pairs of tasks that share the same preferred_time."""
        by_time: dict[str, list[Task]] = {}
        for task in tasks:
            if not task.preferred_time:
                continue
            by_time.setdefault(task.preferred_time, []).append(task)

        conflicts = []
        for same_time_tasks in by_time.values():
            for i in range(len(same_time_tasks)):
                for j in range(i + 1, len(same_time_tasks)):
                    conflicts.append((same_time_tasks[i], same_time_tasks[j]))
        return conflicts

    def find_next_available_slot(
        self, plan: list[dict], duration_minutes: int, preferred_time: str | None = None
    ) -> str:
        """Find the earliest time (from preferred_time onward) that doesn't overlap any entry in plan."""
        candidate = datetime.strptime(preferred_time or DEFAULT_START_TIME, "%H:%M")

        busy = sorted(
            (datetime.strptime(entry["start_time"], "%H:%M"), datetime.strptime(entry["end_time"], "%H:%M"))
            for entry in plan
        )

        for busy_start, busy_end in busy:
            candidate_end = candidate + timedelta(minutes=duration_minutes)
            if candidate_end <= busy_start:
                break
            if candidate < busy_end:
                candidate = busy_end

        return candidate.strftime("%H:%M")

    def generate_plan_for_owner(
        self, owner: Owner, start_time: str = DEFAULT_START_TIME, today: date | None = None
    ) -> list[dict]:
        """Retrieve tasks across all of the owner's pets and build one combined plan from them."""
        return self.generate_plan(owner.get_all_tasks(), start_time=start_time, today=today)

    def explain_plan(self, plan: list[dict]) -> str:
        """Render a plan as a human-readable, multi-line summary string."""
        if not plan:
            return "No tasks were scheduled — either no tasks were given or none fit within the available time."

        lines = [f"Daily plan ({self.available_minutes} minutes available):"]
        for entry in plan:
            task = entry["task"]
            lines.append(f"  {entry['start_time']}-{entry['end_time']}  {task.title} — {entry['reason']}")
        total_used = sum(entry["task"].duration_minutes for entry in plan)
        lines.append(f"Total time used: {total_used}/{self.available_minutes} minutes.")
        return "\n".join(lines)
