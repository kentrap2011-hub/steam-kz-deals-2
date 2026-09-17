# Taste Dossier Parallel Buffer Live Acceptance 02 — worker report

Status: `rejected_live_parallel_buffering`

Task: `taste-dossier-parallel-buffer-live-acceptance-02`
Repository: `kentrap2011-hub/steam-kz-deals-2`
Mode: `READ / VALIDATE`
Validated against `main` after the second real Scheduled ChatGPT run under the active parallel-buffer contract.

No runtime, contract, prompt, schema, workflow, queue, cache, recovery, candidate, or canonical progress fix was made. This report is the only intentional write from this task.

## Architecture preflight

PASS.

1. **Canonical owner:** GitHub remains owner of canonical dossier scope/order, immutable group plan, snapshot identity, strict validation, canonical persistence, progress, recovery and completeness under `config/execution_ownership_contract.json` and `config/taste_steam_review_dossier_contract.json`.
2. **Scheduled-worker authority:** Scheduled ChatGPT remains only the bounded web-evidence synthesis worker plus immutable create-only candidate transport writer. The active contract/prompt explicitly allows local traversal from group N to N+1 without waiting for GitHub canonical acceptance while the snapshot/plan/binding remains live.
3. **Control-plane transfer check:** none. Candidate publication did not become canonical acceptance; GitHub alone validated both candidates and controlled whether canonical progress could advance.
4. **New scheduler/queue/retry/checkpoint ownership check:** none. No second scheduler, per-game retry state, repair loop, backlog manager or alternate control plane appeared.

The observed second live run therefore exercised the intended producer-buffer-validator boundary rather than moving canonical authority into Scheduled ChatGPT.

## Authoritative Scheduled Task result

Per the task file, the following UI result is authoritative evidence and is not rediscovered or reinterpreted from unavailable ChatGPT UI state:

> В этой инвокации create-only опубликованы candidate-группы g000002 и g000003. Snapshot/plan/binding оставались неизменными; это только buffered transport progress, не canonical acceptance. На последней проверке GitHub ещё показывал canonical_expected_sequence=2, completed_required_count=3, remaining_required_count=630, full_backlog_complete=false.
>
> Следующая строго предобъявленная локальная группа — g000004: GRANDIA HD Remaster, Shadow Warrior 3: Definitive Edition, Digimon Story Cyber Sleuth: Complete Edition.

The same-invocation attribution comes from this authoritative UI evidence. GitHub history independently corroborates the exact paths, order, timestamps, snapshot/binding and intervening validation state, but Git commit metadata by itself is not used to invent a ChatGPT invocation boundary.

## Active snapshot and compatibility binding

The active snapshot stayed unchanged from the first live acceptance:

- `snapshot_id`: `d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71`
- `prepared_required_sha256`: `a73cb560704b79bf1069191dd1bd8d52af7e2c7969f619e3e9be11c7351fb95d`
- `group_plan_sha256`: `2d5453942dd473f73c18c6484ca57d1d4bca40a7c8dcce5f70766bfa3c378c45`
- prepared required count: `633`
- group count: `211`
- checkpoint/group size: `3`
- source queue SHA-256: `cda060dbcdbbf104fc87766bad7a35775ccaead0762e0678fb397f871e485cfa`

Active `web_evidence_contract_binding` stayed unchanged:

- evidence contract revision: `parallel-buffer-validation-2026-09-17`
- evidence contract SHA-256: `f12bd44759b52197f4908e0d0f8cadfcf0ceceec38cdee17df422da37c2e871a`
- worker schema revision: `contract-gaps-2026-09-17`
- worker schema SHA-256: `683c310bf9ea7364485f5e39456bcde0f5fb4a8cdf0106bb96d6aa9ea25b73be`
- dossier schema: `TASTE-STEAM-REVIEW-DOSSIER-V2`, version `2`
- worker prompt SHA-256: `deb6d68227f47766c9f159d1461341f540a0f360e848e1c230eb6bf6e32a6478`

The current compact worker index still reports this same snapshot/plan/binding with `canonical_expected_sequence=2`, `completed_required_count=3`, `remaining_required_count=630`, and `full_backlog_complete=false`.

## Exact immutable descriptors and published candidate identities

### g000002

Immutable descriptor:

- sequence: `2`
- range: `[3, 6)`
- ordered appids: `1003890`, `10150`, `1015940`
- ordered titles: `Blacksad: Under the Skin`, `Prototype™`, `Welcome to Elk`
- `items_sha256`: `c031ffaefcc0ca6bb47da3c747d6993f2b9ecb7ca90384d4a930efa66a85b975`
- `group_sha256`: `aaf90ecbc631b2629dad2daf961878d646fe3599b294eb2d4131614b03ec786a`

Deterministic candidate path:

`data/ai_inbox/taste_steam_review_dossiers/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71--g000002--aaf90ecbc631b2629dad2daf961878d646fe3599b294eb2d4131614b03ec786a.json`

The candidate top-level identity exactly matches the immutable descriptor: same snapshot, sequence/range, ordered items/appids, item hash, group hash, scope/source binding and exact active evidence/prompt binding. Transport identity is therefore exact even though the dossier payload later fails strict semantic validation.

### g000003

Immutable descriptor:

- sequence: `3`
- range: `[6, 9)`
- ordered appids: `1018800`, `1025440`, `1029690`
- ordered titles: `DEEEER Simulator: Your Average Everyday Deer Game`, `Fantasy General II`, `Sniper Elite 5`
- `items_sha256`: `f7788e702c6017a771aa599a67c6f4a38945571235b38e7e2ca3c0da94d6f576`
- `group_sha256`: `1b2506a5a231a1b220e437ef909e52b5293758026192d9bf484e7c498fd258a1`

Deterministic candidate path:

`data/ai_inbox/taste_steam_review_dossiers/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71--g000003--1b2506a5a231a1b220e437ef909e52b5293758026192d9bf484e7c498fd258a1.json`

This candidate likewise exactly matches its immutable descriptor and active binding.

## Create-only publication and exact order

GitHub history proves both deterministic paths were genuine create-only additions:

1. `g000002` publication commit `39425e14f3174b5b1b68afdc7a12278b01606145`
   - timestamp: `2026-09-17T08:51:34Z`
   - message: `Buffer Taste Steam review dossier group 2`
   - candidate file status: `added`
   - commit stats for the candidate: one file addition, zero deletions
   - candidate Git blob SHA: `7311df7aeed7a3aefe928497494d960d41c32fe6`
   - canonical artifact SHA-256 recorded by validation: `b3f3029b2c1331dbf256a01a9aea7866bdeab6caadd112cdd0ceb9740971a8e4`

2. `g000003` publication commit `c871b05d991f82e4176c38deae114c50a7586c45`
   - timestamp: `2026-09-17T08:52:12Z`
   - message: `Buffer Taste Steam review dossier group 3`
   - candidate file status: `added`
   - commit stats for the candidate: one file addition, zero deletions
   - candidate Git blob SHA: `816d77722394c06b7cab010a09d5cab01a4b410d`
   - canonical artifact SHA-256 recorded by validation: `7456f4f1d64bea786783bf563f75ffba801941437b8b34e8776a71d7481f06fa`

Each deterministic path has exactly one publication commit in current-snapshot history. No overwrite/update or alternate retry filename is present. The current inbox contains exactly these two whole-group candidates.

The publication order is therefore exactly descriptor order `g000002 -> g000003`, with no skip or reorder. Together with the authoritative UI statement that both were created in this invocation, this proves same-invocation consecutive publication.

## Proof that g000003 did not wait for canonical acceptance of g000002

The chronology is stronger than merely observing the final lagging index:

1. `08:51:34Z` — Scheduled worker publishes `g000002` in commit `39425e14...`.
2. That push triggers GitHub Actions run `35201961754`, workflow `Ingest Steam review dossier checkpoint`.
3. The run completes successfully. Its GitHub-owned drain/status commit `395d7c1a3c97970758c54a048ea15f6497ecdf57` is written at `08:51:44Z`, with parent `39425e14...`.
4. That commit leaves canonical progress at `completed_required_count=3`, `remaining_required_count=630`, expected group `2`, and records `g000002` as the invalid expected group.
5. `08:52:12Z` — Scheduled worker nevertheless publishes the immediately next predeclared `g000003` in commit `c871b05d...`.
6. The parent of the `g000003` publication commit is the already-landed GitHub validation commit `395d7c1a...`.

Thus `g000003` was published while `g000002` had **not** been canonically accepted and canonical progress still remained at sequence `2`. In fact, by the time `g000003` was committed GitHub had already classified `g000002` as invalid. The worker therefore demonstrably did not use canonical acceptance of group 2 as a same-invocation traversal gate.

This proves the intended asynchronous producer-buffer behavior without implying that Scheduled ChatGPT polled or acted on validation status; GitHub branch chronology only proves that canonical acceptance had not advanced when group 3 was created.

## GitHub strict validation result

### g000002 — invalid expected group

The `g000002` push triggered:

- workflow: `Ingest Steam review dossier checkpoint`
- run: `35201961754`
- job: `105138592079`
- conclusion: `success`

The GitHub-owned job successfully ran both:

- `Drain maximal valid contiguous dossier prefix from current repository state`
- `Record strict validation status for all current-snapshot candidate groups`

GitHub then durably recorded:

- validation: `invalid`
- canonical position: `expected`
- exact validator error: `observation 1 claims Russian evidence without Russian player-feedback record`
- `invalid_expected_group.sequence = 2`
- `retry_state = false`

The offending candidate content is consistent with that error: in the `Blacksad: Under the Skin` dossier, observation index `1` declares `evidence_languages` containing `russian`, but its bound feedback records `b-f4`, `b-f5`, and `b-f6` are all recorded as `non_russian`. This is a real strict semantic/data-contract defect in the produced candidate, not a transport identity mismatch.

No fix is implemented in this task.

### g000003 — valid but later buffered

The `g000003` push triggered a second GitHub-owned ingest run:

- workflow: `Ingest Steam review dossier checkpoint`
- run: `35202018377`
- job: `105138776276`
- conclusion: `success`

The same strict drain and all-current-snapshot validation steps completed successfully.

GitHub's resulting status commit `cc689aeffcf6176f598f5cde134bf34caec468fe` has parent `c871b05d...` and changes only the validation-status file. It records:

- `candidate_count: 2`
- `valid_candidate_count: 1`
- `invalid_candidate_count: 1`
- `g000002`: `invalid`, `canonical_position: expected`
- `g000003`: `valid`, `canonical_position: later_buffered`
- `g000003.validator_error: null`

The canonical counts remain unchanged in that commit. `g000003` therefore validated independently but was not promoted through the invalid `g000002` gap.

## Canonical progress before and after the second live invocation

The first live acceptance had already canonically accepted only `g000001`, leaving the second run starting from:

- canonical expected sequence: `2`
- `completed_required_count = 3`
- `remaining_required_count = 630`
- `full_backlog_complete = false`

After both `g000002` and `g000003` were published and both GitHub validations completed, canonical state is still:

- canonical expected sequence: `2`
- `completed_required_count = 3`
- `remaining_required_count = 630`
- `full_backlog_complete = false`

The canonical work manifest itself confirms `completed_required_count=3`, `remaining_required_count=630`, `current_checkpoint_count=3`, the current checkpoint beginning with `App_1003890` / `Blacksad: Under the Skin`, and `status: work_required`. The compact worker index derives the corresponding `canonical_expected_sequence=2`.

Therefore canonical progress stopped exactly at the first invalid group. No member of `g000002` was partially accepted, and the independently valid `g000003` did not cross the gap.

The conditional question “if g000002 is valid and accepted, did g000003 then advance?” is not applicable: `g000002` is invalid and was never accepted.

## Invalid status and gap safety

A durable invalid marker **was** produced and remains current:

- invalid sequence: `2`
- group SHA-256: `aaf90ecbc631b2629dad2daf961878d646fe3599b294eb2d4131614b03ec786a`
- artifact SHA-256: `b3f3029b2c1331dbf256a01a9aea7866bdeab6caadd112cdd0ceb9740971a8e4`
- exact failure: `observation 1 claims Russian evidence without Russian player-feedback record`

The later group remains intact and buffered:

- `g000003.validation = valid`
- `g000003.canonical_position = later_buffered`
- canonical expected sequence remains `2`
- `retry_state = false`
- no malformed-current-snapshot artifacts are recorded

This is live evidence of the negative-path safety property that had previously only been deterministic regression evidence: GitHub can independently validate a later candidate, retain it in the buffer, and still refuse to advance canonical data across the earlier invalid expected group.

## g000004 publication check

The immutable `g000004` descriptor is exactly:

- sequence: `4`
- range: `[9, 12)`
- appids: `1034860`, `1036890`, `1042550`
- titles: `GRANDIA HD Remaster`, `Shadow Warrior 3: Definitive Edition`, `Digimon Story Cyber Sleuth: Complete Edition`
- `items_sha256`: `da84b360a5f37f33affe5ab8d53c5539214d28c6ebe1f31d6eab2596c797dd6d`
- `group_sha256`: `ed3d0ba040daba3188de42c4c687183a27a4fbf3ed20bbc6d7cb104a9041aeaf`

The deterministic candidate path would be:

`data/ai_inbox/taste_steam_review_dossiers/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71--g000004--ed3d0ba040daba3188de42c4c687183a27a4fbf3ed20bbc6d7cb104a9041aeaf.json`

GitHub commit history for that exact path is empty, and the current inbox contains only the `g000002` and `g000003` candidates.

**Conclusion:** `g000004` was only named as the next strictly predeclared local group. It was not actually published.

## Property-by-property live proof matrix

| Property | Result | Live evidence |
| --- | --- | --- |
| `g000002` and `g000003` are exact immutable planned groups | **PROVEN LIVE** | Candidate top-level identities match the active descriptors, ordered items/appids, hashes, snapshot and binding. |
| Both writes are create-only and deterministic | **PROVEN LIVE** | `39425e14...` and `c871b05d...` each add exactly the deterministic group path; no overwrite/update/alternate file history exists. |
| Both were published in the same Scheduled invocation | **PROVEN LIVE** | Authoritative UI explicitly says both were published “в этой инвокации”; GitHub history corroborates consecutive publications 38 seconds apart under one unchanged snapshot/binding. |
| Descriptor order is preserved | **PROVEN LIVE** | `g000002` at `08:51:34Z`, then `g000003` at `08:52:12Z`; no skipped group. |
| Worker can publish the next group while canonical acceptance lags | **PROVEN LIVE** | `g000003` was published while canonical expected sequence remained `2`; its parent already contained GitHub's invalid status for `g000002`, so no group-2 acceptance had occurred. |
| GitHub alone performs strict validation | **PROVEN LIVE** | Runs `35201961754` and `35202018377` perform drain plus strict status recording. |
| Invalid expected group blocks canonical advancement | **PROVEN LIVE** | `g000002` is invalid expected; completed stays `3`, remaining `630`, expected stays `2`. |
| Later valid group may remain buffered behind invalid gap | **PROVEN LIVE** | `g000003` is independently `valid` + `later_buffered` and is not canonically promoted. |
| No canonical data crosses invalid/unvalidated gap | **PROVEN LIVE** | Post-g3 GitHub commit changes only observational validation status; canonical manifest counts/current checkpoint remain at group 2. |
| No per-game split/partial acceptance | **PROVEN LIVE** | Acceptance/status unit remains the 3-game group; completed count does not advance by any subset of g2. |
| No retry/healing/alternate-candidate behavior | **PROVEN LIVE** | `retry_state=false`; current inbox has only the original immutable g2/g3 group artifacts; no corrected duplicate or alternate filename appears. |
| `g000004` was published | **NOT OBSERVED / FALSE FOR THIS RUN** | Exact deterministic path has no Git history and is absent from inbox; it was only named next. |
| Candidate semantics are clean enough for production acceptance | **FAILED** | g2 has a real strict validation defect: Russian evidence claimed without a bound Russian player-feedback record for observation 1. |

## Is the defining parallel-buffer scheme finally proven live?

**Yes, the defining parallel-buffer mechanics are now proven live.**

This run supplies the previously missing real-runtime evidence that a single Scheduled invocation can create two consecutive predeclared groups in exact order without waiting for canonical advancement, while GitHub independently validates candidates and protects canonical state with a contiguous-prefix gate. It additionally gives real negative-path evidence: an invalid expected `g000002` blocks canonical progress while a later independently valid `g000003` remains buffered and unpromoted.

However, **production live acceptance is not successful**, because the expected group `g000002` contains a genuine strict semantic/data-contract defect. The task's success condition explicitly requires the defining buffering behavior to be proven **and no semantic/validation defect to be found**. The first half is proven; the second half fails.

## Non-blocking repository-route drift observed

No documentation fix is allowed by this READ / VALIDATE task, but one bounded route/pitfall candidate was observed:

`PROJECT_ROUTES.md` section **“Taste Steam review dossier: prepublication validation and immutable-safe recovery”** still describes the superseded runtime rule that Scheduled ChatGPT must run the prepublication validator and fail closed when repository Python is unavailable. The active contract, prompt and implementation report now explicitly place strict validation on GitHub after create-only publication.

This stale route did not affect the live validation above because current contract/prompt/runtime files were read directly. It is not modified here because the task explicitly prohibits fixes and instructs the worker to stop after report publication.

## Final acceptance classification

`rejected_live_parallel_buffering`

Rationale: the live **parallel buffering architecture itself is now demonstrated**, including same-invocation multi-group publication, asynchronous GitHub validation, invalid-gap blocking and later-valid buffering. But the required overall live acceptance cannot pass because the canonical expected group `g000002` failed strict validation with a real semantic/data-contract error. Additional repetitions of the unchanged Scheduled Task are not needed to prove the buffering property and would not resolve this defect.

## Exactly one next step

Return control to the Director for the next production-readiness decision on the `g000002` strict-validation defect and the required bounded contract/prompt/validator-level response; do **not** run the Scheduled Task again automatically.
