# Honeycomb

Honeycomb is a system for software development with agents.

## Goals
- turbo speed development
- without compromise of quality or taste
- be as deterministic as possible
- everything must follow a structure
- stack agnostic
- simplicity rules

## Install

Requires Python 3.10+, Git, Unix, and a local `main` branch with a commit.
The main checkout must have a `.git` directory.

1. Copy the `honeycomb`, `define`, `execute`, `prove`, and `integrate` directories
   from `.agents/skills/` into your project's `.agents/skills/`. Do not overwrite
   existing skills with the same names; resolve any collisions first.
2. Add `/.honeycomb/` to `.gitignore` and commit the setup.
3. Ask your agent to use Honeycomb. If it does not discover skills, point it to
   [Honeycomb](.agents/skills/honeycomb/SKILL.md), which routes to the stage skills.
   All five skills use the shared CLI in `honeycomb/scripts/honeycomb.py`.
