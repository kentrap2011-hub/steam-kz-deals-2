#!/usr/bin/env python3
"""Inactive, versioned Notes V2 -> autonomous Assembly GitHub control-plane helpers.

V1 entrypoints, original immutable trial, existing strict Dossier group writer and
production are untouched. No network, Git writes, retry, scheduler or semantics.
Future workers provide claims; only trusted GitHub immutable provenance and the
existing final validator can authorize a prospective item for group acceptance.
"""
import hashlib
import ipaddress
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qsl
from jsonschema import Draft202012Validator

from dossier_two_stage_staging import (
    blob, blob_for, file_at, first_parent_contains, git, json_at,
    require_only_new, strict_json, exists,
)
from dossier_two_stage_contract_guard import _privacy
from taste_steam_review_dossier_strict import validate_dossier_strict

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
CONTRACT_PATH = CONFIG / "dossier_research_notes_v2_contract.json"
ORIGINAL_BUFFER_PATH = CONFIG / "dossier_notes_v2_pinned_original_research_buffer_v1.json"
HEX40 = re.compile(r"^[a-f0-9]{40}$")
NONCE = re.compile(r"^[a-f0-9]{32}$")
TRIAL = re.compile(r"^[a-z0-9][a-z0-9-]{7,99}$")
ASSIGNMENT = re.compile(r"^[a-z0-9][a-z0-9._-]{7,127}$")
RESTRICTED = re.compile(
    r"(?:/profiles?/|/users?/|/id/[0-9]{6,}|/steamid|/members?/|"
    r"author[_-]?(?:id|hash)|account[_-]?id|review[_-]?id|"
    r"(?<![a-z])steamid[0-9]*|[?&](?:token|key|auth|password|secret)=)",
    re.I,
)
DENY_QUERY = {
    "token", "key", "auth", "password", "secret", "steamid", "accountid",
    "profile", "user", "userid", "author", "authorid", "reviewid", "commentid",
    "session", "api_key", "access_token",
}

class NotesV2Error(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(str(detail)[:240])

def reject(code, detail):
    raise NotesV2Error(code, detail)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def _canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _v2_individual_writer_authorized(source, writer):
    """One V2-only permission check shared by source and locked writer.

    A dispatch option or a source active flag alone never grants approval.
    This helper does not persist data and never changes V1 group acceptance.
    """
    precedence = writer.get("v2_group_policy_precedence") or {}
    return (
        source.get("schema") == "DOSSIER-RESEARCH-NOTES-V2-CONTRACT"
        and source.get("schema_version") == 2
        and source.get("owner") == "github_control_plane"
        and source.get("active") is True
        and source.get("authorized_for_canonical_ingest") is True
        and writer.get("schema") == "DOSSIER-NOTES-V2-INDIVIDUAL-WRITER-V1"
        and writer.get("owner") == "github_control_plane"
        and writer.get("active") is True
        and writer.get("authorized_for_canonical_ingest") is True
        and writer.get("existing_writer_integration_approved") is True
        and writer.get("downstream_deep_handoff_approved") is True
        and writer.get("per_item_only") is True
        and writer.get("v1_group_writer_unchanged") is True
        and writer.get("writer") == "scripts/taste_steam_review_dossier_buffered.py"
        and writer.get("shared_concurrency_group")
            == "taste-steam-review-dossier-canonical-writer"
        and writer.get("existing_locked_writer_workflow")
            == ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml"
        and precedence.get("scope") == "explicit_notes_v2_mode_only"
        and precedence.get("acceptance")
            == "individual_game_independent_under_existing_shared_writer"
    )

def _contract():
    c = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    interfaces = json.loads((CONFIG / "dossier_two_stage_interfaces_contract.json").read_text(encoding="utf-8"))
    inactive = (c.get("active") is False
                and c.get("authorized_for_canonical_ingest") is False)
    authorized_v2 = False
    if not inactive:
        # Only the separately approved V2 writer can authorize the enabled
        # source; _contract itself is read-only and does not grant publication.
        writer = json.loads((CONFIG / "dossier_notes_v2_individual_writer_contract.json")
                            .read_text(encoding="utf-8"))
        authorized_v2 = _v2_individual_writer_authorized(c, writer)
    if (c["schema"] != "DOSSIER-RESEARCH-NOTES-V2-CONTRACT"
            or c["schema_version"] != 2
            or not (inactive or authorized_v2)
            or any(c[k] is not False for k in ("authoritative", "authorized_for_semantic_execution", "production_enabled"))
            or interfaces["active"] is not False
            or interfaces["authorized_for_canonical_ingest"] is not False):
        reject("wrong_binding", "Notes V2 requires inactive defaults or an approved V2-only writer")
    return c

def _schema(name, doc):
    schema = json.loads((CONFIG / name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema).iter_errors(doc))
    if errors:
        reject("unparseable", "V2 schema: " + errors[0].message)

def _safe_text(doc):
    try:
        _privacy(doc)
    except (ValueError, TypeError) as exc:
        reject("unsafe_material", str(exc))
    raw = _canonical(doc)
    if len(raw) > 32000:
        reject("unsafe_material", "V2 material exceeds 32 KB")
    return raw

def _locator(loc):
    if not isinstance(loc, dict) or len(loc) != 1:
        reject("unsafe_material", "locator must contain only one safe public reference")
    if "public_ref" in loc:
        ref = loc["public_ref"]
        if not isinstance(ref, str) or RESTRICTED.search(ref) or any(x in ref.lower() for x in ("steamid", "profile", "author", "account", "token", "username")):
            reject("unsafe_material", "private or unsupported public_ref")
        if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._:/#-]{2,199}", ref):
            reject("unsafe_material", "unsafe public_ref")
    elif "url" in loc:
        value = loc["url"]
        if not isinstance(value, str) or len(value) > 600:
            reject("unsafe_material", "unsafe URL")
        u = urlsplit(value)
        host = (u.hostname or "").lower()
        try:
            port = u.port
        except ValueError:
            reject("unsafe_material", "invalid URL port")
        if (u.scheme != "https" or not host or u.username or u.password
                or port not in (None, 443) or u.fragment
                or host == "localhost" or host.endswith((".local", ".internal", ".test", ".invalid"))
                or RESTRICTED.search(unquote(value))
                or any(k.lower() in DENY_QUERY for k, _ in parse_qsl(u.query, keep_blank_values=True))):
            reject("unsafe_material", "unsafe or private locator")
        try:
            ipaddress.ip_address(host)
        except ValueError:
            if not re.fullmatch(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+", host):
                reject("unsafe_material", "invalid public DNS hostname")
        else:
            reject("unsafe_material", "IP literal URL is not a public source locator")
    else:
        reject("unsafe_material", "unknown locator type")

def _validate_sources(rows):
    for row in rows:
        _locator(row["locator"])
        if row.get("observed_at_utc") is not None:
            # The date is worker-claimed provenance, never GitHub-verified browsing.
            if not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", row["observed_at_utc"]):
                reject("unparseable", "source timestamp must be UTC or null")


def _original_rows():
    """Verify an exact byte-for-byte Git blob copy of the original 18-game buffer.

    The SHA is pinned in the separate V2 contract to the actual immutable
    original Research marker's source blob. No test-generated or worker-edited
    product title, edition suffix, assignment identity or original source
    binding can replace the frozen original item.
    """
    c = _contract()
    pin = c["original_research_identity_authority"]
    if (pin["original_marker_commit"] != c["immutable_original_pins"]["research_marker"]
            or pin["original_buffer_git_blob_sha"] != "c8a6b6f515162f431c0e3d86175376114c0acf7e"
            or pin["byte_identical_local_snapshot"] !=
               "config/dossier_notes_v2_pinned_original_research_buffer_v1.json"):
        reject("wrong_binding", "original Research provenance constants differ")
    try:
        raw = ORIGINAL_BUFFER_PATH.read_bytes()
    except OSError as exc:
        reject("broken_git_provenance", "original immutable source not readable: "+str(exc))
    if blob_for(raw) != pin["original_buffer_git_blob_sha"]:
        reject("broken_git_provenance", "pinned original Research Git blob changed")
    try:
        source = strict_json(raw)
    except (ValueError, UnicodeDecodeError) as exc:
        reject("broken_git_provenance", "original frozen buffer invalid: "+str(exc))
    if (source.get("source_head") != c["immutable_original_pins"]["baseline"]
            or source.get("trial_id") != "dossier-shadow-calibration-20261011-6x3"
            or not isinstance(source.get("items"), list)
            or len(source["items"]) != 18):
        reject("wrong_binding", "original Research Git buffer or trial identity mismatch")
    group_pins = {g["sequence"]:g for g in source["groups"]}
    expected = [(g["group_sequence"], i, appid)
                for g in c["original_groups"] for i, appid in enumerate(g["appids"])]
    rows = []
    for item in source["items"]:
        original = item["assignment"]
        group = item["group_sequence"]
        if (item["appid"] != original["appid"]
                or item["item_index"] != original["item_index"]
                or group != original["group_sequence"]
                or original["group_sha256"] != group_pins[group]["group_sha256"]
                or item["appid"] not in group_pins[group]["appids"]):
            reject("wrong_binding", "inconsistent original work, source or group")
        # Deliberately do NOT bind old_year: it may be wrong (Sifu 2022/2023).
        # The title, including any edition suffix, is the original bound work.
        rows.append({
            "group_sequence":group, "item_index":item["item_index"],
            "appid":item["appid"], "title":original["title"],
            "assignment_id":original["assignment_id"],
            "original_assignment_sha256":digest(_canonical(original)),
        })
    if [(r["group_sequence"], r["item_index"], r["appid"]) for r in rows] != expected:
        reject("wrong_binding", "original 18 Git-pinned item identities/order differ")
    return rows

def _assert_unchanged_since(repo, original_commit, path):
    """Fail closed on ANY intervening first-parent path write, even if restored.

    HEAD byte equality alone misses rewrite-then-restore provenance attacks.
    This is an offline prospective guard, not an issuer or runtime authority.
    """
    if not first_parent_contains(repo, original_commit, "HEAD"):
        reject("broken_git_provenance", "original Git commit not on current first-parent chain")
    changed = git(repo, "log", "--first-parent", "--format=%H",
                  f"{original_commit}..HEAD", "--", path).stdout.strip()
    if changed:
        reject("broken_git_provenance", "immutable V2 artifact modified after original introduction")


def _manifest(repo, marker_commit, trial_id):
    c = _contract()
    if not TRIAL.fullmatch(str(trial_id)) or not HEX40.fullmatch(str(marker_commit)):
        reject("wrong_binding", "invalid frozen trial or marker")
    try:
        p = require_only_new(repo, marker_commit, [
            f"data/control/dossier_notes_v2/run_starts/{_marker_nonce(repo, marker_commit)}.json"])
        marker_path = git(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", marker_commit).stdout.decode().strip()
        if not first_parent_contains(repo, marker_commit, "HEAD"):
            reject("broken_git_provenance", "V2 marker is not in current original first-parent lineage")
        marker = json_at(repo, marker_commit, marker_path)
        if (blob(repo, "HEAD", marker_path) != blob(repo, marker_commit, marker_path)
                or file_at(repo, "HEAD", marker_path) != file_at(repo, marker_commit, marker_path)):
            reject("broken_git_provenance", "V2 run-start marker was changed after issuance")
        _assert_unchanged_since(repo, marker_commit, marker_path)
        if marker != {"schema":"DOSSIER-NOTES-V2-RUN-START","schema_version":2,"nonce":_marker_nonce(repo, marker_commit),"trial_id":trial_id}:
            reject("wrong_binding", "marker contents mismatch")
        path = f"data/control/dossier_notes_v2/manifests/{trial_id}.json"
        m = json_at(repo, p, path)
        if (blob(repo, "HEAD", path) != blob(repo, p, path)
                or file_at(repo, "HEAD", path) != file_at(repo, p, path)):
            reject("broken_git_provenance", "V2 frozen manifest was overwritten")
        _assert_unchanged_since(repo, p, path)
        if (not isinstance(m, dict) or set(m) != {"schema","schema_version","trial_id","original_pins","items"}
                or m["schema"] != "DOSSIER-NOTES-V2-FROZEN-MANIFEST"
                or m["schema_version"] != 2 or m["trial_id"] != trial_id
                or m["original_pins"] != c["immutable_original_pins"]):
            reject("wrong_binding", "incorrect frozen GitHub manifest/pins")
        if m["items"] != _original_rows():
            reject("wrong_binding", "title, edition, assignment ID or source binding differs from original frozen Git buffer")
        return m, blob(repo, p, path)
    except NotesV2Error:
        raise
    except (ValueError, KeyError, TypeError, RuntimeError, subprocess.CalledProcessError) as exc:
        reject("broken_git_provenance", str(exc))

def _marker_nonce(repo, commit):
    if not HEX40.fullmatch(str(commit)):
        reject("wrong_binding", "invalid marker SHA")
    from dossier_two_stage_staging import changes
    _, rows = changes(repo, commit)
    if len(rows) != 1 or rows[0][0] != "A":
        reject("broken_git_provenance", "marker must add exactly one file")
    match = re.fullmatch(r"data/control/dossier_notes_v2/run_starts/([a-f0-9]{32})\.json", rows[0][1])
    if not match:
        reject("wrong_binding", "marker namespace wrong")
    return match.group(1)

def frozen_assignment(repo, *, marker_commit, trial_id, appid):
    m, manifest_blob = _manifest(repo, marker_commit, trial_id)
    row = next((r for r in m["items"] if r["appid"] == str(appid)), None)
    if row is None:
        reject("wrong_binding", "AppID not preauthorized in original 18")
    return {**row, "trial_id": trial_id, "marker_commit": marker_commit, "manifest_blob_sha": manifest_blob}

def _path(phase, assignment):
    prefix = "dossier_notes_v2" if phase == "research" else "dossier_assembly_v2"
    return (f"data/ai_inbox/{prefix}/{assignment['trial_id']}/"
            f"g{assignment['group_sequence']:06d}/{assignment['appid']}--{assignment['assignment_id']}.json")

def validate_notes(document, expected_assignment):
    _contract()
    _schema("dossier_research_notes_v2.schema.json", document)
    if document["assignment"] != expected_assignment:
        reject("wrong_binding", "Research V2 AppID/assignment/marker/manifest mismatch")
    _safe_text(document)
    _validate_sources(document["source_log"])
    return _canonical(document)

def prepare_research(repo, *, marker_commit, trial_id, appid, document):
    a = frozen_assignment(repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid)
    raw = validate_notes(document, a)
    path = _path("research", a)
    if exists(repo, "HEAD", path):
        reject("broken_git_provenance", "create-only research path already exists")
    return {"status":"ready_for_create_only_submission","output_path":path,
            "bytes":raw,"blob_sha":blob_for(raw),"raw_sha256":digest(raw),
            "canonical_acceptance":False}

def submitted_research(repo, *, marker_commit, trial_id, appid, introduction_commit):
    a = frozen_assignment(repo, marker_commit=marker_commit, trial_id=trial_id, appid=appid)
    path = _path("research", a)
    if introduction_commit is None:
        return {"status":"missing_research_transport","attempt_state":"unknown",
                "appid":a["appid"],"item_local_only":True,"canonical_acceptance":False}
    if not HEX40.fullmatch(str(introduction_commit)):
        reject("broken_git_provenance", "invalid Git introduction SHA")
    try:
        p = require_only_new(repo, introduction_commit, [path])
        if (not first_parent_contains(repo, marker_commit, p)
                or not first_parent_contains(repo, introduction_commit, "HEAD")):
            reject("broken_git_provenance", "Research introduction outside marker/HEAD first-parent ancestry")
        raw = file_at(repo, introduction_commit, path)
        if (blob(repo, introduction_commit, path) != blob_for(raw)
                or blob(repo, "HEAD", path) != blob_for(raw)
                or file_at(repo, "HEAD", path) != raw):
            reject("broken_git_provenance", "Research bytes altered after original introduction")
        _assert_unchanged_since(repo, introduction_commit, path)
        try:
            doc = strict_json(raw)
        except (ValueError, UnicodeDecodeError) as exc:
            reject("unparseable", str(exc))
        validate_notes(doc, a)
    except NotesV2Error:
        raise
    except (ValueError, TypeError, KeyError, RuntimeError, subprocess.CalledProcessError) as exc:
        reject("broken_git_provenance", str(exc))
    return {"status":"safe_incomplete_research","appid":a["appid"],
            "assignment":a,"research_package_git_commit":introduction_commit,
            "research_package_path":path,"research_package_blob_sha":blob_for(raw),
            "research_package_raw_sha256":digest(raw),
            "research_package_sha256":digest(_canonical(doc)),
            "worker_claims_not_accepted_facts":True,"canonical_acceptance":False}

def classify_research(repo, *, marker_commit, trial_id, appid, introduction_commit):
    try:
        return submitted_research(repo, marker_commit=marker_commit, trial_id=trial_id,
                                  appid=appid, introduction_commit=introduction_commit)
    except NotesV2Error as exc:
        return {"status":exc.code,"diagnostic":str(exc),"appid":str(appid),
                "item_local_only":True,"attempt_state":"unknown","canonical_acceptance":False}

def assembly_work(repo, *, marker_commit, trial_id, appid, research_commit):
    # Stage 2 is a per-item boundary: bad A may not abort B/C.
    transport = classify_research(repo, marker_commit=marker_commit, trial_id=trial_id,
                                  appid=appid, introduction_commit=research_commit)
    if transport["status"] != "safe_incomplete_research":
        return transport
    a = transport["assignment"]
    return {"status":"ready_for_autonomous_assembly",
            "assignment":a, "research_transport":{k:v for k,v in transport.items()
                        if k in ("research_package_git_commit","research_package_path",
                                 "research_package_blob_sha","research_package_raw_sha256",
                                 "research_package_sha256")},
            "output_path":_path("assembly", a),
            "source_notes_are_unverified_leads":True,"may_independently_discover":True,
            "max_mechanical_corrections":2,"canonical_acceptance":False}


def frozen_assembly_traversal(repo, *, marker_commit, trial_id, research_commits):
    """Classify all original 18 independently, preserving immutable order.

    GitHub supplies only committed transport SHAs. No semantics, retries,
    preauthorization or implicit work claims are performed here.
    """
    m, _ = _manifest(repo, marker_commit, trial_id)
    appids = [row["appid"] for row in m["items"]]
    if (not isinstance(research_commits, dict)
            or any(appid not in appids for appid in research_commits)):
        reject("wrong_binding", "unknown AppID in Research transport table")
    rows = []
    for a in m["items"]:
        appid = a["appid"]
        result = assembly_work(repo, marker_commit=marker_commit, trial_id=trial_id,
                               appid=appid, research_commit=research_commits.get(appid))
        rows.append({"group_sequence":a["group_sequence"],
                     "item_index":a["item_index"],"appid":appid,
                     **result})
    return rows

def candidate_assembly(work, *, outcome, final_dossier=None, operations=None,
                       mechanical_corrections=None, diagnostic=None):
    if work.get("status") != "ready_for_autonomous_assembly":
        reject("wrong_binding", "Assembly has no exact verified original Research transport")
    doc = {"schema":"DOSSIER-AUTONOMOUS-ASSEMBLY-RESULT-V2","schema_version":2,
           "assignment":work["assignment"],"research_transport":work["research_transport"],
           "outcome":outcome,"final_dossier":final_dossier,
           "operations":operations if operations is not None else [],
           "mechanical_corrections":mechanical_corrections if mechanical_corrections is not None else [],
           "diagnostic":diagnostic,"staged_only":True,"canonical_acceptance":False}
    _schema("dossier_autonomous_assembly_result_v2.schema.json", doc)
    if (outcome == "assembled_candidate_ready") != (final_dossier is not None):
        reject("final_strict_or_group_rejected", "ready needs a final Dossier, terminals may not claim one")
    if outcome != "assembled_candidate_ready" and not diagnostic:
        reject("assembly_technical_error", "terminal result must contain honest typed diagnostic")
    _safe_text({k:v for k,v in doc.items() if k != "final_dossier"})
    for op in doc["operations"]:
        if op.get("locator") is not None:
            _locator(op["locator"])
        when = op.get("observed_at_utc")
        if when is not None and not re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ",when):
            reject("unparseable", "operation timestamp invalid")
    return doc

def inspect_assembly(repo, *, marker_commit, trial_id, appid, research_commit, result_commit):
    try:
        work = assembly_work(repo, marker_commit=marker_commit, trial_id=trial_id,
                             appid=appid, research_commit=research_commit)
        if work["status"] != "ready_for_autonomous_assembly":
            return work
        path = work["output_path"]
        p = require_only_new(repo, result_commit, [path])
        if (not first_parent_contains(repo, research_commit, p)
                or not first_parent_contains(repo, marker_commit, p)
                or not first_parent_contains(repo, result_commit, "HEAD")):
            reject("broken_git_provenance", "Assembly result not descendant of original frozen Research")
        raw = file_at(repo, result_commit, path)
        if (blob(repo, result_commit, path) != blob_for(raw) or blob(repo, "HEAD", path) != blob_for(raw)
                or file_at(repo, "HEAD", path) != raw):
            reject("broken_git_provenance", "Assembly candidate overwritten")
        _assert_unchanged_since(repo, result_commit, path)
        doc = strict_json(raw)
        _schema("dossier_autonomous_assembly_result_v2.schema.json", doc)
        if doc["assignment"] != work["assignment"] or doc["research_transport"] != work["research_transport"]:
            reject("wrong_binding", "Assembly candidate rebound to other frozen Research")
        candidate_assembly(work,outcome=doc["outcome"],final_dossier=doc["final_dossier"],
                           operations=doc["operations"],mechanical_corrections=doc["mechanical_corrections"],
                           diagnostic=doc["diagnostic"])
        if doc["outcome"] != "assembled_candidate_ready":
            return {"status":doc["outcome"],"item_local_only":True,
                    "attempt_state":"unknown","canonical_acceptance":False}
        try:
            final = doc["final_dossier"]
            if final.get("appid") != work["assignment"]["appid"] or final.get("title") != work["assignment"]["title"]:
                reject("final_strict_or_group_rejected", "wrong final exact product")
            strict = json.loads((CONFIG / "taste_steam_review_dossier_contract.json").read_text("utf-8"))
            validate_dossier_strict(final,strict,expected_appid=work["assignment"]["appid"],
                                    expected_title=work["assignment"]["title"])
        except NotesV2Error:
            raise
        except (ValueError, KeyError, TypeError, AssertionError) as exc:
            reject("final_strict_or_group_rejected", str(exc))
        return {"status":"strict_item_valid_pending_existing_atomic_group_ingest",
                "item_local_only":True,"canonical_acceptance":False,"deep_ready":False}
    except NotesV2Error as exc:
        return {"status":exc.code,"diagnostic":str(exc),"item_local_only":True,
                "canonical_acceptance":False,"deep_ready":False,"attempt_state":"unknown"}
    except (ValueError, KeyError, TypeError, RuntimeError) as exc:
        return {"status":"broken_git_provenance","diagnostic":str(exc)[:240],
                "item_local_only":True,"canonical_acceptance":False,"deep_ready":False}


def manifest_blueprint(trial_id, prepared_rows):
    """GitHub-side pure future manifest planner: returns bytes, NEVER issues authority.

    The new GitHub authorization must independently establish title/edition
    correctness and write one immutable manifest before a new marker exists.
    This code cannot reauthorize the old trial or infer titles from AppIDs.
    """
    c = _contract()
    if not TRIAL.fullmatch(str(trial_id)) or not isinstance(prepared_rows, list):
        reject("wrong_binding", "invalid future GitHub trial or prepared rows")
    if prepared_rows != _original_rows():
        reject("wrong_binding", "future manifest must preserve exact original AppID, title/edition and Research assignment digest")
    obj = {"schema":"DOSSIER-NOTES-V2-FROZEN-MANIFEST",
           "schema_version":2,"trial_id":trial_id,
           "original_pins":c["immutable_original_pins"],"items":prepared_rows}
    return {"output_path":f"data/control/dossier_notes_v2/manifests/{trial_id}.json",
            "bytes":_canonical(obj),"blob_sha":blob_for(_canonical(obj)),
            "authorizes_semantic_execution":False}

def prepare_assembly_transport(repo, work, document):
    """Validate draft once before a single future create-only submission.

    Offline pure proposer. Never claims GitHub acceptance or extends scope.
    """
    if work.get("status") != "ready_for_autonomous_assembly":
        reject("wrong_binding", "not an authorized V2 assembly item")
    # A prior work dict is only a snapshot, not fresh authority. Reverify the
    # original single-add Research bytes, marker and manifest at submission.
    a = work.get("assignment", {})
    transport = work.get("research_transport", {})
    if not isinstance(a, dict) or not isinstance(transport, dict):
        reject("wrong_binding", "invalid frozen Assembly work envelope")
    if not all(k in a for k in ("marker_commit", "trial_id", "appid")) or "research_package_git_commit" not in transport:
        reject("wrong_binding", "incomplete frozen Assembly work envelope")
    current = assembly_work(repo, marker_commit=a["marker_commit"],
                            trial_id=a["trial_id"], appid=a["appid"],
                            research_commit=transport["research_package_git_commit"])
    if current.get("status") != "ready_for_autonomous_assembly" or current != work:
        reject("broken_git_provenance", "stale or forged Assembly work / Research chain")
    # The exact supplied document is what will be serialized below. Validate
    # its full schema/flags/unknown keys and privacy before proposing create-only
    # transport; checking only candidate_assembly's reconstructed copy is unsafe.
    _schema("dossier_autonomous_assembly_result_v2.schema.json", document)
    try:
        _privacy(document)
    except (ValueError, TypeError) as exc:
        reject("unsafe_material", str(exc))
    _safe_text({k:v for k,v in document.items() if k != "final_dossier"})
    if (document["assignment"] != work["assignment"]
            or document["research_transport"] != work["research_transport"]):
        reject("wrong_binding", "Assembly output differs from original V2 binding")
    checked = candidate_assembly(work, outcome=document["outcome"],
                       final_dossier=document["final_dossier"],
                       operations=document["operations"],
                       mechanical_corrections=document["mechanical_corrections"],
                       diagnostic=document["diagnostic"])
    if checked != document:
        reject("wrong_binding", "supplied Assembly document differs from validated candidate")
    if document["outcome"] == "assembled_candidate_ready":
        try:
            strict = json.loads((CONFIG / "taste_steam_review_dossier_contract.json").read_text("utf-8"))
            validate_dossier_strict(document["final_dossier"], strict,
                 expected_appid=work["assignment"]["appid"],
                 expected_title=work["assignment"]["title"])
        except (ValueError, AssertionError, TypeError, KeyError) as exc:
            reject("final_strict_or_group_rejected", "strict draft validation failed: "+str(exc))
    path = _path("assembly", work["assignment"])
    if exists(repo, "HEAD", path):
        reject("broken_git_provenance", "create-only Assembly path occupied")
    if not first_parent_contains(
            repo, work["research_transport"]["research_package_git_commit"], "HEAD"):
        reject("broken_git_provenance", "Research commit no longer in original lineage")
    raw = _canonical(document)
    return {"status":"ready_for_create_only_submission","output_path":path,
            "bytes":raw,"blob_sha":blob_for(raw),"raw_sha256":digest(raw),
            "canonical_acceptance":False}

def item_receipt_blueprint(repo, *, marker_commit, trial_id, appid, phase, disposition, source=None):
    """Typed GitHub receipt proposal, not acceptance or proof of attempt.

    Only a separately authorized GitHub writer may attest and persist it.
    """
    c = _contract()
    if phase not in ("research","assembly") or disposition not in c["receipts"]:
        reject("wrong_binding", "unsupported per-item receipt disposition")
    assignment = frozen_assignment(repo, marker_commit=marker_commit,
                                   trial_id=trial_id, appid=appid)
    doc = {"schema":"DOSSIER-NOTES-V2-ITEM-RECEIPT",
           "schema_version":2,"trial_id":assignment["trial_id"],
           "appid":assignment["appid"],"assignment":assignment,
           "phase":phase,"disposition":disposition,
           "source":source,
           "semantic_attempt_state":"unknown",
           "staged_only":True,"canonical_acceptance":False}
    _schema("dossier_notes_v2_item_receipt.schema.json",doc)
    if phase == "research" and disposition in (
            "assembly_missing_evidence", "assembly_semantic_conflict",
            "assembly_technical_error", "final_strict_or_group_rejected",
            "strict_item_valid_pending_existing_atomic_group_ingest"):
        reject("wrong_binding", "Research phase cannot claim Assembly disposition")
    if phase == "assembly" and disposition == "safe_incomplete_research":
        reject("wrong_binding", "Assembly receipt cannot attest Research completeness")
    _safe_text(doc)
    return doc

def individual_final_readiness(repo, *, marker_commit, trial_id, item_commits):
    """Offline per-game strict readiness, NEVER canonical acceptance.

    A/C can be locally ready while B is invalid, missing or still awaiting
    Assembly. Only immutable submitted Git commits are examined; caller
    assertions of readiness or acceptance are not accepted as input.
    """
    manifest, _ = _manifest(repo, marker_commit, trial_id)
    appids = [item["appid"] for item in manifest["items"]]
    if (type(item_commits) is not dict
            or any(type(key) is not str or key not in appids for key in item_commits)):
        reject("wrong_binding", "item commits must reference only frozen V2 AppIDs")

    outcomes = []
    for item in manifest["items"]:
        appid = item["appid"]
        pair = item_commits.get(appid)
        status = "missing"
        source_status = "missing_research_transport"
        if pair is not None:
            if type(pair) is not dict or set(pair) != {"research_commit", "assembly_commit"}:
                status, source_status = "invalid", "wrong_binding"
            else:
                research, assembly = pair["research_commit"], pair["assembly_commit"]
                if research is None and assembly is not None:
                    status, source_status = "invalid", "wrong_binding"
                elif research is not None:
                    try:
                        if assembly is None:
                            checked = assembly_work(
                                repo, marker_commit=marker_commit, trial_id=trial_id,
                                appid=appid, research_commit=research)
                        else:
                            checked = inspect_assembly(
                                repo, marker_commit=marker_commit, trial_id=trial_id,
                                appid=appid, research_commit=research,
                                result_commit=assembly)
                        source_status = checked["status"]
                        if source_status == "strict_item_valid_pending_existing_atomic_group_ingest":
                            status = "ready"
                        elif source_status == "ready_for_autonomous_assembly":
                            status = "waiting"
                        elif source_status == "missing_research_transport":
                            status = "missing"
                        elif source_status in ("runtime_or_tool_interrupted", "assembly_technical_error"):
                            status = "error"
                        else:
                            status = "invalid"
                    except NotesV2Error as exc:
                        status, source_status = "invalid", exc.code
                    except (KeyError, TypeError, ValueError, RuntimeError,
                            OSError, subprocess.CalledProcessError) as exc:
                        status, source_status = "error", type(exc).__name__
        outcomes.append({
            "appid": appid, "group_sequence": item["group_sequence"],
            "item_index": item["item_index"],
            "status": status, "source_status": source_status,
            "strict_item_valid": status == "ready",
            "canonical_acceptance": False, "deep_ready": False,
        })

    return {
        "schema": "DOSSIER-NOTES-V2-OFFLINE-INDIVIDUAL-READINESS",
        "trial_id": trial_id, "items": outcomes,
        "canonical_acceptance": False, "deep_ready": False,
        "requires_separately_authorized_canonical_writer": True,
    }


def original_group_readiness(group_sequence, item_verdicts):
    """Reporting ONLY. Existing strict three-game writer is sole acceptance path."""
    c = _contract()
    g = next((g for g in c["original_groups"] if g["group_sequence"] == group_sequence),None)
    if g is None:
        reject("wrong_binding", "original group not found")
    if set(item_verdicts) - set(g["appids"]):
        reject("wrong_binding", "foreign item in original group")
    complete = len(item_verdicts) == 3 and all(
        item_verdicts.get(a) == "strict_item_valid_pending_existing_atomic_group_ingest"
        for a in g["appids"])
    return {"group_sequence":group_sequence,"original_appids":g["appids"],"strict_three_ready":complete,
            "canonical_acceptance":False}

def checked_typed_publish_prefix(frozen_authorized_order, typed_git_history,
                                 target_appid, current_inspect):
    """PR232 compatibility: never recompute typed lineage from shrinking ready rows.

    frozen_authorized_order MUST be GitHub-attested at first authorization.
    This function verifies ordering only, not authorization/real GitHub approval.
    """
    c = _contract()
    original = [appid for g in c["original_groups"] for appid in g["appids"]]
    order = list(frozen_authorized_order)
    typed = list(typed_git_history)
    if (len(order) != len(set(order)) or any(a not in original for a in order)
            or [a for a in original if a in order] != order
            or typed != order[:len(typed)]
            or len(typed) != len(set(typed))
            or not typed or typed[-1] != target_appid
            or target_appid not in order):
        reject("wrong_binding", "typed lineage must be exact prefix of stable frozen authorization")
    states = dict(current_inspect)
    if states.get(target_appid) != "ready":
        reject("wrong_binding", "target currently not individually publishable")
    if any(states.get(previous) != "candidate_already_submitted" for previous in typed[:-1]):
        reject("wrong_binding", "historical typed prefix must remain published, not reusable")
    return {"validated_typed_prefix":typed,"target_appid":target_appid,
            "prior_published_items_remain_in_frozen_order":True}

def verify_independent_reviewers(appointments, authenticated_lookup, director_approval):
    """Requires real authenticated GitHub account resolution and owner authorization.

    Callers MUST pass an actual authenticated API lookup and independently checked
    owner approval. A username regex, a self-asserted flag, or missing verifier
    cannot grant a reviewer slot.
    """
    if not callable(authenticated_lookup) or not callable(director_approval):
        reject("wrong_binding", "real authenticated identity and Director approval required")
    if not isinstance(appointments, dict) or set(appointments) != {"A","B","C"}:
        reject("wrong_binding", "three separately appointed reviewer roles required")
    ids = []
    refs = []
    for role in ("A","B","C"):
        row = appointments[role]
        if (not isinstance(row, dict) or set(row) != {"login","github_id","appointment_ref"}
                or not isinstance(row["login"], str)
                or type(row["github_id"]) is not int or row["github_id"] <= 0
                or not isinstance(row["appointment_ref"], str) or not row["appointment_ref"]):
            reject("wrong_binding", "reviewer appointment requires bound authenticated identity")
        observed = authenticated_lookup(row["login"])
        if not isinstance(observed, dict) or observed.get("login","").casefold() != row["login"].casefold() or observed.get("id") != row["github_id"]:
            reject("wrong_binding", "reviewer has no matching authenticated account identity")
        if director_approval(role,row["github_id"],row["appointment_ref"]) is not True:
            reject("wrong_binding", "Director did not authenticate independent appointment")
        ids.append(row["github_id"])
        refs.append(row["appointment_ref"])
    if len(set(refs)) != 3:
        reject("wrong_binding", "independent roles cannot reuse one appointment receipt")
    if len(set(ids)) != 3:
        reject("wrong_binding", "reviewer A/B/C identities are not independent")
    return True
