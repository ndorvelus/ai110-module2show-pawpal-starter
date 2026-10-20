# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

--- Classes: Pet (info on the pet), Owner(info on owner),Task(walks,feeding,medicine,grooming), Schedule(pet/owner schedules)

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

--- The design changed during implementation to be able to catch edge cases and bugs that were popping up, like splitting time_conflict_warnings into 2 seperate methods (detect_conflicts())

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

--- detect_conflicts() finds tasks that don't fit the time budget, while  time_conflict_warnings() finds identical start times.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---I gave up some accuracy for simplicity. The newer find_next_available_slot() does account for durations, so the two checks can disagree. The warnings can say "no conflict" for a time the slot finder treats as busy.

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

--- Debugging, writing tests, writing logic.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

--- 

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

--- sorting, recurrence, add_task, mark_complete, etc. These tests helped make sure that the overall logic was working.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

--- Very; a task that is exactly as long as the remaining time budget.

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
---Everything

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
---Nothing

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
---OOP
