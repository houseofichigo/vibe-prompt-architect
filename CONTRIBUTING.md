# Contributing

The canonical Skill lives in `skills/vibe-prompt-architect/`. Everything outside that folder is repository tooling and is never shipped in `dist/skill.zip`.

## Workflow

1. Edit files under `skills/vibe-prompt-architect/`.
2. Rebuild the distributable archive:

   ```bash
   python3 scripts/build_dist.py
   ```

3. Validate and test:

   ```bash
   python3 scripts/validate_skill.py
   python3 -m unittest discover -s tests
   ```

4. Commit the Skill changes **and** the rebuilt `dist/skill.zip` together. CI fails if they drift apart.

## Rules

- Keep `SKILL.md` frontmatter portable: `name`, `description`, and optionally `license` and `metadata`. Avoid `compatibility` (OpenAI's validator rejects it); state environment needs in the body. Quote any value containing `: ` or ` #`.
- Keep `SKILL.md` under 500 lines; move detail into `references/`.
- No credentials, `.env` files, private keys, caches, or machine-specific paths.
- Scripts must run with the tools they document and fail with clear messages.
