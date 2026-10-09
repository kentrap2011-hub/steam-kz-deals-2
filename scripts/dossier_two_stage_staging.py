#!/usr/bin/env python3
"""Inactive P2 GitHub control-plane *planning* for Research -> Assembly.

No CLI, production inbox scanner, workflow trigger, canonical cache write, retry
engine or implicit activation. All input authority is resolved from immutable Git
commits. The returned create-only file maps need a separately authorized, later
GitHub writer integration; tests may commit them in disposable Git fixtures.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from jsonschema import Draft202012Validator, FormatChecker

from dossier_two_stage_contract_guard import (
    CONFIG, ROOT, canonical_sha256, check_gate, schema_validate,
    validate_research, validate_research_receipt, validate_assembly_assignment,
)

H40 = re.compile(r"^[0-9a-f]{40}$")
AID = re.compile(r"^[a-z0-9][a-z0-9._-]{7,127}$")
H64 = re.compile(r"^[0-9a-f]{64}$")
REVISION = "dossier-two-stage-p2-v1"
RESEARCH_PREPARED = "data/control/dossier_research_assignments"
RESEARCH_MARKER = "data/control/dossier_research_run_starts"
ASSEMBLY_PLAN = "data/control/dossier_assembly_plans"
ASSEMBLY_MARKER = "data/control/dossier_assembly_run_starts"
STATE_ROOT = "data/control/dossier_two_stage_state"
TRACKING = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
            "fbclid", "gclid", "mc_cid", "mc_eid", "ref", "referrer", "tracking"}
FROZEN_MARKER_KEYS = {"research_marker_anchor_commit", "research_marker_nonce"}


def fail(reason):
    raise ValueError("inactive dossier staging: " + reason)


def gate():
    c = check_gate()
    extra = json.loads((CONFIG / "dossier_two_stage_staging_contract.json").read_text("utf-8"))
    if (extra.get("schema") != "DOSSIER-TWO-STAGE-STAGING-P2-V1"
            or extra.get("active") is not False
            or extra.get("executable_in_production") is not False
            or extra.get("authoritative") is not False
            or extra.get("github_owner") != "github_actions_control_plane"):
        fail("inactive P2 gate or owner was changed")
    return c, extra


def strict_json(raw):
    def no_dupes(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                fail("duplicate JSON key")
            d[k] = v
        return d
    return json.loads(raw.decode("utf-8"), object_pairs_hook=no_dupes,
                      parse_constant=lambda _: fail("invalid JSON numeric constant"))


def git(repo, *args, input_bytes=None, required=True):
    cp = subprocess.run(["git", *args], cwd=str(Path(repo).resolve()),
                        input=input_bytes, stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE, check=False)
    if required and cp.returncode:
        fail("Git provenance check failed")
    return cp


def parent(repo, commit):
    if not isinstance(commit, str) or not H40.fullmatch(commit):
        fail("invalid immutable commit ref")
    words = git(repo, "rev-list", "--parents", "-n", "1", commit).stdout.decode().split()
    if len(words) != 2 or words[0] != commit:
        fail("expected exactly one Git parent")
    return words[1]


def file_at(repo, commit, path):
    if not isinstance(path, str) or not path.startswith("data/") and not path.startswith("config/"):
        fail("path outside explicitly allowed immutable namespaces")
    if ".." in Path(path).parts or path.startswith("/"):
        fail("unsafe Git object path")
    return git(repo, "show", f"{commit}:{path}").stdout


def json_at(repo, commit, path):
    return strict_json(file_at(repo, commit, path))


def exists(repo, commit, path):
    return git(repo, "cat-file", "-e", f"{commit}:{path}", required=False).returncode == 0


def blob(repo, commit, path):
    result = git(repo, "rev-parse", f"{commit}:{path}").stdout.decode().strip()
    if not H40.fullmatch(result):
        fail("Git blob binding missing")
    return result


def blob_for(data):
    prefix = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(prefix + data).hexdigest()


def first_parent_contains(repo, older, newer):
    if older == newer:
        return True
    return older in git(repo, "rev-list", "--first-parent", newer).stdout.decode().splitlines()


def changes(repo, commit):
    p = parent(repo, commit)
    rows = git(repo, "diff-tree", "--no-commit-id", "--name-status", "-r", commit).stdout.decode().splitlines()
    return p, [(line.split("\t", 1)[0], line.split("\t", 1)[1]) for line in rows if "\t" in line]


def require_only_new(repo, commit, paths):
    p, entries = changes(repo, commit)
    if sorted(entries) != sorted([("A", x) for x in paths]):
        fail("create-only Git introduction changed unexpected paths or overwrote an artifact")
    for path in paths:
        if exists(repo, p, path):
            fail("expected create-only file already existed in Git parent")
    return p


def marker_context(repo, marker_commit, kind):
    p, entries = changes(repo, marker_commit)
    if len(entries) != 1 or entries[0][0] != "A":
        fail("run-start marker must be the only create-only commit change")
    marker_path = entries[0][1]
    prefix = RESEARCH_MARKER if kind == "research" else ASSEMBLY_MARKER
    m = re.fullmatch(re.escape(prefix) + r"/([0-9a-f]{32})\.json", marker_path)
    if not m:
        fail("wrong marker namespace or nonce")
    nonce = m.group(1)
    doc = json_at(repo, marker_commit, marker_path)
    if doc != {
        "schema": f"DOSSIER-{kind.upper()}-RUN-START-MARKER-V1",
        "schema_version": 1, "run_start_nonce": nonce,
    }:
        fail("marker contents or version mismatch")
    return p, nonce


def prepared_path(a):
    return (f"{RESEARCH_PREPARED}/{a['snapshot_id']}/"
            f"g{a['group_sequence']:06d}/{a['appid']}--{a['assignment_id']}.json")


def receipt_paths(a):
    base = f"{a['snapshot_id']}/g{a['group_sequence']:06d}/{a['appid']}--{a['assignment_id']}"
    return {
        "candidate": f"data/ai_inbox/dossier_research/{base}.json",
        "accepted": f"data/control/dossier_research_accepted/{base}.json",
        "rejected": f"data/control/dossier_research_rejections/{base}.json",
        "state": f"{STATE_ROOT}/{base}--research.json",
        "assembly_state": f"{STATE_ROOT}/{base}--assembly.json",
        "assembly_plan": f"{ASSEMBLY_PLAN}/{base}.json",
    }


def frozen_descriptor(repo, revision, a):
    path = ("data/production/pre_ai/taste_steam_review_dossier_worker_groups/"
            f"{a['snapshot_id']}/g{a['group_sequence']:06d}.json")
    d = json_at(repo, revision, path)
    i = a["item_index"]
    identity = {
        k: d[k] for k in (
            "snapshot_id", "prepared_required_sha256", "sequence",
            "start_index", "end_index_exclusive", "appids", "items_sha256",
            "scope_source", "source_queue_sha256"
        )
    }
    if (d.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORKER-GROUP-V1"
            or d.get("schema_version") != 1
            or d.get("sequence") != a["group_sequence"]
            or i >= len(d["items"]) or len(d["items"]) > 3
            or d["end_index_exclusive"] - d["start_index"] != len(d["items"])
            or d["items_sha256"] != canonical_sha256(d["items"])
            or d["group_sha256"] != canonical_sha256(identity)
            or d["appids"] != [str(x["appid"]) for x in d["items"]]
            or d["items"][i]["appid"] != a["appid"]
            or d["items"][i]["title"] != a["title"]):
        fail("frozen descriptor identity/group hash does not match")
    for left, right in [
        ("snapshot_id", "snapshot_id"), ("prepared_required_sha256", "prepared_required_sha256"),
        ("group_plan_sha256", "group_plan_sha256"), ("group_sha256", "group_sha256"),
        ("items_sha256", "items_sha256"), ("scope_source", "scope_source"),
        ("source_queue_sha256", "source_queue_sha256"),
        ("web_evidence_contract_binding", "web_evidence_contract_binding"),
    ]:
        if d[left] != a[right]:
            fail("immutable descriptor mismatch: " + left)
    idx = json_at(repo, revision, "data/production/pre_ai/taste_steam_review_dossier_worker_index.json")
    if (idx.get("schema") != "TASTE-STEAM-REVIEW-DOSSIER-WORKER-INDEX-V2"
            or idx.get("schema_version") != 2
            or idx.get("snapshot_id") != a["snapshot_id"]
            or idx.get("group_plan_sha256") != a["group_plan_sha256"]
            or idx.get("prepared_required_sha256") != a["prepared_required_sha256"]
            or a["group_sequence"] not in idx.get("pending_group_sequences", [])):
        fail("frozen GitHub-owned index did not authorize pending Research work")
    return d


def research_authority(repo, marker_commit, prepared_work_path):
    gate()
    revision, nonce = marker_context(repo, marker_commit, "research")
    prepared = json_at(repo, revision, prepared_work_path)
    if not isinstance(prepared, dict):
        fail("GitHub-prepared assignment missing")
    a = {**prepared, "research_marker_anchor_commit": marker_commit, "research_marker_nonce": nonce}
    if prepared_work_path != prepared_path(a):
        fail("GitHub-prepared assignment path mismatch")
    schema = json.loads((CONFIG / "dossier_research_package_v1.schema.json").read_text("utf-8"))
    if canonical_sha256(schema) != a.get("research_contract_sha256"):
        fail("GitHub-prepared Research schema digest stale")
    if canonical_sha256(schema) != canonical_sha256(
            json_at(repo, revision, "config/dossier_research_package_v1.schema.json")):
        fail("frozen Research schema not identical to P2 validator schema")
    if set(prepared) != set(schema["properties"]["assignment"]["required"]) - FROZEN_MARKER_KEYS:
        fail("invalid GitHub-prepared assignment field set")
    schema_validate({
        "schema": "DOSSIER-RESEARCH-PACKAGE-V1", "schema_version": 1,
        "assignment": a,
        # other fields are validated separately when package is received
        "identity": {"resolved_title": None, "original_work_release_year": None,
                     "resolution": "unresolved", "corroborators": [],
                     "identity_source_refs": [], "ambiguity_notes": None},
        "sources": [], "observed_feedback": [], "findings": [],
        "research_audit": {
            "russian_attempt_observed": "searched_no_existence_signal",
            "russian_existence_signal": "unresolved",
            "dimension_survey": [
                {"dimension": dimension, "finding_refs": [], "investigation_state": "material_gap"}
                for dimension in (
                    "core_play_mechanics", "controls_game_feel",
                    "progression_development_unlocks", "variety_repetition_over_time",
                    "difficulty_mastery_learning_friction", "pacing_structure_direction",
                    "exploration_mission_activity_structure", "multiplayer_coop_dependence",
                    "story_characters_identity_hooks", "recurring_strengths",
                    "recurring_complaints_tradeoffs", "technical_performance_localization_regional",
                )
            ], "strengths_investigated": False, "weaknesses_tradeoffs_investigated": False,
            "used_distinct_route_classes": [],
            "required_route_state": {k: "unresolved" for k in (
                "identity", "russian", "source_diversification", "temporal")},
            "unresolved_gaps": [], "completeness": "research_incomplete",
            "completion_basis": None,
        },
        "package_hash_algorithm": "github_accepted_canonical_json_sha256_sorted_keys_compact_utf8",
    }, "research")
    frozen_descriptor(repo, revision, a)
    return a


def validate_physical_sources(package):
    def canonical_locator(loc):
        if "public_ref" in loc:
            return "ref:" + loc["public_ref"].lower()
        url = urlsplit(loc["url"])
        host = url.hostname.lower().rstrip(".")
        if url.port not in (None, 443) or not host or url.fragment:
            fail("unsafe noncanonical source authority or fragment")
        host = host[4:] if host.startswith("www.") else host
        path = re.sub(r"/+$", "", url.path) or "/"
        query = urlencode(sorted((k, v) for k, v in parse_qsl(url.query, keep_blank_values=True)
                                 if k.lower() not in TRACKING))
        return urlunsplit(("https", host, path, query, ""))
    physical = set()
    for s in package["sources"]:
        c = canonical_locator(s["locator"])
        if s["normalized_locator"] not in (None, c, s["locator"].get("url")):
            fail("unverifiable normalized physical locator")
        if s["physical_source_identity"] not in (None, c, s["locator"].get("url")):
            fail("unverifiable physical-source dedupe identity")
        if c in physical:
            fail("duplicate canonical physical source identity")
        physical.add(c)
        domain = None if "public_ref" in s["locator"] else urlsplit(c).hostname
        if s["domain"] is not None and s["domain"] != domain:
            fail("source domain differs from verified normalized hostname")


def check_schema(doc, filename):
    schema = json.loads((CONFIG / filename).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(doc))
    if errors:
        fail("invalid GitHub-owned staging receipt/state shape")
    return doc


def no_collisions(repo, files, at="HEAD"):
    # Readers detect already-introduced stage files; caller/writer must also
    # serialize and recheck under the shared canonical-writer lock at commit.
    for p in files:
        if exists(repo, at, p) or (Path(repo) / p).exists():
            fail("create-only collision or replay: " + p)


def state(a, status, source_commit, *, hash_value=None, accepted_blob=None,
          phase="research", assembly_id=None):
    return {
        "schema": "DOSSIER-TWO-STAGE-STAGING-STATE-V1", "schema_version": 1,
        "owner": "github_control_plane", "phase": phase, "assignment": copy.deepcopy(a),
        "research_status": status,
        "assembly_status": ("assigned" if phase == "assembly"
                            else "waiting_for_accepted_research" if status == "accepted_structural_evidence"
                            else "not_authorized"),
        "research_package_sha256": hash_value, "research_receipt_blob_sha": accepted_blob,
        "assembly_assignment_id": assembly_id, "source_commit": source_commit,
        "canonical_dossier_accepted": False, "deep_eligibility_issued": False,
        "normal_first_pass_attempt_consumed": False, "retry_authorized": False,
    }


def bytes_json(doc):
    return (json.dumps(doc, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def receive_research(repo, *, marker_commit, prepared_work_path, package_commit):
    """Return two new GitHub-owned files: receipt + immutable Research state.

    Rejected semantic/schema transport is recorded only after authoritative
    create-only Git introduction and frozen GitHub work have been established.
    """
    a = research_authority(repo, marker_commit, prepared_work_path)
    paths = receipt_paths(a)
    package_path = paths["candidate"]
    p = require_only_new(repo, package_commit, [package_path])
    if not first_parent_contains(repo, marker_commit, p):
        fail("Research transport did not descend on marker's first-parent history")
    raw = file_at(repo, package_commit, package_path)
    bsha = blob(repo, package_commit, package_path)
    if blob_for(raw) != bsha:
        fail("Research candidate Git blob/hash inconsistent")
    status, reason, package_hash = "rejected_invalid", "invalid_json", None
    package = None
    try:
        package = strict_json(raw)
    except (UnicodeError, json.JSONDecodeError, ValueError):
        pass
    if isinstance(package, dict):
        try:
            validate_research(package, expected_assignment=a)
            validate_physical_sources(package)
            completeness = package["research_audit"]["completeness"]
            if completeness == "assembly_ready" and package["identity"]["resolution"] == "resolved":
                status, reason = "accepted_structural_evidence", None
                package_hash = canonical_sha256(package)
            elif completeness == "semantic_exhausted":
                status, reason = "semantic_exhausted", "semantic_exhaustion_not_canonical"
            else:
                status, reason = "research_incomplete", "research_not_assembly_ready"
        except ValueError as exc:
            why = str(exc).lower()
            reason = ("invalid_binding" if "binding" in why or "assignment" in why
                      else "invalid_privacy_or_provenance" if any(w in why for w in (
                          "private", "privacy", "locator", "duplicate", "source",
                          "feedback", "parent", "domain"))
                      else "invalid_schema")
    if status == "accepted_structural_evidence":
        receipt = {
            "schema": "DOSSIER-RESEARCH-ACCEPTANCE-RECEIPT-V1",
            "schema_version": 1, "status": "accepted_structural_evidence_not_canonical_dossier",
            "owner": "github_control_plane", "assignment": copy.deepcopy(a),
            "research_package_path": package_path, "research_package_sha256": package_hash,
            "research_package_blob_sha": bsha, "research_package_git_commit": package_commit,
            "validation_revision": REVISION, "research_schema_id": "DOSSIER-RESEARCH-PACKAGE-V1",
            "research_contract_sha256": a["research_contract_sha256"],
            "accepted_identity": {
                "appid": a["appid"], "title": a["title"],
                "original_work_release_year": package["identity"]["original_work_release_year"],
                "identity_resolution": package["identity"]["resolution"],
            },
            "canonical_acceptance": False, "deep_eligibility_issued": False,
        }
        validate_research_receipt(receipt, package)
        receipt_path = paths["accepted"]
    else:
        receipt = {
            "schema": "DOSSIER-RESEARCH-REJECTION-RECEIPT-V1",
            "schema_version": 1, "owner": "github_control_plane", "assignment": a,
            "status": status, "reason_code": reason,
            "research_package_path": package_path,
            "raw_content_sha256": hashlib.sha256(raw).hexdigest(),
            "research_package_blob_sha": bsha, "research_package_git_commit": package_commit,
            "validation_revision": REVISION, "canonical_acceptance": False,
            "normal_first_pass_attempt_consumed": False, "retry_authorized": False,
            "deep_eligibility_issued": False,
        }
        check_schema(receipt, "dossier_research_rejection_receipt_v1.schema.json")
        receipt_path = paths["rejected"]
    receipt_blob = blob_for(bytes_json(receipt))
    st = state(a, status, package_commit, hash_value=package_hash,
               accepted_blob=receipt_blob if status == "accepted_structural_evidence" else None)
    check_schema(st, "dossier_two_stage_staging_state_v1.schema.json")
    files = {receipt_path: receipt, paths["state"]: st}
    # Reject replay/collision and second terminal outcome even when paths differ.
    no_collisions(repo, {paths["accepted"]: None, paths["rejected"]: None,
                         paths["state"]: None, paths["assembly_state"]: None})
    return {"status": status, "receipt_path": receipt_path,
            "receipt_blob_sha": receipt_blob, "files": files}


def assembly_authority(repo, marker_commit, plan_path):
    gate()
    frozen, nonce = marker_context(repo, marker_commit, "assembly")
    plan = json_at(repo, frozen, plan_path)
    if not isinstance(plan, dict) or set(plan) != {
        "schema", "schema_version", "research_assignment_id", "assembly_assignment_id",
        "accepted_research_package_sha256", "accepted_research_receipt_blob_sha",
        "assembly_contract_sha256", "assembly_prompt_sha256", "assembly_prompt_revision",
        "canonical_dossier_target",
    } or plan["schema"] != "DOSSIER-ASSEMBLY-GITHUB-PLAN-V1" or plan["schema_version"] != 1:
        fail("malformed GitHub-predeclared Assembly plan")
    if not AID.fullmatch(str(plan["assembly_assignment_id"])) or not AID.fullmatch(str(plan["research_assignment_id"])):
        fail("invalid Assembly plan work ids")
    for key in ("accepted_research_package_sha256", "assembly_contract_sha256",
                "assembly_prompt_sha256"):
        if not H64.fullmatch(str(plan[key])):
            fail("invalid GitHub-prepared Assembly immutable digest")
    if not H40.fullmatch(str(plan["accepted_research_receipt_blob_sha"])):
        fail("invalid GitHub-prepared Research receipt blob")
    if not isinstance(plan["assembly_prompt_revision"], str) or not plan["assembly_prompt_revision"]:
        fail("Assembly prompt revision is missing")
    return frozen, nonce, plan


def prepare_assembly(repo, *, marker_commit, plan_path, check_collisions=True):
    """Return create-only Assembly assignment + immutable state, no semantics."""
    frozen, nonce, plan = assembly_authority(repo, marker_commit, plan_path)
    # A plan can be read only after the accepted research receipt was committed
    # on this marker's first-parent history.
    a_id = plan["research_assignment_id"]
    # Its exact Research identity is looked up from the GitHub-frozen plan scope,
    # never from a worker-selected title, AppID or latest mutable work queue.
    match = re.fullmatch(re.escape(ASSEMBLY_PLAN) +
                        r"/([0-9a-f]{64})/g([0-9]{6})/([0-9]+)--([a-z0-9._-]+)\.json",
                        plan_path)
    if not match or match.group(4) != a_id:
        fail("Assembly plan path does not bind the exact Research identity")
    snapshot, seq, appid, _ = match.groups()
    base = f"{snapshot}/g{seq}/{appid}--{a_id}"
    accepted_path = f"data/control/dossier_research_accepted/{base}.json"
    research_state_path = f"{STATE_ROOT}/{base}--research.json"
    receipt = json_at(repo, frozen, accepted_path)
    st = json_at(repo, frozen, research_state_path)
    if receipt.get("schema") != "DOSSIER-RESEARCH-ACCEPTANCE-RECEIPT-V1":
        fail("Assembly cannot consume rejected Research evidence")
    a = receipt["assignment"]
    paths = receipt_paths(a)
    if (plan_path != paths["assembly_plan"] or accepted_path != paths["accepted"]
            or research_state_path != paths["state"]):
        fail("GitHub-prepared Assembly plan path mismatched Research binding")
    check_schema(st, "dossier_two_stage_staging_state_v1.schema.json")
    if (st["phase"] != "research" or st["research_status"] != "accepted_structural_evidence"
            or st["assembly_status"] != "waiting_for_accepted_research"
            or st["assignment"] != a
            or st["research_package_sha256"] != receipt["research_package_sha256"]
            or st["research_receipt_blob_sha"] != blob(repo, frozen, accepted_path)
            or plan["accepted_research_package_sha256"] != receipt["research_package_sha256"]
            or plan["accepted_research_receipt_blob_sha"] != blob(repo, frozen, accepted_path)):
        fail("unaccepted or stale Research lifecycle state/package receipt")
    introduction = receipt["research_package_git_commit"]
    package = json_at(repo, introduction, receipt["research_package_path"])
    # Validate actual immutable package provenance anew without replaying any write.
    a_check = research_authority(repo, a["research_marker_anchor_commit"],
                                 prepared_path(a))
    if a_check != a or not first_parent_contains(repo, introduction, frozen):
        fail("Research original frozen commit identity/ancestry lost")
    if blob(repo, introduction, receipt["research_package_path"]) != receipt["research_package_blob_sha"]:
        fail("Research original Git blob does not match accepted receipt")
    validate_research_receipt(receipt, package)
    if (not first_parent_contains(repo, receipt["research_package_git_commit"], frozen)
            or not first_parent_contains(repo, a["research_marker_anchor_commit"], introduction)):
        fail("Research approval is not on Assembly frozen first-parent lineage")
    if (st["source_commit"] != introduction
            or blob_for(bytes_json(receipt)) != st["research_receipt_blob_sha"]):
        fail("Research receipt/state Git bytes inconsistent")
    if plan["canonical_dossier_target"] != {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-V2", "schema_version": 2,
        "worker_schema": "TASTE-STEAM-REVIEW-DOSSIER-WORKER-SCHEMA-V2",
        "worker_schema_version": 2,
        "web_evidence_contract": "TASTE-STEAM-REVIEW-DOSSIER-WEB-EVIDENCE-CONTRACT-V2",
        "web_evidence_contract_version": 2,
        "canonical_worker_binding_sha256": canonical_sha256(a["web_evidence_contract_binding"]),
    }:
        fail("Assembly canonical target V2 binding mismatch")
    if not isinstance(plan["assembly_assignment_id"], str):
        fail("invalid GitHub-issued Assembly assignment id")
    work = {
        "schema": "DOSSIER-ASSEMBLY-ASSIGNMENT-V1", "schema_version": 1,
        "assembly_assignment_id": plan["assembly_assignment_id"],
        "original_research_assignment": a, "accepted_research": receipt,
        "accepted_research_receipt_blob_sha": blob(repo, frozen, accepted_path),
        "assembly_marker_anchor_commit": marker_commit, "assembly_marker_nonce": nonce,
        "assembly_contract_sha256": plan["assembly_contract_sha256"],
        "assembly_prompt_sha256": plan["assembly_prompt_sha256"],
        "assembly_prompt_revision": plan["assembly_prompt_revision"],
        "canonical_dossier_target": plan["canonical_dossier_target"],
        "output_path": ("data/ai_inbox/dossier_assembly/"
                        f"{snapshot}/g{seq}/{appid}--{plan['assembly_assignment_id']}.json"),
        "permitted_result_namespace": "data/ai_inbox/dossier_assembly/",
        "create_only": True,
        "canonical_acceptance_authority": "existing_github_strict_v2_validator_and_group_ingest_only",
    }
    validate_assembly_assignment(work, package)
    assign_path = (f"data/control/dossier_assembly_assignments/"
                   f"{snapshot}/g{seq}/{appid}--{plan['assembly_assignment_id']}.json")
    nstate = state(a, "accepted_structural_evidence", introduction,
                   hash_value=receipt["research_package_sha256"],
                   accepted_blob=blob(repo, frozen, accepted_path),
                   phase="assembly", assembly_id=plan["assembly_assignment_id"])
    check_schema(nstate, "dossier_two_stage_staging_state_v1.schema.json")
    if check_collisions:
        no_collisions(repo, {assign_path: None, paths["assembly_state"]: None})
    return {"status": "assigned", "assignment_path": assign_path,
            "files": {assign_path: work, paths["assembly_state"]: nstate}}
