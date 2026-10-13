"""PawPal+ domain model: class skeletons based on diagrams/uml.mmd."""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def update(self, duration_minutes: int, priority: str) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet: Pet) -> None:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass


class Schedule:
    def __init__(self, day: date, owner: Owner) -> None:
        self.day = day
        self.owner = owner
        self.planned_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def generate_plan(self) -> list[Task]:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass

    def detect_conflicts(self) -> list[Task]:
        pass

    def total_duration(self) -> int:
        pass

    def explain_plan(self) -> str:
        pass
