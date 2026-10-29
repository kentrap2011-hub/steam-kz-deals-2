# ЧАТ 1 — implementation: автоматическое освобождение номера

**Task:** `director-chat-slot-auto-release-protocol-implement-01` · bounded L1 governance.
**Repository:** `kentrap2011-hub/steam-kz-deals-2` · base `main@316f87e8775d04df0be9e1d566a4a3fc2a484417`.
**Audit authority:** `reviews/worker_reports/director-chat-completion-slot-release-recurrence-audit-01.md` (PR #351).
**Source branch:** `director/chat-slot-auto-release-protocol-implement-01`. **Status:** `complete` (merge is Director-owned).

## Verified facts / Changes
Причина — смешение операционной доступности номера и наблюдаемости окна ChatGPT UI. Заменены конфликтующие правила STATUS, обязательной сводки, выбора минимального свободного слота в §2, сдачи в §3, разграничения registry/UI в §10 и удаления окна в §11. Canonical owner: `DIRECTOR_PROTOCOL.md`; других source, registry, Board, task, workflow или production writes нет.

## Validation — bounded STATUS / REGISTER walkthrough
- Старые QA ЧАТ 1 / ЧАТ 2 завершили #339 / #340: **свободны**, даже если source #322 / #323 не слиты и QA отрицательный или blocked.
- Старые ЧАТ 3 / ЧАТ 4 / ЧАТ 6 сдали implementation: **свободны** независимо от директорской приёмки и QA исходного кода.
- Новые QA ЧАТ 1 / ЧАТ 2 зарегистрированы и выданы, но ещё не запущены: **зарезервированы**, не «заняты» и не доступны для конкурирующего REGISTER.
- Подтверждённый пользовательский запуск: **занят** до итоговой сдачи; отсутствие коммитов и промежуточный progress не release.
- Финальный report, в том числе `CHANGES_REQUIRED`/`BLOCKED_EVIDENCE`: **освобождение немедленно**, без merge или подтверждения закрытия UI.
- Исторический `active/complete` / `worker_slot`: не удерживает номер; конфликт по конкретному launch/result уточняется адресно, без догадки.
- Отдельный вопрос «закрыто ли окно UI»: допустимо **UNKNOWN**, но это не операционный статус.
- Только STATUS: **read-only**, STOP без REGISTER и переназначения; минимальный операционно свободный номер выбирается только при новом разрешённом REGISTER.
- Опасный MERGE без exact-final-HEAD required CI, user permission или обязательной L3 QA: **BLOCKED**. Release номера не даёт полномочия semantic one-shot, immutable rebinding, retries/recovery, scheduler или production.

**Negative examples:** неверно `final report + открытое UI => UNKNOWN slot`; неверно `непринятый PR => занят`; неверно `active registry => занят`; неверно `не запущен => номер свободен`; неверно `свободный номер => можно merge/запускать semantic worker`.

**Existing CI:** проверить точный final HEAD PR: site task + backlog должны быть GREEN перед директорским merge; сам worker не merge.
**Unresolved:** фактическая открытость чужих UI-окон не наблюдается GitHub; не является release-gate.
**Rollback:** revert одного governance implementation commit/PR; не трогать registry, Board, production или исходные PR; прежний конфликт правил вернётся.
**Recommended next step:** директор сверяет финальный HEAD и оба обязательных CI, затем рассматривает один L1 PR на merge без отдельного L3 QA для этой текстовой правки.
**Efficiency / reusable lesson:** none.
