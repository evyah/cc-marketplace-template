---
name: plugin-authoring
description: Use whenever someone wants to create, add, or scaffold a plugin, skill, agent, command, or hook in this marketplace — phrases like "create a new plugin for X", "add this skill to the marketplace", "turn this into a team skill", "add a command for Y". Also use for "what plugins/skills exist", "validate the marketplace", or "publish/push marketplace changes". This is the entry point for all marketplace maintenance so the team doesn't need to remember folder layouts or JSON schemas by hand.
---

# Plugin Authoring

You are helping a teammate add to, browse, or maintain this plugin
marketplace. They may not know the folder structure or JSON schema — your
job is to handle that from a plain-language request.

## Locating the marketplace

The marketplace root contains `.claude-plugin/marketplace.json`. If you're
not already inside a clone of it, ask where the local clone lives before
doing anything else — don't guess a path.

## Flow: "add this skill/command/agent to the marketplace"

1. Figure out the target plugin:
   - If they named an existing plugin, use it.
   - If they didn't, and the content clearly fits an existing plugin's
     technology/domain, suggest that plugin and confirm before proceeding.
   - If nothing fits, this is a new plugin — see "create a new plugin" below,
     then add the content into it.
2. Copy the content into the right subfolder:
   - Skill → `plugins/<name>/skills/<skill-name>/SKILL.md`
   - Command → `plugins/<name>/commands/<command-name>.md`
   - Agent → `plugins/<name>/agents/<agent-name>.md`
   - Hook → `plugins/<name>/hooks/hooks.json` (merge into existing file if present)
   - MCP server → `plugins/<name>/.mcp.json` (merge into existing file if present)
3. Make sure it has the required frontmatter/shape — see
   `plugins/example-plugin/` for the reference format of each type. If given
   rough notes instead of a finished file, write it properly: a clear,
   specific `description` (this is what Claude uses to decide whether to
   load the skill later — vague descriptions won't trigger reliably) and
   concrete instructions, not just a copy of their notes.
4. Bump `version` in that plugin's `.claude-plugin/plugin.json` (patch bump
   for additions, unless told otherwise).
5. Run the validator (see below) before proposing to commit anything.
6. Summarize what changed and where, then commit with a clear message (e.g.
   `helm: add skill for chart values.yaml conventions`) and push, if
   confirmed.

## Flow: "create a new plugin for X"

1. Copy `plugins/example-plugin/` to `plugins/<x>/` (kebab-case name).
2. Fill in `.claude-plugin/plugin.json`: real name, version `0.1.0`,
   description, author = the requester.
3. Add an entry to the root `.claude-plugin/marketplace.json` `plugins`
   array: `name`, `source: "./plugins/<x>"`, `description`,
   `version: "0.1.0"`, `category` (reuse an existing one where it fits —
   ask if unclear), `tags`, `owner`.
4. Remove the placeholder `example-skill`/`example-command` unless they want
   to keep it as a starting point.
5. Run the validator, summarize, commit/push if confirmed.

## Flow: "what plugins/skills exist" / browsing

Read `.claude-plugin/marketplace.json` and `docs/CATALOG.md` and answer from
those directly. If they're looking for something specific, check `tags` and
`description` across all plugin entries.

## Flow: "validate" / "check everything is good"

Use the `/validate` command's fix loop (see
`plugins/plugin-development/commands/validate.md` for the full auto-fix vs
ask-first breakdown by error code): run the script with `--json`, auto-fix
what's safe, ask about anything that needs a human decision, and repeat
until clean.

Once the mechanical pass is clean, do a **judgment pass** on whatever was
just added or changed: is the skill's `description` specific enough to
actually trigger in a real conversation? Is it redundant with an existing
skill? Is `category`/`tags` accurate? Report anything questionable rather
than silently fixing it — these are judgment calls, not mechanical ones,
including the auto-drafted descriptions the fix loop may have written; those
are explicitly flagged as drafts and deserve a second look here.

## Flow: "publish" / "push the marketplace"

Use `/publish` — see `plugins/plugin-development/commands/publish.md`. Don't
push as a side effect of anything else; it's always an explicit step.

## General rules

- Never hand-edit `docs/CATALOG.md` — it's generated.
- Always run the validator before committing.
- Prefer small, focused commits per plugin over one giant commit touching
  everything.
- If unsure which plugin something belongs in, ask rather than guessing.