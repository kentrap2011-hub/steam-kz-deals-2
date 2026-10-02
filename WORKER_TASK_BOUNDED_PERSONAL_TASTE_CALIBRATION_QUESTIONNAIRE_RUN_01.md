# WORKER TASK — bounded personal taste calibration questionnaire run 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `bounded-personal-taste-calibration-questionnaire-run-01`
Mode: `INTERACTIVE / BOUNDED CALIBRATION`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Canonical design:
`reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-design-01.md`

Durable completion report:
`reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-run-01.md`

## Goal

Run the already-approved bounded calibration questionnaire with the user.

This task asks exactly 14 primary questions, one at a time, using the canonical design report.

Do not redesign the questionnaire.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read this task fully.
4. Read the complete canonical design report:
   `reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-design-01.md`.
5. Read only the profile/rating context needed by that design.
6. Then begin the questionnaire immediately with primary question 1.

Do not start another task.

## Fixed total

The questionnaire contains exactly:

`14 primary questions`

At the beginning tell the user:

- `0 / 14`;
- there will be exactly 14 primary questions;
- clarifications do not increase the total;
- the run ends at `14 / 14`;
- estimated total time is about 18–25 minutes.

Do not add question 15.

Do not automatically start a second round.

## Primary-question counter

Before every primary question show:

`Вопрос X из 14`

After the user gives a sufficiently clear answer, mark that primary question complete and move to the next one.

If the answer is unclear, ask a clarification while keeping the same counter:

`Уточнение к вопросу X — всё ещё X / 14`

A clarification does not increment the counter.

## Clarification boundary

A clarification may only clarify the same uncertainty target as the current primary question.

It may:
- distinguish two interpretations of the user's answer;
- ask which already-mentioned reason mattered more;
- ask for a concrete example of the same claimed preference;
- clarify direction or magnitude of the same tradeoff.

It may NOT:
- introduce a new independent preference dimension;
- introduce a new game pair unrelated to the current target;
- collect a second independent preference fact;
- hide another primary question inside a clarification.

If a new independent preference signal would be useful, do not ask it unless it belongs to a later planned primary slot.

## Question content

Use the 14-question plan from the canonical design report.

The exact wording may adapt to earlier answers only within the allowed adaptive rules from that report.

If a future planned slot becomes fully redundant because an earlier answer already resolved it:
- keep the same total of 14;
- reassign that primary slot to the highest-value reserve target defined by the design report;
- do not add another slot.

Do not ask the user to remember facts they explicitly say they no longer remember.

Use the design's fallback for that same target.

## Interaction style

Ask only one primary question at a time.

Do not dump all 14 questions at once.

Keep questions concise and easy to answer.

Do not force essays.

If the user gives a long answer that clearly resolves the current target, accept it and move on.

If the user volunteers useful information relevant to later targets, record it, but do not silently count later questions as answered unless the canonical adaptive rule says that target is fully resolved. If it is fully resolved, reassign that later slot according to the design report.

## What to record

For each primary question retain:
- question_id;
- primary_index;
- exact user answer;
- clarification answers attached to the same primary question;
- direct preference fact(s);
- inferred preference(s);
- confidence;
- related games;
- temporal/franchise/social qualifiers;
- reusability scope;
- unresolved status if applicable.

Keep direct user statements separate from inference.

Do not invent memory or fill gaps the user did not answer.

## Completion

After question 14 is resolved or explicitly marked unresolved:

1. Show `14 / 14 завершено`.
2. Summarize:
   - strongest newly learned preference rules;
   - strongest deal-breakers;
   - strongest decisive positives;
   - contextual/franchise/history qualifiers;
   - unresolved items.
3. Write the durable completion report:
   `reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-run-01.md`.
4. The report must preserve the 14 primary-question records and clarification attachments.

## Profile mutation boundary

Do NOT modify the canonical Taste profile during the questionnaire.

Do NOT write inferred answers directly into production scoring/ranking.

At completion, recommend exactly one next bounded action:
- a separate profile-update/validation task that converts the completed questionnaire into a reviewed canonical profile delta.

This separation is required so questionnaire answers can be reviewed before they affect production scoring.

## Hard boundaries

Do NOT:
- exceed 14 primary questions;
- count clarifications as new primary questions;
- start a second questionnaire round;
- modify production scoring/ranking;
- modify Deep/Dossier contracts or state;
- run production Deep/Dossier workers;
- alter canonical profile during the run;
- publish site changes;
- create or modify Scheduled Tasks;
- start another task.

## Status

At completion use:
`questionnaire_complete_ready_for_profile_update`

If the user stops before completion:
`questionnaire_paused_at_X_of_14`

Do not claim completion before 14/14.
