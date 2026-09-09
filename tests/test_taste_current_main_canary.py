import base64
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse

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

    def _projection(self, profile_blob="a" * 40):
        return {
            "taste_subject_count": 1,
            "classified_count": 1,
            "current_profile": {
                "repository": canary.CANONICAL_PROFILE_REPOSITORY,
                "path": canary.CANONICAL_PROFILE_PATH,
                "blob_sha": profile_blob,
            },
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

    def _manifest(self, profile_blob="a" * 40, **overrides):
        doc = {
            "profile_binding": {
                "canonical_profile_blob_sha": profile_blob,
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

    def _policy(self):
        return {
            "taste_profile": {
                "canonical_repository": canary.CANONICAL_PROFILE_REPOSITORY,
                "canonical_path": canary.CANONICAL_PROFILE_PATH,
                "load_once_per_run": True,
                "record_git_blob_sha": True,
            }
        }

    @staticmethod
    def _blob_sha(raw):
        return hashlib.sha1(f"blob {len(raw)}\0".encode("ascii") + raw).hexdigest()

    def _fake_fetcher(self, head_sequence, raw_by_commit):
        heads = iter(head_sequence)

        def fetch(url):
            if url.endswith("/commits/main"):
                try:
                    return {"sha": next(heads)}
                except StopIteration as exc:
                    raise AssertionError("unexpected extra HEAD resolution") from exc
            parsed = urlparse(url)
            if "/contents/" not in parsed.path:
                raise AssertionError(f"unexpected URL: {url}")
            ref = (parse_qs(parsed.query).get("ref") or [None])[0]
            if ref not in raw_by_commit:
                raise AssertionError(f"unexpected immutable ref: {ref}")
            raw = raw_by_commit[ref]
            return {
                "type": "file",
                "sha": self._blob_sha(raw),
                "encoding": "base64",
                "content": base64.b64encode(raw).decode("ascii"),
            }

        return fetch

    def _frozen_binding(self, raw=b'{"schema_version":"2.0"}\n', commit="f" * 40):
        return {
            "schema_version": 1,
            "authority": "canonical_live_profile",
            "repository": canary.CANONICAL_PROFILE_REPOSITORY,
            "path": canary.CANONICAL_PROFILE_PATH,
            "branch": "main",
            "resolved_commit_sha": commit,
            "blob_sha": self._blob_sha(raw),
            "content_sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "immutable_raw_url": "https://example.invalid/immutable",
            "freeze_method": "test",
            "head_confirmation_attempt": 1,
            "head_drift_before_freeze": [],
            "max_freeze_attempts": 3,
        }

    def test_current_live_profile_is_frozen_with_exact_content_blob_and_commit(self):
        commit = "1" * 40
        raw = json.dumps({"schema_version": "2.0", "evidence_log": ["current"]}).encode("utf-8") + b"\n"
        with tempfile.TemporaryDirectory() as tmp:
            result = canary.freeze_current_live_profile(
                self._policy(),
                Path(tmp),
                fetch_json=self._fake_fetcher([commit, commit], {commit: raw}),
            )
            self.assertEqual(result["profile"]["commit_sha"], commit)
            self.assertEqual(result["profile"]["blob_sha"], self._blob_sha(raw))
            self.assertEqual(result["binding"]["content_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(result["snapshot_path"].read_bytes(), raw)
            canary.validate_frozen_profile_binding(result["binding"], result["snapshot_path"])

    def test_profile_change_before_freeze_selects_newer_proven_version(self):
        old_commit = "1" * 40
        new_commit = "2" * 40
        old_raw = b'{"schema_version":"2.0","value":"old"}\n'
        new_raw = b'{"schema_version":"2.0","value":"new"}\n'
        with tempfile.TemporaryDirectory() as tmp:
            result = canary.freeze_current_live_profile(
                self._policy(),
                Path(tmp),
                fetch_json=self._fake_fetcher(
                    [old_commit, new_commit, new_commit, new_commit],
                    {old_commit: old_raw, new_commit: new_raw},
                ),
            )
            self.assertEqual(result["binding"]["resolved_commit_sha"], new_commit)
            self.assertEqual(result["binding"]["blob_sha"], self._blob_sha(new_raw))
            self.assertEqual(result["snapshot_path"].read_bytes(), new_raw)
            self.assertEqual(result["binding"]["head_confirmation_attempt"], 2)
            self.assertEqual(len(result["binding"]["head_drift_before_freeze"]), 1)

    def test_continuous_profile_churn_is_bounded_and_fails_closed(self):
        commits = [f"{n:x}" * 40 for n in range(1, 7)]
        raws = {commit: json.dumps({"commit": commit}).encode("utf-8") for commit in commits}
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(canary.CanaryError):
                canary.freeze_current_live_profile(
                    self._policy(),
                    Path(tmp),
                    fetch_json=self._fake_fetcher(commits, raws),
                    max_attempts=3,
                )

    def test_unavailable_or_malformed_live_profile_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            def unavailable(url):
                raise canary.CanaryError("unavailable")

            with self.assertRaises(canary.CanaryError):
                canary.freeze_current_live_profile(self._policy(), Path(tmp), fetch_json=unavailable)

        commit = "3" * 40
        malformed = b"not-json"
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(canary.CanaryError):
                canary.freeze_current_live_profile(
                    self._policy(),
                    Path(tmp),
                    fetch_json=self._fake_fetcher([commit, commit], {commit: malformed}),
                )

    def test_stale_committed_profile_cannot_override_frozen_live_binding(self):
        raw = b'{"schema_version":"2.0","value":"live"}\n'
        frozen = self._frozen_binding(raw)
        live_blob = frozen["blob_sha"]
        stale_blob = "a" * 40
        self.assertNotEqual(live_blob, stale_blob)
        with self.assertRaises(canary.CanaryError):
            canary.validate_prepared_outputs(
                "1016800",
                self._projection(profile_blob=stale_blob),
                self._manifest(profile_blob=stale_blob),
                self._queue(),
                frozen,
            )
        accepted = canary.validate_prepared_outputs(
            "1016800",
            self._projection(profile_blob=live_blob),
            self._manifest(profile_blob=live_blob),
            self._queue(),
            frozen,
        )
        self.assertEqual(accepted["bindings"]["profile_blob_sha"], live_blob)

    def test_profile_change_after_freeze_cannot_create_mixed_tuple(self):
        old_raw = b'{"schema_version":"2.0","value":"frozen"}\n'
        frozen = self._frozen_binding(old_raw)
        frozen_blob = frozen["blob_sha"]
        newer_blob = self._blob_sha(b'{"schema_version":"2.0","value":"later"}\n')
        accepted = canary.validate_prepared_outputs(
            "1016800",
            self._projection(profile_blob=frozen_blob),
            self._manifest(profile_blob=frozen_blob),
            self._queue(),
            frozen,
        )
        self.assertEqual(accepted["bindings"]["profile_blob_sha"], frozen_blob)
        with self.assertRaises(canary.CanaryError):
            canary.validate_prepared_outputs(
                "1016800",
                self._projection(profile_blob=newer_blob),
                self._manifest(profile_blob=newer_blob),
                self._queue(),
                frozen,
            )

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
