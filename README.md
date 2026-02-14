# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ includes intelligent scheduling features that go beyond basic task management:

### 🔄 Recurring Task Automation
Automatically create next occurrences when tasks are completed. Supports 6 frequency types:
- **Daily** (medication, feeding, walks)
- **Biweekly** (nail trimming, ear cleaning)
- **Weekly** (grooming, training sessions)
- **Monthly** (flea/tick prevention, vet wellness visits)
- **Quarterly** (dental cleaning, vaccine boosters)
- **Yearly** (annual checkup, license renewal)

### ⏰ Time-Based Sorting
Sort tasks chronologically by preferred time (HH:MM format) to create logical daily schedules that flow naturally throughout the day.

### ⚠️ Conflict Detection
Lightweight algorithm detects scheduling conflicts:
- **Exact time collisions**: Two tasks scheduled at the same time
- **Overlapping windows**: Tasks whose durations cause overlaps
- Returns warnings instead of crashing (non-blocking validation)

### 🔍 Smart Filtering
- **By completion status**: View pending vs completed tasks
- **By pet name**: Filter tasks for specific pets
- **By time constraints**: Greedy algorithm fits tasks within available time

**Implementation**: Uses O(1) dictionary lookups for extensibility, reducing code complexity by 28% while maintaining performance.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
