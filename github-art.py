#!/usr/bin/env python3
"""
github-art.py — paint text/art onto your GitHub contribution graph.

The graph is a 7-row (Sun..Sat, top..bottom) x ~53-column (weeks) grid.
This renders a message in a pixel font and creates backdated git commits
so the lit pixels turn green.

USAGE
  # 1. Preview only (no commits):
  python3 github-art.py "LOCKED IN" --dry-run

  # 2. In a NEW empty repo whose user.email is a verified GitHub email:
  python3 github-art.py "LOCKED IN" --intensity 4

  # then: git push   (and wait a few minutes for the graph to update)

OPTIONS
  --dry-run            Just print the ASCII preview; make no commits.
  --intensity N        Commits per lit pixel (darker green). Default 4.
  --start-sunday DATE  Left edge week, YYYY-MM-DD (must be a Sunday).
                       Default: auto-pick the leftmost visible week.
  --offset-weeks N     Shift the drawing right by N columns (to center it).
  --repo-dir PATH      Where to commit. Default: current directory.
"""

import argparse
import datetime as dt
import os
import subprocess
import sys

# Variable-width pixel font, 5 rows tall. '#' = lit.
FONT = {
    "A": ["###", "#.#", "###", "#.#", "#.#"],
    "B": ["##.", "#.#", "##.", "#.#", "##."],
    "C": ["###", "#..", "#..", "#..", "###"],
    "D": ["##.", "#.#", "#.#", "#.#", "##."],
    "E": ["###", "#..", "###", "#..", "###"],
    "F": ["###", "#..", "###", "#..", "#.."],
    "G": ["###", "#..", "#.#", "#.#", "###"],
    "H": ["#.#", "#.#", "###", "#.#", "#.#"],
    "I": ["###", ".#.", ".#.", ".#.", "###"],
    "J": ["..#", "..#", "..#", "#.#", "###"],
    "K": ["#.#", "#.#", "##.", "#.#", "#.#"],
    "L": ["#..", "#..", "#..", "#..", "###"],
    "M": ["#...#", "##.##", "#.#.#", "#...#", "#...#"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"],
    "O": ["###", "#.#", "#.#", "#.#", "###"],
    "P": ["##.", "#.#", "##.", "#..", "#.."],
    "Q": ["###", "#.#", "#.#", "##.", "###"],
    "R": ["##.", "#.#", "##.", "#.#", "#.#"],
    "S": ["###", "#..", "###", "..#", "###"],
    "T": ["###", ".#.", ".#.", ".#.", ".#."],
    "U": ["#.#", "#.#", "#.#", "#.#", "###"],
    "V": ["#.#", "#.#", "#.#", "#.#", ".#."],
    "W": ["#...#", "#...#", "#.#.#", "##.##", "#...#"],
    "X": ["#.#", "#.#", ".#.", "#.#", "#.#"],
    "Y": ["#.#", "#.#", ".#.", ".#.", ".#."],
    "Z": ["###", "..#", ".#.", "#..", "###"],
    "0": ["###", "#.#", "#.#", "#.#", "###"],
    "1": [".#.", "##.", ".#.", ".#.", "###"],
    "2": ["###", "..#", "###", "#..", "###"],
    "3": ["###", "..#", "###", "..#", "###"],
    "4": ["#.#", "#.#", "###", "..#", "..#"],
    "5": ["###", "#..", "###", "..#", "###"],
    "!": [".#.", ".#.", ".#.", "...", ".#."],
    "?": ["###", "..#", ".##", "...", ".#."],
    ".": ["...", "...", "...", "...", ".#."],
}

ROW_TOP = 1  # vertical offset so the 5-tall glyphs sit in rows 1..5 of 0..6


def render(message):
    """Return a set of (col, row) lit pixels for the message (rows 0..6)."""
    pixels = set()
    col = 0
    for ch in message.upper():
        if ch == " ":
            col += 3
            continue
        glyph = FONT.get(ch)
        if glyph is None:
            col += 4  # unknown char -> blank gap
            continue
        width = len(glyph[0])
        for r, line in enumerate(glyph):
            for c, px in enumerate(line):
                if px == "#":
                    pixels.add((col + c, ROW_TOP + r))
        col += width + 1  # 1-column gap between letters
    return pixels, col


def preview(pixels, width):
    print("\nPreview (Sun top .. Sat bottom):")
    for row in range(7):
        line = "".join("#" if (c, row) in pixels else "." for c in range(width))
        print("  " + line)
    print()


def most_recent_sunday(today):
    # weekday(): Mon=0..Sun=6 ; we want the Sunday on/before today
    return today - dt.timedelta(days=(today.weekday() + 1) % 7)


def default_start_sunday(today):
    # Leftmost fully-visible week ~ 52 weeks back, snapped to a Sunday.
    recent = most_recent_sunday(today)
    return recent - dt.timedelta(weeks=51)


def commit(repo_dir, when, msg, count):
    """Create `count` empty backdated commits dated `when` (a date)."""
    for i in range(count):
        stamp = dt.datetime(when.year, when.month, when.day, 12, 0, i % 60)
        iso = stamp.strftime("%Y-%m-%dT%H:%M:%S")
        env = dict(os.environ, GIT_AUTHOR_DATE=iso, GIT_COMMITTER_DATE=iso)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", msg],
            cwd=repo_dir, env=env, check=True,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )


def main():
    p = argparse.ArgumentParser(description="Paint art onto the GitHub contribution graph.")
    p.add_argument("message", help='Text to draw, e.g. "LOCKED IN"')
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--intensity", type=int, default=4)
    p.add_argument("--start-sunday", default=None)
    p.add_argument("--offset-weeks", type=int, default=0)
    p.add_argument("--repo-dir", default=".")
    args = p.parse_args()

    today = dt.date.today()
    pixels, width = render(args.message)
    full_width = width + args.offset_weeks
    pixels = {(c + args.offset_weeks, r) for (c, r) in pixels}

    preview(pixels, full_width)

    if full_width > 53:
        print(f"!! Drawing is {full_width} cols wide; the graph shows ~53. It will be clipped.\n")

    if args.dry_run:
        print("Dry run — no commits made.")
        return

    if args.start_sunday:
        start = dt.date.fromisoformat(args.start_sunday)
        if (start.weekday() + 1) % 7 != 0:
            sys.exit("--start-sunday must be a Sunday.")
    else:
        start = default_start_sunday(today)

    # sanity: are we in a git repo with an email set?
    if not os.path.isdir(os.path.join(args.repo_dir, ".git")):
        sys.exit(f"{args.repo_dir!r} is not a git repo. Run: git init")
    email = subprocess.run(["git", "config", "user.email"], cwd=args.repo_dir,
                           capture_output=True, text=True).stdout.strip()
    if not email:
        sys.exit("No git user.email set. Set it to a VERIFIED GitHub email first.")
    print(f"Committing as {email}, start Sunday {start}, intensity {args.intensity}...")

    made = skipped = 0
    for (c, r) in sorted(pixels):
        when = start + dt.timedelta(weeks=c, days=r)
        if when > today:
            skipped += 1
            continue
        commit(args.repo_dir, when, f"pixel {c},{r}", args.intensity)
        made += 1

    print(f"Done. {made} pixels painted ({made * args.intensity} commits)"
          + (f", {skipped} skipped (future dates)." if skipped else "."))
    print("Now run:  git push   then check your profile in a few minutes.")


if __name__ == "__main__":
    main()
