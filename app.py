import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ===== Initialize session state (the "vault") =====
# Check if objects exist, create them if not

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pet" not in st.session_state:
    st.session_state.pet = None

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "schedule" not in st.session_state:
    st.session_state.schedule = None

# ===== App Header =====
st.title("🐾 PawPal+")
st.markdown("**AI-powered pet care planning assistant**")
st.caption("Plan your pet's daily care tasks with smart scheduling")

st.divider()

# ===== Owner Information Section =====
st.subheader("👤 Owner Information")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan", key="owner_name_input")
with col2:
    time_available = st.number_input(
        "Time available today (minutes)",
        min_value=0,
        max_value=1440,  # 24 hours
        value=480,  # 8 hours default
        step=30,
        help="How much time do you have for pet care today?"
    )

# Create/update Owner object in session state
st.session_state.owner = Owner(name=owner_name, time_available=time_available)

st.divider()

# ===== Pet Information Section =====
st.subheader("🐕 Pet Information")

col1, col2 = st.columns(2)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi", key="pet_name_input")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])

# Create/update Pet object in session state
st.session_state.pet = Pet(name=pet_name, type=species)

st.caption(f"Planning for: {st.session_state.pet}")

st.divider()

# ===== Tasks Section =====
st.subheader("📋 Care Tasks")
st.caption("Add tasks that need to be completed today")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task name", value="Morning walk", key="task_title_input")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Add Task button - creates actual CareTask objects
if st.button("➕ Add Task", use_container_width=True):
    try:
        # Create a real CareTask object using our backend
        new_task = CareTask(
            name=task_title,
            duration=int(duration),
            priority=priority,
            task_type=task_title  # Use title as type for now
        )
        # Add to session state
        st.session_state.tasks.append(new_task)
        st.success(f"✅ Added: {new_task.name}")
        st.rerun()  # Force refresh to show new task immediately
    except ValueError as e:
        st.error(f"❌ Error adding task: {e}")

# Display current tasks
if st.session_state.tasks:
    st.markdown(f"**Current tasks ({len(st.session_state.tasks)}):**")

    # Create a nice table display
    task_data = []
    for i, task in enumerate(st.session_state.tasks, 1):
        task_data.append({
            "#": i,
            "Task": task.name,
            "Duration (min)": task.duration,
            "Priority": task.priority.capitalize(),
            "ID": task.task_id
        })

    st.table(task_data)

    # Button to clear all tasks
    if st.button("🗑️ Clear All Tasks"):
        st.session_state.tasks = []
        st.session_state.schedule = None  # Also clear schedule
        st.rerun()
else:
    st.info("📝 No tasks yet. Add one above to get started!")

st.divider()

# ===== Schedule Generation Section =====
st.subheader("📅 Generate Schedule")
st.caption("Create an optimized daily schedule based on priorities and time constraints")

# Display current constraints
col1, col2 = st.columns(2)
with col1:
    st.metric("Owner", st.session_state.owner.name if st.session_state.owner else "N/A")
    st.metric("Pet", st.session_state.pet.name if st.session_state.pet else "N/A")
with col2:
    st.metric("Available Time", f"{time_available} min")
    st.metric("Tasks to Schedule", len(st.session_state.tasks))

# Generate Schedule button - calls actual Scheduler
if st.button("🚀 Generate Schedule", type="primary", use_container_width=True):
    if not st.session_state.tasks:
        st.warning("⚠️ Please add at least one task before generating a schedule.")
    elif not st.session_state.owner or not st.session_state.pet:
        st.error("❌ Owner and Pet information are required.")
    else:
        try:
            # Create scheduler with current data
            scheduler = Scheduler(
                owner=st.session_state.owner,
                pet=st.session_state.pet,
                tasks=st.session_state.tasks
            )

            # Generate the schedule!
            st.session_state.schedule = scheduler.generate_schedule()

            st.success("✅ Schedule generated successfully!")
            st.balloons()  # Celebration!

        except Exception as e:
            st.error(f"❌ Error generating schedule: {e}")

st.divider()

# ===== Display Schedule Results =====
if st.session_state.schedule:
    st.subheader("📊 Your Daily Schedule")

    schedule = st.session_state.schedule

    # Display summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Tasks Scheduled",
            len(schedule.scheduled_tasks),
            delta=f"{len(schedule.scheduled_tasks)} / {len(st.session_state.tasks)}"
        )
    with col2:
        st.metric(
            "Total Time",
            f"{schedule.total_duration} min",
            delta=f"{schedule.total_duration - schedule.owner.time_available} min" if not schedule.is_feasible() else None,
            delta_color="inverse"
        )
    with col3:
        feasible = schedule.is_feasible()
        st.metric(
            "Feasible",
            "✅ Yes" if feasible else "⚠️ No",
            delta="Within budget" if feasible else "Over capacity"
        )

    # Display scheduled tasks
    if schedule.scheduled_tasks:
        st.markdown("### 📝 Scheduled Tasks (in priority order)")

        task_table = []
        for i, task in enumerate(schedule.scheduled_tasks, 1):
            task_table.append({
                "Order": i,
                "Task": task.name,
                "Duration": f"{task.duration} min",
                "Priority": task.priority.capitalize(),
                "Status": "⏳ Pending"
            })

        st.dataframe(task_table, use_container_width=True, hide_index=True)

    # Display explanation
    st.markdown("### 💡 Explanation")
    st.info(schedule.explanation)

    # Warning if not feasible
    if not schedule.is_feasible():
        st.error("⚠️ **Warning:** This schedule exceeds your available time! Consider removing low-priority tasks or increasing available time.")

else:
    st.info("👆 Click 'Generate Schedule' above to create your optimized daily plan!")

st.divider()

# ===== Footer =====
st.caption("🐾 PawPal+ | AI110 Module 2 Project")
