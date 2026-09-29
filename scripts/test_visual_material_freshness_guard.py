#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import visual_material_freshness_guard as guard

HISTORICAL_BUILD_COMMIT = "53767218c890c9bdb5698d039a5651fa416c4963"
HISTORICAL_OLD_PASS2_BLOB = "4435430a967f94474c41aa77ea97374f7d276cf1"
HISTORICAL_NEW_PARENT = "dede9ea264b834819642b6e23f778cabd85a4fdd"
HISTORICAL_NEW_PASS2_BLOB = "b1967e420ef55cc3c2368f25f71ef99df8041aec"
PASS2_PATH = "data/cache/progressive_pass2_state.json"
DOSSIER_PATH = "data/production/pre_ai/taste_steam_review_dossier_work.json"


def run(repo: Path, *args: str) -> str:
    return subprocess.check_output(list(args), cwd=repo, text=True).strip()


def git(repo: Path, *args: str) -> str:
    return run(repo, "git", *args)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def seed_material_files(repo: Path, tag: str) -> None:
    for path in guard.unique_material_paths():
        write(repo / path, f"{path}\n{tag}\n")


def commit_all(repo: Path, message: str) -> str:
    subprocess.check_call(["git", "add", "-A"], cwd=repo)
    subprocess.check_call(["git", "commit", "-q", "-m", message], cwd=repo)
    return git(repo, "rev-parse", "HEAD")


def make_repo(root: Path) -> Path:
    repo = root / "repo"
    repo.mkdir()
    subprocess.check_call(["git", "init", "-q", "-b", "main"], cwd=repo)
    subprocess.check_call(["git", "config", "user.name", "test"], cwd=repo)
    subprocess.check_call(["git", "config", "user.email", "test@example.com"], cwd=repo)
    seed_material_files(repo, "old")
    write(
        repo / "data/production/pre_ai/chatgpt_payload.json",
        json.dumps({
            "profile_binding": {
                "canonical_profile_blob_sha": "profile-old",
                "taste_model_version": "taste-v3",
            }
        }) + "\n",
    )
    write(repo / "unrelated.txt", "old\n")
    commit_all(repo, "seed")
    return repo


def visual_for_state(state: dict) -> dict:
    return {
        "schema_version": 5,
        "status": "complete",
        "production_contract": {
            **{
                key: spec["blob_sha"]
                for key, spec in state["visual_contract_bindings"].items()
            },
            **state["derived_visual_bindings"],
        },
        "items": [],
    }


def test_historical_pinned_pass2_proof(repo_root: Path) -> None:
    old = git(repo_root, "rev-parse", f"{HISTORICAL_BUILD_COMMIT}:{PASS2_PATH}")
    new = git(repo_root, "rev-parse", f"{HISTORICAL_NEW_PARENT}:{PASS2_PATH}")
    assert old == HISTORICAL_OLD_PASS2_BLOB
    assert new == HISTORICAL_NEW_PASS2_BLOB
    assert old != new


def test_unrelated_head_movement_is_allowed() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        state = guard.capture_state(repo)
        base = state["build_parent_commit_sha"]

        write(repo / "unrelated.txt", "new\n")
        commit_all(repo, "unrelated move")
        assert guard.compare_parent(state, repo, "HEAD") == []
        assert git(repo, "rev-parse", "HEAD") != base


def test_pass2_material_drift_blocks_stale_rebase() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        state = guard.capture_state(repo)
        visual_path = repo / guard.VISUAL_PATH
        visual_path.parent.mkdir(parents=True, exist_ok=True)
        visual_path.write_text(json.dumps(visual_for_state(state)), encoding="utf-8")
        guard.validate_visual_binding(state, visual_path)

        write(repo / PASS2_PATH, "new-pass2-state\n")
        commit_all(repo, "advance pass2")
        drift = guard.compare_parent(state, repo, "HEAD")
        assert any(row["path"] == PASS2_PATH for row in drift)

        try:
            guard.verify_ref_matches_build_state(state, repo, "HEAD")
        except guard.MaterialDrift as exc:
            assert PASS2_PATH in str(exc)
        else:
            raise AssertionError("historical-style stale PASS2 state was accepted on a newer material parent")


def test_concurrent_dossier_or_deep_write_is_material() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        state = guard.capture_state(repo)
        write(repo / DOSSIER_PATH, "new-dossier-state\n")
        write(repo / PASS2_PATH, "new-deep-state\n")
        commit_all(repo, "concurrent dossier deep advance")
        changed = {row["path"] for row in guard.compare_parent(state, repo, "HEAD")}
        assert DOSSIER_PATH in changed
        assert PASS2_PATH in changed


def test_rebuild_state_then_second_material_drift_fails_closed() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        old = guard.capture_state(repo)
        write(repo / PASS2_PATH, "first-advance\n")
        commit_all(repo, "first advance")
        assert guard.compare_parent(old, repo, "HEAD")

        rebuilt = guard.capture_state(repo)
        write(repo / DOSSIER_PATH, "second-advance\n")
        commit_all(repo, "second advance")
        drift = guard.compare_parent(rebuilt, repo, "HEAD")
        assert any(row["path"] == DOSSIER_PATH for row in drift)


def test_visual_binding_uses_exact_build_bytes() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        duration = repo / "data/cache/duration_estimates.json"
        duration.write_text("producer-owned-refresh\n", encoding="utf-8")
        state = guard.capture_state(repo)
        assert (
            state["build_blob_shas"]["data/cache/duration_estimates.json"]
            != state["parent_blob_shas"]["data/cache/duration_estimates.json"]
        )

        visual_path = repo / guard.VISUAL_PATH
        visual_path.parent.mkdir(parents=True, exist_ok=True)
        visual = visual_for_state(state)
        visual_path.write_text(json.dumps(visual), encoding="utf-8")
        guard.validate_visual_binding(state, visual_path)

        visual["production_contract"]["progressive_pass2_state_blob_sha"] = "stale"
        visual_path.write_text(json.dumps(visual), encoding="utf-8")
        try:
            guard.validate_visual_binding(state, visual_path)
        except guard.MaterialDrift as exc:
            assert "progressive_pass2_state_blob_sha" in str(exc)
        else:
            raise AssertionError("stale visual provenance was accepted")


def test_workflow_has_guarded_rebuild_path(repo_root: Path) -> None:
    workflow = (repo_root / ".github/workflows/build-daily-visual-payload.yml").read_text(encoding="utf-8")
    required = (
        "visual_material_freshness_guard.py capture",
        "visual_material_freshness_guard.py validate-visual",
        "visual_material_freshness_guard.py compare-parent",
        "MATERIAL_DRIFT_REBUILD=true",
        "material_source_drift_after_rebuild",
        "python scripts/build_ranking_review.py",
    )
    for token in required:
        assert token in workflow, token


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    test_historical_pinned_pass2_proof(repo_root)
    test_unrelated_head_movement_is_allowed()
    test_pass2_material_drift_blocks_stale_rebase()
    test_concurrent_dossier_or_deep_write_is_material()
    test_rebuild_state_then_second_material_drift_fails_closed()
    test_visual_binding_uses_exact_build_bytes()
    test_workflow_has_guarded_rebuild_path(repo_root)
    print("VISUAL_MATERIAL_FRESHNESS_GUARD_TESTS=PASS")


if __name__ == "__main__":
    main()
