# WORKER TASK — Taste Dossier Evidence Guard + Batch 3 Implement 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-evidence-guard-batch3-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## Goal
Harden the active Taste dossier V2 web-evidence path against the two semantic shortcuts proven by live acceptance and manual mode/batch experiments, and reduce the semantic research batch from 10 games to 3 games per canonical group/invocation without introducing a new scheduler or moving control-plane ownership away from GitHub.

The desired end state is a fresh canonical dossier snapshot/worker plan under the strengthened evidence binding, with canonical groups of exactly 3 items (except an ordinary shorter final tail group), ready for a new manual Scheduled Task live acceptance.

Do **not** press Scheduled Task `Run now` in this task.

## Authoritative experiment input from Director/user
Treat the following as confirmed product/research input. Do not spend time reproducing the chat experiment itself.

The same current dossier contract was manually exercised on `GRANDIA HD Remaster` and then on the real ten-item group under both `Instant` and `Thinking` modes.

Observed result:

- one-game research was materially more careful;
- `Thinking` reasoned somewhat better than `Instant`, especially around historical/current technical state, but did **not** eliminate the core evidence defects;
- with ten games, both modes repeatedly used Steam aggregate review counts as if they were exact topic-level `mention_count` values;
- both modes repeatedly treated a Steam store page rendered with `?l=russian` as Russian `steam_reviews` / `player_feedback`, even when no attributable Russian player review/discussion had actually been established;
- the same shortcuts appeared from the start of the ten-game batch, not only near item 10;
- therefore the working diagnosis is not simple “model fatigue by list position” and not “Instant alone is too weak”; the current large structured batch plus permissive evidence representation encourages shortcuts.

This task should fix only the bounded structural issues below. Do not redesign the whole Taste system.

## Read first / START gate
Follow `CHAT_PROTOCOL.md` START gate fully.

Read at minimum:
- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- unfinished/relevant `CURRENT_TASK.md` state;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md`, especially active Taste dossier/web-evidence decisions including `TASTE-007`;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-02.md`;
- `reviews/worker_reports/taste-dossier-web-evidence-redesign-01.md`;
- `reviews/worker_reports/taste-package-member-activation-01.md`;
- active dossier worker prompt/schema/evidence contract and the exact current group-plan/buffer/strict-validation implementation needed for this task.

Run architecture preflight before implementation.

## Architecture invariants — must remain true

1. GitHub remains the canonical owner of scope, exact item order, snapshot/group plan, validation, persistence, retry/gap/replay interpretation, canonical progress and completeness.
2. Scheduled ChatGPT remains only the bounded semantic/web-research worker plus create-only transport publisher.
3. Do not create a second queue, scheduler, recurring worker, retry manager, checkpoint manager or ChatGPT-owned backlog mechanism.
4. Preserve deterministic create-only buffered transport and contiguous GitHub-owned drain/reconciliation.
5. Do not manually rewrite canonical dossier progress/cache/receipts.
6. Taste Semantic Producer ownership and semantics are out of scope and must remain unchanged.
7. Package-member dossier identity behavior and independent DLC dossier behavior must remain unchanged.
8. Do not implement offer/package edition-quality scoring in this task.
9. Do not edit Scheduled Task UI. The live wrapper already reads the repository worker prompt; verify repository binding rather than changing UI.

If the requested batch-size change cannot be implemented inside these invariants without a broader architecture change, STOP and report `blocked` rather than inventing a new control plane.

## Required change A — make `mention_count` auditable

The current schema can accept a topic-level statement such as “players repeatedly praise X” together with an exact count that was actually copied from an aggregate Steam review total or otherwise cannot be reconstructed from persisted evidence.

Implement the smallest durable rule that prevents this.

Required semantics:

- `mention_count` means the number of **distinct player-feedback evidence records actually inspected and bound to that exact observation**.
- Overall Steam/store review totals, positive-review counts, language-filtered review totals, rating counts, percentages, curator totals or other aggregate statistics MUST NOT populate topic-level `mention_count`.
- Aggregate storefront statistics MUST NOT by themselves raise observation `recurrence`.
- A source that is only official metadata or aggregate store summary cannot count as one of the supporting player-feedback mentions.
- The persisted representation must make the count mechanically/auditably reconcilable with the evidence bound to that observation. Prefer a small structural rule over prose heuristics.
- If only one attributable player-feedback item supports the observation, it must remain `anecdotal` / `mention_count: 1`; do not generalize it into repeated player consensus.
- Preserve the no-raw-review-body/no-quote/no-username policy. Auditable does **not** mean storing review text or personal data.

The exact compact representation may be adjusted if needed, but keep it minimal and compatible with the existing purpose of provenance. Do not introduce a raw-review corpus.

## Required change B — Russian feedback must be real player feedback

A Steam store URL containing `?l=russian`, Russian UI text, or a language-filtered aggregate review count is not sufficient evidence that an attributable Russian-language player review/discussion was actually inspected.

Implement the smallest durable rule that ensures:

- a language-selected Steam store page by itself is metadata/context, not Russian player feedback;
- it cannot be tagged `player_feedback:true` merely because the page is rendered in Russian;
- it cannot satisfy `russian_attempt:"found_and_used"` by itself;
- it cannot mechanically increase `source_mix_status` as an independent player-feedback source;
- `found_and_used` requires at least one attributable Russian-language player-feedback record that is actually bound to an observation;
- if the bounded Russian search finds only aggregate/store-language information and no usable attributable player feedback, use `searched_not_found_or_insufficient`;
- do not infer Russian-specific localization/translation/voice/font/regional findings from non-Russian evidence.

Do not ban Steam as a source. Real Steam user reviews/community posts in Russian remain valid when they are actually attributable as player feedback.

## Required change C — generalized claim strength must match bound evidence

Keep this narrow. Do not attempt general natural-language fact checking.

Strengthen prompt/contract/validation only enough that:

- a generalized observation cannot structurally claim recurrence stronger than the persisted bound player-feedback evidence supports;
- current-state technical claims still require recent current-state support under the existing temporal contract;
- context-only/official sources cannot satisfy player-sentiment recurrence;
- existing `historical` / `current` / `durable` / `uncertain` semantics remain intact.

The purpose is to close the exact acceptance-02 gap, not to build a second semantic judge.

## Required change D — reduce canonical research group size from 10 to 3

Change the existing dossier worker group plan so a normal canonical group contains **3 games**, with only the natural final tail group allowed to contain fewer.

Requirements:

- preserve canonical item order;
- preserve one deterministic descriptor per group;
- preserve deterministic group hashes/bindings;
- preserve create-only transport and contiguous drain;
- preserve restart/replay/gap behavior;
- do not introduce partial-group publication inside a 10-item group;
- do not add a second buffering layer merely to keep old 10-item descriptors;
- treat the new 3-item group size as the new canonical dossier research/transport boundary for this experiment.

The goal is that one live Scheduled Task group requires full research of at most 3 games before it can publish that canonical group artifact.

## Contract/version migration

The strengthened semantics must not silently treat previously accepted but evidence-quality-rejected dossiers as satisfying the new binding.

Use the existing repository version/binding/freshness mechanism to make the migration explicit.

Requirements:

- bump the minimal appropriate contract/prompt/schema revision(s) needed to distinguish the new evidence semantics;
- do not silently weaken compatibility checks;
- incompatible old dossier evidence must become rebuild-required through normal canonical freshness/compatibility logic;
- same-day preservation must not keep an old incompatible evidence binding solely because the calendar date matches;
- produce a fresh canonical pre-AI/dossier snapshot and worker plan through the repository-owned path after activation;
- no manual edits of cache/progress/receipts to force the new snapshot.

## Deterministic regressions required

Add focused regressions for at least these exact failure classes:

1. An aggregate Steam review count such as `523` cannot become an observation `mention_count:523` unless 523 distinct attributable player-feedback evidence records were actually persisted/bound — which this compact design should not fabricate.
2. One attributable player-feedback item cannot support `moderate` or `strong` recurrence.
3. A Russian Steam store page with `?l=russian` and no attributable Russian review/discussion does not satisfy `found_and_used`.
4. Such a store-language page does not count as a distinct player-feedback source for `multi_source`.
5. A real attributable Russian player-feedback source can satisfy `found_and_used` when actually used by an observation.
6. Existing current/historical temporal protections remain green.
7. Canonical group planning now yields groups of 3 and a shorter tail only when required.
8. Buffered create-only publication/drain, gap blocking, replay/recovery and canonical progress remain correct with group size 3.
9. Existing package-member and DLC identity regressions remain green.

If the experiment exposed Markdown-wrapped links like `[https://...](https://...)` as a possible worker output, add a small regression that strict provenance still requires the actual URL field to be a valid plain HTTPS URL string; do not broaden scope beyond that.

## Implementation / PR / activation

Use the normal repository development path.

- Implement on a worker branch and open a PR.
- Keep changes narrowly limited to the active dossier evidence contract/prompt/schema/validator/group-plan/freshness compatibility and directly related tests.
- Run the repository-defined deterministic tests/CI required for this surface.
- If CI exposes an ordinary defect caused by this implementation, fix it narrowly in the same task.
- If green and the normal repository path permits activation without violating a task restriction, merge through the normal path and let repository-owned workflows rebuild/publish the fresh pre-AI dossier snapshot.
- Do not manually dispatch the Scheduled ChatGPT task.
- Do not press `Run now`.
- Do not manually create a live dossier artifact.

If merging would trigger a production action that is outside this task's authorized scope and cannot be safely treated as the ordinary canonical snapshot rebuild required here, stop with a precise blocker and do not merge.

## Post-activation validation

Before declaring ready for live acceptance, prove from canonical repository state that:

1. the new evidence binding/revision is active on `main`;
2. the fresh dossier snapshot/worker plan uses the new binding;
3. canonical normal group size is 3;
4. expected first live group contains exactly the canonical first 3 pending items under the new snapshot (do not reorder them for convenience);
5. previously rejected old evidence is not silently counted as fresh compatible completion under the new binding;
6. no stale old buffered artifact is accepted under the new plan;
7. Scheduled Task `Run now` has not been pressed by this worker;
8. the system is ready for one separate manual live run followed by a separate acceptance task.

Do not require the first three items to be specifically chosen control games. Canonical order remains authoritative.

## Prohibitions

Do not:
- process dossier games manually in the interactive worker chat;
- publish hand-authored live dossier JSON;
- run Scheduled Task `Run now`;
- create a second semantic producer;
- create a new external service/plugin/appreviews dependency;
- store raw review bodies, quotes, snippets, usernames or profiles;
- change downstream Taste-fit logic, ranking, pricing, discount logic or commercial selection;
- change the temporary downstream all-DLC final-list exclusion rule;
- implement package edition-quality scoring;
- use another repository.

## Definition of Done

Task is complete only when all are true:

- architecture preflight passes;
- the two proven evidence shortcuts are structurally blocked;
- claim-strength/recurrence is auditable against bound compact player-feedback evidence;
- Russian store-language pages alone cannot masquerade as Russian player feedback;
- canonical group size is 3;
- deterministic regressions and relevant CI pass;
- explicit compatibility migration prevents old rejected evidence from silently satisfying the new binding;
- fresh canonical dossier snapshot/worker plan exists under the new binding;
- no Scheduled Task live run was performed;
- durable report is published to `main`.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `blocked`

## Durable report

Publish to `main`:
`reviews/worker_reports/taste-dossier-evidence-guard-batch3-implement-01.md`

Report must include:

- architecture preflight;
- root cause addressed in plain language;
- exact contract/schema/prompt/group-plan revisions;
- exact `mention_count` semantics after the change;
- exact Russian-feedback rule after the change;
- how generalized recurrence is mechanically constrained;
- proof that group size is now 3;
- migration/freshness behavior for old rejected dossiers;
- PR/merge refs and CI/test refs;
- fresh snapshot id and exact first canonical 3-item group descriptor after activation, if activation completes;
- confirmation that Scheduled Task `Run now` was not used;
- remaining risks;
- exactly one next step.

The one next step on successful completion should be: perform one manual Scheduled Task `Run now` against the fresh 3-item group, then run a separate READ/VALIDATE live acceptance task.

Ensure the durable report is in `main` before completion. Stop after report publication.