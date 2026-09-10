from __future__ import annotations

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
