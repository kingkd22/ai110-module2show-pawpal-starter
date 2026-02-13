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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
