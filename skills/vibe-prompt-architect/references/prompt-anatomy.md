# Prompt Anatomy

The canonical prompt skeleton and the mode-specific templates. Every refined
prompt this skill emits is built from these. The point of a fixed skeleton is
that each section kills one specific failure mode — drop a section and you invite
its failure back.

## The canonical spec block (full)

Used whole for real dev; trimmed for mock-ups. Order matters — a tool reads it top to bottom.

1. **Context** — greenfield or existing? current stack and state? For an edit, the exact files/areas involved. *Kills: the tool rebuilding what already exists or guessing the stack.*
2. **Outcome** — the one job, who it's for, and what "done" looks like in one or two sentences. *Kills: building the wrong thing. Write this first even though it sits second.*
3. **Scope** — this build only, as a numbered list with the load-bearing feature first. *Kills: effort spread evenly across everything, load-bearing feature half-done.*
4. **UI / Design** — named components (shadcn / registry items), concrete spacing and layout, design direction with real references — not adjectives. *Kills: generic template output.*
5. **Responsive & States** — mobile-first; mobile/tablet/desktop breakpoints; touch targets; type scaling; reflow rules; loading, empty, and error states; validation; basic a11y. *Kills: desktop-only output and states retrofitted later.*
6. **Data / Logic** — entities, relationships, auth, integrations. *(Real dev only; mock uses sample data.)*
7. **Constraints** — what must NOT change or must NOT be done. *Kills: collateral edits to working code.*
8. **Acceptance criteria** — testable checks that define success. *(Real dev; optional but valuable for mock.)*
9. **Build order** — the sequence/phases to build in. *Kills: everything-at-once tangle.*

---

## Mock-up / demo template

Fast, visual-first, one-shot, throwaway-friendly. Trim the block to what a
clickable demo needs. Sample data is fine; no backend.

```
Build a [page/app] for [who] whose one job is [outcome].

Look & feel: [design direction + 1–2 real references or named components,
e.g. shadcn <Card>, a 21st.dev hero — paste the AI-ready component prompt here].
Use realistic sample content, not lorem ipsum.

Screens/sections (in priority order):
1. [load-bearing screen]
2. [next]
3. [next]

Responsive: mobile-first; works at mobile / tablet / desktop; comfortable touch
targets; include loading, empty, and error states for anything that lists data.

Keep it front-end only with mock data — no backend, no auth. One screen at a
time; start with #1.
```

**Example**
Input: "a habit tracker demo to show an investor"
Output prompt (for Lovable/v0):
```
Build a habit-tracker web app for someone tracking daily habits; its one job is
to let them mark today's habits done and see a streak.

Look & feel: calm, focused, lots of whitespace; shadcn <Card> tiles, a bold
weekly streak strip, muted palette with one accent for "done". Realistic habits
(Drink water, Read 20 min, Walk), not placeholders.

Screens (priority order):
1. Today view — list of habit cards with a large tap-to-complete toggle + streak count
2. Weekly grid — 7-day dots per habit
3. Add-habit sheet — name, icon, colour

Responsive: mobile-first; single column on mobile, two on tablet+, sticky header;
big touch targets; empty state ("Add your first habit") and a done-all celebration state.

Front-end only, mock data, no backend. Start with the Today view.
```

---

## Feature template (adding to an existing build)

For a change against a project that already exists — the everyday case.

```
Context: [what the project is + the current state of the area you're touching;
@reference the files if the tool supports it].

Add: [one feature], because [why].

Behaviour: [what it does, step by step, including edge cases].
UI: [named components + where it sits]. States: loading / empty / error / validation.
Responsive: [breakpoint behaviour for this feature].

Do NOT change: [routing / auth / other features / styling elsewhere].
Done when: [testable acceptance checks].

Build this one feature only. Show me the plan before you build if the tool supports it.
```

---

## Debug template (something came back wrong)

Diagnose before fixing — reflexive rewrites make it worse. Never emit a "just fix
it" prompt.

```
Something's broken. Do NOT rewrite yet — diagnose first.

Symptom: [what you see vs. what you expect].
When it started / what changed just before: [last prompt or edit].
Error/logs: [paste exact text, console + network if UI].

1. Tell me the most likely cause(s) and how you'd confirm each.
2. Propose the smallest fix, and what it might affect.
3. Wait for my go-ahead before changing code.
```

If the same bug has failed 2+ fixes, stop patching: ask the tool to explain what
the failing code is actually doing, and reconcile that against the intended
behaviour before any further edit.

---

## Quality bar before you hand a prompt over

- Could a stranger build the right thing from this prompt alone? If not, a section is thin.
- Is it one concern, or did four sneak in? Split if so.
- Are components named, or are you leaning on adjectives?
- Are the three states (loading/empty/error) and the breakpoints actually stated?
- Is there a "do not change" line for anything that already works?
- Does it end with a testable "done when"?
