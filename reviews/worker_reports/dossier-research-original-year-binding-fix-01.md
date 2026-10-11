# Worker report — Dossier Research original-work year binding fix 01

- **Physical worker:** НОВЫЙ ЧАТ — ЧАТ 1
- **Task:** `WORKER_TASK_DOSSIER_RESEARCH_ORIGINAL_YEAR_BINDING_FIX_01.md`
- **Repository/base:** `kentrap2011-hub/steam-kz-deals-2` / `main`, base SHA `377f3db391c08e422c7c85f722e10234357f6063`
- **Branch:** `fix/dossier-research-original-year-binding-01`
- **PR:** #187 — https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/187 — **open; worker must not merge**.
- **Mode:** inactive two-stage P1/P2 offline-only correction. No semantic analysis or production run.

## Confirmed finding and smallest ownership-safe correction

Merged PR #185's `test_known_gap_conflicting_source_original_year_must_be_rejected` was previously an **XFAIL**: `identity.original_work_release_year=2020` alongside explicit `sources[*].exact_product_binding.original_work_release_year=2021` wrongly passed P1 and was classified as `accepted_structural_evidence` by P2 `receive_research`. This was an unresolved defect, not a passing security property.

The inactive P1 `validate_research` now compares **every explicit source exact-product original-work year** to the Research identity's original-work year, independent of source type/order. A contradiction is rejected with the offending source ref and both years, and an explicit source original-work year cannot be paired with an unknown Research original-work year. A `title_and_work_year` binding cannot omit the year on which its exact-product identification is based. An explicit `appid` identity corroborator cannot contradict the frozen assignment AppID. The check does **not** use `source.publication_date` as an original release date, never fills null years, and does not rewrite evidence or compare port/storefront release dates with original-work dates.

All pre-existing exact AppID/title source binding, source provenance, privacy, schema, literal unknowns, and the strict downstream V2 group validator remain unchanged.

## Changed files (worker-owned only)

1. `scripts/dossier_two_stage_contract_guard.py`: fail-closed original-work-year invariant in P1 Research validator, useful source-local errors.
2. `scripts/test_dossier_two_stage_contract_schemas.py`: five P1 fixture tests covering version/port dates and positive/negative binding matrix.
3. `scripts/test_dossier_two_stage_eventual_chain_qa.py`: removed `@unittest.expectedFailure`; the former known-gap regression now asserts **P2 rejection** (`rejected_invalid` / `invalid_binding`), item-local chain quarantine, no canonical acceptance/Deep readiness and independent acceptance/inspection for the two unaffected siblings.
4. This report.

No files owned by ЧАТ 2's new GitHub final acceptance integration task, workflows, integration writer/adapter, Director registry, production paths or scheduled tasks were edited.

## Isolated fixture acceptance matrix

| Scenario | Required/observed offline result |
| --- | --- |
| Resolved original 2020, metadata + feedback both bind 2020 | P1 PASS |
| Explicit source year 2021 vs original 2020 in either independently copied source | P1 REJECT with source ref and both years |
| Two different exact sources: one says 2020, other says 2019 | P1 REJECT, no conflicting corroborator accepted |
| Original 2020, Steam/port evidence published 2024, `platform`/`version` corroborators | P1 PASS; later storefront date not confused with original year |
| Unresolved identity, no original year anywhere and incomplete audit | P1 PASS as honestly incomplete; cannot become accepted Research in P2 |
| Unresolved original identity year with an explicit source original year | P1 REJECT |
| `resolved` identity missing/null original work year | P1 REJECT (schema/semantic guard) |
| `appid` source binding with null original year and other valid identity evidence | P1 PASS without filling unknown |
| `title_and_work_year` binding with null year | P1 REJECT; matching year PASS |
| AppID identity corroborator contradicts frozen assignment | P1 REJECT; platform/version corroborator PASS |
| Former PR #185 contradiction through real frozen Git transport into P2 `receive_research` | P2 `rejected_invalid`, receipt reason `invalid_binding`; no accepted Research receipt |
| Contradictory A plus valid B/C in three-game pending chain | A locally quarantined, B/C independently accepted as Research and inspected; no item can claim canonical/Deep-ready from P1/P2 |
| Existing strict V2 item/group QA and one-stage factual-date / Deep release-year regressions | Existing offline suites PASS |

No real game evidence or production data was used. Git repos in chain tests are disposable.

## CI evidence

Verified on implementation head `afc3b4b30746b783ed1251e7fb7b60bc06549ecb`:

- **SUCCESS** — GitHub Actions run **38114235820**, `Validate inactive Dossier two-stage interfaces`: P1 schema/contract; P2 frozen Git Research→Assembly; async buffer; one-stage factual date; Dossier↔Deep original-year compatibility. Every named step succeeded.
- **SUCCESS** — GitHub Actions run **38114235831**, `Validate inactive Dossier GitHub eventual chain acceptance QA`: updated formerly-XFAIL negative Research/Git chain fixture, independent chain and strict group QA, async buffer, P1/P2 and one-stage regressions. Every named step succeeded.

These runs validate the implementation commits; the documentation-only report commit must also pass any automatically rerun PR checks before merge review.

## Activation guard and remaining limits

- `config/dossier_two_stage_interfaces_contract.json`: `active=false`, `authoritative=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`. P2 staging and async buffer remain inactive; one-stage Dossier stays production authority.
- This fix validates **declared fields**, not historical truth of a real external source. Null source years without explicit contradictory claims remain representable; unresolved originals remain non-acceptance.
- Item-local Research/Assembly chain checks cannot themselves grant strict canonical three-game Dossier acceptance or Deep eligibility. ЧАТ 2 independently owns the inactive final group-writer integration; no merge or activation is implied by this worker's green tests.
- No live semantic evidence parity test, production deployment/authorization, Scheduled Task change, Fast/Deep/ranking/UI/translation/Steam edit, or real cache/ingest write.
- Shared `CURRENT_TASK.md` and Director registry left unchanged intentionally to avoid competing concurrent writes with ЧАТ 2.
