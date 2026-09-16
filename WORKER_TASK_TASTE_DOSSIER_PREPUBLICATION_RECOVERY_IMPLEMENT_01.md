# WORKER TASK — Taste Dossier Prepublication Validation + Recovery Implement 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`
Repository scope guard: work only in this repository. Do not search, read, modify, or use any other repository. If GitHub/tool opens another repository by default or the repo target is ambiguous, STOP and switch to `kentrap2011-hub/steam-kz-deals-2` before continuing.

Task ID: `taste-dossier-prepublication-recovery-implement-01`
Mode: `IMPLEMENT / RECOVER / ACTIVATE / VALIDATE`

## Goal
Fix only the concrete defects proven by live acceptance 03:

1. The Scheduled ChatGPT worker can currently publish an immutable group that the canonical strict validator rejects later.
2. Prompt-level compact provenance rules forbidding usernames, author-profile links and review excerpts are not fully enforced mechanically.
3. The current snapshot is blocked at sequence 1 by immutable invalid artifacts and needs recovery through a GitHub-owned path without mutating those artifacts.

Do not broaden this task into a general contract audit. A separate worker is auditing for additional gap classes.

## Read first / START gate
Follow `CHAT_PROTOCOL.md` START gate fully, then read at minimum:
- `DIRECTOR_PROTOCOL.md` as applicable;
- `CHAT_CONTEXT.md`;
- relevant `CURRENT_TASK.md` state;
- relevant `PROJECT_ROUTES.md`;
- relevant `PROJECT_DECISIONS.md` for active Taste dossier ownership/contract decisions;
- `config/execution_ownership_contract.json`;
- `reviews/worker_reports/taste-dossier-evidence-guard-batch3-implement-01.md`;
- `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-03.md`;
- active dossier worker prompt/schema/web-evidence contract;
- current strict/buffered validation and repository-owned recovery mechanisms only as needed.

Run architecture preflight before implementation.

## Known live failures to fix
Acceptance 03 proved:

- canonical snapshot `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973` remains `0/591`, expected sequence `1`;
- immutable groups 1, 2 and 3 were published and remain in the inbox;
- group 1 is strict-invalid because Hellish Quart has a `current` observation without a recent `current_state` source;
- group 3 independently contains a DEEEER `source_mix_status` inconsistency and a Sniper Elite 5 `russian_attempt:"found_and_used"` record that is not bound to an observation;
- multiple dossiers persist contributor/user-review attribution names or profile-scoped references, and one compact ref carries review-content-like summary text;
- old aggregate-count/Russian-store evidence defects are materially fixed and must remain fixed.

Do not re-litigate these facts; use them as acceptance input.

## Required change A — pre-publication validation must match canonical strict acceptance
Before any immutable group transport artifact is created, the worker instructions/runtime contract must require an exact local/worker-side structural validation equivalent to the canonical strict rules that can reject the artifact later.

Required behavior:
- validate the complete group payload before create-only publication;
- include all active strict cross-field rules, not a manually duplicated subset that can drift;
- if the group fails validation, publish nothing for that group and stop with the exact validation reason;
- do not advance to later groups after a failed pre-publication validation;
- do not create an alternate filename, corrected duplicate, overwrite, rename or delete;
- preserve GitHub as the canonical owner of scope/order/progress/persistence;
- the worker-side check is a publication guard only, not a second source of canonical truth.

Prefer one repository-defined validation contract/implementation shared by both pre-publication instructions and canonical ingestion, rather than two independently maintained rule lists. If exact code execution by Scheduled ChatGPT is impossible, design the smallest deterministic artifact self-check format/process that uses the same machine-readable rules and fails closed before publication. Do not weaken canonical validation to make this easier.

## Required change B — mechanically enforce compact-provenance privacy/content rules
Persisted compact provenance must not include:
- usernames/display names/author attribution;
- profile URLs or profile-scoped direct review locators;
- review/post excerpts or paraphrased review-content summaries masquerading as locator metadata;
- raw review bodies or body-like fields.

Implement the smallest validator/schema/contract rule that reliably rejects these persisted forms while still allowing useful non-identifying compact provenance such as:
- source domain/type;
- stable public discussion/review page or item locator when it does not encode author/profile identity;
- publication date/approximate date when available;
- language;
- neutral locator/reference metadata that identifies where evidence came from without reproducing content.

Do not store hashes of usernames as a workaround. The goal is not pseudonymization; the goal is that author identity is unnecessary for this product.

Add focused regressions for the live failure shapes from acceptance 03.

## Required change C — recover the blocked snapshot without mutating immutable artifacts
The current immutable group artifacts are already published and must remain immutable.

Use the repository-defined GitHub-owned invalid-expected-artifact recovery mechanism if one exists and is compatible with the active control-plane contract.

Recovery requirements:
- do not edit/delete/rename/overwrite any of the three published transport artifacts by hand;
- do not manually rewrite queue/cache/progress/receipt state;
- do not hand-author replacement dossier JSON;
- do not create an ad hoc bypass path;
- stale/invalid artifacts must become non-authoritative through normal canonical recovery semantics;
- if recovery requires a new contract/prompt binding and therefore a fresh snapshot, use the ordinary repository-owned rebuild path;
- if the repository lacks an authorized recovery path, implement the smallest deterministic GitHub-owned recovery mechanism consistent with existing ownership, then validate it with regressions before using it;
- no accepted semantic work may be silently lost or rebound across incompatible snapshots.

The recovered state must end ready for a fresh live run with a clean expected sequence and no invalid old artifact able to satisfy the new plan.

## Preserve existing fixed behavior
Regressions must prove all remain true:
- `mention_count` equals distinct bound attributable feedback records;
- aggregate review totals cannot become topic mention counts;
- recurrence thresholds remain mechanically constrained;
- Russian Store `?l=russian` alone cannot satisfy Russian feedback;
- real bound Russian feedback can satisfy `found_and_used`;
- current/historical/durable/uncertain temporal rules remain intact;
- group size remains 3;
- create-only transport semantics remain intact;
- maximal contiguous-prefix drain remains fail-closed;
- package-member identity and independent DLC dossier behavior remain unchanged.

## Validation / activation
Use the normal repository branch/PR/CI path.

Required deterministic coverage includes at least:
1. Hellish Quart live shape is rejected pre-publication for missing recent current-state support.
2. DEEEER live `single_source_only`/two-used-sources shape is rejected pre-publication.
3. Sniper live `found_and_used` without bound Russian record is rejected pre-publication.
4. Username/display-name compact refs are rejected.
5. Author/profile URLs are rejected.
6. Review-content/excerpt-like compact refs are rejected while neutral locator metadata remains allowed.
7. A fully valid three-game group passes the same pre-publication validation and canonical strict validation.
8. Recovery leaves invalid immutable old artifacts unable to advance canonical progress.
9. Existing evidence-guard and buffered recovery suites remain green.

After merge, use only ordinary repository-owned activation/rebuild/recovery workflows permitted by the contract. Do not run the Scheduled ChatGPT task.

## Prohibitions
Do not:
- press Scheduled Task `Run now`;
- edit Scheduled Task UI;
- manually process games in interactive chat;
- manually repair any published group JSON;
- weaken strict validation;
- change downstream Taste fit/ranking/pricing/commercial behavior;
- change group size away from 3 in this task;
- implement findings from the separate general audit unless they are independently required to make this task's exact known fixes correct;
- use any other repository.

## Definition of Done
Complete only when:
- pre-publication group validation is demonstrably equivalent to the canonical strict acceptance rules relevant to the artifact;
- invalid group publication is fail-closed before create-only transport write;
- username/profile/excerpt compact provenance violations are mechanically rejected;
- the blocked current state is recovered through a GitHub-owned immutable-safe path;
- fresh canonical state is ready for a new live acceptance;
- relevant CI/regressions are green;
- no Scheduled Task run occurred;
- durable report is in `main`.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `blocked`

## Durable report
Publish to `main`:
`reviews/worker_reports/taste-dossier-prepublication-recovery-implement-01.md`

Report must include:
- architecture preflight;
- exact known defects fixed;
- how pre-publication validation shares/equates to canonical strict rules;
- exact compact-provenance privacy/content rules;
- recovery mechanism and proof immutable artifacts were not manually mutated;
- PR/merge/CI refs;
- fresh canonical snapshot/expected sequence/group-1 descriptor after recovery if available;
- proof group size remains 3;
- confirmation no Scheduled Task `Run now` occurred;
- remaining risks;
- exactly one next step.

On success, the next step should be one fresh manual Scheduled Task `Run now`, followed by a separate READ/VALIDATE acceptance task. Stop after durable report publication.