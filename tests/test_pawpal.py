"""
Simple tests for PawPal+ scheduling system.
"""

from pawpal_system import Pet, CareTask


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


if __name__ == "__main__":
    # Run tests directly if called as script
    print("Running Test 1: Task Completion")
    test_task_completion()
    print("✅ Test 1 passed!\n")

    print("Running Test 2: Task Addition to Pet")
    test_task_addition_to_pet()
    print("✅ Test 2 passed!\n")

    print("All tests passed! 🎉")
