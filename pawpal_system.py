"""PawPal+ domain model: Task, Pet, Owner and Schedule (see diagrams/uml.mmd)."""

from dataclasses import dataclass, field
from datetime import date

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False

    def __post_init__(self) -> None:
        """Validate duration and priority when a task is created."""
        self._validate(self.duration_minutes, self.priority)

    @staticmethod
    def _validate(duration_minutes: int, priority: str) -> None:
        """Raise ValueError if duration is not positive or priority is unknown."""
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")
        if priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def update(self, duration_minutes: int, priority: str) -> None:
        """Change the task's duration and priority after validating both."""
        self._validate(duration_minutes, priority)
        self.duration_minutes = duration_minutes
        self.priority = priority


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet, ignoring tasks it doesn't have."""
        if task in self.tasks:
            self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner, ignoring pets they don't have."""
        if pet in self.pets:
            self.pets.remove(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class Schedule:
    """Builds a daily plan from an owner's pending tasks within their time budget."""

    def __init__(self, day: date, owner: Owner) -> None:
        """Create an empty schedule for an owner on a given day."""
        self.day = day
        self.owner = owner
        self.planned_tasks: list[Task] = []
        self.skipped_tasks: list[Task] = []

    def sort_by_priority(self) -> list[Task]:
        """Pending tasks, highest priority first, shorter tasks first within a tier."""
        pending = [t for t in self.owner.get_all_tasks() if not t.completed]
        return sorted(
            pending, key=lambda t: (PRIORITY_RANK[t.priority], t.duration_minutes)
        )

    def generate_plan(self) -> list[Task]:
        """Greedily fit tasks by priority into the owner's available minutes."""
        self.planned_tasks = []
        self.skipped_tasks = []
        remaining = self.owner.available_minutes
        for task in self.sort_by_priority():
            if task.duration_minutes <= remaining:
                self.planned_tasks.append(task)
                remaining -= task.duration_minutes
            else:
                self.skipped_tasks.append(task)
        return self.planned_tasks

    def detect_conflicts(self) -> list[Task]:
        """Pending tasks that cannot fit in the owner's available time."""
        self.generate_plan()
        return list(self.skipped_tasks)

    def total_duration(self) -> int:
        """Total minutes of the currently planned tasks."""
        return sum(t.duration_minutes for t in self.planned_tasks)

    def explain_plan(self) -> str:
        """Describe the planned and skipped tasks as readable text."""
        if not self.planned_tasks and not self.skipped_tasks:
            return f"No pending tasks for {self.day}."
        lines = [
            f"Plan for {self.owner.name} on {self.day} "
            f"({self.total_duration()}/{self.owner.available_minutes} min used):"
        ]
        for t in self.planned_tasks:
            lines.append(
                f"- {t.title} ({t.duration_minutes} min, {t.priority} priority)"
            )
        if self.skipped_tasks:
            lines.append("Skipped (not enough time):")
            for t in self.skipped_tasks:
                lines.append(
                    f"- {t.title} ({t.duration_minutes} min, {t.priority} priority)"
                )
        return "\n".join(lines)
