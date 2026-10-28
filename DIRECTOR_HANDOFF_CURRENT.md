# DIRECTOR HANDOFF — CURRENT

Repository: `kentrap2011-hub/steam-kz-deals-2`
Source of truth: `main`

## СВЕЖАЯ ПЕРЕДАЧА НОВОМУ ДИРЕКТОРУ — 2026-10-28 (ЧИТАТЬ ТОЛЬКО ЭТОТ БЛОК, ДАЛЕЕ АДРЕСНО)

**Предыдущий директорский чат выведен из дальнейшей проектной работы из-за лимита контекста и повторных ошибок нумерации.** Новый физический директорский чат начинает со свежего main, читает `CHAT_PROTOCOL.md`, выполняет START gate в Director mode, читает `DIRECTOR_PROTOCOL.md`, текущий верх `DIRECTOR_TASK_BOARD.md`, `DIRECTOR_BOOTSTRAP.md` и только этот верхний блок handoff. `config/director_task_plan.json` проверять по точным IDs; не сканировать все 139 задач или 90+ KB исторических разделов. Историческая инструкция ниже от 2026-10-27 «в первом ответе подготовить Dossier V2 freeze» УСТАРЕЛА: оригинальные 18 уже реально прошли isolated Research/Assembly, не повторять их.

**Первая реплика нового директора:** ответить на ещё оставшийся вопрос пользователя: задачи только **зарегистрированы в GitHub**, ChatGPT не пересылает сообщения в другие физические беседы автоматически. Правильные и окончательно сохранённые в main номера после принятого PR [#334](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/334): **НОВЫЙ ЧАТ 1** — адресная доработка Dossier V1 прямо в открытом PR #322; **НОВЫЙ ЧАТ 2** — адресная доработка Progressive Fast/Deep прямо в открытом PR #323. НЕ использовать предыдущие варианты с новыми ЧАТАМИ 2–3, 10–12 или старые физические 7–8. Два запуска независимы; пользователь ещё не подтвердил, что новые ЧАТЫ 1 и 2 созданы/запущены. Не утверждать «работают» без его сообщения или свежих следов GitHub. В первом ответе вывести ДВА коротких копируемых launcher'а с точными именами ниже, **не создавать заново задания и не менять номера**.

**Канонический запуск НОВОГО физического ЧАТА 1:**
```text
ЧАТ 1 — исправление конфликта ручного Dossier V1.

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Работай только в указанном репозитории.

Сначала прочитай CHAT_PROTOCOL.md и выполни START gate.

Затем полностью выполни:
WORKER_TASK_DOSSIER_V1_PR322_FROZEN_ROLLOVER_COLLISION_REPAIR_01.md
```

**Канонический запуск НОВОГО физического ЧАТА 2:**
```text
ЧАТ 2 — исправление оставшихся ошибок коммерческой проверки Fast/Deep.

Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Работай только в указанном репозитории.

Сначала прочитай CHAT_PROTOCOL.md и выполни START gate.

Затем полностью выполни:
WORKER_TASK_PROGRESSIVE_DEEP_PR323_COMMERCIAL_GUARD_TARGETED_REPAIR_01.md
```

**Точная история последних директорских решений:**
- [#325](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/325) — независимый повторный аудит ошибок нумерации ЧАТА 9, принят; [#333](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/333) — внедрены раздельные read-only CHAT_AVAILABILITY и запрет вывода «физический чат свободен» по GitHub статусу задачи. [#334](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/334) — исправил оставшуюся бронь ЧАТА 1: первоначальная физическая беседа ЧАТ 1 завершена пользователем; дальнейшая Steam post-merge Actions задача зарегистрирована, но не подтверждена как запущенная, поэтому её `worker_slot=null` при `status=active`, задача НЕ отменена. Новая пара PR-ремонтов получила номера 1 и 2.
- [#329](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/329) и [#330](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/330) — принятые независимые QA отчёты, оба **CHANGES_REQUIRED**. PR #322 (manual Dossier) исправить только в исходной branch/PR: конфликт candidate+terminal на frozen old-snapshot при двух markers; добавить fail-closed карантин и targeted disposable-Git тест, потом independent L3 **только материальной дельты**. Не разрешать ручной one-shot до принятого L3. PR #323 (Fast/Deep) исправить в исходной branch/PR: `USD100`/`RUB100`, смешанные Cyrillic/Latin буквы в коммерческих токенах, лишний workflow_dispatch и посторонний CURRENT_TASK.md; сохранить исправление «грубую», историю попытки 1261040 не replay. Затем независимая QA только новой дельты; никаких новых implementation PR.
- [#324](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/324) и [#331](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/331) — принятые аудит и диагностика реального Dossier V2 original18: **14 sandbox dossiers, 4 не приняты** (3 недостаточная evidence + 1 invalid), NO_GO production. `206420` исторические observations без обязательной historical/current-state evidence; `1607130` operation access вне схемы; `2124120` SULFUR pre-1.0 evidence. Не повторять исходные 18, не размывать strict validator, не создавать новые semantic attempts/recovery без отдельной авторизации. V2 remains isolated/non-production.
- [#319](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/319): отдельный audit длинных запусков директора существует как report-only draft, не путать с #325; задача `director-recurrent-long-prompts-slow-registration-audit-01` за историческим ЧАТ 5. Не запускать его повторно без основания.
- Steam: PR #311 и #312 merged 27.10; ограниченная нерешённая задача `steam-postmerge-actions-failures-fix-01` (две конкретные main workflow ошибки после merge) остаётся **active, без назначенного worker_slot**, не потерять её и не считать физический ЧАТ 1 занятым по этой записи. Разобрать отдельно после нынешних приоритетов/по решению пользователя.

**Source of truth и дальнейшее управление:** актуальный main при начале handoff после #334 — `a38fa50d175bea848c0cc6f5beea2fd566022509`; после принятия этой передачи SHA снова изменится, всегда обновлять точный SHA. Регистр 139 task items (до этой передачи). `DIRECTOR_HANDOFF_CURRENT.md` ниже содержит архивные секции с устаревшими утверждениями об отсутствии V2 Research и не является authorization; `DIRECTOR_BOOTSTRAP.md` ниже также содержит старую историю, её игнорировать. Для статуса проверять PR HEAD/CI адресно, не называть открытый PR принятой реализацией. Не запускать production, semantic worker, GitHub workflow или Scheduled Tasks, не менять очередь, retries/markers/provenance без явного отдельного полномочия пользователя.

**В конце первой реплики** коротко назвать, что физические чаты должен открыть сам пользователь. Дальше ждать их результатов и принимать по точным Gates; не начинать новую регистрацию и не раздавать другие номера самовольно.

---

## АРХИВНАЯ ПЕРЕДАЧА — 2026-10-27 (УСТАРЕЛА; НЕ ЗАПУСКАТЬ ПО НЕЙ)

**Первая реплика нового Director-чата по прямой просьбе пользователя:** **сразу подготовить копируемый промпт для запуска настоящего Dossier V2 на исходных 18 играх**. Сначала прочесть актуальные `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`, `DIRECTOR_BOOTSTRAP.md`, верх `DIRECTOR_TASK_BOARD.md` и этот свежий handoff; использовать exact текущий `main` и действующий финальный worker-report №309. Не начинать новую разработку, QA-серию или повторение зелёных тестов. В первом ответе дать краткие точные действия владельца (freeze → authorize) и **готовый короткий копируемый launcher первого самостоятельного Research V2 semantic worker** с честными placeholders для действительно полученных GitHub marker/authorization SHA. Затем, когда появятся реальные Research receipts, готовить отдельный launcher Assembly; не подменять его преждевременно фикстурами.

**Dossier V2 original18 — СОСТОЯНИЕ:** PR [#309](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/309) **MERGED** в main `3210d0fd58b9bad687ab8f70d529fdf0535e586b` 27 октября, 10:32 UTC. Включает изолированный оригинальный 18-game launcher, строгий Research/Assembly Git transport с типизированными receipts и existing sandbox writer. Целевые **68/68** в Actions `40462620881` прошли; это синтетическое/изолированное доказательство, НЕ настоящий Research. Реальных Research 0/18, Assembly 0/18, accepted 0/18. `sandbox/dossier-notes-v2-original18-first` отсутствует (404 при проверке этой передачи). `active=false`, `production_enabled=false`, глобальное semantic/canonical разрешение выключено; только однократное scoped V2 испытание в существующем contract. НЕТ доказанного independent final L3 QA report по PR #309 на текущем GitHub; PR #315 лишь зарегистрировал задачу pre-merge review, но №309 уже принят. Не придумывать PASS, проверить необходимый узкий authority gate до манипуляций с живым trial, **без нового общего аудита**.

**Подлинные ручные actions владельца после подготовки команды:**
1. [Freeze original18](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/workflows/publish-dossier-shadow-research-freeze.yml) — выбрать `main`, `issuer_version=v2`, `expected_main_sha=<CURRENT FULL 40-HEX main at time of dispatch>`, `confirmation=FREEZE_DOSSIER_NOTES_V2_ORIGINAL18_ONCE`, один запуск; выписать `marker_commit` из успешного Actions summary.
2. [Authorize original18](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/workflows/authorize-dossier-shadow-research-feasibility.yml) — `main`, `issuer_version=v2`, `expected_main_sha=<CURRENT FULL SHA before second dispatch>`, `original_marker_commit=<REAL marker from freeze>`, `confirmation=AUTHORIZE_DOSSIER_NOTES_V2_ORIGINAL18_ONCE`, один запуск; выписать `authorization_commit` и success run URL. Успех нельзя имитировать кодовым commit или вымышленным GitHub actor. Если интерфейс требует owner action, сказать точные шаги, а не просить ещё раз принципиального согласия.
3. Первый отдельный настоящий Research worker читает `config/dossier_two_stage_research_notes_v2_worker_prompt.md`, принимает только immutable оригинальных 18 и два реальные SHA, публикует create-only документы/receipts через `scripts/dossier_notes_v2_original18_pilot.py research` (либо разрешённый эквивалент GitHub). Если у семантического чата нет реальной GitHub write/identity authority, честно STOP и назвать препятствие, не говорить что Research проведён. Затем **отдельный** Assembly worker по `config/dossier_two_stage_autonomous_assembly_v2_worker_prompt.md` и реальным Research SHA.
4. После реальных per-item receipts владелец один раз запускает [existing checkpoint workflow](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/workflows/ingest-taste-steam-review-dossier-checkpoint.yml) на `main` с `notes_v2_writer=false`, `notes_v2_original18_pilot_writer=true`, `notes_v2_marker_commit=<REAL marker>`, `notes_v2_trial_id=dossier-notes-v2-original18-first`, `notes_v2_item_commits_json=<только подтверждённые реальные Research/Assembly SHA по AppID>`. Результаты только sandbox, не production. Полные точные 2 launcher prompts и CLI contract уже содержатся в `reviews/worker_reports/dossier-v2-original18-real-pilot-end-to-end-route-implement-01.md` из main. **Не переписывать их заново большими сообщениями, дай первую нужную короткую команду.**

**ВТОРАЯ ЗАДАЧА ДИРЕКТОРА: ITAD и Steam совместимость → принятие → штатное обновление сайта.** Независимая совместная QA [#314](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/314): #311 PASS_FOR_DIRECTOR_MERGE отдельно; #312 получил единственный joint-блокер: отсутствие анализа Epic/GOG для Steam AppID вне видимых 100. Старый вывод #314 относится к **старой версии** #312. Существующий ЧАТ 2 уже исправил проблему в том же [#312](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/312), exact HEAD `f27a85d4f6f3c22f682932a64d0026e633d01f60`, regression success включая `test_giveaway_visual_handoff` с анализом ranked #101 через full, giveaway-only и media refresh. Изменения фиксируют заранее посчитанные canonical cards отдельно от capped `ready.items` (без title fallback). **Не отправлять ЧАТ 2 ещё раз переделывать то, что уже исправлено.** Director точечно проверяет новую дельту и совместный файл `scripts/build_final_visual_payload.py` без повторного общего аудита; последовательно согласует/принимает PR №312 и [№311](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/311), №311 пока draft и его tests green. Оба PR НЕ merged на момент передачи. При интеграции сохранить pre-cap complete canonical giveaway evidence и post-rank paid top100 одновременно; при настоящем конфликте точечно исправить combined integration, не создавать новый feature PR.
После принятия двух PR нужен **один нормальный GitHub-owned main Steam collector + downstream site pipeline**, а не PR-only CI; `collect` в PR workflow намеренно skipped. Учесть, что раздельные merge могут **автоматически инициировать два последовательных workflow runs** (concurrency без cancel); сначала проверить уже возникшие запуски и не dispatch третью копию. Проверить реальные KZ >=50%, цену <=4500 KZT, <=100 видимых, весь Deep scope, DLC соответствующих base, независимые discounted bundles, текущие Epic exact ITAD receipts, аналитику/атрибуцию сайта. GOG live giveaway отсутствовал, только диагностический исторический ID (не выдумывать текущий).

**ОТДЕЛЬНЫЙ ФАКТ main CI:** после merge №309 workflow `build` в GitHub Actions [40489230431](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/40489230431) FAIL по `Fresh deal discovery prerequisite failed: discovery_source_older_than_allowed,candidate_universe_not_rebuilt_for_current_production_cycle` (discovery 2026-10-25, commercial 2026-10-27). Другие scope/validate checks pass. Это не доказательство дефекта V2 и не отдельный фоновый QA проект. Предполагается закрывать через нормальный **новый collector run после совместной интеграции**; не считать сайт свежим до подтверждения.

**Распределение и границы:** старые ЧАТЫ 1/2 закончили основную реализацию, 3 — №309, предыдущий ЧАТ 4 — совместную QA №314. Нумерация физических UI-чатов временная; не путать исторические слоты registry с реально открытыми пользователем разговорами. Отдельная новая L3 QA для №309 **зарегистрирована**, но подтверждённый report отсутствует; PR уже merged, не запускать pre-merge поручение автоматически. Новому директору не создавать новый протокол/архитектуру/аудит/очередь; сначала пользовательский запуск Dossier, потом ITAD. Текущий `main` может измениться после этой передачи — считывать свежий SHA именно перед manual freeze.


## НОВЫЙ ЧАТ 3 — РАБОТАЮЩИЙ МАРШРУТ ИСПЫТАНИЯ 18 ИГР, 2026-10-26

- Пользователь разрешил настоящую разовую пробу Dossier V2 на исходных 18 играх (Research → Assembly), а затем поручил реализовать отсутствующий исполняемый маршрут без новых аудитов. **НОВЫЙ физический ЧАТ 3:** `WORKER_TASK_DOSSIER_V2_ORIGINAL18_REAL_PILOT_END_TO_END_ROUTE_IMPLEMENT_01.md`, реализация плюс фактическое испытание, если поддерживаются GitHub dispatch и отдельный user-launched semantic worker; не выдавать тесты за живой запуск.
- #266, #270 и #274 уже в main. Текущие V2 флаги inactive/issuer false; issuer не выполняет Research. Нужен конкретный scoped authority + one-shot semantic handoff + saved GitHub receipts. Текущее подключение GitHub в директорском чате не имеет dispatch action; работать через реально доступные UI, а не имитировать действия.
- ЧАТ 1 завершил отчёт по нумерации в draft PR #306, без правок текущих правил. ЧАТ 3 независим от выбора новой модели director/worker.

## НОВЫЙ ЧАТ 1 — АНАЛИЗ НУМЕРАЦИИ, 2026-10-26

- НОВЫЙ физический ЧАТ 1: `WORKER_TASK_DIRECTOR_CHAT_NUMBERING_CAUSE_AND_REDESIGN_OPTIONS_AUDIT_01.md`. Пользователь запросил самостоятельную диагностику, почему директор выбирает бессмысленные номера и придумывает специализацию чистым чатам. Показать несколько вариантов с плюсами, минусами и рисками без ограничений масштаба, включая полную переработку роли директора, обозначений чатов и хранения задач.
- ЧАТ 2 — пользователь уже запустил упрощение №266; ЧАТ 4 — пользователь уже запустил широкую проверку избыточных QA. ЧАТ 1 независим от них; ЧАТ 3 свободен. Никакие назначения работающих физических чатов не менять.
- Текущие утверждения о статусах PR сверять отдельно с GitHub: исторические записи handoff могут устаревать. Анализ не становится обязательным gate для программных изменений.

## ПОСЛЕДНИЕ РЕШЕНИЯ — 2026-10-26

- ЧАТ 2, НОВЫЙ: `WORKER_TASK_DOSSIER_V2_PR266_REMOVE_EXTRA_FREEZE_PROVENANCE_GATE_01.md`; по явному решению пользователя исключить навязанную внешнюю проверку GitHub freeze-run из будущей выдачи разрешения №266, без реального запуска данных и без отмены ручного grant.
- ЧАТ 4, НОВЫЙ: `WORKER_TASK_DIRECTOR_VERIFICATION_OVERHEAD_OPERATING_MODEL_OPTIONS_AUDIT_01.md`; широкий самостоятельный разбор повторных проверок и вариантов полной перестройки модели чатов/ролей.
- №299 включён в main, имеющийся №270 прошёл 14/14 реальных GitHub тестов без изменения кода после проверки. №300 по-прежнему требует согласования с параллельными director-изменениями, не допускать новой цепочки общего QA. V2 реально не включён.

## ПОДТВЕРЖДЁННЫЕ РЕЗУЛЬТАТЫ — 2026-10-26

- Прежние задания ЧАТОВ 1–3 после №301 завершены: отчёт №302 (№299 PASS/№300 потребовал согласования), №266 с тестами V1/V2, №270 с настоящим GitHub результатом **14/14** + **37/37**. Код №270 не объединён; новая внешняя проверка релиза по действующему правилу остаётся организационным вопросом. №299 уже принят.
- Настоящая проблема №300 была конфликтом одновременного редактирования Board/registry/handoff, а затем DIRECTOR_PROTOCOL при №299. Эта ветка использует актуальный main с принятыми №299 и №303 и переносит только согласованные статусы и простое правило объяснения, не удаляя новые ЧАТЫ 2/4.
- Новый ЧАТ 2 упрощает только дополнительную блокировку подтверждения origin freeze в №266 по явному решению пользователя. Новый ЧАТ 4 независимо сравнивает варианты переработки системы проверок, ролей, PR и реестра. Не запускать настоящий V2 Research/Assembly или production без отдельного разрешения пользователя.

## ИСТОРИЧЕСКАЯ ПЕРЕДАЧА — 2026-10-25 (уже устарела)

**Внимание:** это актуальная управленческая сводка на проверенном `main` 78f5bc3ce28f. Всё ниже секции с датами 2026-10-20 — история. Перед слиянием или новым назначением сверить live PR/CI, верх `DIRECTOR_TASK_BOARD.md` и только нужные записи `config/director_task_plan.json`. Для общих правил сначала `CHAT_PROTOCOL.md`, `DIRECTOR_PROTOCOL.md`.

### Проект

Строим сайт Steam KZ со скидками и персональными рекомендациями. Задача последних чатов — закончить **Dossier V2**: Research собирает сведения о каждой игре → Assembly готовит разбор → существующий писатель GitHub независимо сохраняет готовый результат. Ошибка одной игры не должна задерживать остальные. Историческая первоначальная очередь — **18 игр, 6 троек**, сохранять точный порядок/исходные привязки. Старый Dossier (V1) и production не изменять и не запускать настоящий Research/Assembly без отдельного разрешения.

### Кто чем занимается

- **ЧАТ 1 (разработчик) — закончил.** Draft **PR #274**, HEAD `f7f2f54023acf2d66a8fd54a2888ec1497582781`. Подключил поштучное принятие готового Dossier V2 к прежнему GitHub writer и исправил внутреннее противоречие разрешённого режима (отчёт `reviews/worker_reports/dossier-v2-pr274-enabled-path-contract-fix-01.md`). 8 проверок GitHub зелёные. V2 по умолчанию выключен.
- **ЧАТ 2 (независимая проверка PR #274) — закончил.** Отдельный report-only **PR #284**, HEAD `43f23ef4e78633306957389b5188f55def165212`, отчёт `reviews/worker_reports/dossier-v2-pr274-enabled-fix-final-independent-qa-01.md`: **PASS_FOR_DIRECTOR_MERGE_REVIEW** точно для `f7f2f540...`. 17/17 узких тестов и всего 8 checks успешны; разрешённый V2 режим проходит, без разрешения выключен, A/C сохраняются независимо от неверной B, V1 не затронут. **PR #274 всё ещё draft/open и НЕ объединён.** Тестовый Git не равен настоящей публикации.
- **ЧАТ 3 (независимая проверка Research) — закончил.** Отчёт **PR #282** на код **PR #270**, HEAD `97f30cbfe3285610649c85e96d4ae179644d677e`: **BLOCKED_EVIDENCE**. По коду конкретных ошибок записи промежуточных сведений Research не найдено, но 14 написанных тестов в том чате выполнить не удалось из-за недоступной локальной копии проекта. PR #270 остаётся draft/open.
- **ЧАТ 4 (независимый запуск готовых Research-тестов) — назначен, окончательного отчёта ещё не подтверждено.** Задание `WORKER_TASK_DOSSIER_V2_PR270_EXISTING_TESTS_EXECUTION_QA_01.md`; запустить `python scripts/test_dossier_notes_v2_per_item_receipts.py -v` из PR #270, при отсутствии checkout получить минимум файлов через GitHub-коннектор, **не создавать новый CI**. Проверить свежий отчёт/PR прежде чем считать задачу завершённой. Его работа НЕ повторяет ЧАТ 1: Research Notes ≠ готовый Dossier.
- **ЧАТ 5 (независимая диагностика длинных директорских промптов) — задание зарегистрировано, отчёт ещё не подтверждён.** `WORKER_TASK_DIRECTOR_LAUNCH_PROMPT_LENGTH_DRIFT_DIAGNOSIS_01.md` принят регистрационным **PR #286**. Только выяснить, почему директорам не удаётся соблюдать давно существующее правило короткого запуска; отчёт и одно минимальное предложение, без самостоятельной правки протоколов.

### Ближайшие решения по порядку

1. **Рассмотреть принятие PR #274**: есть точное независимое PASS #284 и 8 проверок на том же HEAD; перед merge перепроверить текущие PR HEAD, mergeability, checks и разрешение пользователя по `DIRECTOR_PROTOCOL.md`. Не повторять разработку или полный QA, если версия не менялась. Принятие неактивного кода НЕ включает V2 и не запускает Research/Assembly.
2. **Получить результат ЧАТА 4 по 14 тестам PR #270**. При успешных тестах и уже пройденной независимой проверке можно решить о принятии неактивного кода #270; если непреодолимый блокер, назвать одну точную причину, не плодить QA круги.
3. **Проверить отчёт ЧАТА 5**, если будет готов. Отдельный draft **PR #275** о понятном языке директора остаётся непроверенным; не смешивать его с причиной разрастания промптов.
4. **Перед живым испытанием 18 игр** согласовать отдельный открытый draft **PR #266** о выдаче Research-разрешений (его QA **PR #269**: CHANGES_REQUIRED), совместимость #266/#270/#274, конфликты с прежним V1-кэшем и передачу в Deep. Не активировать новый Dossier и не запускать реальные семантические стадии автоматически. Отдельно просить явное решение на один настоящий запуск исходных 18 игр.
5. Если нужны новые поручения — сначала зарегистрировать `WORKER_TASK_*.md` + registry + верх Board через GitHub с required checks, затем **всегда давать пользователю очень короткий копируемый запуск**, не повторять содержимое файла. Пользователь прямо жаловался на постепенное удлинение запусков.

### Что сказать пользователю первым ответом нового директора

Кратко, обычным русским: что мы строим; ЧАТ 1 завершил код #274; ЧАТ 2 подтвердил исправление и можно решать о принятии #274; ЧАТ 3 просмотрел Research #270, но тесты не исполнил; ЧАТ 4 должен получить результаты 14 готовых тестов; ЧАТ 5 ищет причину длинных запусков. Затем предложить ближайший порядок: принять проверенный неактивный #274 по правилам, дождаться фактических тестов #270, устранить лишь подтверждённые оставшиеся блокеры, подготовить отдельное разрешение на пробный Dossier V2 для 18 игр. Первое сообщение не должно запускать новые задания или делать merge без надлежащего решения.

---
This is the transfer point for the next Director chat. Read the most recent handoff first; older sections below are historical and may contradict current GitHub state.

**Superseded operational snapshot:** This handoff contains historical statuses through 2026-10-20; it is not a live assignments ledger. For any launch or acceptance, use current `config/director_task_plan.json`, latest Board authorization, exact PR HEAD/CI and the worker task/report. `DIRECTOR_PROTOCOL.md` §10 supersedes every historical two-worker cap in this file.

## DIRECTOR DECISION — 2026-10-20: redesign Research Stage 1 before rerunning all original 18

- **User direction:** Stage 1 semantic Research must concentrate on game investigation and source-supported facts; mechanical technical JSON/IDs/normalization/binding belongs to GitHub-owned deterministic code, without weakening evidence/semantic truth. First audit and fix Stage 1; then execute a separately authorized **new full Research run for the same original 18 games**, preserving original six groups/order and immutable historical records. Do NOT merely patch the six old payloads; do NOT run Research yet.
- **New bounded assignment:** **НОВЫЙ ЧАТ 4** (not launched), `WORKER_TASK_DOSSIER_SHADOW_RESEARCH_STAGE1_TECHNICAL_BOUNDARY_AUDIT_01.md`, Task ID `dossier-shadow-research-stage1-technical-boundary-audit-01`, READ-ONLY architecture recon + contract design, report-only PR allowed. Field-by-field responsibility, failure trace, safe architecture, new immutable namespace/marker/one-shot approval plan, PR232 impact. Developer IMPLEMENT + independent QA must precede new 18-item semantic run.
- **Dependency:** PR #232 prospective Assembly gate and planned ЧАТ 3 multipublish fix are **ON HOLD / do not launch or merge** until Research Stage 1 contract redesign scope/compatibility is known. Existing ЧАТ 2 QA CHANGES_REQUIRED remains valid for current exact HEAD. No Assembly, Research retry, marker reissue, publish or production action authorized by this decision.
- **Existing status:** ЧАТ 1 recon saved in report-only PR #233, two proven technical rejection predicates, four absent transports with unknown attempt history; ЧАТ 2 QA waiting; ЧАТ 3 planned PR232 correction paused. Numbering remains simple unique `ЧАТ N`.

## DIRECTOR VERIFIED — 2026-10-20: ЧАТ 1 six-Research RECON_PARTIAL_BLOCKED

- **Exact GitHub durable result:** [draft report-only PR #233](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/233) OPEN, exact head `d068f57fb983809906da7e7ac1dd805f32042b98`, single new file `reviews/worker_reports/dossier-shadow-18-six-research-gaps-recon-01.md`, no source/test/workflow mutations. [Backlog CI #39425646855](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39425646855) SUCCESS. The worker's report is **RECON_PARTIAL_BLOCKED** because absent-transports' attempt history is not provable from frozen Git; this is a completed bounded inquiry with unresolved historical facts, NOT a reason to run Research again.
- **Two proven Research strict defect predicates:** SULFUR `2124120`, old `identity_source_refs` points to source `rsource-002` tagged `current_state` not `identity`; Sifu `2138710`, `source.domain=www.sifugame.com` mismatches normalized public URL host `sifugame.com`. Original Git introductions otherwise one-add-only. Sifu original work year 2022 versus legacy baseline claim 2023 is a separate comparison discrepancy, **not** proven Research transport rejection reason. Neither package may be overwritten/relabelled.
- **Four absent slots:** `1508750`, `1607130`, `1849000`, `1857090` exact expected frozen transport paths absent, and no original introduction commit; semantic attempt history / non-publication causes **UNKNOWN**. Original fixed 18 membership retained; other 12 `ready` structurally independent and still NOT semantically assembled or canonically accepted.
- **Required next scope (not authorized to execute):** a **new separate GitHub-owned prospective Research six-slot recovery CONTRACT/RECON** determining whether append-only namespace/new marker and explicit item retry permission can coexist with original Stage B immutable trial, or whether an entirely new fixed-same-18 trial is necessary. No Research recovery, extra semantic attempt, Assembly, publish, canonical/cache/production mutation or Scheduled Task authorized by PR #233. Report-only PR should not be merged without separate review decision.
- **Worker numbering:** original **ЧАТ 1** six-gaps inquiry report is saved, no more RECON work required from that physical chat unless specifically assigned; **ЧАТ 2** remains in `CHANGES_REQUIRED` for PR #232 awaiting developer code fix; planned **НОВЫЙ ЧАТ 3** owns PR #232 multi-publish fix if user launches it. Do not confuse with historical PR232 developer formerly labelled ЧАТ 1.

## DIRECTOR OPERATING POLICY — 2026-10-20: no fixed chat limit, retain simple numeric names

- **User choice:** Remove the historical maximum of two concurrent physical worker chats. Updated `DIRECTOR_PROTOCOL.md#10` plus pre-send check in `CHAT_PROTOCOL.md`. Launch 3, 5, 10 or more only for independently owned tasks with separate Task IDs, branches/reports, clear dependencies and GitHub checkpoints. GitHub evidence/independent exact-HEAD QA remain mandatory; this rule is NOT new authorization for semantics, publish, auto-launch, Scheduled Tasks or production.
- **User-facing naming stays simple:** `ЧАТ 1`, `ЧАТ 2`, `ЧАТ 3`, etc., one unique number per concurrently assigned physical dialogue. Status queries `что по чату 2?` resolve against Board + exact GitHub task/PR, not an arbitrary reused same-number physical conversation. Distinguish `assigned/planned` from `user explicitly launched` and from `GitHub report confirmed`.
- **Current slot bookkeeping:** `ЧАТ 1` = **new physical** six-invalid/missing Research RECON (`dossier-shadow-18-six-research-gaps-recon-01`, active/assigned; no proof of execution implied); `ЧАТ 2` = existing independent QA for PR #232, verdict CHANGES_REQUIRED, waiting for developer fix; `ЧАТ 3` = **new physical** PR #232 multipublish regression developer correction, `dossier-shadow-18-pr232-multipublish-prefix-remediation-01`, task prepared **PLANNED / NOT LAUNCHED**. Original finished PR232 physical developer previously called ЧАТ 1 is retired as distinct historical physical conversation; avoid giving two different active physical conversations the label ЧАТ 1.
- **Next:** user may separately launch planned ЧАТ 3 with `WORKER_TASK_DOSSIER_SHADOW_18_PR232_MULTIPUBLISH_PREFIX_REMEDIATION_01.md` from main; until launched no runtime progress is claimed. ЧАТ 2 re-reviews only the new exact-head PR after fix, no automatic merge.

## DIRECTOR VERIFIED QA — 2026-10-20: PR #232 CHANGES_REQUIRED, multi-publish lifecycle

- **Independent exact-HEAD verdict:** existing physical **ЧАТ 2** posted [CHANGES_REQUIRED on PR #232](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232#issuecomment-6291021685) at 2026-10-20T12:38:21Z, reviewed unchanged `9b8535f406c9f22de319156e5f568d0981f5140f`, PR open/DRAFT/unmerged. Eight HEAD CI successes do **not** cover publication 1 -> 2.
- **Blocking root cause:** new `verified_handoff_progress` recomputes expected historical typed prefix from *current sandbox* `inspect.rows where status=="ready"`; after first sandbox `publish(1517180)`, original Stage B marks `1517180` `candidate_already_submitted` and deletes it from the shrinking `ready` list, while valid typed Git history remains immutable. Thus second `publish(1533420)` fails despite correct lineage. Must decouple stable original frozen typed order from mutable per-game publish status and add two-publish end-to-end-like synthetic regression. Secondary: regex-valid A/B/C usernames do not prove actual reviewer identity/appointment.
- **Safe current state:** NO real Assembly, Research retry, candidate, publish, production change or reviewer appointments; PR #232 must NOT merge until repaired and new exact-HEAD independent ЧАТ 2 QA verdict.
- **Director remediation task prepared for NEW ЧАТ 3 (NOT LAUNCHED):** `WORKER_TASK_DOSSIER_SHADOW_18_PR232_MULTIPUBLISH_PREFIX_REMEDIATION_01.md`, task `dossier-shadow-18-pr232-multipublish-prefix-remediation-01`, status `planned`, destination **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 3**, dedicated PR #232 developer correction. Other unique active labels: ЧАТ 1 six-Research RECON; ЧАТ 2 independent QA. No fixed two-worker cap; no branch conflict, no QA acting as developer.
- **Next step:** original developer fixes PR #232 on existing branch; await exact-new-HEAD CI and re-review by SAME existing QA ЧАТ 2; only after independent PASS Director evaluates merge. Six-game Research recon may continue independently and does not authorize retries.

## DIRECTOR PARALLEL TASK — 2026-10-20: NEW ЧАТ 1 read-only diagnosis of six Research gaps

- **User requested new work for ЧАТ 1, independent of PR #232 QA.** By `DIRECTOR_PROTOCOL.md` one finished task = retired physical worker; destination **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1**, not the closed original PR #232 developer conversation. Task `WORKER_TASK_DOSSIER_SHADOW_18_SIX_RESEARCH_GAPS_RECON_01.md` (`dossier-shadow-18-six-research-gaps-recon-01`), mode **READ-ONLY / RECON** with optionally ONE report-only branch/draft PR, otherwise final evidence. Expected report `reviews/worker_reports/dossier-shadow-18-six-research-gaps-recon-01.md`.
- **Exact six:** original submitted invalid SULFUR `2124120` and Sifu `2138710`; unsubmitted `1508750`, `1607130`, `1849000`, `1857090`. Existing original read-only `inspect` [#39413937596](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596) proves 18 original rows, 12 ready / 2 transport-invalid / 4 not submitted; generic origin/binding diagnostic does **not** prove why. Worker must establish item-level evidence, unknowns and authorized future remediation path, NOT run Research or mutate frozen data. Strict original one-shot no retry and historical Research authority remains.
- **Parallel isolation:** PR #232 remains unmerged and is under independent exact-head QA by the existing physical ЧАТ 2; no QA verdict is assumed or preempted here. No overlap: ЧАТ 1 only original Research diagnostic, no source/config/workflow/developer PR edits; ЧАТ 2 independently reviews PR #232 and must not incorporate an unaudited new source patch. No real semantic Assembly, canonical ingest, production or Scheduled Tasks.
- **Director next:** inspect exact six-item report and independent PR #232 QA separately; plan bounded recovery **only** if original contract permits and user separately authorizes. Don't infer missing attempts or retry permission.

## DIRECTOR NEXT ACTION — 2026-10-20: ЧАТ 1 COMPLETE; assign ЧАТ 2 exact-head QA of PR #232

- **ЧАТ 1 developer done:** [draft PR #232](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232) open/unmerged, HEAD `9b8535f406c9f22de319156e5f568d0981f5140f`, 19 commits, 11 changed files, no conflict. Real source PR comment [final CI report](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/232#issuecomment-6290844977) states `PR_READY_FOR_INDEPENDENT_QA`. **Eight same-HEAD CI workflows all SUCCESS**: `39422164552`, `39422164712`, `39422164495`, `39422164500`, `39422164690`, `39422164560`, `39422164775`, `39422164796`. Main remains unaffected by developer branch. No real Assembly, GitHub `publish`, new marker or scheduled task.
- **ЧАТ 2 independent preflight done:** separate [report-only draft PR #231](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/231) `PREFLIGHT_READY_FOR_PR_QA`, **NOT** code QA / live semantics approval. Report branch `report/dossier-shadow-18-independent-execution-preflight-01`; one Markdown report, no source code changes.
- **Assignment RIGHT NOW:** **СУЩЕСТВУЮЩИЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2**, using its existing `WORKER_TASK_DOSSIER_SHADOW_18_INDEPENDENT_EXECUTION_PREFLIGHT_01.md` as baseline and original independent preflight findings, perform new bounded **READ-ONLY developer PR #232 exact-head security/contract review**. Check every changed path, negative authority, original immutable marker, reviewer appointments gate, GitHub run/artifact authenticity, exact 18/12/2/4, typed first-ref/append-only order, per-AppID human publish and production isolation. Post complete `PASS_FOR_DIRECTOR_MERGE_REVIEW` or `CHANGES_REQUIRED` with findings + evidence in GitHub PR #232 Conversation. **Do not modify implementation code or merge, do not run semantic Assembly/Research/publish.** If PR HEAD changes, independently recheck against its fresh HEAD before verdict.
- **Director next:** require independent QA, then merge decision. After merge separate human operator reviewer appointment, first typed branch setup, one read-only authority dispatch, fresh one-shot semantic launch. No one-game-only or automatic bulk publish permission.

## DIRECTOR TWO-CHAT PARALLEL ASSIGNMENT — 2026-10-20: unblock original shadow Assembly for all 18, 12 eligible

- **User decision:** split into **TWO WORKER CHATS NOW**, without 12 semantic chats or an additional one-game-only approval. Scope is the immutable original 18-row/six-group experiment; only 12 are currently `ready`, 2 Research-invalid and 4 missing must be skipped until separately addressed. A single explicitly launched semantic chat is the eventual intended execution mode; **not authorized to start now**.
- **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1 (developer):** `WORKER_TASK_DOSSIER_SHADOW_18_TRIAL_WIDE_SEMANTIC_AUTHORITY_01.md` (`dossier-shadow-18-trial-wide-semantic-authority-01`) — implement additive, canonical, versioned **trial-wide isolated sandbox-only semantic permission** and strict one-session/12-ready traversal/typed handoff ownership; isolated DRAFT PR, negative tests and durable report. Contract-block if original frozen authority cannot be reconciled without weakening protection. No real Assembly or any `publish`.
- **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 2 (independent preflight):** `WORKER_TASK_DOSSIER_SHADOW_18_INDEPENDENT_EXECUTION_PREFLIGHT_01.md` (`dossier-shadow-18-independent-execution-preflight-01`) — independently audit full original frozen order/12 readiness, exact authority contradiction, handoff/runtime feasibility, reviewer-role gate, GitHub per-AppID publication approval, acceptance/negative test checklist. READ-ONLY except optional dedicated report-only PR. Later re-use this physical Chat2 for **independent QA of Chat1's developer PR** after Director names actual PR. Do not begin semantic execution before acceptance.
- **Old `WORKER_TASK_DOSSIER_SHADOW_18_SANDBOX_SEMANTIC_AUTHORITY_FIX_01.md` is explicitly SUPERSEDED**; it was one-game-only and is not to be dispatched. Original semantic `1517180` worker result `BLOCKED_AUTHORITY` remains historically correct and **must not be restarted**.
- **Immutable evidence:** merged PR #230, successful original GitHub manual read-only [inspect #39413937596](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596), original Assembly marker `2c2649fb98322507cd3758ff0ff7992128f94de0`, original 12/2/4 disposition, no real semantic Assembly or candidate publish. Never modify original Research/marker or production activation; no Scheduled Tasks.
- **Next Director gate:** review both actual worker reports and Chat1 PR/CI; then independent Chat2 PR QA; only after Director merger and separate launch user approval can one semantic conversation process eligible original games. Original GitHub `publish` per game remains separately human-gated.

## DIRECTOR BLOCKER + ASSIGNMENT — 2026-10-20: original one-game Assembly BLOCKED_AUTHORITY

- **Real worker result:** NEW one-shot physical ЧАТ 1 stopped `BLOCKED_AUTHORITY` BEFORE semantic work on exact AppID `1517180`. No typed handoff branch/JSON/commit or Assembly, no publish, frozen sandbox unchanged. This is **correct contract compliance**, not Research failure. Chat-only worker result, no durable authored worker report yet.
- **Independently confirmed main contracts:** `config/dossier_shadow_research_trial_contract_v1.json` has `no_assembly_activation=true`, `standalone_sandbox_semantics_approved=false`; immutable original Director decision has `actual_semantic_execution_permitted_now=false` and requires compatible sandbox gate plus review-role appointments; `config/execution_ownership_contract.json#explicit_manual_semantic_worker_chats` has Russian translation/Deep exceptions only, no Dossier shadow one-shot. Research feasibility authorization `assembly_authorized=false` was reported by worker and must be rechecked from immutable Git proof. The prior Director task could **not** authorize semantics by itself.
- **NEW physical developer worker destination: ЧАТ 2** (`НЕ` reuse previous QA ЧАТ 2); complete task `WORKER_TASK_DOSSIER_SHADOW_18_SANDBOX_SEMANTIC_AUTHORITY_FIX_01.md`. Mode IMPLEMENT in isolated PR with mandatory architecture/contract preflight, strict additive sandbox-only versioned one-game gate, current ownership explicit exception, tests and durable report; or `CONTRACT_BLOCKED` if any immutable authority forbids compatible exception. Do not modify frozen authority, approve appointments on worker's behalf, run semantics/publish/Actions/Scheduled Tasks or enable full Dossier production.
- **Next Director action after Chat 2:** inspect worker PR/security tests and independent QA; obtain required user/Director approval to merge such governance before separately asking user to launch ONE new explicit semantic worker. Manual candidate `publish` remains separately unapproved per AppID. The former physical Chat1 is blocked/completed and should not be resumed as an implicit retry.
- **Owner:** GitHub owns exact frozen scope/marker/validation/transport/persistence. ChatGPT semantic worker may only act under an explicit canonical one-shot exception. No new control-plane or recurring task owner.

## DIRECTOR NEXT WORK — 2026-10-20: first original-ready one-game Assembly handoff

- **User instruction:** stop waiting after each declared next step. Director assigns the bounded actual worker step; Director itself does NOT perform semantic research/Assembly or Git candidate publication.
- **Куда отправить:** **НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1**, task `WORKER_TASK_DOSSIER_SHADOW_18_FIRST_ONE_GAME_ASSEMBLY_HANDOFF_01.md`, `id=dossier-shadow-18-first-one-game-assembly-handoff-01`, scoped to original frozen **AppID `1517180`**, first transport-ready row in original 18 order (previous `1508750` is research_not_submitted). Task begins with READ-ONLY authority/transport preflight. If and ONLY if immutable canonical isolated sandbox one-shot is explicitly allowed, worker may produce exactly one genuine semantic typed Git handoff commit on `handoff/dossier-shadow-18-assembly-typed`. No ordinary developer PR or source changes. On any authority/runtime ambiguity, fail closed with exact evidence.
- **Current real evidence:** merged [PR #230](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230); manual inspect [39413937596](https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596) SUCCESS, 12 ready / 2 invalid / 4 missing, sandbox unchanged at `2c2649fb98322507cd3758ff0ff7992128f94de0`, no semantic output. First ready `1517180` Research SHA `33faf93e578d32dd5e694f72f119041eb102021d` pinned in `config/dossier_shadow_18_github_python_handoff_pins_v1.json`.
- **Next Director gate:** inspect actual worker report / new typed introducing SHA and original immutable Git branch/bytes before separately deciding an exact authorized **one-game** manual `publish` UI dispatch. **No `publish` authorization now.** No original marker/Research/source/production/Deep/Task changes; no Scheduled Tasks. `WORKER_TASK.md` belongs to unrelated task.
- **Physical chat state:** prior developer/QA Chat1/Chat2 are completed/retired. This is a new physical Chat1, not a continuation of merged PR #230 implementation.

## DIRECTOR VERIFIED — 2026-10-20: one post-merge read-only Assembly inspect PASSED

- **EXECUTED, COMPLETE**: user manually triggered existing merged workflow `Isolated shadow 18 Assembly canonical Python handoff` **run #16 / ID `39413937596`** on `main` at `dfa159f6ac6826bad5dc38ef59f113c8638b156d`, `event=workflow_dispatch`, `run_attempt=1`, final `SUCCESS`. https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596
- **Jobs:** `read-only-inspect` SUCCESS; `manually-gated-candidate` SKIPPED; semantic fixture suite skipped as expected for non-PR event. Actual original GitHub Python `inspect` ran successfully; run logs print `{'ready': 12, 'research_not_submitted': 4, 'research_transport_invalid': 2}` (all 18). The active workflow also asserts `semantic_attempts=0`, `canonical_acceptance=false`, `deep_ready=false`. Result artifact `frozen-shadow-18-python-inspect` ID `12260293764` was uploaded: https://github.com/kentrap2011-hub/steam-kz-deals-2/actions/runs/39413937596/artifacts/12260293764
- **Frozen sandbox unchanged:** `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research` HEAD still `2c2649fb98322507cd3758ff0ff7992128f94de0`; 12 transport ready only, 2 invalid (SULFUR `2124120`, Sifu `2138710`), 4 missing (`1508750`,`1607130`,`1849000`,`1857090`). No candidate writes, no real semantic Assembly, no canonical Dossier/Deep acceptance. User granted **only** this one inspection; authorization is consumed, not permission for publish, semantic work, other manual runs or Scheduled Tasks.
- **Next Director gate:** design and separately obtain user's explicit authorization for ONE real semantic Assembly candidate from the original 12 ready, with exact original AppID, immutable typed handoff git introduction SHA/branch, documented human approval and separately authorized single `publish` dispatch. First perform bounded feasibility/preflight of available tools if unclear; do not launch real work merely because `inspect` succeeded. The connected GitHub tool cannot manually dispatch Actions; a GitHub UI operator is required. Do not repeat inspect without new consent.

## ACTIVE DIRECTOR STATUS — 2026-10-20: PR #230 MERGED; no Assembly execution authorized

- **Latest verified main at PR merge:** `d543337e3613bc0542b7a89018ff980e9b2189a3` (refresh before decisions); [PR #230](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230) is **CLOSED/MERGED**, GitHub `merged_at=2026-10-20T11:07:22Z`, merged from head `48db1de81294008e1f55e857c4a42c663184e8a3`. User explicitly authorized only the merge. Source commit history preserved.
- **Independent QA:** [re-review #6274188636](https://github.com/kentrap2011-hub/steam-kz-deals-2/pull/230#issuecomment-6274188636) gave `PASS_FOR_DIRECTOR_MERGE_REVIEW`; final-head GitHub actions `39297241772`, `39297241824`, `39297242033` all succeeded; publish job skipped. Prior `CHANGES_REQUIRED` no longer applies to merged code.
- **Pilot state unchanged:** original sandbox `sandbox/dossier-shadow-calibration-20261011-6x3-frozen-research`, original Assembly marker `2c2649fb98322507cd3758ff0ff7992128f94de0`, issuer `39054131983`, original Research frozen. Authentic read-only Python inspect shows **12 transport-ready, 2 invalid (SULFUR/Sifu), 4 not submitted** out of 18. **Zero real semantic Assembly candidate submissions/publish**; no canonical Dossier acceptance or production activation by PR #230.
- **NEXT director decision (not yet authorized):** plan one separately permissioned **read-only** `inspect` of the merged workflow through supported human GitHub Actions UI or equivalent proven operator path; separately authorize even read-only manual dispatch. Only after evidence and new explicit per-candidate consent plan individually scoped semantic Assembly typed handoffs and candidate publications. There is no supported connected GitHub workflow-dispatch action; do NOT invent one, auto-launch, reissue issuer, or alter Scheduled Tasks.
- **Worker status:** initial developer ЧАТ 1, independent QA ЧАТ 2 closed their PR work and may be retired. For any NEW task create a **NEW physical worker chat**, not a stale continuation, unless specifically fixing the just-merged PR; do not recycle old physical chats for unrelated work. `WORKER_TASK.md` belongs to unrelated task, do not overwrite without authority.
- **Residual scope:** approved technical code has a narrow non-atomic handoff-ref race and unrelated flaky P2 fixture. Recheck current GitHub before any operational call; no live semantics or source/production changes were authorized by the merge.



## HISTORICAL HANDOFF (superseded) — 2026-10-13: Deep history emergency + gamepad SVG

**HISTORICAL FIRST-RESPONSE INSTRUCTION — SUPERSEDED by the 2026-10-19 PR #230 remediation handoff above:** former October 13 plan for Deep history and site icons follows for archival context only.

- **ЧАТ 1 (NEW)**: `WORKER_TASK_DEEP_VERSIONED_HISTORY_FIRST_CORE_01.md` → implement immutable versioned Deep history + producer compatibility/historical fallback + ordering NEVER-DEEP-ANALYZED FIRST, then oldest last successful Deep. User's rule: ANY new profile content version including punctuation becomes a version, but prior analysis is never erased and remains visible as last completed with original accepted date and old profile-version label. New current-version validity remains separate. Build new producer fields first; **do not modify web/** while Chat 2 owns site icons. After PR acceptance, assign separate new task to wire cards+statistics: both last Deep analyzed date and latest profile revision date, stale label and old/new version counts. DO NOT rerun all Deep or fabricate "new current" authoritativeness. Snapshot 2026-09-30 had 47 current-compatible Deep; snapshot 2026-10-13T09:28:42Z: 425 current games, 8 current-compatible Deep, 12 attempts, 4 unresolved; 30 old migration and 43 later score-explainability migration accepted but overlapping, not additive. Profile content blob changed from `9b992603...` (~270KB) to `1d0a3aac...` (~292KB). This causes stale projection, not proven deletion of accepted old bytes.
- **ЧАТ 2 (NEW)**: `WORKER_TASK_SITE_GAMEPAD_SVG_TEXT_CONVERSION_01.md` → user wants avoid failed binary transfer by converting *exact user-approved* `steam_icon_pack.zip` art to **text SVG** (old site icons were text SVG and thus easy to commit) and updating favicon/manifest/static refs; check maskable. Require original ZIP attachment SHA-256 `c73d3d1a36de580f3dc7318dbc3cd410cdfd0826bd62cb19887bb9d514efe2c4`, 3,281,824 bytes. Old physical Chat2 `implement/site-gamepad-icon-pack-replacement-01` has **only a blocked report**, no icon PR. SVG cannot guarantee Apple-touch PNG or all launchers; report partial and exact manual binary upload step if needed; do not invent new art.
- **Remaining prioritized work, after independent worker PRs:** Director review/merge both; Chat1 producer Deep core acceptance → separate Deep **UI cards + version-specific statistics** implementation (latest historical result even if old, two dates, clear stale/current, never analyzed vs older-only vs current); then restore/reconcile legacy Deep history across 30/43 overlapping migration families and regression-test behavior across future content updates; then separately dispatch the already merged **PR #218 GitHub manual-once Dossier freeze publisher** to prepare exact 18-game Research work/marker, appoint independent A/B/C reviewers and approve bounded nonproduction Research→Assembly, compare speed/quality, correct defects, switch Dossier to two stages in production only after gates; finally finish 2-stage Deep cutover and retire Fast. Do not stall Deep history bug waiting for Dossier; do not run new semantics from developer chat or change Scheduled Tasks.
- **CRITICAL provenance and site truth:** `data/production/site/current_status.json` at 2026-10-13 09:28:42 UTC says 425 total Deep scope, 8 current completed (7 fit / 1 not), 4 incomplete, 219 waiting Dossier; old accepted Deep results are not counted in current 8 and cards may say not analyzed. Current matching code: `scripts/progressive_pass2.py::matching_state_entry` → `progressive_pass1.state_entry_semantically_matches`; `progressive_pass1.semantic_generation` includes profile blob/content SHA, so prior semantic generations become non-current after profile content changes. Retain exact old truth; do not claim all historical results can be treated as current or summarily rewrite their scores.
- **PR #218** merged `c23d952418edca8adbc8e6db0a69ba89698830b4`, but manual publishing `.github/workflows/publish-dossier-shadow-research-freeze.yml` has **not** run. Do not announce "18 games analyzed." **PR #220** governance accepted `8907f2cba0052028a855f10d91e640390488d95b`. Old site `web/icon.svg` / `web/icon-maskable.svg`, HTML and PWA manifest currently still use old icons.
- All implementation PRs independently review and merge through Director only. **No Scheduled Tasks, automations, semantic production changes, direct cache writes, blind old Deep reanalysis or fake icon binaries.**

## LATEST DIRECTOR CHECK — 2026-10-13: Chat 1 implemented, Chat 2 blocked on GitHub binary upload

- **ЧАТ 1 PR #218 merged `c23d952418edca8adbc8e6db0a69ba89698830b4`**, 2 green CI, only manual-once isolated GH publisher + read-only PR-only tests + report; no durable freeze marker/buffer published yet; no 18-game semantic Research or Assembly run. To publish original GitHub authority, launch `Publish frozen Dossier 18 Research trial (manual, once)` via Actions selecting main and using exact current main SHA plus `PUBLISH_DOSSIER_SHADOW_18_ONCE`, only after verifying expected main SHA and no prior sandbox branch. The separate actual semantic execution and A/B/C reviewer gate stays blocked.
- **ЧАТ 2 no implementation PR**. Branch `implement/site-gamepad-icon-pack-replacement-01` contains only blocked report `reviews/worker_reports/site-gamepad-icon-pack-replacement-01.md`. Original ZIP verified SHA-256 `c73d3d1a36de580f3dc7318dbc3cd410cdfd0826bd62cb19887bb9d514efe2c4`; supplied binary bytes are correct, but Chat2 cannot upload binary PNG/ICO Git blobs with available cross-tool transport (sandbox ↔ GitHub). Current main site still references old SVG favicon/manifest. Next needs real GitHub binary file upload of eight extracted assets, then newly authorized Chat2 worker continuation, targeted tests/PR. No fake PNG, no site/Scheduled Task/production/Deep/Fast changes.
- Both physical worker chats should stop after their reports. This is an implementation status update, not authorization for new semantic Research, restart of other jobs, or icon placeholder commit.

## LATEST DIRECTOR PARALLEL ASSIGNMENT — 2026-10-12: site gamepad icon pack

- User requests **ЧАТ 2** to replace website icons from attached `steam_icon_pack.zip`. Prepare **NEW physical worker Chat 2** with `WORKER_TASK_SITE_GAMEPAD_ICON_PACK_REPLACEMENT_01.md` from main. Actual Director ZIP SHA-256 `c73d3d1a36de580f3dc7318dbc3cd410cdfd0826bd62cb19887bb9d514efe2c4`, 3,281,824 bytes. User **must attach same ZIP to Chat 2** because Director attachments do not automatically transfer. Worker verifies binary inputs and changes only actual favicon/HTML/PWA manifest/Apple/maskable/targeted cache and tests; PR and report, no self-merge.
- Current main website: `web/index.html` old `icon.svg?v=shortcut-icon-1`; `web/manifest.webmanifest` still `icon.svg` and `icon-maskable.svg`. The user-provided package includes PNG sizes 16,32,48,64,128,180,192,256,512,1024; ICO, maskable and master. Do not create new imagery instead of using supplied asset.
- **ЧАТ 1 separate outstanding marker assignment remains unchanged** (`WORKER_TASK_DOSSIER_SHADOW_FIRST_18_PUBLISH_GITHUB_FROZEN_RESEARCH_AUTHORITY_01.md`); no implicit approval of Dossier semantics. Scheduled Tasks and production control plane unchanged.

## LATEST DIRECTOR RESULT / ASSIGNMENT — 2026-10-11: Stage A/B sandbox PRs done, real GitHub marker next

- PR #215 (ЧАТ 1) merged `25f6ca93bbcf8a95176ee0c519298962f684e261`, all **3** latest PR checks green: real reusable Research sandbox validation/proposal/one-shot future prompt; `sandbox_research_invocation_ready=blocked`, **zero semantic runs**, missing real immutable GitHub marker and buffer plus independent A/B/C review signoff.
- PR #214 (ЧАТ 2) merged `55cffacc3e234ff0424e49c566b9593e094bf4f2`, **2** PR checks green, converted draft to ready by Director: real offline Assembly Git transport strict bridge/review adapter, **zero Assembly semantics**, waiting on actual Research. Both are isolated, production gates unchanged and old one-stage Dossier authoritative.
- **NEW ЧАТ 1**: `WORKER_TASK_DOSSIER_SHADOW_FIRST_18_PUBLISH_GITHUB_FROZEN_RESEARCH_AUTHORITY_01.md`. Build/publish an actual GitHub-controlled durable sandbox Research buffer and its one-parent marker-only commit for exact **6 groups [3,8,13,15,18,20] / 18 AppIDs**, using existing PR #215 strict writer validation. No further 114-source/55-year pre-audit, no semantically researching a game from implementation chat. Publish real authority or one precise blocked reason, PR and report, never self-merge.
- **ЧАТ 2 unassigned** (wait for Research output). After accepted real frozen marker, Director chooses separate review A/B/C roles, formally approves nonproduction semantic gate and issues a NEW bounded one-shot Research invocation. Contract `active=false` production flags are never to be flipped for this sandbox. No Scheduled Tasks, canonical cache/writer/Deep/Fast/UI/production changes. Previous assignments below historical.

## LATEST DIRECTOR DECISION — 2026-10-11: first real 6×3 Research→Assembly test, sandbox authority first

- User said **Делаем** after Director proposed stopping the 114-old-source/55-old-year pre-audit loop and advancing to an **actual limited semantic Dossier experiment**. Selected deterministic PR #205 six original groups **[3,8,13,15,18,20]** = 18 distinct AppIDs as **nonrepresentative calibration**. Frozen historical writer-proven parent at `95a4bf4990a60082ecb3302da5bc7f23b618d93e`; exact source/blobs and group hashes in `reviews/dossier_shadow_offline/dossier_shadow_calibration_20261011_6x3_director_decision_v1.json`. The user wants speed and quality evidence from NEW analysis, not more old-source audits.
- **Current hard gate:** genuine production two-stage Research/Assembly contracts remain `active=false / authorized_for_semantic_execution=false`. No actual GitHub-owned trial marker/buffer/prompt assignment exists. Director decision **approves objective and exact proposed scope, NOT a direct runtime bypass or production activation**. Need distinct minimal sandbox-only GitHub authority and independent reviewer/stop rules before real data-plane starts; do not mistakenly run current inactive prompts or write live GitHub inbox.
- **NEW ЧАТ 1:** `WORKER_TASK_DOSSIER_SHADOW_FIRST_REAL_18_RESEARCH_SANDBOX_AUTHORITY_01.md`; own stage-A exact immutable GitHub 6×3 sandbox preauthorization and manual one-shot worker entry, real evidence acquisition deferred until its safe pilot marker exists. PR-only isolated safety tests, no live production.
- **NEW ЧАТ 2:** `WORKER_TASK_DOSSIER_SHADOW_FIRST_REAL_18_ASSEMBLY_COMPARE_SANDBOX_INTEGRATION_01.md`; independent stage-B exact submitted Research→Assembly sandbox handoff and historical accepted comparator / blinded reviewer structural gate; real execution only with actual authorized Research transport. Separate files/PR.
- Year conflicts Sonic Adventure 2 AppID 213610 old original binding 2012 vs verified 2001; Sifu 2138710 old 2023 vs verified 2022; fail closed as typed comparison issues rather than silently rewriting baseline or suppressing results. No additional blanket source/year scans are prerequisite.
- When both PRs accepted, Director checks the actual nonproduction execution authority and launches next finite semantic invocation if fully proved; otherwise identify exact missing gate, don't claim trial already run. Existing one-stage Dossier/Deep unchanged; no Scheduled Tasks, canonical queue/receipts/cache/writer changes. Older handoff below historical.

## LATEST DIRECTOR RESULT — 2026-10-11: both public pre-output worker audits merged, no real pilot authorized

- ЧАТ 1 PR #210 merged `04a8eec3d8e851137248d30d807cdbcc03e628e0`, PR-only CI 2/2: 20 historical groups/60 Dossier safe source metadata ledger, 118 predeclared public parent candidates but 4 attempted/2 metadata-visible/2 inaccessible/**114 not measured**. Russian/negative/date counts are **old Dossier claims** only, not independently verified player-source truth; external quality still unproven.
- ЧАТ 2 PR #209 merged `a89540707e72f9d966c87995df4e47ee016bb14b`, PR-only CI 2/2: 60 old exact AppIDs retained, only **5 independently supported original-work release years**, 13 publicly evidenced Steam displayed dates, original years **55 unknown**; candidate old year conflicts AppID **1638220**, **213610** (Sonic Adventure 2), **2138710** (Sifu), plus five edition/EA ambiguities requiring adjudication. Exact source/edition fact kinds matter.
- Both *bounded work products* complete; **substantive public evidence verification remains partial**. PR #205 illustrated groups [3,8,13,15,18,20] are still NOT_READY_FOR_APPROVAL / not chosen / not frozen. No actual new Research/Assembly semantics or human quality reviews.
- No new assigned worker task. Director/user must decide whether to authorize additional bounded systematic source metadata checks on remaining **114** candidate source parents and stronger 55-game original-work date/edition verification before any fair 18-game trial selection. Source authenticity, privacy, reviewer roles and stopping gates need concrete plan.
- Current one-stage Dossier remains canonical, two-stage inactive; no Scheduled Tasks, Deep/Fast/ranking, live caches/receipts/queues/writer/production or user data changes. Older handoff entries below are historical.

## LATEST DIRECTOR ASSIGNMENT — 2026-10-11: paired read-only public source metadata and original work-year checks

- User approved the next preparation step after PR #205/#206: **read-only examination of provenance/identity for ALL 20 historically accepted old Dossier groups (60 exact games)**, not actual Research→Assembly semantic execution or any trial activation. The prior six groups 3,8,13,15,18,20 remain an inert illustration marked NOT_READY_FOR_APPROVAL.
- **NEW CHAT 1:** `WORKER_TASK_DOSSIER_SHADOW_PREOUTPUT_SOURCE_PROVENANCE_AUDIT_01.md`, pinned old frame, bounded public player-source **metadata-only** verification of reachable exact sources/physical-parent independence, date/language/claimed negatives/gaps, safe exhaustive 60-game/20-group rows, unknown/not_measured if unsafe; no reading/conclusions from review prose.
- **NEW CHAT 2:** `WORKER_TASK_DOSSIER_SHADOW_PREOUTPUT_IDENTITY_YEAR_READINESS_QA_01.md`, separate bounded public original work/year/Steam storefront/edition/version checks for same 60 AppIDs plus future decision checklist and missing categories. No Chat 1 result dependence or duplicated source-review work.
- Preserve PR #201 immutable pin `95a4bf4990a60082ecb3302da5bc7f23b618d93e`, exact old manifest/audit blobs and per-game GitHub writer receipts. Both workers work independently in branches, PRs, isolated tests, reports and safe metadata only. Director must review/merge them separately and then decide whether to ask user for a separate concrete 6×3 trial authorization; no group selection or freeze now.
- Production one-stage Dossier stays authoritative; two-stage inactive. No real semantic calls, source review synthesis, production/cache/writer/Deep/Fast/UI mutation, Scheduled Tasks or automations changes. Earlier handoff sections below are historical.

## LATEST DIRECTOR RESULT — 2026-10-11: PR #205/#206 completed, real shadow cohort not approved

- PR #205 merged `063ed71826d60a7028906217c3cd327901ceb8d7`: strict historical 20 old one-stage groups baseline reused; deterministic **unapproved preview** original groups **3, 8, 13, 15, 18, 20** = 18 AppIDs; 14 in-frame nonselected groups transparently counted, future cohort `NOT_READY_FOR_APPROVAL` since external original-work/year/edition, language, source-parent independence, timing, negatives, risks and gaps are still unmeasured across the full 20-group frame.
- PR #206 merged `c3f766730e81e9316d1b80a77279b46a5dc99f24`: independent inactive synthetic strict writer-proof and Research→Assembly chain review gate, blinded A/B mechanical first-round Git freeze and third-party adjudication rubric, 13 dimensions; zero actual semantic work or externally verified source quality.
- Both workers' PRs and reports reviewed, CI green, and accepted; Chat 1 and Chat 2 can be retired. **No active worker task assigned.** If user approves next read-only evidence step, create a NEW Director task: independent pre-output source metadata/original year and truthful strata for all 20 old groups before selecting a representative/fair 6×3 real semantic pilot. The six from PR #205 are only a sample illustration, not user-approved scope.
- No live semantic trial, production activation, Scheduled Tasks, Deep/Fast/ranking/cache/writer/website changes. Existing one-stage Dossier remains production truth. Earlier assignments below are historical.

## LATEST DIRECTOR ASSIGNMENT — 2026-10-11: dual Dossier pilot decision preparation (inactive)

- PR #201 merged `d98966c64cf088fe28854a2f42408fd75f9daffd`: pinned historical accepted one-stage Dossier 20/20 exact groups (60 games) proved strict Git baseline and independently matched GitHub Actions writer jobs; external source trust and new two-stage quality still unevaluated. PR #203 merged `a1f1c5fa2d38727f8ee8cd44d6a3464d25085dbb`: compact popover outside tap repair, synthetic CI green, awaiting user Android acceptance.
- **NEW ЧАТ 1**: `WORKER_TASK_DOSSIER_SHADOW_PILOT_COHORT_DECISION_PACKET_01.md` — deterministic, metadata-only prospective **6 whole groups × 3 games** approval packet, strictly from verified historical 20-group frame; do not cherry-pick/freeze/authorize a live trial, note genuinely unknown category diversity, no real semantics.
- **NEW ЧАТ 2**: `WORKER_TASK_DOSSIER_SHADOW_QUALITY_REVIEW_GATE_01.md` — separate offline reviewer A/B + adjudicator and quality-difference gate, synthetic fixtures only, source-anchor/negative-evidence/identity fail closed. No Chat 1 scripts touched.
- Both create independent PR and worker report, never self-merge. Separate user approval still required before any real semantic Research→Assembly pilot. Never change Scheduled Tasks, production cache/receipts/writer/Deep/Fast, two-stage active flags or real-stage scope.
- Older assignments below historical.

## LATEST DIRECTOR FOLLOW-UP — 2026-10-11: compact freshness popover dismiss

- PR #199 merged `7683c94ce5736052e1e071593f58ab6bad4e7545`, user confirmed much improved small feed freshness status in normal Android browser. Newly reported: expanded status detail popover sometimes remains open when tapping outside (screenshot ~16:06). Director checked `web/feed-bootstrap.js`: status icon toggle + Escape listeners but **no document-level outside-click** handling.
- **NEW ЧАТ 2:** `WORKER_TASK_SITE_FEED_SYNC_POPOVER_OUTSIDE_DISMISS_FIX_01.md` — minimal click-away/touch dismiss, preserve inside retry, aria/focus, ensure listener cleanup and nonblocking mobile feed interactions. PR-only tests/report, no worker self-merge.
- **ЧАТ 1** independently assigned real baseline audit in `WORKER_TASK_DOSSIER_SHADOW_REAL_BASELINE_ELIGIBILITY_AUDIT_01.md`; no interference or pilot authorization.
- No Scheduled Tasks changes, semantic execution, production writes, cache/user state reset or Deep cutover. Older handoff entries below historical.

## LATEST DIRECTOR ASSIGNMENT — 2026-10-11: audit real old Dossier writer baselines (no semantic run)

- **NEW ЧАТ 1:** `WORKER_TASK_DOSSIER_SHADOW_REAL_BASELINE_ELIGIBILITY_AUDIT_01.md` — read-only audit **ALL currently accepted** original three-game groups using immutable main Git history, PR #197 writer preflight and source/cache/receipt provenance; per-group safe statuses and blockers, separate Actions attestation status. Do not authorize, freeze/select or run a real pilot; even 6 positive groups only justify a **new user approval step**.
- Director checked current Dossier snapshot `4d7be57c9a1a90482d948270ab034c49eca3dd84102d28fc67b6fbc1d33f8239` on main: 76 original three-item groups, 19 accepted/57 pending, 19 matching snapshot `dossier_candidate_accepted_current_snapshot` audit records. This is a promising one-to-one count, **NOT strict historical proof**; worker must pin head and check every binding and historical writer commit.
- **NEW ЧАТ 2 still assigned:** `WORKER_TASK_SITE_FEED_SYNC_COMPACT_FRESHNESS_UX_FIX_01.md`, compact truthful feed refresh UI; do not modify its scope. Prior #196 resolved missing Deep marker; user confirmed Strange Horticulture position #26 lit.
- Both workers separate independent branches/PR+reports, do not self-merge. No Scheduled Tasks/automations changes, live semantics, real shadow run, production activation, existing writer/cache or Deep/Fast migration. Older handoff sections below are historical.

## LATEST DIRECTOR ASSIGNMENT — 2026-10-11: compact mobile feed sync UI

- PR #197 merged `a216807f95cfa71bb28435142af10605c5c1aa60` (ЧАТ 1 historical Dossier writer receipt preflight, synthetic only; real candidate eligibility not established, some accepted legacy groups lack audit). PR #196 merged `d75c60d8d1a7eb2bc3dfd1f83051cdb27781b431` (ЧАТ 2 browser cache/Deep refresh).
- User confirmed **site is now updated** in ordinary Android browser: Strange Horticulture #26 with Deep lit. However screenshot shows large permanent amber freshness banner + button and immediate "saved copy / could be out of date" even though cache timestamp only ~1 minute old. Exact code uses `freshnessNotice('stale')` for *network verification failure*, not measured age.
- **NEXT: НОВЫЙ ЧАТ 2** `WORKER_TASK_SITE_FEED_SYNC_COMPACT_FRESHNESS_UX_FIX_01.md`: compact status in/near header, no permanent multiline/button, small accessible retry/details and truthful network-verified vs cached-unverified vs confirmed outdated semantics; retain quick cache-first feed and all persistent user state. PR-only QA, no direct deploy.
- **ЧАТ 1** has completed #197; no new assignment until Director/user explicitly decides next Dossier real-evidence trial / writer-receipt coverage. Do not start semantics or freeze live groups.
- No Scheduled Tasks changes, production or semantic writes/activation, Deep/Fast migration. Older handoff assignments below are historical.

## LATEST DIRECTOR ASSIGNMENT — 2026-10-11: feed freshness and shadow pilot preflight

- PR #193 merged `f6718dafe3267d926e72e4070e134e011d2187a7`: bridge proof flag `cross_pr_research_original_year_fix_verified=true` now independent of real authority, CI green, inactive. PR #194 merged `85e320eb8bc88310f75a3c0a28cefb722c7c1850`: shadow trial prospective plan and Deep site count read-only QA; prior worker chats retired.
- User verified `Strange Horticulture` Deep indicator OFF in persistent browser (position 45) and ON in incognito; GitHub visual producer `game:1574580` has `deep_stage_state=completed,deep_stage_outcome=fit`. This rules out manual queue deferral as sufficient Deep-indicator explanation and supports stale local feed/bootstrap.
- **NEW ЧАТ 1:** `WORKER_TASK_DOSSIER_SHADOW_PILOT_PREFLIGHT_01.md`: technical writer-receipt/immutable group preflight to prepare later separately approved real-source Dossier shadow pilot, no semantic work, selection or authorization.
- **NEW ЧАТ 2:** `WORKER_TASK_SITE_DEEP_STATUS_BROWSER_FEED_REFRESH_FIX_01.md`: bounded site stale feed/cache-first/background refresh repair, stale data signaling, non-destructive retry and preservation of `manual_end_at` / user queue and settings. PR only, no direct deploy.
- Distinct PRs/reports and file ownership; worker never self-merges. No Scheduled Tasks, live semantic tasks, production writes or activation. Deep `mass_migration_authorized=false`; Fast stays until separately approved atomic cutover. Earlier assignments below historical.

## MOST RECENT DIRECTOR ASSIGNMENT — 2026-10-11

- PR #190 merged `44b1d8f54aa7692220439b82892999de7a75e1dd` (all joint Research/Assembly/GitHub strict offline tests passed; proof metadata/offline gate bug found). PR #191 merged `42919b50af4df6212a9d2ab7233635c438571a7f` (inactive shadow-quality readiness harness and draft trial protocol; no real evidence used). Prior physical workers retired.
- **NEW ЧАТ 1:** `WORKER_TASK_DOSSIER_ASYNC_BRIDGE_PROOF_GATE_DECOUPLE_01.md`; narrow proof flag/offline gate decoupling and redo joint tests, no activation.
- **NEW ЧАТ 2:** `WORKER_TASK_DOSSIER_SHADOW_TRIAL_PLAN_AND_SITE_DEEP_COUNT_QA_01.md`; future real-evidence shadow trial pre-registration **without running it**; additionally read-only detailed analysis of user question 8 Deep/9 not Deep in displayed UI versus 14 global suitable. Separate two reports, no UI code changes.
- Canonical `data/production/site/current_status.json` on 2026-10-11 09:22 UTC reported 14 Deep-fit, 6 Deep-not-fit, 2 incomplete. Visual production payload had 297 cards including 14 `deep_fit`, 2 incomplete, 281 not analyzed. Therefore current full producer did not lose six suitable cards; exact user-visible subset/browser filter reason not yet proven. Do not guess.
- No scheduled-task creation/modification, production activation or real semantic runs. Deep `mass_migration_authorized=false`; Fast remains authoritative until final atomic cutover. Older assignments are historical.

## NEWEST DIRECTOR HANDOFF — 2026-10-11

- User confirms `Being a DIK - Season 1` translation now displays normally; no site cache incident remains.
- PR #187 Research year validator merged `aec7701dfb484bbe3d0165e3dc75875c4d2e2c23`; PR #188 inactive final group bridge merged `0549dc00b4a96833f747707f92c000bf44f443fc`. Previous physical worker chats retired.
- **NEW ЧАТ 1:** `WORKER_TASK_DOSSIER_ASYNC_POSTMERGE_JOINT_INTEGRATION_QA_01.md`, actual joint Research/Assembly/GitHub bridge offline regression, original-year formerly-XFAIL check.
- **NEW ЧАТ 2:** `WORKER_TASK_DOSSIER_ASYNC_SHADOW_QUALITY_READINESS_01.md`, inactive evidence-quality/parity harness and future real-evidence trial criteria only.
- Separate PRs, no production semantic work, Scheduled Task changes or activation. Deep `mass_migration_authorized=false`; Fast remains production authority until final atomic Deep cutover. Earlier assignments below are historical.

## LATEST DIRECTOR TASKS — 2026-10-11

- PR #184 Research→Assembly offline E2E QA merged `2a5f0fe0173848b8e5baf6b488bb923be8cb4efd` (87 passing unit tests).
- PR #185 GitHub chain offline QA merged `6bbfadeeada12f46955fa60bc3b26f820bd7a429`. A Research original-release-year contradiction remains an explicit XFAIL, **not** fixed. No final GitHub three-game writer adapter exists yet.
- **НОВЫЙ ЧАТ 1:** `WORKER_TASK_DOSSIER_RESEARCH_ORIGINAL_YEAR_BINDING_FIX_01.md`, bounded Research fail-closed year-consistency fix.
- **НОВЫЙ ЧАТ 2:** `WORKER_TASK_DOSSIER_ASYNC_GITHUB_FINAL_ACCEPTANCE_INTEGRATION_01.md`, inactive GitHub-owned final group strict acceptance bridge.
- Independent developer PRs. No real semantic work, production activation, canonical writes or Scheduled Task changes.
- Deep `mass_migration_authorized=false`; no early production Fast removal. Historical assignments below are superseded.

## MOST RECENT DIRECTOR DECISION — 2026-10-10

- #181 (Research) merged at `8bba23fca6337e06504f819c8ccda298ffd8505a`; #182 (Assembly) merged at `4cca97a838e42b275259751010f339116d068adc`. Both passed branch CI and remain inactive/non-authoritative.
- **NEW ЧАТ 1:** `WORKER_TASK_DOSSIER_ASYNC_END_TO_END_COMPATIBILITY_01.md` — offline Research→Assembly end-to-end compatibility proof.
- **NEW ЧАТ 2:** `WORKER_TASK_DOSSIER_ASYNC_GITHUB_CHAIN_ACCEPTANCE_QA_01.md` — independent offline GitHub eventual-chain and atomic three-game final acceptance QA.
- Older worker assignment sections below are historical snapshots. No production activation, no Scheduled Task changes, no Deep Stage 1 authorization (`mass_migration_authorized=false`), no early Fast removal.

## CURRENT DECISION / ASSIGNMENTS — 2026-10-09 (newer than historical snapshot below)

- PR #179 and PR #178 have **already been merged** into main; checks were successful. Do not merge them again.
- **НОВЫЙ ЧАТ — ЧАТ 1:** `WORKER_TASK_DOSSIER_ASYNC_RESEARCH_SEMANTIC_WORKER_IMPLEMENT_01.md` — implement inactive asynchronous Dossier Research semantic worker, no GitHub item acknowledgements.
- **НОВЫЙ ЧАТ — ЧАТ 2:** `WORKER_TASK_DOSSIER_ASYNC_ASSEMBLY_SEMANTIC_WORKER_IMPLEMENT_01.md` — implement inactive asynchronous Dossier Assembly semantic worker, use exact submitted immutable Research bytes, no GitHub Research acceptance wait.
- These are two separate developer PR-only tasks, **not** live semantic executions; neither stage may activate production or alter Scheduled Tasks.
- Deep Stage 1 executable migration still requires separate user authorization; `mass_migration_authorized=false`. A later authorized manual semantic worker does not consume ЧАТ 1/2.
- Fast must stay production-authoritative until a **single atomic Deep cutover** with accepted Stage 1/2 semantics and Stage 2 anchors; explicit visible plan substep `deep-fast-production-off`.
- The rest of this file is previous contextual/historical information; where stale, this latest assignment and `main` contracts win.

## CONTEXT-BUDGET / DEPTH RULE — VERY IMPORTANT

The Director must stay shallow and conserve context.

- Do **not** broadly inspect code, scripts, old PRs, workflows, historical reports, or repository trees just to "understand the project".
- Start from this handoff and only the **top/current** Board state.
- For a concrete question, inspect only the exact artifact needed.
- If answering correctly would require deep implementation/code analysis, **do not perform that analysis in the Director chat**. Create/assign a bounded worker task instead.
- Do not duplicate analysis already completed by a worker report.
- Do not re-open accepted PR #156 architecture freeze unless there is direct contradictory evidence.
- Keep Director responses concise and decision-oriented.

## THREE-QUESTION FACTS ALREADY ESTABLISHED

### CURRENT USER DECISION — SUPERSEDES FIRST-WAVE/RESERVE IMPLEMENTATION

The user rejected semantic first-wave/deferred-reserve gating as the production direction.

Current approved and implemented direction:
- keep the full canonically eligible semantic pool;
- do not defer ordinary eligible candidates merely to shrink semantic work;
- GitHub-owned ordering prioritizes never-Deep-analyzed subjects first;
- within comparable cohort, priority uses Steam positive rating + logarithmic review-count confidence + current price + current discount;
- no hard top-N and no eligibility reduction;
- implementation task: `WORKER_TASK_STEAM_SEMANTIC_QUEUE_PRIORITY_IMPLEMENT_01.md`;
- PR #158 accepted and merged as `9c9d79194fba3ff22ad491d80257277a87fdcfaf`;
- validations on PR head were green;
- no Stage 1/Stage 2 scoring logic changed;
- ЧАТ 1 task-page work is fully accepted and published: PR #165 fixed the closeout regression and merged as `b9ad7aed7bcc76237fb3402a291cb632ac730598`; real Pages deploys 37768728895 and 37769122260 succeeded. ЧАТ 1 is complete and free.
- PR #157 remains closed without merge as superseded.

The older ~581 + ~1,720 reserve analysis below remains historical diagnostic evidence only and must not be turned into production gating unless the user explicitly reopens that decision.

### A. Shortlist reduction: what happens to the ~1,700

Current corrected main report:
`reviews/worker_reports/steam-shortlist-scope-reduction-diagnostic-02.md`

Current funnel:
`2,522 shortlist offers -> 2,385 purchase families -> 2,301 semantic families`.

Corrected recommendation currently in `main`:
- first semantic wave: about **581** families;
- roughly **1,720** remain as `deferred_reserve`;
- reserve is **not** `not_fit`, not deleted, and not removed from canonical source truth;
- after the new 60/40 Deep model is production-active, GitHub may keep promoting reserve items that can still mathematically beat the current top-100 boundary.

Why reserve rather than permanent exclusion:
- when the same deterministic gates are tested on 112 current known Deep-fit games *without* protecting them because they are already known fit, only **23/112 (20.5%)** naturally pass the balanced ~581 gate;
- therefore Steam metadata/reviews/tags are too weak to safely make permanent taste decisions.

Concrete current examples of the type of rows likely to be deferred unless another protected lane applies:
- **Superliminal** — current discovery reasons are generic quality only (`mainstream_quality`, `very_high_rating`, `high_confidence_adjacent`), 92.5% / ~14.5k reviews, 60% discount; moderate purchase scenario says `ЛУЧШЕ ЖДАТЬ`. Under the balanced first-wave design, standalone generic routes do not qualify.
- **Seen** — `mainstream_quality` + `very_high_rating`, 90.5% / ~9.3k reviews, 50% discount; moderate scenario `ЛУЧШЕ ЖДАТЬ`. No stronger personal-fit route is visible in the current deterministic reasons.
- **Russian Life Simulator** — `mainstream_quality` only, 88.5% / ~7.1k reviews, 50% discount; moderate scenario `ЛУЧШЕ ЖДАТЬ`.
- **Sayonara Wild Hearts** — `very_high_rating` only, 94.5% / ~3.7k reviews, 50% discount; moderate scenario `ЛУЧШЕ ЖДАТЬ`.

Use these as examples of **why an item is deferred from the first wave**, not proof it can never be good. If a protected lane (Wishlist, already authoritative Deep-fit, direct user reference, package/bundle lane, current DLC lane, or protected strong-commercial lane) applies, that protection overrides ordinary defer logic.

### B. PR #157: why it exists and why it diverged

PR #157:
`Steam shortlist scope reduction diagnostic 02`

Exact chronology:
- PR branch `diagnostic-steam-shortlist-scope-reduction-02` contains two commits:
  - `c9aa423...` — add diagnostic report;
  - `3abeb5e...` — record diagnostic completion.
- That PR's report is the **older recommendation**, around **784** families in a conservative first wave.
- After the PR was created, the worker performed a stronger Deep-fit recall backtest and wrote corrected report commits into **main**:
  - `6b79acb...` — report;
  - `9f3c879...` — corrected recommendation with Deep-fit recall backtest.
- The corrected `main` report recommends ~**581 first-wave + reserve**, not the older 784 permanent-style recommendation.
- `CURRENT_TASK.md` also moved independently in main.
- Therefore PR #157 is now `dirty`/conflicting: its branch contains an older version of files that were later changed directly in main.

Why PR #157 was created: the worker used a normal task branch/PR path for the report and CURRENT_TASK update. The later corrections were not applied back to that branch; they landed in main. Do not merge PR #157 blindly. First decide whether it contains any unique useful content not already superseded by main; likely outcome is close it as superseded after a bounded comparison.

### C. Why the previous Chat 2 message was too long

The Director over-packed the continuation prompt with state the worker can read from GitHub. Going forward, continuation prompts should contain only:
- repo/source of truth;
- exact task filename;
- one or two critical known blockers/state facts;
- explicit "continue, do not restart";
- explicit boundaries if necessary.

Do not restate the entire task specification in the chat message when the canonical task file already contains it.

- ЧАТ 1 historical backlog audit is accepted via PR #167. Five strong restoration candidates and three Director-decision cases were found; none are yet auto-restored. Physical slot is free.

- ЧАТ 1 complete/free: follow-up PR #172 merged as `31f5049c1366c59a125ed73db2e74cf5e77e1b72`; remaining `deep-site` / `deep-cutover` lifecycle assertions are canonical-plan-driven, and real Pages run #37803117331 succeeded.

- Deep site/UI PR #168 is accepted and merged as `ae06070f6e26ae8bdf7cf1864981b78c0e31cee7`; all Deep implementation prerequisites are complete and final integration/cutover is now unblocked.

- ЧАТ 2 is complete/free. Two-stage Dossier Research/Assembly architecture accepted via PR #171 (`290d31a52c00d9feea86ecfc78fdb1f037db66bb`). No implementation/activation yet; one GitHub queue owner and unchanged strict final Dossier validator remain mandatory.

- ЧАТ 2 complete/free: Dossier two-stage P1 contracts/schemas accepted via PR #173; P2 inactive GitHub staging/control-plane accepted via PR #175 (`ae92337ae5e8360ec15a4af4f85802bad39767b7`). Research intake validation, receipts, lifecycle state and accepted-only Assembly assignment are implemented but inactive/non-authoritative. One-stage Dossier remains production authority.

- ЧАТ 1 complete/free: commercial/Dossier isolation accepted via PR #174 (`a243b7bf61b2127a75491646ca1265fa5d13e149`). Fresh deterministic commercial data now persists before Dossier. Real pre-AI run #37909195575 and visual run #37909274274 succeeded. The first Pages deploy then failed only because Director registry metadata had invalid `order: 0`; that metadata is corrected separately.

- ЧАТ 1 complete/free: async Dossier amendment PR #177 merged as `d4a19c595fbd20cebe8f3f186c0afc1bfb63ff3f`. Research/Assembly can traverse frozen preauthorized buffers without per-item acknowledgement; GitHub validates prior outputs asynchronously. Buffer cap is 8 unresolved slots per phase; this is backpressure, not per-item acknowledgement. New path remains inactive/non-authoritative.
- ЧАТ 2 complete/free at semantic boundary: Deep integration preflight PR #176 merged as `a2eaeef1a3203585970b62cb548e801faa073bc4`. Cutover not performed. Current new Stage 1/Stage 2 accepted state is empty and Stage 2 has no approved bootstrap anchors. Next step requires explicit Director/user authorization for GitHub-prepared Stage 1 migration work and subsequent manual semantic execution; new two-stage Dossier remains inactive and is not a dependency.

- ЧАТ 1 complete/free: fully asynchronous Dossier PR #179 merged as `707e4b44a582fa11833fd17059e3cd413fe5d268`. Research and Assembly no longer wait on GitHub acknowledgements; Assembly may use exact immutable submitted Research bytes under frozen preauthorization; GitHub later validates/quarantines per-item chains. New path remains inactive/non-authoritative.
- ЧАТ 2 complete/free: Deep Stage 1 migration preparation PR #178 merged as `c429cead3788875e36f2596f2abb770307cd75cc`. Preview on worker snapshot: 245 current targets, 27 with current accepted Dossier ready for new Stage 1, 218 waiting/blocked, 0 accepted new Stage 1. Executable materialization is still blocked by canonical `mass_migration_authorized=false`; next step needs explicit authorization, then a separate manual Stage 1 semantic worker.

## CURRENT PHYSICAL WORKER SLOTS

### ЧАТ 1 — DIAGNOSTIC COMPLETE

Task:
`WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Status:
`diagnostic_complete_recommendation_ready`

Authoritative corrected report is already in `main`:
`reviews/worker_reports/steam-shortlist-scope-reduction-diagnostic-02.md`

Recommendation:
- ~581 first semantic wave;
- ~1,720 deferred reserve;
- do not permanently exclude reserve;
- do not implement until Director/user accepts semantics;
- future bounded implementation task proposed by report:
  `WORKER_TASK_STEAM_SEMANTIC_FIRST_WAVE_AND_RESERVE_IMPLEMENT_01.md`.

PR #157 remains open but conflicts with main and contains an older report variant. Do not merge it blindly.

ЧАТ 1 physical slot is available after the Director resolves/records the PR #157 disposition.

### ЧАТ 2 — STAGE 2 ACCEPTED / CONTINUE STAGE 1

Accepted task:
`WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`

Accepted PR:
`#159` merged as `06aeeda19bf550899fd690f08f413e58d6f33b1d`

Deep Stage 1 is accepted and merged via PR #163 as `e410ee6183e29ec595f2c1fce1336751ceea9585`.

Deep Fast-removal/ranking migration preparation is accepted via clean replacement PR #166 (`4d1cfb4745989994051f6233a3810759f1f1a305`). Old #164 is closed superseded. The new scorer remains non-active until cutover; remaining Deep prerequisite is the separate mirror UI/Statistics implementation. Physical ЧАТ 2 is free.

Branch:
`implement/deep-stage2-calibration-worker-01`

Known work already present on branch:
- Stage 2 manual worker prompt;
- Stage 2 work manifest;
- state file;
- validation workflow;
- partial implementation start.

Latest known branch head:
`8e674ea33ecc2710acc2bb1946ab741a0971e06d`

Known failed validation:
`Validate Deep Stage 2 calibration` run `37509068199`

Immediate failure:
workflow compile step references missing `scripts/deep_stage2.py`.

No Stage 2 PR or final worker report existed at the last Director check.

Correct continuation style for ЧАТ 2 should be short, e.g.:

```
Продолжай текущую задачу:
WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md

Рабочая ветка уже есть:
implement/deep-stage2-calibration-worker-01

Не начинай заново. Последняя проверка 37509068199 упала на отсутствующем scripts/deep_stage2.py.
Продолжи реализацию, добей проверки, создай PR и worker report.

Не переходи к следующей задаче.
```


## CURRENT TURN HANDOFF — 2026-10-09

- User stopped this Director chat because context limit was reached.
- Pending Director action: complete acceptance of PR #179 and PR #178; neither had been merged at the last check.
- PR #179 checks green: inactive Dossier two-stage interfaces, execution ownership, site publication resilience, Progressive PASS 2 core, backlog dispositions. Core result: no fixed unresolved-slot liveness gate; Assembly can use exact submitted Research bytes before GitHub Research acceptance; GitHub validates/quarantines the item chain later; one-stage Dossier remains production authority.
- PR #178 checks green: Deep Stage 1 migration preparation + backlog dispositions. Real-data preview last reported 245 current targets, 27 with current accepted one-stage Dossier eligible for Stage 1, 27 requiring Stage 1 semantics, 218 waiting/blocked, 0 accepted new Stage 1. Preview is non-executable because canonical migration contract still has `mass_migration_authorized=false`.
- Do not confuse the 27-item current eligible preview with a permanent quota; rerun from current main at authorization/materialization time.
- User explicitly wants Fast removed. Actual Fast production authority must disappear at the final atomic Deep cutover, after valid new Stage 1 and Stage 2 semantic authority exists. Fast-free ranking preparation is already accepted; current production Fast must not be removed prematurely.
- No Scheduled Task changes authorized.

## CRITICAL START RULE FOR THE NEXT DIRECTOR

Do **not** reconstruct the project by roaming through the entire repository.

Do **not** enumerate all PRs, branches, workflow history, old worker reports, or old Board sections just to rebuild context.

Preserve context and token budget.

Start in this order only:

1. Read current `DIRECTOR_PROTOCOL.md` and `CHAT_PROTOCOL.md`; perform only the required Director START gate.
2. Read this file fully.
3. Read only the top/current section of `DIRECTOR_TASK_BOARD.md`.
4. For a concrete user request, open only the exact task/report/config/artifact referenced here or by that request.
5. Inspect wider GitHub history only when there is a specific contradiction, missing fact, failed check, or explicit user request.

Treat old Board sections as historical unless this handoff explicitly points to them.

## CURRENT PHYSICAL WORKER SLOTS

### ЧАТ 1 — ASSIGNED / NEW PHYSICAL CHAT

Task:
`WORKER_TASK_STEAM_SHORTLIST_SCOPE_REDUCTION_DIAGNOSTIC_02.md`

Mode:
`READ-ONLY / DIAGNOSTIC / OFFLINE SIMULATION`

Current fresh funnel is roughly 60,632 paid eligible -> 7,972 broad -> 2,522 paid shortlist -> ~2.3k Dossier/Deep semantic target. The user wants ЧАТ 1 to analyze how to reduce this much further without restoring the old accidental shrinkage caused by broken review enrichment.

The task must quantify which admission rules create the current explosion, simulate safer stronger gates, protect Wishlist/packages/known-good candidates, and compare conservative/balanced/aggressive semantic-pool sizes. No implementation.

### ЧАТ 2 — ASSIGNED / SOLE DEEP LOGIC OWNER

Current task:
`WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`

The user explicitly wants one physical worker chat to carry the Deep logic changes forward to avoid split logic ownership.

Sequence in this same physical chat, with separate task boundaries/reports/PRs:
1. finish `WORKER_TASK_DEEP_STAGE2_CALIBRATION_WORKER_IMPLEMENT_01.md`;
2. then implement `WORKER_TASK_DEEP_STAGE1_WORKER_IMPLEMENT_01.md`;
3. then implement `WORKER_TASK_DEEP_FAST_REMOVAL_RANKING_MIGRATION_01.md`.

Do not merge these into one uncontrolled PR. Close/validate each task cleanly before the next.

ЧАТ 1 must not touch Deep logic while this assignment stands. Site/UI remains a later separate implementation task. Production authority remains unchanged until final integration/cutover.

## CURRENTLY WORKING / RECENT SEMANTIC CHATS

These do **not** occupy physical ЧАТ 1/2 slots.

### Russian-description manual semantic worker — STOPPED AFTER INGEST FAILURE

Canonical prompt:
`config/russian_description_manual_semantic_worker_prompt.md`

A one-shot run was authorized and submitted checkpoint 1, but canonical ingest rejected the checkpoint. Do not retry or retranslate it in the semantic worker.

Relevant commits:
- authorization: `30f59b693cdef3eca520ddc78334850fdf850948`;
- checkpoint 1 submission: `32caa3b35fb750cd31da7198f28e34855928edd6`.

Current confirmed result after checking ingest:
- ingest run `37138503097` failed at `Validate and ingest current submissions`;
- exact failing item observed: AppID `1237980`, request `2aeac6b...`, translated result failed the `good_ru` gate;
- canonical cache/status did not persist checkpoint 1;
- current queue remains 82 and the last successful translation timestamp remains 2026-10-01 at the Director check.

Do **not** tell the semantic worker to redo checkpoint 1. ЧАТ 2 now owns the user-authorized implementation that will isolate bad items, accept valid siblings, create translation diagnostics, and reconcile the existing checkpoint without retranslation.

No Scheduled Task action is authorized.

### Progressive Deep semantic worker — ACTIVE / RECENT

A current Deep invocation started and has begun submitting results.

Relevant commits:
- run start: `0b47a0fe3830dfbcec37fa5a2395d6be08169067`;
- result AppID 1577120: `7005c0f0901e33e087494c92617bbe1e71b2bf0c`;
- result AppID 1237980: `0622b86499dab789711b07ab7f08270eb0bda0e3`.

Current PASS 2 manifest observed at handoff had 23 items.

Do not rebuild, reorder, or restart Deep scope. If the user asks for status, inspect the current canonical PASS 2 work and the latest exact worker/result commits only.

### Dossier semantic worker — ACTIVE / RECENT

The frozen-authority behavior is already on `main` and recent Dossier work is progressing.

Canonical snapshot at handoff:
`a9a1390c7821fcc69c06f83e57c0297df0016e0d90e637ddccd7185d53bd8b19`

Observed current progress:
- next_pending_sequence: 5;
- accepted_group_count: 4;
- pending_group_count: 127;
- accepted_dossier_count: 12;
- pending_dossier_count: 379;
- failed_group_count: 0.

Recent commits:
- group 3 buffered: `391afad22736b6dd3ca0990eff480fecd3af228d`;
- group 3 ingested/reconciled: `1782812ec194cd8d78cd30c83d1a588008177bed` / `79f5e476774d122ba802655407d57ad54f3e3957`;
- group 4 buffered: `98f10a2c2f5c934b7c1ae3d890d8c490c7544d2c`;
- group 4 ingested: `1ae9bc6e55304ca5d773fb3a8b0b3f8e688003a1`.

Do not assume these counts remain current; if asked, read only the current worker index.

## MIRROR'S EDGE CATALYST — DIAGNOSIS COMPLETE

User-visible symptom:
Mirror's Edge Catalyst (AppID `1233570`) still did not appear after PR #140.

Do not re-diagnose.

Worker conclusion:
`diagnosis_complete_root_cause_identified`.

First causal stage:
**fresh Steam KZ discovery does not complete/persist**.

Key result:
- a real post-PR-#140 production discovery run did execute on `main`;
- run `37120664964` was cancelled at the 60-minute collector timeout;
- live Steam still exposed about `100307` rows despite the PR #140 `category1=998,21,996` bounding attempt;
- canonical discovery therefore remained the stale 2026-09-23 universe;
- Catalyst never reached shortlist, mailing, pre-AI, semantic work, ranking, or Pages.

Important split conclusion:
- PR #140 freshness/fail-closed guards are working;
- PR #140's live discovery-input bounding is not sufficient against current Steam behavior;
- live acceptance was attempted and failed in discovery itself;
- this is not a Dossier/Deep/ranking/Pages problem.

Smallest next action from the worker:
a bounded implementation task on the **existing Steam KZ production shortlist owner only** to make live discovery input/traversal actually bounded enough to finish inside the existing production cycle, with no Catalyst special case and no second scheduler/collector.

**Do not create that implementation task until the user authorizes fixing it.**

## RECENT ACCEPTED IMPLEMENTATIONS — DO NOT REOPEN WITHOUT NEW EVIDENCE

- PR #140 — fresh deal discovery freshness handoff:
  merge `7df5ed0cbe9dd9217c56344e0caab47dd366915f`.
  Freshness guards accepted; live discovery bounding remains the newly diagnosed unresolved part above.

- PR #141 — isolate PR validation from production `workflow_run` triggers:
  merge `da71fb7578c5fe467da0ce8e3decfbc62a6465a4`.
  PR validation can no longer masquerade as production authority.

- PR #143 — Dossier frozen invocation rollover safety:
  merge `a354500fc83d20fff89d19c0752aa2810898861e`.
  Already-started legitimate Dossier work no longer dies merely because a later daily snapshot replaces the current projection.

- PR #125 — Russian translations nonblocking + Statistics observability remains accepted.

- RANK-013 and accepted score/ranking architecture remain closed unless the user explicitly reopens them.

## IMPORTANT USER OPERATING RULES

- Director delegates implementation/diagnostics to worker chats; do not directly implement when user says “исправляем/делаем”.
- Historical two-slot limit is superseded: no fixed physical-worker cap; assign unique `ЧАТ N` under current `DIRECTOR_PROTOCOL.md` §10.
- Semantic workers (Dossier, Deep, manual translation) do not consume those physical slots.
- User remains operator of semantic runs/Scheduled Task UI.
- Never create/modify Scheduled Tasks unless explicitly requested.
- GitHub is source of truth.
- Explain simply in Russian.
- When checking a chat, prefer a narrow status check: branch/PR/report/latest checks. Do not inspect raw logs unless needed.
- Bootstrap for a physical worker must say `ЧАТ N`, point to the exact `WORKER_TASK_*.md`, and tell it not to start other tasks.
- Full task instructions belong in GitHub task files, not in the bootstrap.
- Concurrent GitHub writes are normal; never overwrite newer canonical production state.

## IMMEDIATE DIRECTOR PRIORITIES

1. Preserve and monitor the currently active semantic translation / Deep / Dossier work without restarting it.
2. If user asks about Catalyst, report the completed diagnosis above; do not redo it.
3. If user says to fix Catalyst/discovery, create a new bounded implementation task for a free physical slot, based on the completed diagnostic report.
4. If user asks about translation status, first check whether checkpoint 1 was ingested and then use the fresh canonical queue/status.
5. If user asks about Dossier or Deep status, inspect only their current exact canonical index/work/results.

## HANDOFF SNAPSHOT

Final observed recent `main` activity included:
- Deep result AppID 1237980: `0622b86499dab789711b07ab7f08270eb0bda0e3`;
- Catalyst diagnostic closeout: `62cf27a2ef7fd4c3312fe9b4a629bc4f539434d8`;
- Dossier/PASS2 reconciliation: `fb9bf4efa3445cbd27fc148035bd1b32e369e0d0`;
- Russian translation checkpoint 1 submission: `32caa3b35fb750cd31da7198f28e34855928edd6`.

This snapshot is descriptive only. Always trust newer exact canonical state if it has advanced.

## CONTEXT-CONSERVATION RULE

The next Director should assume this handoff is correct unless a **specific** current check contradicts it.

Do not spend context proving settled history again.

Do not fetch dozens of files “for completeness”.

Read the one exact file needed for the user's current question, answer it, and preserve the rest of the context window for actual decisions.
