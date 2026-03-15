---
name: repo-local-github-auth
description: Keep Git and GitHub auth scoped to the aarshps workspace when working in this repo.
---

# Repo-Local GitHub Auth

Use this skill for issues, commits, pushes, or any GitHub CLI/API action.

## Required Commands

- Use `./scripts/gh-aarshps ...`. Do not run plain `gh ...` here.
- Git commits should use `Aarsh <aarshps@users.noreply.github.com>`.
- Verify login with `./scripts/gh-aarshps api user --jq .login`.

## Scope Rules

- Keep auth scoped to `/Users/aps/Source/aarshps`.
- Do not modify global Git or global GitHub CLI state.
- Let GitHub-authenticated `git` commands rely on local `.git/config`.

## Checks

- `git config user.name` should be `Aarsh`.
- `git config user.email` should be `aarshps@users.noreply.github.com`.
- Before push, confirm the current branch and `git status --short`.
