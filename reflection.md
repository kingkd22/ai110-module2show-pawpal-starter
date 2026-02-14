# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

- Three basic functions a user should be able to complete are: Manage pet/owner info, add/edit tasks, view daily/weekly tasks

- Main objects:
- Owner: 
- attributes: name(String), time available(int), preferences
- methods: get_available_time(), set_available_time(time), update_preferences(...), has_time_for(duration)

- Pet: 
- attributes: name(string), type(string), breed(string), age(int), special_needs
- methods: get_info(), update_info(), _str_() 

CareTask:
attributes: task_id, name, task_type, duration, priority, preferred_time, notes
methods: get_duration, get_priority, update_task, is_valid, _str_

Schedule:
attributes: date, scheduled_tasks, total_duration, owner, pet, explanation
methods: add_task(task, time_slot), remove_task(task_id), get_schedule(), calculate_total_duration(), generate_explanations(), is_feasible(), display()

Scheduler
attributes: tasks, owner, pet
methods: generate_schedule(), sort_by_priority(), filter_by_time_constraint(), optimize_order(), explain_reasoning(), handle_conflicts()

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

- Changes: 
- Return Type Mismatch in filter_by_time_constraint() --> this method needs to return both selected AND excluded tasks for explanation generation. Currently returns only a list. --> Change return type to tuple[list[CareTask], list[CareTask]]

- CareTask Class constants placement --> In dataclasses, class variables defined after instance fields can be problematic. These should be defined at the top of the class or use ClassVar type hint.

- Method Redundancy: Two Explanation Generators --> Schedule.generate_explanatio() (line 134) Scheduler.explain_reasoning(schedule) (line 172)

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

- The scheduler considers time available (owner's daily minutes), task priority (high/medium/low), task duration, and preferred time slots (with conflict detection for overlapping times).
- Priority was chosen as the primary constraint because critical pet care tasks (medication, feeding) must be completed before optional activities (playtime, grooming), ensuring essential needs are never skipped due to time limitations.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

- The recurring task system uses a dictionary (`FREQUENCY_DAYS = {"daily": 1, "weekly": 7, ...}`) instead of an if/elif chain, trading ~400 bytes of memory for O(1) constant-time lookup and easy extensibility. This is reasonable for pet care because: 
- memory cost is negligible (0.0005% of app memory),
- pet care naturally needs 6+ different frequencies (daily medication, weekly grooming, monthly vet visits, quarterly checkups, yearly vaccines),
- adding new frequencies now requires just updating the dictionary instead of modifying code logic. The trade sacrifices nothing meaningful to gain significant maintainability.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

- I used Claude at the beginning in the plan mode to fully plan out the project and designing. As the project went along I continued to use it for debugging, test creation and refactoring. 
- I used prompts which were similar to the codepath instructions. Making sure I'm being clear and descriptive of what I'm doing and the output I am expecting

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

- I verified what AI suggested by having Claude explain its reasoning of why it did certain things and planning ahead before implementing code.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

- Tested 26 behaviors across 5 categories: (1) core functionality (task completion, recurring tasks with 6 frequencies), (2) sorting algorithms (chronological time, priority-based), (3) conflict detection (exact collisions, overlapping windows, 1-minute precision), (4) AM/PM time parsing (12-hour and 24-hour formats), and (5) edge cases (empty data, zero time, boundary conditions).
- These tests validate algorithm correctness (O(n log n) sorting, O(n²) conflict detection), ensure real-world reliability (recurring task chains, multi-format time handling), and prevent silent failures in edge cases (tasks without times, exact time-budget fits) that could cause scheduling errors or data loss in production.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

- I am very confident the schedular works correctly. If i had more time I would test for different pets sharing a task or having different tasks at the same time.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

- I am most satisfied with my backend logic and thorogh testing

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- I would do a redesign on the UI make it a different style

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

- I learned how to use the plan mode thoroghly especially designing systems out prior to implementation.