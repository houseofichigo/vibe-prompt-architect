# Tool Adapters

How each vibecoding tool wants to be prompted, what it's good at, and where its
live docs are. **Read the target tool's section on every run, then `WebFetch` its
docs URL to confirm volatile details** (mode names, credit behaviour, syntax).
Anything marked ⚠️ drifts often — verify or flag `[Low]`.

## Tool selection table

Use this when the user hasn't named a tool. Confirm the pick before building.

| Job | Recommend | Why |
|---|---|---|
| Full web app, founder/non-dev, design-forward | **Lovable** | Full-stack from natural language, Supabase-native, strong design defaults |
| Same, wants an all-in-one canvas | **Base44** | App builder with built-in DB/auth/hosting |
| Next.js/React + shadcn UI, design systems, components | **v0** | Generative UI, shadcn-native, great component output |
| Quick runnable full-stack demo in-browser | **Bolt** | WebContainer runs the whole stack live in the browser |
| One tool for build + host + DB + auth, mobile-friendly | **Replit Agent** | End-to-end: generates, runs, deploys, provisions DB |
| Change / extend an **existing** codebase | **Cursor** or **Windsurf** | IDE agents that operate on a real repo, not greenfield |
| Pull specific UI components into any of the above | any + **21st.dev / shadcn registry** | See `component-sources.md` |

Rule of thumb: greenfield app → Lovable/Base44/Bolt/Replit; component/design work
→ v0 + registries; existing repo → Cursor/Windsurf; "just show me the idea" → the
fastest single-prompt tool (Lovable or v0).

---

## Lovable
- **Docs to verify:** https://docs.lovable.dev/prompting/prompting-one (prompt library at docs.lovable.dev)
- **Best at:** full-stack web apps from natural language; React + Tailwind + shadcn + Supabase; design-forward MVPs that are real code (GitHub-syncable), not throwaway.
- **Prompt shape it rewards:** the four-part prompt — **context** (existing project state) · **scope** (one feature) · **outcome** (what done looks like) · **constraints** (what must not change). Build by component, "Lego bricks", one meaningful change per prompt.
- **Levers:**
  - **Plan mode** before executing a build — it surfaces misreads before credits are spent. ⚠️ verify current name/behaviour.
  - **Knowledge / project knowledge** file at T=0 — persistent product + design context every later prompt inherits. Seed it first for real dev.
  - **`@file` references** to scope a change to specific files precisely.
  - Name concrete shadcn components + spacing, not adjectives.
  - Stabilise the UI before wiring the backend.
- **Watch:** vague prompts burn credits going in circles; giant multi-feature prompts produce tangle. ⚠️ credit mechanics are volatile.

## v0 (Vercel)
- **Docs to verify:** https://v0.app/docs (and v0's model/prompting notes)
- **Best at:** React/Next.js UI generation, shadcn/ui + Tailwind, design systems, polished components and pages; generative UI you refine by iterating.
- **Prompt shape it rewards:** describe the component/page, the design language, the states, and the data shape (mock is fine). It's component-centric — prompt one screen or one component well rather than a whole app at once.
- **Levers:** name shadcn primitives; give real content; specify variants and states; iterate ("now add the empty state", "make the header sticky"). Pairs naturally with 21st.dev components (same registry format).
- **Watch:** it leans Next.js/React — not the tool for a non-JS stack.

## Bolt (bolt.new)
- **Docs to verify:** https://bolt.new (StackBlitz) docs
- **Best at:** full-stack apps that run **live in the browser** (WebContainer); fast end-to-end demos you can click through and edit immediately.
- **Prompt shape it rewards:** state the stack explicitly (it can run many), the core flow, and the data. Because it runs the whole stack, be concrete about what's real vs. mocked.
- **Watch:** in-browser runtime has limits for heavy native deps; keep demo scope tight.

## Replit Agent
- **Docs to verify:** https://docs.replit.com (Agent section)
- **Best at:** one place for generate → run → deploy → DB → auth; good when the user wants a live URL and a database without leaving the tool. Mobile-friendly.
- **Prompt shape it rewards:** describe the app, the core entities, auth need, and "deploy it" as an explicit outcome. It'll provision infra, so name the infra you want (DB, auth) rather than leaving it implicit.
- **Watch:** ⚠️ agent behaviour and checkpoint/credit model change often — verify.

## Cursor / Windsurf (IDE agents)
- **Docs to verify:** https://docs.cursor.com · https://docs.windsurf.com
- **Best at:** working inside an **existing repository** — features, refactors, fixes — with the real codebase as context. **Not** the greenfield "describe an app" tools.
- **Prompt shape it rewards:** file/context anchoring (`@files`, `@folders`, rules files), a bounded task, and explicit "don't touch X" constraints. This is where the spec-driven path (`spec-driven.md`) shines — and where **spec-kit's `/speckit.*` commands actually run**, since they install into `.claude/`, `.cursor/`, etc.
- **Watch:** the "must-not-change" constraint matters most here — these agents edit real code.

## Base44
- **Docs to verify:** https://base44.com docs
- **Best at:** all-in-one app building with built-in data, auth, and hosting; similar niche to Lovable for non-developers.
- **Prompt shape it rewards:** app purpose · core entities · key screens · who logs in. Confirm current capabilities against docs — ⚠️ younger tool, faster drift.

---

## Cross-tool truths (apply everywhere)
- One feature per prompt. Numbered priority so the load-bearing feature is built first.
- Real content beats lorem ipsum — the layout the tool picks depends on realistic data.
- Name components and spacing; ban adjective-only design ("clean, modern, sleek").
- State responsiveness + loading/empty/error explicitly, or they get retrofitted.
- Constraints ("do not change auth", "keep the current routing") prevent collateral edits.
- Verify anything about pricing, credits, modes, or model versions live — all volatile.
