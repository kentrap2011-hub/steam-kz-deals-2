# Taste Dossier Live Web Evidence Acceptance 03

Task ID: `taste-dossier-live-web-evidence-acceptance-03`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Source of truth: `main`  
Mode: `READ / VALIDATE / ACCEPTANCE`  
Status: `rejected_live_web_evidence_groups1_3`

## Task
Validate the first live three-group run under the active auditable player-feedback binding and 3-item transport boundary, distinguish immutable transport publication from GitHub-owned canonical acceptance, audit all nine dossiers against the acceptance-02 failure classes, and make no production repair.

## Architecture preflight
PASS.

- GitHub remains owner of snapshot scope/order, immutable group plan, strict validation, canonical drain/progress, persistence, recovery and completeness.
- Scheduled ChatGPT remains a constrained semantic/data worker that can only publish deterministic create-only transport artifacts.
- This acceptance worker did not run the Scheduled Task, trigger ingestion, repair/rewrite/delete any transport artifact, change code/contracts/prompts/schemas/workflows/group size/queue/cache/progress/receipts, or author replacement dossiers.
- Task-specific no-mutation scope was treated as overriding the normal worker progress-file convention: the only repository write from this worker is this durable report.

## Verified facts

### Transport publication
The authoritative manual `Run now` output is consistent with repository history. All three commits are create-only additions at the exact deterministic paths for snapshot:

`d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`

| Group | Planned appids | Group SHA | Transport commit | Git blob SHA | Current main state |
|---|---|---|---|---|---|
| 1 | `2378500,1000360,1003590` | `83d91127ece346690fb62af453938d80be6707c19ae6019ab85de6404b11d021` | `3d5296bfbbf54115651b163a30a615f56f06f386` | `c8a602d80a13f7e311f9d2e6e727a8298c16212f` | still in inbox unchanged |
| 2 | `1003890,10150,1015940` | `4bf163f8c62c39a7d6fed6b18fa24b64511c36bf964def36583b561ba7db4283` | `dc6112096728c5fafd1241723b5cb4314590d330` | `244a2617f9b9c0f767b48500a85f033c70405e4e` | still in inbox unchanged |
| 3 | `1018800,1025440,1029690` | `22af57a771861638ed2d5d493f604ba95e4f883d67c31fe6cde06d59cfc57694` | `67e4090fb4e322f5046ac630613e3fcf967d9323` | `c90b77f4a0d344ddaf73c01d1841e5d6fbc83e6b` | still in inbox unchanged |

The current inbox contains exactly those three current-snapshot artifacts. No alternate group artifact, overwrite, rename, accepted-drain deletion or replacement was observed.

Exact transport paths:

- `data/ai_inbox/taste_steam_review_dossiers/d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000001--83d91127ece346690fb62af453938d80be6707c19ae6019ab85de6404b11d021.json`
- `data/ai_inbox/taste_steam_review_dossiers/d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000002--4bf163f8c62c39a7d6fed6b18fa24b64511c36bf964def36583b561ba7db4283.json`
- `data/ai_inbox/taste_steam_review_dossiers/d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973--g000003--22af57a771861638ed2d5d493f604ba95e4f883d67c31fe6cde06d59cfc57694.json`

### Asynchronous GitHub ingestion outcome
Each transport publication correctly woke the existing `Ingest Steam review dossier checkpoint` workflow, but every ingest job failed at the same step, `Drain maximal valid contiguous dossier prefix from current repository state`; the subsequent canonical commit step was skipped.

- group 1: run `35141427471`, job `104946617882`, `failure`;
- group 2: run `35141497710`, job `104946851874`, `failure`;
- group 3: run `35141599997`, job `104947188353`, `failure`.

Group 1 is independently proven invalid rather than being affected by later buffered files: its ingest job ran from `19:35:11Z` to `19:35:20Z`, while the group-2 transport commit was not created until `19:35:41Z`.

The active buffered planner converts any strict dossier validation failure for the current expected group to:

- `blocked_reason = "invalid_expected_group"`
- `stop_sequence = 1`

and the state-based inbox wrapper raises the deterministic CLI envelope:

`TASTE_STEAM_REVIEW_DOSSIER_INBOX_INVALID: buffered drain blocked at sequence 1: invalid_expected_group`

The Actions API exposed the failed drain step but not raw stderr through the available repository endpoint; the exact classification above follows directly from the active deterministic `taste_steam_review_dossier_buffered.py` + `ingest_taste_steam_review_dossier_inbox.py` code path and the first failing dossier data below.

### Canonical progress after settlement
No group was canonically accepted.

Current canonical worker projection remains:

- `completed_required_count = 0`
- `remaining_required_count = 591`
- `canonical_expected_sequence = 1`
- `full_backlog_complete = false`

The full work manifest remains the same snapshot with 591 eligible rows, and the first nine ordered appids exactly match immutable descriptors g1-g3.

Therefore:

- group 1 did **not** pass canonical validation;
- group 2 did **not** become canonically accepted behind group 1;
- group 3 did **not** become canonically accepted;
- canonical progress did not cross any invalid group; maximal-valid-contiguous-prefix behavior correctly yielded an empty accepted prefix.

### First actual strict failure: group 1 / Hellish Quart
The fourth `Hellish Quart` observation is persisted as `evidence_status:"current"` but cites only `hq_2025_discussion`, whose source metadata is `freshness:"older"` and `evidence_role:"durable_trait"`.

The active strict validator requires a `current` observation to cite at least one `recent` `current_state` source. Therefore the exact underlying validator error is:

`observation 3 current claim lacks recent current-state evidence`

This occurs in canonical group 1, before group 2 or group 3 can be considered by the contiguous drain.

### Group 3 guard findings
The known `Sniper Elite 5` inconsistency is real. It stores one Russian player-feedback record (`se_f8`) and declares `russian_attempt:"found_and_used"`, but none of its observations binds `se_f8` in `player_feedback_ids`. The active validator derives `used_records` only from observation bindings, so if this dossier is evaluated it fails the exact rule:

`russian found_and_used requires a bound Russian player-feedback record`

However, the actual asynchronous GitHub drain did **not** reach group 3 because sequence 1 was already invalid. It would therefore be inaccurate to report that the live GitHub run stopped on Sniper Elite 5.

Group 3 also contains an earlier-in-order strict defect in `DEEEER Simulator`: its observations use feedback records from two distinct player-feedback source IDs (`deer_reviews` and `deer_recent`) while `source_mix_status` is `single_source_only`. Under the active validator this fails:

`single_source_only must have exactly one used player-feedback source`

Thus group 3 is independently invalid even before reaching its Sniper Elite 5 dossier.

## Nine-dossier evidence audit

All nine descriptor title/appid identities are exact. Across all 26 observations:

- every `mention_count` equals the number of distinct bound `player_feedback_ids`;
- recurrence levels are consistent with the active thresholds (`1 anecdotal`, `>=2 limited`, `>=3 moderate`, `>=5 strong`);
- bound records resolve to `player_feedback:true` sources included in the observation's `source_ids`;
- no aggregate Steam/storefront count is used as `mention_count`;
- no Russian Steam **Store** `?l=russian` page is represented as attributable player feedback;
- no raw review/post body archive is present.

This is a material improvement over acceptance-02: the old aggregate-count/recurrence inflation and Russian Store UI-as-player-feedback failure classes are absent from these nine dossiers.

Per subject:

| Group | Subject | Active strict-rule audit | Semantic acceptance note |
|---|---|---|---|
| 1 | Baldur's Gate 3 - Digital Deluxe Edition DLC | count/binding/recurrence/temporal rules pass | FAIL prompt compactness/privacy: several `public_ref` values persist contributor names |
| 1 | Hellish Quart | **FAIL**: current observation lacks recent current-state source | also persists contributor names in compact refs |
| 1 | Tetris® Effect: Connected | count/binding/recurrence/current-state rules pass | FAIL prompt compactness/privacy: a compact ref persists a contributor name |
| 2 | Blacksad: Under the Skin | inspected strict rules pass | current technical claim has recent current-state support; Russian attempt correctly insufficient |
| 2 | Prototype™ | inspected strict rules pass | compatibility conflict is represented as `uncertain`, not falsely current/fixed |
| 2 | Welcome to Elk | inspected strict rules pass | FAIL prompt compactness/privacy: compact refs persist user-review attribution names; a direct review locator is profile-scoped |
| 3 | DEEEER Simulator: Your Average Everyday Deer Game | **FAIL**: `single_source_only` but two used player-feedback source IDs | one compact ref also contains review-content-like summary rather than locator-only metadata |
| 3 | Fantasy General II | inspected strict rules pass | Russian Store/aggregate-only search is correctly recorded as `searched_not_found_or_insufficient` |
| 3 | Sniper Elite 5 | **FAIL**: `found_and_used` Russian record is not bound to any observation | compact refs also persist contributor names |

### Temporal/current-state discipline
The new temporal rule is materially active rather than decorative: it rejects Hellish Quart's unsupported `current` classification. Other explicit current-state observations audited here (notably Tetris Effect and Blacksad) include recent current-state support. Prototype uses `uncertain` for unresolved modern-PC compatibility conflict. No dossier in this nine-item set makes a `historical` observation requiring the dual historical + recent-current check, so that specific path is not live-tested by this sample.

### Russian-feedback discipline
Eight dossiers use `searched_not_found_or_insufficient`; none uses a Russian Store page/aggregate as a substitute for attributable Russian player feedback. `Fantasy General II` explicitly distinguishes Russian Store/aggregate discovery from usable player feedback. `Sniper Elite 5` is the sole `found_and_used` dossier and is structurally wrong because its real Russian record is not used by any observation. The active strict rule would reject that state if reached.

### Raw bodies / quotes / usernames / profiles
Raw bodies are absent, but this acceptance condition does **not** fully pass. Multiple compact `public_ref` values contain contributor/user-review attribution names, and at least one direct review locator is profile-scoped. One DEEEER compact ref also carries review-content-like summary text. The worker prompt explicitly forbids usernames, author profiles and quotes/excerpts, while the current strict validator only blocks body-like field names and does not mechanically reject these values inside `public_ref`/URL strings. This is a demonstrated validator/prompt enforcement gap independent of the count-binding hardening.

## Guard effectiveness versus acceptance-02

Materially fixed in live output:

- `mention_count` is now auditable against exact bound player-feedback records;
- one-record evidence is no longer inflated to moderate/strong recurrence;
- aggregate storefront counts are not used as observation mention counts;
- Russian Steam Store UI / `?l=russian` metadata is not treated as Russian player feedback;
- observation-to-feedback/source binding is substantially stronger;
- current-state temporal support is now enforced by strict validation.

Still failing acceptance:

- the worker can publish an immutable group that the already-active strict validator rejects (group 1);
- group 3 contains two independent strict defects, not just the manually noticed Sniper Russian binding issue;
- the prompt's no-usernames/no-author-profile/no-excerpt compact-provenance rule is not fully enforced by the validator and is violated in multiple groups.

Therefore the evidence guard improved the old failure classes, but the live Scheduled Task output is not acceptance-ready.

## Workload-quality comparison: group 1 -> 2 -> 3
There is no simple monotonic degradation curve. Group 2 is structurally cleaner than group 1 under the active strict rules, while group 3 regresses with two strict defects. Count/recurrence/store-Russian discipline remains improved across all three groups, but correctness is inconsistent within the same invocation even at a 3-item transport boundary.

This is a broader workload-quality/pre-publication-validation problem: smaller groups reduce the blast radius of bad immutable artifacts but do not ensure that each published group satisfies the canonical validator.

## Changes
- Added only `reviews/worker_reports/taste-dossier-live-web-evidence-acceptance-03.md`.
- No production state, transport, cache, progress, recovery request, code, contract, prompt, workflow or Scheduled Task state was changed.

## Validation
- START/architecture/ownership preflight: PASS.
- Exact immutable descriptor vs transport identity for groups 1-3: PASS.
- Create-only publication and current blob identity: PASS.
- Automatic ingest fired for all three commits: PASS.
- Canonical acceptance of group 1: FAIL.
- Canonical acceptance of group 2: FAIL / never reachable behind invalid group 1.
- Canonical acceptance of group 3: FAIL / never reachable behind invalid group 1.
- Canonical progress safety (`0/591`, expected sequence `1`): PASS.
- New mention-count / bound-record / recurrence guard across all 26 observations: PASS.
- Aggregate-count rejection semantics in live output: PASS.
- Russian Store/UI false-evidence failure class: PASS.
- Russian `found_and_used` binding: FAIL for Sniper Elite 5; active validator rule is correct but actual canonical drain never reached g3.
- Current-state temporal discipline: FAIL in Hellish Quart and correctly rejectable by active strict validator.
- Raw-body absence: PASS.
- Username/profile/excerpt absence: FAIL.
- Consistent quality across g1-g3: FAIL.

## Unresolved
The current snapshot is still blocked at canonical sequence 1 with all three immutable artifacts waiting in the transport inbox. Group 2 was not canonically accepted despite being the cleanest structural group in this run. The canonical strict guard is working fail-closed, but invalid artifacts are being created before that guard, and one prompt-level compact-provenance privacy rule is not mechanically enforced by strict validation.

## Status
`rejected_live_web_evidence_groups1_3`

The live run cannot be partially accepted as `guard_worked_group3_rejected`: groups 1 and 2 were not canonically accepted, group 1 itself is strict-invalid, and semantic compact-provenance defects remain outside current strict enforcement.

## Recommended next step
Create one bounded IMPLEMENT/RECOVERY task that makes the worker's pre-publication group check equivalent to the canonical strict rules, adds mechanical rejection of persisted username/author-profile/review-excerpt compact references, and then uses only the GitHub-owned invalid-expected-artifact recovery path to recover this snapshot from canonical sequence 1 without mutating the immutable published artifacts.

## Exact refs
- Task: `WORKER_TASK_TASTE_DOSSIER_LIVE_WEB_EVIDENCE_ACCEPTANCE_03.md`
- Snapshot: `d45430762377a5de89ab2705585f5e6d6674af0a5b1882611e0852a376ef6973`
- Work manifest: `data/production/pre_ai/taste_steam_review_dossier_work.json`
- Worker index: `data/production/pre_ai/taste_steam_review_dossier_worker_index.json`
- Active evidence contract: `config/taste_steam_review_dossier_web_evidence_contract.json`
- Active schema: `config/taste_steam_review_dossier_schema.json`
- Active worker prompt: `config/taste_steam_review_dossier_worker_prompt.md`
- Strict validator: `scripts/taste_steam_review_dossier_strict.py`
- Buffered validator/drain: `scripts/taste_steam_review_dossier_buffered.py`
- Inbox wrapper: `scripts/ingest_taste_steam_review_dossier_inbox.py`
- g1 transport commit / ingest run / job: `3d5296bfbbf54115651b163a30a615f56f06f386` / `35141427471` / `104946617882`
- g2 transport commit / ingest run / job: `dc6112096728c5fafd1241723b5cb4314590d330` / `35141497710` / `104946851874`
- g3 transport commit / ingest run / job: `67e4090fb4e322f5046ac630613e3fcf967d9323` / `35141599997` / `104947188353`

Efficiency / reusable lesson: acceptance must inspect the **first canonical expected group** before attributing a later buffered failure to a known defect; buffered publication order does not imply canonical acceptance order, and a later worker self-detected defect may never have been reached by GitHub drain.