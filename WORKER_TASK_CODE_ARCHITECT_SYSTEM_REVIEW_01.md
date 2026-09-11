# TASK — code-architect-system-review-01

Status: `authorized_dispatched_chat_2`
Mode: `READ_ONLY_REVIEW`

## Goal

Review the current repository/system architecture for maintainability and structural efficiency while `ЧАТ 1` independently performs the authorized real Steam production integration/refresh.

This review must not slow, block, mutate, or interfere with the production work.

## Parallel-work snapshot rule

`main` may change while this review is running because `ЧАТ 1` is integrating accepted Steam partial-publish changes and running production.

Therefore:
- record the exact `main` commit reviewed at the start;
- also review the already accepted Steam implementation at worker head `5556ce5c763d886a42b3c89ba69df711ba745adb` so the incoming production structure is included;
- if `main` changes before the review finishes, do not restart the whole review; perform only a narrow final check of production-architecture files that changed materially and record the final observed `main` commit;
- do not inspect or modify live production data/results merely because `ЧАТ 1` is running them.

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
- repeated worker difficulty locating the correct code path;
- whether the accepted Steam partial-publish runner duplicates too much legacy collector logic or represents a reasonable bounded transition.

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

- READ ONLY. Do not refactor, commit code, edit workflows, modify data, dispatch workflows, stop workflows, or change `main`.
- Do not interfere with `ЧАТ 1` or the real Steam refresh.
- Do not turn architectural findings into implementation work without separate user authorization.
- Do not treat file size alone as proof that a file must be split.
- Prefer the smallest amount of repository reading necessary to establish architecture and evidence; avoid exhaustive unrelated history crawling.
- Operational speed remains the current priority, so recommendations must include expected benefit versus implementation cost.

## Required output

Write durable report:
`reviews/worker_reports/code-architect-system-review-01.md`

The report must include:
- exact starting and final repository commit refs reviewed;
- `blocking_structure_issue` findings, if any;
- `refactor_recommended` findings;
- `navigation_improvement` findings;
- areas where `no_change_recommended`;
- evidence/measurements behind uncertain recommendations;
- explicit review of one-large-file vs several-focused-modules choices where relevant;
- explicit review of the accepted Steam partial-publish runner/legacy Steam collector relationship;
- prioritized recommendations by benefit vs implementation cost;
- which recommendations can wait while operational speed is the priority.

Do not implement anything.

Final status exactly one of:
- `review_complete_recommendations_ready`
- `review_complete_no_material_architecture_change_needed`
- `blocked_requires_followup`
