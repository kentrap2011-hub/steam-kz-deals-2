#!/usr/bin/env python3
"""Regression for atomic Dossier canonical-writer staging and clean-worktree proof."""
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGE_SCRIPT = ROOT / "scripts/stage_taste_dossier_canonical_writer.sh"


def run(cmd, cwd, *, check=True):
    return subprocess.run(
        cmd,
        cwd=cwd,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class DossierCanonicalWriterAtomicStagingTest(unittest.TestCase):
    def test_optional_control_absence_cannot_drop_audit_or_quarantine(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run(["git", "init", "-q"], repo)
            run(["git", "config", "user.name", "test"], repo)
            run(["git", "config", "user.email", "test@example.invalid"], repo)

            required = {
                "data/cache/taste_steam_review_dossiers/1.json": "{}\n",
                "data/production/pre_ai/taste_steam_review_dossier_work.json": "{}\n",
                "data/production/pre_ai/taste_steam_review_dossier_worker_index.json": "{}\n",
                "data/production/pre_ai/taste_steam_review_dossier_validation_status.json": "{}\n",
                "data/production/pre_ai/progressive_pass2_work.json": "{}\n",
                "data/ai_inbox/taste_steam_review_dossiers/candidate.json": "{}\n",
                "data/production/pre_ai/taste_steam_review_dossier_worker_groups/snapshot/g000001.json": "{}\n",
                "data/audit/taste_steam_review_dossier_group_failures.jsonl": "{\"baseline\":true}\n",
            }
            for rel, body in required.items():
                write(repo / rel, body)
            run(["git", "add", "-A"], repo)
            run(["git", "commit", "-qm", "baseline"], repo)

            # Normal canonical progress/candidate changes.
            changed = [
                "data/production/pre_ai/taste_steam_review_dossier_work.json",
                "data/production/pre_ai/taste_steam_review_dossier_worker_index.json",
                "data/production/pre_ai/taste_steam_review_dossier_validation_status.json",
                "data/production/pre_ai/progressive_pass2_work.json",
                "data/ai_inbox/taste_steam_review_dossiers/candidate.json",
            ]
            for rel in changed:
                write(repo / rel, "{\"changed\":true}\n")

            audit = repo / "data/audit/taste_steam_review_dossier_group_failures.jsonl"
            audit.write_text(audit.read_text(encoding="utf-8") + "{\"failed\":true}\n", encoding="utf-8")
            quarantine_rel = (
                "data/quarantine/taste_steam_review_dossier_inbox/failed_group/"
                "snapshot/g000001/candidate.json.invalid-test"
            )
            write(repo / quarantine_rel, "{\"quarantined\":true}\n")
            self.assertFalse((repo / "data/control").exists())

            # Prove the historical combined command is unsafe when data/control is absent.
            old = run(
                ["git", "add", "-A", "--", "data/control", "data/quarantine", "data/audit"],
                repo,
                check=False,
            )
            self.assertNotEqual(old.returncode, 0)
            old_staged = set(filter(None, run(["git", "diff", "--cached", "--name-only"], repo).stdout.splitlines()))
            self.assertFalse({
                "data/audit/taste_steam_review_dossier_group_failures.jsonl",
                quarantine_rel,
            }.issubset(old_staged))
            run(["git", "reset", "-q"], repo)

            # Execute the exact helper used by the real ingest workflow.
            run(["bash", str(STAGE_SCRIPT), "stage"], repo)
            staged = set(filter(None, run(["git", "diff", "--cached", "--name-only"], repo).stdout.splitlines()))
            expected = set(changed) | {
                "data/audit/taste_steam_review_dossier_group_failures.jsonl",
                quarantine_rel,
            }
            self.assertTrue(expected.issubset(staged), sorted(staged))

            run(["git", "diff", "--cached", "--check"], repo)
            run(["git", "commit", "-qm", "canonical ingest"], repo)
            committed = set(filter(None, run(["git", "show", "--name-only", "--format="], repo).stdout.splitlines()))
            self.assertTrue(expected.issubset(committed), sorted(committed))
            run(["bash", str(STAGE_SCRIPT), "assert-clean"], repo)
            self.assertEqual(
                run(["git", "status", "--porcelain", "--untracked-files=all"], repo).stdout,
                "",
            )

            # The safety assertion must expose exact leftover paths and fail.
            write(repo / "unexpected-leftover.txt", "leftover\n")
            dirty = run(["bash", str(STAGE_SCRIPT), "assert-clean"], repo, check=False)
            self.assertNotEqual(dirty.returncode, 0)
            self.assertIn("?? unexpected-leftover.txt", dirty.stderr)


if __name__ == "__main__":
    unittest.main()
