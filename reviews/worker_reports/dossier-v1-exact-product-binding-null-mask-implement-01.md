# Dossier V1 exact_product_binding basis-specific null-mask clarification

- **Task:** `dossier-v1-exact-product-binding-null-mask-implement-01`
- **Role:** bounded developer implementation; no semantic worker or production invocation
- **Base main SHA:** `32a427503a459c66173eb60de938c78cdefd08fc`
- **Diagnosis authority:** PR #367 report at `e787c5df924f2255ad31e56b5472e95b00c12574`
- **Allowed source writes:** worker prompt and one existing pragmatic evidence regression file; this report only
- **Status:** implementation ready for independent L2/L3 delta QA; draft only; no merge

## Root cause / unchanged truth

All nine original V1 candidate groups (27 dossiers) failed canonical ingest. Of 72 inspected exact product source bindings, 57 `source_appid` sources populated forbidden title/year fields and 15 `source_title_release` sources populated forbidden AppID. All are structurally invalid under existing `config/taste_steam_review_dossier_web_evidence_contract.json` and `scripts/taste_steam_review_dossier_strict.py`. Source value coincidence is not proof of a valid field mask, and fixing the mask alone does not certify that every underlying feedback item was actually observed.

The strict validator, schema, evidence contract, group identity, ownership, immutable quarantine and canonical persistence remain **unchanged**. No previous rejected candidate is repaired, re-labelled or replayed.

## Bounded implementation

- `config/taste_steam_review_dossier_worker_prompt.md`: immediately after the allowed basis labels, explicitly mandate all four keys including nulls, three mutually exclusive source-proven masks, three exact short JSON examples, ingest rejection for extra non-null fields, and prohibition on query/dossier-derived metadata or edition/DLC mixing.
- `scripts/test_taste_dossier_pragmatic_evidence_model.py`: append PRAG-16..20, asserting prompt examples/contract parity, strict positives for all three basis types, historical malformed mask patterns with **synthetic** AppIDs, wrong AppID/title/year/edition, missing null key, query-only, one bad source among correct sources, and 3-dossier frozen-descriptor parity with strict/prepublication validation. Test fixtures are not real web attestations. The validators remain the authority.

## Architecture and pin compatibility

1. GitHub controls plan, scope, frozen binding, validation, retry/progress, acceptance and persistence. The existing Dossier semantic worker owns truthful source observation and metadata serialization.
2. Existing `config/execution_ownership_contract.json`, `config/taste_steam_review_dossier_web_evidence_contract.json` and the worker prompt authorize this narrow clarification.
3. No interactive/scheduled worker gains control-plane authority.
4. No new scheduler, quota, queue, retry, marker, writer, or recurring stage is added.

Changing worker prompt content changes the content-complete `worker_prompt_sha256` in `web_evidence_contract_binding`. Per PITFALL-006, frozen descriptors with the old hash remain immutable and **must not** be rebound or reused. After reviewed merge, compatible fresh work must be produced/re-pinned by the **existing GitHub canonical preparation route** before any separately user-authorized V1 semantic run. The current task does not authorize that run or a forced refresh.

## Test evidence

- GitHub Actions `Validate buffered Steam review dossier runtime` on tested code HEAD `32256ec9767b9cdf11255e12833f9a4b6b686cbf`: **SUCCESS** ([run #41440855037](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41440855037); job `125262048143`). Actual GitHub-run Python regressions: **273/273 PASS** across 24 scripts, including PRAG-01..20 (20/20), prepublication parity (10/10), strict recovery (21/21), and frozen invocation rollover (8/8). Python compilation and ownership validation also passed.
- Initial [run #41440714154](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41440714154) failed because a **new test** incorrectly expected a content pin on the group transport descriptor; the real strict check correctly uses the **dossier** binding. The test was corrected in `32256ec` without changing runtime/validator code.
- Local Python execution in this isolated conversation environment was not possible (GitHub checkout network unavailable). Actual offline Python tests executed in GitHub Actions, not locally.
- This report update adds no source code. The **exact final PR HEAD** is verified via its own subsequent CI; final SHA/run evidence should be appended to the PR conversation rather than guessed inside a report commit that changes the HEAD.
- Other executed checks on the code HEAD: site-task registry [run #41440854888](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41440854888) SUCCESS and backlog dispositions [run #41440854960](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/41440854960) SUCCESS.
- Generic test AppIDs are synthetic, not fixed to current production work; zero canonical accepted original groups and all immutable quarantined artifacts remain unchanged.

## Independent L2/L3 delta QA required

- **L2, generation correctness (moderate recurrence risk):** independent reviewer checks one NEW synthetic generated source binding against both the prompt mask and independently presented source-observed identity; no fields copied across sources. Run PRAG-16..20 plus existing strict and prepublication regressions.
- **L3, pin/recovery safety (high-impact mismatch risk):** reviewer verifies exact new GitHub-prepared `web_evidence_contract_binding` and marker-parent/descriptor parity after an eventual approved merge; old immutable candidates/quarantine and previous pins remain unchanged; validator rejects stale/wrong basis/edition/descriptor.
- **Rollback:** revert only this prompt clarification and its matching regression additions through reviewed Git history if QA fails, preserving immutable rejected bytes, strict GitHub validation, audit and historical pin identity. A rollback also changes the content hash and requires the standard GitHub compatibility/reprepare route; never manually force an old descriptor into a new binding.

**Worker verdict:** `READY_FOR_INDEPENDENT_DELTA_QA` after successful exact final HEAD CI. Independent L2/L3 review remains required; no worker merge or semantic execution.
