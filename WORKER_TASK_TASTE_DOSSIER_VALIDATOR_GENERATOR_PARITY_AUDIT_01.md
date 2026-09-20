# WORKER TASK — TASTE DOSSIER VALIDATOR ↔ GENERATOR PARITY AUDIT 01

Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main

Не ищи, не читай, не меняй и не используй другие репозитории.
Если GitHub/tool открыл другой repo по умолчанию или repo неоднозначен — остановись и переключись на `kentrap2011-hub/steam-kz-deals-2` до любых действий.

Task ID: `taste-dossier-validator-generator-parity-audit-01`
Mode: `READ-ONLY / RECON`

## START

Сначала открой актуальный `CHAT_PROTOCOL.md` из `main` и выполни START gate полностью.
Затем открой этот task-файл из `main`.

После START прочитай только минимально необходимое:
- `CHAT_CONTEXT.md`;
- `CURRENT_TASK.md`;
- релевантный Taste Steam review dossier route в `PROJECT_ROUTES.md`;
- `config/execution_ownership_contract.json`;
- `config/taste_steam_review_dossier_contract.json`;
- `config/taste_steam_review_dossier_worker_prompt.md`;
- `config/taste_steam_review_dossier_schema.json`;
- `config/taste_steam_review_dossier_web_evidence_contract.json`;
- `scripts/taste_steam_review_dossier_strict.py`;
- при необходимости только напрямую связанные prepublication/buffered validation helpers;
- `reviews/worker_reports/taste-dossier-identity-provenance-generation-fix-01.md` как уже закрытый контрольный пример.

До широкого Git history не переходить. Старые task/report файлы читать только если конкретный current-main rule невозможно классифицировать без них.

## Why this audit exists

Недавний production blocker показал конкретный класс дефекта:

- canonical strict validator уже жёстко требовал правило;
- generator-facing prompt/schema не выражали это правило достаточно явно;
- Scheduled worker поэтому мог сформировать структурно неверный candidate;
- GitHub корректно отклонял его только после публикации.

Identity-provenance gap уже исправлен и не является новым finding этого аудита.

Нужно проверить, остались ли ещё **такие же реальные parity gaps**.

Это не аудит всех возможных будущих ошибок и не попытка заранее предсказать любой необычный web case.

## Goal

Сопоставить substantive canonical validation requirements для worker-generated dossier с generator-facing instructions/contracts и ответить:

> Есть ли сейчас правило, которое GitHub validator реально требует для принятия dossier, но Scheduled worker не получает достаточно явной инструкции/машинного инварианта, чтобы разумно ожидать корректную генерацию до публикации?

Искать только доказанные текущим `main` расхождения.

## Exact comparison layers

Сравнить только эти активные слои:

1. authoritative acceptance:
   - `scripts/taste_steam_review_dossier_strict.py`;
   - только необходимые напрямую вызываемые validation helpers.

2. generator-facing machine contract:
   - `config/taste_steam_review_dossier_schema.json`;
   - `config/taste_steam_review_dossier_web_evidence_contract.json`.

3. generator-facing semantic instructions:
   - `config/taste_steam_review_dossier_worker_prompt.md`.

4. ownership/control-plane boundary:
   - canonical dossier + execution ownership contracts только для проверки, что предполагаемое правило вообще принадлежит Scheduled worker generation, а не GitHub-only control plane.

Не расширять аудит на весь проект, Taste ranking, UI, purchase logic, scheduler platform internals или unrelated workflows.

## What counts as a finding

Finding допустим только если выполнены ВСЕ условия:

1. strict/canonical validator действительно проверяет конкретный инвариант на worker-generated dossier;
2. этот инвариант относится к данным/семантике, которые должен сформировать Scheduled worker;
3. generator-facing prompt/schema/evidence contract:
   - не выражают его вообще; ИЛИ
   - выражают существенно слабее/двусмысленнее; ИЛИ
   - дают формулировку, которая разумно допускает output, затем отвергаемый validator-ом;
4. расхождение можно показать конкретным минимальным valid-looking counterexample shape;
5. это не уже закрытый identity-provenance gap;
6. это не чисто defensive GitHub-side проверка malformed/corrupt/tampered transport, которую Scheduled worker не должен эмулировать;
7. это не гипотеза о web retrieval, источнике или игре, для которой validator/generator contract сейчас согласован.

Если хотя бы одно условие не доказано — не считать finding.

## Required classification

Для substantive validator rules составить compact parity matrix, не копируя код/JSON целиком.

Для каждого проверенного класса правила указать одну из классификаций:

- `aligned` — validator и generator-facing layers достаточно согласованы;
- `validator_only_by_design` — GitHub обязан проверять это post-publication, но worker не должен получать/эмулировать отдельное правило;
- `confirmed_parity_gap` — есть доказанное расхождение по критериям выше;
- `unclear_needs_bounded_followup` — только если current-main evidence объективно недостаточно; не превращать это в speculative finding.

Матрица должна охватить substantive classes как минимум:
- game identity / exact product binding;
- source role and provenance;
- player-feedback record identity;
- parent/child physical binding and aliasing;
- source / feedback language containment;
- observation evidence-language derivation;
- mention_count and recurrence;
- stable vs fallback recurrence strength;
- Russian attempt states;
- source mix / physical diversity;
- current / historical / durable / uncertain temporal support;
- freshness / dates;
- privacy / forbidden author identity;
- source type / player_feedback role restrictions;
- professional/official context boundaries;
- Steam Store parent exception;
- summary derivation;
- duplicate observations/conflicts;
- contract/binding compatibility fields relevant to worker serialization.

Не надо перечислять тривиальные JSON type/length checks по одному, если они не создают generator parity risk.

## Important exclusions

НЕ искать:
- «что теоретически ещё может когда-нибудь сломаться»;
- новые retrieval strategies;
- новые источники;
- новые retry/queue/checkpoint mechanisms;
- platform hang/stall handling;
- scheduler reliability;
- performance optimization;
- general code quality;
- validator hardening unrelated to worker instructions.

НЕ предлагать менять validator только потому, что worker prompt можно сделать подробнее.

## Identity provenance control case

Недавний закрытый дефект должен использоваться как контрольный образец типа finding:

`identity_source_ids` без source с `evidence_role:"identity"`
→ strict reject
→ старый generator contract был слабее
→ теперь prompt/schema выровнены.

Подтверди, что current `main` для этого правила теперь классифицируется как `aligned`.

Не открывай его заново как finding.

## Prioritization of confirmed gaps

Если найдены реальные gaps, для каждого указать:

- exact validator behavior;
- exact generator-facing omission/ambiguity;
- минимальный пример output, который worker может разумно сформировать, но validator отвергнет;
- production consequence:
  - `hard_blocker` — гарантированно блокирует canonical prefix при возникновении;
  - `conditional_blocker` — блокирует только конкретный evidence shape;
- smallest likely repo-owned fix surface:
  - prompt only;
  - schema only;
  - prompt + schema;
  - evidence contract clarification;
  - tests/fixtures;
- не писать сам fix.

Не давать баллы/проценты риска. Только фактическая классификация blocker class.

## Boundedness rule

Это один bounded audit pass.

Если после систематического сравнения активных substantive rule classes подтверждённых gaps нет — так и зафиксировать:

`no_confirmed_parity_gaps`.

Не продолжать искать дополнительные гипотезы ради количества findings.

Если найдено несколько gaps, не исследовать downstream production examples для каждого, если static current-main evidence уже достаточен.

## Writes / safety

Это READ-ONLY / RECON.

Запрещено менять:
- prompt;
- schema;
- evidence contract;
- validator;
- runtime scripts;
- workflows;
- Scheduled Task;
- production candidates;
- inbox/quarantine;
- canonical progress;
- recovery state.

Разрешён единственный итоговый project write:
- compact worker report по указанному пути.

Если текущий protocol требует task-state bookkeeping, не уничтожать и не переписывать чужую активную работу; отразить task state только внутри report либо остановиться и указать конфликт.

## Validation of the audit itself

Перед финалом worker должен проверить:

1. каждый `confirmed_parity_gap` привязан к конкретному validator requirement;
2. показано, почему текущий prompt/schema/evidence contract недостаточен;
3. исключены GitHub-only defensive/transport checks;
4. identity provenance не переобъявлен как новый gap;
5. нет speculative «может быть» findings;
6. report достаточно компактный, чтобы Director мог принять решение без чтения source/diffs.

## Durable report

Required path:
`reviews/worker_reports/taste-dossier-validator-generator-parity-audit-01.md`

Required sections:

1. Task / repo / mode.
2. Scope and exclusions.
3. Sources of truth checked.
4. Parity method.
5. Compact substantive parity matrix.
6. Confirmed parity gaps.
7. Validator-only-by-design items worth noting.
8. Identity-provenance control case status.
9. Unclear items, if any.
10. Changes: `none` except report.
11. Validation of findings.
12. Unresolved.
13. Status.
14. Exactly one recommended next step.
15. Efficiency / reusable lesson.

Allowed statuses:
- `complete_no_confirmed_parity_gaps`
- `complete_confirmed_parity_gaps`
- `needs_bounded_followup`
- `blocked`

## Exactly one next step

If `complete_no_confirmed_parity_gaps`:
- recommend returning to one clean production `Run now` acceptance; do not invent further preventive audits.

If `complete_confirmed_parity_gaps`:
- recommend one bounded IMPLEMENT task covering only the confirmed gaps, without starting implementation.

If `needs_bounded_followup`:
- identify exactly one unresolved rule class and the minimal evidence needed.

If `blocked`:
- identify exact missing/unreadable canonical source.

Do not implement fixes in this audit.
