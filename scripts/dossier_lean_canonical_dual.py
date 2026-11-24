#!/usr/bin/env python3
"""Additive, default-off canonical Lean Dossier acceptance/reader boundary.

A schema label, sandbox receipt, in-memory record, or uncommitted writer output
is not Deep evidence. Existing strict-V2 readers and bytes remain unchanged.
"""
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from dossier_notes_v2_lean_final import LEAN_SCHEMA, SCHEMA_PATH, validate_lean_final
from taste_steam_review_dossier import canonical_sha256

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/dossier_lean_canonical_dual_format_contract.json"
SOURCE_PATH = ROOT / "config/dossier_research_notes_v2_contract.json"
WRITER_PATH = ROOT / "config/dossier_notes_v2_individual_writer_contract.json"
STORE = Path("data/cache/taste_steam_review_dossiers")
RECEIPTS = Path("data/control/dossier_notes_v2/canonical_accepted")
RECEIPT_SCHEMA = "DOSSIER-NOTES-V2-INDIVIDUAL-CANONICAL-ACCEPTANCE-V1"
QUALITY_CONTRACT = "DOSSIER-LEAN-CANONICAL-QUALITY-V1"
COMPAT_CONTRACT = "DOSSIER-LEAN-CANONICAL-DEEP-V1"
_SHA = re.compile(r"[0-9a-f]{40}")
_NAME = re.compile(r"[0-9]+--[a-zA-Z0-9_-]+\.json")


def _policy():
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if (policy.get("schema") != "DOSSIER-LEAN-CANONICAL-DUAL-FORMAT-V1"
            or policy.get("version") != 1
            or policy.get("owner") != "github_control_plane"
            or policy.get("legacy_strict_v2_unchanged") is not True
            or policy.get("legacy_cache_and_deep_binding_unchanged") is not True
            or policy.get("lean_schema") != LEAN_SCHEMA
            or policy.get("canonical_receipt_schema") != RECEIPT_SCHEMA
            or policy.get("canonical_store") != STORE.as_posix()
            or policy.get("canonical_receipt_root") != RECEIPTS.as_posix()
            or any(type(policy.get(key)) is not bool for key in (
                "lean_writer_enabled", "lean_reader_enabled", "lean_deep_enabled"))):
        raise ValueError("unrecognized canonical Lean dual-format authority")
    return policy


def require_gate(stage, *, repo_root=ROOT, offline_fixture=False):
    """Offline test bypass is confined to an existing independent temp Git gate.

    Live requires all existing V2 owner+writer approvals as well as this
    stage-specific explicit opt-in. No caller-supplied boolean grants live use.
    """
    if stage not in ("writer", "reader", "deep"):
        raise ValueError("unknown Lean canonical stage")
    policy = _policy()
    if offline_fixture:
        from dossier_two_stage_final_acceptance import offline_gate
        offline_gate(repo_root, offline_fixture=True)
        if any(policy["lean_" + name + "_enabled"] for name in ("writer", "reader", "deep")):
            raise ValueError("offline fixture requires default-OFF Lean policy")
        return policy
    if not policy["lean_" + stage + "_enabled"]:
        raise ValueError("canonical Lean " + stage + " is disabled")
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    writer = json.loads(WRITER_PATH.read_text(encoding="utf-8"))
    from dossier_research_notes_v2 import _v2_individual_writer_authorized
    if not _v2_individual_writer_authorized(source, writer):
        raise ValueError("canonical Lean requires real GitHub-owned source/writer approval")
    if not (policy["lean_writer_enabled"] and policy["lean_reader_enabled"]):
        raise ValueError("canonical Lean writer/reader must be jointly authorized")
    return policy


def quality_binding():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return {
        "contract": QUALITY_CONTRACT,
        "dossier_format": LEAN_SCHEMA,
        "schema_sha256": canonical_sha256(schema),
        "no_legacy_review_ledger": True,
    }


def validate_writer_lean(dossier, *, appid, title, now=None, expected_ttl_days=None):
    validate_lean_final(dossier, expected_appid=appid, expected_title=title,
                        expected_ttl_days=expected_ttl_days, now=now)
    year = dossier["game_identity"]["release_year"]
    if type(year) is not int or not 1970 <= year <= 2100:
        raise ValueError("canonical Lean requires identified original release year")
    return dossier


def lean_receipt_fields(dossier):
    return {
        "dossier_format": LEAN_SCHEMA,
        "quality_binding": quality_binding(),
        "original_release_year": dossier["game_identity"]["release_year"],
    }


def _git_committed_bytes(repo_root, path):
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", "HEAD:" + path.as_posix()],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ValueError("canonical Lean record/receipt not committed at Git HEAD")
    return result.stdout


def _receipt_for(repo_root, appid, digest, dossier):
    base = repo_root / RECEIPTS
    if not base.is_dir():
        raise ValueError("canonical Lean owner acceptance receipt absent")
    matches = list(base.glob("*/g[0-9][0-9][0-9][0-9][0-9][0-9]/" + appid + "--*.json"))
    if len(matches) != 1:
        raise ValueError("canonical Lean requires one unambiguous owner acceptance receipt")
    path = matches[0]
    if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):
        raise ValueError("canonical Lean receipt path escape")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assignment = receipt.get("assignment")
    if (receipt.get("schema") != RECEIPT_SCHEMA
            or receipt.get("dossier_format") != LEAN_SCHEMA
            or receipt.get("quality_binding") != quality_binding()
            or receipt.get("dossier_sha256") != digest
            or receipt.get("original_release_year") != dossier["game_identity"]["release_year"]
            or not isinstance(assignment, dict)
            or assignment.get("appid") != appid
            or assignment.get("title") != dossier["title"]
            or assignment.get("trial_id") != receipt.get("trial_id")
            or type(assignment.get("group_sequence")) is not int
            or str(assignment["group_sequence"]).zfill(6) != path.parent.name[1:]
            or path.name != appid + "--" + str(assignment.get("assignment_id")) + ".json"
            or path.parent.parent.name != receipt.get("trial_id")
            or any(not isinstance(receipt.get(key), str)
                   or not _SHA.fullmatch(receipt[key])
                   for key in ("marker_commit", "research_commit", "assembly_commit"))):
        raise ValueError("canonical Lean issuer/receipt binding invalid")
    relative = path.relative_to(repo_root)
    if _git_committed_bytes(repo_root, relative) != path.read_bytes():
        raise ValueError("canonical Lean receipt not exactly Git-committed")
    # A committed file is insufficient by itself: rebind to the exact immutable
    # Research/Assembly chain authenticated by the existing GitHub V2 inspector.
    from dossier_research_notes_v2 import assembly_work, inspect_assembly
    try:
        checked = inspect_assembly(
            repo_root, marker_commit=receipt["marker_commit"],
            trial_id=receipt["trial_id"], appid=appid,
            research_commit=receipt["research_commit"],
            result_commit=receipt["assembly_commit"],
        )
        if checked.get("status") != "strict_item_valid_pending_existing_atomic_group_ingest":
            raise ValueError("wrong immutable V2 Assembly status")
        work = assembly_work(
            repo_root, marker_commit=receipt["marker_commit"],
            trial_id=receipt["trial_id"], appid=appid,
            research_commit=receipt["research_commit"],
        )
        if (work.get("status") != "ready_for_autonomous_assembly"
                or work["assignment"] != assignment):
            raise ValueError("wrong original frozen work assignment")
        from dossier_two_stage_staging import json_at
        candidate = json_at(repo_root, receipt["assembly_commit"], work["output_path"])
        if (candidate.get("final_dossier") != dossier
                or candidate.get("outcome") != "assembled_candidate_ready"):
            raise ValueError("immutable Assembly bytes differ from accepted Lean")
    except (ValueError, TypeError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("canonical Lean issuer/Research/Assembly ancestry unverified") from exc
    return receipt


def inspect_accepted_lean(dossier_record, *, repo_root=ROOT, now=None,
                          expected_appid=None, expected_title=None,
                          expected_ttl_days=None,
                          offline_fixture=False, stage="reader"):
    """Use only exact Git-committed canonical store + owner writer receipt."""
    require_gate(stage, repo_root=repo_root, offline_fixture=offline_fixture)
    root = Path(repo_root).resolve()
    if not isinstance(dossier_record, dict):
        raise ValueError("canonical Lean record missing")
    doc, path = dossier_record.get("doc"), dossier_record.get("path")
    if not isinstance(doc, dict) or doc.get("schema") != LEAN_SCHEMA:
        raise ValueError("canonical Lean schema incorrect")
    appid = doc.get("appid")
    if not isinstance(appid, str) or not appid.isdigit():
        raise ValueError("canonical Lean AppID invalid")
    expected_path = STORE / ("App_" + appid + ".json")
    if path != expected_path.as_posix():
        raise ValueError("canonical Lean does not promote sandbox paths")
    if expected_appid is not None and appid != str(expected_appid):
        raise ValueError("canonical Lean wrong AppID")
    if expected_title is not None and doc.get("title") != expected_title:
        raise ValueError("canonical Lean wrong edition")
    disk_path = root / expected_path
    if disk_path.is_symlink() or not disk_path.is_file():
        raise ValueError("canonical Lean store file missing/unsafe")
    raw = disk_path.read_bytes()
    if _git_committed_bytes(root, expected_path) != raw:
        raise ValueError("canonical Lean store is uncommitted/mutable")
    if json.loads(raw.decode("utf-8")) != doc:
        raise ValueError("canonical Lean stored document mismatch")
    # The existing Deep loader binds SHA256 of exact stored file bytes, whereas
    # the legacy V2 writer's receipt binds canonical JSON-object SHA256.
    # Preserve BOTH without ever conflating them or changing old receipts.
    raw_digest = hashlib.sha256(raw).hexdigest()
    if dossier_record.get("content_sha256") != raw_digest:
        raise ValueError("canonical Lean raw-content digest mismatch")
    digest = canonical_sha256(doc)
    validate_writer_lean(doc, appid=appid, title=doc["title"], now=now,
                         expected_ttl_days=expected_ttl_days)
    receipt = _receipt_for(root, appid, digest, doc)
    receipt_digest = canonical_sha256(receipt)
    binding = {
        "contract": COMPAT_CONTRACT,
        "dossier_format": LEAN_SCHEMA,
        "quality_binding": quality_binding(),
        "accepted_receipt_sha256": receipt_digest,
    }
    return {"doc": doc, "receipt": receipt, "binding": binding}


def versioned_dossier_state(dossier, contract, *, store_dir, appid, now=None,
                            expected_title=None, expected_ttl_days=None,
                            offline_fixture=False):
    """Strict default stays byte-compatible; Lean needs committed owner receipt."""
    from taste_steam_review_dossier_strict import dossier_state_strict
    if not isinstance(dossier, dict) or dossier.get("schema") != LEAN_SCHEMA:
        return dossier_state_strict(dossier, contract, now=now, expected_appid=appid,
                                    expected_title=expected_title), None
    path = STORE / ("App_" + str(appid) + ".json")
    root = Path(store_dir).resolve().parent.parent.parent
    raw_path = root / path
    if not raw_path.is_file() or raw_path.is_symlink():
        raise ValueError("canonical Lean source bytes not found")
    record = {"path": path.as_posix(), "doc": dossier,
              "content_sha256": hashlib.sha256(raw_path.read_bytes()).hexdigest()}
    if (Path(store_dir).resolve() != (root / STORE).resolve()):
        raise ValueError("canonical Lean cannot be read from arbitrary store")
    evidence = inspect_accepted_lean(
        record, repo_root=root, expected_appid=appid,
        expected_title=expected_title, now=now,
        expected_ttl_days=expected_ttl_days,
        offline_fixture=offline_fixture, stage="reader")
    return "fresh", evidence["binding"]

# A separate *sandbox-only* grant. This never enables the canonical Lean flags.
SANDBOX_GRANT = ROOT / "config/dossier_notes_v2_isolated_lean_acceptance.json"


def require_isolated_sandbox_writer(repo_root, *, trial_id, marker_commit,
                                    item_commits, issuer):
    """Fail closed on the exact user-approved six, before any cache/receipt write.

    Executed only by the existing serialized GitHub batch writer. It does not
    mint GitHub authority, accept typed transport as quality, or bypass the
    full independent Lean validator.
    """
    grant = json.loads(SANDBOX_GRANT.read_text(encoding="utf-8"))
    if (grant.get("schema") != "DOSSIER-NOTES-V2-ISOLATED-LEAN-ACCEPTANCE-V1"
            or grant.get("version") != 1 or grant.get("owner") != "github_control_plane"
            or grant.get("isolated_only") is not True
            or grant.get("single_owner_first_attempt_only") is not True
            or grant.get("exact_six_atomic_persistence") is not True
            or grant.get("canonical_main_acceptance") is not False
            or grant.get("production_enabled") is not False
            or grant.get("deep_enabled") is not False
            or grant.get("automatic_retry") is not False
            or trial_id != grant.get("trial_id")
            or marker_commit != grant.get("marker_commit")
            or issuer.get("authorization_commit") != grant.get("authorization_commit")
            or str(issuer.get("github_authorization_run_id"))
               != grant.get("owner_source_actions_run_id")
            or issuer.get("request_commit") != grant.get("original_request_commit")
            or grant.get("writer_workflow") !=
               ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml"):
        raise ValueError("unapproved Lean sandbox writer trial or owner source")
    policy = _policy()
    if any(policy["lean_" + stage + "_enabled"] for stage in ("writer", "reader", "deep")):
        raise ValueError("sandbox Lean requires all canonical/Deep gates OFF")
    items = grant.get("items")
    if (not isinstance(items, list) or len(items) != 6
            or len({x.get("appid") for x in items if isinstance(x, dict)}) != 6
            or type(item_commits) is not dict
            or set(item_commits) != {x["appid"] for x in items}):
        raise ValueError("Lean sandbox must bind exactly six frozen candidates")
    frozen = grant.get("frozen_sandbox_head")
    if not isinstance(frozen, str) or not _SHA.fullmatch(frozen):
        raise ValueError("invalid exact pre-acceptance sandbox HEAD")
    root = Path(repo_root).resolve()
    actual = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, check=False, text=True,
    )
    if actual.returncode or actual.stdout.strip() != frozen:
        raise ValueError("Lean sandbox must equal exact frozen pre-acceptance HEAD")
    from dossier_two_stage_staging import json_at
    auth = json_at(root, grant["authorization_commit"],
                   "data/control/dossier_notes_v2/authorizations/" + trial_id + ".json")
    if (auth.get("sandbox_writer_authorized") is not True
            or auth.get("canonical_acceptance") is not False
            or auth.get("production_authorized") is not False
            or auth.get("request_commit") != grant["original_request_commit"]):
        raise ValueError("GitHub owner did not authorize exact sandbox writer")
    for row in items:
        appid = row["appid"]
        pair = item_commits[appid]
        if (type(pair) is not dict
                or pair != {k: row[k] for k in ("research_commit", "assembly_commit")}
                or type(row.get("title")) is not str
                or type(row.get("group_sequence")) is not int
                or not re.fullmatch(r"batch-[0-9a-f]{24}", str(row.get("assignment_id")))):
            raise ValueError("Lean AppID/edition/immutable commits differ from frozen six")
        path = (
            "data/control/dossier_notes_v2/receipts/" + trial_id
            + "/g" + str(row["group_sequence"]).zfill(6) + "/"
            + appid + "--" + row["assignment_id"] + "--assembly.json"
        )
        observed = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD:" + path],
            capture_output=True, check=False, text=True,
        )
        if (observed.returncode or observed.stdout.strip() !=
                row.get("typed_assembly_receipt_blob_sha")):
            raise ValueError("Lean original typed Assembly transport changed: " + appid)
        # This is a one-use sandbox publication, not a repeatable acceptance API.
        store = root / ("data/control/dossier_notes_v2/batch_pilot_store/"
                        + trial_id + "/App_" + appid + ".json")
        receipt = root / ("data/control/dossier_notes_v2/batch_pilot_accepted/"
                          + trial_id + "/g"
                          + str(row["group_sequence"]).zfill(6) + "/"
                          + appid + "--" + row["assignment_id"] + ".json")
        if store.exists() or receipt.exists():
            raise ValueError("Lean sandbox acceptance already published or collided")
    return {row["appid"]: row for row in items}
