import streamlit as st
from pawpal_system import Owner, Pet, CareTask, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ===== Initialize session state (the "vault") =====
# Check if objects exist, create them if not

if "owner" not in st.session_state:
    st.session_state.owner = None

if "pets" not in st.session_state:
    st.session_state.pets = []  # List of Pet objects

if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None  # Currently selected pet name

if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "schedules" not in st.session_state:
    st.session_state.schedules = {}  # Dict mapping pet_name -> Schedule

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

# ===== Pet Management Section =====
st.subheader("🐕 Pet Management")

# Display existing pets
if st.session_state.pets:
    st.markdown(f"**Your pets ({len(st.session_state.pets)}):**")

    # Show pets in a nice format
    pet_cols = st.columns(min(len(st.session_state.pets), 4))
    for idx, pet in enumerate(st.session_state.pets):
        with pet_cols[idx % 4]:
            is_selected = st.session_state.selected_pet == pet.name
            icon = "✅" if is_selected else "🐾"
            if st.button(f"{icon} {pet.name} ({pet.type})", key=f"select_pet_{idx}", use_container_width=True):
                st.session_state.selected_pet = pet.name
                st.rerun()

    st.caption(f"💡 Selected: **{st.session_state.selected_pet or 'None'}**")
else:
    st.info("👋 No pets yet! Add your first pet below.")

st.markdown("---")
st.markdown("**Add a new pet:**")

# Add new pet form
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    new_pet_name = st.text_input("Pet name", placeholder="e.g., Mochi", key="new_pet_name_input")
with col2:
    new_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"], key="new_species_select")
with col3:
    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)  # Spacer
    if st.button("➕ Add Pet", use_container_width=True):
        if new_pet_name:
            # Check if pet name already exists
            if any(p.name == new_pet_name for p in st.session_state.pets):
                st.error(f"❌ Pet named '{new_pet_name}' already exists!")
            else:
                # Create new pet
                new_pet = Pet(name=new_pet_name, type=new_species)
                st.session_state.pets.append(new_pet)
                st.session_state.selected_pet = new_pet_name  # Auto-select new pet
                st.success(f"✅ Added {new_pet_name}!")
                st.rerun()
        else:
            st.warning("⚠️ Please enter a pet name.")

# Option to remove selected pet
if st.session_state.selected_pet and st.session_state.pets:
    if st.button("🗑️ Remove Selected Pet", type="secondary"):
        # Remove pet and its tasks
        st.session_state.pets = [p for p in st.session_state.pets if p.name != st.session_state.selected_pet]
        st.session_state.tasks = [t for t in st.session_state.tasks if t.pet_name != st.session_state.selected_pet]
        if st.session_state.selected_pet in st.session_state.schedules:
            del st.session_state.schedules[st.session_state.selected_pet]
        st.session_state.selected_pet = None
        st.success("✅ Pet removed!")
        st.rerun()

st.divider()

# ===== Tasks Section =====
st.subheader("📋 Care Tasks")
if st.session_state.selected_pet:
    st.caption(f"Adding tasks for: **{st.session_state.selected_pet}** 🐾")
else:
    st.warning("⚠️ Please select a pet first to add tasks.")

# Task input fields
col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task name", value="Morning walk", key="task_title_input")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

# Advanced options in expander
with st.expander("⏰ Advanced Options (Time & Recurrence)"):
    col1, col2 = st.columns(2)
    with col1:
        preferred_time = st.text_input(
            "Preferred time",
            value="",
            placeholder="e.g., 8:00 AM or 14:30",
            help="Optional: 24-hour (14:30) or 12-hour (2:30 PM) format"
        )
    with col2:
        frequency = st.selectbox(
            "Recurrence",
            ["once", "daily", "biweekly", "weekly", "monthly", "quarterly", "yearly"],
            help="How often should this task repeat?"
        )

# Add Task button - creates actual CareTask objects
if st.button("➕ Add Task", use_container_width=True, disabled=not st.session_state.selected_pet):
    if not st.session_state.selected_pet:
        st.error("❌ Please select a pet first!")
    else:
        try:
            # Create a real CareTask object using our backend
            new_task = CareTask(
                name=task_title,
                duration=int(duration),
                priority=priority,
                task_type=task_title,
                preferred_time=preferred_time if preferred_time else None,
                frequency=frequency,
                pet_name=st.session_state.selected_pet  # Link task to selected pet
            )
            # Add to session state
            st.session_state.tasks.append(new_task)
            st.success(f"✅ Added: {new_task.name} for {st.session_state.selected_pet} ({frequency})")
            st.rerun()  # Force refresh to show new task immediately
        except ValueError as e:
            st.error(f"❌ Error adding task: {e}")

# Display current tasks
if st.session_state.tasks:
    # Filter options
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_option = st.radio(
            "Show tasks for:",
            ["Selected Pet Only", "All Pets"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col2:
        completion_filter = st.radio(
            "Status:",
            ["All Status", "Pending Only", "Completed Only"],
            horizontal=True,
            label_visibility="collapsed"
        )
    with col3:
        # View mode selector
        view_mode = st.selectbox(
            "Sort:",
            ["All", "Time", "Priority"],
            label_visibility="collapsed"
        )

    # Filter tasks based on selected pet
    if filter_option == "Selected Pet Only" and st.session_state.selected_pet:
        display_tasks = [t for t in st.session_state.tasks if t.pet_name == st.session_state.selected_pet]
    else:
        display_tasks = st.session_state.tasks.copy()

    # Filter by completion status
    if completion_filter == "Pending Only":
        display_tasks = [t for t in display_tasks if not t.completed]
    elif completion_filter == "Completed Only":
        display_tasks = [t for t in display_tasks if t.completed]

    st.markdown(f"**Showing {len(display_tasks)} task(s):**")

    # Sort tasks based on view mode
    if view_mode == "Time" and display_tasks:
        # Use backend sorting logic
        from pawpal_system import Scheduler
        # Create temporary pet object for scheduler if needed
        temp_pet = next((p for p in st.session_state.pets if p.name == st.session_state.selected_pet),
                       Pet(name="temp", type="dog")) if st.session_state.selected_pet else Pet(name="temp", type="dog")
        temp_scheduler = Scheduler(
            owner=st.session_state.owner,
            pet=temp_pet,
            tasks=display_tasks
        )
        display_tasks = temp_scheduler.sort_by_time()
    elif view_mode == "Priority":
        # Sort by priority (high > medium > low)
        priority_order = {"high": 3, "medium": 2, "low": 1}
        display_tasks = sorted(
            display_tasks,
            key=lambda t: priority_order.get(t.priority, 0),
            reverse=True
        )

    # Create enhanced table display with completion checkboxes
    task_data = []
    for i, task in enumerate(display_tasks, 1):
        # Format time
        time_str = task.preferred_time if task.preferred_time else "—"

        # Format frequency with emoji
        freq_display = {
            "once": "🔵 Once",
            "daily": "🔄 Daily",
            "biweekly": "📅 Biweekly",
            "weekly": "📆 Weekly",
            "monthly": "🗓️ Monthly",
            "quarterly": "📊 Quarterly",
            "yearly": "🎂 Yearly"
        }.get(task.frequency, task.frequency)

        # Completion status
        status_icon = "✅ Done" if task.completed else "⏳ Pending"

        task_data.append({
            "#": i,
            "Pet": task.pet_name if task.pet_name else "—",
            "Time": time_str,
            "Task": task.name,
            "Duration": f"{task.duration} min",
            "Priority": task.priority.capitalize(),
            "Recurrence": freq_display,
            "Status": status_icon
        })

    st.dataframe(task_data, use_container_width=True, hide_index=True)

    # Task completion section
    st.markdown("**Mark tasks as complete:**")

    # Show pending tasks with completion buttons
    pending_tasks = [t for t in display_tasks if not t.completed]
    if pending_tasks:
        cols = st.columns(min(len(pending_tasks), 3))
        for idx, task in enumerate(pending_tasks):
            with cols[idx % 3]:
                if st.button(f"✓ {task.name[:20]}", key=f"complete_{task.task_id}", use_container_width=True):
                    # Mark task as complete
                    next_task = task.mark_complete()

                    # If recurring, add the next occurrence
                    if next_task:
                        st.session_state.tasks.append(next_task)
                        st.success(f"✅ {task.name} completed! Next occurrence: {next_task.due_date}")
                    else:
                        st.success(f"✅ {task.name} marked as complete!")

                    st.rerun()
    else:
        st.info("🎉 All tasks completed!")

    # Button to clear all tasks
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Tasks", use_container_width=True):
            st.session_state.tasks = []
            st.session_state.schedules = {}
            st.rerun()
    with col2:
        if st.button("🔄 Reset Completed", use_container_width=True):
            for task in st.session_state.tasks:
                task.completed = False
            st.success("✅ All tasks reset to pending!")
            st.rerun()
else:
    st.info("📝 No tasks yet. Add one above to get started!")

st.divider()

# ===== Schedule Generation Section =====
st.subheader("📅 Generate Schedule")
st.caption("Create an optimized daily schedule based on priorities and time constraints")

# Schedule generation options
col1, col2 = st.columns([2, 1])
with col1:
    schedule_mode = st.radio(
        "Generate schedule for:",
        ["Selected Pet Only", "All Pets"],
        horizontal=True,
        help="Generate schedules for one pet or all your pets"
    )
with col2:
    pass  # Reserved for future options

# Display current constraints
st.markdown("**Current Settings:**")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Owner", st.session_state.owner.name if st.session_state.owner else "N/A")
with col2:
    st.metric("Available Time", f"{time_available} min")
with col3:
    if schedule_mode == "Selected Pet Only":
        if st.session_state.selected_pet:
            pet_tasks = [t for t in st.session_state.tasks if t.pet_name == st.session_state.selected_pet]
            st.metric(f"Tasks for {st.session_state.selected_pet}", len(pet_tasks))
        else:
            st.metric("Tasks", "No pet selected")
    else:
        st.metric("Total Tasks", len(st.session_state.tasks))
        st.metric("Total Pets", len(st.session_state.pets))

# Generate Schedule button - calls actual Scheduler
if st.button("🚀 Generate Schedule", type="primary", use_container_width=True):
    if not st.session_state.tasks:
        st.warning("⚠️ Please add at least one task before generating a schedule.")
    elif not st.session_state.owner:
        st.error("❌ Owner information is required.")
    elif schedule_mode == "Selected Pet Only" and not st.session_state.selected_pet:
        st.error("❌ Please select a pet first.")
    elif not st.session_state.pets:
        st.error("❌ Please add at least one pet.")
    else:
        try:
            st.session_state.schedules = {}  # Clear old schedules

            if schedule_mode == "Selected Pet Only":
                # Generate schedule for selected pet only
                selected_pet_obj = next((p for p in st.session_state.pets if p.name == st.session_state.selected_pet), None)
                if selected_pet_obj:
                    pet_tasks = [t for t in st.session_state.tasks if t.pet_name == st.session_state.selected_pet]

                    scheduler = Scheduler(
                        owner=st.session_state.owner,
                        pet=selected_pet_obj,
                        tasks=pet_tasks
                    )

                    st.session_state.schedules[st.session_state.selected_pet] = scheduler.generate_schedule()
                    st.success(f"✅ Schedule generated for {st.session_state.selected_pet}!")
            else:
                # Generate schedules for all pets
                for pet in st.session_state.pets:
                    pet_tasks = [t for t in st.session_state.tasks if t.pet_name == pet.name]

                    if pet_tasks:  # Only generate if pet has tasks
                        scheduler = Scheduler(
                            owner=st.session_state.owner,
                            pet=pet,
                            tasks=pet_tasks
                        )

                        st.session_state.schedules[pet.name] = scheduler.generate_schedule()

                if st.session_state.schedules:
                    st.success(f"✅ Schedules generated for {len(st.session_state.schedules)} pet(s)!")
                    st.balloons()
                else:
                    st.warning("⚠️ No pets have tasks to schedule.")

        except Exception as e:
            st.error(f"❌ Error generating schedule: {e}")

st.divider()

# ===== Display Schedule Results =====
if st.session_state.schedules:
    st.subheader("📊 Your Daily Schedule(s)")

    # Display schedule for each pet
    for pet_name, schedule in st.session_state.schedules.items():
        st.markdown(f"### 🐾 {pet_name}'s Schedule")



        # Display summary metrics for this pet
        col1, col2, col3 = st.columns(3)
        with col1:
            pet_task_count = len([t for t in st.session_state.tasks if t.pet_name == pet_name])
            st.metric(
                "Tasks Scheduled",
                len(schedule.scheduled_tasks),
                delta=f"{len(schedule.scheduled_tasks)} / {pet_task_count}"
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

        # Extract and display conflicts prominently
        # Check if explanation contains conflicts
        if "SCHEDULING CONFLICTS DETECTED" in schedule.explanation:
            # Extract conflict lines from explanation
            explanation_lines = schedule.explanation.split("\n")
            conflict_section = False
            for line in explanation_lines:
                if "SCHEDULING CONFLICTS DETECTED" in line:
                    conflict_section = True
                    st.warning("**⚠️ Scheduling Conflicts Detected:**")
                elif conflict_section and line.strip().startswith("⚠️"):
                    st.warning(line.strip())
                elif conflict_section and not line.strip():
                    break

        # Warning if not feasible
        if not schedule.is_feasible():
            st.error("⚠️ **Warning:** This schedule exceeds your available time! Consider removing low-priority tasks or increasing available time.")

        # Display scheduled tasks with enhanced formatting
        if schedule.scheduled_tasks:
            st.markdown("**📝 Scheduled Tasks**")

            # Sort scheduled tasks chronologically if they have times
            from pawpal_system import parse_time_to_minutes
            sorted_tasks = sorted(
                schedule.scheduled_tasks,
                key=lambda t: parse_time_to_minutes(t.preferred_time) if t.preferred_time else 1440
            )

            task_table = []
            cumulative_time = 0
            for i, task in enumerate(sorted_tasks, 1):
                cumulative_time += task.duration

                # Format time display
                time_display = task.preferred_time if task.preferred_time else "Flexible"

                # Priority with color emoji
                priority_emoji = {
                    "high": "🔴",
                    "medium": "🟡",
                    "low": "🟢"
                }.get(task.priority, "⚪")

                # Recurrence badge
                freq_badge = {
                    "once": "",
                    "daily": "🔄",
                    "biweekly": "📅",
                    "weekly": "📆",
                    "monthly": "🗓️",
                    "quarterly": "📊",
                    "yearly": "🎂"
                }.get(task.frequency, "")

                task_table.append({
                    "Order": i,
                    "Time": time_display,
                    "Task": f"{task.name} {freq_badge}",
                    "Duration": f"{task.duration} min",
                    "Priority": f"{priority_emoji} {task.priority.capitalize()}",
                    "Cumulative": f"{cumulative_time} min"
                })

            st.dataframe(task_table, use_container_width=True, hide_index=True)

            # Success message
            if schedule.is_feasible():
                st.success(f"✅ Schedule is feasible! All {len(sorted_tasks)} tasks fit within {schedule.owner.time_available} minutes.")

        # Display explanation
        st.markdown("**💡 Explanation**")
        with st.expander("View Scheduling Rationale"):
            st.info(schedule.explanation)

        st.divider()  # Separator between pets' schedules

else:
    st.info("👆 Click 'Generate Schedule' above to create your optimized daily plan!")

st.divider()

# ===== Footer =====
st.caption("🐾 PawPal+ | AI110 Module 2 Project")
