# honeycomb
Honeycomb is a workflow for software development with agents

## Install

```bash
npx skills add https://gitlab.com/wawow830/honeycomb
```

Install all Honeycomb skills together; they share supporting files.

## Structure

- `.agents/skills/`: Reusable skills, supporting files, and configuration templates.
- `honeycomb/`: Project configuration created during setup.
- `.honeycomb/`: Version-controlled production artifacts created during execution.

## Goals
- turbo speed development
- without compromise of quality or taste
- be as deterministic as possible
    - clear bounds
    - clear input/processing/output
    - everything must follow a structure
- stack agnostic
- simplicity rules
