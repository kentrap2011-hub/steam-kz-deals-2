# WORKER TASK — PROGRESSIVE FAST/DEEP COACTIVATION STALE-GUARD AUDIT 01

## Assignment
- Worker slot: **NEW physical ЧАТ 2**
- Mode: **READ-ONLY / RECON**
- Repository: `kentrap2011-hub/steam-kz-deals-2`
- Source of truth: `main`
- Report: `reviews/worker_reports/progressive-fast-deep-coactivation-stale-guard-audit-01.md`

## Goal
Before repairing the confirmed PASS 1 ingest defect, audit the current production control plane for **all analogous stale assumptions left from the pre-Deep architecture**.

Known confirmed seed defect:
- current valid architecture allows `pass1_active=true` and `pass2_active=true` simultaneously;
- `scripts/ingest_progressive_pass1.py` still rejects that state because it requires `pass2_active=false`;
- real PASS 1 ingest run `35812546365` therefore failed on the already-created Friends vs Friends result, leaving canonical PASS 1 at 100 attempted / 460 remaining.

This task must determine whether the same class of stale mutual-exclusion / pre-activation assumption exists anywhere else before an implementation task is issued.

## START
1. Read current `CHAT_PROTOCOL.md` and execute its START gate.
2. Read this task fully.
3. Read current Progressive architecture/contracts on `main`, especially:
   - `config/progressive_personalization_contract.json`
   - `config/progressive_pass1_contract.json`
   - `config/progressive_pass2_contract.json`
   - `config/execution_ownership_contract.json`
4. Read only the runtime/workflow/test files needed for this audit.

## Required audit
Search the current repository for stale assumptions related to the old Fast-only / pre-Deep model, including but not limited to:

- `pass1_active` / `pass2_active` mutual-exclusion checks;
- requirements that PASS 2 must be inactive for PASS 1 ingest/build/validation;
- requirements that PASS 1 must finish or fail before Deep can proceed;
- requirements that Deep needs prior Fast / Fast incomplete;
- old recovery-only PASS 2 activation predicates;
- old activation guards that reject the accepted production-active Deep state;
- tests that model `pass1_active=true, pass2_active=true` differently from production runtime;
- workflow or recompute paths that can fail once both Fast and Deep are active;
- stale phase/state-schema assumptions introduced before `FAST-DOSSIER-DEEP-V1`.

At minimum inspect the current production paths for:
- PASS 1 build / ingest / validation;
- PASS 2 build / ingest / validation / recovery authorization;
- shared canonical-writer workflows touching Progressive state;
- pre-AI generation/recompute;
- visual/projection generation only where it validates or gates activation state.

For every finding classify:
- exact file and controlling condition;
- whether it is currently reachable in production;
- whether it can block Fast, Deep, Dossier, shared writer, or visual rebuild;
- whether it is the same root-cause class as the confirmed PASS 1 defect;
- smallest implementation scope needed.

Also explicitly report **negative evidence**: which relevant production paths were inspected and found compatible with simultaneous Fast+Deep activation.

## Known PASS 1 incident evidence
Verify, do not rewrite:
- Friends vs Friends appid `1785150`;
- work_id `4a85ac1f78ca5a8812a59631c715058f36032959b997b8be2504018c1100eed0`;
- create-only result commit `63ceb92cc4a3628b987a5ee537cb22ca30c35be8`;
- failed ingest run `35812546365`;
- exact failure `Progressive PASS 1 work activation flags are invalid`;
- current canonical PASS 1 projection was 100 attempted / 460 remaining at incident observation.

Do not process or replace this result in this audit.

## Hard prohibitions
Read-only except the report.

Do not:
- fix `ingest_progressive_pass1.py`;
- ingest/replay/delete/overwrite the Friends vs Friends artifact;
- dispatch or rerun workflows;
- change PASS 1 / PASS 2 / Dossier state, work, cache, inbox or contracts;
- enable/disable/edit any Scheduled Task;
- run production semantic work;
- alter site/visual output;
- touch the separate Dossier Scheduled Task self-disable diagnosis.

## Validation gates
- **AUD-01** confirmed PASS 1 defect independently verified.
- **AUD-02** all current production consumers of PASS1/PASS2 activation flags located or bounded.
- **AUD-03** all stale mutual-exclusion / pre-Deep assumptions identified.
- **AUD-04** each finding classified by reachability and impact.
- **AUD-05** current-compatible paths explicitly listed as negative evidence.
- **AUD-06** no production mutation/workflow dispatch/Scheduled Task mutation occurred.
- **AUD-07** implementation fix set is bounded and ordered, but not applied.
- **AUD-08** report committed to `main` and reread exactly from `main`.

## Report requirements
Create:
`reviews/worker_reports/progressive-fast-deep-coactivation-stale-guard-audit-01.md`

Use a compact finding table:
`ID | path | stale assumption | production reachability | impact | fix scope`

Final status:
- `complete_no_additional_analogues`
- `complete_additional_analogues_found`
- `needs_fix`
- `blocked`

Do not start implementation after the audit.
