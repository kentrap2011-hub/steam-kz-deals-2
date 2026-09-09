#!/usr/bin/env python3
"""Read-only one-AppID Taste preparation proof from current main.

This harness creates a one-family sandbox under an output directory outside the
repository checkout, freezes the canonical live Taste profile to an immutable
Git commit/blob/content snapshot, then invokes the existing production Taste
projection and ChatGPT-payload builders against that sandbox. It never executes
semantics or canonical ingest and never writes generated state back into the
checkout.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Iterable


class CanaryError(RuntimeError):
    pass


CANONICAL_GENERATED_PATHS = {
    "family_graph": Path("data/production/pre_ai/family_graph.json"),
    "content_metadata": Path("data/production/pre_ai/content_metadata.json"),
    "store": Path("data/production/pre_ai/store_snapshot.json"),
    "fx": Path("data/production/pre_ai/fx_snapshot.json"),
    "history": Path("data/production/pre_ai/history_snapshot.json"),
    "deals": Path("data/production/pre_ai/deal_scenarios.json"),
    "fixed_packages": Path("data/production/pre_ai/fixed_package_options.json"),
    "taste_projection": Path("data/production/pre_ai/taste_projection.json"),
    "chatgpt_payload": Path("data/production/pre_ai/chatgpt_payload.json"),
    "purchase_context": Path("data/production/pre_ai/chatgpt_purchase_context.jsonl"),
    "mailing_index": Path("data/production/mailing/index.json"),
}

TASTE_CACHE_PATHS = (
    Path("data/cache/taste_fit.json"),
    Path("data/cache/taste_fit.entry_overlay.json"),
    Path("data/cache/taste_fit.entry_index.json"),
    Path("data/cache/taste_fit.ledger_validation.json"),
    Path("data/cache/taste_ingest_receipts/latest_runtime_status.json"),
)

SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PROFILE_FREEZE_MAX_ATTEMPTS = 3
CANONICAL_PROFILE_REPOSITORY = "kentrap2011-hub/stopgame-ratings-data"
CANONICAL_PROFILE_PATH = "gaming_taste_live.json"


def parse_appid(value: Any) -> str:
    text = str(value).strip()
    if not text or not text.isdigit():
        raise CanaryError("appid must be exactly one positive numeric AppID")
    normalized = str(int(text))
    if normalized == "0":
        raise CanaryError("appid must be a positive numeric AppID")
    return normalized


def _load_json(path: Path) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CanaryError(f"required input missing: {path}") from exc
    except json.JSONDecodeError as exc:
        raise CanaryError(f"invalid JSON input: {path}: {exc}") from exc
    if not isinstance(doc, dict):
        raise CanaryError(f"expected JSON object: {path}")
    return doc


def _write_json(path: Path, doc: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise CanaryError(
            f"git {' '.join(args)} failed ({proc.returncode}): {proc.stderr.strip()}"
        )
    return proc.stdout.strip()


def git_status(repo: Path) -> str:
    return _git(repo, "status", "--porcelain=v1", "--untracked-files=all")


def establish_current_main(repo: Path) -> dict[str, str]:
    head = _git(repo, "rev-parse", "HEAD")
    origin_main = _git(repo, "rev-parse", "refs/remotes/origin/main")
    if not SHA1_RE.fullmatch(head) or not SHA1_RE.fullmatch(origin_main):
        raise CanaryError("cannot establish unambiguous git provenance")
    if head != origin_main:
        raise CanaryError(f"checkout is not current origin/main: HEAD={head} origin/main={origin_main}")
    status = git_status(repo)
    if status:
        raise CanaryError(f"repository must be clean before canary preparation:\n{status}")
    return {"checked_out_head_sha": head, "resolved_origin_main_sha": origin_main}


def ensure_output_isolated(repo: Path, output_dir: Path) -> None:
    repo = repo.resolve()
    output_dir = output_dir.resolve()
    if output_dir == repo or repo in output_dir.parents:
        raise CanaryError("output-dir must be outside the repository checkout")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise CanaryError("output-dir must be empty for an auditable canary run")


def _repo_blob_sha(repo: Path, relpath: Path) -> str:
    value = _git(repo, "hash-object", str(relpath))
    if not SHA1_RE.fullmatch(value):
        raise CanaryError(f"invalid git blob hash for {relpath}: {value!r}")
    return value


def _source_record(repo: Path, relpath: Path) -> dict[str, Any]:
    path = repo / relpath
    if not path.is_file():
        raise CanaryError(f"required committed input missing: {relpath}")
    return {
        "path": relpath.as_posix(),
        "git_blob_sha": _repo_blob_sha(repo, relpath),
        "bytes": path.stat().st_size,
    }


def _git_blob_sha_bytes(raw: bytes) -> str:
    return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()


def _github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "steam-kz-deals-current-main-canary/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _fetch_github_json(url: str) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers=_github_headers())
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
    except Exception as exc:
        raise CanaryError(f"canonical live profile fetch failed: {type(exc).__name__}: {exc}") from exc
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanaryError(f"canonical live profile API returned malformed JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise CanaryError("canonical live profile API response must be a JSON object")
    return doc


def _decode_github_contents_file(doc: dict[str, Any]) -> tuple[bytes, str]:
    if doc.get("type") != "file":
        raise CanaryError("canonical live profile contents response is not a file")
    blob_sha = str(doc.get("sha") or "")
    if not SHA1_RE.fullmatch(blob_sha):
        raise CanaryError("canonical live profile blob SHA is missing or malformed")
    if doc.get("encoding") != "base64" or not isinstance(doc.get("content"), str):
        raise CanaryError("canonical live profile contents response has no unambiguous base64 content")
    encoded = "".join(doc["content"].split())
    try:
        raw = base64.b64decode(encoded, validate=True)
    except Exception as exc:
        raise CanaryError(f"canonical live profile base64 is malformed: {exc}") from exc
    if _git_blob_sha_bytes(raw) != blob_sha:
        raise CanaryError("canonical live profile content does not match advertised Git blob SHA")
    try:
        profile_doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanaryError(f"canonical live profile content is malformed JSON: {exc}") from exc
    if not isinstance(profile_doc, dict):
        raise CanaryError("canonical live profile JSON must be an object")
    return raw, blob_sha


def freeze_current_live_profile(
    policy: dict[str, Any],
    output_dir: Path,
    fetch_json: Callable[[str], dict[str, Any]] = _fetch_github_json,
    max_attempts: int = PROFILE_FREEZE_MAX_ATTEMPTS,
) -> dict[str, Any]:
    cfg = policy.get("taste_profile") or {}
    repository = str(cfg.get("canonical_repository") or "")
    profile_path = str(cfg.get("canonical_path") or "")
    if repository != CANONICAL_PROFILE_REPOSITORY or profile_path != CANONICAL_PROFILE_PATH:
        raise CanaryError("canonical live profile authority does not match the approved Taste policy")
    if cfg.get("load_once_per_run") is not True or cfg.get("record_git_blob_sha") is not True:
        raise CanaryError("canonical Taste policy does not permit immutable load-once profile binding")
    if int(max_attempts) < 1:
        raise CanaryError("profile freeze attempts must be bounded and positive")

    api_root = f"https://api.github.com/repos/{repository}"
    branch = "main"
    encoded_path = urllib.parse.quote(profile_path, safe="/")
    head_url = f"{api_root}/commits/{branch}"
    drift: list[dict[str, str]] = []

    for attempt in range(1, int(max_attempts) + 1):
        before = str(fetch_json(head_url).get("sha") or "")
        if not SHA1_RE.fullmatch(before):
            raise CanaryError("canonical live profile main commit SHA is missing or malformed")
        contents_url = f"{api_root}/contents/{encoded_path}?ref={before}"
        raw, blob_sha = _decode_github_contents_file(fetch_json(contents_url))
        after = str(fetch_json(head_url).get("sha") or "")
        if not SHA1_RE.fullmatch(after):
            raise CanaryError("canonical live profile confirmation commit SHA is missing or malformed")
        if after != before:
            drift.append({"attempt": str(attempt), "before": before, "after": after})
            continue

        content_sha256 = hashlib.sha256(raw).hexdigest()
        immutable_raw_url = f"https://raw.githubusercontent.com/{repository}/{before}/{profile_path}"
        binding = {
            "schema_version": 1,
            "authority": "canonical_live_profile",
            "repository": repository,
            "path": profile_path,
            "branch": branch,
            "resolved_commit_sha": before,
            "blob_sha": blob_sha,
            "content_sha256": content_sha256,
            "bytes": len(raw),
            "immutable_raw_url": immutable_raw_url,
            "freeze_method": "github_contents_api_commit_pinned_with_bounded_head_confirmation",
            "head_confirmation_attempt": attempt,
            "head_drift_before_freeze": drift,
            "max_freeze_attempts": int(max_attempts),
        }
        frozen_dir = output_dir / "frozen_profile"
        frozen_dir.mkdir(parents=True, exist_ok=True)
        snapshot_path = frozen_dir / "gaming_taste_live.json"
        snapshot_path.write_bytes(raw)
        _write_json(frozen_dir / "profile_binding.json", binding)
        validate_frozen_profile_binding(binding, snapshot_path)
        return {
            "profile": {
                "repository": repository,
                "path": profile_path,
                "raw_url": immutable_raw_url,
                "blob_sha": blob_sha,
                "bytes": len(raw),
                "commit_sha": before,
                "content_sha256": content_sha256,
            },
            "binding": binding,
            "snapshot_path": snapshot_path,
            "binding_path": frozen_dir / "profile_binding.json",
        }

    raise CanaryError(
        f"canonical live profile changed during all {int(max_attempts)} bounded freeze attempts; retry later"
    )


def validate_frozen_profile_binding(binding: dict[str, Any], snapshot_path: Path | None = None) -> None:
    if binding.get("authority") != "canonical_live_profile":
        raise CanaryError("frozen profile authority is missing or ambiguous")
    if binding.get("repository") != CANONICAL_PROFILE_REPOSITORY or binding.get("path") != CANONICAL_PROFILE_PATH:
        raise CanaryError("frozen profile identity does not match canonical authority")
    for field in ("resolved_commit_sha", "blob_sha"):
        if not SHA1_RE.fullmatch(str(binding.get(field) or "")):
            raise CanaryError(f"frozen profile {field} is missing or malformed")
    if not SHA256_RE.fullmatch(str(binding.get("content_sha256") or "")):
        raise CanaryError("frozen profile content_sha256 is missing or malformed")
    if not isinstance(binding.get("bytes"), int) or int(binding["bytes"]) <= 0:
        raise CanaryError("frozen profile byte count is missing or malformed")
    if snapshot_path is None:
        return
    try:
        raw = snapshot_path.read_bytes()
    except FileNotFoundError as exc:
        raise CanaryError("frozen profile snapshot is missing") from exc
    if len(raw) != binding["bytes"]:
        raise CanaryError("frozen profile snapshot byte count mismatch")
    if _git_blob_sha_bytes(raw) != binding["blob_sha"]:
        raise CanaryError("frozen profile snapshot Git blob mismatch")
    if hashlib.sha256(raw).hexdigest() != binding["content_sha256"]:
        raise CanaryError("frozen profile snapshot content SHA256 mismatch")
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CanaryError(f"frozen profile snapshot is malformed JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise CanaryError("frozen profile snapshot JSON must be an object")


def select_one_family(family_doc: dict[str, Any], appid: str) -> dict[str, Any]:
    key = f"App_{appid}"
    matches = [row for row in (family_doc.get("families") or []) if row.get("taste_subject_key") == key]
    if len(matches) != 1:
        raise CanaryError(f"requested AppID must resolve to exactly one Taste family; found {len(matches)}")
    family = copy.deepcopy(matches[0])
    if str(family.get("taste_subject_key")) != key:
        raise CanaryError("Taste subject key mismatch")
    return family


def _find_mailing_row(repo: Path, index: dict[str, Any], key: str) -> tuple[str, str]:
    columns = index.get("columns") or []
    if "key" not in columns:
        raise CanaryError("mailing index has no key column")
    key_index = columns.index("key")
    pattern = str(index.get("chunk_pattern") or "")
    count = int(index.get("chunk_count") or 0)
    if not pattern or count <= 0:
        raise CanaryError("mailing index chunk metadata is invalid")
    matches: list[tuple[str, str]] = []
    for n in range(1, count + 1):
        rel = Path(pattern.replace("NNN", f"{n:03d}"))
        path = repo / rel
        if not path.is_file():
            raise CanaryError(f"mailing chunk missing: {rel}")
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            cells = line.split("\t")
            if len(cells) != len(columns):
                raise CanaryError(f"mailing column mismatch in {rel}")
            if cells[key_index] == key:
                matches.append((line, rel.as_posix()))
    if len(matches) != 1:
        raise CanaryError(f"requested Taste key must occur exactly once in mailing feed; found {len(matches)}")
    return matches[0]


def _slice_entries(doc: dict[str, Any], key: str, label: str) -> dict[str, Any]:
    entries = doc.get("entries")
    if not isinstance(entries, dict) or key not in entries:
        raise CanaryError(f"{label} lacks required key {key}")
    sliced = copy.deepcopy(doc)
    sliced["entries"] = {key: copy.deepcopy(entries[key])}
    for field in ("entry_count", "item_count", "source_item_count", "classified_count"):
        if field in sliced:
            sliced[field] = 1
    return sliced


def _find_jsonl_rows(path: Path, field: str, value: str) -> list[dict[str, Any]]:
    if not path.is_file():
        raise CanaryError(f"required JSONL input missing: {path}")
    result: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if str(row.get(field) or "") == value:
            result.append(row)
    return result


def _committed_wishlist_binding(repo: Path, appid: str, taste_key: str, source_stamp: str) -> dict[str, Any]:
    manifest = _load_json(repo / CANONICAL_GENERATED_PATHS["chatgpt_payload"])
    if manifest.get("source_mailing_updated_at_utc") != source_stamp:
        raise CanaryError("committed ChatGPT payload is stale versus current mailing source")
    binding = manifest.get("wishlist_binding") or {}
    blob_sha = binding.get("blob_sha")
    entry_count = binding.get("entry_count")
    if not SHA1_RE.fullmatch(str(blob_sha or "")) or not isinstance(entry_count, int):
        raise CanaryError("committed wishlist binding is missing or malformed")
    rows = _find_jsonl_rows(repo / CANONICAL_GENERATED_PATHS["purchase_context"], "taste_subject_key", taste_key)
    if len(rows) != 1:
        raise CanaryError("target wishlist/context provenance is ambiguous or unavailable in committed purchase context")
    context_only = rows[0].get("context_only") or {}
    if not isinstance(context_only.get("wishlist"), bool):
        raise CanaryError("target committed wishlist flag is unavailable")
    return {
        "blob_sha": blob_sha,
        "entry_count": entry_count,
        "appids": {appid} if context_only["wishlist"] else set(),
        "target_wishlist": context_only["wishlist"],
        "provenance": "committed chatgpt_payload wishlist binding + target purchase_context flag",
    }


def _copy_if_exists(src: Path, dst: Path) -> None:
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def build_one_subject_workspace(repo: Path, output_dir: Path, appid: str) -> dict[str, Any]:
    taste_key = f"App_{appid}"
    workspace = output_dir / "workspace"
    workspace.mkdir(parents=True, exist_ok=False)
    shutil.copytree(repo / "config", workspace / "config")
    for rel in TASTE_CACHE_PATHS:
        _copy_if_exists(repo / rel, workspace / rel)

    family_doc = _load_json(repo / CANONICAL_GENERATED_PATHS["family_graph"])
    mailing = _load_json(repo / CANONICAL_GENERATED_PATHS["mailing_index"])
    content = _load_json(repo / CANONICAL_GENERATED_PATHS["content_metadata"])
    family = select_one_family(family_doc, appid)
    primary_key = str(family.get("primary_key") or "")
    if not primary_key:
        raise CanaryError("selected family has no primary_key")

    source_stamp = str(mailing.get("source_updated_at_utc") or "")
    if not source_stamp:
        raise CanaryError("mailing source timestamp is missing")
    for label, doc, field in (
        ("family_graph", family_doc, "source_updated_at_utc"),
        ("content_metadata", content, "source_updated_at_utc"),
    ):
        if doc.get(field) != source_stamp:
            raise CanaryError(f"{label} is stale versus current mailing source")

    line, source_chunk = _find_mailing_row(repo, mailing, taste_key)
    mini_index = copy.deepcopy(mailing)
    mini_index["item_count"] = 1
    mini_index["chunk_count"] = 1
    mini_index["chunk_pattern"] = "data/production/mailing/canary_NNN.tsv"
    _write_json(workspace / CANONICAL_GENERATED_PATHS["mailing_index"], mini_index)
    mini_chunk = workspace / "data/production/mailing/canary_001.tsv"
    mini_chunk.parent.mkdir(parents=True, exist_ok=True)
    mini_chunk.write_text(line + "\n", encoding="utf-8")

    mini_family = copy.deepcopy(family_doc)
    mini_family["families"] = [family]
    for field in ("family_count", "taste_subject_count", "assigned_item_count", "family_candidate_item_count"):
        if field in mini_family:
            mini_family[field] = 1
    _write_json(workspace / CANONICAL_GENERATED_PATHS["family_graph"], mini_family)

    mini_content = _slice_entries(content, taste_key, "content metadata")
    target_meta = mini_content["entries"][taste_key]
    if not str(target_meta.get("short_description") or "").strip():
        raise CanaryError("upstream_snapshot_missing_or_insufficient: target has no committed StoreBrowse short description")
    _write_json(workspace / CANONICAL_GENERATED_PATHS["content_metadata"], mini_content)

    for name in ("store", "fx", "history", "deals"):
        source = _load_json(repo / CANONICAL_GENERATED_PATHS[name])
        stamp = source.get("source_updated_at_utc") or source.get("source_mailing_updated_at_utc")
        if stamp and stamp != source_stamp:
            raise CanaryError(f"{name} snapshot is stale versus current mailing source")
        _write_json(workspace / CANONICAL_GENERATED_PATHS[name], _slice_entries(source, primary_key, name))

    fixed = repo / CANONICAL_GENERATED_PATHS["fixed_packages"]
    _copy_if_exists(fixed, workspace / CANONICAL_GENERATED_PATHS["fixed_packages"])
    policy = _load_json(repo / Path("config/mailing_policy.json"))
    frozen_profile = freeze_current_live_profile(policy, output_dir)
    profile = frozen_profile["profile"]
    wishlist = _committed_wishlist_binding(repo, appid, taste_key, source_stamp)

    source_paths: list[Path] = [
        CANONICAL_GENERATED_PATHS["mailing_index"], Path(source_chunk),
        CANONICAL_GENERATED_PATHS["family_graph"], CANONICAL_GENERATED_PATHS["content_metadata"],
        CANONICAL_GENERATED_PATHS["store"], CANONICAL_GENERATED_PATHS["fx"],
        CANONICAL_GENERATED_PATHS["history"], CANONICAL_GENERATED_PATHS["deals"],
        CANONICAL_GENERATED_PATHS["chatgpt_payload"], CANONICAL_GENERATED_PATHS["purchase_context"],
        Path("config/mailing_policy.json"), Path("config/taste_fingerprint_contract.json"),
        Path("config/taste_candidate_context_contract.json"), Path("config/taste_cache_entry_contract.json"),
    ]
    source_paths.extend(rel for rel in TASTE_CACHE_PATHS if (repo / rel).is_file())
    if fixed.is_file():
        source_paths.append(CANONICAL_GENERATED_PATHS["fixed_packages"])
    seen: set[str] = set()
    records = []
    for rel in source_paths:
        if rel.as_posix() not in seen:
            seen.add(rel.as_posix())
            records.append(_source_record(repo, rel))
    return {
        "workspace": workspace,
        "taste_key": taste_key,
        "primary_key": primary_key,
        "family": family,
        "source_stamp": source_stamp,
        "source_chunk": source_chunk,
        "profile": profile,
        "profile_binding": frozen_profile["binding"],
        "profile_snapshot_path": frozen_profile["snapshot_path"],
        "wishlist": wishlist,
        "source_provenance": records,
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise CanaryError(f"expected output missing: {path}")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def validate_prepared_outputs(
    appid: str,
    projection: dict[str, Any],
    manifest: dict[str, Any],
    queue: list[dict[str, Any]],
    frozen_profile_binding: dict[str, Any] | None = None,
) -> dict[str, Any]:
    key = f"App_{appid}"
    entries = projection.get("entries") or {}
    if projection.get("taste_subject_count") != 1 or projection.get("classified_count") != 1:
        raise CanaryError("Taste projection is not bounded to exactly one subject")
    if set(entries) != {key}:
        raise CanaryError(f"other AppID/key leaked into Taste projection: {sorted(entries)}")
    row = entries[key]
    if str(row.get("appid")) != appid:
        raise CanaryError("Taste projection AppID mismatch")
    if row.get("description_source") != "storebrowse_basic_info":
        raise CanaryError("candidate context provenance is ambiguous or not committed StoreBrowse basic info")
    if not str(row.get("short_description") or "").strip():
        raise CanaryError("candidate context is insufficient")

    profile = projection.get("current_profile") or {}
    binding = projection.get("current_binding") or {}
    required = {
        "profile_blob_sha": profile.get("blob_sha"),
        "taste_model_version": binding.get("taste_model_version"),
        "taste_semantics_sha256": binding.get("taste_semantics_sha256"),
        "taste_fingerprint": row.get("taste_fingerprint"),
        "candidate_context_sha256": row.get("candidate_context_sha256"),
    }
    for field, value in required.items():
        if not isinstance(value, str) or not value:
            raise CanaryError(f"required Taste binding missing: {field}")
    if not SHA1_RE.fullmatch(required["profile_blob_sha"]):
        raise CanaryError("profile blob binding is malformed")
    for field in ("taste_semantics_sha256", "taste_fingerprint", "candidate_context_sha256"):
        if not SHA256_RE.fullmatch(required[field]):
            raise CanaryError(f"{field} is malformed")

    if frozen_profile_binding is not None:
        validate_frozen_profile_binding(frozen_profile_binding)
        expected_profile = {
            "repository": frozen_profile_binding["repository"],
            "path": frozen_profile_binding["path"],
            "blob_sha": frozen_profile_binding["blob_sha"],
        }
        actual_profile = {
            "repository": profile.get("repository"),
            "path": profile.get("path"),
            "blob_sha": profile.get("blob_sha"),
        }
        if actual_profile != expected_profile:
            raise CanaryError(
                f"prepared tuple profile does not equal frozen canonical profile: prepared={actual_profile!r} frozen={expected_profile!r}"
            )

    mp = manifest.get("profile_binding") or {}
    if mp.get("canonical_profile_blob_sha") != required["profile_blob_sha"]:
        raise CanaryError("payload/profile binding mismatch")
    if mp.get("taste_model_version") != required["taste_model_version"]:
        raise CanaryError("payload/model binding mismatch")
    if int(manifest.get("source_family_count") or -1) != 1 or manifest.get("complete_family_partition") is not True:
        raise CanaryError("payload is not a complete one-family partition")
    if len(queue) > 1:
        raise CanaryError("semantic queue cardinality exceeded 1")
    if queue:
        q = queue[0]
        if str(q.get("appid")) != appid or q.get("taste_subject_key") != key:
            raise CanaryError("queue row belongs to another AppID")
        if q.get("taste_fingerprint") != required["taste_fingerprint"]:
            raise CanaryError("queue fingerprint binding mismatch")
        if q.get("candidate_context_sha256") != required["candidate_context_sha256"]:
            raise CanaryError("queue candidate-context binding mismatch")

    partition = {
        "queue": len(queue),
        "ready_without_ai": int(manifest.get("ready_without_ai_count") or 0),
        "deterministically_excluded": int(manifest.get("deterministically_excluded_without_ai_count") or 0),
    }
    if sum(partition.values()) != 1:
        raise CanaryError(f"one-family decision partition is invalid: {partition}")
    return {
        "target_row": row,
        "bindings": required,
        "queue_decision": "semantic_queue_row" if queue else (
            "ready_without_ai" if partition["ready_without_ai"] == 1 else "deterministically_excluded"
        ),
        "partition": partition,
    }


def _run_current_production_builders(repo: Path, info: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    workspace = info["workspace"]
    scripts = repo / "scripts"
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    projection_mod = importlib.import_module("build_pre_ai_taste_projection")
    payload_mod = importlib.import_module("build_pre_ai_chatgpt_payload")
    profile = copy.deepcopy(info["profile"])
    wishlist = info["wishlist"]
    projection_mod.current_profile = lambda policy: copy.deepcopy(profile)

    def deny_appdetails(targets: dict[str, Any], max_workers: int = 8):
        if targets:
            raise CanaryError("upstream_snapshot_missing_or_insufficient: AppDetails fallback is forbidden in current-main canary")
        return {}, [], 0.0, 0.0

    projection_mod.fetch_appdetails_descriptions = deny_appdetails
    payload_mod.load_wishlist = lambda: {
        "blob_sha": wishlist["blob_sha"],
        "entry_count": wishlist["entry_count"],
        "appids": set(wishlist["appids"]),
    }
    old_cwd = Path.cwd()
    try:
        os.chdir(workspace)
        projection_mod.main()
        projection = _load_json(CANONICAL_GENERATED_PATHS["taste_projection"])
        payload_mod.main()
        manifest = _load_json(CANONICAL_GENERATED_PATHS["chatgpt_payload"])
        queue = _load_jsonl(Path("data/production/pre_ai/chatgpt_taste_queue.jsonl"))
    finally:
        os.chdir(old_cwd)
    return projection, manifest, queue


def _copy_artifact(src: Path, dst: Path) -> None:
    if not src.exists():
        raise CanaryError(f"expected canary output missing: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def run_canary(repo: Path, output_dir: Path, appid: str) -> dict[str, Any]:
    started = time.monotonic()
    repo, output_dir, appid = repo.resolve(), output_dir.resolve(), parse_appid(appid)
    ensure_output_isolated(repo, output_dir)
    provenance = establish_current_main(repo)
    status_before = git_status(repo)
    output_dir.mkdir(parents=True, exist_ok=True)
    info = build_one_subject_workspace(repo, output_dir, appid)
    projection, manifest, queue = _run_current_production_builders(repo, info)
    validation = validate_prepared_outputs(appid, projection, manifest, queue, info["profile_binding"])
    workspace = info["workspace"]
    _copy_artifact(workspace / CANONICAL_GENERATED_PATHS["taste_projection"], output_dir / "taste_projection.one.json")
    _copy_artifact(workspace / CANONICAL_GENERATED_PATHS["chatgpt_payload"], output_dir / "chatgpt_payload.one.json")
    _copy_artifact(workspace / "data/production/pre_ai/chatgpt_taste_queue.jsonl", output_dir / "chatgpt_taste_queue.one.jsonl")

    status_after = git_status(repo)
    diff_exit = subprocess.run(
        ["git", "-C", str(repo), "diff", "--exit-code", "--"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode
    if status_before or status_after or diff_exit != 0:
        raise CanaryError("repository working tree changed during read-only canary preparation")
    elapsed = round(time.monotonic() - started, 3)
    main_provenance = {
        "requested_appid": appid,
        **provenance,
        "head_matches_origin_main": provenance["checked_out_head_sha"] == provenance["resolved_origin_main_sha"],
        "repository_status_before": status_before,
        "repository_status_after": status_after,
        "git_diff_exit_code_after": diff_exit,
        "source_mailing_updated_at_utc": info["source_stamp"],
        "source_inputs": info["source_provenance"],
    }
    _write_json(output_dir / "main_provenance.json", main_provenance)
    row, bindings = validation["target_row"], validation["bindings"]
    tuple_doc = {
        "schema_version": 1,
        "purpose": "immutable_one_appid_taste_semantic_tuple_preparation",
        "appid": appid,
        "taste_subject_key": info["taste_key"],
        "profile_binding": info["profile_binding"],
        "taste_model_version": bindings["taste_model_version"],
        "taste_semantics_sha256": bindings["taste_semantics_sha256"],
        "taste_fingerprint": bindings["taste_fingerprint"],
        "candidate_context_sha256": bindings["candidate_context_sha256"],
        "queue_cardinality": len(queue),
        "queue_row": queue[0] if queue else None,
        "semantic_execution_attempted": False,
    }
    _write_json(output_dir / "prepared_semantic_tuple.json", tuple_doc)
    proof = {
        "schema_version": 2,
        "purpose": "read_only_current_main_one_appid_taste_preparation_proof",
        "status": "complete",
        "requested_appid": appid,
        "target_subject_count": 1,
        "taste_subject_key": info["taste_key"],
        "primary_key": info["primary_key"],
        "current_main": main_provenance,
        "frozen_profile": info["profile_binding"],
        "binding": {
            "profile_identity": f"{projection['current_profile'].get('repository')}:{projection['current_profile'].get('path')}",
            "profile_commit_sha": info["profile_binding"]["resolved_commit_sha"],
            "profile_blob_sha": bindings["profile_blob_sha"],
            "profile_content_sha256": info["profile_binding"]["content_sha256"],
            "taste_model_version": bindings["taste_model_version"],
            "taste_semantics_sha256": bindings["taste_semantics_sha256"],
            "taste_fingerprint": bindings["taste_fingerprint"],
            "candidate_context_sha256": bindings["candidate_context_sha256"],
        },
        "candidate_context": {
            "source": row.get("description_source"),
            "short_description": row.get("short_description"),
            "bundle_members": row.get("bundle_members") or [],
            "bundle_member_descriptions": row.get("bundle_member_descriptions") or [],
        },
        "raw_taste_projection_row": row,
        "raw_decision_evidence": {
            "status": row.get("status"),
            "ai_required_reason": row.get("ai_required_reason"),
            "cache_entry_present": row.get("cache_entry_present"),
            "cache_appid_matches": row.get("cache_appid_matches"),
            "cache_profile_matches": row.get("cache_profile_matches"),
            "cache_model_matches": row.get("cache_model_matches"),
            "cache_semantics_matches": row.get("cache_semantics_matches"),
            "cache_fingerprint_matches": row.get("cache_fingerprint_matches"),
            "cache_candidate_context_bound": row.get("cache_candidate_context_bound"),
            "cache_candidate_context_matches": row.get("cache_candidate_context_matches"),
            "cached_taste": row.get("cached_taste"),
        },
        "deterministic_queue_decision": validation["queue_decision"],
        "decision_partition": validation["partition"],
        "queue_cardinality": len(queue),
        "queue_row": queue[0] if queue else None,
        "safety": {
            "semantic_execution_attempted": False,
            "canonical_ingest_attempted": False,
            "production_write_attempted": False,
            "storebrowse_refresh_attempted": False,
            "steam_appdetails_fallback_attempted": False,
            "canonical_profile_refetch_attempted": True,
            "canonical_profile_refetch_read_only": True,
            "canonical_profile_snapshot_frozen": True,
            "canonical_wishlist_refetch_attempted": False,
            "outputs_outside_repository": True,
            "repository_clean_before_after": True,
            "scheduled_task_modified": False,
            "scheduled_task_triggered": False,
        },
        "timing": {
            "harness_elapsed_seconds": elapsed,
            "projection_elapsed_seconds": projection.get("elapsed_seconds"),
            "payload_elapsed_seconds": manifest.get("elapsed_seconds"),
        },
    }
    _write_json(output_dir / "canary_proof.json", proof)
    shutil.rmtree(workspace)
    return proof


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--appid", required=True, help="Exactly one numeric Steam AppID")
    parser.add_argument("--output-dir", required=True, type=Path, help="Empty output directory outside repository")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help=argparse.SUPPRESS)
    args = parser.parse_args(list(argv) if argv is not None else None)
    try:
        proof = run_canary(args.repo_root, args.output_dir, args.appid)
    except CanaryError as exc:
        print(f"CANARY_ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "status": proof["status"],
        "requested_appid": proof["requested_appid"],
        "profile_blob_sha": proof["binding"]["profile_blob_sha"],
        "profile_commit_sha": proof["binding"]["profile_commit_sha"],
        "queue_cardinality": proof["queue_cardinality"],
        "deterministic_queue_decision": proof["deterministic_queue_decision"],
        "harness_elapsed_seconds": proof["timing"]["harness_elapsed_seconds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())