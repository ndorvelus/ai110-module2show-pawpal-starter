from pawpal_system import Pet, Task


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
