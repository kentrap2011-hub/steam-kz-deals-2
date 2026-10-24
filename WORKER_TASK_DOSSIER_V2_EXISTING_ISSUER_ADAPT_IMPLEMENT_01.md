# ЧАТ 1 — Dossier V2: адаптация существующего ручного GitHub issuer

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v2-existing-issuer-adapt-implement-01
Worker slot: НОВЫЙ физический ЧАТ 1
Mode: BOUNDED IMPLEMENT, inactive/manual only; draft PR, no self-merge

## Решение пользователя (scope approval)

Мы уже реально запустили первоначальный Dossier Research на 18 играх. ЧАТ 1 в report-only PR #264 доказал, что уже существует reusable GitHub freeze → nonce marker → отдельная одноразовая feasibility authorization. **Пользователь одобрил адаптацию этого существующего механизма для будущего Dossier Notes V2 — НЕ создание нового механизма, НЕ конкретный реальный запуск.**

Это разрешение — только на разработку ограниченного неактивного V2-specific manual control-plane issuer / grant contract. Оно **НЕ** является одноразовым human grant на конкретный V2 Research, не запускает разрешение, не запускает semantics, не создаёт live marker и не переводит V2 в активное состояние.

## START / Evidence budget

Полностью прочитай текущий CHAT_PROTOCOL.md, выполни START gate и **ограниченный** architecture preflight (GitHub owns authorization/manifest/marker/writer; interactive semantic workers only submit bounded candidate data; no new recurring pipeline). Прочитай ЭТО задание из текущего main и адресную registry item + верх Board, но не длинный Board/history.

Следуй непосредственным источникам:
- Точный результат доказательной проверки в PR #264 (`reviews/worker_reports/dossier-v2-original-run-issuer-reuse-01.md` в её branch) — основной comparative source. Не повторяй её расследование.
- Исходные скрипты только механизма publisher/feasibility: `scripts/dossier_shadow_research_trial_publish.py`, `scripts/dossier_shadow_research_feasibility.py`; manual workflows `.github/workflows/publish-dossier-shadow-research-freeze.yml`, `.github/workflows/authorize-dossier-shadow-research-feasibility.yml`.
- Текущие canonical V2 contracts, pinned original 18, `scripts/dossier_research_notes_v2.py` и существующие V2 tests в том объёме, который нужен для функционального diff.
- Реальные старые привязки для предотвращения replay: original buffer commit `343e5956ceda07c728c00371301c418036068a22`, marker `bb63cc291eba5aa8fc56e2920ef84d131ac28a4f`, feasibility authorization `2a726cf6731c0fc1e7bc809474627383c107ef9b`. Это **доказательства V1**, но не активные полномочия V2.
- Inactive V2 PR #239 / #243; blocker report PR #261. Исторический PR #232 не запускать и не возобновлять.

## Цель — один функциональный минимум

1. В существующем GitHub-owned manual issuer workflow/code **переиспользуй** механизм двух отдельных control-plane разрешений, deterministic frozen original 18, одноразового create-only GitHub marker и separate post-marker authorization, remote Git ancestry, commit/nonce/parent checks, race refusal, first-attempt and exact SHA pinning. Не копируй архитектуру; предпочтительна явно версия-ориентированная V2 ветка/адаптер поверх уже существующих примитивов. Существующее поведение V1 must remain unchanged.
2. Добавь только необходимые **prospective, inactive V2-specific** bindings / contract fields: точная исходная 18/six triple очередь и original blob, собственные V2 namespace/branch, immutable V2 manifest→nonce-only marker parent, отдельный вручную подтверждаемый V2 authorization commit, immutable scoped approval evidence и proof of one-time use/duplicate refusal. Документируй, что обычный prompt/worker ответ не является V2 human grant, а старый V1 grant уже израсходован.
3. До будущего отдельного human approval вся prospective V2 issuer ветка должна **fail closed**. Не переводить `active=false`, `authorized_for_semantic_execution=false`, `authorized_for_canonical_ingest=false`, `production_enabled=false` в true. Создание реальных объектов невозможно как побочный эффект теста, setup или merge PR. Не расширять per-item receipts, reviewer appointment, Research Notes semantics или Assembly writer — это самостоятельные будущие gates.
4. Если для V2 issuer принципиально требуется редактирование существующего **РУЧНОГО issuer workflow**, допускается только минимальный additive V2 mode *с выключенным запуском по умолчанию* и доказанной неизменностью V1. **Не создавай новый workflow или CI check.** Если нельзя сделать это без модификации существующих CI/validator Actions или без granting live authority — остановись: `BLOCKED_NEEDS_SCOPE_DECISION`, краткий report-only draft PR вместо псевдореализации.
5. Проверяй через существующие offline тестовые средства на disposable Git/local fixture, не через реальные GitHub `workflow_dispatch`. Adversarial cases обязательны: повтор разрешения, reuse старого SHA/nonce, чужой parent/изменение frozen 18, forged/unverified GH actor, missing human grant, попытка второго marker/authorization, concurrent/racing ref update, изменения marker/manifest после сохранения, direct semantics without separate approval. Отличай synthetic validation от actual GitHub activation.
6. Сфокусируйся на **одном small implementation PR**; не откладывай работу ради очередного широкого архитектурного отчёта. Если реализация доказанно невозможна в этих рамках — назови одно точное минимальное дополнительное разрешение, а не предлагай новую систему.

## Запреты

- НЕ запускать Research, Assembly, иной semantic worker, live feasibility grant, `workflow_dispatch`, real issuer, marker/manifest/nonce/persistence, Deploy или production/canonical write.
- НЕ создавать новые GitHub Actions, CI checks, workflow files, валидаторы, планировщики, background tasks, очереди, retries, новую службу issuer, подмену пользователя.
- НЕ изменять действующие CI checks/validators. Существующие **manual issuer** workflow менять только если выполнено условие п. 4; GitHub CI и issuer workflow — разные вещи.
- НЕ менять Deep, Fast, site/UI/currency, old 18 Research packages, frozen original branch, PR #232, Director files, Board/task registry, старый V1 grant/contract семантически.
- НЕ ослаблять original source-quality QA, exact immutable bindings, actor proof, reviewer independence, create-only, fail-closed acceptance. No PR self-merge.

## Deliverable

Один draft PR с минимальным diff и коротким report `reviews/worker_reports/dossier-v2-existing-issuer-adapt-implement-01.md`.
Отчёт:
- 1 абзац о том, что реально переиспользовано вместо новой архитектуры;
- exact changed paths, HEAD, test results + existing GitHub checks;
- что предотвращает live V2 grant/semantic execution сейчас;
- проверка V1 compatibility и adversarial cases;
- один следующий нужный gate после этого компонента (никаких автоматических запусков);
- `READY_FOR_INDEPENDENT_QA` или `BLOCKED_NEEDS_SCOPE_DECISION`.

После реализации необходим **другой физический ЧАТ 2** для независимого QA на точном HEAD PR до любого merge. Сам PR не даёт право активировать V2.
