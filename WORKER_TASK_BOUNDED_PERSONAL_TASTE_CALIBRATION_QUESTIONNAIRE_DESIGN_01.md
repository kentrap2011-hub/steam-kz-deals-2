# WORKER TASK — bounded personal taste calibration questionnaire design 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

Task ID: `bounded-personal-taste-calibration-questionnaire-design-01`
Mode: `READ-ONLY / RESEARCH / DESIGN`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-design-01.md`

## Goal

Design a finite calibration questionnaire that extracts the maximum useful new preference information from the user's existing game history without requiring new games, new playthroughs, or an open-ended interview.

The questionnaire must have a fixed, known end before it starts.

The worker must determine the number of **primary questions** from the current evidence. Do not assume 40. Choose and justify the number.

## User requirement — hard boundary

Before the questionnaire begins, the user must be told an exact total:

`0 / N primary questions`

That total is frozen for the questionnaire.

The system must never respond after question N with:
- “a few more questions”;
- “we need another round”;
- “let's continue until confident”.

If uncertainty remains after N, report it as unresolved. Do not extend N automatically.

## Clarifications do NOT count as new questions

A clarification is allowed without incrementing the primary-question counter.

Example:
- Primary question 7 asks the user to compare two games or explain one tradeoff.
- The user's answer is ambiguous.
- The worker asks one or more follow-ups solely to understand the answer to primary question 7.
- Progress remains `7 / N` until question 7 is resolved.
- Only when moving to the next independently selected information target does progress become `8 / N`.

Clarifications may:
- disambiguate what the user meant;
- ask which of two interpretations is correct;
- ask for a concrete example of the same answer;
- distinguish two reasons already raised by the user in that answer.

Clarifications may NOT:
- introduce a new game pair;
- introduce a new preference dimension unrelated to the current question;
- opportunistically collect a second independent preference fact;
- hide extra questionnaire items inside one “clarification”.

If the follow-up seeks a new independent preference signal, it is a new primary question and must consume one slot.

## Mandatory START gate

1. Read current `CHAT_PROTOCOL.md` fully and execute START gate.
2. Read current `DIRECTOR_TASK_BOARD.md` current-state section.
3. Read the current canonical Taste/profile material and the current game-rating/reason dataset.
4. Read:
   - `reviews/worker_reports/personal-taste-scoring-architecture-research-01.md`;
   - `reviews/worker_reports/personal-taste-scoring-offline-backtest-01.md`;
   - `reviews/worker_reports/personal-taste-scoring-targeted-offline-backtest-02.md`.
5. Inspect the exact observed failure cases and error taxonomy from the experiments.
6. Do not change production state.

Do not start another task.

## What the questionnaire must learn

Focus on missing preference information that the existing ratings did not encode well enough, especially:

- decisive deal-breakers;
- one dominant positive that outweighs several conventional flaws;
- franchise/history-relative expectations;
- order in which related games were experienced;
- first-contact novelty;
- novelty decay across sequels;
- sustained development vs strong opening followed by stagnation;
- onboarding / first-hours friction;
- information overload / system density;
- combat or control feel;
- repetition tolerance;
- reading/dialogue tolerance;
- emotional/story hook;
- social/contextual value;
- nostalgia/context effects;
- whether conventional quality is personally important or merely nice to have;
- why superficially similar games received different ratings.

Do not force a fixed ontology if the actual profile suggests other more informative gaps.

## Question selection method

Design the primary questions to maximize information gain from the existing profile.

Prefer:
- pairwise comparisons where they isolate one uncertain preference;
- contrastive questions between games with similar ratings but different reasons;
- contrastive questions between externally similar games with very different ratings;
- “which mattered more?” tradeoff questions;
- “what would have changed your rating most?” counterfactuals;
- carefully chosen cases from the prior backtest failures.

Avoid:
- generic personality questions;
- repeated restatement of facts already explicit in the profile;
- questions whose answer can be inferred reliably from existing direct reasons;
- asking the user to remember details they have already said they no longer remember;
- long open-ended essays when a bounded comparison can extract the same signal.

## Determine N before proposing the questionnaire

The worker must estimate how many independent uncertainty targets remain.

For each candidate target, estimate:
- importance to future scoring;
- uncertainty under current profile;
- redundancy with other questions;
- expected information gain;
- whether the target can be combined responsibly with another primary question.

Then choose the smallest N that covers the high-value uncertainty targets without obvious redundancy.

Do not use an arbitrary round number.

The report must explicitly state:
- chosen N;
- why fewer questions would leave important gaps;
- why more questions would have sharply diminishing value;
- approximate expected time for the user;
- expected distribution of question types.

## Adaptive wording, fixed count

The questionnaire may be adaptive in **content**, but not in **length**.

That means:
- the exact wording/order of later questions may depend on earlier answers;
- the total number N remains fixed;
- each primary slot must be reserved for one independent information target;
- if an earlier answer resolves a later target completely, that later slot should be reassigned to the next highest-value unresolved target, not deleted and not used to exceed N.

No dynamic extension beyond N.

## Early finish

The worker must decide whether early finish is allowed.

Preferred rule:
- early finish MAY be allowed if all remaining reserved targets become redundant/resolved;
- early finish must only reduce the total, never extend it;
- if used, UI should say `completed early at X / N maximum`.

If early finish would make the experiment harder to audit, recommend no early finish. Justify the choice.

## Progress UX

Design a simple progress contract.

At minimum:
- show `Question X of N`;
- clarification retains the same X;
- after resolving question X, move to X+1;
- show remaining primary questions;
- on completion show `N/N complete` or `X/N complete early`;
- never hide or reset the counter.

## Output format for each primary question

Design a structured question record with:
- question_id;
- primary_index;
- uncertainty_target;
- question_text_ru;
- games/references used;
- expected answer type;
- allowed clarification scope;
- what new profile fact it can establish;
- what scoring failure it is intended to reduce;
- fallback if the user cannot remember enough.

Do not actually ask the user the questionnaire in this task.

## Future profile update

Design how answers should later update profile evidence.

Separate:
- direct user statement;
- inferred preference;
- confidence;
- source question;
- related games;
- temporal/context qualifier;
- whether it is globally reusable or game/franchise-specific.

Clarification answers should attach to the same source primary question.

Do not implement profile writes in this task.

## Validation against known failures

Test the proposed questionnaire design against the hardest known examples from backtests, including where available:
- Mass Effect;
- Castlevania: Lords of Shadow;
- GTA V / GTA III;
- Red Dead Redemption / RDR2 ordering/context;
- Cyberpunk 2077;
- Perfect World;
- Sanitarium;
- Postal 2;
- Assassin's Creed;
- Banner Saga 2.

For each, explain which planned question(s) would likely have captured the missing preference information and whether that knowledge generalizes beyond the one game.

Do not create AppID-specific production rules.

## External practice review

Perform a bounded current web review of relevant methods:
- active preference learning;
- adaptive questionnaires;
- pairwise elicitation;
- value-of-information / information gain;
- stopping criteria in preference elicitation;
- avoiding respondent fatigue.

Use primary/academic/first-party sources where possible.

Do not copy long passages.

## Required report

Write:
`reviews/worker_reports/bounded-personal-taste-calibration-questionnaire-design-01.md`

Required sections:

1. Task
2. Current evidence reviewed
3. Missing information map
4. External practices
5. Definition of a primary question
6. Definition of a clarification
7. Clarification counting rule
8. Candidate uncertainty targets
9. Information-gain prioritization
10. Chosen total N
11. Why not fewer
12. Why not more
13. Early-finish rule
14. Progress UX
15. Question-type distribution
16. Proposed questionnaire plan
17. Adaptive branching rules
18. Profile-update schema proposal
19. Validation against known failure cases
20. Expected user time
21. Risks / fatigue / ambiguity
22. Exact external sources
23. Status
24. Recommended next step — exactly one bounded next action

Allowed statuses:
- `design_complete_ready_for_director_review`
- `needs_more_research`
- `blocked`

## Hard boundaries

Do NOT:
- ask the user the questionnaire now;
- modify canonical profile;
- modify production scoring/ranking;
- modify Deep/Dossier contracts;
- run production semantic workers;
- publish site changes;
- create Scheduled Tasks;
- create an implementation PR;
- start another task.

Only the report and minimal task-tracking metadata may be written.
