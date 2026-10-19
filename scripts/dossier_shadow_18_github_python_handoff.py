#!/usr/bin/env python3
"""Github-native, manually gated transport for the ORIGINAL shadow Stage B.

This adapter has no issuer, semantic computation, queue, retry or canonical
ingest. Stage B's pinned original Python remains the ONLY evidence validator,
candidate builder, and verifier. Use only on the frozen Git checkout.
"""
import argparse
import json
import re
import os
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


def remote_tip(repo, stage, branch):
    """Fresh advertised GitHub ref; a stale local tracking ref is not authority."""
    require(branch in (
        "handoff/dossier-shadow-18-assembly-typed",
        "sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research",
    ), "unapproved Git remote branch")
    ref = "refs/heads/" + branch
    raw = stage.git(repo, "ls-remote", "--heads", "origin", ref).stdout.decode().strip()
    rows = [line.split() for line in raw.splitlines()]
    require(len(rows) == 1 and len(rows[0]) == 2
            and rows[0][1] == ref and SHA.fullmatch(rows[0][0]),
            "remote branch absent or ambiguous")
    return rows[0][0]


def validate_sandbox_descendants(repo, stage, marker, remote, expected_paths):
    """Every descendant MUST be a linear, single-add original Assembly candidate."""
    require(stage.first_parent_contains(repo, marker, remote),
            "remote no longer descends from original Assembly marker")
    commits = stage.git(repo, "rev-list", "--reverse",
                        marker + ".." + remote).stdout.decode().splitlines()
    previous = marker
    submitted = set()
    for child in commits:
        parents = stage.git(repo, "rev-list", "--parents", "-n", "1",
                            child).stdout.decode().strip().split()
        require(parents == [child, previous],
                "post-marker history must be direct-child linear and unmerged")
        paths = stage.git(repo, "diff-tree", "--no-commit-id", "--name-only",
                          "-r", child).stdout.decode().splitlines()
        require(len(paths) == 1 and paths[0] in expected_paths,
                "post-marker commit changed non-authorized path")
        path = paths[0]
        require(path not in submitted, "original candidate path repeated")
        stage.require_only_new(repo, child, [path])
        require(stage.blob(repo, child, path) == stage.blob(repo, remote, path),
                "original candidate overwritten")
        submitted.add(path)
        previous = child
    require(previous == remote, "nonlinear post-marker history")
    return len(commits)


def load_original_stage(authority):
    """Import Stage B and ALL transitive Python/config from marker checkout."""
    from subprocess import check_output
    authority = Path(authority).resolve()
    actual = check_output(["git", "-C", str(authority), "rev-parse", "HEAD"],
                          text=True).strip()
    require(actual == FIXED_MARKER, "executable authority not original marker")
    require(not check_output(["git", "-C", str(authority), "status",
                              "--porcelain"], text=True).strip(),
            "executable authority checkout not clean")
    require((authority / "scripts/dossier_shadow_18_assembly_stage_b.py").is_file(),
            "marker-era Stage B module missing")
    sys.path.insert(0, str(authority / "scripts"))
    import dossier_shadow_18_assembly_stage_b as stage
    require(Path(stage.__file__).resolve() ==
            (authority / "scripts/dossier_shadow_18_assembly_stage_b.py").resolve(),
            "Stage B imported from mutable or launcher checkout")
    from dossier_two_stage_contract_guard import CONFIG
    require(Path(CONFIG).resolve() == (authority / "config").resolve(),
            "strict schema/config imported from mutable checkout")
    return stage


def require_publish_dispatch(*, event, ref, repository, actor, attempt,
                             operation, approval, appid, commit):
    """Technical gate ONLY; independent human consent is external/procedural."""
    require(event == "workflow_dispatch" and ref == "refs/heads/main"
            and repository == "kentrap2011-hub/steam-kz-deals-2"
            and actor == "kentrap2011-hub" and str(attempt) == "1"
            and operation == "publish"
            and approval == "DIRECTOR_AUTHORIZED_SHADOW_ASSEMBLY_TYPED_HANDOFF",
            "unauthorized GitHub publish context")
    require(bool(re.fullmatch(r"[0-9]+", str(appid)))
            and str(appid) in FIXED_RESEARCH_COMMITS
            and SHA.fullmatch(str(commit)) is not None,
            "unapproved AppID or semantic commit")


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
    require(remote_tip(repo, stage, stage.BRANCH) == remote,
            "sandbox remote changed since checkout")
    local = stage.head(repo)
    if allow_local_result and local != remote:
        parents = stage.git(repo, "rev-list", "--parents", "-n",
                            "1", local).stdout.decode().strip().split()
        require(parents == [local, remote],
                "verify must use exactly one direct local candidate commit")
    else:
        require(local == remote,
                "sandbox checkout differs from remote (no race/rebind)")
    require(stage.git(repo, "symbolic-ref", "--short", "HEAD").stdout.decode().strip()
            == stage.BRANCH, "must checkout ORIGINAL sandbox branch")
    require(not stage.git(repo, "status", "--porcelain").stdout,
            "sandbox checkout must be clean")
    require(stage.git(repo, "rev-parse", FIXED_MARKER + "^").stdout.decode().strip()
            == FIXED_BUFFER, "wrong original Assembly buffer parent")
    require(stage.blob(repo, FIXED_BUFFER, stage.BUFFER)
            == p["assembly_buffer_blob_sha"], "frozen Assembly buffer blob mismatch")
    manifest, _nonce, _parent = stage.frozen(repo, marker_commit=FIXED_MARKER)
    expected_paths = {stage.result_path(item) for item in manifest["items"]}
    require(len(expected_paths) == 18, "frozen Assembly candidate paths not unique")
    validate_sandbox_descendants(repo, stage, FIXED_MARKER, remote, expected_paths)
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


def semantic_submission(repo, stage, p, appid, commit, expected_tip):
    """Git transport is a single create-only immutable typed JSON file."""
    require(SHA.fullmatch(str(commit)) is not None, "semantic commit must be Git SHA")
    require(appid in FIXED_RESEARCH_COMMITS, "no source Research or foreign AppID")
    branch_head = stage.git(
        repo, "rev-parse", "refs/remotes/origin/" + p["submission_branch"]
    ).stdout.decode().strip()
    require(SHA.fullmatch(str(expected_tip)) is not None
            and expected_tip == branch_head
            and remote_tip(repo, stage, p["submission_branch"]) == expected_tip,
            "typed handoff ref rewritten, withdrawn or drifted after fetch")
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
    """Frozen traversal order stays in inspect; sibling readiness is independent."""
    row = next((r for r in state["rows"] if r["appid"] == appid), None)
    require(row is not None, "foreign AppID")
    require(row["status"] == "ready", "not canonical Python ready")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["inspect", "build", "verify"])
    parser.add_argument("--sandbox", required=True)
    parser.add_argument("--authority", required=True,
                        help="immutable detached Git checkout at original marker")
    parser.add_argument("--expected-semantic-tip")
    parser.add_argument("--pins", required=True)
    parser.add_argument("--appid")
    parser.add_argument("--semantic-commit")
    parser.add_argument("--result-commit")
    args = parser.parse_args()
    repo = Path(args.sandbox).resolve()
    # Code, recursive imports and strict CONFIG live in immutable authority checkout.
    stage = load_original_stage(args.authority)

    p = checked(repo, args.pins, stage,
                allow_local_result=args.mode == 'verify')
    state = readiness(repo, args.pins, stage,
                      allow_local_result=args.mode == 'verify')
    if args.mode == "inspect":
        print(json.dumps(state, indent=2, sort_keys=True, ensure_ascii=False))
        return
    require(args.appid in FIXED_RESEARCH_COMMITS, "AppID not submitted in Research")
    require(SHA.fullmatch(str(args.expected_semantic_tip)) is not None,
            "exact fetched semantic tip required")
    if args.mode == "build":
        original_order_gate(state, args.appid)
    semantic = semantic_submission(repo, stage, p, args.appid,
                                   args.semantic_commit, args.expected_semantic_tip)
    if args.mode == "build":
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
        require(stage.head(repo) == args.result_commit,
                "verify must target actual current local candidate")
        proof = stage.verify_candidate(
            repo, marker_commit=FIXED_MARKER,
            research_commits=FIXED_RESEARCH_COMMITS, appid=args.appid,
            result_commit=args.result_commit)
        candidate = stage.strict_json(stage.git(
            repo, "show", args.result_commit + ":" + proof["result_path"]).stdout)
        require({k: candidate[k] for k in
                 ("outcome", "payload", "supplemental_operations")} == semantic,
                "published candidate does not match approved typed submission")
        require(remote_tip(repo, stage, p["submission_branch"]) ==
                args.expected_semantic_tip,
                "typed handoff withdrawn during verification")
        print(json.dumps(proof, sort_keys=True))


if __name__ == "__main__":
    main()
