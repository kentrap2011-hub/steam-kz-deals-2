#!/usr/bin/env python3
"""One-shot GitHub-owned shadow Stage B. Never a production issuer or writer.

This namespace adapter REUSES the existing Research strict transport,
Assembly schema/source-first checks and strict V2 Dossier validator. The
canonical two-stage worker and its inactive production gates stay unchanged.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from dossier_shadow_research_trial import (
    PREFIX, TRIAL, frozen_trial, inspect_transport, sandbox_output_path, require,
)
from dossier_two_stage_assembly_semantic_worker import (
    _check_exact_source_first, inactive_assembly_gate,
)
from dossier_two_stage_contract_guard import CONFIG, canonical_sha256, _privacy
from dossier_two_stage_staging import (
    blob, exists, first_parent_contains, git, require_only_new, strict_json,
)
from taste_steam_review_dossier_strict import validate_dossier_strict

BUFFER = PREFIX + "/assembly_buffer.json"
MARKERS = PREFIX + "/assembly_run_starts"
PROMPT = "config/dossier_shadow_18_assembly_semantic_prompt.md"
CONTRACT = "config/dossier_two_stage_interfaces_contract.json"
SCHEMA = "DOSSIER-SHADOW-18-ASSEMBLY-BUFFER-V1"
RESULT = "DOSSIER-ASYNC-ASSEMBLY-RESULT-V1"
H40 = re.compile(r"^[0-9a-f]{40}$")
H32 = re.compile(r"^[0-9a-f]{32}$")
BRANCH = "sandbox/" + TRIAL


def raw_at(repo, commit, path):
    require(isinstance(path, str) and path.startswith(
        ("reviews/dossier_shadow_offline/trials/" + TRIAL + "/", "config/")),
        "read outside isolated sandbox/config")
    require(".." not in Path(path).parts, "traversal in Git path")
    return git(repo, "show", f"{commit}:{path}").stdout


def json_at(repo, commit, path):
    return strict_json(raw_at(repo, commit, path))


def head(repo):
    return git(repo, "rev-parse", "HEAD").stdout.decode().strip()


def fixed_group_order(items):
    from dossier_shadow_18_assembly_sandbox import _decision
    groups = _decision()["scope"]["groups"]
    require(len(items) == 18 and [
        (e["group_sequence"], e["item_index"], e["appid"]) for e in items
    ] == [(g["sequence"], i, appid) for g in groups
         for i, appid in enumerate(g["appids"])],
            "18 original items/order or group membership drift")


def _pin(repo, revision, path):
    return blob(repo, revision, path)


def prepare(repo, *, research_marker_commit):
    """Produce the *single fixed* GitHub-owned buffer (no file writes).

    Marker and frozen Research buffer must already have been issued in this
    exact sandbox branch. No generic source commit input is accepted.
    """
    inactive_assembly_gate()
    trial = frozen_trial(repo, marker_commit=research_marker_commit,
                         buffer_path=PREFIX + "/research_buffer.json")
    require(trial["sandbox_semantics_authorized"] is True,
            "parallel Research semantic/reviewer gate is still blocked")
    require(first_parent_contains(repo, research_marker_commit, head(repo)),
            "Research marker not on current branch first-parent lineage")
    fixed_group_order(trial["items"])
    parent = trial["marker_parent"]
    for path in (trial["buffer_path"],):
        require(_pin(repo, parent, path) == _pin(repo, head(repo), path),
                "Research frozen buffer was overwritten")
    prompt_blob = _pin(repo, head(repo), PROMPT)
    contract_blob = _pin(repo, head(repo), CONTRACT)
    contract = json_at(repo, head(repo), CONTRACT)
    require(contract["active"] is False
            and contract["authorized_for_semantic_execution"] is False
            and contract["authorized_for_canonical_ingest"] is False,
            "accidental live two-stage activation")
    entries = []
    for item in trial["items"]:
        a = item["assignment"]
        identity = {"trial_id": TRIAL, "research_marker_commit": research_marker_commit,
                    "assignment": a, "assembly_prompt_blob": prompt_blob}
        aid = "shadow-assembly-" + canonical_sha256(identity)[:24]
        entries.append({
            "group_sequence": item["group_sequence"],
            "item_index": item["item_index"],
            "appid": item["appid"], "assignment_id": a["assignment_id"],
            "assembly_assignment_id": aid,
            "research_path": sandbox_output_path(item),
            "research_assignment_sha256": canonical_sha256(a),
        })
    body = {
        "schema": SCHEMA, "version": 1, "trial_id": TRIAL, "sandbox_only": True,
        "research_marker_commit": research_marker_commit,
        "research_buffer_path": trial["buffer_path"],
        "research_buffer_blob_sha": trial["buffer_blob_sha"],
        "research_buffer_id": json_at(repo, parent, trial["buffer_path"])["research_buffer_id"],
        "assembly_contract_blob_sha": contract_blob,
        "assembly_prompt_blob_sha": prompt_blob,
        "groups": [x["sequence"] for x in __import__(
            "dossier_shadow_18_assembly_sandbox")._decision()["scope"]["groups"]],
        "items": entries, "production_writes": [], "canonical_acceptance": False,
        "scheduled_tasks_mutated": False,
    }
    return {**body, "buffer_id": canonical_sha256(body)}


def marker_parent(repo, marker_commit):
    require(isinstance(marker_commit, str) and H40.fullmatch(marker_commit),
            "exact Assembly marker commit required")
    parent = git(repo, "rev-list", "--parents", "-n", "1", marker_commit
                 ).stdout.decode().split()
    require(len(parent) == 2 and parent[0] == marker_commit,
            "Assembly marker must have exactly one Git parent")
    rows = git(repo, "diff-tree", "--no-commit-id", "--name-status",
               "-r", marker_commit).stdout.decode().splitlines()
    require(len(rows) == 1 and rows[0].startswith("A\t"),
            "Assembly marker-only create-only Git commit required")
    path = rows[0][2:]
    match = re.fullmatch(re.escape(MARKERS) + r"/([0-9a-f]{32})\.json", path)
    require(match is not None and not exists(repo, parent[1], path),
            "wrong Assembly marker namespace/duplicate")
    nonce = match.group(1)
    doc = json_at(repo, marker_commit, path)
    require(type(doc) is dict and set(doc) == {
        "schema", "schema_version", "trial_id", "nonce",
        "issuer_workflow", "issuer_run_id", "buffer_blob_sha",
    } and doc == {
        "schema": "DOSSIER-SHADOW-ASSEMBLY-RUN-START-V1",
        "schema_version": 1, "trial_id": TRIAL, "nonce": nonce,
        "issuer_workflow": "issue-dossier-shadow-18-assembly.yml",
        "issuer_run_id": doc.get("issuer_run_id"),
        "buffer_blob_sha": blob(repo, parent[1], BUFFER),
    } and type(doc["issuer_run_id"]) is int and doc["issuer_run_id"] > 0,
            "Assembly marker missing exact GitHub workflow/run/buffer proof")
    return parent[1], nonce, doc


def frozen(repo, *, marker_commit):
    """Marker parent (not user/worker HEAD) is the one authority."""
    inactive_assembly_gate()
    parent, nonce, proof = marker_parent(repo, marker_commit)
    require(first_parent_contains(repo, marker_commit, head(repo)),
            "Assembly marker not in current exact sandbox history")
    manifest = json_at(repo, parent, BUFFER)
    require(manifest == prepare(repo,
                               research_marker_commit=manifest["research_marker_commit"]),
            "Assembly buffer/plan not exactly derived from original Research")
    require(blob(repo, parent, BUFFER) == blob(repo, head(repo), BUFFER),
            "Assembly plan overwritten/stale")
    require(first_parent_contains(
        repo, manifest["research_marker_commit"], marker_commit),
        "Assembly marker not descended from original Research")
    require(manifest["assembly_contract_blob_sha"] == blob(repo, parent, CONTRACT)
            and manifest["assembly_prompt_blob_sha"] == blob(repo, parent, PROMPT),
            "Assembly schema/prompt/contract changed at marker parent")
    return manifest, nonce, parent


def result_path(entry):
    return (PREFIX + f"/assembly/g{entry['group_sequence']:06d}/"
            + entry["appid"] + "--" + entry["assembly_assignment_id"] + ".json")


def inspect(repo, *, marker_commit, research_commits):
    """Independent frozen order; missing/invalid A never blocks B or C."""
    manifest, nonce, parent = frozen(repo, marker_commit=marker_commit)
    require(type(research_commits) is dict and
            set(research_commits) <= {e["appid"] for e in manifest["items"]}
            and all(H40.fullmatch(str(c)) for c in research_commits.values()),
            "foreign or malformed submitted Research commit locator")
    trial = frozen_trial(repo, marker_commit=manifest["research_marker_commit"],
                         buffer_path=manifest["research_buffer_path"])
    fixed_group_order(trial["items"])
    result = []
    for item, entry in zip(trial["items"], manifest["items"]):
        row = {"group_sequence": entry["group_sequence"],
               "item_index": entry["item_index"], "appid": entry["appid"],
               "assembly_assignment_id": entry["assembly_assignment_id"],
               "output_path": result_path(entry),
               "attempt_consumed": False}
        commit = research_commits.get(entry["appid"])
        if commit is None:
            row["status"] = "research_not_submitted"
        else:
            try:
                proof = inspect_transport(repo, trial=trial, item=item,
                                          result_commit=commit)
                require(first_parent_contains(repo, commit, head(repo)),
                        "Research package not in current branch lineage")
                if exists(repo, head(repo), row["output_path"]):
                    row["status"] = "candidate_already_submitted"
                else:
                    row["status"] = "ready"
                row["research_proof"] = proof
            except (ValueError, KeyError):
                row["status"] = "research_transport_invalid"
                row["diagnostic_code"] = "invalid_origin_or_binding"
        result.append(row)
    return {"schema": "DOSSIER-SHADOW-18-ASSEMBLY-STATUS-V1",
            "trial_id": TRIAL, "marker_commit": marker_commit,
            "buffer_id": manifest["buffer_id"], "sandbox_only": True,
            "canonical_acceptance": False, "deep_ready": False,
            "production_writes": [], "semantic_attempts": 0,
            "rows": result, "ready_count": sum(r["status"] == "ready" for r in result)}


def build_candidate(repo, *, marker_commit, research_commits, appid, semantic):
    """Strict existing result schema/source-first semantics, shadow namespace only.

    No Git writes. Caller must publish the exact returned path create-only and
    then GitHub must verify the introducing commit. No semantic generation here.
    """
    manifest, nonce, parent = frozen(repo, marker_commit=marker_commit)
    rows = inspect(repo, marker_commit=marker_commit,
                   research_commits=research_commits)["rows"]
    candidates = [(e, r) for e, r in zip(manifest["items"], rows)
                  if e["appid"] == appid]
    require(len(candidates) == 1, "unbound Assembly AppID")
    e, r = candidates[0]
    require(r["status"] == "ready", "Research not proven or candidate already exists")
    research_raw = raw_at(repo, r["research_proof"]["result_commit"],
                          r["research_proof"]["path"])
    package = strict_json(research_raw)
    trial = frozen_trial(repo, marker_commit=manifest["research_marker_commit"],
                         buffer_path=manifest["research_buffer_path"])
    a = next(item["assignment"] for item in trial["items"] if
             item["appid"] == appid)
    original = {**a, "research_marker_anchor_commit": trial["marker_commit"],
                "research_marker_nonce": trial["nonce"]}
    proof = r["research_proof"]
    rt = {
        "research_marker_anchor_commit": trial["marker_commit"],
        "research_package_git_commit": proof["result_commit"],
        "research_package_path": proof["path"],
        "research_package_blob_sha": proof["git_blob_sha"],
        "research_package_raw_sha256": proof["raw_sha256"],
        "research_package_sha256": proof["canonical_sha256"],
        "research_prepared_work_path": trial["buffer_path"],
        "research_prepared_work_blob_sha": trial["buffer_blob_sha"],
        "assembly_plan_blob_sha": blob(repo, parent, BUFFER),
    }
    require(type(semantic) is dict and set(semantic) == {
        "outcome", "payload", "supplemental_operations"},
        "only typed semantic result fields allowed")
    target = {"schema": "TASTE-STEAM-REVIEW-DOSSIER-V2",
              "schema_version": 2,
              "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
              "worker_schema_version": 2,
              "web_evidence_contract": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
              "web_evidence_contract_version": 2,
              "canonical_worker_binding_sha256":
                  canonical_sha256(a["web_evidence_contract_binding"])}
    doc = {
        "schema": RESULT, "schema_version": 1,
        "assembly_assignment_id": e["assembly_assignment_id"],
        "original_research_assignment": original,
        "research_transport": rt,
        "assembly_marker_anchor_commit": marker_commit,
        "assembly_marker_nonce": nonce,
        "assembly_contract_sha256": canonical_sha256(json_at(repo, parent, CONTRACT)),
        "assembly_prompt_sha256": hashlib.sha256(raw_at(repo, parent, PROMPT)).hexdigest(),
        "canonical_dossier_target": target,
        "output_path": result_path(e),
        "outcome": semantic["outcome"], "payload": copy.deepcopy(semantic["payload"]),
        "supplemental_operations": copy.deepcopy(semantic["supplemental_operations"]),
        "staged_only": True, "canonical_acceptance": False,
    }
    # Use the ONE existing async Assembly schema. Its three live namespace
    # regexes cannot be written in the sandbox: substitute only their path
    # *representations* in the validation view; never emit those live paths.
    view = copy.deepcopy(doc)
    snap = original["snapshot_id"]
    group = f"g{e['group_sequence']:06d}"
    suffix = appid + "--" + a["assignment_id"] + ".json"
    view["research_transport"]["research_package_path"] = (
        f"data/ai_inbox/dossier_research/{snap}/{group}/{suffix}")
    view["research_transport"]["research_prepared_work_path"] = (
        f"data/control/dossier_research_assignments/{snap}/{group}/{suffix}")
    view["output_path"] = (
        f"data/ai_inbox/dossier_assembly/{snap}/{group}/" +
        appid + "--" + e["assembly_assignment_id"] + ".json")
    schema = json.loads((CONFIG / "dossier_async_assembly_result_v1.schema.json").read_text())
    errors = list(Draft202012Validator(schema).iter_errors(view))
    require(not errors, "existing strict Assembly schema failed: " +
            (errors[0].message if errors else ""))
    require(doc["outcome"] == doc["payload"]["status"], "typed Assembly outcome mismatch")
    _check_exact_source_first(package, doc["supplemental_operations"])
    _privacy(doc["payload"])
    if doc["outcome"] == "assembled_candidate_ready":
        dossier = doc["payload"]["dossier"]
        require(dossier["appid"] == appid and dossier["title"] == a["title"],
                "wrong original child work or title")
        strict_contract = json.loads((CONFIG / "taste_steam_review_dossier_contract.json").read_text())
        validate_dossier_strict(dossier, strict_contract, expected_appid=appid,
                                expected_title=a["title"], require_fresh_at_acceptance=False)
        require(dossier["game_identity"].get("release_year") ==
                package["identity"]["original_work_release_year"],
                "Assembly rewrote original Research work release year")
    return r["output_path"], doc


def verify_candidate(repo, *, marker_commit, research_commits, appid,
                     result_commit):
    require(H40.fullmatch(str(result_commit)), "actual Assembly Git commit required")
    state = inspect(repo, marker_commit=marker_commit,
                    research_commits=research_commits)
    row = next((r for r in state["rows"] if r["appid"] == appid), None)
    require(row is not None, "unbound result AppID")
    require(first_parent_contains(repo, marker_commit, result_commit)
            and first_parent_contains(repo, result_commit, head(repo)),
            "Assembly submission outside immutable branch history")
    require_only_new(repo, result_commit, [row["output_path"]])
    raw = raw_at(repo, result_commit, row["output_path"])
    require(blob(repo, result_commit, row["output_path"]) ==
            blob(repo, head(repo), row["output_path"]),
            "Assembly original file overwritten")
    payload = strict_json(raw)
    semantic = {k: payload[k] for k in ("outcome", "payload", "supplemental_operations")}
    # Exact re-validation against frozen Research, not mutable latest.
    # An existing exact output is expected for verification only.
    from unittest.mock import patch
    original_exists = exists
    with patch(f"{__name__}.exists", side_effect=lambda repo_, rev, path:
               False if path == row["output_path"] else original_exists(repo_, rev, path)):
        expected_path, expected = build_candidate(
            repo, marker_commit=marker_commit, research_commits=research_commits,
            appid=appid, semantic=semantic)
    require(expected_path == row["output_path"] and expected == payload,
            "Assembly result mutated frozen Git binding or provenance")
    return {"status": "submitted_unaccepted_shadow_only",
            "canonical_acceptance": False, "deep_ready": False,
            "result_path": row["output_path"], "result_commit": result_commit}


def _issuer_env():
    require(os.environ.get("GITHUB_ACTIONS") == "true"
            and os.environ.get("GITHUB_EVENT_NAME") == "workflow_dispatch"
            and os.environ.get("GITHUB_REF_NAME") == BRANCH
            and os.environ.get("GITHUB_WORKFLOW_REF", "").split("@")[0].endswith(
                "/.github/workflows/issue-dossier-shadow-18-assembly.yml"),
            "issuer is GitHub one-shot workflow on the exact sandbox branch only")


def cli():
    parser = argparse.ArgumentParser(description=__doc__)
    sp = parser.add_subparsers(dest="command", required=True)
    issue = sp.add_parser("issue-buffer")
    issue.add_argument("--research-marker-commit", required=True)
    mark = sp.add_parser("issue-marker")
    mark.add_argument("--nonce", required=True)
    ready = sp.add_parser("inspect")
    ready.add_argument("--assembly-marker-commit", required=True)
    ready.add_argument("--research-commits", required=True,
                       help="JSON dictionary appid -> original Research introducing commit")
    args = parser.parse_args()
    repo = Path.cwd()
    if args.command == "issue-buffer":
        _issuer_env()
        require(not exists(repo, head(repo), BUFFER), "one-shot buffer already exists")
        body = prepare(repo, research_marker_commit=args.research_marker_commit)
        print(json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    elif args.command == "issue-marker":
        _issuer_env()
        require(H32.fullmatch(args.nonce), "bad GitHub-generated nonce")
        require(exists(repo, head(repo), BUFFER), "GitHub must commit buffer first")
        path = MARKERS + "/" + args.nonce + ".json"
        require(not exists(repo, head(repo), path), "marker must be create-only")
        print(json.dumps({
            "schema": "DOSSIER-SHADOW-ASSEMBLY-RUN-START-V1",
            "schema_version": 1, "trial_id": TRIAL, "nonce": args.nonce,
            "issuer_workflow": "issue-dossier-shadow-18-assembly.yml",
            "issuer_run_id": int(os.environ["GITHUB_RUN_ID"]),
            "buffer_blob_sha": blob(repo, head(repo), BUFFER)},
            ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        state = inspect(repo, marker_commit=args.assembly_marker_commit,
                        research_commits=json.loads(args.research_commits))
        print(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    cli()
