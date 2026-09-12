#!/usr/bin/env python3
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from taste_steam_review_dossier import build_work_manifest, dossier_state, persist_submission
from taste_steam_review_dossier_cleanup import cleanup_dossier_store
from test_taste_steam_review_dossier import CONTRACT, NOW, _dossier, _queue, _submission


class SteamReviewDossierCleanupTests(unittest.TestCase):
    def test_01_stale_out_of_full_scope_is_deleted(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_6800.json")
            path.write_text(json.dumps(_dossier(6800, generated=NOW - timedelta(days=21))), encoding="utf-8")
            result = cleanup_dossier_store(queue, CONTRACT, td, now=NOW)
            self.assertFalse(path.exists())
            self.assertEqual([x["appid"] for x in result["deleted_stale_out_of_scope"]], ["6800"])

    def test_02_stale_in_full_scope_is_preserved_and_refresh_required(self):
        queue = _queue(tuple(range(100000, 100121)))
        target = "100115"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, f"App_{target}.json")
            path.write_text(json.dumps(_dossier(target, generated=NOW - timedelta(days=21))), encoding="utf-8")
            result = cleanup_dossier_store(queue, CONTRACT, td, now=NOW)
            self.assertTrue(path.exists())
            self.assertEqual(result["unique_appid_count"], 121)
            self.assertEqual([x["appid"] for x in result["preserved_refresh_required"]], [target])
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            item = next(x for x in work["required_items"] if x["appid"] == target)
            self.assertEqual(item["reason"], "refresh_required")

    def test_03_fresh_out_of_scope_is_preserved_until_ttl_expiry(self):
        queue = _queue((527070,))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_6800.json")
            path.write_text(json.dumps(_dossier(6800, generated=NOW - timedelta(days=5))), encoding="utf-8")
            result = cleanup_dossier_store(queue, CONTRACT, td, now=NOW)
            self.assertTrue(path.exists())
            self.assertEqual([x["appid"] for x in result["preserved_fresh"]], ["6800"])

    def test_04_successful_refresh_atomically_replaces_old_version_without_history(self):
        queue = _queue((527070,))
        stale = _dossier(527070, generated=NOW - timedelta(days=21), title="Old stale fixture")
        fresh = _dossier(527070, generated=NOW, title="Fresh replacement fixture")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_527070.json")
            path.write_text(json.dumps(stale), encoding="utf-8")
            cleanup = cleanup_dossier_store(queue, CONTRACT, td, now=NOW)
            self.assertEqual(cleanup["preserved_refresh_required"][0]["action"], "refresh_required")
            work = build_work_manifest(queue, CONTRACT, td, now=NOW)
            persist_submission(_submission(work, [fresh]), work, CONTRACT, td)
            self.assertEqual(sorted(p.name for p in Path(td).iterdir()), ["App_527070.json"])
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(stored["title"], "Fresh replacement fixture")
            self.assertEqual(dossier_state(stored, CONTRACT, now=NOW, expected_appid="527070"), "fresh")

    def test_05_duplicate_queue_appid_does_not_expand_cleanup_scope(self):
        queue = _queue((527070, 6800, 527070, 6800))
        with tempfile.TemporaryDirectory() as td:
            result = cleanup_dossier_store(queue, CONTRACT, td, now=NOW)
        self.assertEqual(result["source_row_count"], 4)
        self.assertEqual(result["unique_appid_count"], 2)
        self.assertEqual(result["current_scope_appids"], ["527070", "6800"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
