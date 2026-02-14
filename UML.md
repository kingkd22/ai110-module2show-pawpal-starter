```mermaid
classDiagram
    %% Module-level utility function
    class UtilityFunctions {
        <<function>>
        +parse_time_to_minutes(time_str) int
    }

    class Owner {
        -String name
        -int time_available
        -dict preferences
        +get_available_time() int
        +set_available_time(time) void
        +update_preferences(**kwargs) void
        +has_time_for(duration) bool
    }

    class Pet {
        -String name
        -String type
        -String breed
        -int age
        -list special_needs
        -list tasks
        +get_info() String
        +update_info(**kwargs) void
        +add_task(task) void
        +get_task_count() int
        +__str__() String
    }

    class CareTask {
        <<dataclass>>
        -String task_id
        -String name
        -String task_type
        -int duration
        -String priority
        -String preferred_time
        -String notes
        -bool completed
        -String frequency
        -date due_date
        -String pet_name
        +VALID_PRIORITIES ClassVar
        +PRIORITY_VALUES ClassVar
        +VALID_FREQUENCIES ClassVar
        +FREQUENCY_DAYS ClassVar
        +__post_init__() void
        +get_duration() int
        +get_priority() String
        +get_priority_value() int
        +update_task(**kwargs) void
        +is_valid() bool
        +_get_validation_errors() String
        +_get_next_due_date() date
        +mark_complete() CareTask
        +is_completed() bool
        +__str__() String
    }

    class Schedule {
        -date date
        -list~CareTask~ scheduled_tasks
        -int total_duration
        -Owner owner
        -Pet pet
        -String explanation
        +__init__(owner, pet, date) void
        +add_task(task, time_slot) void
        +remove_task(task_id) void
        +get_schedule() list~CareTask~
        +calculate_total_duration() int
        +generate_explanation() String
        +is_feasible() bool
        +display() void
    }

    class Scheduler {
        -list~CareTask~ tasks
        -Owner owner
        -Pet pet
        +__init__(owner, pet, tasks) void
        +generate_schedule() Schedule
        +sort_by_priority() list~CareTask~
        +sort_by_time() list~CareTask~
        +filter_by_time_constraint(sorted_tasks) tuple
        +optimize_order(filtered_tasks) list~CareTask~
        +filter_by_completion(completed) list~CareTask~
        +filter_by_pet_name(pet_name) list~CareTask~
        +detect_conflicts(tasks_to_check) list~String~
        +handle_conflicts() list~String~
    }

    %% Relationships
    Schedule "1" --> "1" Owner : for owner
    Schedule "1" o-- "0..*" CareTask : contains
    Schedule "1" --> "1" Pet : for pet

    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "1" Pet : uses
    Scheduler "1" --> "0..*" CareTask : manages
    Scheduler "1" ..> "1" Schedule : creates

    Pet "1" o-- "0..*" CareTask : tracks tasks
    CareTask ..> CareTask : creates next occurrence

    Scheduler ..> UtilityFunctions : uses
    CareTask ..> UtilityFunctions : uses for time parsing

    %% Notes
    note for CareTask "Supports recurring tasks with 6 frequencies:\ndaily, biweekly, weekly, monthly, quarterly, yearly\n\nAuto-creates next occurrence when marked complete\n\nLinks to specific pet via pet_name for multi-pet support"

    note for Scheduler "Uses priority-based greedy algorithm\n\nSupports conflict detection for overlapping times\n\nFilters by completion status and pet name"

    note for UtilityFunctions "parse_time_to_minutes handles both:\n- 24-hour format: 14:30\n- 12-hour format: 2:30 PM"
```

## Key Changes from Initial UML

### 🆕 New Features Added During Implementation

#### 1. **Recurring Task System**
- **New attributes in CareTask:**
  - `completed` (bool) - tracks completion status
  - `frequency` (String) - supports 7 frequencies (once, daily, biweekly, weekly, monthly, quarterly, yearly)
  - `due_date` (date) - when task is due
  - `pet_name` (String) - links task to specific pet

- **New methods in CareTask:**
  - `mark_complete()` - marks done and creates next occurrence
  - `is_completed()` - checks completion status
  - `_get_next_due_date()` - calculates next due date
  - `get_priority_value()` - returns numeric priority for sorting

- **New class variables in CareTask:**
  - `VALID_FREQUENCIES` - list of valid frequency strings
  - `FREQUENCY_DAYS` - dictionary mapping frequencies to day counts

#### 2. **Multi-Pet Support**
- **New attribute in Pet:**
  - `tasks` (list) - tracks tasks for this pet

- **New methods in Pet:**
  - `add_task(task)` - adds task to pet
  - `get_task_count()` - returns task count

- **New attribute in CareTask:**
  - `pet_name` (String) - links task to specific pet

- **New method in Scheduler:**
  - `filter_by_pet_name(pet_name)` - filters tasks by pet

#### 3. **Time Parsing & Sorting**
- **New module-level function:**
  - `parse_time_to_minutes(time_str)` - converts 12/24-hour formats to minutes

- **New method in Scheduler:**
  - `sort_by_time()` - sorts tasks chronologically using time parsing

#### 4. **Conflict Detection**
- **New methods in Scheduler:**
  - `detect_conflicts(tasks_to_check)` - identifies time overlaps
  - `handle_conflicts()` - wrapper for detecting conflicts in all tasks

#### 5. **Task Filtering**
- **New method in Scheduler:**
  - `filter_by_completion(completed)` - filters by completion status

### 📊 Implementation Stats

| Category | Initial UML | Final Implementation | Change |
|----------|------------|---------------------|---------|
| **Classes** | 5 | 5 + 1 utility | +1 |
| **CareTask attributes** | 7 | 11 | +4 |
| **CareTask methods** | 5 | 12 | +7 |
| **Pet attributes** | 5 | 6 | +1 |
| **Pet methods** | 3 | 5 | +2 |
| **Scheduler methods** | 5 | 9 | +4 |
| **Relationships** | 7 | 10 | +3 |

### 🔄 New Relationships

1. **CareTask → CareTask** - Creates next occurrence when recurring task is completed
2. **Pet → CareTask** - Pet tracks its own tasks
3. **Scheduler/CareTask → UtilityFunctions** - Both use time parsing helper

### ✅ Validation

All features in the UML diagram are now implemented and tested with **26 passing tests**:
- ✅ 9 core functionality tests
- ✅ 4 sorting & filtering tests
- ✅ 7 conflict detection tests
- ✅ 2 priority scheduling tests
- ✅ 4 AM/PM time format tests
