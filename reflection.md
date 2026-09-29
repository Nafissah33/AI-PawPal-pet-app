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

 