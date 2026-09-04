# GIVEAWAY PUBLICATION GAP FIX 01

STATUS: complete

## TASK

- Task ID: `giveaway-publication-gap-fix-01`
- Mode: `IMPLEMENT`
- Goal: close the proven publication gap where healthy canonical giveaway data did not refresh the existing visual/publication payload.
- Prior recon: `reviews/worker_reports/giveaway-publication-gap-recon-01.md`
- Required report: `reviews/worker_reports/giveaway-publication-gap-fix-01.md`

## ARCHITECTURE PREFLIGHT

The publication transform and downstream visual refresh are owned by the existing GitHub Actions control plane. No new scheduler, queue, writer, retry owner, or publication path was introduced.

The bounded fix stays inside:

```text
data/production/giveaways/v1/current.json
  -> existing Build daily visual payload / giveaway_refresh
  -> data/production/visual/current.json
  -> existing Deploy visual mailing
  -> staged web/data/current.json
  -> GitHub Pages
```

No execution authority was moved into the worker chat.

## IMPLEMENTATION

### 1. Route canonical giveaway commits into the existing bounded giveaway refresh

Changed only `.github/workflows/build-daily-visual-payload.yml` classifier allow-list so the already-watched canonical path:

```text
data/production/giveaways/v1/current.json
```

is accepted by the existing `giveaway_only` route.

Implementation commit:
- `b4db23ea0bacbcf00dfaa264c2c27abff502b7c7`
- message: `Route canonical giveaways through bounded visual refresh`
- resulting workflow blob: `90452c73f60addce11a7a6fdc1fa475de7ed3cd7`

No new workflow or alternate publication route was added.

### 2. Runtime-only deploy blocker found while owning the required deploy verification

The first deploy attempt after the correct giveaway visual refresh reached the existing publication workflow and proved that:
- giveaway validation passed;
- UI regressions passed;
- `data/production/visual/current.json` was copied to `web/data/current.json`;
- but the workflow then failed before Pages upload because an existing heredoc inside `Bind staged publication to triggering build freshness receipt` was syntactically invalid in shell command substitution.

Failed deploy run:
- `33832101629`
- workflow: `Deploy visual mailing`
- conclusion: `failure`
- head: `a05aec8daf37958571ece0ab8a6688cfd8820585`

Exact runtime error:

```text
warning: here-document ... delimited by end-of-file (wanted 'PY')
unexpected EOF while looking for matching ')'
```

This was new independent runtime evidence in the same proven publication path, so the smallest necessary publication fix was applied: replace only that fragile heredoc command substitution with an equivalent `python -c` expression. Freshness classification semantics and all validation gates remain unchanged.

Deploy syntax fix commit:
- `ee0a609cfa15612e19249089206fefa9d6dda714`
- message: `Fix visual deploy freshness classification shell syntax`
- resulting deploy workflow blob: `0277832efce8d4f5db6f489143cc47bc97d43b8b`

The commit diff changes only the shell mechanism used to read the existing receipt classification; it does not relax or bypass freshness/completeness checks.

## CANONICAL / VISUAL PROVENANCE

Canonical giveaway current:
- path: `data/production/giveaways/v1/current.json`
- blob: `33c1318a4950450aadb41b98a9552223b5cf43b8`
- contains active Epic giveaway `Alone With You`.

Bounded refresh produced:
- visual commit: `a05aec8daf37958571ece0ab8a6688cfd8820585`
- message: `Refresh giveaway visual payload`
- visual blob: `45636d95a97d4e763115d076fea8c451ccb74231`

The refreshed visual payload records:

```text
production_contract.source_giveaway_snapshot_blob_sha = 33c1318a4950450aadb41b98a9552223b5cf43b8
```

This exactly matches the canonical giveaway blob above; the stale pre-fix giveaway provenance is no longer used.

The refreshed giveaway sibling is active and contains one game:
- `Alone With You`
- Epic claim URL: `https://store.epicgames.com/en-US/p/alone-with-you-028a15`
- active promotion through `2026-09-10T15:00:00Z`.

## BOUNDED WORKFLOW VALIDATION

Canonical routing implementation triggered:
- workflow run: `33832075509`
- workflow: `Build daily visual payload`
- event: `push`
- head: `b4db23ea0bacbcf00dfaa264c2c27abff502b7c7`
- conclusion: `success`

Job selection proved the bounded route:
- `scope`: success
- `giveaway_refresh`: success
- general `build`: skipped
- `no_build_receipt`: skipped

Inside `giveaway_refresh`:
- giveaway visual handoff regression suite: `11 tests` passed;
- refresh result: `VISUAL_GIVEAWAY_REFRESH=BUILT changed=true state=active offers=1`;
- generated giveaway validation: `GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=1`;
- paid payload SHA before: `d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`;
- paid payload SHA after: `d2e0f7d95fd2de9ffc45c562d34dde5e0f7904dda7ab5cf694e21a01bbe94799`;
- structural guard: `GIVEAWAY_AUXILIARY_DIFF=PASS non_giveaway_state_unchanged=true`.

Therefore the fix refreshed only the giveaway sibling/provenance and did not mutate the accepted paid visual payload.

## DEPLOY VALIDATION

After the syntax-only publication blocker fix, the existing deploy workflow ran again:
- successful deploy run: `33832350887`
- workflow: `Deploy visual mailing`
- event: `push`
- head / Pages build version: `ee0a609cfa15612e19249089206fefa9d6dda714`
- conclusion: `success`
- Pages environment URL: `https://kentrap2011-hub.github.io/steam-kz-deals-2/`

Runtime proof from the successful deploy:
- visual mutation classified as `giveaway_only`;
- `non_giveaway_state_unchanged=true`;
- paid visual accepted as reused existing canonical payload;
- giveaway validator: `GIVEAWAY_VISUAL_PAYLOAD=PASS state=active offers=1`;
- all UI regressions passed, including `GIVEAWAY_UI_TESTS=PASS`;
- staged `web/data/current.json` successfully;
- Pages artifact uploaded;
- `actions/deploy-pages@v4` reported deployment success.

For this direct workflow-path verification the existing freshness outcome was explicitly `unbound/non_workflow_run`; that state was not changed or reclassified as fresh. No freshness decision was weakened.

## PUBLISHED PAYLOAD PROOF

Exact Pages artifact from successful deploy run `33832350887`:
- artifact name: `github-pages`
- artifact ID: `9922110216`
- artifact digest: `sha256:c76443526a53e8e50f625d7a19f1dc1ed87875fd3ca3acc83441598824ac581e`
- deployed Pages build version: `ee0a609cfa15612e19249089206fefa9d6dda714`

The worker downloaded that exact artifact, unpacked its `artifact.tar`, and inspected the exact deployed file:

```text
data/current.json
```

Verified content:

```text
giveaways.state = active
giveaways.accepted_offer_count_at_build = 1
giveaways.games[0].title = Alone With You
```

The deployed payload also contains the expected Epic claim URL and active promotion end.

Therefore the technically published Pages payload now contains `Alone With You`.

A separate direct HTTP fetch of the Pages URL from the worker container could not be used because that container's external DNS resolution failed. This does not invalidate the publication proof: the exact artifact was inspected, and GitHub Pages reported successful deployment of that exact artifact/build version.

## SCOPE / STRICTNESS CHECK

Unchanged:
- Epic parser;
- giveaway source rules and current-100%-promotion discriminator;
- ITAD / IGDB;
- Taste / semantic ranking;
- paid deal/ranking payload;
- giveaway UI behavior/design;
- source completeness rules;
- visual freshness receipt contract;
- freshness classifications;
- existing workflow ownership and publication path.

No fallback, alternate source, manual title inference, alternate deployment path, or relaxed completeness/freshness rule was introduced.

## USER SITE VERIFICATION

Still required: **yes**.

Technical end-to-end publication is complete: the exact deployed Pages artifact contains `Alone With You`. Per project protocol, only the user can close the final real-browser UX check by opening the actual site and confirming that the giveaway card is visibly rendered in their browser.

If the user still does not see it after a hard refresh, that would be new independent browser/UI/cache evidence and should be investigated separately without reopening the Epic parser by default.

## EXACT REFS / RUNS

- canonical giveaway blob: `33c1318a4950450aadb41b98a9552223b5cf43b8`
- routing fix commit: `b4db23ea0bacbcf00dfaa264c2c27abff502b7c7`
- routing workflow blob: `90452c73f60addce11a7a6fdc1fa475de7ed3cd7`
- bounded build/refresh run: `33832075509` — success
- refreshed visual commit: `a05aec8daf37958571ece0ab8a6688cfd8820585`
- refreshed visual blob: `45636d95a97d4e763115d076fea8c451ccb74231`
- first deploy run: `33832101629` — failure on pre-existing shell syntax after staging
- deploy syntax fix commit: `ee0a609cfa15612e19249089206fefa9d6dda714`
- deploy workflow blob: `0277832efce8d4f5db6f489143cc47bc97d43b8b`
- successful Pages deploy run: `33832350887` — success
- deployed Pages artifact ID: `9922110216`
- deployed artifact digest: `sha256:c76443526a53e8e50f625d7a19f1dc1ed87875fd3ca3acc83441598824ac581e`

## STATUS DECISION

`complete`

The proven canonical-to-visual publication gap is repaired, the visual provenance now points at the current healthy giveaway snapshot, the bounded route is runtime-proven, and the exact successfully deployed Pages artifact contains `Alone With You`.

Only the user's final real-site visibility check remains; it is not a technical blocker for this implementation status.

## REUSABLE LESSON

When a canonical auxiliary payload already has an existing bounded refresh job, keep the repair at the routing boundary: make the canonical path eligible for that route, then prove source-blob provenance, unchanged unrelated payload fingerprints, staged artifact content, and the exact deployed artifact before declaring publication complete.
