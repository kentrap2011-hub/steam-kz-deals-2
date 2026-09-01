#!/usr/bin/env python3
"""Fail-closed validation for deletions from BACKLOG.md.

A deleted task is identified by its exact level-3 heading under
"## Отложенные задачи". The same git change must add exactly one durable
``backlog-disposition`` marker outside BACKLOG.md.

Marker format:
    <!-- backlog-disposition: {"task":"Exact heading","type":"active",...} -->

Accepted types:
- active: marker lives in the exact WORKER_TASK*.md and names its report path;
- completed: marker lives in a durable evidence file whose report status is complete;
- cancelled/superseded: marker lives in canonical state/decision evidence and says why.

Tasks whose old backlog section contains ``needs_user_verification`` are special:
implementation alone can never satisfy ``completed``. Completion requires explicit
``acceptance=user_verified`` plus a non-empty acceptance_evidence field; an active
transfer must preserve the same verification token in the destination task file.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Callable, Iterable, Mapping, Sequence

BACKLOG_PATH = "BACKLOG.md"
DEFERRED_SECTION = "Отложенные задачи"
MARKER_RE = re.compile(r"<!--\s*backlog-disposition:\s*(\{.*\})\s*-->\s*$")
STATUS_COMPLETE_RE = re.compile(r"(?im)^###\s+Status\s*$\s*^\s*`?complete`?\s*$")
CANONICAL_DECISION_PATHS = {
    "CURRENT_TASK.md",
    "DIRECTOR_TASK_BOARD.md",
    "PROJECT_DECISIONS.md",
}


class ValidationError(RuntimeError):
    pass


@dataclass(frozen=True)
class BacklogTask:
    title: str
    body: str

    @property
    def needs_user_verification(self) -> bool:
        return "needs_user_verification" in self.body.casefold()


@dataclass(frozen=True)
class DispositionMarker:
    source_path: str
    payload: Mapping[str, object]

    @property
    def task(self) -> str:
        value = self.payload.get("task")
        return value if isinstance(value, str) else ""


def _normalize_repo_path(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field} must be a non-empty repository-relative path")
    candidate = value.strip().replace("\\", "/")
    path = PurePosixPath(candidate)
    if path.is_absolute() or ".." in path.parts or candidate.startswith("./"):
        raise ValidationError(f"{field} must be a normalized repository-relative path: {candidate!r}")
    return candidate


def extract_backlog_tasks(text: str) -> dict[str, BacklogTask]:
    lines = text.splitlines()
    in_deferred = False
    tasks: dict[str, BacklogTask] = {}
    current_title: str | None = None
    current_body: list[str] = []

    def flush() -> None:
        nonlocal current_title, current_body
        if current_title is None:
            return
        if current_title in tasks:
            raise ValidationError(f"duplicate backlog task heading: {current_title!r}")
        tasks[current_title] = BacklogTask(current_title, "\n".join(current_body))
        current_title = None
        current_body = []

    for line in lines:
        if line.startswith("## ") and not line.startswith("### "):
            flush()
            section = line[3:].strip()
            in_deferred = section == DEFERRED_SECTION
            continue
        if not in_deferred:
            continue
        if line.startswith("### "):
            flush()
            current_title = line[4:].strip()
            if not current_title:
                raise ValidationError("empty level-3 task heading in backlog")
            continue
        if current_title is not None:
            current_body.append(line)
    flush()
    return tasks


def parse_marker_line(line: str, source_path: str) -> DispositionMarker | None:
    match = MARKER_RE.search(line.strip())
    if not match:
        return None
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid backlog-disposition JSON in {source_path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValidationError(f"backlog-disposition in {source_path} must be a JSON object")
    return DispositionMarker(source_path=source_path, payload=payload)


def _require_nonempty_text(payload: Mapping[str, object], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"disposition field {field!r} must be non-empty")
    return value.strip()


def _validate_active(
    task: BacklogTask,
    marker: DispositionMarker,
    changed_paths: set[str],
    read_head_file: Callable[[str], str],
) -> None:
    payload = marker.payload
    task_file = _normalize_repo_path(payload.get("task_file"), "task_file")
    report = _normalize_repo_path(payload.get("report"), "report")
    if not (PurePosixPath(task_file).name.startswith("WORKER_TASK") and task_file.endswith(".md")):
        raise ValidationError("active disposition task_file must be an exact WORKER_TASK*.md path")
    if not (report.startswith("reviews/worker_reports/") and report.endswith(".md")):
        raise ValidationError("active disposition report must be an expected reviews/worker_reports/*.md path")
    if marker.source_path != task_file:
        raise ValidationError("active disposition marker must live in the exact task_file it names")
    if task_file not in changed_paths:
        raise ValidationError("active disposition task_file must be changed in the same operational change")
    content = read_head_file(task_file)
    if report not in content:
        raise ValidationError("active task_file does not contain its exact expected report path")
    if "Task ID:" not in content:
        raise ValidationError("active task_file does not expose a Task ID")
    if task.needs_user_verification:
        verification = payload.get("verification")
        if verification not in {"pending", "preserved"}:
            raise ValidationError(
                "needs_user_verification task can transfer only with verification=pending or preserved"
            )
        if "needs_user_verification" not in content.casefold():
            raise ValidationError(
                "destination task_file must explicitly preserve needs_user_verification"
            )


def _validate_completed(
    task: BacklogTask,
    marker: DispositionMarker,
    changed_paths: set[str],
    read_head_file: Callable[[str], str],
) -> None:
    payload = marker.payload
    evidence = _normalize_repo_path(payload.get("evidence"), "evidence")
    if marker.source_path != evidence:
        raise ValidationError("completed disposition marker must live in the exact evidence file it names")
    if evidence not in changed_paths:
        raise ValidationError("completion evidence must be changed in the same operational change")
    content = read_head_file(evidence)
    if not STATUS_COMPLETE_RE.search(content):
        raise ValidationError("completion evidence must contain a `### Status` section with `complete`")
    if task.needs_user_verification:
        if payload.get("acceptance") != "user_verified":
            raise ValidationError(
                "needs_user_verification task cannot complete from implementation-only evidence"
            )
        _require_nonempty_text(payload, "acceptance_evidence")


def _validate_cancelled_or_superseded(
    marker: DispositionMarker,
    changed_paths: set[str],
    read_head_file: Callable[[str], str],
) -> None:
    payload = marker.payload
    reason = _require_nonempty_text(payload, "reason")
    _ = reason
    decision = _normalize_repo_path(payload.get("decision"), "decision")
    if marker.source_path != decision:
        raise ValidationError("cancelled/superseded marker must live in the exact decision file it names")
    if decision not in changed_paths:
        raise ValidationError("decision evidence must be changed in the same operational change")
    if decision not in CANONICAL_DECISION_PATHS and not decision.startswith("reviews/worker_reports/"):
        raise ValidationError(
            "decision evidence must be canonical state/decision data or a durable worker report"
        )
    content = read_head_file(decision)
    task_title = _require_nonempty_text(payload, "task")
    if task_title not in content:
        raise ValidationError("decision evidence must mention the exact deleted backlog task heading")
    disposition_type = payload.get("type")
    if disposition_type == "cancelled":
        by = payload.get("by")
        if by not in {"user", "canonical_decision"}:
            raise ValidationError("cancelled disposition requires by=user or canonical_decision")
    else:
        _require_nonempty_text(payload, "replacement")


def validate_transition(
    before_backlog: str,
    after_backlog: str,
    markers: Sequence[DispositionMarker],
    changed_paths: Iterable[str],
    read_head_file: Callable[[str], str],
) -> list[str]:
    before = extract_backlog_tasks(before_backlog)
    after = extract_backlog_tasks(after_backlog)
    deleted = sorted(set(before) - set(after))
    if not deleted:
        return []

    changed = set(changed_paths)
    errors: list[str] = []
    for title in deleted:
        task = before[title]
        matches = [marker for marker in markers if marker.task == title]
        if len(matches) != 1:
            errors.append(
                f"{title}: deleted backlog task requires exactly one added durable disposition marker; "
                f"found {len(matches)}"
            )
            continue
        marker = matches[0]
        disposition_type = marker.payload.get("type")
        try:
            if marker.source_path == BACKLOG_PATH:
                raise ValidationError("disposition marker cannot live in BACKLOG.md")
            if disposition_type == "active":
                _validate_active(task, marker, changed, read_head_file)
            elif disposition_type == "completed":
                _validate_completed(task, marker, changed, read_head_file)
            elif disposition_type in {"cancelled", "superseded"}:
                _validate_cancelled_or_superseded(marker, changed, read_head_file)
            else:
                raise ValidationError(
                    "type must be one of active, completed, cancelled, superseded"
                )
        except (ValidationError, FileNotFoundError) as exc:
            errors.append(f"{title}: {exc}")
    return errors


def _git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args],
        check=False,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise ValidationError(f"git {' '.join(args)} failed: {detail}")
    return proc.stdout


def _git_show(ref: str, path: str) -> str:
    return _git("show", f"{ref}:{path}")


def _changed_paths(base: str, head: str) -> set[str]:
    return {line for line in _git("diff", "--name-only", base, head).splitlines() if line}


def _added_markers(base: str, head: str) -> list[DispositionMarker]:
    diff = _git("diff", "--unified=0", "--no-ext-diff", base, head, "--", ".")
    path: str | None = None
    markers: list[DispositionMarker] = []
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            candidate = line[6:]
            path = candidate if candidate.endswith(".md") and candidate != BACKLOG_PATH else None
            continue
        if not (path and line.startswith("+") and not line.startswith("+++")):
            continue
        marker = parse_marker_line(line[1:], path)
        if marker:
            markers.append(marker)
    return markers


def validate_git_change(base: str, head: str) -> list[str]:
    before_backlog = _git_show(base, BACKLOG_PATH)
    after_backlog = _git_show(head, BACKLOG_PATH)
    changed = _changed_paths(base, head)
    markers = _added_markers(base, head)
    return validate_transition(
        before_backlog,
        after_backlog,
        markers,
        changed,
        lambda path: _git_show(head, path),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail closed when BACKLOG.md tasks disappear without a durable same-change disposition."
    )
    parser.add_argument("--base", required=True, help="base commit SHA/ref")
    parser.add_argument("--head", required=True, help="head commit SHA/ref")
    args = parser.parse_args()
    try:
        errors = validate_git_change(args.base, args.head)
    except ValidationError as exc:
        raise SystemExit(f"Backlog disposition validation failed: {exc}") from exc
    if errors:
        details = "\n".join(f"- {error}" for error in errors)
        raise SystemExit(
            "Backlog disposition validation failed:\n"
            f"{details}\n"
            "Add exactly one `<!-- backlog-disposition: {...} -->` marker to the durable "
            "destination/evidence file in the same change."
        )
    print("Backlog disposition validation passed")


if __name__ == "__main__":
    main()
