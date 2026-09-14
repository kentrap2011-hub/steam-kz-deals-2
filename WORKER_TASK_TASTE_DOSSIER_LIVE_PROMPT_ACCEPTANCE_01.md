# WORKER TASK — Taste Dossier Live Prompt Acceptance 01

Task ID: `taste-dossier-live-prompt-acceptance-01`
Mode: `ACCEPTANCE`

## Goal
Validate the manually updated live prompt of the existing ChatGPT Scheduled Task `Taste Steam Review Dossier` by observing one controlled production continuation of the current prepared snapshot.

## Preconditions
- User has manually replaced only the Scheduled Task prompt/instructions with the approved replacement from `reviews/worker_reports/taste-dossier-live-prompt-alignment-01.md`.
- Title, schedule/cadence, checkpoint size, production limits, and Taste Semantic Producer settings were not intentionally changed.
- Worker access to live Scheduled Task UI is unreliable. Do not spend time trying to read/edit the Scheduled Task through automation/tool surfaces.

## Required reads
Perform the `CHAT_PROTOCOL.md` START gate, then read:
- `CHAT_CONTEXT.md`
- this task completely
- `reviews/worker_reports/taste-dossier-run-stop-recon-01.md`
- `reviews/worker_reports/taste-dossier-live-prompt-alignment-01.md`
- `config/taste_steam_review_dossier_worker_prompt.md`
- only the minimum current dossier state/contract needed for acceptance.

## Acceptance boundary
1. Do not edit the Scheduled Task or Taste Semantic Producer.
2. Do not change schedule, limits, queue/state ownership, snapshot scope, checkpoint size, or canonical contracts.
3. The user will perform any required `Run now` action manually in the ChatGPT UI.
4. Before asking for `Run now`, determine the current durable dossier state from GitHub and record snapshot id, completed count, remaining count, current checkpoint count, and `full_backlog_complete`.
5. Then stop and ask the user to run the existing `Taste Steam Review Dossier` once manually, only if the UI shows it is not already running.
6. After the user reports that the run has finished, continue acceptance by reading durable GitHub state and relevant production evidence.

## Acceptance criteria
Pass if the controlled run demonstrates all of the following:
- it resumes the same prepared snapshot from durable state;
- it persists at least one additional valid checkpoint;
- checkpoint size remains a durability boundary, not a quota;
- if execution continues across multiple checkpoints, each accepted checkpoint advances the same snapshot correctly;
- if the run stops before `full_backlog_complete=true`, the observed result must expose a concrete blocker/error/runtime interruption or otherwise provide materially better evidence than the prior arbitrary 30-stop; do not invent a cause;
- no duplicate/reordered scope and no unrelated Taste Semantic Producer changes.

Do not require the entire remaining backlog to finish in one invocation if a real platform/tool/runtime interruption is explicitly exposed. The key acceptance question is whether the new prompt enforces canonical same-snapshot continuation rather than self-selecting an arbitrary checkpoint count.

## Durable report
After the controlled run is complete, write to main:
`reviews/worker_reports/taste-dossier-live-prompt-acceptance-01.md`

Allowed final statuses:
- `accepted`
- `accepted_with_explicit_runtime_stop`
- `failed_premature_stop_without_evidence`
- `blocked`

Report exact before/after counts, snapshot id, checkpoint progression, run/action refs when available, stop reason evidence, and whether the prompt alignment is accepted.

Stop after report.