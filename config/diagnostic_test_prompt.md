# Diagnostic production test prompt

Проведи fail-fast diagnostic production-test игровой рассылки.

Обязательный порядок загрузки:

1. Первым содержательным файлом из репозитория через прямой GitHub connector загрузи `kentrap2011-hub/steam-kz-deals-2`, ветка `main`, файл `config/mailing_policy.json`.
2. Зафиксируй canonical policy version и Git blob SHA. Никакие старые правила из памяти не используй.
3. Только после canonical policy загрузи `config/diagnostic_runner.json` из того же репозитория и ветки.
4. Diagnostic runner является только test harness: при любом конфликте canonical `mailing_policy.json` имеет безусловный приоритет.

После этого запускай стадии из `diagnostic_runner.json` строго по порядку, автоматически переходя к следующей только после полного PASS текущей стадии.

Для каждой стадии действует её `limit_seconds` (по умолчанию 60 секунд). Это диагностический порог, а не production SLA.

Немедленно останови весь run на первой стадии, если выполняется хотя бы одно условие:

- стадия превысила активный лимит времени;
- произошла ошибка инструмента или данных;
- обязательный результат неоднозначен или не доказан полностью;
- нарушен canonical policy invariant;
- фактические count/schema/coverage не совпали с обязательными;
- полная проверка требуемого множества не завершена.

Нельзя экстраполировать результат с проверенной части на непроверенную. Нельзя объявлять unchecked rows cache hits/misses. После первого FAIL не загружай и не выполняй downstream-стадии.

После исправления проблемы следующий тест всегда должен начинаться снова с canonical policy и стадии 01, а не продолжаться с места остановки.

Сохраняй canonical checkpoint/write order. Не делай дополнительных debug writes. GitHub writes разрешены только там, где их разрешает canonical policy.

Особенно для taste-cache:

- confirmed cache hit требует exact key + exact profile blob SHA + exact taste model version + exact price-blind fingerprint;
- confirmed hits нельзя семантически переоценивать;
- `entry_count` сам по себе ничего не доказывает;
- full fingerprint validation обязана покрыть весь текущий feed;
- Store/SteamDB/deal-quality/content-family downstream запрещён до достижения обязательного taste checkpoint.

Для внешних Store/SteamDB lookup используй единый lookup registry и не повторяй provider+exact-key в рамках run. Не запускай новый lookup, если стадия уже явно близка к превышению лимита и это помешает корректно остановиться с отчётом.

На каждом PASS веди компактный stage ledger по схеме из diagnostic runner. Пользователю не нужно показывать названия исключённых кандидатов или промежуточный список игр.

Если стадия FAIL — сразу выдай технический отчёт и остановись. В отчёте обязательно укажи:

- canonical policy version/blob;
- последний успешно завершённый этап;
- первый failed stage id/name;
- тип FAIL (`FAIL_TIMEOUT`, `FAIL_ERROR`, `FAIL_AMBIGUOUS` или `FAIL_POLICY`);
- elapsed и active limit;
- input / processed / remaining counts, если применимо;
- external calls attempted/succeeded/failed;
- GitHub writes, которые реально успели состояться;
- какие downstream stages не запускались;
- изменилось ли что-либо в persistent cache;
- одну конкретную следующую проблему, которую нужно анализировать/оптимизировать.

При любом FAIL обычную игровую рассылку не публикуй.

Если все diagnostic stages и canonical final_self_check прошли PASS, выдай полный stage timing ledger и `final_self_check = PASS`. Только полный PASS разрешает считать production pipeline успешно пройденным.
