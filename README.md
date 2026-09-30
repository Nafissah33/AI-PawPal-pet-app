# 🐾 PawPal+

PawPal+ is a Streamlit app that helps a pet owner plan daily care tasks — walks, feeding, meds, enrichment, grooming, and more — across one or more pets, and builds a prioritized daily schedule that explains its own reasoning.

## Features

- **Priority-based scheduling** (`Scheduler.sort_tasks`) — tasks are ordered high → medium → low priority first; within the same priority, tasks with a set preferred time are ordered chronologically, and untimed tasks fall back to shortest-duration-first.
- **Time-budget filtering** (`Scheduler.filter_tasks`) — greedily keeps every not-yet-completed task that still fits in the remaining minutes, skipping ones that don't without giving up on shorter tasks later in the list.
- **Sequential plan generation with reasoning** (`Scheduler.generate_plan` / `generate_plan_for_owner`) — lays selected tasks into back-to-back time slots and records *why* each one was scheduled.
- **Conflict warnings with a suggested fix** (`Scheduler.detect_conflicts` + `find_next_available_slot`) — flags any pair of tasks that share the same preferred time, and suggests the next open time slot for the second task instead of just flagging the problem.
- **Daily/weekly recurrence** (`Pet.complete_task`) — completing a recurring task automatically creates a fresh pending copy for its next occurrence.
- **Cross-pet scheduling** (`Owner.get_all_tasks`) — one owner's tasks are scheduled together across all of their pets, not pet-by-pet in isolation.
- **Multi-pet support** — one `Owner` can manage any number of `Pet`s, each with its own task list.
- **Persistence between runs** (`Owner.save_to_json` / `Owner.load_from_json`) — save your data to `data.json` and it's still there the next time you launch the app.
- **Professional CLI output** (`main.py`, using `tabulate`) — structured tables with color-coded priority (🔴/🟡/🟢), category icons (🚶/🍽️/🧼/🎾), and status indicators (✅ Done / ⏳ Pending) instead of plain text.

## Getting Started

### Requirements

- Python 3.10+
- See `requirements.txt` (Streamlit, pytest, tabulate)

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the app

```bash
streamlit run app.py
```

### Try it from the command line

`main.py` is a lightweight script for exercising the backend without the UI:

```bash
python3 main.py
```

## Project Structure

| Path | Purpose |
|---|---|
| `app.py` | Streamlit UI — add pets/tasks, view schedules, see conflict warnings, save/load data |
| `pawpal_system.py` | Backend logic layer: `Owner`, `Pet`, `Task`, `Scheduler`, plus JSON persistence |
| `main.py` | Command-line script for manually exercising the backend |
| `tests/test_pawpal.py` | Automated test suite (pytest) |
| `data.json` | Saved `Owner`/`Pet`/`Task` data (generated at runtime, not committed to git) |
| `diagrams/uml.mmd` | Initial UML class diagram (Mermaid) |
| `diagrams/uml_final.mmd` | UML diagram refined to match the final implementation |
| `reflection.md` | Design decisions, tradeoffs, and testing confidence |

## How Scheduling Works

| Feature | Method(s) | Notes |
|---|---|---|
| Priority-based scheduling | `Scheduler.sort_tasks()` | High → medium → low priority first; same-priority tasks are ordered chronologically by `preferred_time`, falling back to shortest-duration-first if untimed |
| Filtering | `Scheduler.filter_tasks()` | Greedily drops completed tasks and any task that no longer fits in the remaining time |
| Conflict handling | `Scheduler.detect_conflicts()` | Flags pairs of tasks sharing the same `preferred_time`; surfaced as warnings in the UI |
| Next available slot | `Scheduler.find_next_available_slot()` | Given a plan and a duration, finds the earliest time that doesn't overlap already-scheduled entries — used to suggest a fix for a flagged conflict |
| Date-aware recurrence | `Pet.complete_task()` + `Scheduler.filter_tasks()` | Completing a `daily`/`weekly` task schedules its next occurrence on the actual future `due_date` (+1 day / +7 days); the scheduler skips any task not yet due, so it can't be re-completed same-day |
| Plan generation | `Scheduler.generate_plan()` / `generate_plan_for_owner()` | Combines sorting + filtering, then lays tasks out into sequential time slots with reasoning |

### Priority-Based Scheduling Example

Running `python3 main.py` includes this demo: four tasks across three priority levels, two of them sharing "high" priority but with different preferred times.

```
--- Priority-Based Scheduling Demo ---
Sort order (priority first, then by preferred time):
  🔴 High       |             07:00 | Morning walk
  🔴 High       |             18:00 | Evening walk
  🟡 Medium     |             10:00 | Grooming
  🟢 Low        | no preferred time | Play time

╭─────────┬───────┬──────────────┬────────────┬────────────╮
│ Start   │ End   │ Task         │ Priority   │ Duration   │
├─────────┼───────┼──────────────┼────────────┼────────────┤
│ 08:00   │ 08:20 │ Morning walk │ 🔴 High     │ 20 min     │
│ 08:20   │ 08:40 │ Evening walk │ 🔴 High     │ 20 min     │
│ 08:40   │ 08:55 │ Grooming     │ 🟡 Medium   │ 15 min     │
│ 08:55   │ 09:25 │ Play time    │ 🟢 Low      │ 30 min     │
╰─────────┴───────┴──────────────┴────────────┴────────────╯

Total time used: 85/90 minutes.
```

Notice both "high" priority tasks are scheduled before "medium," and "medium" before "low" — but "Morning walk" (07:00) is ordered before "Evening walk" (18:00) since they share a priority, breaking the tie chronologically rather than by duration. **Note:** `preferred_time` controls sort *order*, not the actual clock time a task is placed at — `generate_plan()` still lays tasks into sequential slots starting from the day's start time (08:00 here), so "Evening walk" appears at 08:20 in the plan, not literally at 18:00. Full time-slot placement based on `preferred_time` is a known limitation, not yet implemented (see `reflection.md`).

## Professional Output Formatting

`main.py`'s CLI output uses structured tables and status indicators instead of plain text, so it reads like a real report rather than a debug dump.

| Formatting feature | Where it's implemented | Details |
|---|---|---|
| Structured CLI tables | `tabulate` library, in `main.py`'s `print_schedule_table()` / `print_task_table()` | Schedules and task lists render as bordered tables (`tablefmt="rounded_outline"`) instead of raw `print()` lines |
| Color-coded priority | `PRIORITY_ICONS` dict in `pawpal_system.py` (shared by `main.py` and `app.py`) | 🔴 High / 🟡 Medium / 🟢 Low — defined once in the backend so the CLI and the Streamlit UI stay visually consistent |
| Task-type emojis | `CATEGORY_ICONS` dict in `main.py` | 🚶 Walk, 🍽️ Feeding, 🐾 Litter, 🧼 Grooming, 🎾 Play — falls back to 📌 for an unset or unrecognized category |
| Status indicators | `_status_label()` helper in `main.py` | ✅ Done vs. ⏳ Pending, based on `Task.completed` |

Demonstrated in `main.py`'s output: marking "Play time" complete after generating a schedule and printing an updated task table shows both statuses side by side:

```
Task list after marking "Play time" complete
╭───────────┬──────────────┬────────────┬────────────┬────────────╮
│ Status    │ Task         │ Category   │ Priority   │ Duration   │
├───────────┼──────────────┼────────────┼────────────┼────────────┤
│ ⏳ Pending │ Evening walk │ 🚶 Walk     │ 🔴 High     │ 20 min     │
│ ⏳ Pending │ Morning walk │ 🚶 Walk     │ 🔴 High     │ 20 min     │
│ ⏳ Pending │ Grooming     │ 🧼 Grooming │ 🟡 Medium   │ 15 min     │
│ ✅ Done    │ Play time    │ 🎾 Play     │ 🟢 Low      │ 30 min     │
╰───────────┴──────────────┴────────────┴────────────┴────────────╯
```

`PRIORITY_ICONS` was previously duplicated locally inside `app.py`; it now lives once in `pawpal_system.py` and both `main.py` and `app.py` import it, so the CLI and the Streamlit UI can never visually drift apart.

## Persistence

PawPal+ can save an `Owner` (and all of their `Pet`s and `Task`s) to a JSON file and reload it later, so your data survives restarting the app — not just clicking around within one running session.

**How it works:**

1. **Serialization (`to_dict`)** — `Task`, `Pet`, and `Owner` each have a `to_dict()` method built on `dataclasses.asdict()`. Since all three are plain dataclasses made of JSON-safe types (strings, ints, bools, lists, dicts), `asdict()` recursively converts the entire object graph — an `Owner` with nested `Pet`s and their nested `Task`s — into plain nested dicts in one call.
2. **Writing to disk (`save_to_json`)** — `Owner.save_to_json(filepath)` calls `to_dict()` and writes the result with `json.dump()`. This is exposed in the UI as the **💾 Save data** button, which writes to `data.json` in the project folder.
3. **Reconstruction (`from_dict`)** — going from a plain dict *back* to real `Task`/`Pet`/`Owner` objects isn't automatic (Python's dataclasses don't provide an inverse of `asdict()`), so each class has a small `from_dict(data)` classmethod that explicitly rebuilds nested objects — `Owner.from_dict()` calls `Pet.from_dict()` for each pet dict, which calls `Task.from_dict()` for each task dict.
4. **Reading from disk (`load_from_json`)** — `Owner.load_from_json(filepath)` reads the JSON file and calls `from_dict()` on it. In the UI, this happens automatically on startup if `data.json` already exists (instead of building a blank `Owner`), and can also be triggered manually with the **📂 Reload from file** button.

**Why a custom dict conversion instead of a library like `marshmallow`:** the object graph here is small and uniform (3 levels, all dataclasses, all primitive field types), so `dataclasses.asdict()` already gives free recursive serialization with zero extra code. `marshmallow` would add an external dependency and require writing a parallel `Schema` class per model — overhead this project's scale doesn't need. It would be worth reconsidering if the models grew field-level validation rules, versioning needs, or many more nested types.

**Files involved:** `pawpal_system.py` (the `to_dict`/`from_dict`/`save_to_json`/`load_from_json` methods), `app.py` (the Save/Reload buttons and startup auto-load), `tests/test_pawpal.py` (a round-trip test), and `data.json` itself (generated at runtime, excluded from git via `.gitignore`).

## 📸 Demo Walkthrough

### Main UI features

- **Owner & pet setup** — enter an owner name and first pet on load (or automatically load a previously saved `data.json`); add more pets anytime via the **Add a Pet** form.
- **Save/reload data** — **💾 Save data** writes everything to `data.json`; **📂 Reload from file** discards in-session changes and reloads the last saved version.
- **Task management** — per pet, add tasks with a title, duration, priority, optional preferred time, and optional recurrence (`daily`/`weekly`); mark any task complete with one click.
- **Live conflict warnings** — as soon as two tasks share a preferred time, a specific warning appears naming both tasks and pets involved.
- **Sorted task preview** — an expandable "All tasks, sorted by priority" table shows the scheduling order before you even generate a plan.
- **Schedule generation** — set the minutes available today and generate a full daily plan with per-task reasoning.

### Example workflow

1. Enter owner **Jordan** and first pet **Mochi** (dog) — this creates the `Owner`/`Pet` for the session.
2. Use **Add a Pet** to register a second pet, **Luna** (cat).
3. Add tasks: "Morning walk" (30 min, high) and "Feeding" (10 min, high) for Mochi; "Litter box" (5 min, high) for Luna.
4. Set **Minutes available today** to 60 and click **Generate schedule** to see today's plan across both pets.
5. Click **Mark complete** on a recurring task (e.g., a "daily" feeding) — a fresh pending copy for tomorrow appears immediately in the task list.

### Key Scheduler behaviors shown

- **Sorting** — high-priority tasks ("Litter box," "Feeding," "Morning walk") are scheduled before any medium/low-priority task, with shorter tasks breaking ties within the same priority.
- **Filtering** — a task that no longer fits in the remaining time budget (e.g., a 45-minute task with only 25 minutes left) is dropped from today's plan, not just left unscheduled by accident.
- **Conflict warnings with a suggested fix** — two tasks both set to the same preferred time (e.g., `08:00`) trigger a warning like: *"Feeding" (Mochi) and "Walk" (Luna) are both set for this time. Try moving "Walk" to 08:10 instead.* — the suggested time comes from `find_next_available_slot()`, not a generic message.
- **Recurrence** — completing a `daily`/`weekly` task doesn't just check it off; it immediately queues the next occurrence as a new pending task.

### Sample CLI output

Running `python3 main.py` builds an `Owner` with two `Pet`s and three `Task`s, then generates and prints today's schedule as a formatted table:

```
Today's Schedule
╭─────────┬───────┬──────────────┬────────────┬────────────╮
│ Start   │ End   │ Task         │ Priority   │ Duration   │
├─────────┼───────┼──────────────┼────────────┼────────────┤
│ 08:00   │ 08:05 │ Litter box   │ 🔴 High     │ 5 min      │
│ 08:05   │ 08:15 │ Feeding      │ 🔴 High     │ 10 min     │
│ 08:15   │ 08:45 │ Morning walk │ 🔴 High     │ 30 min     │
╰─────────┴───────┴──────────────┴────────────┴────────────╯

Total time used: 45/60 minutes.
```

## 🧪 Testing PawPal+

Run the test suite with:

```bash
python3 -m pytest
```

The suite in `tests/test_pawpal.py` covers:

- **Sorting correctness** — `Scheduler.generate_plan()` returns tasks in chronological (non-decreasing start time) order.
- **Priority-then-time sorting** — `Scheduler.sort_tasks()` orders by priority first, breaking ties within the same priority by `preferred_time`.
- **Recurrence logic** — completing a task with a `recurrence` value (e.g., `"daily"`) via `Pet.complete_task()` creates a new pending task for the next occurrence.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags tasks that share the same `preferred_time`.
- **Next available slot** — `Scheduler.find_next_available_slot()` returns the earliest time that doesn't overlap an already-scheduled entry.
- **JSON persistence** — `Owner.save_to_json()` / `Owner.load_from_json()` round-trip an owner's pets and tasks without data loss.
- **Task completion** — `Task.mark_complete()` correctly updates a task's `completed` status.
- **Task addition** — `Pet.add_task()` increases that pet's task count.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/nafissah/AI-PawPal-pet-app
plugins: anyio-4.15.1
collected 8 items

tests/test_pawpal.py ........                                            [100%]

============================== 8 passed in 0.01s ===============================
```

## Design

The system is built around four classes — see `diagrams/uml_final.mmd` for the class diagram and `reflection.md` for the design decisions and tradeoffs behind it (e.g., why `Task` carries a generated `id`, and known limitations like conflict detection not yet blocking schedule generation).
