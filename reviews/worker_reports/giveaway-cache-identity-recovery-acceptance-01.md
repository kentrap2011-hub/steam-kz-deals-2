# Giveaway cache identity recovery acceptance 01

## Status

**FAIL — needs_followup_fix**

Failure class: **`deployed_but_fix_insufficient`**.

Target landed commit:

- `6282619c65c134459a4e85c80b9355fe3174e8ae`
- `Fix giveaway cache payload identity`
- parent: `fb521c6c310c5d7deadc8163ac808778ea07247a`
- commit time: `2026-09-04T04:45:48Z`
- GitHub signature: verified

This recovery/acceptance did **not** re-implement the fix. The only repository change made by this task is this report.

## Executive verdict

The landed commit is cleanly scoped and its added focused regression test passes, but the implementation does **not** fix the actual production collision it was intended to fix.

The reason is concrete and reproducible: `payloadIdentity()` was extended using a **synthetic giveaway schema** that does not match the deployed production payload.

The commit reads these top-level values:

- `payload.giveaway_generated_at_utc`
- `payload.giveaway_status`
- `Array.isArray(payload.giveaways) ? payload.giveaways.length : null`

The deployed production payload instead has:

- no top-level `giveaway_generated_at_utc`;
- no top-level `giveaway_status`;
- `giveaways` as an object, not an array;
- actual giveaway publication provenance under `production_contract.source_giveaway_snapshot_blob_sha`;
- giveaway state/data nested under the `giveaways` object.

Therefore all three newly-added giveaway components collapse to empty values for the real payload. A stale canonical payload and a fresh giveaway-only payload with the same top-level `generated_at_utc` and `items.length` still receive the same identity, so the background refresh can still return `identical` and leave stale giveaway state active.

The code from `6282619c...` **was successfully deployed**, but the deployed code is semantically insufficient. There is no newer correction in the current `web/feed-bootstrap.js` on `main` at the time of this acceptance.

**Do not ask the user to re-test giveaways on the phone yet.** A bounded follow-up correction is required first.

## 1. Landed commit review

Commit `6282619c65c134459a4e85c80b9355fe3174e8ae` changes exactly two intended files:

- `web/feed-bootstrap.js`
- `scripts/test_feed_bootstrap_cache_identity.js`

Diff size: 162 additions, 2 deletions.

There are no unrelated frontend changes in the landed commit.

### What changed in `payloadIdentity()`

Before the commit, identity used only:

- `generated_at_utc`
- `items.length`

The commit added:

- top-level `giveaway_generated_at_utc`
- top-level `giveaway_status`
- `giveaways.length` only when `giveaways` is an array

This is internally consistent with the newly-added test fixture, but not with the actual production payload schema.

### Assessment of the landed commit

**Scoped correctly, conceptually aimed at the correct failure mode, but functionally incorrect for production data.**

It should not be accepted as the completed fix.

## 2. Actual production schema check

Acceptance inspected the exact GitHub Pages artifact produced for the target commit, not only source fixtures.

Relevant deployed artifact payload facts:

- `generated_at_utc`: present
- `items`: array
- top-level `giveaway_generated_at_utc`: **absent**
- top-level `giveaway_status`: **absent**
- `giveaways`: **object**, not array
- `giveaways.state`: `active`
- `giveaways.games`: 1 game in the deployed artifact
- `production_contract.source_giveaway_snapshot_blob_sha`:
  `7102b39bf64feeb6d8af22bc204e7e72bf077159de7da71a7c0ef42c2c7f5773`

This proves the implementation reads the wrong giveaway identity fields for the real schema.

## 3. Real-schema collision reproduction

A temporary acceptance-only probe was run against the **exact shipped `feed-bootstrap.js` and exact shipped `data/current.json`** from the Pages artifact. No repository source was modified.

The probe constructed a stale cached variant by changing only real giveaway publication/data fields while preserving the ordinary feed identity inputs:

- changed `production_contract.source_giveaway_snapshot_blob_sha` to an old value;
- changed `giveaways.state` from `active` to `absent`;
- emptied `giveaways.games`;
- changed `giveaways.accepted_offer_count_at_build` to `0`;
- kept `generated_at_utc` unchanged;
- kept `items` unchanged.

Observed output:

```text
schema_top_keys_has_flat_generated= false
schema_top_keys_has_flat_status= false
giveaways_is_array= false
fresh_provenance= 7102b39bf64feeb6d8af22bc204e7e72bf077159de7da71a7c0ef42c2c7f5773
cached_identity= 2026-09-03T18:29:04.806292Z|73|||
fresh_identity= 2026-09-03T18:29:04.806292Z|73|||
identity_equal_despite_real_giveaway_change= true
real_schema_refresh_outcome= identical
real_schema_app_init_calls= 0
initial_delivered_giveaway_state= absent
synthetic_commit_fixture_refresh_outcome= updated
true_identical_refresh_outcome= identical
ACCEPTANCE_PROBE=PASS (expected defect reproduced)
```

The key acceptance result is:

- real stale giveaway payload identity == real fresh giveaway payload identity;
- refresh outcome remains `identical`;
- fresh payload is not applied;
- the original failure class is still reachable after the landed fix.

This is a direct reproduction of the intended regression using production-shaped data.

## 4. Focused regression tests

### Landed focused test

Command:

```text
node scripts/test_feed_bootstrap_cache_identity.js
```

Result:

```text
giveaway cache identity regression: PASS
```

However, this test uses a synthetic fixture with:

- top-level `giveaway_generated_at_utc`;
- top-level `giveaway_status`;
- `giveaways` as an array.

Those assumptions do not match deployed `data/current.json`. The green test therefore validates the implementation against its invented fixture, not against production contract shape.

### Existing UI regressions from the exact Pages artifact

All passed:

```text
node giveaway-ui.test.js              -> PASS
node image-swipe-sync.test.js         -> PASS
node package-deal-ui.test.js          -> PASS
node score-details-ui.test.js         -> PASS
```

These results show no obvious collateral UI regression, but they do not cover the stale-cache identity failure.

### Acceptance-only real-schema probe

Result: **defect reproduced**.

This is the decisive test for acceptance because it exercises the deployed production schema and the exact shipped bootstrap code.

## 5. CI / deploy / Pages evidence

### Target production deployment

GitHub Actions run:

- workflow: `Deploy visual mailing`
- run ID: **`33838022027`**
- trigger: push
- target SHA: `6282619c65c134459a4e85c80b9355fe3174e8ae`
- status: completed
- conclusion: **success**
- created: approximately `2026-09-04T04:45:53Z`
- completed: approximately `2026-09-04T04:46:22Z`

Deploy job:

- job ID: **`100914409159`**
- name: `deploy`
- conclusion: **success**

GitHub Pages artifact:

- artifact ID: **`9923930740`**

The packaged site includes at least:

- `feed-bootstrap.js`
- `app.js`
- `data/current.json`
- `index.html`
- the existing UI regression scripts

`index.html` loads `feed-bootstrap.js`, so the changed bootstrap code is part of the deployed runtime path.

The deploy artifact also contains valid active giveaway data (`giveaways.state = active`, one game), while the shipped cache identity logic still collapses real giveaway-only differences.

### Focused-test CI coverage at the target run

At the exact `6282619c...` deploy, `.github/workflows/deploy-visual.yml` did **not** yet execute `scripts/test_feed_bootstrap_cache_identity.js` as part of that workflow. The deploy run covered the existing UI regression scripts. The focused identity test was separately recovered/run during this acceptance.

A later workflow edit adds the focused test for future runs, but that does not change the incorrect identity implementation in `web/feed-bootstrap.js`.

## 6. Production / publication ordering conclusion

Commit time: `2026-09-04T04:45:48Z`.

Its Pages deployment started almost immediately and completed successfully at approximately `2026-09-04T04:46:22Z`.

The original task notes that the user re-checked the real mobile site immediately after the landed commit. The exact wall-clock instant of that phone check is not available here, so it may have overlapped the short deployment window.

That timing ambiguity does **not** change the acceptance classification, because the successfully deployed artifact itself still reproduces the cache collision. Even after deployment completed, the implementation remained insufficient.

Therefore the failure class is:

**`deployed_but_fix_insufficient`**

—not `not_deployed_at_user_check`, and not `newer_correction_deployed`.

## 7. Current `main` check

At acceptance time, current `main` HEAD was:

- `626e08552708459985222fa2c4c33acdd19bedce`

There are later commits after `6282619c...`, but the relevant `web/feed-bootstrap.js` identity logic remains the same faulty implementation introduced by `6282619c...`.

No newer correction for this cache identity defect was found.

## 8. Exactly one bounded follow-up fix

**FOLLOW-UP FIX 1 — production-shaped giveaway cache identity correction**

Change the giveaway component of `payloadIdentity()` to use the **actual production publication provenance**, at minimum `payload.production_contract.source_giveaway_snapshot_blob_sha` (plus only an actual-schema fallback if evidence requires one), and update the focused regression to use a production-shaped payload where `giveaways` is an object and giveaway provenance lives in `production_contract`. The regression must prove that a stale no-giveaway cached payload versus a fresh active-giveaway payload with unchanged ordinary feed fields yields `updated`, while a truly identical payload still yields `identical`.

Do not rely on invented flat `giveaway_generated_at_utc` / `giveaway_status` fields or an array-shaped `giveaways` fixture.

This acceptance task does **not** implement that follow-up.

## 9. User re-check recommendation

**No — do not ask the user to test giveaways on the phone again yet.**

The defective implementation has already reached production and the exact deployed artifact still reproduces the stale-cache collision. First land and deploy the bounded production-shaped identity correction above; only then is another mobile verification meaningful.
