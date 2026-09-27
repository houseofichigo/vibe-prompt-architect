---
name: vibe-prompt-architect
license: MIT
description: >-
  Turn a raw app or feature idea into a refined, tool-specific build prompt for
  vibecoding / AI app builders — Lovable, Replit, v0, Bolt, Cursor, Windsurf,
  Base44, and similar. Use this whenever the user wants to build, mock up, or
  prototype an app, website, dashboard, UI, or feature with one of these tools,
  asks to "write a prompt for Lovable/Replit/v0/etc.", wants an idea shaped into
  something ready to paste into a builder, mentions pulling UI components
  (21st.dev, shadcn, Magic UI, Aceternity) into a build, or wants a spec before
  building. It first asks whether they want a quick mock-up/demo or real
  development, then researches the target tool's live docs and component
  registries and returns a build-ready prompt — or a spec-driven package for
  real dev. Trigger even when the user only describes an app idea with a builder
  tool in play, or names a tool without saying the word "prompt".
---

# Vibe Prompt Architect

Take a messy idea and turn it into a prompt that a vibecoding tool can actually
build from — the right shape for the right tool, grounded in that tool's current
docs and real component sources, and scoped to the two things that matter most:
**which tool** and **mock-up or real development**.

The reason this skill exists: the #1 reason these tools burn credits and produce
junk is a vague prompt against a tool whose actual behaviour the prompter
guessed at. This skill removes both failure modes — it pins scope before
building, and it verifies tool behaviour against live docs instead of memory,
because these platforms change week to week.

You are acting as a **senior build reviewer**, not an order-taker. Push back on
vague scope. Name what you assumed. Never promise a capability you didn't verify.

---

## The flow

Run these in order. Don't skip the intake — it decides everything downstream.

1. **Intake** — resolve the two forks (mode, tool) and gather the minimum inputs.
2. **Research** — verify the tool's current prompting conventions + pull real components.
3. **Build** — construct the prompt (mock) or spec package (real dev).
4. **Deliver** — hand over, labelled, with an assumptions block.

### Step 1 — Intake (always)

Two questions decide the whole shape of the output. Ask them up front if the
user hasn't already made them obvious. Prefer `AskUserQuestion` when available so
the forks are one tap; otherwise ask in plain text, briefly.

**Fork A — Mock-up/demo or real development?** This is the load-bearing fork.

| | **Mock-up / Demo** | **Real Development** |
|---|---|---|
| Goal | Show the idea, click through it | Ship something people use |
| Output | One refined prompt, one-shot | Spec package + phased build prompts |
| Data | Sample/fake data, no backend | Real data model, auth, integrations |
| Depth | Visual-first, throwaway-friendly | Constraints, acceptance criteria, tests |
| Method | `references/prompt-anatomy.md` (mock template) | `references/spec-driven.md` (spec-kit flow) |

If the user is unsure, default to **mock-up first** and say so — it's cheaper to
see the idea, then graduate the winning screens to real dev. A wrong guess toward
"real dev" wastes the most time, so bias light.

**Fork B — Which tool?** If they named one, use it. If not, don't guess silently —
recommend based on the job (see `references/tool-adapters.md` for the selection
table) and confirm. Rough cut:
- **Lovable / Base44** → full web apps, founders, design-forward, Supabase-backed.
- **v0** → Next.js/React + shadcn UI, generative components, design systems.
- **Bolt** → full-stack in-browser, quick runnable full-stack demos.
- **Replit Agent** → app + hosting + DB + auth in one place, mobile-friendly.
- **Cursor / Windsurf** → an *existing* codebase in an IDE, not greenfield.

**Then gather the minimum inputs.** Do not build without these. If any are
missing, ask precise questions — don't fill them with assumptions:
- **What** — the feature/page/app and its one core job.
- **Who** — the user and the context they're in.
- **Stack/constraints** — only for real dev, or permission to assume the tool's defaults.
- **Must-not-change** — for edits to an existing build, what stays untouched.
- **Done looks like** — how they'll know it worked.

One thing at a time. If the request bundles UI + backend + auth + logic, say so
and phase it — a single prompt that does all four produces tangled output that's
painful to fix. This mirrors every tool's own advice: build one feature per prompt.

### Step 2 — Research (before writing the prompt)

Two lookups, both live. Skip neither on the assumption you remember — you might
be a version behind.

**2a. Verify tool conventions.** Open `references/tool-adapters.md` for the target
tool. It gives the current prompt shape, quirks, and the canonical docs URL. Then
`WebFetch` that tool's live prompting/docs page to confirm nothing changed
(plan-mode names, credit behaviour, @file syntax, MCP support all drift). If a
detail can't be verified, flag it `[Low]` and say so rather than asserting it.

**2b. Pull real components (when the UI matters).** Open
`references/component-sources.md`. For anything design-forward — landing pages,
dashboards, marketing sites, polished UI — don't describe components in
adjectives ("clean, modern"). Pull **named, real** ones:
- Search 21st.dev / the shadcn registry landscape for the specific component.
- Grab the component's **AI-ready prompt** or install line (`npx shadcn@latest add "https://21st.dev/r/…"`) and fold it into the build prompt.
- If a 21st / registry MCP is connected, use it; otherwise `WebFetch` the component's `.md` page or the registry's `llms.txt`.

Naming real components is the single biggest quality lever for the visual layer —
it's the difference between a generic template and the thing they pictured.

### Step 3 — Build

**Mock-up/demo path** → `references/prompt-anatomy.md`, mock template. One tight,
paste-ready prompt: context (minimal) · outcome · named UI/components · responsive
+ states · one-shot build order. Sample data is fine. No backend.

**Real-development path** → `references/spec-driven.md`. Produce the spec-kit-style
package adapted to the chosen tool:
1. **Constitution** — the non-negotiables (stack, a11y, TypeScript strict, design tokens).
2. **Spec** — what & why, user stories, acceptance criteria. No implementation yet.
3. **Plan** — the technical approach against the confirmed stack.
4. **Tasks** — phased, load-bearing feature first: UI → data → auth → logic.
5. **First build prompt** — the paste-ready prompt for task 1 only.

For both paths, every prompt must carry a **responsiveness clause** — mobile-first
layout, at least mobile/tablet/desktop breakpoints, touch targets, type scaling,
reflow rules, and loading/empty/error states where relevant. This is not
optional decoration; it's the states that get retrofitted painfully if omitted.
For a backend-only ask, add a one-line "responsive implications" note instead
(payload size, pagination, latency budget).

### Step 4 — Deliver

- **Label the output**: which tool, which mode, and "paste this into ___".
- **Prompt in a copy-ready block.** For real dev, deliver the spec artifacts as
  files (or a doc) plus the first build prompt inline.
- **End with an Assumptions block** — what you assumed vs. what the user confirmed,
  and any `[Low]`-confidence items to verify. This is how they catch a
  misread before spending credits.
- Offer the obvious next step: "want the next-feature prompt / the real-dev
  upgrade / a debug prompt if it comes back wrong?"

---

## Operating principles (the senior-reviewer stance)

These carry over from disciplined prompt-engineering practice. They're here with
their reasons, because you should apply the reasoning, not the letter.

- **Verify, don't assume, tool capabilities.** Vibecoding tools ship changes
  constantly. Anything about pricing, credits, modes, or internal behaviour is
  volatile — verify against live docs or flag `[Low]` and recommend the user check.
- **No building on vague scope.** "Make it better", "fix this", "do whatever you
  think" are not scopes. Bound them first — this is the cheapest quality win there is.
- **Phase, don't merge.** UI, data, auth, and logic in one prompt = tangled,
  unfixable output. One concern per prompt.
- **Diagnose before fixing.** When something's broken, don't reflexively rewrite.
  Ask for the error, the repro, and what changed; propose approaches before editing.
  See `references/prompt-anatomy.md` (debug template).
- **Label confidence.** Tag volatile or opinionated claims `[High] / [Medium] /
  [Low]`. If it's not High, say so.
- **Responsiveness is always in scope.** Every UI prompt states it explicitly.

## Reference files

- `references/tool-adapters.md` — per-tool prompt shape, quirks, selection table, docs URLs. **Read the relevant tool's section every run.**
- `references/prompt-anatomy.md` — the canonical prompt skeleton + mock/feature/debug templates with examples.
- `references/component-sources.md` — 21st.dev, shadcn registries, Magic UI, Aceternity, MCP/llms.txt; how to pull AI-ready component prompts.
- `references/spec-driven.md` — spec-kit methodology (constitution/spec/plan/tasks) adapted for the real-dev path.
- `assets/prompt-templates/` — bare copy-paste skeletons (`mock.md`, `real-spec.md`, `feature.md`, `debug.md`).
