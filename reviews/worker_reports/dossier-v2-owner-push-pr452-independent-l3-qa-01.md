# ЧАТ 3 — независимая L3 QA PR #452: owner-push Dossier Notes V2

- **Task:** `dossier-v2-owner-push-pr452-independent-l3-qa-01`; `WORKER_TASK_DOSSIER_V2_OWNER_PUSH_PR452_INDEPENDENT_L3_QA_01.md`.
- **Verdict:** **CHANGES_REQUIRED**. Do **not** merge [source PR #452](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/452) yet.
- **Exact reviewed source HEAD:** `901dcea905e96849e1da6124c5355b9f3a0f1b94` (re-read live after review); source PR open/draft, 20 changed files. Source base SHA in PR metadata `268abd13816fac0866a677103ef75be82cc26a56`; main readback during QA `b5788bbbe846726ae2ac713ad6c3caf7ed2f9deb`.
- **Mode:** independent code/contract/CI/actual historical smoke inspection; **read-only against source**, no dispatch, source merge, semantic run, real cohort sandbox, old trial mutation or retry. This report is the only added file in a separate report-only draft PR.

## Positive findings and boundaries

1. The introduced `config/dossier_notes_v2_batches/dossier-notes-v2-fresh6-20261114-rerun1.json` contains exactly the six ordered pinned items: `1000010 Crown Trick`, `102600 Orcs Must Die!`, `1029690 Sniper Elite 5`, `49520 Borderlands 2`, `499180 Braid, Anniversary Edition`, `501590 Bulletstorm: Full Clip Edition`. It retains the real historical `prepared_for_date=2026-11-11` and pinned source SHA `665f5d0202859a6bac20566671f10158538e4764`; it is not a new 2026-11-14 snapshot. The existing `batch.rows` assignment hash incorporates the new `trial_id`, separating candidate/receipt paths. The strict preflight cross-checks source worker index, group descriptors and edition names. PR diff does not touch old cohort or original18 state. Old sandbox `sandbox/dossier-notes-v2-fresh6-20261111-first` still resolves to `164f70870e00d1adc124c769a68f4d5c0ac752b4`; new rerun1 branch does not yet exist.
2. New issuer workflow `.github/workflows/issue-dossier-notes-v2-on-owner-push.yml` limits triggering to main push/path with owner ID 315790060/first attempt, and `guard_owner_push` checks genuine GitHub event `before/after/ref/head_commit/sender`, actual parent, sole new source-path addition, remote main SHA, non-existing sandbox and pinned provenance. Separate grant → manifest → nonce marker → authorization commits and exact branch readbacks are implemented. The authorizer's run ID is subsequently checked using real GitHub Actions REST `status=completed`, `conclusion=success`, first attempt, owner actor, workflow path and exact main source SHA. PR CI cannot substitute for this future owner run.
3. `scripts/dossier_notes_v2_connector_transport.mjs` and Assembly launcher now admit the exact rerun1 `owner_main_push` authorization via one owner Action; legacy cohorts still require two manual owner Actions, and manually originated issuer anchors intentionally remain structurally byte-compatible. Strict Research candidate/typed receipt and existing final writer checks remain. Global inactive/prod flags, V1/Deep, schedules and semantic research are not activated in the source changes.
4. Genuine disposable capabilities, **not live Research**: owner branch `push` [Actions 43682622350](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43682622350), and owner `sandbox/` `push` [Actions 43682840859](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43682840859), both `success`, owner actor id 315790060 and attempt 1. The sandbox run confirms GitHub Actions write ability; it does not prove new workflow issuance or new typed Research receipts.
5. At reviewed exact source HEAD, all four mandatory PR runs are `completed/success`, `event=pull_request`, `run_attempt=1`, `head_sha=901dcea…`:
   - [43683543527](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43683543527) — inactive Research Notes V2, owner-push synthetic suite, route, Research receipt, JS connector, legacy receipts, strict-writer fixture, syntax and flags;
   - [43683543506](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43683543506) — inactive eventual-chain acceptance;
   - [43683543519](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43683543519) — site task registry;
   - [43683543478](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/43683543478) — backlog dispositions.
   Job/step readback confirms success. CI runs *synthetic fixtures* and cannot certify every authorization/provenance invariant.

## Finding L3-001 — HIGH: one authenticated owner push can launder another candidate into a typed receipt

**Code evidence:** `scripts/dossier_notes_v2_research_receipt_ingest.py`:
- `_owner_push_candidate_gate` around lines 182–251 authenticates the **triggering** push and returns one specific `candidate` path after checking the event's sole Git introduction.
- `run_authorized` lines 254–260 calls `_owner_push_candidate_gate(repo,trial_id,env)` **but discards its returned path**.
- `run_authorized` line 275 calls unrestricted `ingest_local(repo,trial_id=...,anchor=...)`.
- `ingest_local` lines 76–151 walks **all six** manifest items and creates receipts for every existing single-introduction candidate; `single_introduction`, `prepare_receipt` and `inspect_receipt_commit` verify Git ancestry/bytes/schema, but do **not** authenticate the per-candidate original GitHub push actor/event.
- The new synthetic test `scripts/test_dossier_notes_v2_owner_push.py::test_owner_candidate_push_serial_receipt_strict_first_parent_and_sibling` (around lines 189–247) deliberately creates **two** candidates and accepts two receipts from one unrestricted `ingest_local` call. It never tests a candidate introduced by a non-owner followed by a distinct owner push.

**Reproducible negative scenario (reasoned from exact source, not executed on live GitHub):**
1. On an otherwise authorized rerun1 sandbox, an actor with branch write capability other than the authorized owner creates a structurally valid one-add Research candidate **A**. That event does not pass the owner-only Actions gate.
2. The owner later uses the approved `create_file` on valid frozen candidate **B**, creating a genuine first-attempt owner push. `_owner_push_candidate_gate` passes for B.
3. The same Actions run enters `ingest_local` and creates a typed Research receipt for **both A and B** (assuming A passes the existing content checks), although **A has no independently verified authenticated owner-push event**. A can then pass the typed-receipt prerequisite for Assembly.

This violates the task's **strict actor/event/path/candidate-only one-add per Research receipt** invariant; it is an authorization boundary gap, even though candidate bytes remain immutable and isolated to this sandbox. Exploitability depends on another actor having sandbox write permission; the invariant cannot rely on that permission assumption. The real owner-push feature is **not yet active**, so no actual unauthorized receipt was observed.

## Finding L3-002 — MEDIUM, coupled: default concurrency does not preserve every candidate event

The automatic workflow `.github/workflows/ingest-dossier-notes-v2-research-on-owner-push.yml` lines 18–20 shares a single concurrency group with the manual ingest; `cancel-in-progress: false` prevents cancellation of the **running** job, but default GitHub concurrency may **replace an existing pending run** when rapid owner `create_file` pushes produce more pending events. See [official GitHub concurrency documentation](https://docs.github.com/en/actions/concepts/workflows-and-actions/concurrency).

The current unscoped six-item sweep partly compensates for lost intermediate events, **but causes L3-001**. A naïve fix that processes only the current event's candidate while retaining default pending replacement risks leaving some of the six valid candidates permanently without automatic receipts (bot pushes do not start a replacement Action and automatic semantic retries are prohibited). No test demonstrates six rapid owner pushes, pending-run replacement, and every candidate both individually actor-attested and eventually receipted.

This is a conditional operational risk, not a claim that pending runs were actually canceled in the real trial.

## Required one bounded scoped fix (source PR #452 only)

Fix the **automatic owner-push Research receipt pathway** as one coherent change: (a) every auto-created receipt must be causally bound to authentic owner event evidence for **that exact candidate introduction**—not merely to one later owner event elsewhere in the cohort; (b) preserve durable per-candidate event delivery or an equally strong authenticated evidence registry under concurrent six single-file pushes, including GitHub's pending-run behavior; (c) keep strict first-parent, exact Git SHA/bytes/privacy, no-force CAS, idempotent one receipt, honest invalid/missing evidence and sibling independence; (d) do not weaken manual cohort behavior or require the user to open GitHub UI.

Add adversarial offline fixtures: unauthorized A then owner B must **never** receipt A; six quick owner pushes with possible pending-run replacement must eventually receipt each authentically introduced candidate; duplicate/replayed event, actor/bot/wrong branch, stale/modified path, CAS race, failed candidate and old manual issuer/receipt byte preservation. Re-run the four required exact-HEAD PR workflows and independent QA. **No merge or real Research until fixed.**

## Coverage / limitations / decision

- Inspected mandatory START/route/policy/decisions/task contracts, source PR diff, issuer, research ingest and candidate validators, legacy/manual workflow, current Assembly connector path, source fixtures and exact CI run details. No source writes, workflow dispatch, owner-authority pushes, synthetic disposable pushes or semantic Research were performed by this QA.
- An independent clone/run of the exact scripts was **not** possible in the tool runtime (GitHub host DNS inaccessible to local `git ls-remote`); existing exact-HEAD GitHub CI is actual execution of the named synthetic test suites, not this reviewer's independent rerun. L3-001 is a direct call-graph/provenance finding that current passing tests do not cover.
- The new rerun1 issuer Actions run, real sandbox authorization, actual Research candidates, auto receipts, Assembly and final writer have **not** executed. Those must only be evaluated after source acceptance and a genuinely authenticated owner `main` event.
- **Final status: `CHANGES_REQUIRED`**, not `PASS_FOR_DIRECTOR_MERGE_REVIEW`. Return one narrowly scoped owner-push receipt provenance/concurrency fix to the source developer; independently QA its exact new HEAD. Do not ask the user to launch GitHub Actions manually.

## QA effort / future speed

Primary time went to reading source and immutable contracts, verifying live Actions metadata and following the candidate-to-receipt trust path; 4/4 green CI alone was insufficient. Next pass can start from L3-001/L3-002 call sites, the new adversarial fixture and exact PR HEAD/CI, rather than repeating repository-wide discovery.
