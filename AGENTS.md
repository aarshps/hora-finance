# AGENTS.md

## GitHub Identity

- This repo is part of the `/Users/aps/Source/aarshps` workspace and must use the shared GitHub CLI profile at `/Users/aps/Source/aarshps/.gh-aarshps`.
- Use the GitHub account `aarshps` for GitHub operations in this repo. Do not use the global `aps_uhg` profile here.
- Git commits in this repo should use `Aarsh <aarshps@users.noreply.github.com>` unless the user asks for a different author identity.
- For direct GitHub CLI commands, use `./scripts/gh-aarshps ...`.
- Do not run plain `gh ...` in this repo. On this machine, plain `gh` still resolves to the global `aps_uhg` profile.
- GitHub-authenticated `git` commands in this repo should rely on repo-local `.git/config` settings that point GitHub auth to `/Users/aps/Source/aarshps/.gh-aarshps`.

## Isolation

- Keep auth and workflow changes scoped to `/Users/aps/Source/aarshps`. Do not edit machine-global Git or GitHub auth state for this repo.
- Do not modify repos outside this workspace unless the user explicitly asks.

## Agent Context

- Read `.github/skills/task-start-rules/SKILL.md` before editing code or GitHub state.
- Read `docs/agent-resume.md` when resuming work or taking over from another agent.
- Keep `.github/skills` guidance repo-specific and under 100 lines per file.
