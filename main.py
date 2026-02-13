"""
PawPal+ Testing Ground

Quick script to test the scheduling system in the terminal.
"""

from pawpal_system import Owner, Pet, CareTask, Schedule, Scheduler


def main():
    print("=" * 60)
    print("🐾 PawPal+ Scheduling System - Testing Ground")
    print("=" * 60)
    print()

    # Create an Owner
    owner = Owner(name="Alice", time_available=120)  # 2 hours available
    print(f"Owner: {owner.name}")
    print(f"Available time: {owner.time_available} minutes")
    print()

    # Create two Pets
    pet1 = Pet(name="Buddy", type="dog", breed="Golden Retriever", age=3)
    pet2 = Pet(name="Whiskers", type="cat", breed="Siamese", age=2)

    print("Pets:")
    print(f"  1. {pet1.get_info()}")
    print(f"  2. {pet2.get_info()}")
    print()

    # Create tasks for Buddy (dog)
    print("=" * 60)
    print("📋 Creating Tasks for Buddy")
    print("=" * 60)

    buddy_tasks = [
        CareTask(name="Morning Walk", duration=30, priority="high"),
        CareTask(name="Feed Breakfast", duration=10, priority="high"),
        CareTask(name="Training Session", duration=45, priority="medium"),
        CareTask(name="Brush Fur", duration=20, priority="low"),
        CareTask(name="Play Fetch", duration=25, priority="medium"),
    ]

    print(f"\nCreated {len(buddy_tasks)} tasks for Buddy:")
    for i, task in enumerate(buddy_tasks, 1):
        print(f"  {i}. {task}")
    print()

    # Generate schedule for Buddy
    print("=" * 60)
    print("📅 Today's Schedule for Buddy")
    print("=" * 60)
    print()

    scheduler_buddy = Scheduler(owner=owner, pet=pet1, tasks=buddy_tasks)
    schedule_buddy = scheduler_buddy.generate_schedule()

    print(schedule_buddy.explanation)
    print()

    # Create tasks for Whiskers (cat)
    print("=" * 60)
    print("📋 Creating Tasks for Whiskers")
    print("=" * 60)

    whiskers_tasks = [
        CareTask(name="Feed Wet Food", duration=5, priority="high"),
        CareTask(name="Clean Litter Box", duration=10, priority="high"),
        CareTask(name="Play with Toys", duration=20, priority="medium"),
        CareTask(name="Grooming", duration=15, priority="low"),
    ]

    print(f"\nCreated {len(whiskers_tasks)} tasks for Whiskers:")
    for i, task in enumerate(whiskers_tasks, 1):
        print(f"  {i}. {task}")
    print()

    # Generate schedule for Whiskers (with same owner time budget)
    print("=" * 60)
    print("📅 Today's Schedule for Whiskers")
    print("=" * 60)
    print()

    scheduler_whiskers = Scheduler(owner=owner, pet=pet2, tasks=whiskers_tasks)
    schedule_whiskers = scheduler_whiskers.generate_schedule()

    print(schedule_whiskers.explanation)
    print()

    # Summary
    print("=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"\nBuddy's Schedule:")
    print(f"  Tasks scheduled: {len(schedule_buddy.scheduled_tasks)}")
    print(f"  Total time: {schedule_buddy.total_duration} minutes")
    print(f"  Feasible: {'✅ Yes' if schedule_buddy.is_feasible() else '❌ No'}")

    print(f"\nWhiskers' Schedule:")
    print(f"  Tasks scheduled: {len(schedule_whiskers.scheduled_tasks)}")
    print(f"  Total time: {schedule_whiskers.total_duration} minutes")
    print(f"  Feasible: {'✅ Yes' if schedule_whiskers.is_feasible() else '❌ No'}")
    print()

    # Test edge case: Over capacity
    print("=" * 60)
    print("⚠️  Testing Edge Case: Over Capacity")
    print("=" * 60)
    print()

    # Create owner with limited time
    busy_owner = Owner(name="Jordan", time_available=30)
    pet3 = Pet(name="Max", type="dog")

    overflow_tasks = [
        CareTask(name="Long Walk", duration=60, priority="high"),
        CareTask(name="Training", duration=45, priority="medium"),
        CareTask(name="Play", duration=20, priority="low"),
    ]

    print(f"Owner: {busy_owner.name} (only {busy_owner.time_available} minutes available)")
    print(f"Attempting to schedule {len(overflow_tasks)} tasks totaling {sum(t.duration for t in overflow_tasks)} minutes...")
    print()

    scheduler_overflow = Scheduler(owner=busy_owner, pet=pet3, tasks=overflow_tasks)
    schedule_overflow = scheduler_overflow.generate_schedule()

    print(schedule_overflow.explanation)
    print()

    print("=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
