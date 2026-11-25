# НОВЫЙ ЧАТ 3 — исправление путей Lean auto-writer

Task ID: dossier-lean-writer-auto-path-layout-fix-01
Repository: kentrap2011-hub/steam-kz-deals-2
Base branch / source of truth: main
Worker: NEW PHYSICAL ЧАТ 3
Mode: bounded FIX + source PR + offline tests. No self-merge or live writer run.

## START
1. Работай ТОЛЬКО в `kentrap2011-hub/steam-kz-deals-2` по актуальному `main`; другие репозитории запрещены. При ошибочном GitHub target сразу STOP и скорректируй его.
2. Сначала ПОЛНОСТЬЮ прочитай `CHAT_PROTOCOL.md` из live main и выполни START gate, затем `CHAT_CONTEXT.md`, этот task, релевантные `PROJECT_ROUTES.md`, `PROJECT_DECISIONS.md`, `KNOWN_WORKER_PITFALLS.md`, `config/execution_ownership_contract.json`, `config/dossier_lean_writer_auto_ready_v1.json` и точные runtime/writer контракты. До workflow/runtime правки выполни architecture preflight.
3. Источник ошибки — завершившийся FAILURE реальный GitHub Actions run `45628656098`, job `139255581611`, `main@4ccf23005166a1ae3c35800e1b38e0c295e29d8e`. Дословная ошибка: `LEAN_AUTO_READY_TERMINAL_OR_PRECHECK_BLOCKED: V2 single-item paths must be separate writer-owned subdirectories`. Сверь текущую действительность и минимальный лог. Это новая стадия после устранения ложных проверок GitHub push payload в PR #488; не переоткрывай широкую диагностику event metadata.
4. Предыдущий ручной run #45540222575 и owner auto runs #45591943959 и #45603534459 failed; не повторять. Последний run #45628656098 также НЕЛЬЗЯ rerun. Перед любым выводом об autorun проверь по живым Git refs, создавался ли одноразовый `dossier-lean-auto-attempts/` claim, и состояние frozen sandbox `refs/heads/sandbox/dossier-notes-v2-assembly-replay-cdcdb4951e2fc98336729af75b954da4` (последнее известное SHA `d1b9a9e78dcde879a03370682ade4969763fd9d1`); не предполагай, что claim свободен, без доказательства. На последнем readback было 0/6 accepted docs и receipts.
5. Текущий Lean auto config уже `activation_enabled=true`; `automatic_retry_after_failure=false`, историческое право на новую recovery не расширять, future opt-in отдельно, глобальные Lean/Deep/production выключены.

## Bounded action
A. Адресно сравни writer-owned single-item destination paths, которые требуют V2 acceptance/manifest, и фактические paths/режим, переданные auto-writer. Укажи точную несовместимость и источник инварианта, без нового Research/Assembly.
B. Сделай минимальный source FIX для этих путей либо выбора штатного writer mode. НЕ отключай проверку раздельных поддиректорий и не ослабляй namespace/relative-path, parent traversal, SHA/edition/year/TTL, source safety, actor/grant/one-use claim, shared writer concurrency и atomic 6 docs + 6 accepted receipts. Strict/manual V1/V2 regressions должны сохраниться.
C. Подтверди targeted offline fixture с настоящей временной Git-структурой и валидными frozen-six paths; негативные тесты для неверного расположения, пересечения writer-owned dirs и старого manual/strict mode. Используй существующий GitHub CI и финальный exact-HEAD PASS; не вводи новые аудит-стадии/Actions без оснований.
D. Не создавай искусственный активационный `config.status`-diff или новый owner grant в source fix. ПЕРЕД любой последующей реальной попыткой выясни, был ли последний run preclaim или postclaim. Если claim расходован либо нет действующего разрешения, STOP с точным blocker; никаких скрытых retry/recovery. Дальнейший live GitHub event только через отдельный подтверждённый канонический owner path после директорской source приёмки.
E. ЗАПРЕЩЕНО: self-merge, workflow_dispatch, rerun любого failed Actions, отдельные writer/Research/Assembly/Deep/production job, Scheduled Tasks, массовая очередь, изменение живого sandbox, генерация новых семантических результатов, пользовательские ручные JSON или GitHub Actions. При риске несовместимой authority STOP, не обходи проверки.

## DELIVERABLE / STOP
Один узкий source PR от live main и `reviews/worker_reports/dossier-lean-writer-auto-path-layout-fix-01.md` с точными ошибочными и ожидаемыми путями, выясненным claim state, changed paths, тестами, exact-final-HEAD CI, границами и одним следующим решением директора. Worker возвращает `SOURCE_READY_AWAITING_DIRECTOR_MERGE` либо точный `BLOCKED_...`. Не объявлять реальную активацию без нового Actions run ID и immutable postpush sandbox 6+6 readback. Поручение пользователя — сменить исполнителя на новый ЧАТ 3; предыдущий ЧАТ 2 не должен продолжать этот FIX.
