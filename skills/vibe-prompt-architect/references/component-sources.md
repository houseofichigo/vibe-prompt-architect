# Component Sources

Where to pull **real, named** UI components so the visual layer is the thing the
user pictured — not a generic template. Naming concrete components is the single
biggest quality lever for the UI, across every tool. Do this whenever the request
is design-forward (landing pages, dashboards, marketing, polished app UI).

## How to use a component in a build prompt

The modern shadcn ecosystem is a **registry format**, not one library: many
authors publish `registry.json` indexes, and `npx shadcn@latest add "<url>"`
fetches from any of them exactly like the official one. Every 21st.dev component
page carries three things you can lift straight into a prompt:

1. A **live preview** (so you/the user can confirm it's the right thing).
2. An **AI-ready prompt** — a description written to drop the component into a build via Cursor / Claude Code / v0 / Lovable.
3. An **install line** — `npx shadcn@latest add "https://21st.dev/r/<author>/<component>?api_key=$API_KEY_21ST"`.

**In a build prompt, do one of:**
- Paste the component's **AI-ready prompt / description** into the UI section, or
- Give the tool the **install line** and tell it to add + use that component, or
- For v0/Lovable/Cursor with a registry MCP connected, tell the agent to search the registry and add it.

⚠️ Installs from 21st.dev generally need an `API_KEY_21ST` and are metered (free
tier = a few copies/day; paid = unlimited). Browsing/previewing is free. Say this
to the user rather than assuming they have a key.

## How to find components (no MCP needed)

- **Search** 21st.dev for the component type ("hero", "pricing table", "sidebar", "bento grid", "auth form").
- **`WebFetch` the component's `.md` page** — every 21st component has one at `https://21st.dev/@<author>/components/<name>.md` giving the description, deps, and install line.
- **`WebFetch` the full directory** at `https://21st.dev/llms.txt` when you need to scan what's available.
- If a **21st / registry MCP** or the **`21st-dev/skill`** is connected, prefer it — it returns previews + writes files directly. (`npx skills add 21st-dev/skill`, or the 21st Claude Code plugin.)

## The registry landscape (pick by aesthetic)

Point the tool at the source whose style matches the brief. All publish in
shadcn-registry format, so any works with v0 / Lovable / Cursor.

| Source | Strength |
|---|---|
| **21st.dev** | Community catalog: components, full templates, shadcn themes, shaders/gradients; AI-ready prompts per item |
| **shadcn/ui** | The base primitives everything composes on; the default vocabulary to name |
| **Magic UI** | Animated heroes, backgrounds, buttons, text effects — landing-page motion |
| **Aceternity UI** | Bold, animated marketing/hero sections, dramatic effects |
| **tweakcn** | Visual theme editor for shadcn tokens — hand the tool a token set, not adjectives |
| **Origin UI / Kokonut / Cult UI / etc.** | Additional registries; check the 21st registry directory for the current landscape |

To pick well: match motion level (marketing → Magic UI/Aceternity; app UI →
shadcn/Origin), check the item's npm deps (one card can drag in an animation
runtime), and prefer items that shipped recently.

## Design tokens over adjectives

"Clean and modern" produces generic output. Instead give the tool a concrete
system: a palette (hex or named tokens), type scale, spacing rhythm, radius, and
one or two reference components. `tweakcn` and the shadcn theme format are good
ways to hand over a real token set the tool can apply consistently. When a brand
already exists, extract its tokens first and state them in the UI section of the
prompt.

## Verify
Registry URLs, key requirements, and free-tier limits are ⚠️ volatile — confirm
against the live page before telling the user what an install will cost or require.
