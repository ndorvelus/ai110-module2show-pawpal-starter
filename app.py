from datetime import date
from pathlib import Path

import streamlit as st

from display import CATEGORY_EMOJI, category_label, priority_badge, status_icon
from pawpal_system import Owner, Pet, Schedule, Task

DATA_FILE = Path(__file__).parent / "data.json"

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# The session "vault": Streamlit reruns this script on every interaction, so the
# Owner is only created the first time and reused on every rerun after that.
# On a fresh session, reload whatever the last run saved to data.json.
if "owner" not in st.session_state:
    try:
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    except FileNotFoundError:
        st.session_state.owner = Owner(name="Jordan", available_minutes=60)
    except ValueError as exc:
        st.warning(f"Could not read saved data, starting fresh: {exc}")
        st.session_state.owner = Owner(name="Jordan", available_minutes=60)
owner: Owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.available_minutes = int(
    st.number_input(
        "Minutes available today",
        min_value=1,
        max_value=1440,
        value=owner.available_minutes,
    )
)

st.subheader("Pets")
col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Mixed")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))

if owner.pets:
    st.table(
        [
            {"name": p.name, "species": p.species, "breed": p.breed, "age": p.age}
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")

if owner.pets:
    pet_choice = st.selectbox("Pet", [p.name for p in owner.pets])
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        category = st.selectbox(
            "Type", list(CATEGORY_EMOJI), format_func=category_label
        )
    col1, col2 = st.columns(2)
    with col1:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
    with col2:
        priority = st.selectbox(
            "Priority",
            ["low", "medium", "high"],
            index=2,
            format_func=priority_badge,
        )
    col1, col2 = st.columns(2)
    with col1:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])
    with col2:
        start = st.time_input("Start time", value=None, step=300)

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == pet_choice)
        pet.add_task(
            Task(
                title=task_title,
                category=category,
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
                time=start.strftime("%H:%M") if start else "",
                due_date=date.today(),
            )
        )
        st.success(f"Added '{task_title}' for {pet_choice}.")
else:
    st.caption("Add a pet first, then you can give it tasks.")

schedule = Schedule(day=date.today(), owner=owner)

# Conflict warnings come straight from the Scheduler, so the owner sees clashes
# as soon as they happen instead of after generating a plan.
for warning in schedule.time_conflict_warnings():
    st.warning(warning)

st.markdown("#### Your tasks")
if owner.get_all_tasks():
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.selectbox("Show status", ["All", "Pending", "Completed"])
    with col3:
        sort_choice = st.selectbox("Sort by", ["Time", "Priority, then time"])

    visible = schedule.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"All": None, "Pending": False, "Completed": True}[status_filter],
    )
    visible = (
        schedule.sort_by_time(visible)
        if sort_choice == "Time"
        else schedule.sort_by_priority_and_time(visible)
    )

    if visible:
        st.table(
            [
                {
                    "status": status_icon(t),
                    "time": t.time or "-",
                    "pet": t.pet_name,
                    "task": t.title,
                    "type": category_label(t.category),
                    "duration (min)": t.duration_minutes,
                    "priority": priority_badge(t.priority),
                    "repeats": t.frequency,
                    "due": t.due_date.isoformat() if t.due_date else "-",
                }
                for t in visible
            ]
        )
    else:
        st.info("No tasks match those filters.")

    pending = schedule.sort_by_time(schedule.filter_tasks(completed=False))
    if pending:
        labels = [f"{t.time or 'anytime'} - {t.title} ({t.pet_name})" for t in pending]
        chosen = st.selectbox("Complete a task", range(len(pending)), format_func=labels.__getitem__)
        if st.button("Mark complete"):
            task = pending[chosen]
            pet = next(p for p in owner.pets if p.name == task.pet_name)
            following = pet.complete_task(task)
            if following:
                st.success(
                    f"Done! '{task.title}' repeats {task.frequency}, so the next one "
                    f"is scheduled for {following.due_date:%A, %b %d}."
                )
            else:
                st.success(f"Done! '{task.title}' is complete.")
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Find a free slot")
col1, col2 = st.columns([2, 1])
with col1:
    slot_minutes = int(
        st.number_input("Task length (minutes)", min_value=1, max_value=240, value=30)
    )
with col2:
    st.write("")
    find_slot = st.button("Find next free slot")
if find_slot:
    slot = schedule.find_next_available_slot(slot_minutes)
    if slot:
        st.success(f"Next free {slot_minutes}-minute slot today: {slot}")
    else:
        st.warning(f"No free {slot_minutes}-minute gap between 08:00 and 20:00.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    planned = schedule.generate_plan()
    if planned:
        st.success(
            f"Planned {len(planned)} task(s): {schedule.total_duration()} of "
            f"{owner.available_minutes} minutes used."
        )
        st.table(
            [
                {
                    "order": n,
                    "task": t.title,
                    "pet": t.pet_name,
                    "duration (min)": t.duration_minutes,
                    "priority": priority_badge(t.priority),
                }
                for n, t in enumerate(planned, start=1)
            ]
        )
    else:
        st.info("Nothing to plan: no pending tasks fit in the time available.")

    if schedule.skipped_tasks:
        st.warning(
            f"{len(schedule.skipped_tasks)} task(s) don't fit in your "
            f"{owner.available_minutes} available minutes:"
        )
        st.table(
            [
                {
                    "task": t.title,
                    "pet": t.pet_name,
                    "duration (min)": t.duration_minutes,
                    "priority": priority_badge(t.priority),
                }
                for t in schedule.skipped_tasks
            ]
        )

# Persist after every interaction so the next run picks up where this one left off.
owner.save_to_json(DATA_FILE)
