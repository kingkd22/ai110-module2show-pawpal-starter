"""
PawPal+ Scheduling System

Core classes for managing pet care tasks and generating daily schedules.
"""

from dataclasses import dataclass, field
from datetime import date as date_type, timedelta
from typing import Optional, ClassVar
import uuid


@dataclass
class Owner:
    """Represents a pet owner with time constraints and preferences."""

    name: str
    time_available: int = 480  # minutes, default 8 hours
    preferences: dict = field(default_factory=dict)

    def get_available_time(self) -> int:
        """Return the available time in minutes."""
        return self.time_available

    def set_available_time(self, time: int) -> None:
        """Set the available time in minutes."""
        if time < 0:
            raise ValueError("Available time cannot be negative")
        self.time_available = time

    def update_preferences(self, **kwargs) -> None:
        """Update owner preferences."""
        self.preferences.update(kwargs)

    def has_time_for(self, duration: int) -> bool:
        """Check if owner has enough time for a task of given duration."""
        return self.time_available >= duration


@dataclass
class Pet:
    """Represents a pet with basic information."""

    name: str
    type: str
    breed: str = ""
    age: int = 0
    special_needs: list = field(default_factory=list)
    tasks: list = field(default_factory=list)

    def get_info(self) -> str:
        """Return pet information as a formatted string."""
        info = f"{self.name} ({self.type})"
        if self.breed:
            info += f", Breed: {self.breed}"
        if self.age > 0:
            info += f", Age: {self.age}"
        if self.special_needs:
            info += f", Special needs: {', '.join(str(n) for n in self.special_needs)}"
        return info

    def update_info(self, **kwargs) -> None:
        """Update pet information."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def add_task(self, task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def get_task_count(self) -> int:
        """Return the number of tasks assigned to this pet."""
        return len(self.tasks)

    def __str__(self) -> str:
        """Return string representation of the pet."""
        return f"{self.name} the {self.type}"


@dataclass
class CareTask:
    """Represents a single pet care task with priority and duration."""

    # Class constants for validation (defined before instance fields)
    VALID_PRIORITIES: ClassVar[list[str]] = ["low", "medium", "high"]
    PRIORITY_VALUES: ClassVar[dict[str, int]] = {"high": 3, "medium": 2, "low": 1}
    VALID_FREQUENCIES: ClassVar[list[str]] = ["once", "daily", "biweekly", "weekly", "monthly", "quarterly", "yearly"]
    FREQUENCY_DAYS: ClassVar[dict[str, int]] = {
        "daily": 1,
        "biweekly": 14,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365
    }

    # Instance fields
    name: str
    duration: int
    priority: str
    task_type: str = ""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    preferred_time: Optional[str] = None
    notes: str = ""
    completed: bool = False
    frequency: str = "once"  # "once", "daily", "weekly"
    due_date: Optional[date_type] = None  # When the task is due

    def __post_init__(self):
        """Validate task after initialization."""
        # Normalize priority to lowercase
        self.priority = self.priority.lower()

        # Set task_type to name if not provided
        if not self.task_type:
            self.task_type = self.name

        # Validate the task
        if not self.is_valid():
            raise ValueError(f"Invalid task: {self._get_validation_errors()}")

    def get_duration(self) -> int:
        """Return task duration in minutes."""
        return self.duration

    def get_priority(self) -> str:
        """Return task priority as string."""
        return self.priority

    def get_priority_value(self) -> int:
        """Return numeric priority value for sorting (high=3, medium=2, low=1)."""
        return self.PRIORITY_VALUES.get(self.priority, 1)

    def update_task(self, **kwargs) -> None:
        """Update task attributes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

        # Re-validate after update
        if not self.is_valid():
            raise ValueError(f"Update would make task invalid: {self._get_validation_errors()}")

    def is_valid(self) -> bool:
        """Validate that task has required fields and valid values."""
        return (
            len(self.name) > 0 and
            self.duration > 0 and
            self.priority in self.VALID_PRIORITIES
        )

    def _get_validation_errors(self) -> str:
        """Helper method to get validation error messages."""
        errors = []
        if len(self.name) == 0:
            errors.append("name cannot be empty")
        if self.duration <= 0:
            errors.append(f"duration must be positive (got {self.duration})")
        if self.priority not in self.VALID_PRIORITIES:
            errors.append(f"priority must be one of {self.VALID_PRIORITIES} (got '{self.priority}')")
        return ", ".join(errors)

    def _get_next_due_date(self) -> Optional[date_type]:
        """Calculate next due date based on task frequency.

        Uses FREQUENCY_DAYS mapping for O(1) lookup. Returns None for
        non-recurring tasks or unrecognized frequencies.

        Returns:
            Next due date, or None if task is not recurring.
        """
        days_to_add = self.FREQUENCY_DAYS.get(self.frequency)
        if days_to_add is None:
            return None

        base_date = self.due_date or date_type.today()
        return base_date + timedelta(days=days_to_add)

    def mark_complete(self) -> Optional['CareTask']:
        """Mark the task as completed.

        For recurring tasks (daily/weekly), automatically creates a new instance
        for the next occurrence using the helper method _get_next_due_date().

        Returns:
            New CareTask instance if task is recurring, None otherwise.
        """
        self.completed = True

        # Early return for non-recurring tasks
        if self.frequency == "once":
            return None

        # Calculate next due date using helper
        next_due_date = self._get_next_due_date()
        if next_due_date is None:
            return None

        # Create new task instance for next occurrence
        return CareTask(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            task_type=self.task_type,
            preferred_time=self.preferred_time,
            notes=self.notes,
            frequency=self.frequency,
            due_date=next_due_date
        )

    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return self.completed

    def __str__(self) -> str:
        """Return string representation of the task."""
        status = "✓" if self.completed else " "
        return f"[{status}] {self.name} ({self.duration} min, {self.priority} priority)"


class Schedule:
    """Represents a daily care schedule with tasks and explanations."""

    def __init__(self, owner: Owner, pet: Pet, date=None):
        """Initialize a schedule for a specific owner, pet, and date."""
        self.date = date if date else date_type.today().isoformat()
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: list[CareTask] = []
        self.total_duration: int = 0
        self.explanation: str = ""

    def add_task(self, task: CareTask, time_slot=None) -> None:
        """Add a task to the schedule.

        Args:
            task: CareTask to add
            time_slot: Optional time slot (currently unused, reserved for future enhancement)

        Raises:
            ValueError: If task with same ID already exists in schedule
        """
        # Check for duplicate task ID
        if any(t.task_id == task.task_id for t in self.scheduled_tasks):
            raise ValueError(f"Task with ID {task.task_id} already exists in schedule")

        self.scheduled_tasks.append(task)
        self.calculate_total_duration()

    def remove_task(self, task_id: str) -> None:
        """Remove a task from the schedule by ID."""
        self.scheduled_tasks = [t for t in self.scheduled_tasks if t.task_id != task_id]
        self.calculate_total_duration()

    def get_schedule(self) -> list[CareTask]:
        """Return the list of scheduled tasks."""
        return self.scheduled_tasks

    def calculate_total_duration(self) -> int:
        """Calculate and return total duration of all scheduled tasks."""
        self.total_duration = sum(task.duration for task in self.scheduled_tasks)
        return self.total_duration

    def generate_explanation(self) -> str:
        """Generate human-readable explanation of the schedule."""
        if not self.scheduled_tasks:
            self.explanation = "No tasks scheduled."
            return self.explanation

        parts = []
        parts.append(f"Schedule for {self.pet.name} (Owner: {self.owner.name})")
        parts.append(f"Date: {self.date}")
        parts.append(f"Total time: {self.total_duration} of {self.owner.time_available} minutes available")

        parts.append(f"\nTasks ordered by priority:")
        for i, task in enumerate(self.scheduled_tasks, 1):
            parts.append(f"{i}. {task.name} ({task.duration} min, {task.priority} priority)")

        if not self.is_feasible():
            parts.append("\n⚠️  WARNING: Schedule exceeds available time!")

        self.explanation = "\n".join(parts)
        return self.explanation

    def is_feasible(self) -> bool:
        """Check if schedule fits within owner's available time."""
        return self.total_duration <= self.owner.time_available

    def display(self) -> None:
        """Display the schedule in a formatted way."""
        print(self.generate_explanation())


class Scheduler:
    """Orchestrates schedule generation using constraints and priorities."""

    def __init__(self, owner: Owner, pet: Pet, tasks: Optional[list] = None):
        """Initialize scheduler with owner, pet, and optional task list."""
        self.owner = owner
        self.pet = pet
        self.tasks: list[CareTask] = tasks if tasks else []

    def generate_schedule(self) -> Schedule:
        """Generate an optimized schedule based on priorities and constraints.

        Algorithm: Priority-Based Greedy with Time Constraints
        1. Sort tasks by priority (high → low), then by duration (short → long)
        2. Filter tasks to fit within available time
        3. Create schedule and add selected tasks
        4. Generate explanation including excluded tasks
        """
        schedule = Schedule(self.owner, self.pet)

        # Handle empty task list
        if not self.tasks:
            schedule.explanation = "No tasks provided to schedule."
            return schedule

        # Step 1: Sort by priority
        sorted_tasks = self.sort_by_priority()

        # Step 2: Filter by time constraint
        selected_tasks, excluded_tasks = self.filter_by_time_constraint(sorted_tasks)

        # Step 3: Add selected tasks to schedule
        for task in selected_tasks:
            schedule.add_task(task)

        # Step 4: Generate explanation
        schedule.generate_explanation()

        # Add information about excluded tasks
        if excluded_tasks:
            exclusion_text = f"\n\nExcluded tasks due to time constraints:"
            for task in excluded_tasks:
                exclusion_text += f"\n  • {task.name} ({task.duration} min, {task.priority} priority)"
            schedule.explanation += exclusion_text

        # Step 5: Detect and report conflicts
        conflicts = self.detect_conflicts(selected_tasks)
        if conflicts:
            conflict_text = f"\n\n⚠️  SCHEDULING CONFLICTS DETECTED:"
            for conflict in conflicts:
                conflict_text += f"\n  {conflict}"
            schedule.explanation += conflict_text

        return schedule

    def sort_by_priority(self) -> list[CareTask]:
        """Sort tasks by priority (high to low), then by duration (short to long).

        This ensures:
        - High priority tasks are scheduled first
        - Among same priority, shorter tasks come first (better packing)
        """
        return sorted(
            self.tasks,
            key=lambda t: (-t.get_priority_value(), t.duration)
        )

    def sort_by_time(self) -> list[CareTask]:
        """Sort tasks by preferred_time in HH:MM format.

        Tasks without preferred_time (None) are placed at the end.
        Uses lambda function to parse time strings for sorting.
        """
        def time_sort_key(task: CareTask) -> tuple:
            # If no preferred_time, use a large value to sort to end
            if task.preferred_time is None:
                return (24, 0)  # Represents end of day

            # Parse "HH:MM" format
            try:
                time_parts = task.preferred_time.split(":")
                hours = int(time_parts[0])
                minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                return (hours, minutes)
            except (ValueError, AttributeError):
                # If parsing fails, sort to end
                return (24, 0)

        return sorted(self.tasks, key=time_sort_key)

    def filter_by_time_constraint(self, sorted_tasks: list[CareTask]) -> tuple[list[CareTask], list[CareTask]]:
        """Filter tasks to fit within available time.

        Greedy algorithm: iterate through sorted tasks and add each task
        if it fits within remaining time.

        Returns:
            tuple: (selected_tasks, excluded_tasks)
        """
        running_time = 0
        selected = []
        excluded = []

        for task in sorted_tasks:
            if running_time + task.duration <= self.owner.time_available:
                selected.append(task)
                running_time += task.duration
            else:
                excluded.append(task)

        return selected, excluded

    def optimize_order(self, filtered_tasks: list[CareTask]) -> list[CareTask]:
        """Optimize the order of tasks.

        Currently a placeholder for future enhancements like:
        - Time-window preferences
        - Task dependencies
        - Logical ordering (e.g., walk before feeding)

        For now, returns tasks as-is (already sorted by priority).
        """
        return filtered_tasks

    def filter_by_completion(self, completed: bool = False) -> list[CareTask]:
        """Filter tasks by completion status.

        Args:
            completed: If True, return only completed tasks.
                      If False, return only pending tasks.

        Returns:
            List of tasks matching the completion status.
        """
        return [task for task in self.tasks if task.is_completed() == completed]

    def filter_by_pet_name(self, pet_name: str) -> list[CareTask]:
        """Filter tasks by pet name.

        Note: This uses the scheduler's pet attribute to check if tasks
        belong to the specified pet.

        Args:
            pet_name: Name of the pet to filter by.

        Returns:
            List of tasks if pet name matches, empty list otherwise.
        """
        if self.pet and self.pet.name.lower() == pet_name.lower():
            return self.tasks
        return []

    def detect_conflicts(self, tasks_to_check: list[CareTask]) -> list[str]:
        """Identify scheduling conflicts between tasks.

        Lightweight conflict detection strategy that checks for:
        - Tasks with the same preferred_time (exact time collision)
        - Tasks with overlapping time windows (start time + duration)

        Args:
            tasks_to_check: List of tasks to check for conflicts

        Returns:
            List of warning messages describing conflicts (empty if no conflicts)
        """
        conflicts = []

        # Only check tasks that have preferred_time set
        timed_tasks = [t for t in tasks_to_check if t.preferred_time is not None]

        # Check each pair of tasks for conflicts
        for i, task1 in enumerate(timed_tasks):
            for task2 in timed_tasks[i + 1:]:
                # Parse time for both tasks
                try:
                    time1_parts = task1.preferred_time.split(":")
                    hours1 = int(time1_parts[0])
                    minutes1 = int(time1_parts[1]) if len(time1_parts) > 1 else 0
                    start1_minutes = hours1 * 60 + minutes1
                    end1_minutes = start1_minutes + task1.duration

                    time2_parts = task2.preferred_time.split(":")
                    hours2 = int(time2_parts[0])
                    minutes2 = int(time2_parts[1]) if len(time2_parts) > 1 else 0
                    start2_minutes = hours2 * 60 + minutes2
                    end2_minutes = start2_minutes + task2.duration

                    # Check for time overlap
                    # Overlap occurs if: task1 starts before task2 ends AND task2 starts before task1 ends
                    if start1_minutes < end2_minutes and start2_minutes < end1_minutes:
                        # Format the conflict message
                        if start1_minutes == start2_minutes:
                            # Exact same start time
                            conflict_msg = (
                                f"⚠️  TIME CONFLICT: '{task1.name}' and '{task2.name}' "
                                f"both scheduled at {task1.preferred_time}"
                            )
                        else:
                            # Overlapping time windows
                            conflict_msg = (
                                f"⚠️  TIME OVERLAP: '{task1.name}' ({task1.preferred_time}, "
                                f"{task1.duration} min) overlaps with '{task2.name}' "
                                f"({task2.preferred_time}, {task2.duration} min)"
                            )
                        conflicts.append(conflict_msg)

                except (ValueError, AttributeError, IndexError):
                    # If time parsing fails, skip this pair
                    continue

        return conflicts

    def handle_conflicts(self) -> list[str]:
        """Identify and handle scheduling conflicts.

        Checks all tasks in the scheduler for time conflicts and returns
        warning messages without crashing the program.

        Returns:
            List of conflict warning messages (empty if no conflicts)
        """
        return self.detect_conflicts(self.tasks)
