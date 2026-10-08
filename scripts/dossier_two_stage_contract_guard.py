#!/usr/bin/env python3
"""P1 offline-only contract fixture guard. NOT a GitHub staging/ingest validator.

This module cannot confer canonical acceptance, authorize retry or consume an
attempt. P2 must implement GitHub-owned immutable Git provenance checks before
any two-stage runtime can be enabled.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import parse_qsl, urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
CONTRACT = CONFIG / "dossier_two_stage_interfaces_contract.json"
FILES = {
    "research": "dossier_research_package_v1.schema.json",
    "research_receipt": "dossier_research_acceptance_receipt_v1.schema.json",
    "assembly_assignment": "dossier_assembly_assignment_v1.schema.json",
    "assembly_result": "dossier_assembly_result_v1.schema.json",
    "assembly_receipt": "dossier_assembly_receipt_v1.schema.json",
}
DIMENSIONS = (
    "core_play_mechanics", "controls_game_feel",
    "progression_development_unlocks", "variety_repetition_over_time",
    "difficulty_mastery_learning_friction", "pacing_structure_direction",
    "exploration_mission_activity_structure", "multiplayer_coop_dependence",
    "story_characters_identity_hooks", "recurring_strengths",
    "recurring_complaints_tradeoffs", "technical_performance_localization_regional",
)
PLAYER_SOURCES = {
    "steam_reviews", "steam_community", "reddit", "forum",
    "store_user_reviews", "community_discussion", "other_player_feedback",
}
FORBIDDEN_KEYS = {
    "username", "displayname", "author", "authorid", "userid", "steamid",
    "steamaccountid", "accountid", "profile", "profileid", "profileurl",
    "authorhash", "userhash", "rawtext", "rawreview", "rawreviews",
    "reviewbody", "postbody", "commentbody", "snippet", "excerpt",
    "quote", "quotes", "reviewtext", "usernames", "authors", "body",
}
PRIVATE_QUERY_KEYS = {
    "user", "userid", "user_id", "username", "author", "author_id",
    "profile", "profile_id", "steamid", "q", "query", "text", "body",
}
PRIVATE_PATH = re.compile(r"/(?:id|profiles?|users?|u|authors?)/[^/]+(?:/|$)", re.I)
PRIVATE_TEXT = re.compile(
    r"(?i)(?:\b(?:username|display[ _-]?name|author|profile)\s*[:=]|"
    r"(?<![a-z0-9_])@[a-z0-9_][a-z0-9_.-]{1,}|"
    r"\b(?:u|user)/[a-z0-9_][a-z0-9_.-]{1,})"
)
RAW_QUOTE = re.compile(r'["“”«»]')


def _fail(message):
    raise ValueError(message)


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canonical_sha256(document):
    return hashlib.sha256(
        json.dumps(document, sort_keys=True, ensure_ascii=False,
                   separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()


def check_gate():
    cfg = _load(CONTRACT)
    if (cfg.get("schema") != "DOSSIER-TWO-STAGE-INTERFACES-V1"
            or cfg.get("active") is not False
            or cfg.get("authoritative") is not False
            or cfg.get("authorized_for_semantic_execution") is not False
            or cfg.get("authorized_for_staging_or_claims") is not False
            or cfg.get("authorized_for_canonical_ingest") is not False
            or cfg.get("canonical_production_authority", {}).get("mode")
                != "one_stage_dossier_only"):
        _fail("two-stage inactive gate is not securely closed")
    return cfg


def schema_validate(document, name):
    check_gate()
    schema = _load(CONFIG / FILES[name])
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(
        schema, format_checker=FormatChecker()
    ).iter_errors(document), key=lambda e: str(list(e.absolute_path)))
    if errors:
        _fail(f"{name} schema error: {errors[0].message}")
    return document


def _privacy(value):
    if isinstance(value, dict):
        for key, val in value.items():
            normalized = re.sub(r"[^a-z0-9]", "", key.lower())
            if normalized in FORBIDDEN_KEYS:
                _fail("private or raw-content field: " + key)
            _privacy(val)
    elif isinstance(value, list):
        for item in value:
            _privacy(item)
    elif isinstance(value, str):
        if len(value) > 1200 or PRIVATE_TEXT.search(value):
            _fail("private or oversized text")
        # Neutral findings are safe paraphrases; raw excerpts cannot be stored
        # as direct quotations in this new Research interface.
        if RAW_QUOTE.search(value):
            _fail("quoted text is forbidden in Research payload")


def _locator(loc):
    if loc is None:
        return None
    if "public_ref" in loc:
        value = loc["public_ref"].lower()
        if any(token in value for token in ("steamid", "username", "profile", "/u/", "/user/")):
            _fail("private public_ref")
        return "ref:" + value
    url = urlsplit(loc["url"])
    if (url.scheme != "https" or not url.hostname or url.username
            or url.password or PRIVATE_PATH.search(url.path)
            or url.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
            or any(part in url.hostname.lower() for part in (".local", ".internal"))):
        _fail("unsafe/private URL locator")
    if any(key.lower() in PRIVATE_QUERY_KEYS for key, _ in parse_qsl(url.query, keep_blank_values=True)):
        _fail("private URL query")
    return "url:" + url.geturl().lower()


def validate_research(document, *, expected_assignment=None):
    schema_validate(document, "research")
    _privacy(document)
    a = document["assignment"]
    if expected_assignment is not None and a != expected_assignment:
        _fail("research frozen assignment binding mismatch")
    source = {}
    physical = set()
    for row in document["sources"]:
        ref = row["ref"]
        if ref in source:
            _fail("duplicate source ref")
        source[ref] = row
        key = _locator(row["locator"])
        if row["normalized_locator"] is not None:
            normalized = row["normalized_locator"]
            if normalized.startswith("https://"):
                _locator({"url": normalized})
            elif normalized.startswith("ref:"):
                _locator({"public_ref": normalized[4:]})
            else:
                _fail("normalized locator not safely typed")
        dedupe = row["physical_source_identity"] or key
        if dedupe in physical:
            _fail("duplicate physical source / alias")
        physical.add(dedupe)
        if row["player_feedback"] and row["source_type"] not in PLAYER_SOURCES:
            _fail("context-only source cannot be feedback")
        bind = row["exact_product_binding"]
        if bind:
            if bind["appid"] is not None and bind["appid"] != a["appid"]:
                _fail("source exact AppID mismatch")
            if bind["title"] is not None and bind["title"] != a["title"]:
                _fail("source exact title mismatch")
    ident = document["identity"]
    if ident["resolution"] == "resolved":
        if not ident["resolved_title"] or ident["original_work_release_year"] is None:
            _fail("resolved identity lacks factual original release year")
        if ident["resolved_title"] != a["title"]:
            _fail("resolved title mismatches descriptor")
        if not ident["identity_source_refs"]:
            _fail("resolved identity lacks actual source")
    for ref in ident["identity_source_refs"]:
        if ref not in source or source[ref]["evidence_role_hint"] != "identity":
            _fail("broken/nonidentity source reference")
    feedback = {}
    for row in document["observed_feedback"]:
        ref = row["ref"]
        if ref in feedback:
            _fail("duplicate feedback ref")
        feedback[ref] = row
        parent = source.get(row["parent_source_ref"])
        if not parent or not parent["player_feedback"] or parent["source_type"] not in PLAYER_SOURCES:
            _fail("invalid feedback parent source")
        if row["exact_product_binding_ref"] != row["parent_source_ref"]:
            _fail("feedback exact-product source must equal parent")
        if parent["exact_product_binding"] is None or parent["exact_product_binding"]["basis"] == "unresolved":
            _fail("feedback parent requires observable exact-product binding")
        if row["language"] == "russian" and parent["language"] not in ("russian", "mixed"):
            _fail("russian feedback cannot descend from non-russian parent")
        if row["language"] == "non_russian" and parent["language"] not in ("non_russian", "mixed"):
            _fail("non-russian feedback cannot descend from russian parent")
        if row["acquisition_mode"] == "stable_item" and row["item_locator"] is None:
            _fail("stable-item feedback requires observed item locator")
        if row["acquisition_mode"] == "search_result_observation":
            if parent["observed_mode"] != "search_representation" or parent["feedback_surface_mode"] != "search_result_representation":
                _fail("search-result feedback bound to wrong surface")
        if row["acquisition_mode"] == "inspected_collection_item":
            if parent["observed_mode"] != "inspected_collection" or parent["feedback_surface_mode"] != "concrete_item_collection":
                _fail("collection item bound to wrong surface")
        _locator(row["item_locator"])
    findings = {}
    for row in document["findings"]:
        if row["ref"] in findings:
            _fail("duplicate finding ref")
        findings[row["ref"]] = row
        if len(row["support_feedback_refs"]) != len(set(row["support_feedback_refs"])):
            _fail("duplicate finding feedback support")
        if any(ref not in feedback for ref in row["support_feedback_refs"]):
            _fail("broken support feedback ref")
        if any(ref not in source for ref in row["contextual_source_refs"]):
            _fail("broken contextual source ref")
        if len(row["dimension_hints"]) != len(set(row["dimension_hints"])):
            _fail("duplicate dimension hints")
    audit = document["research_audit"]
    survey = audit["dimension_survey"]
    if {r["dimension"] for r in survey} != set(DIMENSIONS):
        _fail("12 dimensions must be unique and complete")
    for row in survey:
        if len(set(row["finding_refs"])) != len(row["finding_refs"]):
            _fail("duplicate dimension finding ref")
        if any(ref not in findings for ref in row["finding_refs"]):
            _fail("broken dimension finding ref")
        if row["investigation_state"] == "supported" and not row["finding_refs"]:
            _fail("supported dimension requires actual finding")
    gaps = set()
    for row in audit["unresolved_gaps"]:
        if row["gap_id"] in gaps:
            _fail("duplicate gap id")
        gaps.add(row["gap_id"])
        if any(ref not in source for ref in row["source_refs"]):
            _fail("gap refers to missing source")
    if audit["completeness"] == "assembly_ready" and any(
            x["material"] for x in audit["unresolved_gaps"]):
        _fail("material gap cannot be called assembly-ready")
    if audit["completeness"] == "assembly_ready" and not findings:
        _fail("empty evidence cannot be assembly-ready")
    return canonical_sha256(document)


def validate_research_receipt(receipt, package):
    schema_validate(receipt, "research_receipt")
    if receipt["assignment"] != package["assignment"]:
        _fail("accepted Research receipt assignment mismatch")
    if receipt["research_contract_sha256"] != package["assignment"]["research_contract_sha256"]:
        _fail("accepted Research contract binding mismatch")
    if receipt["research_package_sha256"] != validate_research(package):
        _fail("accepted Research package hash mismatch")
    a = package["assignment"]
    expected_path = (
        f"data/ai_inbox/dossier_research/{a['snapshot_id']}/"
        f"g{a['group_sequence']:06d}/{a['appid']}--{a['assignment_id']}.json"
    )
    if receipt["research_package_path"] != expected_path:
        _fail("accepted Research transport path mismatch")
    ident = package["identity"]
    got = receipt["accepted_identity"]
    if (got["appid"] != package["assignment"]["appid"]
            or got["title"] != package["assignment"]["title"]
            or got["original_work_release_year"] != ident["original_work_release_year"]
            or got["identity_resolution"] != ident["resolution"]):
        _fail("accepted original work / release identity mismatch")
    return receipt


def validate_assembly_assignment(work, package):
    schema_validate(work, "assembly_assignment")
    receipt = work["accepted_research"]
    validate_research_receipt(receipt, package)
    if work["original_research_assignment"] != package["assignment"]:
        _fail("Assembly source assignment mismatch")
    if work["canonical_dossier_target"]["canonical_worker_binding_sha256"] != canonical_sha256(
        package["assignment"]["web_evidence_contract_binding"]):
        _fail("Assembly canonical V2 binding mismatch")
    if work["output_path"] != (
        f"data/ai_inbox/dossier_assembly/{package['assignment']['snapshot_id']}/"
        f"g{package['assignment']['group_sequence']:06d}/"
        f"{package['assignment']['appid']}--{work['assembly_assignment_id']}.json"
    ):
        _fail("Assembly output path differs from GitHub-bound exact path")
    return work


def validate_assembly_result(result, work, package):
    schema_validate(result, "assembly_result")
    validate_assembly_assignment(work, package)
    for key in ("assembly_assignment_id", "original_research_assignment",
                "assembly_marker_anchor_commit", "assembly_marker_nonce",
                "assembly_contract_sha256", "assembly_prompt_sha256",
                "canonical_dossier_target", "output_path"):
        if result[key] != work[key]:
            _fail("Stage B immutable binding mismatch: " + key)
    if result["accepted_research_package_sha256"] != work["accepted_research"]["research_package_sha256"]:
        _fail("Stage B stale/unaccepted Research package hash")
    if result["accepted_research_receipt_blob_sha"] != work["accepted_research_receipt_blob_sha"]:
        _fail("Stage B accepted receipt authority mismatch")
    if result["payload"]["status"] != result["outcome"]:
        _fail("ambiguous Assembly typed outcome")
    if result["outcome"] == "assembled_candidate_ready":
        dossier = result["payload"]["dossier"]
        if (dossier["appid"] != package["assignment"]["appid"]
                or dossier["title"] != package["assignment"]["title"]):
            _fail("Assembly candidate target identity mismatch")
    sources = {row["ref"] for row in package["sources"]}
    gaps = {row["gap_id"]: row for row in package["research_audit"]["unresolved_gaps"]}
    for op in result["supplemental_operations"]:
        gap = gaps.get(op["gap_id"])
        if gap is None or op["source_ref"] not in sources:
            _fail("Assembly unsolicited new research scope")
        if op["missing_field_or_dimension"] != gap["field_or_dimension"]:
            _fail("Assembly gap identity mismatch")
        look = op["narrow_gap_lookup"]
        if look is not None:
            r = op["exact_source_revisit"]
            if r["status"] != "genuinely_absent" or r["observed_fact_present"]:
                _fail("narrow research skipped exact-source-first requirement")
            if (look["gap_id"] != op["gap_id"]
                    or look["missing_field_or_dimension"] != gap["field_or_dimension"]
                    or look["appid"] != package["assignment"]["appid"]
                    or look["original_work_title"] != package["assignment"]["title"]
                    or look["original_work_release_year"] != package["identity"]["original_work_release_year"]):
                _fail("narrow lookup exact work identity mismatch")
    return result


def validate_assembly_receipt(receipt, result, work):
    schema_validate(receipt, "assembly_receipt")
    if (receipt["assembly_assignment_id"] != work["assembly_assignment_id"]
            or receipt["original_research_assignment"] != work["original_research_assignment"]
            or receipt["assembly_outcome"] != result["outcome"]
            or receipt["accepted_research_package_sha256"] != result["accepted_research_package_sha256"]
            or receipt["assembly_result_path"] != work["output_path"]
            or receipt["assembly_result_sha256"] != canonical_sha256(result)):
        _fail("Stage B receipt/result binding mismatch")
    return receipt
