#!/usr/bin/env python3
import copy
import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from build_taste_steam_review_dossier_work import build_or_preserve_daily_work
from taste_steam_review_dossier_buffered import (
    expected_buffer_path,
    plan_buffered_drain,
    validate_buffer_artifact,
)
from taste_steam_review_dossier_daily import BUFFER_GROUP_SCHEMA, load_contract
from taste_steam_review_dossier_prepublication import validate_prepublication_artifact
from taste_steam_review_dossier_strict import (
    current_worker_contract_binding,
    load_web_evidence_contract,
    load_worker_schema,
    validate_dossier_strict,
)
from taste_steam_review_dossier_test_fixture import web_dossier
from taste_steam_review_dossier_web import build_daily_work_manifest_web
from taste_steam_review_dossier_worker_projection import build_worker_projection

ROOT = Path(__file__).resolve().parents[1]
BASE_CONTRACT = load_contract(ROOT / "config/taste_steam_review_dossier_contract.json")
SCHEMA = load_worker_schema(ROOT / "config/taste_steam_review_dossier_schema.json")
EVIDENCE = load_web_evidence_contract(ROOT / "config/taste_steam_review_dossier_web_evidence_contract.json")


def queue(appids):
    return [{
        "taste_subject_key": f"App_{appid}_{index}",
        "appid": str(appid),
        "title": f"Game {appid}",
        "taste_fingerprint": hashlib.sha256(f"taste:{appid}:{index}".encode()).hexdigest(),
        "candidate_context_sha256": hashlib.sha256(f"ctx:{appid}:{index}".encode()).hexdigest(),
        "work_required": ["resolve_grounded_negative_analysis"],
    } for index, appid in enumerate(appids)]


def contract_for(td):
    contract = copy.deepcopy(BASE_CONTRACT)
    root = Path(td)
    contract["paths"]["submission_inbox_dir"] = (root / "buffer").as_posix()
    contract["paths"]["work_manifest"] = (root / "work.json").as_posix()
    contract["paths"]["worker_index"] = (root / "worker_index.json").as_posix()
    contract["paths"]["worker_groups_root"] = (root / "worker_groups").as_posix()
    contract["worker_read_projection"]["canonical_source"] = contract["paths"]["work_manifest"]
    contract["worker_read_projection"]["descriptor_path_template"] = (
        contract["paths"]["worker_groups_root"] + "/{snapshot_id}/g{sequence:06d}.json"
    )
    return contract


def buffered_artifact(work, sequence, *, generated=None):
    descriptor = work["submission_group_plan"]["groups"][sequence - 1]
    when = generated or datetime.now(timezone.utc).replace(microsecond=0)
    return {
        "schema": BUFFER_GROUP_SCHEMA,
        "schema_version": 1,
        **copy.deepcopy(descriptor),
        "dossiers": [web_dossier(item["appid"], when, title=item["title"]) for item in descriptor["items"]],
    }


class ContractGapRegressionTests(unittest.TestCase):
    def validate(self, doc, *, now=None):
        now = now or datetime.now(timezone.utc).replace(microsecond=0)
        return validate_dossier_strict(
            doc,
            BASE_CONTRACT,
            expected_appid=doc["appid"],
            expected_title=doc["title"],
            expected_ttl_days=20,
            now=now,
        )

    def test_gap01_expired_group_fails_shared_prepublication_and_canonical_buffer_validation_without_progress(self):
        with tempfile.TemporaryDirectory() as td:
            now = datetime.now(timezone.utc).replace(microsecond=0)
            contract = contract_for(td)
            work = build_daily_work_manifest_web(queue([510001, 510002, 510003]), contract, Path(td) / "store", now=now)
            descriptor = work["submission_group_plan"]["groups"][0]
            artifact = buffered_artifact(work, 1, generated=now)
            artifact["dossiers"][0] = web_dossier(
                descriptor["items"][0]["appid"],
                now - timedelta(days=21),
                title=descriptor["items"][0]["title"],
            )
            with self.assertRaisesRegex(ValueError, "already-expired dossier"):
                validate_prepublication_artifact(copy.deepcopy(artifact), work, contract)
            with self.assertRaisesRegex(ValueError, "already-expired dossier"):
                validate_buffer_artifact(copy.deepcopy(artifact), descriptor, work, contract)

            path = expected_buffer_path(descriptor, contract)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(artifact), encoding="utf-8")
            plan = plan_buffered_drain(work, contract, contract["paths"]["submission_inbox_dir"])
            self.assertEqual(plan["accepted_count"], 0)
            self.assertEqual(plan["failed_count"], 1)
            self.assertEqual(plan["next_manifest"]["group_progress"]["groups"][0]["state"], "failed_or_invalid_pending_recovery")
            self.assertEqual(plan["next_manifest"]["completed_required_count"], 0)

    def test_gap02_feedback_url_aliases_cannot_double_count_but_distinct_items_same_thread_pass(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        alias = web_dossier(520001, now)
        alias["provenance"]["player_feedback_records"].append({
            "feedback_id": "feedback-005",
            "source_id": "source-003",
            "url": alias["provenance"]["player_feedback_records"][3]["url"] + "?utm_source=share#fragment",
            "publication_date": now.date().isoformat(),
            "language": "russian",
        })
        with self.assertRaisesRegex(ValueError, "duplicate or aliased attributable player-feedback item"):
            self.validate(alias, now=now)

        distinct = web_dossier(520002, now)
        distinct["provenance"]["player_feedback_records"].append({
            "feedback_id": "feedback-005",
            "source_id": "source-003",
            "url": "https://www.reddit.com/r/games/comments/test520002/game_520002/comment2/",
            "publication_date": now.date().isoformat(),
            "language": "russian",
        })
        distinct["observations"][1]["recurrence"] = "limited"
        distinct["observations"][1]["mention_count"] = 2
        distinct["observations"][1]["player_feedback_ids"] = ["feedback-004", "feedback-005"]
        self.assertIs(self.validate(distinct, now=now), distinct)

    def test_gap02_source_aliases_cannot_fake_multi_source_diversity(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        doc = web_dossier(520003, now)
        alias_source = copy.deepcopy(doc["provenance"]["sources"][2])
        alias_source["source_id"] = "source-004"
        alias_source["url"] += "?utm_campaign=x#top"
        doc["provenance"]["sources"].append(alias_source)
        with self.assertRaisesRegex(ValueError, "duplicate or aliased provenance source"):
            self.validate(doc, now=now)

    def test_gap03_collection_search_or_vague_locator_cannot_be_feedback_item(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        collection = web_dossier(530001, now)
        collection["provenance"]["player_feedback_records"][3]["url"] = "https://www.reddit.com/r/games/"
        with self.assertRaisesRegex(ValueError, "one attributable feedback item"):
            self.validate(collection, now=now)

        search = web_dossier(530002, now)
        search["provenance"]["player_feedback_records"][3]["url"] = "https://www.reddit.com/search/?q=game"
        with self.assertRaisesRegex(ValueError, "one attributable feedback item"):
            self.validate(search, now=now)

        vague = web_dossier(530003, now)
        vague_record = vague["provenance"]["player_feedback_records"][3]
        vague_record.pop("url")
        vague_record["public_ref"] = "Steam review found on 2026-09-16"
        with self.assertRaisesRegex(ValueError, "stable non-identifying feedback item locator"):
            self.validate(vague, now=now)

    def test_gap04_dated_freshness_is_mechanical_at_365_day_boundary(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        exact = web_dossier(540001, now)
        exact_date = (now.date() - timedelta(days=365)).isoformat()
        exact["provenance"]["sources"][1]["publication_date"] = exact_date
        exact["provenance"]["sources"][1]["freshness"] = "recent"
        for record in exact["provenance"]["player_feedback_records"]:
            if record["source_id"] == "source-002":
                record["publication_date"] = exact_date
        self.assertIs(self.validate(exact, now=now), exact)

        too_old = web_dossier(540002, now)
        too_old["provenance"]["sources"][1]["publication_date"] = (now.date() - timedelta(days=366)).isoformat()
        too_old["provenance"]["sources"][1]["freshness"] = "recent"
        with self.assertRaisesRegex(ValueError, "freshness is incoherent"):
            self.validate(too_old, now=now)
        too_old["provenance"]["sources"][1]["freshness"] = "older"
        self.assertIs(self.validate(too_old, now=now), too_old)

        false_current = web_dossier(540003, now)
        false_current["provenance"]["sources"][2]["publication_date"] = (now.date() - timedelta(days=800)).isoformat()
        with self.assertRaisesRegex(ValueError, "freshness is incoherent"):
            self.validate(false_current, now=now)

    def test_gap05_russian_attempt_is_bidirectional(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        valid = web_dossier(550001, now)
        self.assertIs(self.validate(valid, now=now), valid)
        doc = web_dossier(550002, now)
        doc["evidence"]["russian_attempt"] = "searched_no_existence_signal"
        with self.assertRaisesRegex(ValueError, "requires russian_attempt=found_and_used"):
            self.validate(doc, now=now)

    def test_gap06_conflict_recurrence_requires_bound_player_feedback(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        valid = web_dossier(560001, now)
        valid["conflicts"] = [{
            "statement": "Players report materially different experiences with the same durable mechanic.",
            "recurrence": "moderate",
            "mention_count": 3,
            "source_ids": ["source-002"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003"],
        }]
        self.assertIs(self.validate(valid, now=now), valid)

        official_only = web_dossier(560002, now)
        official_only["conflicts"] = [{
            "statement": "Official context alone must not establish strong player conflict recurrence.",
            "recurrence": "strong",
            "mention_count": 3,
            "source_ids": ["source-001"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003"],
        }]
        with self.assertRaises(ValueError):
            self.validate(official_only, now=now)

        inflated = web_dossier(560003, now)
        inflated["conflicts"] = [{
            "statement": "Three player records cannot mechanically establish strong recurrence.",
            "recurrence": "strong",
            "mention_count": 3,
            "source_ids": ["source-002"],
            "player_feedback_ids": ["feedback-001", "feedback-002", "feedback-003"],
        }]
        with self.assertRaisesRegex(ValueError, "recurrence exceeds bound player-feedback support"):
            self.validate(inflated, now=now)

    def test_gap07_content_complete_binding_changes_on_schema_contract_or_prompt_content(self):
        prompt = (ROOT / "config/taste_steam_review_dossier_worker_prompt.md").read_text(encoding="utf-8")
        baseline = current_worker_contract_binding(SCHEMA, EVIDENCE, worker_prompt_text=prompt)

        schema_changed = copy.deepcopy(SCHEMA)
        schema_changed["purpose"] += " semantic-change-without-version-bump"
        self.assertNotEqual(
            baseline["worker_schema_sha256"],
            current_worker_contract_binding(schema_changed, EVIDENCE, worker_prompt_text=prompt)["worker_schema_sha256"],
        )

        contract_changed = copy.deepcopy(EVIDENCE)
        contract_changed["purpose"] += " semantic-change-without-version-bump"
        self.assertNotEqual(
            baseline["evidence_contract_sha256"],
            current_worker_contract_binding(SCHEMA, contract_changed, worker_prompt_text=prompt)["evidence_contract_sha256"],
        )

        prompt_changed = current_worker_contract_binding(SCHEMA, EVIDENCE, worker_prompt_text=prompt + "\nsemantic change\n")
        self.assertNotEqual(baseline["worker_prompt_sha256"], prompt_changed["worker_prompt_sha256"])

    def test_gap07_dossier_projection_same_day_rebuild_and_old_artifact_binding(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        current_binding = current_worker_contract_binding()
        stale_doc = web_dossier(570001, now)
        stale_doc["web_evidence_contract_binding"] = {**current_binding, "worker_prompt_sha256": "0" * 64}
        with self.assertRaisesRegex(ValueError, "compatibility binding"):
            self.validate(stale_doc, now=now)

        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            work = build_daily_work_manifest_web(queue([570010, 570011, 570012]), contract, Path(td) / "store", now=now)
            index, descriptors = build_worker_projection(work, contract)
            self.assertEqual(index["web_evidence_contract_binding"], work["web_evidence_contract_binding"])
            self.assertTrue(descriptors)
            self.assertEqual(descriptors[0]["web_evidence_contract_binding"], work["web_evidence_contract_binding"])
            self.assertEqual(int(contract["checkpointing"]["checkpoint_size"]), 3)

        with tempfile.TemporaryDirectory() as td:
            contract = contract_for(td)
            root = Path(td)
            queue_path = root / "queue.jsonl"
            rows = queue([570020, 570021, 570022])
            queue_path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            output = root / "work.json"
            first, first_transition = build_or_preserve_daily_work(
                contract=contract,
                queue_path=queue_path.as_posix(),
                store_dir=root / "store",
                output_path=output,
                family_graph_path=None,
                now=now,
            )
            self.assertEqual(first_transition["mode"], "built_new_daily_snapshot")
            output.write_text(json.dumps(first), encoding="utf-8")
            old_artifact = buffered_artifact(first, 1, generated=now)

            changed_binding = {**first["web_evidence_contract_binding"], "worker_prompt_sha256": "f" * 64}
            with patch("build_taste_steam_review_dossier_work.current_worker_contract_binding", return_value=changed_binding):
                second, transition = build_or_preserve_daily_work(
                    contract=contract,
                    queue_path=queue_path.as_posix(),
                    store_dir=root / "store",
                    output_path=output,
                    family_graph_path=None,
                    now=now,
                )
            self.assertEqual(transition["mode"], "built_new_daily_snapshot")
            self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])
            self.assertEqual(second["web_evidence_contract_binding"], changed_binding)
            with self.assertRaisesRegex(ValueError, "snapshot_id does not match"):
                validate_prepublication_artifact(old_artifact, second, contract)

    def test_gap07_pre_ai_workflow_semantic_file_triggers_were_already_closed_on_pr36(self):
        workflow = (ROOT / ".github/workflows/build-pre-ai-store-snapshot.yml").read_text(encoding="utf-8")
        for path in (
            "config/taste_steam_review_dossier_schema.json",
            "config/taste_steam_review_dossier_web_evidence_contract.json",
            "config/taste_steam_review_dossier_worker_prompt.md",
        ):
            self.assertIn(f'      - "{path}"', workflow)


if __name__ == "__main__":
    unittest.main()
