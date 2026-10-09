#!/usr/bin/env python3
"""Commercial persistence / failed-Dossier handoff regression (no production data writes)."""
import copy
import json
import re
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch

import build_visual_feed_v2 as visual_builder
import progressive_personalization

import progressive_visual_activation_routing as routing
import test_progressive_visual_activation_routing as fixtures
import test_commercial_refresh as commercial_fixtures
import refresh_visual_commercial_fields as commercial


ROOT = Path(__file__).resolve().parents[1]
PRE_AI = ROOT / ".github/workflows/build-pre-ai-store-snapshot.yml"
VISUAL = ROOT / ".github/workflows/build-daily-visual-payload.yml"
PERSIST = ROOT / "scripts/persist_pre_ai_commercial.sh"


def git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, text=True, capture_output=True, check=True
    ).stdout.strip()


def test_workflow_has_durable_commercial_boundary():
    workflow = PRE_AI.read_text(encoding="utf-8")
    names = (
        "Build split ChatGPT consumer bundle",
        "Build item-level Progressive PASS 1 work",
        "Persist deterministic commercial snapshot independently of Dossier",
        "Prepare fixed daily full Steam review dossier backlog",
        "Reconcile already-present dossier inbox state",
        "Regression test fixed daily dossier snapshot control plane",
        "Recompute Progressive PASS 2 eligibility from current canonical truth",
    )
    positions = [workflow.index("      - name: " + name) for name in names]
    assert positions == sorted(positions), "Dossier must run only after commercial persistence"
    assert "bash scripts/persist_pre_ai_commercial.sh" in workflow
    visual = VISUAL.read_text(encoding="utf-8")
    assert '"Build pre-AI deterministic payload"' in visual
    assert "committed_commercial_dossier_failure_current_universe" in visual
    assert "needs.scope.outputs.failed_upstream_full == 'true'" in visual
    assert "needs.scope.outputs.failed_upstream_full != 'true'" in visual
    assert "failed_upstream_commercial" not in visual
    # Failures cannot route through stale-card-only commercial refresh.
    commercial_job = visual.split("  commercial_refresh:", 1)[1].split("  no_build_receipt:", 1)[0]
    full_job = visual.split("\n  build:", 1)[1]
    assert "needs.scope.outputs.failed_upstream_full == 'true'" not in commercial_job
    assert "needs.scope.outputs.failed_upstream_full == 'true'" in full_job
    assert "python scripts/build_final_visual_payload.py" in full_job
    assert "python scripts/visual_material_freshness_guard.py validate-visual" in full_job
    assert "python scripts/test_site_publication_resilience.py" in visual
    assert "python scripts/test_site_publication_resilience.py" in visual


def test_real_git_persistence_survives_later_dossier_error():
    script = PERSIST.read_text(encoding="utf-8")
    files = re.findall(r"^\s+(data/[\w./-]+)(?:\s*\\)?$", script, re.MULTILINE)
    assert len(files) == 15 and len(set(files)) == len(files), files
    assert "data/production/pre_ai/taste_steam_review_dossier_work.json" not in files
    assert "data/production/pre_ai/progressive_pass2_work.json" not in files
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)
        remote, local = base / "origin.git", base / "checkout"
        git(base, "init", "--bare", str(remote))
        git(base, "init", str(local))
        git(local, "config", "user.name", "test")
        git(local, "config", "user.email", "test@example.invalid")
        git(local, "branch", "-M", "main")
        git(local, "remote", "add", "origin", str(remote))
        for rel in files:
            path = local / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("old\n", encoding="utf-8")
        dossier = local / "data/production/pre_ai/taste_steam_review_dossier_work.json"
        dossier.write_text('{"last_valid":"old"}\n', encoding="utf-8")
        git(local, "add", ".")
        git(local, "commit", "-m", "baseline")
        git(local, "push", "-u", "origin", "main")

        source = "2026-10-09T00:10:00+00:00"  # fixture identity, not production timestamp
        payload = local / "data/production/pre_ai/chatgpt_payload.json"
        store = local / "data/production/pre_ai/store_snapshot.json"
        family = local / "data/production/pre_ai/family_graph.json"
        payload.write_text(json.dumps({"source_mailing_updated_at_utc": source}), encoding="utf-8")
        store.write_text(json.dumps({"status": "complete", "discovery_source_updated_at_utc": source}), encoding="utf-8")
        family.write_text(json.dumps({"status": "complete", "source_updated_at_utc": source}), encoding="utf-8")
        run = subprocess.run(["bash", str(PERSIST)], cwd=local, text=True, capture_output=True)
        assert run.returncode == 0, run.stderr + run.stdout
        assert "COMMERCIAL_PRE_AI_PERSISTED=updated" in run.stdout

        # Later strict Dossier failure must not undo the already pushed snapshot.
        dossier.write_text("invalid dossier candidate\n", encoding="utf-8")
        failure = subprocess.run(["bash", "-c", "exit 17"], cwd=local)
        assert failure.returncode == 17
        assert json.loads(git(local, "show", "origin/main:data/production/pre_ai/chatgpt_payload.json"))[
            "source_mailing_updated_at_utc"
        ] == source
        assert json.loads(git(local, "show", "origin/main:data/production/pre_ai/store_snapshot.json"))[
            "discovery_source_updated_at_utc"
        ] == source
        assert json.loads(git(local, "show", "origin/main:data/production/pre_ai/family_graph.json"))[
            "source_updated_at_utc"
        ] == source
        assert json.loads(git(local, "show", "origin/main:data/production/pre_ai/taste_steam_review_dossier_work.json")) == {
            "last_valid": "old"
        }


def test_failed_dossier_safe_commercial_fallback_only():
    original = fixtures.compatible_visual(source="OLD")
    payload = fixtures.payload(source="CURRENT")
    store = fixtures.store(source="CURRENT")
    family = fixtures.family(source="CURRENT")

    def eligible(visual, *, store_doc=store, payload_doc=payload, dossier_blob="DOSSIER", pass2_blob="PASS2"):
        return routing.commercial_fallback_eligible(
            payload=payload_doc,
            store=store_doc,
            family=family,
            visual=visual,
            progressive_context_count=719,
            dossier_work_blob=dossier_blob,
            progressive_contract_blob="CONTRACT",
            pass1_state_blob="PASS1",
            pass2_state_blob=pass2_blob,
        )

    assert eligible(original) is True
    assert eligible(original, dossier_blob="NEW-DOSSIER") is False
    assert eligible(original, pass2_blob="NEW-DEEP") is False
    assert eligible(original, store_doc=fixtures.store(source="STALE")) is False
    assert eligible(original, payload_doc=fixtures.payload(source="CURRENT", count=999)) is False
    altered = copy.deepcopy(original)
    altered["source_mailing_updated_at_utc"] = "CURRENT"
    assert eligible(altered) is False
    altered = copy.deepcopy(original)
    altered["processing_status"]["dossier_last_write_at_utc"] = None
    altered["processing_status"]["normal_visible_count"] += 1
    assert eligible(altered) is False


def test_paid_refresh_advances_commercial_not_semantic_or_dossier():
    previous = fixtures.compatible_visual(source="OLD")
    previous["items"] = [commercial_fixtures.semantic_game("game:1", "One", "1")]
    previous["source_mailing_updated_at_utc"] = "OLD"
    previous["processing_status"]["dossier_last_write_at_utc"] = "OLD-DOSSIER-WRITE"
    previous["processing_status"]["dossier_observability"] = "available"
    before_status = copy.deepcopy(previous["processing_status"])
    before_semantic = copy.deepcopy(previous["items"][0]["why_fit"])
    commercial.refresh_visual_commercial_fields(
        previous,
        payload=commercial_fixtures.payload(),
        store_snapshot=commercial_fixtures.store_snapshot(),
        family_graph=commercial_fixtures.family_graph(),
        history_snapshot=commercial_fixtures.history_snapshot(),
        now=commercial_fixtures.NOW,
    )
    assert previous["commercial_source_mailing_updated_at_utc"] == commercial_fixtures.SOURCE
    assert previous["source_mailing_updated_at_utc"] == "OLD"
    assert previous["processing_status"] == before_status
    assert previous["items"][0]["why_fit"] == before_semantic
    assert previous["items"][0]["current_price_rub"] == 100
    assert previous["items"][0]["discount_percent"] == 50



def test_failed_dossier_full_build_includes_new_not_analyzed_current_game():
    """Real canonical Phase-A visual builder, fed current deterministic GitHub data.

    A new family absent from the prior visual is intentionally NOT present in any
    Dossier, Fast, Deep or Taste cache input. No new semantic result is invented.
    """
    source = "2026-10-09T00:10:00+00:00"
    new_row = {
        "family_id": "game:300",
        "family_type": "base_game",
        "taste_subject_key": "App_300",
        "purchase": {
            "key": "App_300",
            "title": "Fresh New Game",
            "discount_percent": 70,
            "current_price_rub_display": 30,
            "original_price_rub_display": 100,
            "sale_end_utc": "2026-10-20T00:00:00+00:00",
        },
        "semantic_condition": {"base_appids": ["300"]},
        "context_only": {"wishlist": False},
    }
    current = {
        str(visual_builder.STORE_SNAPSHOT): {
            "status": "complete", "entries": {
                "App_300": {
                    "appid": "300", "title": "Fresh New Game",
                    "final_kzt": 150, "original_kzt": 500,
                    "discount_percent": 70,
                    "discount_end_utc": "2026-10-20T00:00:00+00:00",
                }
            },
        },
        str(visual_builder.FAMILY_GRAPH): {
            "status": "complete", "families": [{
                "family_id": "game:300", "family_type": "base_game",
                "base_appids": ["300"], "primary_key": "App_300",
                "alternative_purchase_keys": [],
            }],
        },
        str(visual_builder.HISTORY_SNAPSHOT): {"entries": {}},
        str(visual_builder.TASTE_PROJECTION): {"entries": {}},
        str(visual_builder.CHATGPT_PAYLOAD): {
            "source_mailing_updated_at_utc": source,
            "fx_binding": {"kzt_per_rub": 5},
            "progressive_candidate_count": 1,
        },
    }
    # Derive the new candidate's state from the *real* canonical Progressive
    # state projection with no accepted Fast/Dossier/Deep evidence. The prior
    # visual never contained game:300; Dossier did not prepare this generation.
    import progressive_pass1
    import progressive_pass2

    binding = {"family_id": "game:300", "appid": "300", "work_id": "new-work"}
    with (
        patch.object(progressive_personalization, "load_contract", return_value={}),
        patch.object(progressive_pass1, "load_state", return_value={"entries": {}}),
        patch.object(progressive_pass2, "load_state", return_value={"entries": {}}),
        patch.object(progressive_pass1, "load_jsonl", return_value=[]),
        patch.object(progressive_pass1, "current_bindings", return_value=(
            {"semantic_generation_id": "current-generation"},
            {"game:300": binding},
            {"game:300": {"title": "Fresh New Game", "appid": "300"}},
        )),
        patch.object(progressive_pass2, "current_dossier_binding", return_value={}),
        patch.object(progressive_pass2, "load_json", return_value={"items": []}),
        patch.object(progressive_pass2, "canonical_dossier_loader", return_value=None),
    ):
        projected = progressive_personalization.build_state_index(
            context_rows=[new_row], projection_doc={"entries": {}}, taste_entries={}
        )
    state = projected["game:300"]
    assert state["analysis_state"] == "not_analyzed"
    assert state["dossier_stage_state"] == "not_ready"
    assert state["deep_stage_state"] == "waiting_for_dossier"
    with tempfile.TemporaryDirectory() as td:
        output = Path(td) / "fresh-visual.json"
        with (
            patch.object(visual_builder, "OUT", output),
            patch.object(visual_builder.progressive_personalization, "load_jsonl", return_value=[new_row]),
            patch.object(visual_builder, "load_json", side_effect=lambda p: current.get(str(p), {})),
            patch.object(visual_builder, "load_content_metadata_by_appid", return_value={}),
            patch.object(visual_builder, "effective_taste_entries", return_value={}),
            patch.object(visual_builder, "load_translation_cache", return_value={}),
            patch.object(visual_builder, "resolve_description_for_appids", return_value={"summary": None}),
            patch.object(visual_builder.progressive_personalization, "build_state_index", return_value={"game:300": state}),
            patch.object(visual_builder.progressive_personalization, "build_processing_status", return_value={
                "total_current_candidates": 1, "not_analyzed_count": 1,
            }),
            patch.object(visual_builder.progressive_personalization, "validate_processing_status"),
            patch.object(visual_builder, "apply_visual_semantic_status"),
        ):
            visual_builder.main()
        published = json.loads(output.read_text(encoding="utf-8"))
    assert published["source_mailing_updated_at_utc"] == source
    assert published["item_count"] == 1
    game = published["items"][0]
    assert game["id"] == "game:300"
    assert game["analysis_state"] == "not_analyzed"
    assert game["analysis_tier"] == 3
    assert game["dossier_stage_state"] == "not_ready"
    assert game["deep_stage_state"] == "waiting_for_dossier"
    assert game["fast_stage_state"] == "not_started"
    assert game["pass1_attempted"] is False
    assert game["pass2_attempted"] is False
    assert game["effective_analysis_source"] == "none"
    assert "fit" not in game
    assert "why_fit" not in game
    assert game["current_price_rub"] == 30
    assert game["discount_percent"] == 70


def main():
    for test in (
        test_workflow_has_durable_commercial_boundary,
        test_real_git_persistence_survives_later_dossier_error,
        test_failed_dossier_safe_commercial_fallback_only,
        test_paid_refresh_advances_commercial_not_semantic_or_dossier,
        test_failed_dossier_full_build_includes_new_not_analyzed_current_game,
    ):
        test()
    print("commercial/Dossier failure isolation: 5 tests passed")


if __name__ == "__main__":
    main()
