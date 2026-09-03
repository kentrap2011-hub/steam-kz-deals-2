# WORKER TASK — EPIC GIVEAWAY SCHEMA RECON 01

Task ID: `epic-giveaway-schema-recon-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/epic-giveaway-schema-recon-01.md`

## User-visible incident

On 2026-09-03 the giveaway tab shows no confirmed offers and explicitly says completeness could not be verified.

Canonical current evidence:
- `data/production/giveaways/v1/current.json`
- `snapshot_status: incomplete`
- Steam source: `ok`, complete
- GOG source: `ok`, complete
- Epic source: `failed`, `complete: false`
- `error_code: SOURCE_SCHEMA_FAILURE`
- `error: Epic price.totalPrice schema changed`

This is a current production defect in Epic giveaway discovery/ingestion. It occurs **before** ITAD/IGDB cross-store identity enrichment.

## Goal

Determine the exact current Epic response shape that broke the strict parser, identify the smallest safe parser/schema-contract change, and prove whether current active Epic giveaways can again be read without weakening fail-closed behavior.

Diagnosis only. Do not implement the production fix in this task.

## Read first

Use only the smallest relevant current refs:
- `data/production/giveaways/v1/current.json`
- `scripts/giveaway_production.py`
- exact focused tests/fixtures for Epic giveaway parsing if present
- current giveaway source contract/config if directly referenced by the parser
- `DIRECTOR_TASK_BOARD.md` only for task context

Do not perform broad Git history or workflow archaeology.

## Required investigation

1. Identify the exact current Epic endpoint/request owned by the existing production path.
2. Obtain one bounded current live response/sample through the same safe source semantics used by production, if repository/network access permits.
3. Compare the current response shape to the parser assumptions that triggered `Epic price.totalPrice schema changed`.
4. Determine whether this is:
   - field relocation/renaming;
   - nullable/variant price object;
   - region/currency-specific variant;
   - promotion structure change;
   - another exact schema change.
5. Identify the smallest parser/schema guard update that restores exact current behavior without title guessing or broad schema permissiveness.
6. Confirm how active/free status should be derived under the current response shape.
7. Use a tiny current sample to determine whether at least one active Epic giveaway is currently discoverable, if the live response contains one.
8. Preserve strict failure on unknown/ambiguous variants.

## Critical boundaries

Do NOT:
- implement the fix;
- weaken the parser to accept arbitrary unknown structures;
- use title/fuzzy/manual mapping as source authority;
- start ITAD/IGDB identity work;
- redesign giveaway UI;
- ingest Epic pricing as a general deal source beyond what is strictly needed to establish zero-price giveaway state;
- process the catalog manually item-by-item;
- create another provider/scheduler/queue/writer.

## Required result

Report exactly:
1. current Epic response/schema difference that caused failure;
2. evidence classification: `proven | strongly_supported | hypothesis`;
3. whether current active Epic giveaways can be safely discovered again: `yes | no | cannot_determine`;
4. smallest implementation surface, maximum 3 files/components;
5. exact strictness/fail-closed rules the fix must preserve;
6. whether `IMPLEMENT` is ready now;
7. one recommended next step only.

Status exactly one:
- `complete`
- `blocked`
- `needs_user_evidence`

## Completion

Save:
`reviews/worker_reports/epic-giveaway-schema-recon-01.md`

Final answer must state exact report path, status and exact refs.