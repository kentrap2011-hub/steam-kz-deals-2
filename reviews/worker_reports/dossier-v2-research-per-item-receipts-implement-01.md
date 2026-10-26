# ЧАТ 3 — Dossier Notes V2 per-item Research receipts

**Task:** `dossier-v2-research-per-item-receipts-implement-01`  
**Scope:** inactive offline adapter and disposable Git fixtures only  
**Base:** `main` at `09cc60b91965cb6dd054c26b69ca9792da604274`  
**Adjacent:** draft PR #266, exact reviewed head `1d46b84aff35feee0aca68fc8ad9f3154a330036` — still unmerged at task start; all seven protected paths untouched.  
**Status:** `READY_FOR_INDEPENDENT_QA` for the *inactive offline proposal only*, with execution/evidence limitations below. Never production-ready.

## Reused canonical control-plane primitives

- `scripts/dossier_research_notes_v2.py`: `frozen_assignment`, exact original-18/pinned-title/assignment binding, strict Notes schema/source/privacy checks, `prepare_research`, `classify_research`, `item_receipt_blueprint`, and immutable first-parent/path checks.
- `scripts/dossier_two_stage_staging.py`: `require_only_new`, first-parent and single-parent proof, Git file/blob comparisons and `blob_for`. No second writer service was introduced.
- Existing V1 single-add research transport and GitHub-owned staged receipt conventions are preserved; V1 source, workflows and production writer are not modified.

## Added offline-only component

`scripts/dossier_notes_v2_per_item_receipts.py`

- `issuer_structure`: matches future V2 issuer's direct-child one-add authorization path to a distinct Notes V2 marker, its actual Git parent/nonce, exact original-18 frozen manifest, original pins, Git actor/run fields and the original, immutable scoped issuer human-grant blob. Historic V1 SHA cannot be rebound. **This is structural local Git evidence, not authenticated user consent or GitHub Actions run confirmation.**
- `prepare_candidate`: one strictly checked V2 payload, create-only path, immutable assignment/trial/marker/manifest and source evidence; read-only proposal, no commit or publication.
- `inspect_candidate`: detects missing/invalid/unsafe/stale/wrong Git transport, proves exact original item Git blob and ancestry when valid, never upgrades it to semantic/canonical acceptance.
- `prepare_receipt`: fixed one-item-one-phase create-only receipt path, deterministic bytes and Git blob/raw hashes, original candidate and issuer binding, separate proposed technical disposition. Rejected and missing candidates remain typed as refusal/unknown attempt.
- `inspect_receipt_commit`: locally verifies one-add receipt commit, exact parent/candidate ancestry, immutable bytes and no rewrite-then-restore. Returns `github_receipt_confirmed=false` even when local Git proof succeeds.

The existing receipt schema requires `semantic_attempt_state=unknown`, `staged_only=true` and `canonical_acceptance=false`. Transport submission, local technical correctness, GitHub remote receipt, final semantic quality and canonical Dossier ingest remain **separate**. No code path runs Git commit, Git push, Actions, external Research, Assembly, recovery or production.

## Adversarial tests authored

`scripts/test_dossier_notes_v2_per_item_receipts.py`: disposable Git fixture using existing Notes V2 original-18 data and existing test Git helpers. Covers: good one-item candidate and immutable local receipt; duplicate item/receipt; candidate overwrite; receipt rewrite-and-restore; wrong group/AppID; forged issuer nonce/marker/source/grant; introduction before proper authorization; malformed JSON rejection not acceptance; missing candidate unknown attempt; illegal double-add candidate; two competing local writer branches both remaining **remote-unconfirmed**.

**Execution limitation:** the connected GitHub API provides source and repository mutations but no repository checkout/local Python execution here, and the separate container cannot clone GitHub (DNS unavailable). Accordingly no local test pass is claimed. The authored suite must be run by the independent reviewer with `python scripts/test_dossier_notes_v2_per_item_receipts.py -v` (jsonschema installed) before acceptance. Existing automatic GitHub checks should be reviewed against the final PR HEAD; the existing Notes V2 workflow's explicit `paths` filter does not include these new files, so a green unrelated check is not substitute evidence. No new/modified CI checks or workflow dispatch are allowed.

## Exact authority still blocked

1. PR #266 is pending independent QA/merge; the real V2 issuer is disabled by contract and cannot be assumed issued.
2. No separate actual user authorization for semantic Research, no authenticated GitHub Actions issuer run or completed remote GitHub receipt exists.
3. Real GitHub writer integration, atomic remote first-writer compare-and-swap, collision checking against the authoritative remote branch and re-fetch confirmation are **not implemented/authorized**. Two local writer branches are a deliberately unconfirmed race; they must never count as receipt acceptance.
4. The eventual semantic quality decision, strict Dossier final validation and existing three-game canonical ingest remain separately gated. No production/readiness claim.

**Reviewer:** verify this exact PR HEAD, run the new disposable tests and old V2/V1 tests, scrutinize issuer grant equivalence and remote-authentication fail-closed boundary. **Do not merge or dispatch.**
