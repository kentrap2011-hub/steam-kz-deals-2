#!/usr/bin/env python3
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

REQUIRED_GUARD_MARKERS = (
    "github.event_name != 'workflow_run'",
    "github.event.workflow_run.conclusion == 'success'",
    "github.event.workflow_run.head_branch == 'main'",
)

EXPECTED_MUTATING_WORKFLOW_RUN_JOBS = {
    ("build-daily-visual-payload.yml", "giveaway_refresh"),
    ("build-daily-visual-payload.yml", "commercial_refresh"),
    ("build-daily-visual-payload.yml", "build"),
    ("build-feed-ingest-validation.yml", "validate"),
    ("build-feed.yml", "build"),
    ("build-mailing-feed.yml", "build"),
    ("build-pre-ai-store-snapshot.yml", "build"),
    ("build-steamdb-cache-classification.yml", "build"),
    ("checkpoint-steamdb-history.yml", "checkpoint"),
    ("export-steamdb-miss-manifest.yml", "export"),
    ("ingest-steamdb-runtime-submissions.yml", "ingest"),
}


def authorized(event_name, conclusion=None, head_branch=None):
    return event_name != "workflow_run" or (
        conclusion == "success" and head_branch == "main"
    )


def job_blocks(text):
    lines = text.splitlines()
    in_jobs = False
    current_name = None
    current = []

    for line in lines:
        if line == "jobs:":
            in_jobs = True
            continue
        if not in_jobs:
            continue

        match = re.match(r"^  ([A-Za-z0-9_-]+):\s*$", line)
        if match:
            if current_name is not None:
                yield current_name, "\n".join(current)
            current_name = match.group(1)
            current = []
        elif current_name is not None:
            current.append(line)

    if current_name is not None:
        yield current_name, "\n".join(current)


def job_if_expression(block):
    lines = block.splitlines()
    captured = []
    active = False

    for line in lines:
        if re.match(r"^    if:", line):
            active = True
            captured.append(line.strip())
            continue
        if active:
            if re.match(r"^    [A-Za-z0-9_-]+:", line):
                break
            captured.append(line.strip())

    return " ".join(captured)


def main():
    # Runtime truth table used by every audited workflow_run guard.
    assert authorized("workflow_run", "success", "main")
    assert not authorized("workflow_run", "success", "fix/pr-production-trigger-isolation-01")
    assert not authorized("workflow_run", "success", "fix/fresh-deal-discovery-refresh-fix-01")
    assert not authorized("workflow_run", "failure", "main")
    assert not authorized("workflow_run", "cancelled", "main")
    assert authorized("workflow_dispatch")
    assert authorized("push")
    assert authorized("schedule")

    discovered = set()

    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if "workflow_run:" not in text:
            continue

        for job_name, block in job_blocks(text):
            if "git push" not in block:
                continue

            discovered.add((path.name, job_name))
            condition = job_if_expression(block)
            missing = [marker for marker in REQUIRED_GUARD_MARKERS if marker not in condition]
            assert not missing, (
                f"{path.name}:{job_name} mutates repository state from workflow_run "
                f"without the production-source guard; missing={missing}"
            )

    assert discovered == EXPECTED_MUTATING_WORKFLOW_RUN_JOBS, (
        "workflow_run mutation audit changed; classify the new/removed edge explicitly: "
        f"expected={sorted(EXPECTED_MUTATING_WORKFLOW_RUN_JOBS)} "
        f"actual={sorted(discovered)}"
    )

    # PR validation remains enabled, while its collector mutation stays disabled.
    steam = (WORKFLOWS / "steam-test.yml").read_text(encoding="utf-8")
    assert "  pull_request:" in steam
    assert "  schedule:" in steam
    assert "github.event_name == 'pull_request'" in steam
    assert "github.event_name != 'pull_request'" in steam

    # Direct production entrypoints remain available on every guarded downstream workflow.
    for workflow_name, _ in EXPECTED_MUTATING_WORKFLOW_RUN_JOBS:
        workflow = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")
        assert "  workflow_dispatch:" in workflow, workflow_name

    print("WORKFLOW_RUN_PRODUCTION_AUTHORITY_VALID")


if __name__ == "__main__":
    main()
