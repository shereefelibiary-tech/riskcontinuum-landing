#!/usr/bin/env python3
"""Export documentation from a pinned engine checkout, without importing the app.

Usage: python scripts/refresh-methods-data.py /path/to/engine/source
Only the canonical RSS constants/dataclass and its pure documentation helpers
are evaluated. This script does not assess patients or alter clinical rules.
"""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
ENGINE_REVISION = "18baf7a8651b10cb4f047072590a5c8699e293c5"
SOURCE_FILES = (
    "modules/levels/level_classifier.py", "modules/levels/definitions.py",
    "modules/levels/descriptors.py", "modules/rss/engine.py",
    "core/kidney_categories.py", "core/hypertension.py", "core/version.py",
    "modules/lipids/severe_hypercholesterolemia.py",
    "modules/prevent/eligibility.py", "modules/prevent/precision.py",
    "modules/prevent/treatment_effects.py", "api/simulate.py",
)


def export(source: Path) -> dict:
    scope: dict[str, Any] = {"dataclass": dataclass, "Any": Any, "Optional": Optional}
    kidney = ast.parse((source / "core/kidney_categories.py").read_text())
    for node in kidney.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    scope[target.id] = node.value.value
    rss = ast.parse((source / "modules/rss/engine.py").read_text())
    allowed = []
    for node in rss.body:
        if isinstance(node, ast.ClassDef) and node.name == "RssScoringBand":
            allowed.append(node)
        elif isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith("RSS_") for t in node.targets):
            allowed.append(node)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id.startswith("RSS_"):
            allowed.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in {"_methodology_band_rows", "get_rss_scoring_methodology"}:
            allowed.append(node)
    # Future annotations avoid evaluating unrelated application type names.
    selected = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *allowed], type_ignores=[])
    exec(compile(ast.fix_missing_locations(selected), "rss_documentation_export", "exec"), scope)
    method = scope["get_rss_scoring_methodology"]()
    bands = {}
    for key, value in scope.items():
        if key.startswith("RSS_") and isinstance(value, tuple):
            bands[key] = [dict(label=b.label, points=b.points, min_value=b.min_value, max_value=b.max_value, include_min=b.include_min, include_max=b.include_max) for b in value]
    level_source = (source / "modules/levels/level_classifier.py").read_text()
    rule_ids = list(dict.fromkeys(re.findall(r'"(LEVEL_(?:[1-5][A-C]?|INCOMPLETE)_[A-Z0-9_]+)"', level_source)))
    return {
        "document_version": "1.1-draft", "reviewed_on": "2026-11-04",
        "engine_revision": ENGINE_REVISION,
        "source_sha256": {name: hashlib.sha256((source / name).read_bytes()).hexdigest() for name in SOURCE_FILES},
        "rss": method, "rss_exact_numeric_intervals": bands,
        "level_rule_ids": rule_ids,
        "interpretation": "RCCKM-specific rules and weights are prespecified design choices. Published source evidence does not independently validate this synthesis.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("engine_source", type=Path)
    args = parser.parse_args()
    data = export(args.engine_source)
    destination = ROOT / "downloads/rcckm-methods-data-v1.json"
    head = subprocess.run(["git", "-C", str(args.engine_source), "rev-parse", "HEAD"], capture_output=True, text=True)
    if head.returncode == 0:
        if head.stdout.strip() != ENGINE_REVISION:
            raise ValueError("Engine HEAD differs from the documented revision; review and version the methods before updating the reference.")
        dirty = subprocess.run(["git", "-C", str(args.engine_source), "diff", "--quiet", "HEAD", "--", *SOURCE_FILES])
        if dirty.returncode != 0:
            raise ValueError("Reviewed engine files have uncommitted changes.")
    elif destination.is_file():
        previous = json.loads(destination.read_text())
        if previous.get("engine_revision") != ENGINE_REVISION or previous.get("source_sha256") != data["source_sha256"]:
            raise ValueError("Reference files differ from the retained fingerprints; use a clean checkout at the documented revision.")
    else:
        raise ValueError("First export requires a clean git checkout at the documented revision.")
    # Review proposals are document metadata, not part of the released engine's
    # canonical RSS/Level export. Preserve their explicit unreleased status.
    if destination.is_file():
        previous = json.loads(destination.read_text())
        if previous.get("pending_changes"):
            data["pending_changes"] = previous["pending_changes"]
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    blocks = []
    for domain in data["rss"]["domains"]:
        rows = "".join(f'<tr><th scope="row">{escape(str(row["signal"]))}</th><td class="points">{escape(str(row["points"]))}</td><td>{escape(row["rationale"])}</td></tr>' for row in domain["rows"])
        blocks.append(f'<h4>{escape(domain["domain"])}</h4><div class="table-scroll" tabindex="0" role="region" aria-label="{escape(domain["domain"])} scoring"><table class="rss-table"><caption>{escape(domain["domain"])}: prespecified RSS weights</caption><thead><tr><th scope="col">Finding</th><th scope="col">Points</th><th scope="col">Scoring note</th></tr></thead><tbody>{rows}</tbody></table></div>')
    page = ROOT / "methods.html"
    content = page.read_text()
    content, count = re.subn(r"<!-- RSS-TABLES:START -->.*?<!-- RSS-TABLES:END -->", lambda _: "<!-- RSS-TABLES:START -->\n" + "\n".join(blocks) + "\n<!-- RSS-TABLES:END -->", content, flags=re.S)
    if count != 1:
        raise ValueError("Expected one canonical RSS table location")
    page.write_text(content)
    print(f"Exported {len(data['rss']['domains'])} RSS domains and {len(data['level_rule_ids'])} Level rule IDs from {ENGINE_REVISION[:7]}.")


if __name__ == "__main__":
    main()
