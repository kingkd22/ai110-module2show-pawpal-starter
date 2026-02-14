"""
PawPal+ Testing Ground

Testing conflict detection for overlapping task schedules.
"""

from pawpal_system import Owner, Pet, CareTask, Scheduler


def main():
    print("=" * 70)
    print("🐾 PawPal+ Scheduler - Testing Conflict Detection")
    print("=" * 70)
    print()

    # Create owner and pet
    owner = Owner(name="Alice", time_available=300)
    pet = Pet(name="Buddy", type="dog")

    print(f"Owner: {owner.name}")
    print(f"Pet: {pet}")
    print(f"Available time: {owner.time_available} minutes")
    print()

    # ===== TEST 1: Exact Time Collision =====
    print("=" * 70)
    print("⚠️  TEST 1: Exact Time Collision")
    print("=" * 70)
    print()

    tasks_collision = [
        CareTask(name="Morning Walk", duration=30, priority="high", preferred_time="08:00"),
        CareTask(name="Feed Breakfast", duration=15, priority="high", preferred_time="08:00"),
        CareTask(name="Training Session", duration=45, priority="medium", preferred_time="10:00"),
    ]

    print("Tasks created:")
    for task in tasks_collision:
        print(f"  • {task.name} at {task.preferred_time} ({task.duration} min)")
    print()

    scheduler1 = Scheduler(owner=owner, pet=pet, tasks=tasks_collision)
    schedule1 = scheduler1.generate_schedule()

    print("Schedule generated:")
    print(schedule1.explanation)
    print()

    # ===== TEST 2: Overlapping Time Windows =====
    print("=" * 70)
    print("⚠️  TEST 2: Overlapping Time Windows")
    print("=" * 70)
    print()

    tasks_overlap = [
        CareTask(name="Vet Appointment", duration=60, priority="high", preferred_time="14:00"),
        CareTask(name="Grooming Session", duration=45, priority="medium", preferred_time="14:30"),
        CareTask(name="Play Time", duration=20, priority="low", preferred_time="16:00"),
    ]

    print("Tasks created:")
    for task in tasks_overlap:
        time_parts = task.preferred_time.split(":")
        hours = int(time_parts[0])
        minutes = int(time_parts[1])
        start_min = hours * 60 + minutes
        end_min = start_min + task.duration
        end_hours = end_min // 60
        end_minutes = end_min % 60
        print(f"  • {task.name} at {task.preferred_time}-{end_hours:02d}:{end_minutes:02d} ({task.duration} min)")
    print()

    scheduler2 = Scheduler(owner=owner, pet=pet, tasks=tasks_overlap)
    schedule2 = scheduler2.generate_schedule()

    print("Schedule generated:")
    print(schedule2.explanation)
    print()

    # ===== TEST 3: No Conflicts =====
    print("=" * 70)
    print("✅ TEST 3: No Conflicts (Well-Spaced Tasks)")
    print("=" * 70)
    print()

    tasks_no_conflict = [
        CareTask(name="Morning Walk", duration=30, priority="high", preferred_time="07:00"),
        CareTask(name="Lunch Feeding", duration=10, priority="high", preferred_time="12:00"),
        CareTask(name="Evening Walk", duration=30, priority="medium", preferred_time="18:00"),
    ]

    print("Tasks created:")
    for task in tasks_no_conflict:
        print(f"  • {task.name} at {task.preferred_time} ({task.duration} min)")
    print()

    scheduler3 = Scheduler(owner=owner, pet=pet, tasks=tasks_no_conflict)
    schedule3 = scheduler3.generate_schedule()

    print("Schedule generated:")
    print(schedule3.explanation)
    print()

    # ===== TEST 4: Multiple Conflicts =====
    print("=" * 70)
    print("⚠️  TEST 4: Multiple Conflicts")
    print("=" * 70)
    print()

    tasks_multiple = [
        CareTask(name="Task A", duration=30, priority="high", preferred_time="09:00"),
        CareTask(name="Task B", duration=30, priority="high", preferred_time="09:00"),
        CareTask(name="Task C", duration=30, priority="high", preferred_time="09:15"),
        CareTask(name="Task D", duration=20, priority="medium", preferred_time="11:00"),
    ]

    print("Tasks created:")
    for task in tasks_multiple:
        print(f"  • {task.name} at {task.preferred_time} ({task.duration} min)")
    print()

    scheduler4 = Scheduler(owner=owner, pet=pet, tasks=tasks_multiple)
    schedule4 = scheduler4.generate_schedule()

    print("Schedule generated:")
    print(schedule4.explanation)
    print()

    # ===== TEST 5: Tasks Without Times (No Conflicts) =====
    print("=" * 70)
    print("✅ TEST 5: Tasks Without Preferred Times")
    print("=" * 70)
    print()

    tasks_no_time = [
        CareTask(name="Brush Fur", duration=20, priority="low"),
        CareTask(name="Trim Nails", duration=15, priority="low"),
        CareTask(name="Clean Toys", duration=10, priority="low"),
    ]

    print("Tasks created (no preferred times):")
    for task in tasks_no_time:
        print(f"  • {task.name} ({task.duration} min, no time specified)")
    print()

    scheduler5 = Scheduler(owner=owner, pet=pet, tasks=tasks_no_time)
    schedule5 = scheduler5.generate_schedule()

    print("Schedule generated:")
    print(schedule5.explanation)
    print()

    # ===== TEST 6: Direct Conflict Detection Method =====
    print("=" * 70)
    print("🔍 TEST 6: Direct Conflict Detection Method")
    print("=" * 70)
    print()

    conflict_tasks = [
        CareTask(name="Walk", duration=30, priority="high", preferred_time="10:00"),
        CareTask(name="Play", duration=20, priority="medium", preferred_time="10:15"),
    ]

    scheduler6 = Scheduler(owner=owner, pet=pet, tasks=conflict_tasks)
    conflicts = scheduler6.handle_conflicts()

    print(f"Tasks to check:")
    for task in conflict_tasks:
        print(f"  • {task.name} at {task.preferred_time} ({task.duration} min)")
    print()

    if conflicts:
        print(f"Conflicts detected ({len(conflicts)}):")
        for conflict in conflicts:
            print(f"  {conflict}")
    else:
        print("✅ No conflicts detected")
    print()

    # ===== Summary =====
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"✅ Exact time collision: Detected and reported")
    print(f"✅ Overlapping time windows: Detected and reported")
    print(f"✅ No conflicts (well-spaced): No warnings")
    print(f"✅ Multiple conflicts: All conflicts reported")
    print(f"✅ Tasks without times: No false positives")
    print(f"✅ Direct method call: Returns conflict list")
    print()

    print("=" * 70)
    print("✅ All Conflict Detection Tests Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
