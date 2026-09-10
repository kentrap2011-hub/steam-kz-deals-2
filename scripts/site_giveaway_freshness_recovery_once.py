from pathlib import Path


def main():
    helper = Path('scripts/steam_traversal_recovery.py')
    helper.write_text('''from __future__ import annotations

MAX_TOTAL_PASSES = 3
RECOVERY_SORTS = ("Name_DESC", "Name_ASC")


def reported_total_from_passes(passes):
    totals = [
        int(row["total"])
        for row in passes
        if row.get("total") is not None
    ]
    return max(totals) if totals else None


def recovery_needed(unique_count, passes):
    reported = reported_total_from_passes(passes)
    return bool(
        reported
        and int(unique_count) != reported
        and len(passes) < MAX_TOTAL_PASSES
    )


def next_recovery_sort(passes):
    index = len(passes) - 1
    if index < 0 or index >= len(RECOVERY_SORTS):
        raise RuntimeError("Steam traversal recovery pass budget exhausted")
    return RECOVERY_SORTS[index]
''', encoding='utf-8')

    test = Path('scripts/test_steam_traversal_recovery.py')
    test.write_text('''from steam_traversal_recovery import (
    MAX_TOTAL_PASSES,
    next_recovery_sort,
    recovery_needed,
    reported_total_from_passes,
)


def main():
    first = [{"total": 17036}]
    assert recovery_needed(17033, first) is True
    assert next_recovery_sort(first) == "Name_DESC"

    growing = [{"total": 17036}, {"total": 17037}]
    assert reported_total_from_passes(growing) == 17037
    assert recovery_needed(17036, growing) is True
    assert next_recovery_sort(growing) == "Name_ASC"

    reconciled = growing + [{"total": 17037}]
    assert len(reconciled) == MAX_TOTAL_PASSES
    assert recovery_needed(17037, reconciled) is False

    exhausted_gap = [{"total": 17036}, {"total": 17037}, {"total": 17037}]
    assert recovery_needed(17036, exhausted_gap) is False
    print("Steam traversal bounded recovery regression: PASS")


if __name__ == "__main__":
    main()
''', encoding='utf-8')

    source = Path('scripts/steam_production.py')
    text = source.read_text(encoding='utf-8')
    old_import = 'from production_output_ownership import reset_steam_collector_outputs\n'
    new_import = old_import + 'from steam_traversal_recovery import next_recovery_sort, recovery_needed, reported_total_from_passes\n'
    if text.count(old_import) != 1:
        raise SystemExit(f'expected ownership import once, found {text.count(old_import)}')
    text = text.replace(old_import, new_import, 1)

    old = '''first = collect("Name_ASC")
catalog = dict(first["catalog"])

first_total = first["total"] or 0
second = None

if (
    first_total
    and len(catalog) != first_total
):
    print(
        "First pass is not exact:",
        len(catalog),
        "/",
        first_total,
        "Running Name_DESC recovery pass.",
    )

    second = collect("Name_DESC")
    catalog.update(second["catalog"])

totals = []

if first["total"] is not None:
    totals.append(first["total"])

if second and second["total"] is not None:
    totals.append(second["total"])

reported_total = (
    max(totals)
    if totals
    else None
)

rows_seen = first["rows_seen"]
duplicate_rows = first["duplicate_rows"]
requests_made = first["requests_made"]
reached_end = first["reached_end"]

if second:
    rows_seen += second["rows_seen"]
    duplicate_rows += second["duplicate_rows"]
    requests_made += second["requests_made"]
    reached_end = (
        reached_end
        and second["reached_end"]
    )
'''
    new = '''passes = [collect("Name_ASC")]
catalog = dict(passes[0]["catalog"])

while recovery_needed(len(catalog), passes):
    reported_before = reported_total_from_passes(passes)
    sort_by = next_recovery_sort(passes)
    if len(passes) == 1:
        print(
            "First pass is not exact:",
            len(catalog),
            "/",
            reported_before,
            f"Running {sort_by} recovery pass.",
        )
    else:
        print(
            "Recovery still not exact after live catalog movement:",
            len(catalog),
            "/",
            reported_before,
            f"Running final bounded {sort_by} reconciliation pass.",
        )
    recovery = collect(sort_by)
    passes.append(recovery)
    catalog.update(recovery["catalog"])

reported_total = reported_total_from_passes(passes)
rows_seen = sum(row["rows_seen"] for row in passes)
duplicate_rows = sum(row["duplicate_rows"] for row in passes)
requests_made = sum(row["requests_made"] for row in passes)
reached_end = all(row["reached_end"] for row in passes)
'''
    if text.count(old) != 1:
        raise SystemExit(f'expected traversal orchestration block once, found {text.count(old)}')
    text = text.replace(old, new, 1)
    old_manifest = '    "recovery_pass_used":\n        second is not None,\n'
    new_manifest = '    "recovery_pass_used":\n        len(passes) > 1,\n    "traversal_pass_count":\n        len(passes),\n'
    if text.count(old_manifest) != 1:
        raise SystemExit(f'expected recovery manifest block once, found {text.count(old_manifest)}')
    text = text.replace(old_manifest, new_manifest, 1)
    source.write_text(text, encoding='utf-8')

    freshness = Path('scripts/visual_freshness_receipt.py')
    text = freshness.read_text(encoding='utf-8')
    reason_marker = 'COMMERCIAL_REASON = "commercial_only_refresh"\n'
    reason_addition = reason_marker + 'DETERMINISTIC_REFRESH_REASON = "deterministic_refresh_preserved_semantic_history"\n'
    if text.count(reason_marker) != 1:
        raise SystemExit(f'expected commercial reason marker once, found {text.count(reason_marker)}')
    text = text.replace(reason_marker, reason_addition, 1)

    intent_marker = '        "source_cycle": source_cycle,\n        "commercial_source": commercial_source,\n'
    intent_new = '''        "source_cycle": source_cycle,
        "semantic_state": {
            "payload_status": payload.get("status"),
            "ai_queue_count": payload.get("ai_queue_count"),
            "complete_family_partition": payload.get("complete_family_partition"),
        },
        "commercial_source": commercial_source,
'''
    if text.count(intent_marker) != 1:
        raise SystemExit(f'expected intent return marker once, found {text.count(intent_marker)}')
    text = text.replace(intent_marker, intent_new, 1)

    create_old = '''    intended_history = intent.get("history_snapshot_blob_sha")
    intended_giveaway = intent.get("giveaway_snapshot_blob_sha")
    intended_commercial = intent.get("commercial_source") or {}

    # Scoped publication is a real bounded build but must never claim the unrelated
    # visual domains are globally fresh.
    if scoped_giveaway:
        fresh_build = bool(persisted and intended_giveaway)
    elif scoped_commercial:
        fresh_build = bool(persisted and _commercial_intent_ready(intended_commercial))
    else:
        fresh_build = bool(build_reported and persisted and intended_history)

    observed_visual: dict[str, Any] | None = None
    reason = None if (scoped_giveaway or scoped_commercial) else reason_override
'''
    create_new = '''    intended_history = intent.get("history_snapshot_blob_sha")
    intended_giveaway = intent.get("giveaway_snapshot_blob_sha")
    intended_commercial = intent.get("commercial_source") or {}
    semantic_state = intent.get("semantic_state") or {}
    try:
        pending_semantic_queue = int(semantic_state.get("ai_queue_count") or 0) > 0
    except (TypeError, ValueError):
        pending_semantic_queue = False

    # Scoped publication is a real bounded build but must never claim the unrelated
    # visual domains are globally fresh. Likewise, a FORCE deterministic refresh
    # while semantic work remains queued may persist a new visual blob, but it must
    # preserve the last accepted semantic history and therefore cannot claim full
    # semantic freshness.
    if scoped_giveaway:
        fresh_build = bool(persisted and intended_giveaway)
    elif scoped_commercial:
        fresh_build = bool(persisted and _commercial_intent_ready(intended_commercial))
    else:
        fresh_build = bool(
            build_reported
            and persisted
            and intended_history
            and not pending_semantic_queue
        )

    observed_visual: dict[str, Any] | None = None
    if scoped_giveaway or scoped_commercial:
        reason = None
    elif pending_semantic_queue and build_reported and persisted:
        reason = DETERMINISTIC_REFRESH_REASON
    else:
        reason = reason_override
'''
    if text.count(create_old) != 1:
        raise SystemExit(f'expected receipt create block once, found {text.count(create_old)}')
    text = text.replace(create_old, create_new, 1)
    freshness.write_text(text, encoding='utf-8')

    test_freshness = Path('scripts/test_visual_freshness_receipt.py')
    text = test_freshness.read_text(encoding='utf-8')
    marker = '\ndef test_degraded_no_build() -> None:\n'
    case = '''\ndef test_deterministic_refresh_auto_detects_pending_semantic_queue() -> None:
    with tempfile.TemporaryDirectory() as td:
        repo, _ = make_repo(Path(td))
        write_json(
            repo / freshness.COMMERCIAL_PAYLOAD_PATH,
            {
                "source_mailing_updated_at_utc": SOURCE,
                "fx_binding": {"kzt_per_rub": 5.0},
                "status": "degraded",
                "ai_queue_count": 3,
                "complete_family_partition": True,
            },
        )
        commit_all(repo, "open semantic queue")
        intent = freshness.capture_intent(repo)
        receipt = freshness.create_receipt(
            repo,
            intent,
            run_id="191",
            run_attempt="1",
            event_name="push",
            workflow_head_sha=run(repo, "git", "rev-parse", "HEAD"),
            upstream_run_id=None,
            upstream_head_sha=None,
            build_reported=True,
            persisted=True,
            history_ready=True,
            reason_override=None,
        )
        assert receipt["fresh_build"] is False
        assert receipt["freshness_scope"] == freshness.FULL_SCOPE
        assert receipt["full_visual_freshness"] is False
        assert receipt["reason"] == freshness.DETERMINISTIC_REFRESH_REASON
        assert receipt.get("observed_visual") is None

'''
    if text.count(marker) != 1:
        raise SystemExit(f'expected degraded test marker once, found {text.count(marker)}')
    text = text.replace(marker, case + marker, 1)
    call_marker = '    test_fresh_commercial_only_path_does_not_claim_full_visual_freshness()\n    test_degraded_no_build()\n'
    call_new = '    test_fresh_commercial_only_path_does_not_claim_full_visual_freshness()\n    test_deterministic_refresh_auto_detects_pending_semantic_queue()\n    test_degraded_no_build()\n'
    if text.count(call_marker) != 1:
        raise SystemExit('freshness test call marker not found exactly once')
    text = text.replace(call_marker, call_new, 1)
    print_old = 'cases=fresh_full,fresh_giveaway,fresh_commercial,degraded,stale_mismatch,giveaway_mismatch,commercial_mismatch'
    print_new = 'cases=fresh_full,fresh_giveaway,fresh_commercial,deterministic_preserved,degraded,stale_mismatch,giveaway_mismatch,commercial_mismatch'
    if text.count(print_old) != 1:
        raise SystemExit('freshness cases marker not found exactly once')
    text = text.replace(print_old, print_new, 1)
    test_freshness.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    main()
