"""
Simple tests for PawPal+ scheduling system.
"""

from pawpal_system import Owner, Pet, CareTask, Scheduler, parse_time_to_minutes
from datetime import date as date_type, timedelta


def test_task_completion():
    """
    Task Completion Test: Verify that calling mark_complete()
    actually changes the task's status.
    """
    # Arrange: Create a task
    task = CareTask(name="Walk Dog", duration=30, priority="high")

    # Assert: Task starts as not completed
    assert task.completed is False
    assert task.is_completed() is False

    # Act: Mark task as complete
    task.mark_complete()

    # Assert: Task is now completed
    assert task.completed is True
    assert task.is_completed() is True


def test_task_addition_to_pet():
    """
    Task Addition Test: Verify that adding a task to a Pet
    increases that pet's task count.
    """
    # Arrange: Create a pet
    pet = Pet(name="Buddy", type="dog")

    # Assert: Pet starts with 0 tasks
    assert pet.get_task_count() == 0
    assert len(pet.tasks) == 0

    # Act: Add a task to the pet
    task1 = CareTask(name="Morning Walk", duration=30, priority="high")
    pet.add_task(task1)

    # Assert: Pet now has 1 task
    assert pet.get_task_count() == 1
    assert len(pet.tasks) == 1

    # Act: Add another task
    task2 = CareTask(name="Feed Breakfast", duration=10, priority="high")
    pet.add_task(task2)

    # Assert: Pet now has 2 tasks
    assert pet.get_task_count() == 2
    assert len(pet.tasks) == 2

    # Assert: Tasks are actually in the list
    assert task1 in pet.tasks
    assert task2 in pet.tasks


def test_recurring_task_daily():
    """
    Recurring Task Test: Verify that marking a daily task complete
    creates a new instance with next due date (+1 day).
    """
    # Arrange: Create a daily recurring task
    today = date_type.today()
    task = CareTask(
        name="Morning Walk",
        duration=30,
        priority="high",
        frequency="daily",
        due_date=today
    )

    # Assert: Task starts as not completed
    assert task.is_completed() is False
    assert task.frequency == "daily"
    assert task.due_date == today

    # Act: Mark task as complete
    next_task = task.mark_complete()

    # Assert: Original task is completed
    assert task.is_completed() is True

    # Assert: New task was created
    assert next_task is not None
    assert next_task.name == task.name
    assert next_task.is_completed() is False
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.task_id != task.task_id  # Different ID


def test_recurring_task_weekly():
    """
    Recurring Task Test: Verify that marking a weekly task complete
    creates a new instance with next due date (+7 days).
    """
    # Arrange: Create a weekly recurring task
    today = date_type.today()
    task = CareTask(
        name="Vet Checkup",
        duration=60,
        priority="high",
        frequency="weekly",
        due_date=today
    )

    # Act: Mark task as complete
    next_task = task.mark_complete()

    # Assert: New task created with +7 days
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=7)
    assert next_task.frequency == "weekly"


def test_recurring_task_once():
    """
    Recurring Task Test: Verify that marking a one-time task complete
    does NOT create a new instance.
    """
    # Arrange: Create a one-time task
    task = CareTask(
        name="Grooming",
        duration=45,
        priority="medium",
        frequency="once"
    )

    # Act: Mark task as complete
    next_task = task.mark_complete()

    # Assert: No new task created
    assert next_task is None
    assert task.is_completed() is True


def test_conflict_detection_exact_time():
    """
    Conflict Detection Test: Verify that two tasks with the same
    preferred_time are detected as conflicts.
    """
    # Arrange: Create owner, pet, and tasks with same start time
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Walk", duration=30, priority="high", preferred_time="08:00"),
        CareTask(name="Feed", duration=15, priority="high", preferred_time="08:00"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: Conflict detected
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]
    assert "08:00" in conflicts[0]


def test_conflict_detection_overlap():
    """
    Conflict Detection Test: Verify that two tasks with overlapping
    time windows are detected as conflicts.
    """
    # Arrange: Create tasks with overlapping windows
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Vet", duration=60, priority="high", preferred_time="14:00"),  # 14:00-15:00
        CareTask(name="Groom", duration=45, priority="medium", preferred_time="14:30"),  # 14:30-15:15
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: Overlap detected
    assert len(conflicts) == 1
    assert "Vet" in conflicts[0]
    assert "Groom" in conflicts[0]


def test_conflict_detection_no_conflicts():
    """
    Conflict Detection Test: Verify that well-spaced tasks with no
    overlap do NOT generate false positives.
    """
    # Arrange: Create well-spaced tasks
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Morning Walk", duration=30, priority="high", preferred_time="07:00"),
        CareTask(name="Lunch", duration=10, priority="high", preferred_time="12:00"),
        CareTask(name="Evening Walk", duration=30, priority="medium", preferred_time="18:00"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: No conflicts
    assert len(conflicts) == 0


def test_conflict_detection_no_times():
    """
    Conflict Detection Test: Verify that tasks without preferred_time
    do NOT generate false conflicts.
    """
    # Arrange: Create tasks without preferred times
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Brush", duration=20, priority="low"),
        CareTask(name="Trim Nails", duration=15, priority="low"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: No conflicts (no times to conflict)
    assert len(conflicts) == 0


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_sort_by_time_chronological_order():
    """
    Sorting Correctness: Verify tasks are returned in chronological order.
    """
    # Arrange: Create tasks out of order
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Dinner", duration=15, priority="high", preferred_time="18:00"),
        CareTask(name="Breakfast", duration=10, priority="high", preferred_time="07:00"),
        CareTask(name="Lunch", duration=10, priority="high", preferred_time="12:00"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Sort by time
    sorted_tasks = scheduler.sort_by_time()

    # Assert: Tasks are in chronological order
    assert sorted_tasks[0].preferred_time == "07:00"
    assert sorted_tasks[1].preferred_time == "12:00"
    assert sorted_tasks[2].preferred_time == "18:00"


def test_sort_by_time_with_none_values():
    """
    Edge Case: Tasks without preferred_time should be sorted to end.
    """
    # Arrange: Mix of timed and untimed tasks
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Timed 1", duration=10, priority="high", preferred_time="10:00"),
        CareTask(name="No Time", duration=15, priority="low"),
        CareTask(name="Timed 2", duration=10, priority="high", preferred_time="08:00"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Sort by time
    sorted_tasks = scheduler.sort_by_time()

    # Assert: Timed tasks first, then untimed
    assert sorted_tasks[0].preferred_time == "08:00"
    assert sorted_tasks[1].preferred_time == "10:00"
    assert sorted_tasks[2].preferred_time is None


def test_recurring_daily_without_due_date():
    """
    Recurrence Edge Case: Daily task without due_date should use today.
    """
    # Arrange: Daily task with no due_date
    today = date_type.today()
    task = CareTask(
        name="Daily Medication",
        duration=5,
        priority="high",
        frequency="daily"
    )

    # Act: Mark complete
    next_task = task.mark_complete()

    # Assert: Next task uses today as base
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)


def test_recurring_task_chain():
    """
    Recurrence Logic: Completing recurring tasks multiple times creates chain.
    """
    # Arrange: Daily task
    today = date_type.today()
    task = CareTask(
        name="Morning Walk",
        duration=30,
        priority="high",
        frequency="daily",
        due_date=today
    )

    # Act: Complete 3 times in chain
    current = task
    for day in range(1, 4):
        next_task = current.mark_complete()
        assert next_task is not None
        assert next_task.due_date == today + timedelta(days=day)
        current = next_task


def test_recurring_task_preserves_attributes():
    """
    Recurrence Logic: Next occurrence should preserve all task attributes.
    """
    # Arrange: Task with many attributes
    today = date_type.today()
    original = CareTask(
        name="Special Task",
        duration=45,
        priority="high",
        task_type="medication",
        preferred_time="08:00",
        notes="Give with food",
        frequency="daily",
        due_date=today
    )

    # Act: Mark complete
    next_task = original.mark_complete()

    # Assert: All attributes preserved except completed and due_date
    assert next_task.name == original.name
    assert next_task.duration == original.duration
    assert next_task.priority == original.priority
    assert next_task.task_type == original.task_type
    assert next_task.preferred_time == original.preferred_time
    assert next_task.notes == original.notes
    assert next_task.frequency == original.frequency
    assert next_task.completed is False
    assert next_task.task_id != original.task_id


def test_conflict_detection_multiple_collisions():
    """
    Conflict Detection: Multiple tasks at exact same time should all be flagged.
    """
    # Arrange: 3 tasks at same time
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Task A", duration=20, priority="high", preferred_time="10:00"),
        CareTask(name="Task B", duration=30, priority="high", preferred_time="10:00"),
        CareTask(name="Task C", duration=15, priority="high", preferred_time="10:00"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: All pairs detected (3 tasks = 3 conflict pairs)
    assert len(conflicts) == 3


def test_conflict_detection_back_to_back():
    """
    Edge Case: Back-to-back tasks (no gap) should NOT conflict.
    """
    # Arrange: Adjacent tasks
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Task A", duration=30, priority="high", preferred_time="10:00"),
        CareTask(name="Task B", duration=30, priority="high", preferred_time="10:30"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: No conflicts for back-to-back tasks
    assert len(conflicts) == 0


def test_conflict_detection_one_minute_overlap():
    """
    Edge Case: Even 1 minute overlap should be detected.
    """
    # Arrange: Tasks with 1-minute overlap
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Task A", duration=30, priority="high", preferred_time="10:00"),
        CareTask(name="Task B", duration=30, priority="high", preferred_time="10:29"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Detect conflicts
    conflicts = scheduler.handle_conflicts()

    # Assert: 1-minute overlap detected
    assert len(conflicts) == 1


def test_pet_with_no_tasks():
    """
    Edge Case: Pet with no tasks should generate empty schedule.
    """
    # Arrange: Pet with empty task list
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    scheduler = Scheduler(owner=owner, pet=pet, tasks=[])

    # Act: Generate schedule
    schedule = scheduler.generate_schedule()

    # Assert: Empty schedule
    assert len(schedule.scheduled_tasks) == 0
    assert schedule.total_duration == 0


def test_zero_time_available():
    """
    Edge Case: Owner with 0 minutes available should exclude all tasks.
    """
    # Arrange: Owner with no time
    owner = Owner(name="Alice", time_available=0)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Walk", duration=30, priority="high"),
        CareTask(name="Feed", duration=10, priority="high"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Generate schedule
    schedule = scheduler.generate_schedule()

    # Assert: No tasks scheduled
    assert len(schedule.scheduled_tasks) == 0


def test_single_task_exactly_fits_time():
    """
    Edge Case: Task that exactly matches available time should be scheduled.
    """
    # Arrange: Owner with 30 minutes, task needs 30 minutes
    owner = Owner(name="Alice", time_available=30)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Perfect Fit", duration=30, priority="high"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Generate schedule
    schedule = scheduler.generate_schedule()

    # Assert: Task scheduled
    assert len(schedule.scheduled_tasks) == 1
    assert schedule.is_feasible()
    assert schedule.total_duration == 30


def test_high_priority_scheduled_before_low():
    """
    Happy Path: High priority tasks should be scheduled before low priority.
    """
    # Arrange: High and low priority tasks
    owner = Owner(name="Alice", time_available=100)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Low Priority", duration=20, priority="low"),
        CareTask(name="High Priority", duration=30, priority="high"),
        CareTask(name="Medium Priority", duration=25, priority="medium"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Generate schedule
    schedule = scheduler.generate_schedule()

    # Assert: Scheduled in priority order
    assert schedule.scheduled_tasks[0].priority == "high"
    assert schedule.scheduled_tasks[1].priority == "medium"
    assert schedule.scheduled_tasks[2].priority == "low"


def test_same_priority_shorter_task_first():
    """
    Scheduling Logic: Among same priority, shorter tasks should come first.
    """
    # Arrange: Same priority, different durations
    owner = Owner(name="Alice", time_available=100)
    pet = Pet(name="Buddy", type="dog")

    tasks = [
        CareTask(name="Long", duration=40, priority="high"),
        CareTask(name="Short", duration=10, priority="high"),
        CareTask(name="Medium", duration=25, priority="high"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

    # Act: Generate schedule
    schedule = scheduler.generate_schedule()

    # Assert: Same priority sorted by duration
    assert schedule.scheduled_tasks[0].duration == 10
    assert schedule.scheduled_tasks[1].duration == 25
    assert schedule.scheduled_tasks[2].duration == 40


def test_am_pm_time_parsing():
    """
    AM/PM Parsing Test: Verify that parse_time_to_minutes correctly
    handles both 12-hour (AM/PM) and 24-hour time formats.
    """
    # 12-hour format tests
    assert parse_time_to_minutes("12:00 AM") == 0  # Midnight
    assert parse_time_to_minutes("8:00 AM") == 480  # 8 AM
    assert parse_time_to_minutes("12:00 PM") == 720  # Noon
    assert parse_time_to_minutes("2:30 PM") == 870  # 2:30 PM
    assert parse_time_to_minutes("11:59 PM") == 1439  # 11:59 PM

    # 24-hour format tests
    assert parse_time_to_minutes("00:00") == 0  # Midnight
    assert parse_time_to_minutes("08:00") == 480  # 8 AM
    assert parse_time_to_minutes("12:00") == 720  # Noon
    assert parse_time_to_minutes("14:30") == 870  # 2:30 PM
    assert parse_time_to_minutes("23:59") == 1439  # 11:59 PM

    # Edge case: lowercase am/pm
    assert parse_time_to_minutes("8:00 am") == 480
    assert parse_time_to_minutes("2:00 pm") == 840  # 2:00 PM = 14:00 = 840 minutes


def test_am_pm_sorting():
    """
    AM/PM Sorting Test: Verify that tasks with mixed time formats
    (12-hour and 24-hour) sort correctly in chronological order.
    """
    owner = Owner(name="Alex", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    # Create tasks with mixed formats (intentionally out of order)
    tasks = [
        CareTask(name="Dinner", duration=20, priority="medium", preferred_time="6:00 PM"),
        CareTask(name="Breakfast", duration=15, priority="medium", preferred_time="7:00 AM"),
        CareTask(name="Lunch", duration=15, priority="medium", preferred_time="12:00 PM"),
        CareTask(name="Afternoon Snack", duration=10, priority="medium", preferred_time="15:00"),
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
    sorted_tasks = scheduler.sort_by_time()

    # Assert: Sorted chronologically
    assert sorted_tasks[0].name == "Breakfast"  # 7:00 AM
    assert sorted_tasks[1].name == "Lunch"  # 12:00 PM
    assert sorted_tasks[2].name == "Afternoon Snack"  # 15:00 (3 PM)
    assert sorted_tasks[3].name == "Dinner"  # 6:00 PM


def test_am_pm_conflict_detection():
    """
    AM/PM Conflict Test: Verify that conflict detection works correctly
    when tasks use different time formats (12-hour vs 24-hour).
    """
    owner = Owner(name="Jordan", time_available=300)
    pet = Pet(name="Max", type="dog")

    # Tasks that conflict using different time formats
    tasks = [
        CareTask(name="Walk", duration=30, priority="high", preferred_time="8:00 AM"),
        CareTask(name="Feed", duration=15, priority="high", preferred_time="08:15"),  # Overlaps with Walk
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
    conflicts = scheduler.detect_conflicts(tasks)

    # Assert: Conflict detected despite different time formats
    assert len(conflicts) == 1
    assert "Walk" in conflicts[0]
    assert "Feed" in conflicts[0]


def test_am_pm_exact_time_conflict():
    """
    AM/PM Exact Time Conflict Test: Verify that two tasks at the same time
    (one in 12-hour, one in 24-hour format) are detected as conflicts.
    """
    owner = Owner(name="Sam", time_available=200)
    pet = Pet(name="Luna", type="cat")

    tasks = [
        CareTask(name="Playtime", duration=20, priority="medium", preferred_time="2:00 PM"),
        CareTask(name="Training", duration=20, priority="medium", preferred_time="14:00"),  # Same time
    ]

    scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
    conflicts = scheduler.detect_conflicts(tasks)

    # Assert: Exact time conflict detected
    assert len(conflicts) == 1
    assert "CONFLICT" in conflicts[0]


if __name__ == "__main__":
    # Run all tests
    tests = [
        # Basic functionality
        ("Task Completion", test_task_completion),
        ("Task Addition to Pet", test_task_addition_to_pet),

        # Recurring tasks
        ("Recurring Task - Daily", test_recurring_task_daily),
        ("Recurring Task - Weekly", test_recurring_task_weekly),
        ("Recurring Task - Once", test_recurring_task_once),
        ("Recurring - No Due Date", test_recurring_daily_without_due_date),
        ("Recurring - Chain", test_recurring_task_chain),
        ("Recurring - Preserve Attributes", test_recurring_task_preserves_attributes),

        # Conflict detection
        ("Conflict - Exact Time", test_conflict_detection_exact_time),
        ("Conflict - Overlap", test_conflict_detection_overlap),
        ("Conflict - No Conflicts", test_conflict_detection_no_conflicts),
        ("Conflict - No Times", test_conflict_detection_no_times),
        ("Conflict - Multiple Collisions", test_conflict_detection_multiple_collisions),
        ("Conflict - Back-to-Back", test_conflict_detection_back_to_back),
        ("Conflict - 1 Min Overlap", test_conflict_detection_one_minute_overlap),

        # Sorting
        ("Sort - Chronological Order", test_sort_by_time_chronological_order),
        ("Sort - None Values", test_sort_by_time_with_none_values),

        # Edge cases
        ("Edge - No Tasks", test_pet_with_no_tasks),
        ("Edge - Zero Time", test_zero_time_available),
        ("Edge - Exact Fit", test_single_task_exactly_fits_time),

        # Priority scheduling
        ("Priority - High Before Low", test_high_priority_scheduled_before_low),
        ("Priority - Same Priority Order", test_same_priority_shorter_task_first),

        # AM/PM time format support
        ("AM/PM - Time Parsing", test_am_pm_time_parsing),
        ("AM/PM - Sorting", test_am_pm_sorting),
        ("AM/PM - Conflict Detection", test_am_pm_conflict_detection),
        ("AM/PM - Exact Time Conflict", test_am_pm_exact_time_conflict),
    ]

    passed = 0
    failed = 0

    print("=" * 70)
    print("🧪 Running PawPal+ Test Suite")
    print("=" * 70)
    print()

    for i, (name, test_func) in enumerate(tests, 1):
        try:
            test_func()
            print(f"✅ Test {i:2d}: {name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ Test {i:2d}: {name}")
            print(f"          Error: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 Test {i:2d}: {name}")
            print(f"          Exception: {e}")
            failed += 1

    print()
    print("=" * 70)
    print(f"📊 Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 70)

    if failed == 0:
        print("✅ All tests passed! 🎉")
    else:
        print(f"⚠️  {failed} test(s) need attention")
