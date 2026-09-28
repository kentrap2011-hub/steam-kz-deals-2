# WORKER TASK — STALE DEEP STATISTICS PUBLICATION DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Repository scope guard:
- use only repository `kentrap2011-hub/steam-kz-deals-2`;
- if GitHub/tool opens another repository or target is ambiguous, stop and switch first.

Task ID: `stale-deep-statistics-publication-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable report:
`reviews/worker_reports/stale-deep-statistics-publication-diagnostic-01.md`

## User-observed symptom

At approximately 2026-09-28 21:56 user-local time, the live site Statistics page still showed the older Deep snapshot:

- displayed Deep total scope: 387
- authoritative completed: 30
- fit: 24
- not-fit: 6
- incomplete/recovery: 10
- waiting for Dossier: 338
- ready/pending: 9
- remaining until authoritative: 357
- last Deep write shown: 28.09.2026 20:47

The user had just run Progressive Deep again. That worker reported:

- run-start anchor: `2aa42b36850039e106dca26d4b7a2ff31a8cd070`
- frozen authority: `97012741145611e481858f0e3bc981992ef869bd`
- frozen queue: exactly 1 item
- item: `STAR WARS™ Battlefront`
- result: `analyzed_not_fit`
- result commit: `40e0ba34808314634582770886a1829a7254ab91`

## Already-established Director evidence

Do not discard or needlessly rediscover these facts. Verify only where necessary.

### A. Frozen Deep authority really had one item

At frozen authority `97012741145611e481858f0e3bc981992ef869bd`,
`data/production/pre_ai/progressive_pass2_work.json` had:

- total current coverage target: 399
- first-pass attempted: 54
- authoritative completed: 44
- completed fit: 38
- completed not-fit: 6
- incomplete/recovery: 10
- waiting for Dossier: 344
- ready/pending: 1
- remaining until authoritative: 355
- ordinary work item count: 1
- sole item: `STAR WARS™ Battlefront` / AppID 1237980

So the worker's "1 item" statement was correct for its frozen invocation.

### B. The ready queue had previously drained 9 -> 1

Canonical PASS 2 work history shows this sequence:

- `23e39f8ee4e0380515cc6c5bbc35ae91345a9abc`: ready 9
- `dede9ea264b834819642b6e23f778cabd85a4fdd`: ready 8
- `fe6380a392d43d58489f33f61192a643734d998e`: ready 7
- `284d0f60e55b902c4958cc688041b2931bf2d54f`: ready 6
- `e288a8da6db97fc96ac1b41c3f81d0ae2f9f0af7`: ready 5
- `a0c7d2c989c94eea73e9b81bd4c059292ffb173d`: ready 4
- `6bc5e23f1efb28bd2024bcf7b3ad8f39eb6f2498`: ready 3
- `11e9ff705d9d0f7c9c86021f1e2bb7706d708fe0`: ready 2
- `3080233c1b3dcd04d4dab199b3a2bef3c94ae2d8`: ready 1

Thus the site's visible "9" was already stale relative to the frozen invocation.

### C. Current main later advanced again

At Director inspection after the fresh screenshot, current `main` PASS 2 work showed:

- total current coverage target: 399
- first-pass attempted: 54
- authoritative completed: 44
- fit: 38
- not-fit: 6
- incomplete/recovery: 10
- waiting for Dossier: 340
- ready/pending: 5
- remaining until authoritative: 355

The five current work items were:

1. STAR WARS™ Battlefront
2. Nexomon: Extinction
3. Roadwarden
4. Blazing Sails
5. Assemble with Care

This later increase from 1 to 5 is consistent with new Dossier availability and is separate from the stale-site symptom.

### D. Publication workflows did run later, but the visual payload remained old

Recent workflow facts already observed:

- `Build daily visual payload` run 885, ID `36459026993` — success
  - head SHA: `9cb123765884440d37632740d51695a371338483`
  - created ~17:34 UTC
- `Deploy visual mailing` run 926, ID `36459102720` — success
  - same head SHA `9cb123765884440d37632740d51695a371338483`

However `data/production/visual/current.json` at that deployed head still reports:

- `generated_at_utc=2026-09-28T16:49:10.166499+00:00`
- `item_count=381`

The same old generated timestamp/content was still present at later inspected main commit `f200e809f169c7bd6b0ee74de3775bc8b6043614`.

Therefore this is no longer explainable merely as "the user opened the page before the next deploy". A later successful build/deploy occurred, yet the published data remained based on an older visual snapshot.

### E. Important workflow anomaly near the same period

Observed around the publication chain:

- Build pre-AI deterministic payload run 221, ID `36458961528` — **failure**
  - head `9cb123765884440d37632740d51695a371338483`
- Build daily visual payload run 884 — cancelled
- Build daily visual payload run 885 — success
- Deploy visual mailing run 926 — success

Do not assume the failed pre-AI build is the root cause. Prove the first divergence.

## Goal

Determine exactly why the live Statistics page remained on the old Deep counts even after canonical Deep/PASS 2 state advanced and later visual/deploy workflows succeeded.

The diagnostic must identify the FIRST point where fresh Deep state fails to become the data actually consumed by the Statistics page.

## Required investigation

### 1. Identify the exact live Statistics data source

Trace the exact source used by the deployed Statistics UI.

Do not assume it is the top-level fields of `data/production/visual/current.json`.

Identify:
- exact generated file/path in repository or Pages artifact;
- exact producer script;
- exact workflow;
- exact deploy input;
- whether browser reads one payload or a separate statistics payload;
- whether service worker/cache can retain that payload independently.

### 2. Pin the stale displayed snapshot

Find the exact canonical artifact/commit whose statistics correspond to the user's screenshot:

- total 387
- completed 30
- fit 24
- not-fit 6
- incomplete 10
- waiting 338
- ready 9
- remaining 357
- last write 20:47 local

Prove whether the screenshot is:
- an old Pages artifact,
- an old generated statistics subsection embedded in a newer visual artifact,
- browser/service-worker cache,
- or another source.

### 3. Trace fresh Deep state through the publication chain

For at least these checkpoints, record the relevant Deep counters and commit/artifact identity:

1. canonical PASS 2 state/work after the 9-ready snapshot;
2. canonical state at frozen authority `970127...`;
3. state after later accepted Deep results;
4. pre-AI deterministic output;
5. visual build input;
6. final visual/statistics payload;
7. Pages artifact;
8. deployed Pages version;
9. browser/service-worker fetch target if applicable.

Find the first checkpoint that remains stale.

### 4. Explain successful build/deploy with stale data

Run 885 and deploy 926 succeeded after the Deep state had advanced.

Determine precisely why success did not imply fresh statistics.

Possible classes to confirm or reject:
- build reused an already-generated visual file;
- upstream pre-AI failure caused a legal fallback to stale input;
- trigger/concurrency caused a build against an older parent;
- statistics generation is not triggered by PASS 2 changes;
- deploy copied an old artifact;
- Pages artifact was fresh but browser/service worker served stale bytes;
- downstream commercial refresh preserved old semantic/statistics fields;
- another exact cause.

Do not choose a cause without evidence.

### 5. Scope/count differences

Explain separately why:
- canonical Deep target may be 399,
- Statistics page showed 387,
- feed showed 381.

Do not conflate legitimate publication filtering with staleness.

The diagnosis must distinguish:
- stale counters;
- intentionally filtered published scope;
- hidden `analyzed_not_fit` cards;
- expired/commercially filtered items if relevant.

### 6. User-facing conclusion

State in plain Russian:
- whether site statistics are actually stale;
- exact cause;
- whether refreshing/clearing browser cache would help or would not help;
- whether the defect is publication, deployment, service worker, or UI;
- whether Deep accounting itself is correct.

## Scope limits

READ-ONLY diagnosis only.

Do NOT:
- run Deep/Fast/Dossier;
- rerun workflows;
- rebuild/deploy;
- edit service worker;
- change production state;
- change ranking;
- change Scheduled Tasks;
- interfere with active ЧАТ 1 ranking implementation.

## Report

Write:
`reviews/worker_reports/stale-deep-statistics-publication-diagnostic-01.md`

Required sections:
1. `Task`
2. `Pinned user-visible stale snapshot`
3. `Canonical Deep truth`
4. `Exact Statistics data source`
5. `Publication timeline`
6. `First divergence`
7. `Why successful build/deploy stayed stale`
8. `399 vs 387 vs 381`
9. `Browser/service-worker role`
10. `User-facing explanation`
11. `Changes` — report only
12. `Unresolved`
13. `Status`
14. `Recommended next step` — exactly one bounded next task or `none`
15. exact commit/run/artifact refs
16. `Efficiency / reusable lesson`

Allowed final statuses:
- `complete`
- `needs_fix`
- `blocked`
- `needs_user_decision`

Do not start another task after this one.
