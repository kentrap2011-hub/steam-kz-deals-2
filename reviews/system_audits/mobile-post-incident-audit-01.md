# Mobile Post-Incident Audit 01

Date: 2026-09-03
Task ID: `mobile-post-incident-audit-01`
Role: `SYSTEM AUDITOR`
Mode: `READ-ONLY / AUDIT`
Status: `complete`

## Scope and boundary

This audit used the compact incident evidence required by `WORKER_TASK_MOBILE_POST_INCIDENT_AUDIT_01.md` and only bounded current production evidence needed to answer the five required questions.

No production code, data, workflow, UI behavior, cache behavior, queue/ranking logic, or release was changed. The only repository write performed by this audit is this report.

Audited accepted production release:

- release: `f745dac844213880cd7eb984573877f58803a3f0`;
- Pages run: `33779042331` (`Deploy visual mailing`, run `256`, `success`);
- affected Android real-device acceptance: `works` on 2026-09-03, as recorded by the Director.

A bounded compare of `f745dac844213880cd7eb984573877f58803a3f0...main` showed no subsequent change to `web/**`, `tests/feed-bootstrap.test.js`, or `.github/workflows/deploy-visual.yml`; the accepted mobile client implementation therefore remains the current mobile implementation under review.

## Executive conclusion

The cache-first stabilization preserves the existing canonical ownership model. `data/current.json` remains the only feed input requested by the application; the browser Cache Storage entry is one last-known-good presentation copy of a previously successful canonical response, and every fresh replacement still comes from the canonical network URL. The cache layer does not own ranking, filtering, queue construction, or rendering.

The stabilization also did not introduce a second renderer, service worker, polling loop, background scheduler, or unbounded local data plane. There is one cache entry for the canonical URL, one singleton initial bootstrap promise, one singleton background refresh promise, and at most two network attempts per bootstrap/refresh operation. A changed fresh payload is reapplied by calling the existing `window.init()` path, so `web/app.js` remains the authoritative queue builder and renderer.

The remaining system-level gap is regression gating, not client behavior. The focused `tests/feed-bootstrap.test.js` regression covers the original silent-blank/network-blocking class plus cache-first/lifecycle behavior and passed during implementation, and the affected real device has accepted the deployed behavior. However, the canonical Pages deploy workflow's `Run UI regressions` step does not execute that focused test. A future edit could therefore reintroduce this class while the normal Pages deploy remains green. This is concrete enough to justify one bounded follow-up task, but not to reopen or redesign the already accepted mobile implementation.

The previous mobile incident blocker on the already accepted visual-freshness production release is gone. The visual-freshness failure class remains a separate proven production risk from System Audit 02, so its release priority is now, not after the mobile regression-gate follow-up.

## Required-question disposition

1. **Canonical ownership preserved? — yes, proven.** The canonical network URL remains `data/current.json`; deploy still stages `data/production/visual/current.json` to `web/data/current.json`; Cache Storage is a validated last-known-good presentation fallback and only a successful fresh canonical response can replace it.
2. **Second renderer / polling / service worker / scheduler / unbounded local plane introduced? — no, proven.** The cache controller reuses `window.init()`, bounds attempts to two, keeps singleton bootstrap/refresh promises, stores one response entry, and adds no service worker or polling scheduler.
3. **Durable regression/acceptance story sufficient? — partially.** Real-device acceptance and focused behavioral regression coverage are strong, but the focused regression is not part of the canonical Pages deploy gate, so return of the failure class is not guaranteed to fail a normal deploy.
4. **New implementation task justified now? — yes, one bounded regression-gate task only.** No client/cache redesign or further mobile debugging is justified without new runtime evidence.
5. **Visual-freshness release ordering changed? — yes.** Mobile stabilization removes the prior blocker; the already accepted visual-freshness release should proceed now.

## Finding 1 — Canonical data and renderer ownership remain singular

**User impact**

Repeat visits can render a last-known-good feed immediately without creating a second source of recommendation truth. Fresh data still replaces the visible cached copy only through the existing application path, avoiding split-brain queue/ranking/render behavior.

**Exact evidence**

- `web/app.js` blob `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5` still defines `DATA_URL='data/current.json'`; its existing `init()` parses that response, builds the queue, and calls the existing renderer.
- `web/feed-bootstrap.js` blob `67fbc7866ac5a7244f0fd8a467e2e0a3925235c7` keys the local cache by the resolved canonical data URL, validates cached/network payload shape, performs fresh network revalidation against the same request, and applies changed fresh payloads through `window.init()` rather than a duplicate renderer.
- `.github/workflows/deploy-visual.yml` blob `625a22da18300795974ba6e3b46c6b92db1184d4` still copies `data/production/visual/current.json` to `web/data/current.json` for Pages publication.
- Cache-first implementation report blob `8c80b9da35057ff6443665468329db37bfc8c8b1` explicitly records one last-known-good Cache Storage entry and canonical network ownership.

**Severity:** `low`

**Classification:** `proven`

**Bounded next action:** none.

## Finding 2 — The cache-first layer is bounded and does not create a hidden execution plane

**User impact**

The accepted fix does not add an uncontrolled refresh loop, duplicate renderer, background scheduler, or growing client-side data store that could silently consume network/battery or diverge from production ownership.

**Exact evidence**

- `web/feed-bootstrap.js` blob `67fbc7866ac5a7244f0fd8a467e2e0a3925235c7` has one `bootstrapPromise`, one `refreshPromise`, a 9000 ms timeout, and a maximum of two attempts per bounded network operation; lifecycle recovery can only consume the already allowed retry and skips once a feed is ready/delivered.
- The same blob stores under cache name `steam-deals-feed-lkg-v1` and one canonical request key; no history list, IndexedDB queue, polling timer, or service-worker registration is present in the accepted mechanism.
- `web/index.html` blob `56e92cd99c9a63eaa4f5cd470464652a4751ac8f` loads the bootstrap wrapper directly before the existing `app.js`; it does not register a service worker.
- Cache-first implementation report blob `8c80b9da35057ff6443665468329db37bfc8c8b1` records no polling queue, second data source, service worker, server cache, second renderer, or duplicated filtering/ranking logic.

**Severity:** `low`

**Classification:** `proven`

**Bounded next action:** none.

## Finding 3 — The incident-specific regression exists but is not a canonical Pages release gate

**User impact**

A future change to feed bootstrap/cache/lifecycle behavior could reintroduce a silent-blank or network-blocking regression while the normal Pages deployment still reports success, delaying detection until another real-device complaint.

**Exact evidence**

- `tests/feed-bootstrap.test.js` blob `f4ec8a8d4165cbacdef67a27587494e07972c307` covers cache-first immediate render, slow/pending refresh, refresh failure, corrupt cache fallback, bounded timeout, lifecycle duplicate prevention, cache-write-after-renderability, and unchanged non-feed semantics.
- Cache-first report blob `8c80b9da35057ff6443665468329db37bfc8c8b1` records focused result `feed instant cache regression: PASS`.
- Production Pages release `f745dac844213880cd7eb984573877f58803a3f0` deployed successfully in run `33779042331`, and the Director subsequently recorded affected-device acceptance as `works`.
- Current production `.github/workflows/deploy-visual.yml` blob `625a22da18300795974ba6e3b46c6b92db1184d4` runs `web/image-swipe-sync.test.js`, `web/package-deal-ui.test.js`, `web/score-details-ui.test.js`, and `web/giveaway-ui.test.js`, but does **not** run `tests/feed-bootstrap.test.js`.
- The already accepted visual-freshness deploy workflow blob `7479a56ac7ee363e6a212952e58f36558b371877` retains the same UI-regression list and likewise does not yet close this mobile-specific gate gap.

**Severity:** `medium`

**Classification:** `proven`

**Bounded next action:** add `node tests/feed-bootstrap.test.js` to the canonical Pages deploy UI-regression gate and prove one normal passing Pages run. Do not change caching, rendering, lifecycle semantics, or mobile UI as part of that task.

## Visual-freshness ordering

System Audit 02 already established the visual stale-success risk as `high / proven`: the fix is accepted and release-ready but not active on production `main`. Exact accepted refs remain:

- implementation report blob `e5226710d435cfbb1c0190e11d937b025ceb9aac`;
- final acceptance report blob `6a691fb29d88b1785accf717752149e027265a2c`;
- accepted build workflow blob `b497093eef1f5dac0bfd5efd9d3ef69bb272cb67`;
- accepted deploy workflow blob `7479a56ac7ee363e6a212952e58f36558b371877`.

`DIRECTOR_TASK_BOARD.md` blob `03229a754bf6eaf74ea1a3aa3f3458aa43246a5c` records that the visual-freshness release was deferred during the active mobile incident and that there is now no active mobile incident blocker. The medium regression-gate gap above is orthogonal to the accepted visual-freshness production risk and does not justify delaying that release.

## Exact incident refs

- recon report blob: `48700dc77ac17fa031dd129996bef74075d86872`;
- first resilience-fix report blob: `61b23ffc479dff473310b1d7aed0d36d43a11c8f`;
- cache-first follow-up report blob: `8c80b9da35057ff6443665468329db37bfc8c8b1`;
- accepted production release: `f745dac844213880cd7eb984573877f58803a3f0`;
- production `web/feed-bootstrap.js`: `67fbc7866ac5a7244f0fd8a467e2e0a3925235c7`;
- production `web/app.js`: `a1b86ba6cf6ca6f2b24a68ad47756d6c86d02ef5`;
- production `web/index.html`: `56e92cd99c9a63eaa4f5cd470464652a4751ac8f`;
- focused regression: `f4ec8a8d4165cbacdef67a27587494e07972c307`;
- production deploy workflow: `625a22da18300795974ba6e3b46c6b92db1184d4`;
- Pages deployment run: `33779042331` (`success`);
- checkpoint blob: `9052c8acdc79b76700a45872fd5b752406268ac5`;
- Director board blob: `03229a754bf6eaf74ea1a3aa3f3458aa43246a5c`.

Recommended next task: `mobile-feed-regression-gate-01` — wire the existing `tests/feed-bootstrap.test.js` into the canonical Pages deploy regression gate and prove one ordinary passing deploy; no client redesign.

Mobile incident systemic closure: needs_followup
Visual freshness release priority: now