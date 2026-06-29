# 🌱 astroturf

*sleepmaxxing, while the loop is running...*

Synthetic grass for your contribution graph. This repo is **pixel art made of backdated git commits** — every green square on the calendar is just commits authored on a chosen date.

> Currently spelling **`LOCK IN`** across the graph.

## How it works

The GitHub contribution graph is a 7-row (Sun→Sat) × ~53-column (weeks) grid. A cell turns green when you have ≥1 commit *authored* on that date — and git lets you set the author date to anything:

```bash
GIT_AUTHOR_DATE="2025-09-07T12:00:00" GIT_COMMITTER_DATE="2025-09-07T12:00:00" \
  git commit --allow-empty -m "pixel"
```

So "drawing" is just: render text in a pixel font → map each lit pixel to a date → make commits there. The shade of green scales with commits-per-day relative to your busiest day, so this repo stacks several commits per pixel for solid color.

## Repaint it

```bash
# preview only, no commits
python3 github-art.py "LOCK IN" --dry-run

# paint into this repo (intensity = commits per pixel = darkness)
python3 github-art.py "SHIP IT" --intensity 30 --offset-weeks 8
git push --force
```

| Flag | Meaning |
| --- | --- |
| `--intensity N` | commits per lit pixel (higher = darker green) |
| `--start-sunday YYYY-MM-DD` | left-edge week (must be a Sunday) |
| `--offset-weeks N` | shift the drawing right to center it |
| `--dry-run` | print the ASCII preview, make no commits |

The font covers A–Z, 0–5 and `! ? .`

## Notes

- The author email must be a **verified** email on your GitHub account, or the commits won't count.
- Pixels dated in the future fill in as those dates arrive.
- **Undo:** delete the repo (`gh repo delete <you>/astroturf --yes`) and the green vanishes.

---

*Not real grass. No commits were harmed (or, arguably, meaningfully made).*
