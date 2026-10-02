# WORKER TASK — personal taste game-guess diagnostic 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `personal-taste-game-guess-diagnostic-01`
Mode: `INTERACTIVE / DIAGNOSTIC`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2`

Durable completion report:
`reviews/worker_reports/personal-taste-game-guess-diagnostic-01.md`

## Goal

Run an interactive diagnostic with the user.

The user has one currently very interesting game offer in mind and wants to see on which guess the system can identify the exact game from the user's taste and clues.

This is a diagnostic of combined taste understanding and deal-value judgment. Current price/discount may be used as evidence, but this must not become a mechanical catalog-enumeration exercise.

There is NO maximum number of guesses.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read this task fully.
4. Read current canonical Taste/profile evidence needed for this diagnostic.
5. Read the completed calibration questionnaire report:
   `reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-run-01.md`.
6. Treat that questionnaire report as diagnostic context only; it is not yet canonical profile state.
7. Then begin the game-guess diagnostic immediately.

Do not start another task.

## No attempt limit

There is no fixed maximum.

Continue until:
- the correct game is guessed; or
- the user explicitly stops the diagnostic.

Never invent a stopping threshold.

## What counts as an attempt

An attempt is counted ONLY when the worker explicitly names one concrete game as its guess.

Examples:
- "Попытка 1: Sifu" -> counts as attempt 1.
- "Это экшен?" -> clarification, does not count.
- "Похоже на игру с сильной боевой системой" -> analysis, does not count.

Maintain a visible counter:
- `Попытка 1`
- `Попытка 2`
- etc.

Do not reset the counter.

## Anti-cheating boundary

User-approved amendment during the live diagnostic:
- current price and discount are part of the hypothesis and may be checked for a small number of semantically plausible candidate games;
- price/value may influence which game is guessed next and how strongly the offer fits the user's buying interest;
- the worker may use current public commercial metadata for those already-semantic candidate hypotheses.

Before the correct guess, still do NOT:
- mechanically enumerate or filter the current Steam/deals candidate list to solve the title;
- perform a broad catalog search whose primary key is price/discount;
- ask the user for AppID, store URL, title fragments, publisher/developer, or other direct identifiers;
- use repository deal rows as a candidate-enumeration list.

The worker MAY use:
- canonical taste/profile evidence;
- the completed 14-question calibration report as noncanonical diagnostic context;
- general game knowledge already available to the model;
- clues voluntarily provided by the user;
- answers to clarifying questions;
- current price/discount/value evidence for a bounded set of semantically plausible candidate games.

The purpose is to test combined semantic taste understanding + deal-value judgment, without reducing the exercise to catalog matching.

## Clarifications

Clarifying questions are allowed and do not count as guesses.

Prefer questions that discriminate taste hypotheses, such as:
- what aspect of the offer is most exciting;
- whether the hook is gameplay, structure, franchise context, novelty, price/value, co-op/social context, etc.;
- whether the game resembles a liked game for the same underlying reason or only superficially;
- whether a known negative is acceptable because of a stronger positive.

Do not ask direct-identification questions whose only purpose is narrowing the title:
- release year;
- exact genre taxonomy;
- exact developer/publisher;
- first letter;
- platform-only identifiers;
- AppID/store URL/title fragments.

Price/value questions are allowed when they test purchase-value reasoning rather than acting as a disguised direct identifier.

A clarification should improve the taste hypothesis, not mechanically solve a twenty-questions puzzle.

## Guess protocol

For each explicit guess:

1. Show:
   `Попытка N: <game title>`
2. Give a concise reason tied to the user's taste/profile/clues.
3. Ask only whether it is correct.
4. If wrong, use the user's response/clue to revise the hypothesis.

Do not produce a batch list of candidate games. One concrete game per attempt.

## Diagnostic record

Track each attempt:
- attempt_number;
- guessed_game;
- evidence/clues available before the guess;
- taste hypothesis used;
- why the game was selected;
- user result: correct / incorrect;
- what changed after an incorrect guess.

Track clarifications separately so they do not inflate attempt count.

## Completion

When the user confirms the correct game:

1. State the exact successful attempt number.
2. Explain which clues/profile facts were actually decisive.
3. Distinguish:
   - clues that genuinely helped;
   - clues that misled;
   - profile assumptions that were correct;
   - profile assumptions that were wrong or missing.
4. Assess whether the diagnostic reveals a concrete profile/scoring gap.
5. Write:
   `reviews/worker_reports/personal-taste-game-guess-diagnostic-01.md`

Do not modify the canonical profile automatically.

## If the user stops without a correct guess

Write the report with:
- total attempts made;
- last hypothesis;
- strongest unresolved ambiguity;
- status `diagnostic_stopped_without_correct_guess`.

## Status

On success:
`diagnostic_complete_correct_guess_at_attempt_N`

## Hard boundaries

Do NOT:
- impose an attempt limit;
- mechanically enumerate/filter the current deal-list/catalog to identify the title;
- use broad web/catalog search keyed mainly by price/discount to identify the offer;
- ask for direct identifiers such as AppID/store URL/title fragments;
- modify canonical Taste profile;
- modify scoring/ranking;
- run Deep/Dossier;
- modify production state;
- create or modify Scheduled Tasks;
- start another task.
