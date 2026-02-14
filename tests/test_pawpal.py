"""
Simple tests for PawPal+ scheduling system.
"""

from pawpal_system import Owner, Pet, CareTask, Scheduler
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


if __name__ == "__main__":
    # Run tests directly if called as script
    print("Running Test 1: Task Completion")
    test_task_completion()
    print("✅ Test 1 passed!\n")

    print("Running Test 2: Task Addition to Pet")
    test_task_addition_to_pet()
    print("✅ Test 2 passed!\n")

    print("Running Test 3: Recurring Task - Daily")
    test_recurring_task_daily()
    print("✅ Test 3 passed!\n")

    print("Running Test 4: Recurring Task - Weekly")
    test_recurring_task_weekly()
    print("✅ Test 4 passed!\n")

    print("Running Test 5: Recurring Task - Once")
    test_recurring_task_once()
    print("✅ Test 5 passed!\n")

    print("Running Test 6: Conflict Detection - Exact Time")
    test_conflict_detection_exact_time()
    print("✅ Test 6 passed!\n")

    print("Running Test 7: Conflict Detection - Overlap")
    test_conflict_detection_overlap()
    print("✅ Test 7 passed!\n")

    print("Running Test 8: Conflict Detection - No Conflicts")
    test_conflict_detection_no_conflicts()
    print("✅ Test 8 passed!\n")

    print("Running Test 9: Conflict Detection - No Times")
    test_conflict_detection_no_times()
    print("✅ Test 9 passed!\n")

    print("All tests passed! 🎉")
