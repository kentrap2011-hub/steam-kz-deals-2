#!/usr/bin/env python3
"""Github-native, manually gated transport for the ORIGINAL shadow Stage B.

This adapter has no issuer, semantic computation, queue, retry or canonical
ingest. Stage B's pinned original Python remains the ONLY evidence validator,
candidate builder, and verifier. Use only on the frozen Git checkout.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SHA = re.compile(r"^[0-9a-f]{40}$")
FIXED_MARKER = "2c2649fb98322507cd3758ff0ff7992128f94de0"
FIXED_BUFFER = "9782ab8492aadc744c23ec0425abf8d2d877590e"
FIXED_RESEARCH_MARKER = "bb63cc291eba5aa8fc56e2920ef84d131ac28a4f"
FIXED_AUTH = "2a726cf6731c0fc1e7bc809474627383c107ef9b"
FIXED_MISSING = {"1508750", "1607130", "1849000", "1857090"}
FIXED_RESEARCH_COMMITS = {
    "1517180": "33faf93e578d32dd5e694f72f119041eb102021d",
    "1533420": "4be027d8a26da46ccb3b4887f2cfc89a6517f85d",
    "1590230": "7cb2eed3038a99d8b6af8ad3b36813415979b8dd",
    "1599600": "334251771cbd0c858e7437dbdbae8c9bbb5c39dc",
    "1868140": "162eea9dd2caeefe0e8dae02b82127bf07e9c563",
    "1999170": "abf88e5318422e55915a437ad9b6798c5d22a077",
    "1999360": "37f950419bde189c766eba8a174847b53284cb60",
    "2009010": "90b57935ed598b8d458c839c9a80bee22adbbf04",
    "206420": "73f88b35f7658e9373365489068ae927a75e95b0",
    "2067050": "24dd6b56c50d97e81d7fe1cbb3619a63af71a47c",
    "2076140": "1b5cd015a3a00425f20ca01ae6da4dd43ea40012",
    "2124120": "cef43773d710b2d87c4c75c648d690b36def386f",
    "213610": "9049a4df4766e25a4ae8053200465096323b6b99",
    "2138710": "af470aad964c1f20afebca2d25dd2347b2ddc668",
}


def require(ok, message):
    if not ok:
        raise ValueError("SHADOW_GITHUB_PYTHON_HANDOFF_BLOCKED: " + message)


def checked(repo, pins, stage, *, allow_local_result=False):
    """Fail before even reading semantic input if authority or inputs drift."""
    p = json.loads(Path(pins).read_text("utf-8"))
    require(p["schema"] == "DOSSIER-SHADOW-18-GITHUB-PYTHON-HANDOFF-PINS-V1"
            and p["trial_id"] == stage.TRIAL
            and p["original_sandbox_branch"] == stage.BRANCH
            and p["assembly_marker_commit"] == FIXED_MARKER
            and p["assembly_buffer_commit"] == FIXED_BUFFER
            and p["assembly_buffer_blob_sha"] == "5c7e66db7d3880098c0cd85f0690661c9655cd09"
            and p["research_marker_commit"] == FIXED_RESEARCH_MARKER
            and p["research_feasibility_authorization_commit"] == FIXED_AUTH
            and p["issuer_run_id"] == 39054131983
            and p["original_research_introduction_commits"] == FIXED_RESEARCH_COMMITS
            and set(p["missing_research_appids"]) == FIXED_MISSING
            and p["submission_branch"] == "handoff/dossier-shadow-18-assembly-typed"
            and p["submission_namespace"] == stage.PREFIX.replace("/trials/", "/handoff/")
            and p["canonical_acceptance"] is False
            and p["deep_ready"] is False
            and p["production_writes"] == []
            and p["scheduled_tasks"] is False
            and p["retry_enabled"] is False,
            "frozen pins mismatch")
    remote = stage.git(
        repo, "rev-parse", "refs/remotes/origin/" + stage.BRANCH
    ).stdout.decode().strip()
    require(stage.head(repo) == remote or (
        allow_local_result and stage.first_parent_contains(
            repo, remote, stage.head(repo))),
        "sandbox checkout differs from remote (no race/rebind)")
    require(stage.git(repo, "symbolic-ref", "--short", "HEAD").stdout.decode().strip()
            == stage.BRANCH, "must checkout ORIGINAL sandbox branch")
    require(not stage.git(repo, "status", "--porcelain").stdout,
            "sandbox checkout must be clean")
    require(stage.git(repo, "rev-parse", FIXED_MARKER + "^").stdout.decode().strip()
            == FIXED_BUFFER, "wrong original Assembly buffer parent")
    require(stage.blob(repo, FIXED_BUFFER, stage.BUFFER)
            == p["assembly_buffer_blob_sha"], "frozen Assembly buffer blob mismatch")
    return p


def readiness(repo, pins, stage, *, allow_local_result=False):
    p = checked(repo, pins, stage, allow_local_result=allow_local_result)
    result = stage.inspect(repo, marker_commit=FIXED_MARKER,
                           research_commits=p["original_research_introduction_commits"])
    from dossier_shadow_research_trial_publish import EXPECTED_APPIDS
    rows = result["rows"]
    require([r["appid"] for r in rows] == EXPECTED_APPIDS
            and len(rows) == 18 and not result["canonical_acceptance"]
            and not result["deep_ready"] and result["semantic_attempts"] == 0,
            "not the exact frozen eighteen or inspect pretends acceptance")
    for row in rows:
        if row["appid"] in FIXED_MISSING:
            require(row["status"] == "research_not_submitted",
                    "original missing Research may not become a submission")
    return result


def semantic_submission(repo, stage, p, appid, commit):
    """Git transport is a single create-only immutable typed JSON file."""
    require(SHA.fullmatch(str(commit)) is not None, "semantic commit must be Git SHA")
    require(appid in FIXED_RESEARCH_COMMITS, "no source Research or foreign AppID")
    branch_head = stage.git(
        repo, "rev-parse", "refs/remotes/origin/" + p["submission_branch"]
    ).stdout.decode().strip()
    require(stage.first_parent_contains(repo, commit, branch_head),
            "semantic commit not in designated GitHub handoff branch")
    path = p["submission_namespace"] + "/" + appid + ".json"
    stage.require_only_new(repo, commit, [path])
    require(stage.blob(repo, commit, path) == stage.blob(repo, branch_head, path),
            "semantic handoff JSON rewritten after introduction")
    raw = stage.git(repo, "show", commit + ":" + path).stdout
    require(len(raw) <= 2_000_000, "semantic handoff exceeds finite safety limit")
    semantic = stage.strict_json(raw)
    require(type(semantic) is dict
            and set(semantic) == {"outcome", "payload", "supplemental_operations"}
            and type(semantic["outcome"]) is str
            and type(semantic["payload"]) is dict
            and type(semantic["supplemental_operations"]) is list,
            "not exact typed semantic-only transport")
    return semantic


def original_order_gate(state, appid):
    """Existing frozen row order, without requiring invalid/missing siblings."""
    require(any(row["appid"] == appid for row in state["rows"]),
            "foreign AppID")
    found = False
    for row in state["rows"]:
        if row["appid"] == appid:
            require(row["status"] == "ready", "not canonical Python ready")
            found = True
            break
        require(row["status"] != "ready",
                "earlier ready original row needs its create-only candidate first")
    require(found, "foreign AppID")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["inspect", "build", "verify"])
    parser.add_argument("--sandbox", required=True)
    parser.add_argument("--pins", required=True)
    parser.add_argument("--appid")
    parser.add_argument("--semantic-commit")
    parser.add_argument("--result-commit")
    args = parser.parse_args()
    repo = Path(args.sandbox).resolve()
    # This must import the exact original checkout, NOT the newer launcher tree.
    sys.path.insert(0, str(repo / "scripts"))
    import dossier_shadow_18_assembly_stage_b as stage

    p = checked(repo, args.pins, stage,
                allow_local_result=args.mode == 'verify')
    state = readiness(repo, args.pins, stage,
                      allow_local_result=args.mode == 'verify')
    if args.mode == "inspect":
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False))
        return
    require(args.appid in FIXED_RESEARCH_COMMITS, "AppID not submitted in Research")
    if args.mode == "build":
        original_order_gate(state, args.appid)
        semantic = semantic_submission(repo, stage, p, args.appid,
                                       args.semantic_commit)
        path, payload = stage.build_candidate(
            repo, marker_commit=FIXED_MARKER,
            research_commits=FIXED_RESEARCH_COMMITS,
            appid=args.appid, semantic=semantic)
        require(path.startswith(stage.PREFIX + "/assembly/"), "non-shadow output")
        target = repo / path
        target.parent.mkdir(parents=True, exist_ok=True)
        # Mode x explicitly denies overwrite, including an existing bogus file.
        with target.open("x", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"))
            file.write("\n")
        print(path)
    else:
        require(SHA.fullmatch(str(args.result_commit)) is not None,
                "real result commit required")
        proof = stage.verify_candidate(
            repo, marker_commit=FIXED_MARKER,
            research_commits=FIXED_RESEARCH_COMMITS, appid=args.appid,
            result_commit=args.result_commit)
        print(json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    main()
