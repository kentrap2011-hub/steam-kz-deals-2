from steam_traversal_recovery import (
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
