---
name: plugin-authoring
description: Use whenever someone wants to create, add, or scaffold a plugin, skill, agent, command, or hook in this marketplace — phrases like "create a new plugin for X", "add this skill to the marketplace", "turn this into a team skill", "add a command for Y". Also use for "what plugins/skills exist", "validate the marketplace", or "publish/push marketplace changes". This is the entry point for all marketplace maintenance so the team doesn't need to remember folder layouts or JSON schemas by hand.
---

# Plugin Authoring

You are helping a teammate add to, browse, or maintain this plugin
marketplace. They may not know the folder structure or JSON schema — your
job is to handle that from a plain-language request.

## Locating the marketplace

The marketplace root contains `.claude-plugin/marketplace.json`. Before
doing anything else:

1. Check if the current directory (or a parent of it) is already a clone of
   this marketplace — look for `.claude-plugin/marketplace.json` walking up
   from the working directory.
2. If it's not, ask if there's an existing local clone elsewhere on disk
   whose path you should use.
3. If there isn't one yet, this is likely someone's first time using this —
   offer to clone it for them: ask for (or confirm, if you already know it)
   the repo URL, then run `git clone <url>` into a sensible default location
   (e.g. `~/dev/<repo-name>` or wherever they'd prefer) and use that as the
   marketplace root from here on. Don't guess a path silently either way —
   confirm where it landed.

This means someone should be able to say "create a new plugin for X" as
their very first message, with no prior manual `git clone`, and still get a
working result — cloning is something you do for them, not something they
need to already know to do.

Note: pushing later (via `/publish-plugin`) still requires their git host
auth to already be set up (SSH key or access token) — that's a one-time
account-level step outside anything a clone can solve, and isn't something
to attempt on their behalf.

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
3. Make sure it has the required frontmatter/shape (see "Reference shapes"
   below). If given rough notes instead of a finished file, write it
   properly: a clear, specific `description` (this is what Claude uses to
   decide whether to load the skill later — vague descriptions won't
   trigger reliably) and concrete instructions, not just a copy of their
   notes.
4. Bump `version` in that plugin's `.claude-plugin/plugin.json` (patch bump
   for additions, unless told otherwise).
5. Run the validator (see below) before proposing to commit anything.
6. Summarize what changed and where, then commit with a clear message (e.g.
   `helm: add skill for chart values.yaml conventions`) and push, if
   confirmed.

## Flow: "create a new plugin for X"

1. Create `plugins/<x>/` (kebab-case name) with a `.claude-plugin/plugin.json`
   — real name, version `0.1.0`, description, author = the requester — plus
   whichever of `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json` the
   request actually needs. Generate these directly per "Reference shapes"
   below — don't look for a template folder to copy, there isn't one.
2. Add an entry to the root `.claude-plugin/marketplace.json` `plugins`
   array: `name`, `source: "./plugins/<x>"`, `description`,
   `version: "0.1.0"`, `category` (reuse an existing one where it fits —
   ask if unclear), `tags`, `owner`.
3. Run the validator, summarize, commit/push if confirmed.

## Reference shapes

**`plugin.json`** (`plugins/<name>/.claude-plugin/plugin.json`):
```json
{
  "name": "plugin-name",
  "version": "0.1.0",
  "description": "One line — shown when browsing.",
  "author": { "name": "...", "email": "..." }
}
```

**`SKILL.md`** (`plugins/<name>/skills/<skill-name>/SKILL.md`):
```markdown
---
name: skill-name
description: Specific — what it does AND when to use it. This is the only
  thing used to decide whether to load it, so be concrete, not vague.
---

# Skill Title

Instructions for what Claude should do when this skill is active.
```

**Command** (`plugins/<name>/commands/<command-name>.md`):
```markdown
---
description: One line shown when browsing available commands.
---

# Command Title

Deterministic steps — only use a command instead of a skill for things that
should run identically every time.
```

**`.mcp.json`** (`plugins/<name>/.mcp.json`, plugin root):
```json
{
  "mcpServers": {
    "server-name": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/some-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": { "API_KEY": "${API_KEY}" }
    }
  }
}
```
Must be wrapped in a top-level `"mcpServers"` key — a bare server object at
the top level is silently ignored. `${CLAUDE_PLUGIN_ROOT}` resolves to the
plugin's own install path, useful for bundling a server binary/script inside
the plugin itself.

For a remote server instead of a local process, use `"type"` + `"url"`
instead of `"command"`:
```json
{
  "mcpServers": {
    "server-name": {
      "type": "http",
      "url": "https://your-server.example.com/mcp"
    }
  }
}
```
`"type"` is required whenever `"url"` is present (`"http"`, `"sse"`, or
`"ws"`) — a `url` with no `type` is treated as a broken stdio server and
silently skipped at session start, not just a style preference.

Only use these three shapes exactly as-is; don't invent extra frontmatter
fields.

## Flow: "what plugins/skills exist" / browsing

Read `.claude-plugin/marketplace.json` and `docs/CATALOG.md` and answer from
those directly. If they're looking for something specific, check `tags` and
`description` across all plugin entries.

## Flow: "validate" / "check everything is good"

Use the `/validate-plugin` command's fix loop (see
`plugins/plugin-development/commands/validate-plugin.md` for the full auto-fix vs
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

Use `/publish-plugin` — see `plugins/plugin-development/commands/publish-plugin.md`. Don't
push as a side effect of anything else; it's always an explicit step.

## General rules

- Never hand-edit `docs/CATALOG.md` — it's generated.
- Always run the validator before committing.
- Prefer small, focused commits per plugin over one giant commit touching
  everything.
- If unsure which plugin something belongs in, ask rather than guessing.