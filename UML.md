classDiagram
    class Owner {
        -String name
        -int time_available
        -dict preferences
        +get_available_time() int
        +set_available_time(time) void
        +update_preferences(...) void
        +has_time_for(duration) bool
    }

    class Pet {
        -String name
        -String type
        -String breed
        -int age
        -list special_needs
        +get_info() String
        +update_info(...) void
        +__str__() String
    }

    class CareTask {
        -String task_id
        -String name
        -String task_type
        -int duration
        -int priority
        -String preferred_time
        -String notes
        +get_duration() int
        +get_priority() int
        +update_task(...) void
        +is_valid() bool
        +__str__() String
    }

    class Schedule {
        -date date
        -list scheduled_tasks
        -int total_duration
        -Owner owner
        -Pet pet
        -String explanation
        +add_task(task, time_slot) void
        +remove_task(task_id) void
        +get_schedule() list
        +calculate_total_duration() int
        +generate_explanation() String
        +is_feasible() bool
        +display() void
    }

    class Scheduler {
        -list tasks
        -Owner owner
        -Pet pet
        +generate_schedule() Schedule
        +sort_by_priority() list
        +filter_by_time_constraint() list
        +optimize_order() list
        +explain_reasoning() String
        +handle_conflicts() void
    }

    Schedule "1" --> "1" Owner : for owner
    Schedule "1" o-- "0..*" CareTask : contains
    Schedule "1" --> "1" Pet : for pet
    Scheduler "1" --> "1" Owner : uses
    Scheduler "1" --> "1" Pet : uses
    Scheduler "1" --> "0..*" CareTask : manages
    Scheduler "1" ..> "1" Schedule : creates
