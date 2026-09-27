# Spec-Driven Path (Real Development)

For the **real-development** fork: don't hand the user one big prompt. Produce a
small chain of artifacts where each one feeds the next, so intent and constraints
live in files the agent re-reads at every step instead of decaying in a chat.
This is GitHub **spec-kit's** method, adapted so it works whether or not the user
runs spec-kit's CLI.

The reason to bother: for anything that will actually ship, the codebase becomes
the de-facto spec if you don't write one first — a pile of components that work
until they don't and are hard to evolve. A spec written before code is the source
of truth for both the human and the agent.

## When to use this vs. a single prompt
- **Single prompt** (mock template): demos, one screen, throwaway, "show me the idea".
- **Spec chain** (this file): multi-feature apps, real data + auth, anything maintained, anything going into an existing repo via Cursor/Windsurf.

## The chain

Produce these in order. Each is a short Markdown artifact. Confirm the spec with
the user before planning; confirm the plan before tasking — cheap course
correction beats rebuilding.

### 1. Constitution — the non-negotiables
The rules every later step must honour. Keep it short and real:
- Stack and framework (once confirmed with the user).
- Quality bars: TypeScript strict, accessibility level, test expectation.
- Design system: token source, component library, responsive baseline.
- Anything the user says must always/never be true.

### 2. Specify — what & why (no implementation)
- The problem and who has it.
- User stories / core flows.
- Acceptance criteria per story (testable).
- Explicitly out of scope.
- **No tech choices here** — this is behaviour, not build.

### 3. Clarify — close the gaps (before planning)
List the underspecified decisions and ask the user, or state the assumption
explicitly. Ambiguity resolved here is 10× cheaper than after code exists.

### 4. Plan — the technical approach
- Confirmed stack + key libraries.
- Data model (entities, relationships).
- Auth/integration approach.
- The screens/components and how they compose.
- Structure as modular parts with clear boundaries, not a monolith.

### 5. Tasks — phased, buildable units
Break the plan into ordered tasks, **load-bearing feature first**, and phased so
concerns don't mix:
- Phase 1: UI shell + primary screen (mock data)
- Phase 2: data model + persistence
- Phase 3: auth
- Phase 4: remaining logic + integrations
- Phase 5: states, validation, polish, a11y pass

Each task = one paste-ready build prompt (use the feature template in
`prompt-anatomy.md`). Ship them one at a time; verify each before the next.

### 6. (Optional) Analyze / checklist
Before implementing, sanity-check the artifacts against each other for gaps and
contradictions — spec vs. plan vs. tasks. Treat it like "unit tests for the spec".

## Delivering the spec package
- Emit the artifacts as files (or a doc if a doc connector is available), named
  `constitution.md`, `spec.md`, `plan.md`, `tasks.md` — then the **first build prompt** inline.
- If the user is on **Cursor / Windsurf / Claude Code**, mention they can run real
  spec-kit so these become live `/speckit.*` commands in their repo:
  `uvx --from git+https://github.com/github/spec-kit.git specify init <name>`
  then `/speckit.constitution` → `/speckit.specify` → `/speckit.clarify` →
  `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`.
  ⚠️ command names and install line drift — verify at https://github.github.com/spec-kit/ before quoting them as current.
- If the user is on **Lovable / v0 / Bolt / Replit** (no repo/CLI), spec-kit's CLI
  doesn't apply — deliver the artifacts as the plan, seed the tool's own
  knowledge/project file from `constitution.md` + `spec.md`, then feed the phased
  prompts one at a time.

## Guardrails specific to real dev
- Never mix phases in one prompt.
- Every phase carries the responsiveness clause (see `prompt-anatomy.md`).
- Every prompt against existing code carries a "do not change" constraint.
- Label anything unverified about the tool `[Low]` and tell the user to confirm.
