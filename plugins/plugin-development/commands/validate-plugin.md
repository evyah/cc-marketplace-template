---
description: Validate the marketplace, automatically fix what's safe to fix, and flag what needs a human decision
---

# Validate

Run the script in structured mode and act on the result — don't just report it.

```
python3 plugins/plugin-development/scripts/validate.py --json
```

Parse the JSON output (`errors`, `warnings`, each with a `code`, `path`, and
`message`). Then loop, up to 5 passes:

1. For every error whose `code` is in the **safe-to-auto-fix** list below,
   fix it directly by editing the file — don't ask first.
2. Re-run `python3 plugins/plugin-development/scripts/validate.py --json`.
3. Repeat until either no errors remain, no progress was made on the last
   pass, or 5 passes have run.

After the loop, report clearly, in two groups:
- **Fixed automatically** — list what changed and in which files, so it's
  easy to `git diff` before committing.
- **Needs your input** — anything left, with a suggested fix per item where
  you have one. Don't guess at these; a wrong guess here is worse than
  asking.

## Safe to auto-fix

| code | fix |
| --- | --- |
| `EMPTY_PLUGIN_ENTRY` | Remove the empty `{}` entry from `marketplace.json` — it's never intentional. |
| `MANIFEST_MISSING_FIELD` (`name`/`version`) | `name` from the plugin's folder name (kebab-case); `version` defaults to `"0.1.0"` if this is a new plugin. |
| `MANIFEST_NAME_MISMATCH` | Sync `marketplace.json`'s entry name to match `plugin.json` — treat `plugin.json` as the source of truth. |
| `PLUGIN_MISSING_DESCRIPTION` / `MANIFEST_MISSING_FIELD` (`description`) | Draft one from the plugin's actual skill/command descriptions — but say explicitly in your summary that it's a draft worth a human read, since this text is what makes the plugin findable. |
| `SKILL_MISSING_FRONTMATTER` / `SKILL_MISSING_NAME` | Add `name:` from the skill's folder name. |
| `SKILL_MISSING_DESCRIPTION` | Draft one from the skill's own body content — flag as a draft: a bad description means this skill silently never triggers, so it deserves a human look even though you filled it in. |
| `COMMAND_MISSING_DESCRIPTION` | Draft a one-line description from the command's body. |
| Invalid JSON (any `*_INVALID_JSON` code) from a trivial syntax slip (trailing comma, unquoted key, unmatched bracket) | Fix the syntax directly. If the file is malformed enough that you're not confident what was intended, don't guess — flag it instead. |

## Never auto-fix — always ask

| code | why |
| --- | --- |
| `PLUGIN_DUPLICATE_NAME` | Renaming picks a winner between two people's work — needs a human call. |
| `PLUGIN_SOURCE_NOT_FOUND` | Could be a typo or a genuinely deleted/moved folder — don't guess which. |
| `PLUGIN_MISSING_OWNER` | Only a human knows who actually owns this. |
| `SKILL_DESCRIPTION_SHORT` (warning) | Improving a vague description is a judgment call about what the skill should trigger on — surface it, don't silently rewrite someone's wording. |
| `MCP_MISSING_MCPSERVERS_KEY` / `MCP_SERVER_MISSING_TRANSPORT` | The person knows whether this is meant to be a local process or a remote URL — don't invent a command or endpoint. |
| `MCP_URL_MISSING_TYPE` | Usually a one-word fix (`"type": "http"` is the common case), but confirm rather than guess — `sse`/`ws` are also valid and only the person knows which transport the server actually speaks. |

## Rules

- Never touch `docs/CATALOG.md` by hand — the script regenerates it whenever
  errors are clean; that's expected and fine to include in the commit.
- If a fix pass makes no progress (same error count, same codes), stop and
  report rather than looping uselessly.
- Don't commit or push as part of this command — that's `/publish-plugin`, and
  should be a separate, explicit step so nothing gets pushed without the
  person seeing what changed first.