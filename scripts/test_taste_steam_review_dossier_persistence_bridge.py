#!/usr/bin/env python3
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from ingest_taste_steam_review_dossier_inbox import ingest_inbox_submission
from taste_steam_review_dossier import canonical_sha256
from taste_steam_review_dossier_daily import build_daily_work_manifest, load_contract

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "config/taste_steam_review_dossier_contract.json"
BRIDGE_PATH = ROOT / "config/taste_steam_review_dossier_persistence_bridge.json"
WORKFLOW_PATH = ROOT / ".github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml"
PROMPT_PATH = ROOT / "config/taste_steam_review_dossier_worker_prompt.md"


@contextmanager
def cwd(path):
    old = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_queue(count):
    return [
        {
            "key": f"App_{100000 + i}",
            "appid": str(100000 + i),
            "title": f"Synthetic {i}",
            "taste_fingerprint": f"taste-{i}",
            "candidate_context_sha256": canonical_sha256({"i": i}),
            "work_required": ["evaluate_taste_fit"],
        }
        for i in range(count)
    ]


def make_dossier(item, ttl_days=20, generated=None):
    generated = generated or datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc)
    expires = generated + timedelta(days=ttl_days)
    digest = canonical_sha256([item["appid"], "synthetic-review-sample"])
    return {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-V1",
        "schema_version": 1,
        "appid": str(item["appid"]),
        "title": item["title"],
        "generated_at_utc": generated.isoformat(),
        "expires_at_utc": expires.isoformat(),
        "ttl_days": ttl_days,
        "summary": "Synthetic neutral dossier used only for deterministic persistence bridge acceptance.",
        "observations": [
            {
                "category": "mechanics",
                "statement": "Synthetic observation for bridge validation only.",
                "sentiment": "neutral",
                "recurrence": "anecdotal",
                "mention_count": 1,
                "evidence_languages": ["store"],
            }
        ],
        "conflicts": [],
        "review_sample": {
            "strategy": "adaptive_stability",
            "sampled_russian": 0,
            "sampled_non_russian": 0,
            "sampled_total": 0,
            "sample_ids_sha256": digest,
            "lanes": [
                {"language_scope": "russian", "sampled": 0, "batches": 0, "stop_reason": "synthetic_fixture"},
                {"language_scope": "non_russian", "sampled": 0, "batches": 0, "stop_reason": "synthetic_fixture"},
            ],
        },
        "provenance": {
            "store_description": {
                "url": f"https://store.steampowered.com/app/{item['appid']}/",
                "content_sha256": canonical_sha256({"store": item["appid"]}),
            },
            "steam_reviews": {
                "url": f"https://store.steampowered.com/app/{item['appid']}/#app_reviews_hash",
                "capture_note": "synthetic acceptance fixture",
            },
        },
    }


def make_submission(manifest, docs=None):
    docs = docs if docs is not None else [make_dossier(item, manifest["ttl_days"]) for item in manifest["current_checkpoint_items"]]
    return {
        "schema": "TASTE-STEAM-REVIEW-DOSSIER-SUBMISSION-V1",
        "schema_version": 1,
        "snapshot_id": manifest["snapshot_id"],
        "scope_sha256": manifest["scope_sha256"],
        "scope_source": manifest["scope_source"],
        "source_queue_sha256": manifest["source_queue_sha256"],
        "dossiers": docs,
    }


def submission_path(submission):
    return Path("data/ai_inbox/taste_steam_review_dossiers") / f"{submission['snapshot_id']}--{submission['scope_sha256']}.json"


def setup_repo(tmp, count=25):
    tmp = Path(tmp)
    contract_target = tmp / "config/taste_steam_review_dossier_contract.json"
    contract_target.parent.mkdir(parents=True, exist_ok=True)
    contract_target.write_text(CONTRACT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    contract = load_contract(contract_target)
    store = tmp / "data/cache/taste_steam_review_dossiers"
    manifest = build_daily_work_manifest(
        make_queue(count),
        contract,
        store,
        now=datetime(2026, 9, 14, 0, 0, tzinfo=timezone.utc),
        source_queue_path=contract["paths"]["taste_queue"],
    )
    manifest_path = tmp / "data/production/pre_ai/taste_steam_review_dossier_work.json"
    write_json(manifest_path, manifest)
    return contract, store, manifest_path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def submit_current(manifest_path, store):
    manifest = read_json(manifest_path)
    submission = make_submission(manifest)
    path = submission_path(submission)
    write_json(path, submission)
    result = ingest_inbox_submission(
        path,
        manifest_path=manifest_path,
        contract_path="config/taste_steam_review_dossier_contract.json",
        store_dir=store,
    )
    assert not path.exists()
    return result, read_json(manifest_path), submission


def expect_rejected(manifest_path, store, submission):
    before_manifest = read_json(manifest_path)
    before_files = sorted(p.name for p in Path(store).glob("*.json"))
    path = submission_path(submission)
    write_json(path, submission)
    try:
        ingest_inbox_submission(
            path,
            manifest_path=manifest_path,
            contract_path="config/taste_steam_review_dossier_contract.json",
            store_dir=store,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("submission unexpectedly accepted")
    assert path.exists(), "rejected submission must not be mistaken for accepted cleanup"
    assert read_json(manifest_path) == before_manifest
    assert sorted(p.name for p in Path(store).glob("*.json")) == before_files
    path.unlink()


def test_progress_and_resume():
    with tempfile.TemporaryDirectory() as td, cwd(td):
        _, store, manifest_path = setup_repo(td, 25)
        initial = read_json(manifest_path)
        snapshot = initial["snapshot_id"]
        assert initial["remaining_required_count"] == 25
        assert initial["current_checkpoint_count"] == 10

        result1, after1, first_submission = submit_current(manifest_path, store)
        assert result1["persisted_count"] == 10
        assert after1["snapshot_id"] == snapshot
        assert after1["remaining_required_count"] == 15
        assert after1["completed_required_count"] == 10
        assert [x["appid"] for x in after1["current_checkpoint_items"]] == [str(100010 + i) for i in range(10)]

        replay = json.loads(json.dumps(first_submission))
        expect_rejected(manifest_path, store, replay)

        result2, after2, _ = submit_current(manifest_path, store)
        assert result2["persisted_count"] == 10
        assert after2["snapshot_id"] == snapshot
        assert after2["remaining_required_count"] == 5
        assert after2["completed_required_count"] == 20

        result3, after3, _ = submit_current(manifest_path, store)
        assert result3["persisted_count"] == 5
        assert after3["snapshot_id"] == snapshot
        assert after3["remaining_required_count"] == 0
        assert after3["completed_required_count"] == 25
        assert after3["full_backlog_complete"] is True
        assert len(list(Path(store).glob("*.json"))) == 25


def test_fail_closed_matrix():
    with tempfile.TemporaryDirectory() as td, cwd(td):
        _, store, manifest_path = setup_repo(td, 25)
        manifest = read_json(manifest_path)

        partial = make_submission(manifest, [make_dossier(x, manifest["ttl_days"]) for x in manifest["current_checkpoint_items"][:-1]])
        expect_rejected(manifest_path, store, partial)

        wrong_snapshot = make_submission(manifest)
        wrong_snapshot["snapshot_id"] = "0" * 64
        write_json(submission_path(wrong_snapshot), wrong_snapshot)
        bad_path = submission_path(wrong_snapshot)
        try:
            ingest_inbox_submission(bad_path, manifest_path=manifest_path, contract_path="config/taste_steam_review_dossier_contract.json", store_dir=store)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong snapshot accepted")
        bad_path.unlink()

        wrong_scope = make_submission(manifest)
        wrong_scope["scope_sha256"] = "1" * 64
        write_json(submission_path(wrong_scope), wrong_scope)
        bad_path = submission_path(wrong_scope)
        try:
            ingest_inbox_submission(bad_path, manifest_path=manifest_path, contract_path="config/taste_steam_review_dossier_contract.json", store_dir=store)
        except ValueError:
            pass
        else:
            raise AssertionError("wrong checkpoint binding accepted")
        bad_path.unlink()

        missing_appid_docs = [make_dossier(x, manifest["ttl_days"]) for x in manifest["current_checkpoint_items"]]
        missing_appid_docs.pop(3)
        missing_appid = make_submission(manifest, missing_appid_docs)
        expect_rejected(manifest_path, store, missing_appid)

        invalid_docs = [make_dossier(x, manifest["ttl_days"]) for x in manifest["current_checkpoint_items"]]
        invalid_docs[0]["summary"] = "too short"
        invalid = make_submission(manifest, invalid_docs)
        expect_rejected(manifest_path, store, invalid)

        _, after1, _ = submit_current(manifest_path, store)
        before_failed_later = json.loads(json.dumps(after1))
        invalid_later_docs = [make_dossier(x, after1["ttl_days"]) for x in after1["current_checkpoint_items"]]
        invalid_later_docs[0]["schema"] = "INVALID"
        invalid_later = make_submission(after1, invalid_later_docs)
        expect_rejected(manifest_path, store, invalid_later)
        assert read_json(manifest_path) == before_failed_later
        assert len(list(Path(store).glob("*.json"))) == 10


def test_path_binding_and_static_route():
    bridge = json.loads(BRIDGE_PATH.read_text(encoding="utf-8"))
    assert bridge["submission"]["action"] == "github_contents_create_file"
    assert bridge["submission"]["mode"] == "create_only"
    assert bridge["ingest"]["canonical_ingest"] == "scripts/ingest_taste_steam_review_dossiers.py"
    assert bridge["ingest"]["same_snapshot_only"] is True
    assert bridge["ingest"]["source_queue_reread"] is False

    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    assert 'data/ai_inbox/taste_steam_review_dossiers/*.json' in workflow
    assert "workflow_dispatch" not in workflow
    assert "ingest_taste_steam_review_dossier_inbox.py" in workflow
    assert "data/cache/taste_steam_review_dossiers" in workflow
    assert "taste_steam_review_dossier_work.json" in workflow
    assert "ingest-taste-batch.yml" not in workflow

    prompt = PROMPT_PATH.read_text(encoding="utf-8")
    assert "GitHub **create-file** action" in prompt
    assert "Branch: `main`" in prompt
    assert "{snapshot_id}--{scope_sha256}.json" in prompt
    assert "Never update, overwrite, delete, or directly edit `data/cache/taste_steam_review_dossiers/**`" in prompt


def main():
    tests = [test_progress_and_resume, test_fail_closed_matrix, test_path_binding_and_static_route]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)} dossier persistence bridge test groups")


if __name__ == "__main__":
    main()
