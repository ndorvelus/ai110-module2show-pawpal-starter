from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Schedule, Task

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
if "owner" not in st.session_state:
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
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=20
        )
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        pet = next(p for p in owner.pets if p.name == pet_choice)
        pet.add_task(
            Task(
                title=task_title,
                category="general",
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
            )
        )
else:
    st.caption("Add a pet first, then you can give it tasks.")

all_tasks = [
    {
        "pet": pet.name,
        "title": t.title,
        "duration_minutes": t.duration_minutes,
        "priority": t.priority,
        "frequency": t.frequency,
    }
    for pet in owner.pets
    for t in pet.get_tasks()
]
if all_tasks:
    st.write("Current tasks:")
    st.table(all_tasks)
else:
    st.info("No tasks yet.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    schedule = Schedule(day=date.today(), owner=owner)
    schedule.generate_plan()
    st.text(schedule.explain_plan())
