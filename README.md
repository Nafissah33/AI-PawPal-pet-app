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

## 🖥️ Sample Output

Terminal output from running `python3 main.py`, which builds an `Owner` with two `Pet`s and three `Task`s, then generates and prints today's schedule:

```
Today's Schedule
Daily plan (60 minutes available):
  08:00-08:05  Litter box (high priority, 5 min)
  08:05-08:15  Feeding (high priority, 10 min)
  08:15-08:45  Morning walk (high priority, 30 min)
Total time used: 45/60 minutes.
```

## 🧪 Testing PawPal+

Run the test suite with:

```bash
python3 -m pytest
```

The suite in `tests/test_pawpal.py` covers:

- **Sorting correctness** — `Scheduler.generate_plan()` returns tasks in chronological (non-decreasing start time) order.
- **Recurrence logic** — completing a task with a `recurrence` value (e.g., `"daily"`) via `Pet.complete_task()` creates a new pending task for the next occurrence.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags tasks that share the same `preferred_time`.
- **Task completion** — `Task.mark_complete()` correctly updates a task's `completed` status.
- **Task addition** — `Pet.add_task()` increases that pet's task count.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/nafissah/AI-PawPal-pet-app
plugins: anyio-4.15.1
collected 5 items

tests/test_pawpal.py .....                                               [100%]

============================== 5 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
