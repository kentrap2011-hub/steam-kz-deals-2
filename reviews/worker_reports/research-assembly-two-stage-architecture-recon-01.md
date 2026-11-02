# ЧАТ 3 — Research → Assembly: пересмотр двухэтапной архитектуры

**Task:** research-assembly-two-stage-architecture-recon-01  
**Result:** RECON_COMPLETE; CONTRACT_REDRAFT_REQUIRED; IMPLEMENT_NOT_AUTHORIZED.  
**Mode:** READ-ONLY. Разрешённая запись — только этот Markdown в отдельном draft PR.  
**Repository:** kentrap2011-hub/steam-kz-deals-2. **Base main HEAD:** 4bca3f1fda6ee0e941271369408953a1854f9914 (2026-10-21).  
**Главное новое требование пользователя:** Research собирает свободные материалы, Assembly сам проверяет, дополняет, исправляет и оформляет окончательный строгий результат. Неполнота Research не блокирует handoff.

## 1. Вердикт и architecture preflight

**НЕ НАЧИНАТЬ IMPLEMENT НА СТАРЫХ RESEARCH-КОНТРАКТАХ.** Текущая неактивная двухэтапная схема имеет полезный immutable per-game Git transport, GitHub-подготовленные задания, асинхронную независимость и финальную strict V2 Dossier-проверку, но ошибочно требует от первого интеллектуального этапа почти готового досье. Простая адаптация Research к заполненному строгому JSON до передачи в Assembly (предложение PR #234) противоречит новой границе.

1. Владелец scope, group/assignment/order, run-start marker, retry, attempts, validation, receipts, canonical persistence и Deep eligibility — **GitHub**, по config/execution_ownership_contract.json.
2. Текущие config/dossier_two_stage_interfaces_contract.json, dossier_two_stage_staging_contract.json, dossier_two_stage_async_buffer_contract.json, dossier_two_stage_final_acceptance_bridge_contract.json имеют **active=false**, без права на semantic execution/canonical ingest. Канонический production Dossier остаётся **one-stage**.
3. Research и Assembly — только bounded semantic data-plane, без собственного scope/retry/queue/scheduler; данный чат не исполнитель. Новая recurring stage, quota, третья интеллектуальная стадия, ChatGPT-owned backlog запрещены.
4. Прежде чем менять код, нужно версионированно обновить **канонический контракт** относительно Stage-1 Notes V2, автономной Stage-2 проверки и ownership. Сам документ — RECON, не разрешение на реализацию или запуск.

Сохранить решение PROJECT_DECISIONS.md#DOSSIER-ASYNC-001: Assembly после frozen preauthorization читает **точно опубликованный immutable Research Git transport**, не ожидая GitHub Research acceptance, подтверждения предыдущих siblings или свободного слота. Submitted ≠ accepted.

## 2. Аудит доказанных конфликтов

| Точка | Доказанное текущее поведение | Требуемое изменение |
| --- | --- | --- |
| config/dossier_shadow_research_trial_semantic_prompt.md и config/dossier_two_stage_research_semantic_worker_prompt.md | Research обязан заполнить DOSSIER-RESEARCH-PACKAGE-V1, все 12 dimensions, identity/source/feedback graph, выполнить validate_research и physical validator; только потом публиковать | Research должен передавать **любые безопасные читаемые сведения и честные пробелы**, без полной схемы/семантической достаточности |
| config/dossier_research_package_v1.schema.json; scripts/dossier_two_stage_contract_guard.py::validate_research | Полный required assignment/identity/sources/observed_feedback/findings/research_audit, уникальные 12 dimension_survey, cross-refs, identity-role consistency | Строгие проверки **не должны стоять перед Stage 2**. Старый V1 immutable; новый минимальный Notes V2 handoff |
| scripts/dossier_two_stage_staging.py::validate_physical_sources и ::receive_research | Домен, физическая независимость и source roles проверяются уже у Research; accepted_structural_evidence лишь при assembly_ready + resolved identity | Stage-1 gate только безопасное сохранение, точная привязка, parseability и Git-provenance; доменная нормализация/истинность role, достаточность — Assembly/final GitHub |
| scripts/dossier_two_stage_research_worker.py::_validated_bytes | Обязательные strict Research + physical validations перед transport | V2 minimal safety validator; не подменять неполноту фактов technical failure |
| scripts/dossier_two_stage_async_buffer.py::submitted_research_transport / provisional_assembly_work | Асинхронно читает original Research commit/path/blob/raw/canonical SHA, хотя ожидает V1 JSON/assignment | Сохранить цепочку и version-aware envelope, разрешить неполный V2 |
| config/dossier_two_stage_assembly_semantic_worker_prompt.md; scripts/dossier_two_stage_assembly_semantic_worker.py::_check_exact_source_first | Assembly разрешён только named Research gaps, exact source revisit first и узкий one-gap lookup; новый самостоятельный поиск и исправление Research запрещены | **Разрешить самостоятельную проверку любых Research assertions, новый поиск источников, покрытие неуказанных пробелов, substantive correction** по exact product |
| scripts/dossier_two_stage_async_buffer.py::inspect_buffered_assembly_candidate | Повторно вызывает receive_research; rejected/incomplete Research блокирует Assembly chain независимо от качества Stage-2 final. Адаптирует V1 acceptance receipt и проверяет gap_id | Для V2 валидировать safe original transport и независимо строгий финальный Assembly result, **без промежуточной Research полноты** |
| scripts/dossier_shadow_18_assembly_stage_b.py::inspect/build_candidate | Историческое ready = old Research strict pass; build_candidate сверяет final year с Research identity и старую gap модель | Старый immutable путь оставить; V2 sandbox successor version-aware и не обязан повторять ошибочный Research year |
| scripts/taste_steam_review_dossier_strict.py; scripts/taste_steam_review_dossier_buffered.py; scripts/dossier_two_stage_final_acceptance.py | Итоговая строгая V2-проверка, original atomic 3-game group acceptance и shared canonical writer | **Не ослаблять**. Только после независимой Assembly проверки и strict final ingest (позднее отдельно разрешённого) |

GitHub Actions: .github/workflows/validate-dossier-shadow-research-trial.yml, validate-dossier-shadow-research-publisher.yml, validate-dossier-shadow-18-real-assembly.yml, validate-dossier-two-stage-contract-interfaces.yml, validate-dossier-async-chain-acceptance-qa.yml и validate-dossier-async-final-acceptance-integration.yml — validation/test routes. Оригинальный issue-dossier-shadow-18-assembly.yml — manual workflow_dispatch с sandbox-only guard, но **сейчас не запускать**. Production ingest-taste-steam-review-dossier-checkpoint.yml пишет только в пределах уже существующего taste-steam-review-dossier-canonical-writer. Двухэтапное live ingest не активировано.

## 3. Фактическая исходная история (не новая проверка семантики)

Исторические immutable bindings:
- original baseline: **95a4bf4990a60082ecb3302da5bc7f23b618d93e**
- frozen Research marker: **bb63cc291eba5aa8fc56e2920ef84d131ac28a4f**
- одноразовая Research authorization: **2a726cf6731c0fc1e7bc809474627383c107ef9b**
- frozen original sandbox/Assembly marker: **2c2649fb98322507cd3758ff0ff7992128f94de0**
- исходный Research buffer Git blob: **c8a6b6f515162f431c0e3d86175376114c0acf7e**
- подтверждённый real read-only old Python inspect: GitHub Action [39413937596](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596): **12 ready, 2 research_transport_invalid, 4 research_not_submitted**. Статус ready **не** доказывает качество фактов.

- **SULFUR / 2124120:** identity_source_refs включает rsource-002, помеченный evidence_role_hint=current_state (не identity); старый validate_research отклоняет. Нельзя автоматически менять смысл current_state на identity; Assembly ищет настоящее identity evidence либо возвращает unresolved. Объём качественно достаточных сведений неизвестен.
- **Sifu / 2138710:** locator https://www.sifugame.com/news, stored domain www.sifugame.com, но physical validator канонизирует к sifugame.com; это **техническая** ошибка нормализации, а не доказательство отсутствия факта. Сохранить отдельно substantive original-work **2022** vs old baseline **2023**; сопоставление требует самостоятельной evidence-based проверки Assembly, не принудительного равенства.
- **1508750, 1607130, 1849000, 1857090:** нет original Research Git transport; причины, наличие прошлой попытки или tool failure **неизвестны**. Старый marker/authorization нельзя переиспользовать.
- **PR #234** (HEAD 4ec133977895962517a7fb0b99b5882ac184feb7) подтверждает проблемы и предлагает deterministic adapter с заполнением строгого Research JSON V2 и полным intermediate validator. Это **не утверждённая** архитектура; такой обязательный adapter фактически создаст прежний Stage-1 completeness gate.
- **PR #232** (HEAD 9b8535f406c9f22de319156e5f568d0981f5140f), draft/unmerged. [Независимый QA: CHANGES_REQUIRED](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232#issuecomment-6291021685): after first publish current sandbox inspect превращает published item из ready в candidate_already_submitted, а verifier ошибочно строит immutable typed branch order из **сократившегося** ready list; второе publish может быть ложно отклонено. 8 green CI не покрывают этот сценарий. Дополнительно username regexp не доказывает реальные независимые reviewer appointments. Никакой merge/launch до исправления и нового QA.

## 4. Новая точная граница этапов

**Stage 1 — сбор материалов, не финальное решение.** Один GitHub-assigned AppID: свободные нейтральные заметки об игре, gameplay positives/negatives, наблюдённые URL/public refs, фактические даты или null, тип доступа/видел ли страницу/только search result, противоречивые версии, unknowns и пробелы. Может быть одна заметка без ссылок и без установленного original year. Ни заполнение 12 финальных dimensions, ни fixed source/review quota, ни assembly_ready, ни исчерпание маршрутов не являются handoff requirement. Не выдумывать visited links/facts, не переносить raw player quotes/идентифицирующие сведения.

**Stage 2 — собственная интеллектуальная проверка.** Получить Stage-1 notes как **наводки**, а не как доказанную истину; проверить исходные утверждения/источники; заново выяснить identity/year/edition, исправить ложные refs/roles/physical aliases, самостоятельно искать недостающие negative/positive player findings и 12 coverage dimensions, Russian/temporal evidence даже без заявленного research gap; добавлять новые безопасные источники; строить strict final Dossier V2. При необходимости точечно возвращаться к исходному источнику; но **не ограничивать** independent discovery требованием exact source revisit, когда источник отсутствует/сломан/противоречив или не покрывает вопрос. Действительно недоступный источник ≠ доказанная пустота; search-hit/professional page/aggregate ≠ inspected player feedback.

**GitHub:** Stage-1 отвечает только за safe readable bound transport, Stage-2 — за все содержательные и форматные проверки финального результата, GitHub повторно строго валидирует Stage-2 submission и лишь потом (при отдельной activation authority) original atomic 3-game group writer. Никакой третьей семантической стадии. Mechanical serializer, URL normalization, digest validator или state ledger — технические GitHub functions, не самостоятельный интеллектуальный gate.

## 5. Простая передача Research Notes V2 (предложение контракту, не действующая схема)

**Новое имя:** DOSSIER-RESEARCH-NOTES-V2; новая isolated nonproduction namespace; исторический DOSSIER-RESEARCH-PACKAGE-V1/bytes/markers не менять.

Один UTF-8 JSON *envelope*, но **содержимое свободное**:
- schema, schema_version=2;
- assignment: точные GitHub-frozen AppID/title/edition/group_sequence/item_index/assignment_id/snapshot/trial/marker/prompt/contract references (worker только повторяет, GitHub сверяет);
- notes_text: свободный краткий нейтральный текст, включая сомнения/противоречия; допустима честная формулировка «не удалось получить подтверждённых сведений» — но нельзя объявлять совершённой несуществующую попытку;
- source_log: **может быть пустым**; при наличии записи (safe public HTTPS URL или safe public_ref, opened/inspected_collection/search_result_only/unvisited_reference/unknown, фактическая date|null, concise source/observation claim). Способ сбора и реальная независимость от другой страницы не выдумываются;
- unknowns_text / conflicts_text: свободные nullable notes (опциональны);
- research_status: информационный notes_recorded / limited_evidence / no_verifiable_findings / tool_interrupted (если подтверждено), **не** Stage-2 readiness.

Minimal first boundary check: корректный UTF-8/JSON, разумные size limits и safe free text, **только настоящий AppID/assignment frozen equality**, safe public locators, absence of personally identifying author/account/profile URL, snippets/quotes/raw reviews and private tokens, original single-added create-only Git commit/path/blob/raw digest, parent marker and exact work provenance. Не применять к Notes V2: 12-dimension count, role/reference semantic joins, Russian existence requirement, observed feedback count, original work-year resolution, source sufficiency, old completeness enum, final Dossier strict schema. Если source_log пуст, это не основание не передать Stage 2. Не подставлять фиктивные normalized locators, sources, years, dates, author identifiers или якобы выполненные веб-просмотры.

Provenance semantics: Stage 1 reports **worker-claimed** inspected/search status; только Stage 2 после собственного доступа может подтвердить observation и приписать источник финальному результату. Transport acceptance **не подтверждает истинность** исследовательских тезисов.

Assembly handoff читает exact original introduction Git SHA/path/blob/raw SHA256, source Notes V2 bytes, expected prepared assignment, marker/nonce и Assembly frozen plan. Не ждёт Research accepted receipt. Safe, sparse notes — **передать**. Malformed bytes, wrong AppID, stale marker, private URL, wrong identity Git chain — **block only that item as transport/safety**, без фиктивного semantic failure. Отсутствующий файл — research_not_submitted/unknown attempt, а не «неполный Research». Если понадобится Stage-2 запуск без Stage-1 transport вообще, сначала отдельным контрактом разрешить **новый честный empty-material preauthorization**, а не имитировать опубликованный Research и не переписывать историческую попытку.

## 6. Финальный Assembly и ограниченное самоисправление

Version-aware Assembly input/result wrapper должен ссылаться на Notes V2 и точно указать GitHub-owned marker/plan/source raw bytes и newly independently confirmed evidence; старые V1 historical artifacts по-прежнему разбираются старым контрактом.

Убрать из V2 обязательную связь каждого supplemental_operation с существующим research_audit.unresolved_gaps[].gap_id и запрет broad independent fact-checking. Вместо этого прозрачно логировать безопасные виды работы: source_revisit / independent_discovery / targeted_gap_lookup / identity_disambiguation / conflict_resolution / technical_normalization / result_self_correction с причиной и фактами реального доступа. Все final observations должны проходить прежние privacy, physical identity, parent/child, exact AppID/title, historical/current evidence, Russian/source and strict V2 validators. Не превращать search-result representation в firsthand review.

Assembly может в **рамках одной назначенной попытки** проверить черновик и исправить до **2** механических format/reference errors перед единственной create-only публикацией; это предлагаемый явный лимит, не бесконечный retry. При обнаружении новой смысловой нехватки источников Assembly самостоятельно исследует вопрос в рамках bounded invocation, не возвращая задачу в Research. Невозможность собрать настоящие обязательные факты, semantic contradiction, unavailable source, runtime/tool failure — отдельный честный typed terminal outcome. Нельзя переписывать уже опубликованную версию, создавать alternate path или самому авторизовать reattempt.

**SULFUR:** Stage 2 вправе найти true identity corroborator или оставить unresolved; не менять role без основания. **Sifu:** Stage 2 приводит verified final hostname к канонической форме и отдельно проверяет original-work 2022/old 2023 с фактическими sources; может исправить неверный Research year в final result, сохранив old evidence and diff. Ни один old V1 Research field не становится неоспоримым Final authority.

## 7. Виды отказов и GitHub receipts

| Код/класс | Действие |
| --- | --- |
| safe_incomplete_research | **handoff PASS**; Stage 2 проверяет/ищет недостающее. Не считать semantic failure или reason for Research retry. |
| missing_research_transport | Нет real submitted bytes; Stage-2 semantic attempt=0; exact item local stop/continue siblings, no invented Research attempt. |
| wrong_binding / broken_git_provenance / unsafe_material / unparseable | zero Stage-2 semantic attempts, independent transport/security quarantine; preserve exact verified diagnostic and source Git provenance. |
| assembly_missing_evidence | Stage 2 не нашёл достаточных player/identity/temporal фактов после bounded examination: real semantic insufficiency, not Research rejection. |
| assembly_semantic_conflict | Не устранён wrong product, conflicting supported original year, fake review/source independence: item-local terminal, no fabricated complete result. |
| assembly_technical_error | Исправимые wrapper/refs/normalization — max 2 same-invocation corrections; затем typed technical terminal. |
| runtime_or_tool_interrupted | Не приравнивать к exhaustion; attempt state only if independently observed. |
| final_strict_or_group_rejected | GitHub rechecks final V2/chain and original three-game group, quarantine failed item/group; **no canonical Dossier/Deep acceptance**. |

Append-only versioned GitHub receipt per trial/assignment/AppID/stage: frozen original group/index, marker/plan/source/target Git SHAs, raw digest, real authorization and run identity if attested, validation code and detail, published path, actual semantic attempt confirmed/unknown, GitHub timestamp, old/new lineage. No invented zero-attempt inference from absence; no automatic retry, queue expansion, new scheduler, group reshuffle or three-member partial accept. Immutable candidate **submitted is never accepted**.

## 8. Те же исходные 18, тот же порядок

| Group | Original ordered AppIDs |
| --- | --- |
| g3 | 1508750, 1517180, 1533420 |
| g8 | 1590230, 1599600, 1607130 |
| g13 | 1849000, 1857090, 1868140 |
| g15 | 1999170, 1999360, 2009010 |
| g18 | 206420, 2067050, 2076140 |
| g20 | 2124120, 213610, 2138710 |

Не сокращать выборку до 12, не менять замороженные original six triples, marker, one-shot Research authorization, source baseline, old JSON/candidate paths, sandbox branch и исторические Git blobs. Для нового реального прогона требуется **отдельный** versioned isolated namespace, GitHub-issued new immutable assignments/marker + authorization, ссылка-хэш на original baseline/18 manifest, explicit user launch и независимый real A/B/C identity/quality review. Две стадии должны пройти исходную очередь без ожидания других siblings. Каждая из 18 строк получает validated Stage-2 final **или конкретный доказанный unresolved/transport/runtime/semantic reason**. Финальное принятие одной группы только при трёх валидных original members, остальные группы независимы.

## 9. СЛЕДУЮЩЕЕ ТЕХНИЧЕСКОЕ ЗАДАНИЕ РАЗРАБОТЧИКУ

**Suggested task:** WORKER_TASK_RESEARCH_ASSEMBLY_NOTES_V2_AUTONOMOUS_ASSEMBLY_IMPLEMENT_01.md — **новый developer worker после решения директора**. Не воспринимать RECON как разрешение на старт.

1. **CONTRACT FIRST.** Новая versioned Notes V2 schema и минимальный handoff contract; изменить/расширить только inactive two-stage interfaces/staging/async-buffer/receipt/ownership bindings. Прямо запретить Stage-1 strict Research readiness. Сохранить historical V1 parsing/immutable origin; final Dossier V2 strict remains unchanged. Описать однозначно classification/attempt/recovery semantics и отсутствие no-Research-input substitution.
2. **Research V2.** Future one-shot prompt/producer в config/dossier_two_stage_research_semantic_worker_prompt.md и scripts/dossier_two_stage_research_worker.py (либо versioned siblings), sandbox scripts/dossier_shadow_research_trial.py successor: GitHub-assigned frozen scope, arbitrary safe research notes, source provenance/unknowns, create-only introduction, minimal privacy/transport safety, no extra identity/year/sufficiency gate.
3. **Handoff and ingestion.** scripts/dossier_two_stage_async_buffer.py::submitted_research_transport/provisional_assembly_work/inspect_buffered_assembly_candidate, scripts/dossier_two_stage_staging.py and dedicated receipts: raw/blob/lineage V2 version switch, sparse Stage-1 PASS, reject unsafe/wrong binding, eliminate V2 acceptance dependency on receive_research accepted_structural_evidence; item-local isolation, original group order, future existing writer compatibility. Никакой промежуточный V1/strict Research serializer.
4. **Autonomous Assembly.** Amend/version config/dossier_two_stage_assembly_semantic_worker_prompt.md and scripts/dossier_two_stage_assembly_semantic_worker.py; sandbox scripts/dossier_shadow_18_assembly_stage_b.py successor. Independently verify/augment facts, new source operations without predeclared gap ID, restore correct original-work evidence, neutral negative/positive coverage, source provenance, safe V2 output, max 2 self-corrections and typed terminal statuses. GitHub final strict Dossier/group validation remains final authority.
5. **PR #232 compatibility.** Preserve GitHub Actions artifact/owner comment/CAS and single-add typed Git proof, but compute immutable typed publication order from frozen original 18 manifest, **not** current changing ready list. Test publish(1517180) then publish(1533420) with first transitioned to candidate_already_submitted, plus duplicate/invalid negatives. Explicit V1/V2 versioning; verify actual independent reviewer identities, not just regex. **Do not merge present #232 without updated QA.**
6. **Isolated CI.** Add/update only PR read-only validation jobs in .github/workflows/validate-dossier-two-stage-contract-interfaces.yml, validate-dossier-async-assembly-semantic-worker.yml, validate-dossier-async-chain-acceptance-qa.yml, relevant sandbox fixture validators. No production workflows, data/cache, site/UI, Fast/Deep/ranking or Scheduled Task changes.

### Minimum deterministic tests (no live Research, web research or production writes)

- **Positive sparse** Notes V2: correct AppID, free notes/no date/no year/no source/no 12 dimensions, unknown conflicts → handoff PASS; Assembly attempts independent investigation.
- **SULFUR** current_state mislinked as identity → transport PASS; Assembly must seek actual identity source or output unresolved, never silently promote.
- **Sifu** www domain → safe handoff; canonical normalization on final output plus independent 2022/2023 work-year adjudication.
- Russian unknown, no named research gaps, missing/invalid linked page, wrong-product DLC/port/sequel, unobserved search hit, duplicated physical aliases, old-vs-current assertions → Stage 2 audits or returns typed insufficiency, does not invent source/date/review.
- Unsafe public Git payload: private/localhost IP URL, credentials, profile-scoped locator/SteamID/author hashes, raw quotes/player bodies, huge bytes, invalid UTF-8/JSON, wrong AppID/title/assignment, wrong nonce/marker/hash/source Git parent, overwritten path, multiple-file introduction → safe no-handoff **failure**, never partial accepted.
- Tool interrupted vs evidence missing vs semantic conflict vs technical final output failure vs bounded same-invocation correction → distinct typed outcomes; no automatic retry or claim of semantic exhaustion.
- A incomplete/B complete/C missing Research in frozen group → Assembly A and B runnable independently (if safe transport), C zero-attempt local hold; another fully valid group unaffected, original 3-game final acceptance atomic.
- Fixed two-publish typed-history regression from PR #232; duplicate/modified marker and unsupported authorization hard rejects.
- Entire **18 exact AppIDs / six group order** preserved in manifest, original hashes/pins untouched, 18-row disposition ledger, only existing writer can accept final Dossier after 3 strict members.
- All current one-stage, Fast/Deep, ranking, production state and schedules unchanged by PR; inactive activation flags remain false.

**Definition of done IMPLEMENT:** new contract+versioned source+adversarial synthetic tests, exact PR HEAD CI, independently attested QA **PASS** covering sparse-Research handoff + independent Assembly + PR #232 double-publish; nonproduction 18-item manifest/provenance ledger. Successful commit/CI alone ≠ real-semantic quality, live activation or full 18 completion. Separate Director+user permission for fresh real Research and Assembly, separate independent QA and source-quality A/B/C, then an entirely new shadow run.

## 10. Risks, unknowns, next authority and references

**Confirmed:** original structural 12/2/4, exact invalid defects, four missing transport paths, current V1 Research strictness, current Assembly named-gap restriction, current inactive final strict bridge, PR #232 QA blocker. **Unknown:** original worker attempts for four missing games, quality of the twelve ready, current real-world availability of linked sources and whether new Stage-2 semantics can finish all games. **Proposed only:** Notes V2 envelope, expanded Stage-2 browse rules, max-2 local corrections, receipt taxonomy, new isolated namespace. All require Director/contract approval.

PR #234's useful mechanical/source classification can inform final serialization, **not** install strict intermediate Research adapter as a third gate. New semantic V2 work and recovery require new authority; no migration of old one-stage canonical Dossier, no producer/scheduler activation, no merge PR #232/#234 by this audit.

Primary sources:
- [Task](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/WORKER_TASK_RESEARCH_ASSEMBLY_TWO_STAGE_ARCHITECTURE_RECON_01.md); [ownership](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/execution_ownership_contract.json); [two-stage interfaces](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_two_stage_interfaces_contract.json); [async buffer](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_two_stage_async_buffer_contract.json).
- [Original Research schema](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_research_package_v1.schema.json); [guard](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/scripts/dossier_two_stage_contract_guard.py); [staging](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/scripts/dossier_two_stage_staging.py); [async chain](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/scripts/dossier_two_stage_async_buffer.py).
- [Research prompt](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_two_stage_research_semantic_worker_prompt.md); [Assembly prompt](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_two_stage_assembly_semantic_worker_prompt.md); [frozen 18 pins](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_shadow_18_github_python_handoff_pins_v1.json).
- [Final strict validator](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/scripts/taste_steam_review_dossier_strict.py); [final bridge](https://github.com/kentrap2011-hub/steam-kz-deals-2/blob/main/config/dossier_two_stage_final_acceptance_bridge_contract.json); [PR #233](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/233); [PR #234](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/234); [PR #232 QA](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232#issuecomment-6291021685).

**No work executed:** 0 Research, 0 Assembly, 0 issuer/publish Actions, 0 production/code/workflow/queue/Scheduled Task modifications. Read-only GitHub content/PR inspection; Python validator and live source quality **not** re-executed. Only report-only draft PR creation allowed.

**Time/context hygiene:** time spent reading actual prompts, schema/validators, frozen history, workflows and PR QA; future workers can follow PROJECT_ROUTES.md lines 513–542 and references above instead of rediscovering old JSON. Route/pitfall updates should be a separate bounded task because this RECON permits exactly one report.
