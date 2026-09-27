# Vibe Prompt Architect

Turn a raw app or feature idea into a refined, tool-specific build prompt for vibecoding / AI app builders — Lovable, Replit, v0, Bolt, Cursor, Windsurf, Base44, and similar. Use this whenever the user wants to build, mock up, or prototype an app, website, dashboard, UI, or feature with one of these tools, asks to "write a prompt for Lovable/Replit/v0/etc.", wants an idea shaped into something ready to paste into a builder, mentions pulling UI components (21st.dev, shadcn, Magic UI, Aceternity) into a build, or wants a spec before building. It first asks whether they want a quick mock-up/demo or real development, then researches the target tool's live docs and component registries and returns a build-ready prompt — or a spec-driven package for real dev. Trigger even when the user only describes an app idea with a builder tool in play, or names a tool without saying the word "prompt".

This repository packages the **`vibe-prompt-architect`** Agent Skill in the open [`SKILL.md` format](https://agentskills.io/specification), so it can be used by Claude, Codex/ChatGPT, Cursor and other agents that support Agent Skills.

## Install

### Any supported agent (recommended)

```bash
npx skills add houseofichigo/vibe-prompt-architect --skill vibe-prompt-architect
```

Target a specific agent with `--agent`, for example `--agent claude-code`, `--agent codex` or `--agent cursor`. Add `-g` to install for your user instead of the current project. Try it without installing:

```bash
npx skills use houseofichigo/vibe-prompt-architect --skill vibe-prompt-architect
```

### Manual install

| Host | Where the Skill goes |
|------|----------------------|
| Claude Code | copy `skills/vibe-prompt-architect/` to `~/.claude/skills/vibe-prompt-architect/` (personal) or `.claude/skills/vibe-prompt-architect/` (project) |
| Claude apps (claude.ai / desktop) | upload `dist/skill.zip` in Claude's Skills settings |
| Claude API | upload the Skill folder through the `/v1/skills` endpoints |
| Codex | copy `skills/vibe-prompt-architect/` to `~/.agents/skills/vibe-prompt-architect/` (personal) or `.agents/skills/vibe-prompt-architect/` (repository) |
| Other agents | unzip `dist/skill.zip` into the agent's skills directory |

## What's inside

```text
skills/vibe-prompt-architect/
  LICENSE.txt
  SKILL.md
  assets/prompt-templates/debug.md
  assets/prompt-templates/feature.md
  assets/prompt-templates/mock.md
  assets/prompt-templates/real-spec.md
  references/component-sources.md
  references/prompt-anatomy.md
  references/spec-driven.md
  references/tool-adapters.md
dist/skill.zip        # the same Skill, zipped, for upload-based hosts
```

Everything outside `skills/vibe-prompt-architect/` is repository tooling and is not part of the Skill.

## Validate

```bash
python3 scripts/validate_skill.py          # Agent Skills spec + Claude + OpenAI/Codex rules
python3 scripts/build_dist.py --check      # dist/skill.zip matches the Skill folder
python3 -m unittest discover -s tests
```

These checks need only Python 3.9+ and run in CI on every push. They verify structure and host rules, not the Skill's runtime behavior, which depends on the host, model, tools and permissions available.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). After editing the Skill, run `python3 scripts/build_dist.py` and commit the rebuilt `dist/skill.zip`.

## License

Released under the [MIT License](LICENSE). The license text is bundled with the Skill as `LICENSE.txt`.
