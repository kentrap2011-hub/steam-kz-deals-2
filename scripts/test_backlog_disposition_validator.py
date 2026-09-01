#!/usr/bin/env python3
from validate_backlog_dispositions import DispositionMarker, validate_transition


def backlog(body: str) -> str:
    return "# BACKLOG\n\n## Отложенные задачи\n\n" + body.strip() + "\n"


def task(title: str, extra: str = "") -> str:
    return f"### {title}\nСтатус: planned.\n{extra}\n"


def marker(source, **payload):
    return DispositionMarker(source_path=source, payload=payload)


def run(before, after, markers=(), files=None, changed=None):
    files = files or {}
    changed = changed or set(files)
    return validate_transition(before, after, list(markers), changed, lambda p: files[p])


def assert_pass(name, *args, **kwargs):
    errors = run(*args, **kwargs)
    if errors:
        raise AssertionError(f"{name}: expected pass, got {errors}")


def assert_fail(name, needle, *args, **kwargs):
    errors = run(*args, **kwargs)
    if not errors or not any(needle in error for error in errors):
        raise AssertionError(f"{name}: expected failure containing {needle!r}, got {errors}")


def main():
    title = "Example task"
    before = backlog(task(title))
    after = backlog("")

    active_file = "WORKER_TASK_EXAMPLE_01.md"
    report = "reviews/worker_reports/example-01.md"
    active_content = f"# Worker\nTask ID: `example-01`\nReport: `{report}`\n"
    assert_pass(
        "delete -> exact active task/report",
        before,
        after,
        [marker(active_file, task=title, type="active", task_file=active_file, report=report)],
        {active_file: active_content},
    )

    evidence = "reviews/worker_reports/example-complete.md"
    completed_content = f"# Report\n\n### Task\n{title}\n\n### Status\ncomplete\n"
    assert_pass(
        "delete -> completed evidence",
        before,
        after,
        [marker(evidence, task=title, type="completed", evidence=evidence)],
        {evidence: completed_content},
    )

    decision = "PROJECT_DECISIONS.md"
    decision_content = f"# Decisions\n\n{title}\nCancelled by explicit user request.\n"
    assert_pass(
        "delete -> explicit cancellation",
        before,
        after,
        [marker(decision, task=title, type="cancelled", decision=decision, by="user", reason="User cancelled it")],
        {decision: decision_content},
    )

    assert_fail(
        "delete without disposition",
        "requires exactly one",
        before,
        after,
        [],
        {},
        set(),
    )

    verify_title = "Phone acceptance task"
    verify_before = backlog(task(verify_title, "Статус: needs_user_verification."))
    verify_evidence = "reviews/worker_reports/phone.md"
    verify_content = f"# Report\n{verify_title}\n\n### Status\ncomplete\n"
    assert_fail(
        "needs_user_verification implementation-only cannot complete",
        "cannot complete from implementation-only evidence",
        verify_before,
        after,
        [marker(verify_evidence, task=verify_title, type="completed", evidence=verify_evidence, acceptance="implementation_only")],
        {verify_evidence: verify_content},
    )

    verify_task_file = "WORKER_TASK_PHONE_ACCEPTANCE_01.md"
    verify_report = "reviews/worker_reports/phone-acceptance-01.md"
    verify_task_content = (
        "# Worker\nTask ID: `phone-acceptance-01`\n"
        f"Report: `{verify_report}`\n"
        "Status remains needs_user_verification until device acceptance.\n"
    )
    assert_pass(
        "pending verification transferred exactly",
        verify_before,
        after,
        [marker(
            verify_task_file,
            task=verify_title,
            type="active",
            task_file=verify_task_file,
            report=verify_report,
            verification="pending",
        )],
        {verify_task_file: verify_task_content},
    )

    unrelated_before = backlog(task("Keep me", "note: old"))
    unrelated_after = backlog(task("Keep me", "note: edited"))
    assert_pass(
        "unrelated backlog edit",
        unrelated_before,
        unrelated_after,
        [],
        {},
        set(),
    )

    assert_fail(
        "duplicate dispositions fail",
        "requires exactly one",
        before,
        after,
        [
            marker(active_file, task=title, type="active", task_file=active_file, report=report),
            marker(evidence, task=title, type="completed", evidence=evidence),
        ],
        {active_file: active_content, evidence: completed_content},
    )

    accepted_content = (
        f"# Report\n{verify_title}\nUser/device acceptance: confirmed on phone.\n\n### Status\ncomplete\n"
    )
    assert_pass(
        "needs_user_verification with user acceptance",
        verify_before,
        after,
        [marker(
            verify_evidence,
            task=verify_title,
            type="completed",
            evidence=verify_evidence,
            acceptance="user_verified",
            acceptance_evidence="User confirmed on real phone",
        )],
        {verify_evidence: accepted_content},
    )

    print("Backlog disposition validator regression tests passed")


if __name__ == "__main__":
    main()
