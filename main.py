"""Demo script: build an owner with two pets and print today's schedule."""

from datetime import date

from pawpal_system import Owner, Pet, Schedule, Task


def main() -> None:
    owner = Owner(name="Jordan", available_minutes=60, preferences=["mornings"])

    buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=4)
    whiskers = Pet(name="Whiskers", species="cat", breed="Siamese", age=2)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # Added deliberately out of time order to exercise sort_by_time().
    buddy.add_task(Task("Brush coat", "grooming", 20, "low", "weekly", time="18:30"))
    whiskers.add_task(Task("Play with laser", "enrichment", 15, "medium", "daily", time="12:00"))
    buddy.add_task(Task("Morning walk", "exercise", 30, "high", "daily", time="07:15"))
    whiskers.add_task(Task("Feed breakfast", "feeding", 10, "high", "daily", time="07:00"))
    whiskers.add_task(Task("Vet reminder", "health", 5, "low", "weekly"))  # no time
    whiskers.tasks[0].mark_complete()  # Play with laser is done

    schedule = Schedule(day=date.today(), owner=owner)
    schedule.generate_plan()

    print("=" * 40)
    print(f"Today's Schedule - {schedule.day:%A, %B %d, %Y}")
    print("=" * 40)
    print(schedule.explain_plan())

    def show(label: str, tasks: list[Task]) -> None:
        print(f"\n{label}")
        for t in tasks:
            mark = "x" if t.completed else " "
            print(f"  [{mark}] {t.time or '--:--'}  {t.title} ({t.pet_name})")

    # Two deliberate clashes: same pet (Buddy) and different pets, both at 09:00.
    buddy.add_task(Task("Vet visit", "health", 30, "high", "weekly", time="09:00"))
    buddy.add_task(Task("Training", "exercise", 20, "medium", "daily", time="09:00"))
    whiskers.add_task(Task("Medication", "health", 5, "high", "daily", time="09:00"))
    print("\nConflict check:")
    for w in schedule.time_conflict_warnings() or ["No conflicts."]:
        print(f"  {w}")

    print("\nRecurrence:")
    walk = buddy.tasks[1]
    walk.due_date = date.today()
    nxt = buddy.complete_task(walk)
    print(f"  Completed '{walk.title}' ({walk.frequency}) -> next due {nxt.due_date}")
    groom = buddy.tasks[0]
    groom.due_date = date.today()
    nxt = buddy.complete_task(groom)
    print(f"  Completed '{groom.title}' ({groom.frequency}) -> next due {nxt.due_date}")
    vet = whiskers.tasks[-1]
    print(f"  Completed 'Vet reminder' ({vet.frequency})")
    whiskers.complete_task(vet)

    show("All tasks, as added:", owner.get_all_tasks())
    show("Sorted by time:", schedule.sort_by_time())
    show("Pet = Buddy:", schedule.filter_tasks(pet_name="Buddy"))
    show("Pending only:", schedule.filter_tasks(completed=False))
    show("Whiskers, completed:", schedule.filter_tasks(pet_name="Whiskers", completed=True))
    show("Whiskers pending, sorted by time:",
         schedule.sort_by_time(schedule.filter_tasks("Whiskers", False)))


if __name__ == "__main__":
    main()
