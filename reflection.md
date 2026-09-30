# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

The initial design is built around four classes, each with a single, focused responsibility:

- **`Owner`** — holds the owner's name, preferences (e.g., preferred start time), and the list of `Pet`s they own. Responsible for answering "whose plan is this?" and letting preferences update over time via `update_preferences()`.
- **`Pet`** — holds basic pet info (name, species, breed) and owns the list of `Task`s assigned to it. Responsible for adding/removing tasks and returning a pet's task list (`add_task()`, `remove_task()`, `get_tasks()`).
- **`Task`** — represents a single care item (title, duration, priority, category, recurrence). Responsible for holding task data and allowing it to be edited (`edit()`), instead of living as loose dictionaries in the UI layer.
- **`Scheduler`** — takes a list of `Task` objects plus a time constraint (`available_minutes`) and is responsible for turning them into an ordered daily plan: sorting by priority/duration (`sort_tasks()`), dropping tasks that don't fit (`filter_tasks()`), producing the plan (`generate_plan()`), and explaining the reasoning behind it (`explain_plan()`).

This gives a clean separation: `Owner`/`Pet` model *who* the plan is for, `Task` models *what* needs to be done, and `Scheduler` models *how* those tasks get turned into a plan. `Task` and `Pet` are implemented as Python `dataclasses` since they are primarily data holders; `Scheduler` is a plain class since it holds no persistent state beyond the time constraint.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

While reviewing the class skeleton against the UML, I noticed `Task` had no unique identifier — `Pet.remove_task()` and `Task.edit()` would have had to rely on Python dataclass field equality to find the right task. Since two tasks can easily share identical values (e.g., two "Morning walk, 20 min, high priority" entries for the same pet), that equality check could match the wrong task and silently corrupt the wrong entry. I added an `id: str` field to `Task`, generated automatically with `uuid.uuid4()` at construction, so every task has a stable identity independent of its data. This was a design change made *before* implementing the actual method logic, so `remove_task`/`edit` can be written against `task.id` instead of value equality once the scheduling logic is filled in.

I also dropped an earlier idea (from initial brainstorming) of a separate `Plan`/`PlanEntry` class to represent the scheduler's output. The final design has `Scheduler.generate_plan()` return a plain list instead, since a dedicated result class added complexity without a clear responsibility beyond what `Scheduler` itself already tracks.

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

I used Claude Code end-to-end: object-model brainstorming, UML drafting/refinement, class skeletons, scheduling logic, Streamlit wiring, tests, and this reflection. The most useful feature was that it verified its own work — running `pytest` and booting the app after each change — so I was reviewing confirmed-working code, not untested claims. Asking it to review the code for edge cases *before* writing tests also surfaced real gaps (like tasks having no unique id) instead of just testing whatever existed.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I once asked it to save the diagram as `diagrams/uml_draft.mmd`, following an instruction sheet literally. It flagged that git history already showed that filename renamed to `uml.mmd` "to match grading expectation," so recreating it would undo that fix. I checked `git log --follow` myself to confirm, then kept `uml.mmd` instead of following the instruction as written.

- How did using separate chat sessions for different phases help you stay organized?

Splitting work into phases (UML, skeletons, logic, UI, tests, polish) kept each session focused on verifying one layer before moving to the next, so testing started from an already-stable backend instead of a moving target. Starting fresh for the final UML review also forced an explicit "does this still match the code?" check rather than assuming consistency.

- Summarize what you learned about being the "lead architect"

The AI implements fast but has no sense of which changes are actually safe — it would have happily dropped `priority` to match a pasted spec if I'd let it, breaking the scheduler. Being lead architect meant constantly asking "does this still match the design, and what did it break?" rather than just accepting output.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**Confidence Level: ⭐⭐⭐☆☆ (3/5)**

The core scheduling path is well-covered and passing: priority-then-time sorting, time-budget filtering, chronological plan ordering, task completion, date-aware recurrence, conflict detection with a suggested fix, and JSON persistence all have tests and behave correctly ([tests/test_pawpal.py](tests/test_pawpal.py), 10/10 passing). That gives me confidence in the everyday "add tasks → generate today's plan" flow.

**Resolved since the original 3/5 rating:** recurrence now tracks a real `due_date` — `Pet.complete_task()` computes the actual next occurrence date (`+1 day` for daily, `+7 days` for weekly) instead of an immediately-pending clone, and `Scheduler.filter_tasks()`/`generate_plan()` now skip any task whose `due_date` is still in the future. A weekly task can no longer be completed and regenerated multiple times in the same day.

I'm still holding back from a 5/5 because of gaps the current tests don't touch:

- **`generate_plan()` still ignores `preferred_time` for actual placement** — `find_next_available_slot()` can *suggest* a conflict-free time, but the plan itself still lays tasks out sequentially from the day's start regardless of any preferred time. Suggestions exist; enforcement doesn't yet.
- **No boundary tests** — zero/negative `available_minutes`, a task exactly equal to the remaining time, or an empty task list are all untested.
- **No multi-pet plan test** — `generate_plan_for_owner()` aggregates tasks across pets, but no test confirms tasks from two different pets both show up correctly in one combined plan.

If I had more time, I'd prioritize making `generate_plan()` actually honor `preferred_time` during placement next, since that's the same "field exists but isn't fully load-bearing" pattern that recurrence just got fixed for, then add the boundary and multi-pet tests.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

 