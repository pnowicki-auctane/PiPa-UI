"""Filesystem-based PiPa skill loader.

Scans the pipa_skills/ directory for SKILL.md files with `runtime: pipa`
in their YAML frontmatter. Returns structured skill objects for use by
the PiPa local skill runtime.

Skills are NOT loaded from a Python dict — they live as Markdown files
at pipa_skills/<category>/<skill-id>/SKILL.md so they can be version-
controlled, edited, and extended without touching Python code.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# pipa_skills/ sits at the repo root, one level above this file.
_PIPA_SKILLS_DIR = Path(__file__).parent.parent / "pipa_skills"


def _parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Parse YAML-like frontmatter from a Markdown file.

    Returns (metadata_dict, body_text). Supports simple key: value pairs
    and does not require PyYAML — the values we care about are all scalars.
    """
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?", text, re.DOTALL)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    meta: dict[str, Any] = {}
    for line in raw.splitlines():
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        # Strip surrounding quotes if present
        if len(val) >= 2 and val[0] in ('"', "'") and val[-1] == val[0]:
            val = val[1:-1]
        # Coerce integer strings
        if re.fullmatch(r"\d+", val):
            meta[key] = int(val)
        else:
            meta[key] = val
    return meta, body


def iter_pipa_skills() -> list[dict[str, Any]]:
    """Walk pipa_skills/, return all skills with runtime: pipa."""
    results: list[dict[str, Any]] = []
    if not _PIPA_SKILLS_DIR.exists():
        return results
    for skill_md in sorted(_PIPA_SKILLS_DIR.rglob("SKILL.md")):
        try:
            content = skill_md.read_text(encoding="utf-8")
            meta, body = _parse_frontmatter(content)
            if str(meta.get("runtime", "")).lower() != "pipa":
                continue
            skill_id = str(meta.get("id") or skill_md.parent.name)
            results.append({
                "id": skill_id,
                "name": str(meta.get("name") or skill_id),
                "description": str(meta.get("description") or ""),
                "category": str(meta.get("category") or "general"),
                "runtime": "pipa",
                "version": meta.get("version", 1),
                "path": str(skill_md),
                "body": body.strip(),
            })
        except Exception:
            continue
    return results


def get_pipa_skill(skill_id: str) -> dict[str, Any] | None:
    """Return a single skill dict by id, or None if not found."""
    for skill in iter_pipa_skills():
        if skill["id"] == skill_id:
            return skill
    return None
