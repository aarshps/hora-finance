---
name: task-start-rules
description: Mandatory pre-task workflow for coding agents in this repo.
---

# Task Start Rules

Apply these steps before starting any task in `hora-finance`.

1. Pull latest from default branch:
   - `git checkout main`
   - `git pull --ff-only origin main`
2. Check local state with `git status --short`.
3. Read `.github/skills/repo-local-github-auth/SKILL.md`.
4. Read `.github/skills/repo-map/SKILL.md` and `docs/agent-resume.md`.
5. Before any GitHub action, verify `./scripts/gh-aarshps api user --jq .login` returns `aarshps`.
6. Prefer static checks unless the task explicitly requires live Google auth or Sheets data.

## Finish Rules

1. If architecture, workflow, or operator steps changed, update `.github/skills` and `docs/agent-resume.md` in the same commit.
2. Keep each skill file within the 100-line limit.
