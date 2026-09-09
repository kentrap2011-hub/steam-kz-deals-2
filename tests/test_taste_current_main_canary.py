import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "build_taste_current_main_canary.py"
spec = importlib.util.spec_from_file_location("taste_current_main_canary", MODULE_PATH)
canary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(canary)


class TasteCurrentMainCanaryTests(unittest.TestCase):
    def test_requires_exactly_one_numeric_appid(self):
        self.assertEqual(canary.parse_appid("1016800"), "1016800")
        self.assertEqual(canary.parse_appid("00123"), "123")
        for value in ("", "101,6800", "1016800 123", "App_1016800", "-1", "0"):
            with self.subTest(value=value):
                with self.assertRaises(canary.CanaryError):
                    canary.parse_appid(value)

    def test_output_must_be_outside_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            with self.assertRaises(canary.CanaryError):
                canary.ensure_output_isolated(root, root / "out")
            canary.ensure_output_isolated(root, Path(tmp) / "external")

    def test_one_appid_bounding_and_missing_context_fail_closed(self):
        doc = {
            "families": [
                {"taste_subject_key": "App_1016800", "primary_key": "App_1016800"},
                {"taste_subject_key": "App_42", "primary_key": "App_42"},
            ]
        }
        family = canary.select_one_family(doc, "1016800")
        self.assertEqual(family["taste_subject_key"], "App_1016800")
        with self.assertRaises(canary.CanaryError):
            canary.select_one_family(doc, "999")
        doc["families"].append({"taste_subject_key": "App_1016800", "primary_key": "App_1016800"})
        with self.assertRaises(canary.CanaryError):
            canary.select_one_family(doc, "1016800")

    def _projection(self):
        return {
            "taste_subject_count": 1,
            "classified_count": 1,
            "current_profile": {"blob_sha": "a" * 40},
            "current_binding": {
                "taste_model_version": "taste-v3",
                "taste_semantics_sha256": "b" * 64,
            },
            "entries": {
                "App_1016800": {
                    "appid": "1016800",
                    "description_source": "storebrowse_basic_info",
                    "short_description": "committed description",
                    "taste_fingerprint": "c" * 64,
                    "candidate_context_sha256": "d" * 64,
                    "status": "ai_required",
                    "ai_required_reason": "canonical_profile_blob_changed_for_entry",
                }
            },
        }

    def _manifest(self, **overrides):
        doc = {
            "profile_binding": {
                "canonical_profile_blob_sha": "a" * 40,
                "taste_model_version": "taste-v3",
            },
            "source_family_count": 1,
            "complete_family_partition": True,
            "ready_without_ai_count": 0,
            "deterministically_excluded_without_ai_count": 0,
        }
        doc.update(overrides)
        return doc

    def _queue(self):
        return [{
            "taste_subject_key": "App_1016800",
            "appid": "1016800",
            "taste_fingerprint": "c" * 64,
            "candidate_context_sha256": "d" * 64,
        }]

    def test_queue_cardinality_and_binding_consistency(self):
        result = canary.validate_prepared_outputs(
            "1016800", self._projection(), self._manifest(), self._queue()
        )
        self.assertEqual(result["queue_decision"], "semantic_queue_row")
        self.assertEqual(result["partition"]["queue"], 1)
        bad = self._queue() + [dict(self._queue()[0])]
        with self.assertRaises(canary.CanaryError):
            canary.validate_prepared_outputs("1016800", self._projection(), self._manifest(), bad)
        bad_binding = self._queue()
        bad_binding[0]["candidate_context_sha256"] = "e" * 64
        with self.assertRaises(canary.CanaryError):
            canary.validate_prepared_outputs("1016800", self._projection(), self._manifest(), bad_binding)

    def test_no_other_appid_leakage(self):
        projection = self._projection()
        projection["entries"]["App_42"] = dict(projection["entries"]["App_1016800"], appid="42")
        with self.assertRaises(canary.CanaryError):
            canary.validate_prepared_outputs("1016800", projection, self._manifest(), self._queue())

    def test_missing_or_ambiguous_candidate_context_fails_closed(self):
        for source, description in ((None, "x"), ("steam_appdetails_fallback", "x"), ("storebrowse_basic_info", "")):
            projection = self._projection()
            projection["entries"]["App_1016800"]["description_source"] = source
            projection["entries"]["App_1016800"]["short_description"] = description
            with self.subTest(source=source, description=description):
                with self.assertRaises(canary.CanaryError):
                    canary.validate_prepared_outputs("1016800", projection, self._manifest(), self._queue())

    def test_zero_queue_is_valid_only_with_exact_one_family_partition(self):
        result = canary.validate_prepared_outputs(
            "1016800", self._projection(), self._manifest(ready_without_ai_count=1), []
        )
        self.assertEqual(result["queue_decision"], "ready_without_ai")
        bad = self._manifest(ready_without_ai_count=0, deterministically_excluded_without_ai_count=0)
        with self.assertRaises(canary.CanaryError):
            canary.validate_prepared_outputs("1016800", self._projection(), bad, [])


if __name__ == "__main__":
    unittest.main()
