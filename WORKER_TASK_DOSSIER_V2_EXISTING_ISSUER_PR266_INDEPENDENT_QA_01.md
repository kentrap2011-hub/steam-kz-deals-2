# ЧАТ 2 — независимый QA адаптации существующего Dossier V2 issuer, PR #266

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v2-existing-issuer-pr266-independent-qa-01
Worker slot: НОВЫЙ физический ЧАТ 2
Implementation PR: #266
Implementation exact HEAD at registration: 1d46b84aff35feee0aca68fc8ad9f3154a330036
Mode: independent read-only QA + own report-only draft PR; NO code edits, no self-merge

## START / source of evidence

Полностью прочитай актуальный CHAT_PROTOCOL.md; выполни START gate и **ограниченный** architecture preflight. Проверь эту задачу из current main, адресный элемент config/director_task_plan.json и текущую верхнюю секцию DIRECTOR_TASK_BOARD.md. Не перечитывай исторические Board/registry целиком.

Проверь live PR #266, точный HEAD, changed-file list и существующие CI на ЭТОМ HEAD. Если HEAD отличается от указанного, отметь stale binding и не аттестуй старую ревизию; получи новую точную привязку от директора.

Источники: PR #264 (доказательная реконструкция реально существовавшего GitHub issuer V1), принятые PR #239/#243 и их ограниченные контракты, отчёт разработчика в PR #266; точные затронутые scripts/config/workflows/tests. Не проводить общий аудит Dossier или Deep.

## Independent verification — основные риски

1. **Изоляция изменений**: изменение только ожидаемых семи файлов. Нет новых GitHub workflows, CI/Actions/checks/validators/schedules; два редактируемых workflow — только прежде существовавшие ручные publisher/feasibility, V2 default-off. Нет изменений site/Deep/Fast, production, исторического V1.
2. **V1 must remain unchanged in effect:** ручные legacy inputs/defaults, publisher freeze, nonce marker, original strict authority gate, parent/first-attempt, separate Research feasibility authorization, one-use, source/provenance, create-only Git ref leasing и fail-closed при отказе. Проверяй реальную backward compatibility не только по утверждению worker.
3. **V2 fail-closed:** contract active=false, authorized_for_semantic_execution=false, authorized_for_canonical_ingest=false, production_enabled=false. Нет успешного V2 freeze/authorization при отсутствии отдельного будущего human grant, trusted actor/GitHub run proof, точного main/ref и явно разрешённого V2 mode. UI/PR/ChatGPT text/commit author не могут быть самостоятельной выдачей прав.
4. **V2 grant/provenance:** new namespace/branch, exact pinned original 18 AppIDs and six 3-game groups, title/edition/assignment digest and V1 blob pins; оригинальные historical marker bb63cc29 / feasibility 2a726cf6 или старые nonce/permissions НЕ могут быть переиспользованы как новая власть.
5. **Security adversarial cases:** missing/revoked/grant mismatch, malicious or impersonated Github actor, wrong workflow run attempt/ref/main, wrong marker parent or nonce, modified manifest/replaced blobs, duplicated/replayed approvals, second marker/authorization, concurrent remote update/lease race, failed push before remote check, extra hidden tree changes, bypass via workflow version default or direct CLI.
6. **Independent tests:** run/review only *existing* corresponding local offline/disposable Git tests where available. Verify developer's 46-case run claim and all relevant existing GH Actions checks on exact FINAL HEAD. Distinguish synthetic tests and actual historical provenance; no real V2 dispatch execution is authorized.
7. **Missing downstream gates:** Research/Assembly, durable per-item receipts, independent reviewer appointment, source-quality and group writer remain separately blocked. PR #266 cannot be relabeled as live trial authorization or full V2 readiness.

## Deliverables / permissions

If proven blocking regression/security issue: `CHANGES_REQUIRED`, cite precise path/test/rule and minimum correction for Chat 1; do not edit its branch.
If clean on reviewed HEAD: `PASS_FOR_DIRECTOR_MERGE_REVIEW`; not automatic permission to launch Research/Assembly or activate V2.
Publish short independent report `reviews/worker_reports/dossier-v2-existing-issuer-pr266-independent-qa-01.md` via own **report-only draft PR** and a concise linked review comment on PR #266; include exact reviewed SHA, test/CI facts, unresolved residual risks and file whitelist. No implementation edits or merge.

No real `workflow_dispatch`, issuer freeze/approval/marker, semantic Research/Assembly, production, Deploy, new CI/Actions/validators/automations, permission bypass or Scheduled Tasks.
