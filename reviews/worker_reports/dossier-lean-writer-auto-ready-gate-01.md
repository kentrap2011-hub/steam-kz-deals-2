# ЧАТ 1 — Lean writer auto-ready: scoped six recovery source, INACTIVE / future-trial gate pending

**Task:** `WORKER_TASK_DOSSIER_LEAN_WRITER_AUTO_READY_GATE_01.md`  
**Base:** `main@bf5a017392f5ffa491d10ef513d7232b5229d643`  
**PR:** [#484](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/484), `recon/dossier-lean-writer-auto-ready-auth-boundary-20261125`  
**Stage:** `PARTIAL_IMPLEMENTED_SOURCE_IN_DRAFT_INACTIVE`. **Not ready for merge or activation.** Exact-final-HEAD PR CI and independent L3 still mandatory.

## Original blocker resolved narrowly by the user's new explicit decision

The user expressly approved **one NEW automatic attempt for the historical six** after the previously failed first writer run. This approval is stored in `config/dossier_lean_writer_auto_ready_v1.json` as a separate versioned scoped recovery permission, bound to original `dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4`, frozen sandbox SHA `d1b9a9e78dcde879a03370682ade4969763fd9d1`, marker `b267882dd3d056a1fc18d6a3fb75380ac38bd9cd`, original owner source request and **failed owner first attempt #45540222575**. This is **not** retroactive reuse of the original grant and **not** authorization for a second try after the next failure.

Previous real run: `workflow_dispatch`, run_attempt=1, completed/failure on main `147be762d217dc1e7dc53a6fbd896f323f6af08c`, actor and triggering actor `kentrap2011-hub`. Real job failed at legacy cohort preflight without store/receipt commit; PR #482 fixed routing on main `7e0d575...`. Original frozen sandbox remains at 0/6 accepted.

## Current source implementation (only historical six are mapped)

- `config/dossier_lean_writer_auto_ready_v1.json`: versioned exact owner recovery and future-grant requirements; `activation_enabled=false` and explicit separate owner activation/L3 review gates. Canonical/production/Deep and generic automatic-writer flags remain false.
- `.github/workflows/dossier-lean-writer-ready-signal.yml`: read-only sandbox terminal-receipt push hint, without secrets/write permission. Existing frozen six predates this workflow and instead has **one bounded catch-up on a separately approved main activation-policy push**.
- `.github/workflows/dossier-lean-writer-auto-ready.yml`: main-owned `workflow_run` consumer / bounded main activation catch-up, inside the **existing shared** `taste-steam-review-dossier-canonical-writer` concurrency group. No schedule, workflow_dispatch form, semantic worker or independent canonical writer.
- `scripts/dossier_lean_writer_auto_ready.py`: trust boundary for exact main GitHub workflow/repo/ref, original completed source issuer, previous real failed owner run, original frozen six Git SHA pairs and typed receipts, all six actual Assembly files / Lean TTL, original year, title, edition, source safety. Reads all six before consuming new attempt. Fail-closed missing/partial/collision/stale HEAD.
- One **create-only atomic Git control ref** `refs/heads/dossier-lean-auto-attempts/<exact-32hex>` is a durable one-shot claim: once it exists, later wakeups must be suppressed regardless of success or failure. Claim is distinct from frozen sandbox; creation is one nonforce push with readback and no retry. After claim the existing `taste_steam_review_dossier_buffered.py::_drain_notes_v2_individual` owns the full writer. Exact 12 files are checked by existing `dossier_notes_v2_isolated_lean_readback.py` staged, committed and after exactly one nonforce sandbox push.
- Original strict manual actor/first-attempt path is preserved; a **separate** automatic GitHub workflow + source event + exact remote claim proof is required for auto. Original18/V1/manual/canonical/Deep/production are not opted in or disabled.
- Both auto event modes remain **dormant** while `activation_enabled=false`. The source PR merge cannot activate writer.

## Tests and evidence

PR-only test paths:
- `scripts/test_dossier_lean_writer_auto_ready.py`: versioned owner permission and previous failure, source workflow/repo/ref/run verification, forged signal/event/activation, exact six readiness and original-year rejection, repeat-claim disposition. The actual GitHub API responses are mocked; it does **not** authenticate a live Actions actor.
- Extended `scripts/test_dossier_notes_v2_isolated_lean_acceptance.py`: synthetic automatic event identity enters **real existing shared writer** and verifies six generated Lean cache documents plus six receipts through the real isolated staged/committed readback on disposable Git. Only automatic event/issuer GitHub identity is mocked.
- `.github/workflows/validate-dossier-research-notes-v2.yml`: new test routed together with existing strict/legacy tests.

**Test result:** check GitHub CI on final PR HEAD; no claim of passing CI until observed. These are synthetic Git fixtures, not an actual source event/owner approval, remote branch write or production trial.

## Critical remaining blockers / independent L3

1. **Future owner-issued Lean batches are not yet supported.** Existing generic owner request/issuer has `allow_automatic_writer=false` and contains no independently frozen original release-year per item. The new runner deliberately accepts **only** the existing exact-six grant. A fresh versioned per-trial opt-in issued by a real, first-attempt existing owner GitHub Action, with immutable original-year/edition and typed receipt authority, must be implemented/tested before the reusable future path is complete. Do not mistake `sandbox_writer_authorized=true` (manual grant) for automatic permission or enable all generic trials by default.
2. Independently review exact final source HEAD for L3 event/write permissions, worktree source pinning, authenticity of source signals/claim ref and attempted-write irreversibility, potential workflow_run event-provider edge cases, correct staged-and-pushed transaction handling and remote delete/replay threat.
3. End-to-end actual live event→GitHub Actions bot actor→one-use claim→writer push is **not verified**; no workflow has been launched. No actual original six accepted, no production/Deep effects.
4. Do not merge/activate this source PR as feature-complete. Later Director approval of final source and a **separate explicit activation authorization** are required; first owner-approved activation changes only `activation_enabled` on reviewed main and requires verified source revision. A merge with this flag false cannot run writer.

## Source files changed

`config/dossier_lean_writer_auto_ready_v1.json`; `scripts/dossier_lean_writer_auto_ready.py`; `scripts/test_dossier_lean_writer_auto_ready.py`; `scripts/taste_steam_review_dossier_buffered.py`; `scripts/test_dossier_notes_v2_isolated_lean_acceptance.py`; `.github/workflows/dossier-lean-writer-ready-signal.yml`; `.github/workflows/dossier-lean-writer-auto-ready.yml`; `.github/workflows/validate-dossier-research-notes-v2.yml`; `CURRENT_TASK.md`, this report, `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md` (when updated). No live sandbox, cache, source result, execution or existing owner grant mutated.

**Blocked task acceptance:** original six path is source-implemented but INACTIVE; future per-trial path and independent L3/CI/real activation not complete. No automatic attempts permitted.
