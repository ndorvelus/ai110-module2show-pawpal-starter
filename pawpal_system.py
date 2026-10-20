"""PawPal+ domain model: Task, Pet, Owner and Schedule (see diagrams/uml.mmd)."""

import json
from dataclasses import asdict, dataclass, field, replace
from datetime import date, datetime, timedelta
from pathlib import Path

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}

RECURRENCE_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    frequency: str
    completed: bool = False
    time: str = ""  # "HH:MM" start time; empty means unscheduled
    pet_name: str = ""  # set by Pet.add_task
    due_date: date | None = None  # None is treated as today when recurring

    def __post_init__(self) -> None:
        """Validate duration, priority and time when a task is created."""
        self._validate(self.duration_minutes, self.priority)
        if self.time:
            try:
                datetime.strptime(self.time, "%H:%M")
            except ValueError:
                raise ValueError("time must be in HH:MM format") from None

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

    def next_occurrence(self) -> "Task | None":
        """Build the next occurrence of a recurring task.

        Uses RECURRENCE_STEP to look up how far to advance: one day for "daily",
        one week for "weekly". The new date is counted from this task's due_date,
        or from today if due_date is unset.

        Returns:
            A pending copy of this task with the advanced due_date, or None if
            the frequency is not recurring. The original task is not modified.
        """
        step = RECURRENCE_STEP.get(self.frequency)
        if step is None:
            return None
        base = self.due_date or date.today()
        return replace(self, completed=False, due_date=base + step)

    def update(self, duration_minutes: int, priority: str) -> None:
        """Change the task's duration and priority after validating both."""
        self._validate(duration_minutes, priority)
        self.duration_minutes = duration_minutes
        self.priority = priority

    def to_dict(self) -> dict:
        """Convert to a JSON-safe dict; the only non-JSON field, due_date, becomes ISO text."""
        data = asdict(self)
        data["due_date"] = self.due_date.isoformat() if self.due_date else None
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Rebuild a Task from to_dict() output, re-running validation."""
        data = dict(data)
        if data.get("due_date"):
            data["due_date"] = date.fromisoformat(data["due_date"])
        return cls(**data)


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list and tag it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet, ignoring tasks it doesn't have."""
        if task in self.tasks:
            self.tasks.remove(task)

    def complete_task(self, task: Task) -> Task | None:
        """Complete a task and schedule its next occurrence if it recurs.

        Args:
            task: A task belonging to this pet.

        Returns:
            The newly added next occurrence, or None if the task does not recur.
        """
        task.mark_complete()
        following = task.next_occurrence()
        if following is not None:
            self.add_task(following)
        return following

    def get_tasks(self) -> list[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def to_dict(self) -> dict:
        """Convert this pet and its tasks to a JSON-safe dict."""
        data = asdict(self)
        data["tasks"] = [t.to_dict() for t in self.tasks]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Pet":
        """Rebuild a Pet, and its tasks, from to_dict() output."""
        pet = cls(**{k: v for k, v in data.items() if k != "tasks"})
        for task_data in data.get("tasks", []):
            pet.add_task(Task.from_dict(task_data))
        return pet


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

    def to_dict(self) -> dict:
        """Convert this owner, their pets and every task to a JSON-safe dict."""
        data = asdict(self)
        data["pets"] = [p.to_dict() for p in self.pets]
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Owner":
        """Rebuild an Owner, with pets and tasks, from to_dict() output."""
        owner = cls(**{k: v for k, v in data.items() if k != "pets"})
        for pet_data in data.get("pets", []):
            owner.add_pet(Pet.from_dict(pet_data))
        return owner

    def save_to_json(self, path: str | Path = "data.json") -> None:
        """Write this owner, their pets and tasks to a JSON file.

        The file is written to a temporary sibling first and then renamed over the
        target, so a crash mid-write cannot leave a half-written data file.
        """
        path = Path(path)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(json.dumps(self.to_dict(), indent=2))
        tmp.replace(path)

    @classmethod
    def load_from_json(cls, path: str | Path = "data.json") -> "Owner":
        """Read an Owner saved by save_to_json.

        Raises:
            FileNotFoundError: if the file does not exist yet (first run).
            ValueError: if the file is not valid JSON or holds invalid task data.
        """
        try:
            return cls.from_dict(json.loads(Path(path).read_text()))
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            raise ValueError(f"{path} is not a valid PawPal+ data file: {exc}") from exc


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

    def sort_by_priority_and_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Order tasks by priority first (high to low), then by start time.

        Within a priority tier, tasks run chronologically and untimed tasks go last.
        Python's sort is stable, so ties keep their input order.

        Args:
            tasks: Tasks to sort; defaults to the owner's pending tasks.

        Returns:
            A new sorted list. The input is not modified.
        """
        if tasks is None:
            tasks = [t for t in self.owner.get_all_tasks() if not t.completed]
        return sorted(
            tasks, key=lambda t: (PRIORITY_RANK[t.priority], t.time == "", t.time)
        )

    def sort_by_time(self, tasks: list[Task] | None = None) -> list[Task]:
        """Order tasks chronologically by their "HH:MM" time.

        Zero-padded "HH:MM" strings sort chronologically as plain strings, so the
        key only needs to push untimed tasks to the end: (time == "", time).
        Python's sort is stable, so tasks with equal times keep their input order.

        Args:
            tasks: Tasks to sort; defaults to all of the owner's tasks.

        Returns:
            A new sorted list. The input is not modified.
        """
        if tasks is None:
            tasks = self.owner.get_all_tasks()
        # Zero-padded "HH:MM" strings sort chronologically as plain strings.
        return sorted(tasks, key=lambda t: (t.time == "", t.time))

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Select tasks by pet name and/or completion status.

        A criterion left as None is ignored, so both None returns every task.

        Args:
            pet_name: Keep only tasks belonging to the pet with this name.
            completed: True for finished tasks, False for pending ones.

        Returns:
            A new list of the owner's matching tasks, in their stored order.
        """
        return [
            t
            for t in self.owner.get_all_tasks()
            if (pet_name is None or t.pet_name == pet_name)
            and (completed is None or t.completed == completed)
        ]

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

    def time_conflict_warnings(self) -> list[str]:
        """Warn about pending tasks that start at the same time on the same day.

        Lightweight check: tasks are bucketed by (due_date, time) in one pass, and
        any bucket with more than one task yields a message. It never raises, and
        it covers same-pet and cross-pet clashes alike. Tasks without a time are
        ignored, and overlapping-but-different start times are not detected.

        Returns:
            One message per clashing time slot, ordered by time; empty if none.
        """
        buckets: dict[tuple[date | None, str], list[Task]] = {}
        for t in self.owner.get_all_tasks():
            if t.time and not t.completed:
                buckets.setdefault((t.due_date, t.time), []).append(t)

        warnings = []
        for (_, at), tasks in sorted(buckets.items(), key=lambda kv: kv[0][1]):
            if len(tasks) < 2:
                continue
            pets = sorted({t.pet_name for t in tasks})
            kind = f"pet: {pets[0]}" if len(pets) == 1 else f"pets: {', '.join(pets)}"
            names = ", ".join(f"'{t.title}' ({t.pet_name})" for t in tasks)
            warnings.append(f"Warning: {len(tasks)} tasks at {at} ({kind}): {names}")
        return warnings

    def find_next_available_slot(
        self, duration_minutes: int, earliest: str = "08:00", latest: str = "20:00"
    ) -> str | None:
        """Find the first start time where a task of this length fits without overlap.

        Collects the busy intervals of pending timed tasks that fall on this
        schedule's day (a task with no due_date counts as today), sorts them, and
        sweeps a cursor from `earliest`, jumping past each interval that blocks it.
        The first gap of at least `duration_minutes` before `latest` wins. This is
        O(n log n) in the number of timed tasks and, unlike time_conflict_warnings,
        accounts for task durations, not just identical start times.

        Args:
            duration_minutes: Length of the task to place; must be positive.
            earliest: "HH:MM" start of the window to search.
            latest: "HH:MM" end of the window; the task must finish by then.

        Returns:
            The start time as "HH:MM", or None if no gap is big enough.
        """
        if duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

        def to_minutes(hhmm: str) -> int:
            parsed = datetime.strptime(hhmm, "%H:%M")
            return parsed.hour * 60 + parsed.minute

        busy = sorted(
            (to_minutes(t.time), to_minutes(t.time) + t.duration_minutes)
            for t in self.owner.get_all_tasks()
            if t.time and not t.completed and t.due_date in (None, self.day)
        )
        cursor, end_of_day = to_minutes(earliest), to_minutes(latest)
        for start, end in busy:
            if start - cursor >= duration_minutes:
                break
            cursor = max(cursor, end)
        if end_of_day - cursor >= duration_minutes:
            return f"{cursor // 60:02d}:{cursor % 60:02d}"
        return None

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
