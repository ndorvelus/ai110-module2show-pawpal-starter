from datetime import date, timedelta

from pawpal_system import Owner, Pet, Schedule, Task


def test_mark_complete_changes_status():
    task = Task("Morning walk", "exercise", 30, "high", "daily")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age=4)
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task("Morning walk", "exercise", 30, "high", "daily"))
    assert len(pet.get_tasks()) == 1

    pet.add_task(Task("Brush coat", "grooming", 20, "low", "weekly"))
    assert len(pet.get_tasks()) == 2


def test_sort_by_time_is_chronological_with_untimed_last_and_empty_pet_ok():
    owner = Owner(name="Sam", available_minutes=120)
    buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=4)
    empty = Pet(name="Ghost", species="cat", breed="Tabby", age=2)  # no tasks
    owner.add_pet(buddy)
    owner.add_pet(empty)
    buddy.add_task(Task("Evening walk", "exercise", 30, "high", "daily", time="18:00"))
    buddy.add_task(Task("Anytime play", "play", 10, "low", "daily"))  # untimed
    buddy.add_task(Task("Breakfast", "feeding", 10, "high", "daily", time="07:30"))

    schedule = Schedule(date.today(), owner)

    assert [t.title for t in schedule.sort_by_time()] == [
        "Breakfast",
        "Evening walk",
        "Anytime play",
    ]
    assert schedule.filter_tasks(pet_name="Ghost") == []
    assert Schedule(date.today(), Owner("Nobody", 60)).sort_by_time() == []


def test_completing_recurring_task_creates_next_occurrence():
    pet = Pet(name="Buddy", species="dog", breed="Labrador", age=4)
    due = date(2026, 1, 31)
    daily = Task("Walk", "exercise", 30, "high", "daily", due_date=due)
    weekly = Task("Bath", "grooming", 20, "low", "weekly", due_date=due)
    once = Task("Vet visit", "health", 60, "high", "once", due_date=due)
    for t in (daily, weekly, once):
        pet.add_task(t)

    next_daily = pet.complete_task(daily)
    next_weekly = pet.complete_task(weekly)
    next_once = pet.complete_task(once)

    assert daily.completed is True
    assert next_daily.completed is False
    assert next_daily.due_date == due + timedelta(days=1)  # crosses month end
    assert next_daily.pet_name == "Buddy"
    assert next_weekly.due_date == due + timedelta(weeks=1)
    assert next_once is None
    assert len(pet.get_tasks()) == 5  # 3 originals + 2 new occurrences


def test_same_time_tasks_are_flagged_across_pets_but_not_when_completed():
    owner = Owner(name="Sam", available_minutes=120)
    buddy = Pet(name="Buddy", species="dog", breed="Labrador", age=4)
    whiskers = Pet(name="Whiskers", species="cat", breed="Siamese", age=3)
    owner.add_pet(buddy)
    owner.add_pet(whiskers)
    today = date(2026, 1, 5)
    walk = Task("Walk", "exercise", 30, "high", "daily", time="08:00", due_date=today)
    feed = Task("Feed", "feeding", 10, "high", "daily", time="08:00", due_date=today)
    buddy.add_task(walk)
    whiskers.add_task(feed)
    buddy.add_task(Task("Nap", "rest", 5, "low", "daily", time="09:00", due_date=today))
    schedule = Schedule(today, owner)

    warnings = schedule.time_conflict_warnings()
    assert len(warnings) == 1
    assert "08:00" in warnings[0] and "Buddy" in warnings[0] and "Whiskers" in warnings[0]

    feed.mark_complete()  # a finished task no longer clashes
    assert schedule.time_conflict_warnings() == []
