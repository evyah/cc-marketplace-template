#!/usr/bin/env python3
"""
Marketplace validator + catalog generator.

Deterministic checks only — no LLM involved for the checking itself. Run
this before every commit that touches the marketplace, or via /validate.

Usage:
  python3 plugins/plugin-development/scripts/validate.py            # human-readable
  python3 plugins/plugin-development/scripts/validate.py --json     # structured, for automated fixing

Exit code 0 = all good. Exit code 1 = errors found.

Stdlib only, on purpose — no pip install / venv needed to run this, which
matters in an airgapped environment.
"""

import json
import re
import sys
from pathlib import Path

# Repo root = three levels up from this script
# (plugins/plugin-development/scripts/validate.py -> repo root)
ROOT = Path(__file__).resolve().parents[3]

JSON_MODE = "--json" in sys.argv

errors = []
warnings = []


def rel(p) -> str:
    p = Path(p)
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def add_error(code: str, path, message: str):
    errors.append({"code": code, "path": rel(path) if path else None, "message": message})


def add_warning(code: str, path, message: str):
    warnings.append({"code": code, "path": rel(path) if path else None, "message": message})


def read_json(path: Path, label: str, code_prefix: str):
    if not path.exists():
        add_error(f"{code_prefix}_NOT_FOUND", path, f"{label}: file not found at {rel(path)}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        add_error(f"{code_prefix}_INVALID_JSON", path, f"{label}: invalid JSON — {e}")
        return None


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
FIELD_RE = re.compile(r"^(\w[\w-]*):\s*(.*)$")


def parse_frontmatter(content: str):
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None
    fm = {}
    for line in match.group(1).splitlines():
        m = FIELD_RE.match(line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("'\"")
    return fm


# ---- 1. Root marketplace.json ----

marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
marketplace = read_json(marketplace_path, "marketplace.json", "MARKETPLACE")

if marketplace:
    for field in ("name", "owner", "plugins"):
        if field not in marketplace:
            add_error(
                "MARKETPLACE_MISSING_FIELD",
                marketplace_path,
                f'marketplace.json: missing required field "{field}"',
            )
    if marketplace.get("name") and re.search(r"[^a-z0-9-]", marketplace["name"]):
        add_warning(
            "MARKETPLACE_NAME_FORMAT",
            marketplace_path,
            f'marketplace.json: name "{marketplace["name"]}" should be kebab-case',
        )

plugin_entries = (marketplace or {}).get("plugins", [])
seen_names = set()

for entry in plugin_entries:
    if not isinstance(entry, dict) or not entry:
        add_error(
            "EMPTY_PLUGIN_ENTRY",
            marketplace_path,
            "marketplace.json: found an empty/invalid plugin entry — remove or fill it in",
        )
        continue

    name = entry.get("name")
    ctx = f'plugin "{name or "(unnamed)"}"'

    if not name:
        add_error("PLUGIN_MISSING_NAME", marketplace_path, f"{ctx}: missing \"name\"")
    if not entry.get("source"):
        add_error("PLUGIN_MISSING_SOURCE", marketplace_path, f"{ctx}: missing \"source\"")
    if not entry.get("description"):
        add_warning(
            "PLUGIN_MISSING_DESCRIPTION",
            marketplace_path,
            f'{ctx}: missing "description" (shown when browsing)',
        )
    if not entry.get("owner"):
        add_warning(
            "PLUGIN_MISSING_OWNER",
            marketplace_path,
            f'{ctx}: missing "owner" — nobody to ask when this breaks',
        )

    if name:
        if name in seen_names:
            add_error("PLUGIN_DUPLICATE_NAME", marketplace_path, f'marketplace.json: duplicate plugin name "{name}"')
        seen_names.add(name)

    source = entry.get("source", "")
    if source.startswith("./"):
        plugin_dir = ROOT / source
        if not plugin_dir.exists():
            add_error(
                "PLUGIN_SOURCE_NOT_FOUND",
                marketplace_path,
                f'{ctx}: source path "{source}" does not exist',
            )
            continue

        # ---- 2. Each plugin's own manifest ----
        manifest_path = plugin_dir / ".claude-plugin" / "plugin.json"
        manifest = read_json(manifest_path, f"{ctx} > plugin.json", "MANIFEST")
        if manifest:
            for field in ("name", "version", "description"):
                if not manifest.get(field):
                    add_error(
                        "MANIFEST_MISSING_FIELD",
                        manifest_path,
                        f'{rel(manifest_path)}: missing required field "{field}"',
                    )
            if manifest.get("name") and name and manifest["name"] != name:
                add_warning(
                    "MANIFEST_NAME_MISMATCH",
                    manifest_path,
                    f'{rel(manifest_path)}: name "{manifest["name"]}" doesn\'t match '
                    f'marketplace.json entry name "{name}"',
                )

        # ---- 3. Skills: every SKILL.md needs name + description frontmatter ----
        skills_dir = plugin_dir / "skills"
        if skills_dir.exists():
            for skill_folder in skills_dir.iterdir():
                if not skill_folder.is_dir():
                    continue
                skill_file = skill_folder / "SKILL.md"
                if not skill_file.exists():
                    add_warning("SKILL_MISSING_FILE", skill_folder, f"{rel(skill_folder)}: no SKILL.md found")
                    continue
                content = skill_file.read_text(encoding="utf-8")
                fm = parse_frontmatter(content)
                if not fm:
                    add_error(
                        "SKILL_MISSING_FRONTMATTER",
                        skill_file,
                        f"{rel(skill_file)}: missing YAML frontmatter (--- name / description ---)",
                    )
                else:
                    if not fm.get("name"):
                        add_error("SKILL_MISSING_NAME", skill_file, f'{rel(skill_file)}: frontmatter missing "name"')
                    desc = fm.get("description")
                    if not desc:
                        add_error(
                            "SKILL_MISSING_DESCRIPTION",
                            skill_file,
                            f'{rel(skill_file)}: frontmatter missing "description"',
                        )
                    elif len(desc) < 20:
                        add_warning(
                            "SKILL_DESCRIPTION_SHORT",
                            skill_file,
                            f"{rel(skill_file)}: description is very short — Claude decides whether "
                            f"to load this skill based only on this text, so vague descriptions "
                            f"won't trigger reliably",
                        )

        # ---- 4. Commands: frontmatter description ----
        commands_dir = plugin_dir / "commands"
        if commands_dir.exists():
            for cmd_file in commands_dir.glob("*.md"):
                content = cmd_file.read_text(encoding="utf-8")
                fm = parse_frontmatter(content)
                if not fm or not fm.get("description"):
                    add_warning(
                        "COMMAND_MISSING_DESCRIPTION",
                        cmd_file,
                        f'{rel(cmd_file)}: missing "description" in frontmatter',
                    )

        # ---- 5. MCP config, if present, must be valid JSON ----
        mcp_path = plugin_dir / ".mcp.json"
        if mcp_path.exists():
            read_json(mcp_path, rel(mcp_path), "MCP")


# ---- 6. Regenerate docs/CATALOG.md ----

def generate_catalog():
    if not marketplace:
        return
    lines = [
        "<!-- GENERATED FILE — do not hand-edit. Run "
        "`python3 plugins/plugin-development/scripts/validate.py` to regenerate. -->",
        "",
        f'# {marketplace.get("name", "Marketplace")} Catalog',
        "",
        marketplace.get("metadata", {}).get("description", ""),
        "",
        "| Plugin | Category | Tags | Owner | Description |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in plugin_entries:
        if not isinstance(entry, dict) or not entry:
            continue
        lines.append(
            f'| `{entry.get("name", "?")}` | {entry.get("category", "-")} | '
            f'{", ".join(entry.get("tags", [])) or "-"} | {entry.get("owner", "-")} | '
            f'{entry.get("description", "-")} |'
        )
    lines.append("")
    catalog_path = ROOT / "docs" / "CATALOG.md"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text("\n".join(lines), encoding="utf-8")
    if not JSON_MODE:
        print(f"Regenerated {rel(catalog_path)}")


if not errors:
    generate_catalog()

# ---- Report ----

if JSON_MODE:
    print(json.dumps({"errors": errors, "warnings": warnings, "ok": len(errors) == 0}, indent=2))
else:
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - [{w['code']}] {w['message']}")
    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"  - [{e['code']}] {e['message']}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s). Fix errors before committing.")
    else:
        print(f"\nAll checks passed ({len(warnings)} warning(s)).")

sys.exit(1 if errors else 0)