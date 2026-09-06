# cc-marketplace-template

Template for a private team plugin marketplace for Claude Code. Skills, commands, agents, hooks, MCP configs — one plugin per technology, shared across the team instead of everyone rebuilding the same thing on their own.

No CI needed. Validation runs as a local script, so this works the same on GitHub, self-hosted GitLab, or fully airgapped.

## Why

- **One plugin per technology, not per skill and not per category.** Enough granularity to install only what you need, without dozens of tiny plugins to manage.
- **No CI required.** `validate.py` is a zero-dependency Python script — run it locally, as a git hook, or wire it into CI later if you get one.
- **Add plugins by talking, not by memorizing commands.** The `plugin-development` plugin ships a skill that scaffolds, validates, and commits for you from a plain-language request.
- **Any git host.** GitHub, GitLab (including self-managed), whatever you use.

## What's here right now

| Component | What it does |
| --- | --- |
| `.claude-plugin/marketplace.json` | The catalog — every plugin gets listed here |
| `plugin-development` | The plugin that helps you build other plugins: scaffolding, validation, publishing |
| `plugin-authoring` skill | Say what you want in plain language, it figures out the rest |
| `/validate-plugin` | Runs the checks, auto-fixes what's safe, tells you what needs a decision |
| `/publish-plugin` | Validates, commits, pushes |
| `validate.py` | The actual checks — stdlib only, no pip install needed |

This is a template. There's no real technology plugin (Helm, Grafana, whatever) in here yet — `plugin-development` is the only plugin so far. Add your own the same way it was built.

## Install in Claude Code

```
/plugin marketplace add evyah/cc-marketplace-template
/plugin install plugin-development@team-plugin-marketplace
```

That's it. From there, just talk to it:

```
"Create a new plugin for Helm"
"Add this skill to the marketplace"
"Validate the marketplace"
"Publish"
```

Or run the commands directly if you'd rather: `/validate-plugin`, `/publish-plugin`.

## Repository layout

```
.
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── plugin-development/
│       ├── .claude-plugin/plugin.json
│       ├── skills/plugin-authoring/SKILL.md
│       ├── commands/
│       │   ├── validate-plugin.md
│       │   └── publish-plugin.md
│       └── scripts/validate.py
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

`docs/CATALOG.md` gets generated the first time you run the validator — not committed yet since nothing's been validated in this repo.

## Validate locally

```bash
python3 plugins/plugin-development/scripts/validate.py
```

Checks the catalog and every plugin manifest for missing fields, duplicate names, broken paths, missing skill/command descriptions. No dependencies — just Python.

## Adding a plugin

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Short version: install `plugin-development`, say "create a new plugin for X," done.
