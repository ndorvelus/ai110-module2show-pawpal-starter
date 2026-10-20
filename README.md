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

Requires Python 3.10+ (the code uses `X | None` type syntax). Install dependencies first with `pip install -r requirements.txt`.

```bash
python -m pytest
```

**What the tests cover** (`tests/tests_pawpal.py`):

- **Basics:** `mark_complete` flips a task's status, and `add_task` grows a pet's task list.
- **Sorting:** `sort_by_time` returns tasks in chronological order with untimed tasks last. A pet with no tasks and an owner with no pets both return empty results without errors.
- **Priority sorting:** `sort_by_priority_and_time` ranks high before low even when the low task starts earlier, puts untimed tasks last within a tier, and leaves out completed tasks.
- **Recurrence:** completing a daily task creates a pending copy due the next day (including across a month boundary). Weekly tasks advance 7 days, and one-off tasks create nothing.
- **Conflict detection:** two tasks at the same time are flagged, including across different pets. Tasks at different times and completed tasks are not.
- **Next available slot:** the finder skips busy blocks, respects the task's duration, ignores tasks on other days, and returns `None` when nothing fits.
- **Persistence:** a save/load round trip preserves every field (including real `date` objects, completed flags and pets with no tasks). A corrupt file raises `ValueError` and a missing file raises `FileNotFoundError`.

Test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0 
cachedir: .pytest_cache
rootdir: /Users/nathan/Documents/GitHub/ai110-module2show-pawpal-starter
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 8 items

tests/tests_pawpal.py::test_mark_complete_changes_status PASSED          [ 12%]
tests/tests_pawpal.py::test_add_task_increases_pet_task_count PASSED     [ 25%]
tests/tests_pawpal.py::test_sort_by_time_is_chronological_with_untimed_last_and_empty_pet_ok PASSED [ 37%]
tests/tests_pawpal.py::test_completing_recurring_task_creates_next_occurrence PASSED [ 50%]
tests/tests_pawpal.py::test_same_time_tasks_are_flagged_across_pets_but_not_when_completed PASSED [ 62%]
tests/tests_pawpal.py::test_sort_by_priority_and_time_ranks_priority_before_time PASSED [ 75%]
tests/tests_pawpal.py::test_find_next_available_slot_skips_busy_blocks_and_respects_duration PASSED [ 87%]
tests/tests_pawpal.py::test_json_round_trip_preserves_data_and_rejects_corrupt_file PASSED [100%]

============================== 8 passed in 0.02s ===============================
```

**Confidence Level: ★★★★☆ (4/5)**

All 8 tests pass, and they cover the main behaviors and several edge cases of sorting, recurrence, conflict detection, slot finding and persistence. I'm holding back one star because conflict detection only catches identical start times (the slot finder is duration-aware, but the warnings are not), and I haven't tested malformed `HH:MM` times or the Streamlit UI beyond a scripted smoke run.

## ✨ Features

- **Priority-based planning:** `generate_plan()` takes pending tasks in order of priority (high, then medium, then low), shortest first within a tier. It adds each one until the owner's available minutes run out; the rest are listed as skipped.
- **Sorting by time:** `sort_by_time()` orders tasks chronologically by their `"HH:MM"` start time. Tasks with no time go last, and tasks with equal times keep their original order.
- **Filtering:** `filter_tasks()` narrows tasks by pet, by completion status, or both. The result can be passed straight into `sort_by_time()`.
- **Conflict warnings:** `time_conflict_warnings()` flags two or more pending tasks that start at the same time on the same day. It catches clashes within one pet and across pets, and returns messages instead of raising errors.
- **Overflow detection:** `detect_conflicts()` lists the pending tasks that don't fit in the owner's available minutes.
- **Daily and weekly recurrence:** `Pet.complete_task()` marks a task done and adds the next occurrence, due one day or one week later. One-off tasks don't repeat.
- **Priority, then time ordering:** `sort_by_priority_and_time()` sorts by priority first and start time second.
- **Next available slot:** `find_next_available_slot()` finds the first gap that fits a task of a given length, accounting for the duration of the tasks already scheduled.
- **Data persistence:** `Owner.save_to_json()` and `Owner.load_from_json()` keep pets and tasks between runs in `data.json`.
- **Readable output:** emoji task types, color-coded priority badges, status icons and `tabulate` tables.
- **Input validation:** a task rejects non-positive durations, unknown priorities and badly formatted times when it is created.
- **Plan explanation:** `explain_plan()` describes what was planned, what was skipped, and how many minutes were used.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Schedule.sort_by_priority()` | High priority first, shorter tasks first within a tier |
| Sort by time | `Schedule.sort_by_time()` | Chronological by `"HH:MM"`; untimed tasks last |
| Sort by priority, then time | `Schedule.sort_by_priority_and_time()` | High to low, then chronological; untimed last in each tier |
| Next available slot | `Schedule.find_next_available_slot()` | First gap that fits a task's duration |
| Persistence | `Owner.save_to_json()`, `Owner.load_from_json()` | Pets and tasks stored in `data.json` |
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

## 🚀 Advanced Challenges

### Next available slot (algorithmic capability)

`Schedule.find_next_available_slot(duration_minutes, earliest="08:00", latest="20:00")`
returns the first start time where a task of that length fits without overlapping
anything already scheduled today. It builds the busy interval `(start, start + duration)`
for each pending, timed task on the schedule's day, sorts them, and sweeps a cursor
forward from `earliest`, jumping past each interval that blocks it. The first gap big
enough wins, and `None` is returned if there isn't one. It is O(n log n) in the number
of timed tasks. Unlike `time_conflict_warnings()`, it accounts for durations, so it
catches overlaps between different start times. In the app, use **Find next free slot**.

```
Next available slot (08:00-20:00, tasks block their duration):
   15 min -> 08:00
   45 min -> 08:00
  120 min -> 09:30
```

### Priority-based scheduling

Every `Task` has a `priority` of `"low"`, `"medium"` or `"high"`, validated when the
task is created. `Schedule.sort_by_priority_and_time()` orders pending tasks by priority
first (high to low) and start time second, with untimed tasks last inside each tier. The
app exposes it as **Sort by: Priority, then time**. (`sort_by_priority()` is still what
`generate_plan()` uses, and orders by priority then duration.) In the output below, the
medium-priority 09:00 task comes after every high-priority task, and the untimed low task
comes last:

```
Pending, priority first then time:
╭────────────┬────────┬────────────────┬──────────┬─────────────┬────────────┬───────╮
│ Status     │ Time   │ Task           │ Pet      │ Type        │ Priority   │   Min │
├────────────┼────────┼────────────────┼──────────┼─────────────┼────────────┼───────┤
│ ⏳ pending │ 07:00  │ Feed breakfast │ Whiskers │ 🍖 feeding  │ 🔴 high    │    10 │
│ ⏳ pending │ 07:15  │ Morning walk   │ Buddy    │ 🦮 exercise │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Vet visit      │ Buddy    │ 💊 health   │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Medication     │ Whiskers │ 💊 health   │ 🔴 high    │     5 │
│ ⏳ pending │ 09:00  │ Training       │ Buddy    │ 🦮 exercise │ 🟡 medium  │    20 │
│ ⏳ pending │ 18:30  │ Brush coat     │ Buddy    │ 🛁 grooming │ 🟢 low     │    20 │
│ ⏳ pending │ --:--  │ Vet reminder   │ Whiskers │ 💊 health   │ 🟢 low     │     5 │
╰────────────┴────────┴────────────────┴──────────┴─────────────┴────────────┴───────╯
```

### Data persistence

Pets and tasks are saved to `data.json` and reloaded on the next run.

- **Conversion:** `Task`, `Pet` and `Owner` each have `to_dict()` and `from_dict()`. This is
  a custom dictionary conversion rather than a library such as marshmallow, because the
  only value JSON can't store natively is a `date`, which is written as ISO text
  (`"2026-10-21"`) and parsed back with `date.fromisoformat`. `from_dict` goes through the
  normal constructors, so loaded data is re-validated.
- **Saving:** `Owner.save_to_json(path="data.json")` writes the whole tree (owner, pets,
  tasks). It writes to a `.tmp` file and renames it over the target, so a crash can't leave
  a half-written file.
- **Loading:** `Owner.load_from_json(path="data.json")` raises `FileNotFoundError` on a
  first run and `ValueError` for a corrupt file.
- **In the app:** [app.py](app.py) loads `data.json` when a session starts (falling back
  to a fresh owner, with a warning if the file is corrupt) and saves at the end of every
  interaction. `data.json` is listed in `.gitignore`.
- **Files modified:** `pawpal_system.py` (the methods above), `app.py` (load and save),
  `main.py` (round-trip demo), `.gitignore`, and `tests/tests_pawpal.py`.

Round-trip demo from `python main.py`:

```
Persistence:
  Saved 11 tasks for 2 pets -> reloaded 11 tasks for 2 pets
  Round trip identical: True
```

### Professional output formatting

[display.py](display.py) holds the formatting helpers, used by both the CLI and the app:

| Feature | Function | Example |
|---------|----------|---------|
| Emoji per task type | `category_label()` | 🦮 exercise, 🍖 feeding, 🛁 grooming, 💊 health, 🧶 enrichment |
| Color-coded priority | `priority_badge()` | 🔴 high, 🟡 medium, 🟢 low |
| Status icons | `status_icon()` | ✅ done, ⏳ pending |
| CLI tables | `format_task_table()` | Rounded, boxed tables built with `tabulate` |
| Streamlit tables | `st.table`, `st.success`, `st.warning` | The app reuses the same helpers |

Libraries: [`tabulate`](https://pypi.org/project/tabulate/) draws the tables and
[`wcwidth`](https://pypi.org/project/wcwidth/) lets it measure emoji widths so columns
line up. Both are in `requirements.txt`. Files modified: `display.py` (new), `main.py`,
`app.py`, `requirements.txt`.

## 📸 Demo Walkthrough

### The Streamlit app

Start it with `streamlit run app.py`. From top to bottom the page lets you:

- **Set up the owner:** enter your name and how many minutes you have today.
- **Add pets:** give each pet a name, species, breed and age. They appear in a table.
- **Add tasks:** pick a pet, then set a title, type (with an emoji), duration, priority, frequency (daily, weekly or once) and an optional start time.
- **See warnings right away:** if two pending tasks start at the same time, a yellow warning names the tasks and pets involved.
- **Browse tasks:** the task table shows status icons, emoji types and color-coded priorities. "Show pet" and "Show status" filter it, and "Sort by" switches between time and priority-then-time.
- **Find a free slot:** enter a task length and click "Find next free slot" to get the first gap that fits.
- **Complete a task:** pick a pending task and click "Mark complete". Daily and weekly tasks confirm the date of the next one.
- **Generate a schedule:** a green message reports the minutes used, followed by the ordered plan. Tasks that don't fit appear under a warning.

### Example workflow

1. Add a pet, for example Mochi the dog.
2. Add a "Morning walk" task: 30 minutes, high priority, daily, at 08:00.
3. Add a second task, "Feed breakfast", also at 08:00. A conflict warning appears immediately.
4. Change the status filter to "Pending" to see only unfinished tasks, sorted by time.
5. Select "Morning walk" and click "Mark complete". The app reports that the next walk is scheduled for tomorrow.
6. Click "Generate schedule" to see today's plan and anything that was skipped for lack of time.

### Scheduler behaviors on display

- **Sorting:** tasks added out of order are shown chronologically, with untimed tasks last.
- **Filtering:** by pet, by status, or both.
- **Conflict warnings:** same-time tasks are flagged for one pet or across pets, without crashing the app.
- **Recurrence:** completing a daily or weekly task creates a pending copy dated one day or one week later.
- **Free-slot search:** the first gap that fits a task of a given length, accounting for the duration of existing tasks.
- **Persistence:** everything you add is still there after you restart the app.
- **Time budget:** tasks that don't fit in the available minutes are skipped and listed.

### Sample CLI output

`python main.py` runs the same logic on sample data (the dates below depend on the day you run it):

```
========================================
Today's Schedule - Tuesday, October 20, 2026
========================================
Plan for Jordan on 2026-10-20 (45/60 min used):
- Feed breakfast (10 min, high priority)
- Morning walk (30 min, high priority)
- Vet reminder (5 min, low priority)
Skipped (not enough time):
- Brush coat (20 min, low priority)

Conflict check:
  Warning: 3 tasks at 09:00 (pets: Buddy, Whiskers): 'Vet visit' (Buddy), 'Training' (Buddy), 'Medication' (Whiskers)

Recurrence:
  Completed 'Morning walk' (daily) -> next due 2026-10-21
  Completed 'Brush coat' (weekly) -> next due 2026-10-27
  Completed 'Vet reminder' (weekly) -> next due 2026-10-27

All tasks, as added:
╭────────────┬────────┬─────────────────┬──────────┬───────────────┬────────────┬───────╮
│ Status     │ Time   │ Task            │ Pet      │ Type          │ Priority   │   Min │
├────────────┼────────┼─────────────────┼──────────┼───────────────┼────────────┼───────┤
│ ✅ done    │ 18:30  │ Brush coat      │ Buddy    │ 🛁 grooming   │ 🟢 low     │    20 │
│ ✅ done    │ 07:15  │ Morning walk    │ Buddy    │ 🦮 exercise   │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Vet visit       │ Buddy    │ 💊 health     │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Training        │ Buddy    │ 🦮 exercise   │ 🟡 medium  │    20 │
│ ⏳ pending │ 07:15  │ Morning walk    │ Buddy    │ 🦮 exercise   │ 🔴 high    │    30 │
│ ⏳ pending │ 18:30  │ Brush coat      │ Buddy    │ 🛁 grooming   │ 🟢 low     │    20 │
│ ✅ done    │ 12:00  │ Play with laser │ Whiskers │ 🧶 enrichment │ 🟡 medium  │    15 │
│ ⏳ pending │ 07:00  │ Feed breakfast  │ Whiskers │ 🍖 feeding    │ 🔴 high    │    10 │
│ ✅ done    │ --:--  │ Vet reminder    │ Whiskers │ 💊 health     │ 🟢 low     │     5 │
│ ⏳ pending │ 09:00  │ Medication      │ Whiskers │ 💊 health     │ 🔴 high    │     5 │
│ ⏳ pending │ --:--  │ Vet reminder    │ Whiskers │ 💊 health     │ 🟢 low     │     5 │
╰────────────┴────────┴─────────────────┴──────────┴───────────────┴────────────┴───────╯

Sorted by time:
╭────────────┬────────┬─────────────────┬──────────┬───────────────┬────────────┬───────╮
│ Status     │ Time   │ Task            │ Pet      │ Type          │ Priority   │   Min │
├────────────┼────────┼─────────────────┼──────────┼───────────────┼────────────┼───────┤
│ ⏳ pending │ 07:00  │ Feed breakfast  │ Whiskers │ 🍖 feeding    │ 🔴 high    │    10 │
│ ✅ done    │ 07:15  │ Morning walk    │ Buddy    │ 🦮 exercise   │ 🔴 high    │    30 │
│ ⏳ pending │ 07:15  │ Morning walk    │ Buddy    │ 🦮 exercise   │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Vet visit       │ Buddy    │ 💊 health     │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Training        │ Buddy    │ 🦮 exercise   │ 🟡 medium  │    20 │
│ ⏳ pending │ 09:00  │ Medication      │ Whiskers │ 💊 health     │ 🔴 high    │     5 │
│ ✅ done    │ 12:00  │ Play with laser │ Whiskers │ 🧶 enrichment │ 🟡 medium  │    15 │
│ ✅ done    │ 18:30  │ Brush coat      │ Buddy    │ 🛁 grooming   │ 🟢 low     │    20 │
│ ⏳ pending │ 18:30  │ Brush coat      │ Buddy    │ 🛁 grooming   │ 🟢 low     │    20 │
│ ✅ done    │ --:--  │ Vet reminder    │ Whiskers │ 💊 health     │ 🟢 low     │     5 │
│ ⏳ pending │ --:--  │ Vet reminder    │ Whiskers │ 💊 health     │ 🟢 low     │     5 │
╰────────────┴────────┴─────────────────┴──────────┴───────────────┴────────────┴───────╯

Pet = Buddy:
╭────────────┬────────┬──────────────┬───────┬─────────────┬────────────┬───────╮
│ Status     │ Time   │ Task         │ Pet   │ Type        │ Priority   │   Min │
├────────────┼────────┼──────────────┼───────┼─────────────┼────────────┼───────┤
│ ✅ done    │ 18:30  │ Brush coat   │ Buddy │ 🛁 grooming │ 🟢 low     │    20 │
│ ✅ done    │ 07:15  │ Morning walk │ Buddy │ 🦮 exercise │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Vet visit    │ Buddy │ 💊 health   │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Training     │ Buddy │ 🦮 exercise │ 🟡 medium  │    20 │
│ ⏳ pending │ 07:15  │ Morning walk │ Buddy │ 🦮 exercise │ 🔴 high    │    30 │
│ ⏳ pending │ 18:30  │ Brush coat   │ Buddy │ 🛁 grooming │ 🟢 low     │    20 │
╰────────────┴────────┴──────────────┴───────┴─────────────┴────────────┴───────╯

Pending only:
╭────────────┬────────┬────────────────┬──────────┬─────────────┬────────────┬───────╮
│ Status     │ Time   │ Task           │ Pet      │ Type        │ Priority   │   Min │
├────────────┼────────┼────────────────┼──────────┼─────────────┼────────────┼───────┤
│ ⏳ pending │ 09:00  │ Vet visit      │ Buddy    │ 💊 health   │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Training       │ Buddy    │ 🦮 exercise │ 🟡 medium  │    20 │
│ ⏳ pending │ 07:15  │ Morning walk   │ Buddy    │ 🦮 exercise │ 🔴 high    │    30 │
│ ⏳ pending │ 18:30  │ Brush coat     │ Buddy    │ 🛁 grooming │ 🟢 low     │    20 │
│ ⏳ pending │ 07:00  │ Feed breakfast │ Whiskers │ 🍖 feeding  │ 🔴 high    │    10 │
│ ⏳ pending │ 09:00  │ Medication     │ Whiskers │ 💊 health   │ 🔴 high    │     5 │
│ ⏳ pending │ --:--  │ Vet reminder   │ Whiskers │ 💊 health   │ 🟢 low     │     5 │
╰────────────┴────────┴────────────────┴──────────┴─────────────┴────────────┴───────╯

Whiskers, completed:
╭──────────┬────────┬─────────────────┬──────────┬───────────────┬────────────┬───────╮
│ Status   │ Time   │ Task            │ Pet      │ Type          │ Priority   │   Min │
├──────────┼────────┼─────────────────┼──────────┼───────────────┼────────────┼───────┤
│ ✅ done  │ 12:00  │ Play with laser │ Whiskers │ 🧶 enrichment │ 🟡 medium  │    15 │
│ ✅ done  │ --:--  │ Vet reminder    │ Whiskers │ 💊 health     │ 🟢 low     │     5 │
╰──────────┴────────┴─────────────────┴──────────┴───────────────┴────────────┴───────╯

Whiskers pending, sorted by time:
╭────────────┬────────┬────────────────┬──────────┬────────────┬────────────┬───────╮
│ Status     │ Time   │ Task           │ Pet      │ Type       │ Priority   │   Min │
├────────────┼────────┼────────────────┼──────────┼────────────┼────────────┼───────┤
│ ⏳ pending │ 07:00  │ Feed breakfast │ Whiskers │ 🍖 feeding │ 🔴 high    │    10 │
│ ⏳ pending │ 09:00  │ Medication     │ Whiskers │ 💊 health  │ 🔴 high    │     5 │
│ ⏳ pending │ --:--  │ Vet reminder   │ Whiskers │ 💊 health  │ 🟢 low     │     5 │
╰────────────┴────────┴────────────────┴──────────┴────────────┴────────────┴───────╯

Pending, priority first then time:
╭────────────┬────────┬────────────────┬──────────┬─────────────┬────────────┬───────╮
│ Status     │ Time   │ Task           │ Pet      │ Type        │ Priority   │   Min │
├────────────┼────────┼────────────────┼──────────┼─────────────┼────────────┼───────┤
│ ⏳ pending │ 07:00  │ Feed breakfast │ Whiskers │ 🍖 feeding  │ 🔴 high    │    10 │
│ ⏳ pending │ 07:15  │ Morning walk   │ Buddy    │ 🦮 exercise │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Vet visit      │ Buddy    │ 💊 health   │ 🔴 high    │    30 │
│ ⏳ pending │ 09:00  │ Medication     │ Whiskers │ 💊 health   │ 🔴 high    │     5 │
│ ⏳ pending │ 09:00  │ Training       │ Buddy    │ 🦮 exercise │ 🟡 medium  │    20 │
│ ⏳ pending │ 18:30  │ Brush coat     │ Buddy    │ 🛁 grooming │ 🟢 low     │    20 │
│ ⏳ pending │ --:--  │ Vet reminder   │ Whiskers │ 💊 health   │ 🟢 low     │     5 │
╰────────────┴────────┴────────────────┴──────────┴─────────────┴────────────┴───────╯

Next available slot (08:00-20:00, tasks block their duration):
   15 min -> 08:00
   45 min -> 08:00
  120 min -> 09:30

Persistence:
  Saved 11 tasks for 2 pets -> reloaded 11 tasks for 2 pets
  Round trip identical: True
```
