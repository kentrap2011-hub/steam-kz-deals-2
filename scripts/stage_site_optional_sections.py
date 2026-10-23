#!/usr/bin/env python3
"""Stage optional Pages sections independently without changing signed paid JSON.

A missing or invalid task/status/giveaway section is omitted only in scopes where
its own canonical contract permits it. Global canonical byte integrity remains
fail-closed. A giveaway-only or status-only publication MUST accept its own section.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK_LINK = re.compile(r'(?m)^[ \t]*<a class="statistics-entry tasks-entry" href="tasks\.html">[^<]*</a>[ \t]*\n?')
GIVEAWAY_SCRIPT = "<script>window.SITE_GIVEAWAY_ENABLED=false;</script>"
APP_SCRIPT = '<script src="app.js?v=deep-history-site-01"></script>'


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def invoke(root: Path, *args: str) -> tuple[bool, str]:
    try:
        proc = subprocess.run(args, cwd=root, text=True, capture_output=True, timeout=90, check=False)
        return proc.returncode == 0, (proc.stdout + "\n" + proc.stderr).strip()[-1200:]
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, type(exc).__name__ + ": " + str(exc)


def check_core(root: Path) -> tuple[str, str]:
    canonical = root / "data/production/visual/current.json"
    staged = root / "web/data/current.json"
    if not canonical.is_file() or not staged.is_file() or not canonical.read_bytes():
        raise ValueError("Missing canonical or staged paid visual")
    if canonical.read_bytes() != staged.read_bytes():
        raise ValueError("Staged paid bytes differ from canonical visual")
    payload = json.loads(canonical.read_text(encoding="utf-8"))
    contract = payload.get("production_contract")
    if not isinstance(contract, dict) or contract.get("mode") != "daily_precomputed_read_only_for_ui":
        raise ValueError("Invalid core production contract")
    if contract.get("heavy_calculation_allowed_in_ui") is not False or contract.get("external_lookup_allowed_in_ui") is not False:
        raise ValueError("Client-side source/commercial recalculation forbidden")
    if not isinstance(payload.get("items"), list):
        raise ValueError("Missing canonical paid items list")
    if type(payload.get("schema_version")) is not int or payload["schema_version"] < 1:
        raise ValueError("Invalid canonical visual schema version")
    seen = set()
    for index, item in enumerate(payload["items"]):
        if not isinstance(item, dict):
            raise ValueError(f"Invalid canonical paid item at index {index}")
        identity = item.get("id")
        if not isinstance(identity, (str, int)) or isinstance(identity, bool) or not str(identity).strip():
            raise ValueError(f"Missing canonical paid identity at index {index}")
        identity = str(identity)
        if identity in seen:
            raise ValueError(f"Duplicate canonical paid identity: {identity}")
        seen.add(identity)
        for field, minimum, maximum in (("current_price_rub", 0, None), ("discount_percent", 0, 100)):
            value = item.get(field)
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"Invalid canonical paid {field} for {identity}")
            import math
            if not math.isfinite(value) or value < minimum or (maximum is not None and value > maximum):
                raise ValueError(f"Out-of-range canonical paid {field} for {identity}")
    # Staging may not modify ANY field in canonical paid/giveaway JSON; Git blob
    # identity and freshness receipt are verified against this exact file.
    ok, blob = invoke(root, "git", "rev-parse", "HEAD:data/production/visual/current.json")
    if not ok:
        raise ValueError("Cannot prove current canonical visual Git blob: " + blob)
    ok, staged_blob = invoke(root, "git", "hash-object", str(staged.relative_to(root)))
    if not ok or staged_blob != blob:
        raise ValueError("Canonical Git material SHA does not match exact staged bytes")
    return blob, sha256(staged)


def remove_tasks(root: Path) -> None:
    index = root / "web/index.html"
    html = index.read_text(encoding="utf-8")
    result, n = TASK_LINK.subn("", html)
    if n != 1 or 'href="tasks.html"' in result:
        raise ValueError("Cannot omit task section safely: task navigation is not unambiguous")
    index.write_text(result, encoding="utf-8")
    for name in ("tasks.html", "tasks.js", "tasks.css"):
        (root / "web" / name).unlink(missing_ok=True)
    (root / "web/data/tasks.json").unlink(missing_ok=True)


def omit_giveaway(root: Path) -> None:
    index = root / "web/index.html"
    html = index.read_text(encoding="utf-8")
    if html.count(APP_SCRIPT) != 1 or GIVEAWAY_SCRIPT in html:
        raise ValueError("Cannot isolate giveaway presentation with an exact app script binding")
    index.write_text(html.replace(APP_SCRIPT, GIVEAWAY_SCRIPT + "\n  " + APP_SCRIPT), encoding="utf-8")


def stage(root: Path, scope: str) -> dict:
    if scope not in {"general", "commercial_only", "giveaway_only", "status_only"}:
        raise ValueError("Invalid deploy scope")
    blob, paid_sha = check_core(root)
    staged_dir = root / "web/data"
    manifest = {
        "schema_version": 1,
        "contract": "SITE-PAGES-SECTION-DISPOSITION-V1",
        "scope": scope,
        "source_visual_git_blob_sha": blob,
        "source_visual_sha256": sha256(root / "data/production/visual/current.json"),
        "staged_visual_sha256": paid_sha,
        "published_visual_sha256": None,
        "published_verification": "unverified_until_live_pages_readback",
        "sections": {},
    }
    status_path = root / "data/production/site/current_status.json"
    staged_status = staged_dir / "status.json"
    staged_status.unlink(missing_ok=True)
    if status_path.is_file() and status_path.stat().st_size:
        valid, reason = invoke(root, "python", "scripts/build_site_status.py", "--validate-current", str(status_path.relative_to(root)))
    else:
        valid, reason = False, "missing_current_site_status"
    if valid:
        staged_status.write_bytes(status_path.read_bytes())
        manifest["sections"]["status"] = {"disposition": "fresh", "sha256": sha256(staged_status)}
    elif scope == "status_only":
        raise ValueError("Status-only publication requires exact canonical validated status: " + reason)
    else:
        manifest["sections"]["status"] = {"disposition": "omitted", "reason": "independent_status_validation_failed", "detail": reason[:300]}

    task_output = staged_dir / "tasks.json"
    task_output.unlink(missing_ok=True)
    generated, reason = invoke(root, "python", "scripts/build_site_tasks.py", "--output", str(task_output.relative_to(root)))
    validated, check_reason = (invoke(root, "python", "scripts/build_site_tasks.py", "--validate-current", str(task_output.relative_to(root))) if generated else (False, "generation_failed"))
    if generated and validated and task_output.is_file() and task_output.stat().st_size:
        manifest["sections"]["tasks"] = {"disposition": "fresh", "sha256": sha256(task_output)}
    else:
        remove_tasks(root)
        manifest["sections"]["tasks"] = {"disposition": "omitted", "reason": "independent_task_generation_or_validation_failed", "detail": (reason + " " + check_reason)[-300:]}

    if scope == "status_only":
        manifest["sections"]["giveaways"] = {"disposition": "unchanged", "reason": "status_only"}
    else:
        giveaway_ok, reason = invoke(root, "python", "scripts/validate_giveaway_visual_payload.py", "data/production/visual/current.json")
        if giveaway_ok:
            manifest["sections"]["giveaways"] = {"disposition": "fresh", "source": "exact_canonical_visual"}
        elif scope == "giveaway_only":
            raise ValueError("Giveaway-only publication requires valid giveaway section: " + reason)
        else:
            # Source/receipt/global provenance checks are NEVER waived.
            # Omission is browser presentation only; raw canonical bytes remain exact.
            omit_giveaway(root)
            manifest["sections"]["giveaways"] = {"disposition": "omitted", "reason": "independent_giveaway_presentation_invalid", "detail": reason[-300:]}
    staged_dir.mkdir(parents=True, exist_ok=True)
    (staged_dir / "publication-disposition.json").write_text(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scope", choices=("general", "commercial_only", "giveaway_only", "status_only"), required=True)
    args = parser.parse_args()
    result = stage(ROOT, args.scope)
    print("SITE_PUBLICATION_OPTIONAL_SECTIONS=" + json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
