"""Demo script: build an owner with two pets and print today's schedule."""

from datetime import date

from pawpal_system import Owner, Pet, Schedule, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=60, preferences=["mornings"])

    buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=4)
    whiskers = Pet(name="Whiskers", species="cat", breed="Siamese", age=2)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    buddy.add_task(Task("Morning walk", "exercise", 30, "high", "daily"))
    buddy.add_task(Task("Brush coat", "grooming", 20, "low", "weekly"))
    whiskers.add_task(Task("Feed breakfast", "feeding", 10, "high", "daily"))
    whiskers.add_task(Task("Play with laser", "enrichment", 15, "medium", "daily"))

    schedule = Schedule(day=date.today(), owner=owner)
    schedule.generate_plan()

    print("=" * 40)
    print(f"Today's Schedule - {schedule.day:%A, %B %d, %Y}")
    print("=" * 40)
    print(schedule.explain_plan())


if __name__ == "__main__":
    main()
