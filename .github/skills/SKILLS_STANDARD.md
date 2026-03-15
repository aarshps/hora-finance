---
description: Standards for keeping hora-finance agent skills concise, current, and executable.
---

# Hora Finance Skills Standard

The `.github/skills` folder stores repo-specific instructions for future coding agents.

## Core Rules

1. Every file under `.github/skills` must stay at 100 lines or fewer, including frontmatter and blank lines.
2. Keep each skill focused on one concern such as auth, repo map, task start, resume context, or reporting workflow.
3. Write only repository-specific commands, paths, constraints, and failure modes.
4. Prefer short checklists and exact commands over long explanations.
5. When repo behavior changes, update the affected skill files and `docs/agent-resume.md` in the same commit.
6. If guidance becomes stale, fix or delete it immediately.

## Verification

```bash
find .github/skills -name '*.md' -type f -print | while read -r f; do
  lines=$(wc -l < "$f")
  [ "$lines" -le 100 ] || echo "FAIL: $f has $lines lines"
done
```
