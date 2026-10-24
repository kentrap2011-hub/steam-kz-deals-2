# ЧАТ 3 — Research Notes V2: durable per-item GitHub receipt persistence

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v2-research-per-item-receipts-implement-01
Worker slot: НОВЫЙ физический ЧАТ 3
Mode: bounded inactive IMPLEMENT or CONTRACT_BLOCKED report; draft PR only, no self-merge
Report path: reviews/worker_reports/dossier-v2-research-per-item-receipts-implement-01.md

## START and exact ownership

Прочитай текущий CHAT_PROTOCOL.md полностью, исполни START gate и ограниченный architecture preflight (источник полномочий, owner writer, отсутствие переноса control-plane в чат). Проверь этот файл в текущем main, адресную запись config/director_task_plan.json и только текущий верх Board. Не проводи полный аудит Dossier, не перебирай историю всех PR и не пересчитывай старые 18 исследованных игр.

**GitHub** владеет границами Research queue, run/attempt authority, durable write/receipt, history и accept decision. Semantic worker только передаёт candidate Research, он не назначает себе authority и не помечает свои результаты принятыми.

## Почему это независимая параллельная задача

ЧАТ 2 сейчас независимо проверяет draft PR #266 exact HEAD 1d46b84aff35feee0aca68fc8ad9f3154a330036 (ручной V2 issuer). **Этот PR не принят.** ЧАТ 3 НЕ проверяет и НЕ редактирует issuer; твоя задача — один последующий компонент: персистентное сохранение и подтверждение КАЖДОГО V2 Research Notes candidate, не финальный Assembly.

Контекст: merged inactive V2 PR #239 и #243, existing V1 Research single-add transport / Git history / receipt patterns, current V2 offline interfaces and pinned original-18/six groups. Читать только необходимые exact contracts, existing scripts and tests. Старые marker/authorization SHA — **исторические доказательства**, а не V2 разрешение.

## Цель: один реальный безопасный implementation outcome

1. Найди уже существующие GitHub-owned Research transport/ingest/receipt примитивы V1 и offline V2 proof functions. Коротко обозначь, какие из них переиспользуются — **не создавать новый writer сервис, GitHub workflow, CI, validator, queue или scheduler**.
2. Адаптируй ровно один **неактивный offline** путь для *предлагаемого* V2 per-item Research payload → строгой локальной проверки → create-only Git history write/receipt preparation/verification, оставляя фактические remote writes закрытыми до отдельной будущей авторизации. Формат должен удерживать immutable original 18 assignment identity, конкретный V2 marker/manifest/run + Git parent/nonce, source evidence bindings, item attempt identity, one-item-once uniqueness и immutable receipt. Чётко различай candidate transport, rejected/accepted receipt, semantic quality verdict, canonical ingest — не выдавай запись payload за полностью accepted Research или Dossier.
3. Если существующий контракт разрешает только offline prepare/verify без реального writer, разрешён минимальный готовый offline адаптер + disposable Git tests, но НЕ создание «нового активного writer» и НЕ выдумывание GitHub-подтверждения. При отсутствии права на writer/grant — `CONTRACT_BLOCKED_WRITER_AUTHORITY` с единственной конкретной недостающей предпосылкой.
4. Доказательные негативные случаи в уже существующих offline тестовых средствах: повторная запись того же item, изменённый payload/blob после receipt, другое assignment/group, чужой marker/nonce/parent, create-only нарушение, некорректный proof или самовольный повтор, rejection/failure не становится accepted, гонка двух writer-веток, «принято» без настоящего GitHub receipt.
5. Не менять рабочие V1 пути, исходный frozen Research 18, не ретраить 2 invalid и 4 missing, не переносить production writer authority, не запускать GitHub Action или semantic work.

## Жёсткое разделение ownership от PR #266

**НЕ редактировать и НЕ переопределять ни один из семи файлов в PR #266:**
- `.github/workflows/authorize-dossier-shadow-research-feasibility.yml`
- `.github/workflows/publish-dossier-shadow-research-freeze.yml`
- `config/dossier_research_notes_v2_contract.json`
- `scripts/dossier_shadow_research_feasibility.py`
- `scripts/dossier_shadow_research_trial_publish.py`
- `scripts/test_dossier_research_notes_v2.py`
- `reviews/worker_reports/dossier-v2-existing-issuer-adapt-implement-01.md`

Если необходима правка любого из этих путей, **не делай конфликтующих изменений**: report-only `BLOCKED_FILE_OWNERSHIP` и одно точное dependency на принятие/переработку PR #266. Для собственного малого isolated component разрешены лишь не пересекающиеся V2 receipt transport paths и соответствующие существующие offline test mechanisms. Можно добавить отдельный *unit test module*, если он не является новым CI/validator или архитектурной службой; никакого нового внешнего workflow.

No change to Director files, Board/registry, site, prices, Deep/Fast, Dossier V1 production or canonical output. No new GitHub CI/Actions/validators, changes to existing checks, automations, Scheduled Tasks, deploy, production writer, real human grant, marker issuance, Research/Assembly execution or manual workflow_dispatch.

## Required output

Один draft PR с минимальными изменениями кода и коротким report в указанном пути — **или report-only при доказанном blocker**. Укажи точный HEAD, изменённые файлы, результаты локальных offline tests и *существующих* GitHub checks, evidence provenance, что именно ещё нельзя записать/подтвердить в настоящем GitHub и статус `READY_FOR_INDEPENDENT_QA` / `CONTRACT_BLOCKED_WRITER_AUTHORITY` / `BLOCKED_FILE_OWNERSHIP`. Не объявляй production/Research V2 готовым к запуску. Реальный кодовый PR требует отдельный independent QA exact HEAD до merge.
