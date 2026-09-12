#!/usr/bin/env python3
import json
import tempfile
import unittest
from datetime import timedelta
from pathlib import Path

from taste_steam_review_dossier import (
    SUBMISSION_SCHEMA,
    build_work_manifest,
    dossier_state,
    persist_submission,
)
from taste_steam_review_dossier_cleanup import cleanup_dossier_store
from test_taste_steam_review_dossier import CONTRACT, NOW, _dossier, _pin


class SteamReviewDossierCleanupTests(unittest.TestCase):
    def test_01_stale_out_of_scope_is_deleted(self):
        pin = _pin((527070,))
        stale = _dossier(6800, generated=NOW - timedelta(days=21))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_6800.json")
            path.write_text(json.dumps(stale), encoding="utf-8")
            result = cleanup_dossier_store(pin, CONTRACT, td, now=NOW)
            self.assertFalse(path.exists())
            self.assertEqual([x["appid"] for x in result["deleted_stale_out_of_scope"]], ["6800"])
            self.assertEqual(result["preserved_refresh_required"], [])

    def test_02_stale_in_scope_is_preserved_and_refresh_required(self):
        pin = _pin((527070,))
        stale = _dossier(527070, generated=NOW - timedelta(days=21))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_527070.json")
            path.write_text(json.dumps(stale), encoding="utf-8")
            result = cleanup_dossier_store(pin, CONTRACT, td, now=NOW)
            self.assertTrue(path.exists())
            self.assertEqual([x["appid"] for x in result["preserved_refresh_required"]], ["527070"])
            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            self.assertEqual(work["required_items"][0]["reason"], "refresh_required")

    def test_03_fresh_out_of_scope_is_preserved_until_ttl_expiry(self):
        pin = _pin((527070,))
        fresh = _dossier(6800, generated=NOW - timedelta(days=5))
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_6800.json")
            path.write_text(json.dumps(fresh), encoding="utf-8")
            result = cleanup_dossier_store(pin, CONTRACT, td, now=NOW)
            self.assertTrue(path.exists())
            self.assertEqual(result["deleted_stale_out_of_scope"], [])
            self.assertEqual([x["appid"] for x in result["preserved_fresh"]], ["6800"])

    def test_04_successful_refresh_atomically_replaces_old_version_without_history(self):
        pin = _pin((527070,))
        stale = _dossier(527070, generated=NOW - timedelta(days=21), title="Old stale fixture")
        fresh = _dossier(527070, generated=NOW, title="Fresh replacement fixture")
        with tempfile.TemporaryDirectory() as td:
            path = Path(td, "App_527070.json")
            path.write_text(json.dumps(stale), encoding="utf-8")
            cleanup = cleanup_dossier_store(pin, CONTRACT, td, now=NOW)
            self.assertTrue(path.exists())
            self.assertEqual(cleanup["preserved_refresh_required"][0]["action"], "refresh_required")

            work = build_work_manifest(pin, CONTRACT, td, now=NOW)
            submission = {
                "schema": SUBMISSION_SCHEMA,
                "schema_version": 1,
                "scope_sha256": work["scope_sha256"],
                "pin_work_unit_sha256": work["pin_work_unit_sha256"],
                "dossiers": [fresh],
            }
            persist_submission(submission, work, CONTRACT, td)

            files = sorted(p.name for p in Path(td).iterdir())
            self.assertEqual(files, ["App_527070.json"])
            stored = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(stored["title"], "Fresh replacement fixture")
            self.assertEqual(dossier_state(stored, CONTRACT, now=NOW, expected_appid="527070"), "fresh")


if __name__ == "__main__":
    unittest.main(verbosity=2)
