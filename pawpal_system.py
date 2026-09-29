"""
PawPal+ logic layer.

Backend classes for PawPal+: Owner, Pet, Task, and Scheduler.
Mirrors diagrams/uml.mmd. No scheduling logic implemented yet (stubs only).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str = ""
    recurrence: str = ""

    def edit(self, **fields) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task: Task) -> None:
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def update_preferences(self, prefs: dict) -> None:
        raise NotImplementedError


class Scheduler:
    def __init__(self, available_minutes: int):
        self.available_minutes = available_minutes

    def generate_plan(self, tasks: list[Task]) -> list:
        raise NotImplementedError

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def filter_tasks(self, tasks: list[Task]) -> list[Task]:
        raise NotImplementedError

    def explain_plan(self, plan: list) -> str:
        raise NotImplementedError
