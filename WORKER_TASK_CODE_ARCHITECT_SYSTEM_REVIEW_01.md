# TASK — code-architect-system-review-01

Status: `queued_later_do_not_start_now`
Mode: `READ_ONLY_REVIEW`

## Goal

When later authorized, review the current repository/system architecture for maintainability and structural efficiency without slowing the current operational work.

## Scope

Review the current system as a whole, including:
- large or overloaded files/modules;
- duplicated logic and parallel production paths;
- unclear production entry points;
- places where responsibilities should be separated into smaller cohesive modules;
- places where a large cohesive file should remain intact but gain clear section anchors/headings;
- unnecessary helper layers or indirection;
- coupling between modules;
- testability and failure isolation;
- naming/folder layout/navigation cost;
- repeated worker difficulty locating the correct code path.

## Evidence rule

Do not guess when two architectural choices are both plausible.

If it is genuinely unclear which option is better, perform bounded measurements/comparisons appropriate to the question. Examples:
- runtime/memory/API-call measurements when performance is the question;
- dependency/coupling comparison;
- number of responsibilities per module;
- number of code locations needed for a representative change;
- search/navigation hops needed to locate behavior;
- duplication/change-coupling evidence from history;
- ability to test components independently.

Record actual evidence and state when a result is inconclusive instead of forcing a recommendation.

## Constraints

- Review only; do not refactor production code without separate user authorization.
- Do not run this task now.
- Do not become a permanent third worker; use a free `ЧАТ 1` or `ЧАТ 2` slot when later started.
- Operational speed remains the current priority.

## Output when eventually run

Produce a durable report with:
- blocking structural issues;
- recommended refactors;
- navigation improvements;
- areas where no change is recommended;
- evidence/measurements behind uncertain recommendations;
- prioritized next actions by benefit vs implementation cost.
