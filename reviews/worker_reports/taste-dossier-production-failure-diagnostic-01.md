# Taste Dossier production failure diagnostic 01

Task: `taste-dossier-production-failure-diagnostic-01`  
Mode: READ-ONLY / RECON, with this durable report as the only authorized write.  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`

## 1. Final status

`complete_root_cause_proven`

Both production failures are independently explained and reproduced to the level needed for a separately authorized fix.

1. The sequence-1 candidate is semantically invalid under the active 365-day temporal contract. Tiny Snow contains multiple temporal contradictions. The requested `source-002` contradiction is real, but it is not the first strict-validator exception in the serialized Tiny Snow dossier: an earlier `source-006` contradiction is encountered first.
2. The GitHub ingest workflow then correctly classified the group as failed in the runner working tree, but its staging command deterministically left the failure audit and quarantine artifact unstaged because `data/control` did not exist. The command failure was hidden by `|| true`. The later `git rebase origin/main` therefore failed on a dirty worktree. No concurrent movement of `main` is required to reproduce that failure.

No production state, workflow, contract, candidate, recovery request, cache, queue, or schedule was modified by this diagnostic.

## 2. Sources / exact production refs

Production case:

- snapshot: `b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5`
- sequence: `1`
- group SHA-256: `9299039791406b032d652da85c685c8868e4dcaba808168f67c68b6fe5b709b0`
- candidate create commit: `2a3a2e2dbd99faf784f22878f0b7ec2252d1f5fa`
- candidate:
  `data/ai_inbox/taste_steam_review_dossiers/b98f8691529d9c4d1bdf66227f08537fbb5dd385ba8798280da05aa98f4054d5--g000001--9299039791406b032d652da85c685c8868e4dcaba808168f67c68b6fe5b709b0.json`
- games, in group order:
  - Crown Trick — `1000010`
  - Tiny Snow — `1002560`
  - EARTH DEFENSE FORCE 5 — `1007040`
- workflow: `Ingest Steam review dossier checkpoint`
- workflow file: `.github/workflows/ingest-taste-steam-review-dossier-checkpoint.yml`
- run id: `36241650284`
- job id: `108403182115`
- runner-local unpublished commit shown in the log: `d1481f75` — `Drain and validate Steam review dossier buffer`
- run result: failure
- run-local classification summary:
  - accepted groups this run: 0
  - failed groups this run: 1
  - failed sequence: 1
  - accepted dossier count this run: 0
  - failed dossier count: 3
- rebase error:
  - `error: cannot rebase: You have unstaged changes.`
  - `error: Please commit or stash them.`

Authoritative files inspected from the exact production commit or current `main`, as appropriate:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `WORKER_TASK_TASTE_DOSSIER_PRODUCTION_FAILURE_DIAGNOSTIC_01.md`
- `DIRECTOR_TASK_BOARD.md`
- `PROJECT_ROUTES.md`
- `PROJECT_DECISIONS.md`
- `config/execution_ownership_contract.json`
- `config/taste_steam_review_dossier_contract.json`
- `config/taste_steam_review_dossier_schema.json`
- `config/taste_steam_review_dossier_web_evidence_contract.json`
- `config/taste_steam_review_dossier_worker_prompt.md`
- `scripts/taste_steam_review_dossier_strict.py`
- `scripts/taste_steam_review_dossier_prepublication.py`
- `scripts/taste_steam_review_dossier_buffered.py`
- `scripts/ingest_taste_steam_review_dossier_inbox.py`
- `scripts/taste_steam_review_dossier_parallel_validation.py`
- `scripts/taste_steam_review_dossier_worker_projection.py`
- `scripts/taste_steam_review_dossier_recovery.py`
- `scripts/build_progressive_pass2_work.py`
- relevant Dossier validator / prepublication / canonical-writer tests.

Current-`main` state was read immediately before writing this report at SHA `e3de48693e711c8bf65fb62948f7344a5745810f`.

## 3. Freshness failure — reproduced facts

Tiny Snow has:

- `appid: "1002560"`
- `generated_at_utc: "2026-09-26T12:19:55Z"`

The active web-evidence contract has:

- `recent_max_age_days: 365`
- dated evidence is `recent` at age <=365 days and `older` at age >365 days
- a known old child feedback date must not inherit `freshness:"recent"` from an undated parent source
- a genuinely undated child remains allowed; no date may be invented.

The exact requested serialized contradiction is:

`source-002`:

- `publication_date: null`
- `freshness: "recent"`
- `evidence_role: "durable_trait"`
- `player_feedback: true`
- `feedback_surface_mode: "concrete_item_collection"`

Its bound feedback records include:

- `feedback-001` — `publication_date: "2022-02-03"` — age 1696 days on 2026-09-26
- `feedback-002` — `publication_date: "2025-08-02"` — age 420 days on 2026-09-26

Both are strictly older than the 365-day boundary while their parent is labeled `recent`.

The exact strict code path for this contradiction is `_validate_feedback_record()` in `scripts/taste_steam_review_dossier_strict.py`:

1. parse the feedback record `publication_date`;
2. read `evidence_contract["recency"]["recent_max_age_days"]`;
3. compute `generated_date - publication_date`;
4. if age is greater than the threshold and the parent source has `freshness == "recent"`, raise:

`provenance.player_feedback_records[N] older feedback cannot inherit recent parent-source freshness`

For this Tiny Snow shape, after earlier errors are repaired, the first requested child-parent failure is:

`provenance.player_feedback_records[0] older feedback cannot inherit recent parent-source freshness`

and `feedback-002` independently violates the same rule at index 1.

There is also an earlier temporal contradiction in the same serialized Tiny Snow dossier:

`source-006` has:

- `publication_date: "2019-07-13"`
- `freshness: "older"`
- `evidence_role: "current_state"`

The strict validator validates all provenance sources before feedback records. `_validate_source()` therefore reaches `source-006` first and raises:

`provenance.sources[5] current_state evidence must be classified recent`

This ordering matters: the requested `source-002` defect is real and independently invalid, but the actual unmodified Tiny Snow object has a prior strict failure at `source-006`. Crown Trick and EARTH DEFENSE FORCE 5 did not show either of these two temporal contradiction classes in the same targeted scan.

## 4. Freshness escape path — exact root cause

The temporal rule itself is not missing.

The active worker prompt explicitly says:

- 365 days or less is `recent`; more than 365 days is `older`;
- if a bound feedback record has a known date older than 365 days, its parent player-feedback source must not be `freshness:"recent"` or `evidence_role:"current_state"` merely because the parent date is null;
- if the child date is genuinely null, preserve the undated path.

The active evidence contract contains the same `known_child_date_parent_coherence_rule`.

The worker nonetheless serialized a noncompliant Tiny Snow object. That is the immediate candidate-generation/compliance failure.

The system-level escape path is explicit in the same active contract and prompt:

- `prepublication_validation.status = "not_required_for_scheduled_worker"`
- mode = `github_postpublication_canonical_validation`
- `validate_complete_group_before_create_only_publication = false`
- scheduled-worker Python execution is not required
- the worker prompt states that `scripts/taste_steam_review_dossier_prepublication.py` is a CI/developer parity utility only and “must not be executed or emulated before create-only candidate publication”
- the worker publishes through GitHub create-file first; GitHub validates afterward.

Therefore no machine validator ran between the worker's final JSON serialization and the create-file action. Prompt compliance was the only pre-write protection. The post-publication GitHub strict validator then did its job and rejected the candidate.

Existing tests already prove the validator semantics. In particular, `test_scg02_old_known_child_cannot_be_laundered_by_undated_recent_parent_but_unknown_child_is_preserved` asserts both:

- known old child + undated recent parent => rejected with `older feedback cannot inherit recent parent-source freshness`
- genuinely undated child => preserved/accepted.

The missing protection is not strict-validator coverage; it is enforcement of that validator on the Scheduled-worker publication path before the immutable candidate is created.

## 5. Machine-enforced prevention point

The prevention point should be the complete, fully serialized three-game candidate immediately before the irreversible/create-only inbox write.

Do not add a second handwritten temporal checker. The smallest safe semantic barrier is to reuse the canonical path already exposed by:

`scripts/taste_steam_review_dossier_prepublication.py::validate_prepublication_artifact`

which delegates to:

`taste_steam_review_dossier_buffered.validate_buffer_artifact`

and therefore to the same strict validator used by canonical GitHub ingestion.

Required behavior for a future authorized implementation:

1. serialize the complete candidate exactly as intended for the deterministic inbox path;
2. machine-run the canonical buffered/prepublication validator against the current exact manifest/descriptor/binding;
3. only if validation succeeds, perform the create-only write;
4. on validation failure, create no inbox artifact and stop fail-closed with the validator error;
5. do not weaken or special-case `recent_max_age_days = 365`;
6. preserve `publication_date:null` for genuinely undated feedback exactly as the existing validator does.

The present Scheduled ChatGPT transport does not have repository-local Python as an allowed prerequisite. Therefore implementation must not pretend that a prompt instruction is a machine gate. If the scheduled runtime cannot execute the repository validator, the safe alternative is a thin GitHub-owned guarded-publication entrypoint that accepts the candidate payload, runs the existing canonical prepublication validator, and writes the deterministic inbox file only on success. That remains a one-shot publication guard; it must not become a queue, retry daemon, scheduler, crawler, or second canonical acceptance authority.

The contract currently explicitly authorizes post-publication validation only, so changing this behavior requires a separate authorized contract/prompt/workflow change. This diagnostic does not make it.

## 6. Rebase failure — exact reproduction

The production workflow stage order is:

1. recovery
2. buffered drain/classification
3. validation-status regeneration
4. Progressive PASS 2 eligibility regeneration
5. staging
6. local commit
7. fetch
8. rebase
9. push.

Production log facts:

- recovery returned `no_recovery_request`
- classification returned one failed group, sequence 1
- validation-status step succeeded
- PASS 2 regeneration succeeded with target 444 / waiting_dossier 444
- staging reached the commit
- runner created local commit `d1481f75` with message `Drain and validate Steam review dossier buffer`
- commit summary: `4 files changed, 36 insertions(+), 1265 deletions(-)`
- the candidate deletion was included in that commit
- the immediately following rebase failed because unstaged changes remained.

The exact workflow staging tail is:

`git add -A -- data/control data/quarantine data/audit 2>/dev/null || true`

At production commit `2a3a2e2...`:

- there is no `data/control` path;
- `data/audit/taste_steam_review_dossier_group_failures.jsonl` is tracked;
- there is no current-snapshot failed-group quarantine artifact yet.

Git behavior was reproduced in an isolated local repository with the same path condition and the same workflow staging command. A missing `data/control` path makes that multi-path `git add` fail as one command with exit code 128:

`fatal: pathspec 'data/control' did not match any files`

Because stderr is redirected and the command is followed by `|| true`, the workflow suppresses the staging failure.

The same material steps were replayed in workflow order using the exact production path classes and candidate identity. The recorded `git status --porcelain` states were:

After recovery:

- clean.

After buffered drain/classification:

- ` D data/ai_inbox/taste_steam_review_dossiers/<exact g000001 candidate>.json`
- ` M data/audit/taste_steam_review_dossier_group_failures.jsonl`
- ` M data/production/pre_ai/taste_steam_review_dossier_work.json`
- ` M data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- `?? data/quarantine/`

After validation-status:

- the same paths, plus
- ` M data/production/pre_ai/taste_steam_review_dossier_validation_status.json`.

After PASS 2 regeneration:

- unchanged from the preceding state in the reproduction; the PASS 2 output is semantically unchanged at waiting_dossier=444.

After the current git-add sequence:

- staged:
  - `D  data/ai_inbox/taste_steam_review_dossiers/<exact g000001 candidate>.json`
  - `M  data/production/pre_ai/taste_steam_review_dossier_validation_status.json`
  - `M  data/production/pre_ai/taste_steam_review_dossier_work.json`
  - `M  data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- still unstaged:
  - ` M data/audit/taste_steam_review_dossier_group_failures.jsonl`
  - `?? data/quarantine/`

Immediately after the local commit:

- ` M data/audit/taste_steam_review_dossier_group_failures.jsonl`
- `?? data/quarantine/`

Immediately before rebase:

- same two dirty paths.

A local rebase with no concurrent remote movement then reproduced the production error exactly:

- `error: cannot rebase: You have unstaged changes.`
- `error: Please commit or stash them.`

Thus concurrency is not required for this failure.

The local replay used the exact workflow shell command and the exact material file effects proved from the repository scripts. The connector environment did not expose the GitHub checkout as a local filesystem clone, so repository Python modules were not executed from a full local checkout; that limitation does not affect the Git pathspec/staging proof because the exact producer writes and exact production path existence were independently read from the production commit.

## 7. Exact unstaged paths and creator step

Two file classes are left outside the local commit.

### Tracked modified file

`data/audit/taste_steam_review_dossier_group_failures.jsonl`

Creator:

`scripts/taste_steam_review_dossier_buffered.py::apply_buffered_drain()`

For every failed group it calls `_append_failure_audit(...)`, which appends the failed-group record. This happens in the buffered drain/classification step.

This tracked modification is sufficient by itself to make `git rebase` refuse to start.

### New untracked quarantine artifact

The production-shaped path is under:

`data/quarantine/taste_steam_review_dossier_inbox/failed_group/<snapshot>/g000001/`

with the failed candidate moved to an `.invalid-<artifact-sha-prefix>` target.

Creator:

`scripts/taste_steam_review_dossier_buffered.py::apply_buffered_drain()`

For each failed group it creates the quarantine parent and performs `shutil.move(source, target)`.

The source candidate deletion is separately staged by the earlier explicit `git add ... data/ai_inbox/taste_steam_review_dossiers`, but the quarantine destination is not staged because the later combined `data/control data/quarantine data/audit` add fails before applying the intended staging.

The exact discarded production quarantine filename suffix cannot be recovered from durable `main` because the runner-local result was never pushed, but its deterministic path class, creator, source artifact, and reason for remaining untracked are proven.

## 8. Why staging/tests missed it

### Staging defect

The workflow assumes that including `data/control`, `data/quarantine`, and `data/audit` in one `git add -A` command is enough. It is not safe when one optional pathspec is absent.

The specific defect is the combination:

- optional/nonexistent `data/control`
- mandatory changed `data/quarantine` and `data/audit`
- one shared `git add`
- stderr discarded
- `|| true`.

That converts a real staging failure into apparent success.

### Existing test gap

`scripts/test_taste_dossier_canonical_writer_coalescing_liveness.py` performs static workflow-content checks. It verifies that several core staging surfaces appear in shared writer text, and it checks step ordering. It does not execute the staging commands in a temporary Git repository, does not model an absent `data/control`, and does not assert a clean `git status --porcelain` before rebase.

The inspected Dossier buffered/prepublication/parallel-validation tests likewise do not execute the final workflow Git staging/commit/rebase path.

Therefore tests could all pass while the shell command still had a pathspec-level transactional staging failure.

### Freshness test gap is different

The semantic validator test is present and passes. The failure was not “tests do not know the temporal rule”; the failure was “Scheduled publication does not machine-run that validator before create-file.” Existing prepublication parity tests exercise the helper only when deliberately called, while the active prompt/contract explicitly exclude it from Scheduled runtime.

## 9. Relationship between defects

The defects are independent and sequential.

1. The Scheduled worker created a substantively invalid group. This is a real temporal/semantic candidate defect, not a Git transport artifact.
2. GitHub ingestion correctly rejected/classified the group in the runner's working tree.
3. The workflow then failed to publish that correct failed-group state because of the unrelated staging bug.
4. Therefore:
   - the candidate should not be canonically accepted;
   - the run-local failed classification is semantically justified;
   - the durable current Git state can still show the group as pending because the commit carrying the failure classification never reached `main`.

Fixing only the Git staging problem would make the invalid group durably failed, but would not stop future invalid candidates from being created.

Fixing only the pre-create semantic gate would prevent this candidate class in the future, but would not repair the workflow's dirty-worktree/rebase hazard for any other failed group that writes audit/quarantine output.

Both fixes are required, separately regression-tested.

## 10. Minimal future fixes

No fix was applied in this task. Recommended smallest safe future changes:

### A. Pre-create semantic guard

Promote the existing canonical prepublication validator from optional CI/developer parity to an actual machine gate on the Scheduled candidate publication path.

Preferred invariant:

`complete candidate -> canonical validate_buffer_artifact/prepublication validation -> create-only inbox write`

Never duplicate the 365-day rule in a second ad-hoc checker.

If repository-local execution is unavailable to Scheduled ChatGPT, use a thin GitHub-owned guarded publisher that performs the same validation before it creates the deterministic inbox file. Keep canonical acceptance after publication GitHub-owned as today; the new preflight is a write guard, not a new acceptance state machine.

### B. Workflow staging

Do not combine optional `data/control` with required audit/quarantine surfaces in one error-suppressed `git add`.

A minimal safe shape is:

- always stage `data/quarantine` and `data/audit` in a command that must succeed;
- stage `data/control` separately/conditionally;
- do not discard a failure that can prevent required output staging;
- after the local commit and before fetch/rebase, assert `git status --porcelain` is empty and fail with a clear diagnostic if not.

One small shell-level implementation pattern would be to split the current line into a mandatory audit/quarantine add and a separately guarded control add. The exact implementation should preserve recovery-request deletion staging when `data/control` exists.

No scheduler, retry loop, queue, alternate candidate path, automatic recovery, or acceptance bypass is needed.

## 11. Required regression tests

### Freshness / publication

1. Production-shaped Tiny Snow parent-child case:
   - parent `publication_date:null`
   - parent `freshness:"recent"`
   - child date 366+ days old
   - guarded Scheduled publication must fail before create-file and must create no inbox artifact.
2. Exact boundary:
   - age 365 => recent allowed
   - age 366 => recent parent inheritance rejected.
3. Genuine unknown path:
   - child `publication_date:null` remains allowed without inventing a date.
4. Current-state source:
   - `evidence_role:"current_state"` + `freshness:"older"` rejects before publication.
5. Atomic group:
   - one invalid dossier in a three-game group means the complete candidate is not written.
6. Integration test proves the Scheduled publication entrypoint actually invokes the canonical validator; testing the optional helper in isolation is insufficient.
7. Keep the existing semantic-consistency old-child/undated-child regression unchanged.

### Workflow staging / rebase

1. Temporary Git repo with no `data/control`, a tracked failure audit, and a newly created failed-group quarantine file.
2. Execute the actual staging helper/workflow command path.
3. Assert audit append and quarantine destination are staged.
4. Commit and assert `git status --porcelain` is empty before any rebase.
5. Run a no-op/local rebase and assert it does not fail from dirty working-tree state.
6. Separate case with an actual control recovery request/deletion to prove conditional control staging is preserved.
7. Static workflow test should additionally forbid the specific unsafe pattern of one error-suppressed multi-path add where an optional missing path can suppress mandatory audit/quarantine staging.
8. Prefer one executable clean-worktree regression over only checking that path strings are present in YAML.

## 12. Architecture/ownership preflight for proposed future fix

### Current owner

`config/execution_ownership_contract.json` assigns the Dossier nonblocking-progress control plane to GitHub.

GitHub owns:

- immutable group plan
- per-group progress state
- strict validation
- canonical persistence
- failed-group quarantine/recovery eligibility
- next worker projection
- completeness.

Scheduled ChatGPT owns only bounded semantic candidate generation plus create-only transport.

### Pre-create guard

The proposed guard must preserve those boundaries.

- Owner remains GitHub control plane.
- Scheduled ChatGPT does not gain canonical acceptance authority.
- The guard reuses GitHub's canonical validator; it does not create a second semantic truth source.
- No queue, retry daemon, scheduler, crawler, or backlog manager is added.
- Because the current contract explicitly says prepublication validation is not required for the Scheduled worker, enabling this guard requires an explicit future contract/prompt/transport authorization. It must not be smuggled in as an undocumented runtime behavior.

### Staging fix

The staging change is internal to the already-authorized GitHub canonical writer. It does not alter ownership, scheduling, retry semantics, group state semantics, or acceptance criteria. It only makes the writer atomically commit the outputs it already creates and assert its worktree is clean before rebase.

## 13. Production state/stale implications

At the diagnostic read of current `main` SHA `e3de48693e711c8bf65fb62948f7344a5745810f`:

- the same snapshot `b98f...` is active;
- group 1 is still durably `pending`;
- accepted group count: 0
- failed group count: 0
- pending group count: 148
- worker index next pending sequence: 1
- validation status also reports failed group count 0
- Progressive PASS 2 still reports all 444 targets waiting for Dossier
- the exact g000001 candidate file is still present on `main`
- the durable failure audit does not contain the new b98f/g000001 failure.

This is stale relative to the failed workflow runner's local truth, where group 1 had already been classified failed.

The failed run did not persist the corrected canonical progress because its local commit never reached `main`. No accepted Dossier from this group was persisted. The current candidate must not be treated as accepted merely because it remains in the inbox.

This task deliberately did not retry, recover, delete, overwrite, reclassify, or resume the group. Any production reconciliation after the future fix requires separate authorization.

## 14. Unresolved

No material root-cause question remains.

Two forensic limitations are non-blocking:

1. The production log exposes only the abbreviated runner-local commit id `d1481f75`; the unpublished full SHA is not durable in GitHub.
2. Because the GitHub connector checkout was not mounted as a local repository and direct network cloning was unavailable in the diagnostic container, the local Git reproduction replayed the exact workflow staging command and the exact material filesystem effects proved from the production source rather than executing the full repository Python stack from a local clone.

Neither limitation changes the conclusions:

- the strict temporal failures follow deterministically from the exact candidate plus exact validator order/code;
- the staging/rebase failure follows deterministically from the exact workflow shell, the proven absence of `data/control`, the tracked audit append, the new quarantine output, and reproduced Git behavior.

## 15. Director recommendation

Authorize a separate minimal implementation task with two independent fix tracks, both required before normal Dossier production is resumed:

1. **Pre-create canonical validation guard** — make the complete Scheduled candidate pass the existing canonical buffered/prepublication validator before the immutable inbox file can be created, while preserving the genuine-undated path and the 365-day boundary unchanged.
2. **Canonical-writer clean staging** — split optional control staging from mandatory audit/quarantine staging, stop swallowing mandatory staging failures, and assert a clean worktree immediately after the local commit / before rebase.

Required acceptance for that implementation:

- production-shaped Tiny Snow contradictions cannot create an inbox artifact;
- genuinely undated feedback still passes under existing rules;
- a failed group produces audit + quarantine + canonical failed progress in one committable set;
- `git status --porcelain` is clean before rebase;
- the rebase path succeeds without requiring concurrent `main` movement;
- no new scheduler, queue, retry loop, crawler, automatic recovery, or second acceptance authority is introduced.

After those fixes are validated, separately authorize reconciliation of the still-present b98f/g000001 candidate. Do not infer canonical failure from the discarded runner-local commit and do not mark the group accepted.
