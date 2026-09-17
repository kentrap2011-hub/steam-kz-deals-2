# WORKER TASK — TASTE DOSSIER SEMANTIC CONSISTENCY GAPS IMPLEMENT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-semantic-consistency-gaps-implement-01`
Mode: `IMPLEMENT / ACTIVATE / VALIDATE`

## START gate

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main` и зафиксируй обязательный checklist до широкого поиска.

После этого прочитай только необходимые для задачи актуальные canonical files, включая:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste dossier маршрут в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- canonical strict validator и только связанные dossier validation paths;
- `PROJECT_DECISIONS.md` только если для конкретного изменения требуется понять/изменить неочевидное архитектурное rationale.

Перед первой runtime/workflow/contract write выполни architecture preflight из `CHAT_CONTEXT.md`.

## Required prior durable reports

Прочитай полностью:

1. `reviews/worker_reports/taste-dossier-semantic-consistency-gap-audit-01.md`
2. `reviews/worker_reports/taste-dossier-language-binding-fix-implement-01.md`

Audit baseline был до language-binding fix, поэтому **нельзя слепо реализовывать старые findings**.

## Goal

Закрыть все шесть доказанных semantic-consistency gaps `SCG-01..SCG-06` на актуальном `main` после уже принятого language-binding fix.

Главный принцип: candidate с внутренне противоречивой provenance/evidence semantics не должен становиться canonical, а worker-facing generation contract не должен позволять легко генерировать формы, которые canonical strict validator затем закономерно отвергает.

Исправления должны быть системными на уровне canonical contract/prompt/schema/strict validation/derived generation semantics. Не использовать retry/healing как замену корректному generation/validation contract.

## Mandatory reconciliation against fresh main

**Сначала** заново проверь каждый `SCG-01..SCG-06` против текущего `main` после language-binding fix.

Для каждого finding итоговый durable report обязан дать ровно одну классификацию:

- `implemented_now`
- `already_closed_on_current_main`

Ни один finding нельзя молча пропустить.

Если language-binding fix уже полностью или частично закрыл finding, не дублируй реализацию. Для `already_closed_on_current_main` добавь/укажи deterministic regression, доказывающий exact audited counterexample.

Если finding только частично закрыт, он считается `implemented_now`: реализуй недостающую часть и явно опиши, что уже существовало и что добавлено.

## Findings that must be reconciled and closed

### SCG-01 — acceptance gap: parent source ↔ child feedback physical provenance

Audit proof:
- live strict-valid `g000003` смог связать Reddit child items из `r/XboxSeriesX` / `r/patientgamers` с parent source locator `r/sniperelite` только потому, что host совпадал;
- DEEEER смог связать `steam-discussion:*` child item с parent, объявленным как `steam_reviews` `/reviews/` surface.

Required outcome:
- определить **один canonical deterministic parent-item relationship rule** для feedback item URL/public ref ↔ parent source locator/type;
- strict validation должна reject-ить audited mismatch;
- не ломать корректные same-thread / same-surface distinct feedback items;
- source_mix/source_type/language/freshness/role не должны выводиться из ложного parent provenance.

Не вводить второй validator truth source.

### SCG-02 — acceptance gap: source ↔ child temporal coherence

Audit counterexample:
- parent source `publication_date=null`, `freshness=recent`, `evidence_role=current_state`;
- exact bound child feedback record того же physical item имеет известную старую дату, например `2020-01-01`;
- current observation всё равно проходит через parent metadata.

Required outcome:
- добавить deterministic source ↔ feedback temporal coherence там, где child date разрешает физический item/current-state support;
- old known child item не должен поддерживать current/recent claim через противоречащую parent metadata;
- сохранить существующее допустимое поведение truly-undated source/item cases, где child date реально неизвестна;
- существующий dated-source `<=365 recent / >365 older` guard не ослаблять.

### SCG-03 — acceptance gap: dossier `summary` not evidence-bound

Audit counterexample:
- structured fields strict-valid;
- `summary` можно заменить на противоречащий structured evidence текст или добавить неподтверждённый factual claim;
- strict сейчас проверяет в основном type/length/privacy guards.

Required outcome:
- summary не должна иметь возможность добавлять новые неподтверждённые factual/evidence claims;
- предпочесть механически derived summary из уже validated structured findings **или** эквивалентный явный structured binding, который strict-validates summary content against validated findings;
- downstream не должен получать canonical free-form contradiction.

Не добавлять brittle natural-language truth parser как отдельную competing authority, если deterministic derivation/binding решает задачу проще.

### SCG-04 — acceptance gap: exact duplicate conflicts

Audit counterexample:
- byte-identical valid conflict можно добавить второй раз;
- оба проходят individual mention_count/recurrence/source/feedback checks.

Required outcome:
- deterministic exact-conflict duplicate rejection;
- по смыслу выровнять с уже существующим exact duplicate guard для observations;
- semantic near-duplicate redesign не делать без необходимости — задача требует закрыть proven exact duplicate gap.

### SCG-05 — generation contract gap: `overall_strength`

Audit proof:
- strict derivation для `strong/moderate` основана на observations;
- strong conflict сам по себе не делает `overall_strength=strong` валидным;
- worker-facing prompt/schema/evidence contract раньше не объясняли это явно.

Required outcome:
- на свежем main определить текущую canonical derivation и сделать её **явной и machine/worker-facing**;
- если strict semantics по-прежнему observation-based, сохранить её и явно закрепить в contract/prompt/schema invariants вместо ослабления validator;
- worker не должен логично, но ошибочно повышать overall_strength только из-за strong conflict;
- strict validator и worker contract должны иметь одну семантику.

Не расширять scope до общего redesign evidence scoring.

### SCG-06 — generation contract gap: parent source language ↔ child feedback language

Audit proof отдельный от Blacksad:
- strict уже требует child `russian` -> parent `russian|mixed`;
- child `non_russian` -> parent `non_russian|mixed`;
- worker-facing contract раньше не объяснял exact invariant.

Required outcome:
- сначала re-check после `taste-dossier-language-binding-fix-implement-01`;
- если invariant уже полностью worker-facing и regression-covered, классифицировать `already_closed_on_current_main`;
- иначе перенести exact parent↔child language containment rule в active machine contract/prompt/schema invariants без изменения смысла existing strict validator;
- не дублировать Blacksad observation-language fix и не добавлять лишние representations.

## Mandatory regression proof

Нужен deterministic regression для **каждого** `SCG-01..SCG-06` exact audited counterexample.

Минимально доказать:
- SCG-01: audited same-host wrong-parent/surface mismatch rejected; valid same-surface distinct items preserved;
- SCG-02: old dated child cannot be laundered through undated `recent/current_state` parent; genuinely unknown date behavior preserved;
- SCG-03: contradictory/unsupported summary shape cannot become canonical;
- SCG-04: exact duplicate conflict rejected;
- SCG-05: worker-facing contract deterministically matches canonical `overall_strength` derivation and audited strong-conflict-only shape cannot be generated/accepted inconsistently;
- SCG-06: parent-child language invariant is explicitly worker-facing and exact mismatch shape is regression-covered.

Сохрани все уже существующие guards, включая:
- expired dossier rejection;
- physical feedback/source alias normalization;
- item-level feedback vs list/search/index/vague refs;
- dated freshness 365-day rule;
- bidirectional `russian_attempt`;
- conflicts feedback-bound recurrence;
- mention_count = distinct bound feedback records;
- aggregate Steam counts do not create mention_count;
- Russian-rendered store page is not player feedback;
- compact provenance privacy/content guard;
- no usernames/profile URLs/raw review bodies;
- content-complete compatibility binding;
- maximal contiguous prefix;
- parallel buffering behind invalid expected group.

## Architecture constraints — MUST NOT CHANGE

- GitHub remains control plane.
- Scheduled ChatGPT remains bounded semantic/data worker + immutable create-only candidate publisher.
- Interactive chat is not production executor/backlog manager.
- Canonical group size remains **3**.
- Do not split groups into per-game acceptance/retry.
- Do not add automatic retry/healing manager around semantic errors.
- Do not weaken canonical strict validation for throughput.
- Keep one canonical strict validator truth source.
- Do not change parallel-buffer architecture, maximal-contiguous-prefix acceptance, canonical writer ownership, stale quarantine ownership, scope/order/progress/completeness ownership.
- Do not change Taste Semantic Producer, ranking, pricing, package economics, giveaway, duration, translation, or unrelated UI.
- Do not change DLC/package product architecture.
- Do not manually repair/rewrite queue/cache/progress/receipts/candidate artifacts.

## Compatibility / activation requirement

Because prompt/contract/schema/validator semantics may change content-complete compatibility binding, use only the normal GitHub-owned compatibility migration path.

If the resulting binding is incompatible with the current active snapshot:
- merge the implementation through the normal PR/CI path;
- allow/trigger only the existing canonical activation path permitted by the repository;
- require a fresh compatible snapshot/binding;
- old candidates/snapshot must become stale/inert only through normal GitHub-owned behavior;
- do **not** rebind, patch, overwrite or manually advance old artifacts/progress.

If a fresh snapshot is not required under the actual current canonical binding rules, prove why in the report instead of forcing one manually.

## Scheduled Task / MANUAL UI RULE

**Do NOT run Scheduled Task `Run now` in this implementation task.**

Scheduled Task UI worker надёжно читать не умеет. Если для последующего live acceptance нужен UI-result, пользователь предоставит его вручную. Не трать время на попытки получить Scheduled Task UI.

This task ends after deterministic implementation + merge + canonical post-merge activation/compatibility verification.

Live Scheduled ChatGPT behavior is a **separate later acceptance task**.

Если причина любого зависания/ошибки неизвестна — так и написать: `причина неизвестна`. Не придумывать причину.

## PR / merge / validation

Required if implementation changes are needed:
- use a bounded worker branch/PR;
- run the relevant focused dossier CI/regressions plus any canonical ownership/backlog checks required by changed paths;
- merge only after required validation is green;
- verify post-merge activation/compatibility state from canonical GitHub outputs;
- do not launch production `Run now`.

If all six findings are already closed on fresh main (unlikely but possible), do not create no-op implementation churn: prove all six with current-main regressions and report `already_closed_on_current_main` for each.

## Durable report

Required path:

`reviews/worker_reports/taste-dossier-semantic-consistency-gaps-implement-01.md`

Report must be committed to `main` before presenting the task as complete.

Keep it compact but sufficient for Director review. It must include:

1. `Task` / mode / repository.
2. Architecture preflight result.
3. A table for **SCG-01..SCG-06**, each with:
   - fresh-main status before change;
   - classification exactly `implemented_now` or `already_closed_on_current_main`;
   - exact canonical invariant after task;
   - regression proof/ref.
4. Exact changes made, without large diffs/logs.
5. Confirmation that strict validator was not weakened and whether it changed/was extended.
6. Confirmation that one canonical validator truth source remains.
7. Confirmation that parallel buffer architecture and group size `3` remain unchanged.
8. PR, CI, merge refs.
9. Post-merge compatibility/activation result:
   - current snapshot/binding;
   - whether a fresh snapshot was created and why;
   - canonical expected sequence / prepared/completed/remaining/group count;
   - treatment of old candidate artifacts as stale/inert if applicable.
10. Confirmation that Scheduled Task `Run now` was not executed and settings were not changed.
11. `Unresolved` — anything still not proved.
12. `Status`.
13. Exactly one recommended next step.
14. `Efficiency / reusable lesson` per `DIRECTOR_PROTOCOL.md`.

Allowed final statuses:
- `complete_ready_for_live_acceptance`
- `needs_fix`
- `blocked`
- `needs_user_decision`

`complete_ready_for_live_acceptance` is allowed only if all `SCG-01..SCG-06` are individually classified and deterministically closed on current `main`, required merge/activation is complete, and `Run now` has not been used as proof.

## CURRENT_TASK.md

Worker may update `CURRENT_TASK.md` only as required by `CHAT_PROTOCOL.md` for this actually executing task. Do not erase or overwrite unrelated concurrent work.

## Expected next step after success

One separate live acceptance of the existing `Taste Steam Review Dossier` Scheduled Task against the fresh/current compatible snapshot, followed by a separate READ / VALIDATE acceptance report. Do not perform that live run inside this task.
