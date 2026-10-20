# AI Interactions Log

---

## Agent Workflow (SF7)

**What task did you give the agent?**

Across the project I asked Claude Code to make a series of multi-step changes: implement sorting, filtering and conflict detection; auto-create the next occurrence when a daily or weekly task is completed; add docstrings; write tests; wire the logic into the Streamlit UI; update the UML and README; and then the five challenges: a third algorithm (next available slot), JSON persistence (`save_to_json` / `load_from_json`), priority-then-time sorting, formatted CLI and UI output, and a multi-model prompt comparison.

**What did the agent do?**

| Files modified | Change |
|----------------|--------|
| `pawpal_system.py` | Added `Task.next_occurrence`, `Pet.complete_task`, `Schedule.sort_by_time`, `filter_tasks`, `time_conflict_warnings`, `sort_by_priority_and_time`, `find_next_available_slot`, and `to_dict` / `from_dict` on `Task`, `Pet` and `Owner`, plus `Owner.save_to_json` / `load_from_json`. |
| `display.py` (new) | Emoji, priority badges, status icons and `tabulate` tables. |
| `app.py` | Uses the Scheduler methods for sorting, filtering, warnings (`st.warning`), success messages (`st.success`) and tables (`st.table`); adds a free-slot finder, a sort selector and load/save of `data.json`. |
| `main.py` | Demo script with tables, priority sorting, slot search and a persistence round trip. |
| `tests/tests_pawpal.py`, `pytest.ini` | 8 tests covering sorting, priority sorting, recurrence, conflicts, slot finding and persistence. |
| `README.md`, `diagrams/uml_final.mmd`, `requirements.txt`, `.gitignore` | Documentation, final UML, new dependencies (`tabulate`, `wcwidth`), and `data.json` ignored. |

The agent ran the tests and `main.py` after each change, and exercised the Streamlit app with Streamlit's `AppTest` harness in a throwaway virtual environment.

**What did you have to verify or fix manually?**

Problems the agent found and fixed while working (please add your own review notes below):

- `main.py` completed the wrong task in its recurrence demo (`whiskers.tasks[-1]` was "Medication", but the output said "Vet reminder"). It now looks the task up by title.
- Plain `pytest` collected 0 tests because of the `tests_pawpal.py` file name, so `pytest.ini` was added.
- The machine's default `python` is 3.9, which can't run the `X | None` type syntax; the project needs Python 3.10+, and the README now says so.
- Without `wcwidth`, `tabulate` misaligned the emoji columns; it was added to `requirements.txt`.

Known limitations that need a human decision: `generate_plan()` doesn't filter by `due_date`, so future occurrences can appear in today's plan, and `time_conflict_warnings()` only catches identical start times.

<!-- Add your own manual verification and corrections here. -->

---

## Prompt Comparison (SF11)

**Task chosen:** the logic for rescheduling recurring (daily and weekly) tasks when one is completed.

> **Status: half complete.** Option A below is real and describes the code in this repo.
> Option B has **not been run**: the agent working on this project is a single model and
> could not query a second one, so no second-model output is recorded rather than inventing
> one. Paste the prompt below into a different tool (Gemini, ChatGPT or Copilot), then fill
> in the Option B column from its actual answer.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | Claude (Claude Code) | *(fill in, e.g. Gemini or ChatGPT)* |
| **Prompt** | "Add logic to your Task or Scheduler class so that when a 'daily' or 'weekly' task is marked complete, a new instance is automatically created for the next occurrence." | Paste the prompt below, with the contents of `pawpal_system.py` |
| **Response summary** | `Task.next_occurrence()` looks up a `timedelta` in a `RECURRENCE_STEP` dict (1 day or 1 week) and returns a pending copy made with `dataclasses.replace`, or `None` for other frequencies. `Pet.complete_task()` marks the task done and adds the copy. | *(fill in)* |
| **What was useful** | Small and testable. Adding a frequency is one dict entry. The original task is left unmodified, and the copy keeps the pet name and time. | *(fill in)* |
| **Problems noticed** | The next date is counted from the task's `due_date`, not from when it was actually completed, so completing late leaves the next one overdue. Callers must use `Pet.complete_task()` instead of `Task.mark_complete()`, or no copy is made. Monthly or custom intervals aren't supported. | *(fill in)* |
| **Decision** | Used in the final implementation. | *(fill in after comparing)* |

**Prompt to paste into the second tool:**

```text
I have a Python dataclass `Task` with fields title, category, duration_minutes, priority,
frequency ("daily", "weekly" or "once"), completed, time ("HH:MM"), pet_name and
due_date (date or None). A `Pet` owns a list of tasks. Add logic so that when a daily or
weekly task is marked complete, a new pending instance for the next occurrence is
created and added to the same pet. Use due_date as the base (today if it is None). Keep
the original task unchanged apart from being marked complete. Explain edge cases.
```

**Which approach did you use in your final implementation and why?**

Option A, because it is already implemented, tested (`test_completing_recurring_task_creates_next_occurrence`) and small. Revisit this once Option B has been filled in; the things worth comparing are how each handles a `None` due date, month boundaries, and which object is responsible for creating the next occurrence.
