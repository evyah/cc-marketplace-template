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

## How validation works

**It's not automatic.** There's no CI and no git hook — nothing runs in the
background when a file changes. Validation only happens when something
explicitly triggers it:

| Trigger | What happens |
| --- | --- |
| `python3 plugins/plugin-development/scripts/validate.py` | Run it yourself, anytime, from the repo root |
| `/validate-plugin` in Claude Code | Same checks, but Claude auto-fixes what's safe (missing fields, empty entries, drafts a missing description) and only asks you about things that need a real decision |
| Plain language — *"validate the marketplace"* | Triggers the `plugin-authoring` skill, which does the same thing as `/validate-plugin` |
| `/publish-plugin` | Runs validation **first**, automatically, before anything gets committed — so nothing broken can get pushed this way, but it's still only running because you ran `/publish-plugin`, not on its own |

### What it checks

- `marketplace.json` is valid JSON with `name`, `owner`, `plugins`
- Every plugin entry has `name` and `source`; warns if `description` or `owner` is missing
- No two plugins share a `name`
- Every `source` path actually exists
- Each plugin's own `plugin.json` is valid JSON with `name`, `version`, `description`
- Every `SKILL.md` has `name` + `description` in its frontmatter (and warns if the description is too short to trigger reliably)
- Every command file has a `description` in its frontmatter
- If a plugin has a `.mcp.json`, it's checked structurally, not just for valid JSON — see below

### What a plugin must have, minimum

- `plugins/<name>/.claude-plugin/plugin.json` with `name`, `version`, `description`
- A matching entry in the root `marketplace.json` (`name`, `source` required; `description`/`owner` strongly recommended)
- At least one of `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json` — a plugin with none of these is valid JSON but doesn't actually do anything

### MCP servers specifically

A `.mcp.json` needs a top-level `"mcpServers"` key wrapping each server —
a bare server object with no wrapper is silently ignored by Claude Code, not
just invalid. Each server needs either `"command"` (local process) or
`"url"` (remote); if it's `"url"`, it also needs `"type"` (`"http"`, `"sse"`,
or `"ws"`) — a `url` with no `type` is a documented Claude Code failure mode
where the server gets treated as broken and silently skipped at startup,
not a style nitpick.

## Validate locally

```bash
python3 plugins/plugin-development/scripts/validate.py
```

No dependencies — just Python (stdlib only).

## Adding a plugin

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Short version: install `plugin-development`, say "create a new plugin for X," done.