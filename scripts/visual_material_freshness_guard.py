#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
CONTRACT = "FULL-VISUAL-MATERIAL-STATE-V1"
VISUAL_PATH = "data/production/visual/current.json"

# These are the exact repository files whose immutable blob identities are already
# projected into the full visual production_contract and therefore materially bind
# one deterministic full build. Duplicate source paths are intentional where the
# contract exposes both general and scoped provenance keys.
FULL_VISUAL_MATERIAL_BINDINGS: dict[str, str] = {
    "visual_builder_blob_sha": "scripts/build_visual_feed_v2.py",
    "final_visual_producer_blob_sha": "scripts/build_final_visual_payload.py",
    "card_explanation_policy_blob_sha": "scripts/card_explanation_policy.py",
    "play_priority_context_helper_blob_sha": "scripts/play_priority_context.py",
    "play_priority_context_contract_blob_sha": "config/play_priority_context_contract.json",
    "achievement_quality_builder_blob_sha": "scripts/achievement_quality.py",
    "ranking_helper_blob_sha": "scripts/priority_ranking.py",
    "ranking_policy_blob_sha": "config/final_ranking_policy.json",
    "refinement_helper_blob_sha": "scripts/refine_visual_ranking.py",
    "duration_enrichment_helper_blob_sha": "scripts/duration_enrichment.py",
    "duration_enrichment_contract_blob_sha": "config/duration_enrichment_contract.json",
    "duration_cache_blob_sha": "data/cache/duration_estimates.json",
    "fixed_package_helper_blob_sha": "scripts/apply_fixed_package_purchase_options.py",
    "fixed_package_options_blob_sha": "data/production/pre_ai/fixed_package_options.json",
    "purchase_equivalence_blob_sha": "config/purchase_equivalence_overrides.json",
    "source_chatgpt_payload_blob_sha": "data/production/pre_ai/chatgpt_payload.json",
    "commercial_source_payload_blob_sha": "data/production/pre_ai/chatgpt_payload.json",
    "commercial_source_store_snapshot_blob_sha": "data/production/pre_ai/store_snapshot.json",
    "commercial_source_family_graph_blob_sha": "data/production/pre_ai/family_graph.json",
    "commercial_source_history_snapshot_blob_sha": "data/production/pre_ai/history_snapshot.json",
    "source_purchase_context_blob_sha": "data/production/pre_ai/chatgpt_purchase_context.jsonl",
    "source_progressive_candidate_context_blob_sha": "data/production/pre_ai/progressive_candidate_context.jsonl",
    "source_taste_steam_review_dossier_work_blob_sha": "data/production/pre_ai/taste_steam_review_dossier_work.json",
    "source_russian_description_status_blob_sha": "data/production/pre_ai/chatgpt_ru_description_status.json",
    "russian_description_translation_contract_blob_sha": "config/russian_description_translation_contract.json",
    "progressive_personalization_contract_blob_sha": "config/progressive_personalization_contract.json",
    "progressive_pass1_contract_blob_sha": "config/progressive_pass1_contract.json",
    "progressive_pass1_state_blob_sha": "data/cache/progressive_pass1_state.json",
    "progressive_pass2_contract_blob_sha": "config/progressive_pass2_contract.json",
    "progressive_pass2_state_blob_sha": "data/cache/progressive_pass2_state.json",
    "source_taste_queue_blob_sha": "data/production/pre_ai/chatgpt_taste_queue.jsonl",
    "source_history_snapshot_blob_sha": "data/production/pre_ai/history_snapshot.json",
    "giveaway_visual_handoff_blob_sha": "scripts/giveaway_visual_handoff.py",
    "source_giveaway_snapshot_blob_sha": "data/production/giveaways/v1/current.json",
}


class MaterialDrift(RuntimeError):
    pass


def _git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _blob_at_ref(repo: Path, ref: str, path: str) -> str:
    try:
        return _git(repo, "rev-parse", f"{ref}:{path}")
    except subprocess.CalledProcessError as exc:
        raise MaterialDrift(f"missing material path at {ref}: {path}") from exc


def _working_blob(repo: Path, path: str) -> str:
    file_path = repo / path
    if not file_path.is_file():
        raise MaterialDrift(f"missing material path in working tree: {path}")
    return _git(repo, "hash-object", path)


def unique_material_paths() -> tuple[str, ...]:
    return tuple(sorted(set(FULL_VISUAL_MATERIAL_BINDINGS.values())))


def capture_state(repo: Path) -> dict[str, Any]:
    parent = _git(repo, "rev-parse", "HEAD")
    parent_blobs = {path: _blob_at_ref(repo, "HEAD", path) for path in unique_material_paths()}
    build_blobs = {path: _working_blob(repo, path) for path in unique_material_paths()}
    payload = json.loads((repo / "data/production/pre_ai/chatgpt_payload.json").read_text(encoding="utf-8"))
    profile_binding = payload.get("profile_binding") or {}
    derived_visual_bindings = {
        "canonical_profile_blob_sha": profile_binding.get("canonical_profile_blob_sha"),
        "taste_model_version": profile_binding.get("taste_model_version"),
    }
    if not all(derived_visual_bindings.values()):
        raise MaterialDrift("missing canonical profile/taste model binding in chatgpt payload")
    return {
        "schema_version": SCHEMA_VERSION,
        "contract": CONTRACT,
        "build_parent_commit_sha": parent,
        "parent_blob_shas": parent_blobs,
        "build_blob_shas": build_blobs,
        "visual_contract_bindings": {
            key: {
                "path": path,
                "blob_sha": build_blobs[path],
            }
            for key, path in FULL_VISUAL_MATERIAL_BINDINGS.items()
        },
        "derived_visual_bindings": derived_visual_bindings,
    }


def load_state(path: Path) -> dict[str, Any]:
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("schema_version") != SCHEMA_VERSION or state.get("contract") != CONTRACT:
        raise MaterialDrift("unsupported full visual material state")
    return state


def compare_parent(state: dict[str, Any], repo: Path, candidate_ref: str) -> list[dict[str, str]]:
    baseline = state.get("parent_blob_shas") or {}
    drift: list[dict[str, str]] = []
    for path in unique_material_paths():
        expected = baseline.get(path)
        actual = _blob_at_ref(repo, candidate_ref, path)
        if expected != actual:
            drift.append({"path": path, "build_parent_blob_sha": expected, "candidate_blob_sha": actual})
    return drift


def validate_visual_binding(state: dict[str, Any], visual_path: Path) -> None:
    visual = json.loads(visual_path.read_text(encoding="utf-8"))
    contract = visual.get("production_contract") or {}
    bindings = state.get("visual_contract_bindings") or {}
    mismatches = []
    for key, spec in bindings.items():
        expected = spec.get("blob_sha")
        actual = contract.get(key)
        if actual != expected:
            mismatches.append(
                {
                    "contract_key": key,
                    "path": spec.get("path"),
                    "expected_blob_sha": expected,
                    "visual_blob_sha": actual,
                }
            )
    for key, expected in (state.get("derived_visual_bindings") or {}).items():
        actual = contract.get(key)
        if actual != expected:
            mismatches.append(
                {
                    "contract_key": key,
                    "path": "derived:chatgpt_payload.profile_binding",
                    "expected_blob_sha": expected,
                    "visual_blob_sha": actual,
                }
            )
    if mismatches:
        first = mismatches[0]
        raise MaterialDrift(
            "visual material binding mismatch: "
            f"key={first['contract_key']} path={first['path']} "
            f"expected={first['expected_blob_sha']} actual={first['visual_blob_sha']} "
            f"count={len(mismatches)}"
        )


def verify_ref_matches_build_state(state: dict[str, Any], repo: Path, ref: str) -> None:
    expected = state.get("build_blob_shas") or {}
    mismatches = []
    for path in unique_material_paths():
        actual = _blob_at_ref(repo, ref, path)
        if actual != expected.get(path):
            mismatches.append((path, expected.get(path), actual))
    if mismatches:
        path, wanted, actual = mismatches[0]
        raise MaterialDrift(
            f"persisted material state mismatch: path={path} expected={wanted} actual={actual} count={len(mismatches)}"
        )


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    capture = sub.add_parser("capture")
    capture.add_argument("--repo", default=".")
    capture.add_argument("--output", required=True)

    compare = sub.add_parser("compare-parent")
    compare.add_argument("--repo", default=".")
    compare.add_argument("--state", required=True)
    compare.add_argument("--candidate-ref", required=True)

    validate = sub.add_parser("validate-visual")
    validate.add_argument("--repo", default=".")
    validate.add_argument("--state", required=True)
    validate.add_argument("--visual", default=VISUAL_PATH)

    verify = sub.add_parser("verify-ref")
    verify.add_argument("--repo", default=".")
    verify.add_argument("--state", required=True)
    verify.add_argument("--ref", required=True)

    args = parser.parse_args()
    repo = Path(args.repo).resolve()

    try:
        if args.command == "capture":
            state = capture_state(repo)
            _write(Path(args.output), state)
            print(
                "VISUAL_MATERIAL_CAPTURE=pass "
                f"parent={state['build_parent_commit_sha']} "
                f"pass2={state['visual_contract_bindings']['progressive_pass2_state_blob_sha']['blob_sha']}"
            )
            return

        state = load_state(Path(args.state))
        if args.command == "compare-parent":
            drift = compare_parent(state, repo, args.candidate_ref)
            if drift:
                print("VISUAL_MATERIAL_DRIFT=true " + json.dumps(drift, ensure_ascii=False, separators=(",", ":")))
                raise SystemExit(42)
            print(f"VISUAL_MATERIAL_DRIFT=false candidate_ref={args.candidate_ref}")
            return

        if args.command == "validate-visual":
            validate_visual_binding(state, Path(args.visual))
            print("VISUAL_MATERIAL_BINDING=pass")
            return

        verify_ref_matches_build_state(state, repo, args.ref)
        print(f"VISUAL_PERSISTED_MATERIAL_BINDING=pass ref={args.ref}")
    except MaterialDrift as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
