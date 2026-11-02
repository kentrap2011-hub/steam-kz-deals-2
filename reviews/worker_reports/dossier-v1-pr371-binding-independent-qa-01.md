# Independent QA — Dossier V1 PR #371 exact product binding null masks

- **Task:** `dossier-v1-pr371-binding-independent-qa-01`
- **Role:** independent focused L2/L3 read-only source QA; **report-only** draft PR, no semantic execution.
- **Repository / source of truth:** `kentrap2011-hub/steam-kz-deals-2` / `main`.
- **Source PR:** [#371](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/371), draft, base `main`.
- **Exact reviewed source HEAD:** `56f59ce92b6e529fbccf3d0327b277d6338f8157`.
- **Reviewed base at PR inspection:** `32a427503a459c66173eb60de938c78cdefd08fc`.
- **Verdict:** **PASS_FOR_DIRECTOR_MERGE_REVIEW** — limited to the proposed serialization/prompt correction and observed CI, **not** approval of old dossier transport, live feedback truth or a production/manual semantic invocation.

## Independent delta scope and canonical boundary

GitHub's entire PR file list contains exactly:
1. `config/taste_steam_review_dossier_worker_prompt.md` — one added explanatory block and three illustrative masks.
2. `scripts/test_taste_dossier_pragmatic_evidence_model.py` — synthetic fixture helper, imports and PRAG-16..20 regressions.
3. `reviews/worker_reports/dossier-v1-exact-product-binding-null-mask-implement-01.md` — implementer report.

No source changes to canonical strict ingestion, evidence schema/contract, ownership, runtime marker, frozen descriptor machinery, queue, workflows or production data. Git blob SHA comparisons between source HEAD and `main` confirmed unchanged:
- web-evidence contract `c52c611459e513ecc2a776b33d7ad830741386be`;
- strict validator `e6f0d0ee93cc03f03f702bf19fa9e517c853a6b5`;
- execution ownership `cf5d96f1d758117991e571832147d7b9aa93e507`;
- Dossier contract `1335d3df358e9ec38064e026b48169f7d9ab69ee`;
- frozen invocation authority `1e5391093c1131bb430d1dd8ca60128163819652`;
- runtime prompt `5743c85120db2b7f50cb4230c3ba1d44e7950017`.

GitHub retains plan, group identity/ordering, strict validation, pending/failed/recovery, persistence and scheduling authority; the semantic worker remains constrained to truthful source observations and create-only transport.

## L2 — source-observed product identity / null-mask test

Manually checked the added instruction against `config/taste_steam_review_dossier_web_evidence_contract.json#exact_product_observation_binding` and `scripts/taste_steam_review_dossier_strict.py::_validate_exact_product_binding`:

| Basis | What the **single inspected source/result** must prove | Serialized four-field mask |
| --- | --- | --- |
| `source_appid` | exact source-observed AppID only | `{"basis":"source_appid","appid":"910001","title":null,"release_year":null}` |
| `source_title_release` | exact source-observed product title **and** release year | `{"basis":"source_title_release","appid":null,"title":"Example Game","release_year":2020}` |
| `source_appid_title_release` | exact AppID, title **and** year all from the same actual source/result | `{"basis":"source_appid_title_release","appid":"910001","title":"Example Game","release_year":2020}` |

All four keys are mandatory; a forbidden extra non-null value is invalid **even when it coincides with dossier metadata**. Query text, domain, another page, dossier descriptor or same-name edition cannot supply missing proof. The new prompt says this explicitly and the existing validator enforces each exact field mask, required-key set and dossier identity equality. There is no inference or repair path inside the validator.

Independent code review of synthetic positives: `observed_binding_fixture` generates one candidate per basis; PRAG-17 retains its mask after strict validation (no post-hoc rewriting). The helper describes its own synthetic source identity; it is **not an independent live-page attestation**. This is sufficient to regress serialization acceptance, but it does **not** prove the worker observed any real review or that a given third-party page displayed the claimed title/year. Those semantic facts remain the worker's obligation and cannot be certified by this offline fixture.

Independent negative coverage: PRAG-18 rejects the two historical invalid mask *shapes* (source-AppID incorrectly populated title/year; source-title-year incorrectly populated AppID). PRAG-19 tests wrong AppID, a different AppID/edition URL, wrong title, wrong release year, wrong all-three identity, absent required null key, query-only data missing a source binding, and one malformed source among correct ones. Values `970xxx` and `910001` are synthetic. PRAG-16 tests exact prompt examples/contract agreement and warnings. These tests verify strict rejection, not factual discovery of feedback.

**Historical evidence distinction:** the implementer reports nine rejected groups / 27 dossiers and 72 malformed original binding entries (57 AppID-basis and 15 title/year-basis). These are historical diagnostic examples, **not** 72 verified new real feedback items, not accepted dossiers and not replay authorization.

## L3 — group/marker/pin and recovery safety

- PRAG-20 builds a disposable 3-item manifest, three dossiers with distinct valid masks, validates them through **both** `validate_prepublication_artifact` and `validate_buffer_artifact`, and confirms bad source, wrong descriptor items/hash and stale dossier `worker_prompt_sha256` all fail closed. It verifies the test manifest remains unchanged and its group remains pending. These checks are **offline synthetic**, not a publication/ingest.
- `validate_prepublication_artifact` delegates to the same canonical `validate_buffer_artifact`; that validator compares immutable descriptor fields, ordered AppIDs and per-dossier strict bindings. A wrong dossier blocks the entire 3-game group, not just a single game.
- PRAG-20 does **not** itself create or authenticate a real GitHub nonce-only run-start marker; the **unchanged** `config/taste_steam_review_dossier_runtime_prompt.md`, `scripts/taste_steam_review_dossier_authority.py` and existing frozen-invocation rollover regression cover the separate single-parent marker/authority rule. A candidate may only refer to the durable marker; GitHub derives the immutable parent, and later main movement does not authorize rebind/relabel.
- Actual `main` worker index and first immutable descriptor at inspection still bind snapshot `d20d3109fc28b00f0658697a77abecf717678fd614cdbc9b13afc961554c8e69` to **old** `worker_prompt_sha256=719722e85584c32bf10f877cdd19465dfc74a40a0a0992fe1f5e02ae828ff18d`. Prompt content changes in PR #371, while `current_worker_contract_binding()` hashes full prompt UTF-8 bytes. Therefore old immutable groups cannot simply become compatible with the changed worker prompt.
- After a director-approved merge, a **new canonical GitHub preparation/repin** of current work and its exact binding is required **before** any separately authorized Dossier V1 semantic invocation. Do not edit or re-label the old index/descriptor, marker, quarantined candidate or prior group failure; do not interpret old transport as new acceptance. No actual post-merge prepared descriptor has been verified, since **the merge and preparation have not happened**.
- A late old-snapshot outcome may only be treated by the pre-existing frozen-authority/cache rules when genuinely compatible; it cannot directly advance a newer group's progress or override strict binding checks.

## Exact-source-head GitHub Actions evidence (actually executed, not assumed)

`fetch_commit_workflow_runs` for source HEAD `56f59ce92b6e529fbccf3d0327b277d6338f8157` returned three completed successful PR runs:
- [Validate buffered Steam review dossier runtime — run 41441094716](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41441094716), successful job `125262874838`. Fetched job steps and actual log: checkout of PR merge `60e9385ee7330ecc34681c62f26876ff10ad1c1b` **explicitly merges source HEAD `56f59ce9...` into base `32a4275...`**. Compilation succeeded; `ARCHITECTURE_OWNERSHIP_VALID`; **273/273 tests PASS across 24 Python scripts** (sum independently extracted from the log), including PRAG-01..20 **20/20**, prepublication **10/10**, strict recovery **21/21**, and frozen invocation rollover **8/8**.
- [Validate backlog dispositions — run 41441094501](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41441094501) — success.
- [Validate site task registry and page — run 41441094419](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41441094419) — success.

The earlier reported 273/273 test code HEAD was `32256ec...`; the final source HEAD was **also independently checked** above, so the review does not substitute the older result for current PR CI. **Execution boundary:** these are actual GitHub Actions tests plus static source/fixture analysis. This QA chat did not locally execute Python tests, a live web research run, marker creation, reprepare, recovery, ingestion, Scheduled Task or production.

## Nonblocking documentation precision

The implementer report cites `PITFALL-006` as support for immutable old-hash descriptor no-rebinding. The actual `KNOWN_WORKER_PITFALLS.md#PITFALL-006` is about stale exact revision-string assertions after binding revisions. **The no-rebind conclusion is correct**, but its authority comes instead from the web-evidence compatibility contract, the runtime prompt, strict binding comparison and frozen descriptor projection. This attribution mismatch does not weaken implementation code or CI. A separate documentation correction can be made later if needed; this read-only QA does not modify the implementation report.

## Safety and final disposition

**PASS_FOR_DIRECTOR_MERGE_REVIEW** for this bounded prompt-serialization change, with the explicit limitation that synthetic tests do not verify any real feedback, all old invalid submissions remain invalid, and fresh repin is still outstanding. No changes to PR #371, source, registry, Board, `CURRENT_TASK.md`, runtime, workflows, transport, cached/prod results, marker or scheduler; no self-merge.

**One narrow next action:** Director independently reviews and, if satisfied, merges **PR #371**; the director must subsequently use the existing GitHub-owned fresh-preparation/repin procedure before separately approving any real V1 semantic execution.
