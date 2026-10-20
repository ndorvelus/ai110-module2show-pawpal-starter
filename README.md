# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
========================================
Today's Schedule - Tuesday, October 13, 2026
========================================
Plan for Jordan on 2026-10-13 (55/60 min used):
- Feed breakfast (10 min, high priority)
- Morning walk (30 min, high priority)
- Play with laser (15 min, medium priority)
Skipped (not enough time):
- Brush coat (20 min, low priority)
```

## 🧪 Testing PawPal+

Requires Python 3.10+ (the code uses `X | None` type syntax).

```bash
python -m pytest
```

**What the tests cover** (`tests/tests_pawpal.py`):

- **Basics:** `mark_complete` flips a task's status, and `add_task` grows a pet's task list.
- **Sorting:** `sort_by_time` returns tasks in chronological order with untimed tasks last. A pet with no tasks and an owner with no pets both return empty results without errors.
- **Recurrence:** completing a daily task creates a pending copy due the next day (including across a month boundary). Weekly tasks advance 7 days, and one-off tasks create nothing.
- **Conflict detection:** two tasks at the same time are flagged, including across different pets. Tasks at different times and completed tasks are not.

Test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.6.0 -- /Users/nathan/.pyenv/versions/3.13.15/bin/python3
cachedir: .pytest_cache
rootdir: /Users/nathan/Documents/GitHub/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.14.2
collecting ... collected 5 items

tests/tests_pawpal.py::test_mark_complete_changes_status PASSED          [ 20%]
tests/tests_pawpal.py::test_add_task_increases_pet_task_count PASSED     [ 40%]
tests/tests_pawpal.py::test_sort_by_time_is_chronological_with_untimed_last_and_empty_pet_ok PASSED [ 60%]
tests/tests_pawpal.py::test_completing_recurring_task_creates_next_occurrence PASSED [ 80%]
tests/tests_pawpal.py::test_same_time_tasks_are_flagged_across_pets_but_not_when_completed PASSED [100%]

============================== 5 passed in 0.02s ===============================
```

**Confidence Level: ★★★★☆ (4/5)**

All 5 tests pass, and they cover the main behaviors and several edge cases of sorting, recurrence and conflict detection. I'm holding back one star because conflict detection only catches identical start times (a 30-minute task at 08:00 and another at 08:15 are not flagged), and I haven't tested invalid input such as a malformed `HH:MM` time, or the Streamlit UI.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Schedule.sort_by_priority()` | High priority first, shorter tasks first within a tier |
| Sort by time | `Schedule.sort_by_time()` | Chronological by `"HH:MM"`; untimed tasks last |
| Filtering | `Schedule.filter_tasks()` | By pet name and/or completion status |
| Time-conflict warnings | `Schedule.time_conflict_warnings()` | Same start time, same pet or different pets |
| Overflow detection | `Schedule.detect_conflicts()` | Pending tasks that don't fit in the owner's available minutes |
| Recurring tasks | `Pet.complete_task()`, `Task.next_occurrence()` | Daily and weekly tasks regenerate when completed |

### Sorting

`Schedule.sort_by_time(tasks=None)` returns a new list ordered by each task's `time`.
Zero-padded `"HH:MM"` strings sort chronologically as plain strings, so the sort key is
just `lambda t: (t.time == "", t.time)`. The first element pushes tasks with no time to
the end. Python's sort is stable, so tasks with equal times keep their original order.
Pass a list (for example the output of `filter_tasks`) to sort a subset; with no
argument it sorts all of the owner's tasks.

`Schedule.sort_by_priority()` is what `generate_plan()` uses to fill the day:
`(priority rank, duration)` over pending tasks.

### Filtering

`Schedule.filter_tasks(pet_name=None, completed=None)` keeps tasks matching both
criteria. A criterion left as `None` is ignored, so you can filter by pet only, by
status only (`completed=False` for pending), or both. Each task carries a `pet_name`,
set automatically by `Pet.add_task()`, which is what makes pet filtering possible.
Results can be passed into `sort_by_time()`.

### Conflict detection

`Schedule.time_conflict_warnings()` is a lightweight check that returns a list of
warning strings instead of raising, so the app keeps running. It buckets pending,
timed tasks by `(due_date, time)` in a single pass and reports any bucket with two or
more tasks, for example:

```
Warning: 3 tasks at 09:00 (pets: Buddy, Whiskers): 'Vet visit' (Buddy), 'Training' (Buddy), 'Medication' (Whiskers)
```

It catches clashes within one pet and across pets. **Limitation:** it only compares
exact start times, so a 45-minute task at 08:00 and another at 08:30 are not flagged.

`Schedule.detect_conflicts()` is a separate check: it returns pending tasks that were
skipped because they don't fit in `Owner.available_minutes`.

### Recurring tasks

`Task.next_occurrence()` builds a pending copy of a `"daily"` (+1 day) or `"weekly"`
(+1 week) task with an advanced `due_date`, counted from the task's `due_date` or
from today if it is unset. Other frequencies return `None`.

`Pet.complete_task(task)` marks the task complete and adds the next occurrence to the
same pet. Use it instead of `Task.mark_complete()` for recurring tasks; the plain
method only sets the flag and does not create a new task. The completed task stays in
the list.

**Known gap:** `generate_plan()` does not yet filter by `due_date`, so a future
occurrence can appear in today's plan.

Run `python main.py` to see all of these on sample data.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
