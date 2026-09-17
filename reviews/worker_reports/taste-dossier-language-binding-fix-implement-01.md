# Taste Dossier Language Binding Fix Implement 01 — worker report

Status: `complete_ready_for_live_acceptance`

Task: `taste-dossier-language-binding-fix-implement-01`  
Repository: `kentrap2011-hub/steam-kz-deals-2`  
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## Architecture preflight

PASS.

- GitHub remains the canonical control plane for dossier scope/order, snapshot identity, immutable group plan, strict validation, persistence, canonical progress, recovery and completeness.
- Scheduled ChatGPT remains the constrained semantic web-evidence worker and immutable create-only candidate publisher. It does not own canonical acceptance, retry state, recovery, checkpoint progress or completeness.
- The active parallel-buffer architecture remains unchanged: multiple predeclared candidate groups may be buffered, GitHub validates asynchronously, and canonical progress accepts only the maximal valid contiguous prefix from the expected sequence.
- Canonical group/checkpoint size remains `3`.
- No second queue, scheduler, retry/healing loop, per-game repair path or alternate validator truth source was introduced.
- Repository-local Python remains optional CI/developer parity tooling and is not a Scheduled ChatGPT runtime prerequisite.

## Proven live defect and exact root cause

The defect was proven in live snapshot:

`d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71`

Its expected `g000002` contained `Blacksad: Under the Skin` (`appid=1003890`) and failed the existing strict validator with:

`observation 1 claims Russian evidence without Russian player-feedback record`

The offending Blacksad observation declared Russian support in `evidence_languages`, while all exact feedback records bound to that observation (`b-f4`, `b-f5`, `b-f6`) were `non_russian`.

The strict validator therefore behaved correctly. The production defect was upstream generation semantics: the worker contract/prompt still allowed the observation language summary to be authored independently enough from its final exact `player_feedback_ids` that Russian search/page context could leak into the summary even though no bound record supported Russian evidence.

`g000003` from the same old snapshot independently validated as a later buffered candidate but correctly could not cross the invalid `g000002` gap. This confirmed that the transport/parallel-buffer architecture was not the defect.

## Generation invariant added

Language is now **derived from exact bound player-feedback records**, not treated as a free-form observation label.

Generation order is explicit and mandatory:

1. classify each persisted `provenance.player_feedback_records[]` record language;
2. bind the final exact supporting `player_feedback_ids` to an observation or conflict;
3. derive language support only from those bound records;
4. serialize the observation language summary or any language-specific conflict wording from that derived support.

For observations, `evidence_languages` is the ordered distinct union of support projected from the exact bound records:

- record `russian` -> `russian`;
- record `non_russian` -> `non_russian`;
- record `mixed` -> both `russian` and `non_russian`;
- record `unknown` -> `unknown`.

Canonical output order is `russian`, `non_russian`, `unknown`. `mixed` is not emitted as an observation-summary token; it is an input record language that expands to both Russian and non-Russian support.

Therefore a non-Russian-only bound record set can never legitimately yield `russian`. A Russian search attempt, Russian-rendered Steam Store page, page locale, query language, parent-source metadata, or Russian/mixed record that is not bound to that exact observation/conflict cannot create Russian support for it.

Conflicts currently have no parallel `evidence_languages` field. The contract therefore does not add a redundant field: any Russian/non-Russian population or language-evidence assertion in `conflicts[].statement` must be supportable by that conflict's exact bound `player_feedback_ids` using the same projection.

The existing bidirectional Russian-attempt rule is preserved: bound Russian/mixed feedback implies `found_and_used`, while `found_and_used` requires attributable Russian/mixed feedback actually bound to an observation or conflict.

## Contract / prompt / schema / validator changes

### Evidence contract

`config/taste_steam_review_dossier_web_evidence_contract.json` now uses:

- `contract_revision = language-binding-2026-09-17`;
- `worker_prompt_revision = web-evidence-v2-language-binding-v1`.

A machine-readable `language_binding` section defines the binding fields, deterministic record-language projection, canonical output ordering, prohibited non-evidence inputs and generation order.

### Worker prompt

`config/taste_steam_review_dossier_worker_prompt.md` now contains an operational section:

`Language binding — bind records first, derive claims second`

It explicitly tells the Scheduled worker to classify records first, bind exact feedback ids second, derive language only from those final records, re-derive immediately before serialization, and never promote Russian search/page context into Russian evidence.

It also includes the exact operational case that would have prevented the live Blacksad artifact: if every record bound to an observation is `non_russian`, that observation's language summary must be exactly non-Russian.

### Schema

The dossier schema shape was intentionally **not changed**. Existing `evidence_languages` remains for compatibility with current consumers and validation. The fix constrains its generation semantics rather than adding another redundant representation.

### Strict validator

`scripts/taste_steam_review_dossier_strict.py` was not weakened or relaxed. The existing fail-closed rule that rejected the live Blacksad candidate remains authoritative.

No new competing validator truth source was introduced.

## Focused regression proof

Added:

`scripts/test_taste_steam_review_dossier_language_binding.py`

It proves:

- the exact Blacksad-shaped non-Russian-bound / Russian-claim artifact is rejected;
- non-Russian-only bound feedback cannot gain Russian support from a Russian context-only page or Russian search attempt;
- a genuinely bound Russian record permits Russian support;
- a bound `mixed` record permits both Russian and non-Russian support;
- the active machine contract makes observation language summary deterministic from exact bound records;
- the worker prompt explicitly contains the pre-publication generation rule;
- checkpoint/group size remains `3`, multiple pending buffered groups remain allowed, and GitHub-owned maximal-contiguous-prefix acceptance remains unchanged.

The focused workflow `.github/workflows/validate-taste-dossier-buffered.yml` now compiles and runs this suite alongside the existing dossier regressions.

### CI history

The first PR run, `35246729786`, failed in `Strict recovery regression` because an existing regression still hard-coded the superseded worker prompt revision `web-evidence-v2-prepublication-v1`. This was a stale regression expectation, not a production logic failure. Commit `228598f2e6340f27a04eb980481867bcd091b3b7` aligned it to the new content-complete prompt revision and added the language-binding prompt needle.

The next profile run, `35260850801`, reached the new language-binding suite and exposed a faulty test fixture: the test changed a player source's language to Russian while leaving its feedback record non-Russian, correctly triggering the older source/record coherence guard before the target observation assertion. Commit `16e9e5007113e1534206d40317af2618fe968ae7` replaced that setup with a Russian context-only Steam Store page, isolating the intended rule without bypassing existing strict guards.

Final pre-merge validation was green:

- `Validate buffered Steam review dossier runtime`: run `35261100326`, job `105336731038` — success;
- `Validate backlog dispositions`: run `35261100450`, job `105336731176` — success.

The green profile run included the existing daily snapshot, buffered submission, same-day preservation, strict recovery, prepublication parity, contract-gap, package-identity and parallel contiguous-prefix regressions plus the new language-binding regression.

## PROJECT_ROUTES.md correction

The stale Taste dossier route was updated to describe the active architecture rather than the superseded local-Python publication gate.

It now states that:

- Scheduled ChatGPT publishes complete predeclared 3-game groups create-only;
- a successful write means only `candidate buffered`;
- GitHub asynchronously performs authoritative strict validation;
- canonical progress advances only through the maximal contiguous valid prefix;
- later valid groups may remain buffered behind an invalid earlier group;
- local repository Python is not a Scheduled runtime prerequisite;
- `scripts/taste_steam_review_dossier_prepublication.py` is optional CI/developer parity tooling only;
- content-complete binding changes use the normal GitHub-owned fresh-snapshot/stale-quarantine mechanism rather than worker repair.

No unrelated route cleanup was performed.

## PR / merge / activation refs

Implementation PR:

- PR `#42` — `Fix Taste dossier bound-language generation`;
- merged to `main` as `76b00c4af4769cbaf04f30f40d6947d1b6ab21e0`.

Automatic GitHub-owned activation after merge:

- `Build pre-AI deterministic payload`: run `35261291584`, job `105337381143` — success;
- `Validate execution ownership`: run `35261291662`, job `105337381395` — success;
- `Validate backlog dispositions`: run `35261291634`, job `105337381402` — success;
- activation commit: `b6deb67178392f85a858adc7b0db7ac7a2797e5d` (`Refresh atomic pre-AI payload`).

## Post-merge compatibility activation result

The normal content-complete compatibility mechanism created a fresh active snapshot:

- `snapshot_id = e2fe16341be5bdfdb314a668c2152703e2db7f20f0a4bf769f179818b090fc59`;
- `prepared_required_count = 564`;
- `completed_required_count = 0`;
- `remaining_required_count = 564`;
- `canonical_expected_sequence = 1`;
- `group_count = 188`;
- `full_backlog_complete = false`.

The active compatibility binding is:

- evidence contract revision: `language-binding-2026-09-17`;
- evidence contract SHA-256: `fb8221c6388d728f3d92706bd476c70de9bb267fa58f9f05e75feea0666f7b75`;
- worker schema revision: `contract-gaps-2026-09-17`;
- worker schema SHA-256: `683c310bf9ea7364485f5e39456bcde0f5fb4a8cdf0106bb96d6aa9ea25b73be`;
- worker prompt revision: `web-evidence-v2-language-binding-v1`;
- worker prompt SHA-256: `59b0c73009bd5761da3e35718c2491b805b7e537084fe9d43e2f7fe2ad82d04f`.

The current worker index and first immutable descriptor expose the same exact binding.

Fresh `g000001` is range `[0,3)` and contains exactly three items, in order:

1. `2378500` — `Baldur's Gate 3 - Digital Deluxe Edition DLC`;
2. `1000360` — `Hellish Quart`;
3. `1003590` — `Tetris® Effect: Connected`.

This independently confirms that group size remains `3` after activation.

## Prior invalid artifacts are stale / inert

The prior live snapshot was:

`d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71`

Normal GitHub-owned activation moved its buffered artifacts into stale quarantine rather than repairing or rebinding them.

The old invalid `g000002` now exists at:

`data/quarantine/taste_steam_review_dossier_inbox/stale/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71/d7c882f8e9663573584c8a9d65b9183d60e4189173e1cf12db735eb7f1ae0f71--g000002--aaf90ecbc631b2629dad2daf961878d646fe3599b294eb2d4131614b03ec786a.json`

Its Git blob remains `7311df7aeed7a3aefe928497494d960d41c32fe6`, the same immutable blob as the original live candidate.

The old later-buffered `g000003` now exists beside it in the same stale snapshot directory with Git blob `816d77722394c06b7cab010a09d5cab01a4b410d`.

Thus neither candidate was edited into a valid artifact, rebound to the new snapshot, overwritten, or replaced under the old binding. The fresh active index points only to `e2fe1634…`, so the old `d7c882f8…` candidates are stale/inert and cannot contaminate the new canonical plan.

## Scheduled Task / prohibited actions confirmation

- Scheduled Task `Run now` was **not** executed during this task.
- Scheduled Task settings were not changed.
- The old invalid candidate was not manually repaired, overwritten, deleted or republished.
- No corrected candidate was created under the old snapshot.
- No retry/healing/per-game repair architecture was added.
- No group splitting was introduced.
- No Taste/ranking/pricing/commercial downstream semantics were changed by this fix.

## Remaining risks

The new generation invariant, strict rejection behavior, compatibility activation and stale handling are deterministic/CI-validated, but this task intentionally did not execute a new live Scheduled ChatGPT generation because `Run now` was explicitly prohibited. A separate live acceptance is therefore still required to observe the actual scheduled semantic worker obeying the new prompt/contract on fresh work.

Conflicts do not currently carry a separate machine language-summary field, so language-specific conflict wording is constrained by the active contract/prompt against exact bound records rather than by adding brittle natural-language parsing to the strict validator. This avoids creating another validator truth source, but it remains a useful live-acceptance observation point.

## Next step

After the independent semantic-consistency audit has also been reviewed by the Director, run one separate live acceptance of the existing Scheduled Taste Dossier task against the fresh snapshot; do not combine that run with additional implementation changes.
