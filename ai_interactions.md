# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

Add a third algorithmic scheduling capability beyond the basic sorting/filtering requirement — something like "next available slot" or weighted prioritization — and keep it wired into the rest of the project (tests, UI, diagrams, docs) rather than leaving it as isolated code.

**What did the agent do?**

- Implemented `Scheduler.find_next_available_slot()` in `pawpal_system.py` — given a plan and a task duration, it finds the earliest time that doesn't overlap already-scheduled entries.
- Added `test_find_next_available_slot_skips_busy_time` to `tests/test_pawpal.py` and ran the full suite (6/6 passing).
- Wired the new method into `app.py`'s conflict-warning banner, so a flagged conflict now suggests a concrete alternative time instead of just saying "these overlap."
- Updated both `diagrams/uml.mmd` and `diagrams/uml_final.mmd` to list the new method, and updated the README's Features list and "How Scheduling Works" table to match.
- Verified the app still boots with no runtime errors by launching it headless and checking the log.

Files modified: `pawpal_system.py`, `tests/test_pawpal.py`, `app.py`, `diagrams/uml.mmd`, `diagrams/uml_final.mmd`, `README.md`.

**What did you have to verify or fix manually?**

No functional corrections were needed this time — I verified independently by re-running `pytest` and the headless Streamlit boot myself rather than just trusting the agent's summary. I did make sure the new conflict-warning wording ("Try moving X to HH:MM instead") stayed consistent in tone with the existing warning message rather than reading like a bolted-on addition.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | ChatGPT | Claude Code (Claude Sonnet 5) |
| **Prompt** | "Choose a complex algorithmic task (like rescheduling weekly tasks when there's a conflict) and give me a solution" | Same prompt, asked directly in this project's chat with full repo context |
| **Response summary** | Pseudocode: `while new_time in existing_tasks: new_time += 1` — treats `existing_tasks` as a set of occupied timestamps and increments a scalar `time` by 1 until it lands on a free value | Two real, tested pieces of code: (1) `Scheduler.find_next_available_slot()` — interval-based, checks a candidate time against sorted `(start, end)` busy ranges and jumps straight to the end of any overlap; (2) date-aware weekly recurrence — `Pet.complete_task()` computes a real `due_date` (+7 days) and `Scheduler.filter_tasks()` skips tasks not yet due |
| **What was useful** | The conceptual shape is right and easy to explain in one sentence: "check if occupied, if so move forward, repeat." Good as a plain-language mental model for the *idea* of conflict resolution | Directly runnable, already integrated with the rest of `pawpal_system.py` (used by `app.py`'s conflict-warning UI), and duration-aware — jumps to the end of a conflicting task instead of scanning minute by minute |
| **Problems noticed** | Treats time as a single scalar rather than a `(start, end)` interval, so it ignores task *duration* entirely — a 30-minute task could still overlap another task even if its exact start minute isn't in `existing_tasks`. `new_time += 1` also doesn't specify a unit and can't be applied directly to `"HH:MM"` strings without real `datetime`/`timedelta` arithmetic. No bound on the loop (could run past midnight), and it's a standalone function, not wired into a scheduler | None functionally — the main cost was that it took real implementation + test-writing effort across two separate turns, versus a five-line pseudocode answer |
| **Decision** | Not used as-is | Kept the existing `find_next_available_slot()` implementation, since it already solves the same problem correctly for variable-duration tasks — it's effectively what Option A's idea looks like once made duration-aware and interval-based |

**Which approach did you use in your final implementation and why?**

Option B (the already-implemented `find_next_available_slot()` + date-aware `due_date` recurrence). ChatGPT's pseudocode named the right general strategy (search forward from the conflicting time until free), but its scalar, unit-less `+= 1` model doesn't hold up for a system where tasks have real, variable durations — pretending every task is "1 unit" long would either under- or over-estimate conflicts. The existing implementation already handles this correctly by comparing against busy `(start, end)` intervals, so there was nothing to port over from Option A beyond the general concept.
