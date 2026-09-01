# Worker report — compact-purchase-options-01

Дата: 2026-09-01  
Статус: `complete`

## Scope

Выполнена только UI-задача G из `CURRENT_TASK.md`: компактное отображение вариантов покупки с одним producer-selected вариантом по умолчанию и полным списком по запросу пользователя.

Taste semantics, package eligibility/economics, commercial source values, score/ranking math и producer-owned выбор purchase route не изменялись.

## Изменённые файлы

- `web/package-deal-ui.js`
- `web/package-deal-ui.test.js`
- `web/purchase-options.css`
- `web/index.html`
- `.github/workflows/deploy-visual.yml`
- `CURRENT_TASK.md`
- `reviews/worker_reports/compact-purchase-options-01.md`

## UI: было

- `ВАРИАНТЫ ПОКУПКИ` показывал сразу package explanation и все standalone/DLC варианты;
- длинный package composition/economics занимал значительную высоту мобильной карточки;
- пользовательский текст мог раскрывать внутреннюю score/ranking терминологию вроде «балл покупки» вместо практического ответа, что выгоднее купить.

## UI: стало

- при наличии нескольких вариантов в свернутом состоянии показывается ровно один рекомендуемый вариант;
- primary route берётся из уже рассчитанного producer-owned `score_breakdown.purchase_route`: `fixed_package` показывает пакет первым, иначе первым остаётся основной standalone offer;
- UI не сравнивает цены заново и не переигрывает producer route;
- под primary показывается явная кнопка `Показать ещё N вариант/варианта/вариантов`;
- раскрытие показывает все остальные доступные regular offers и полный подтверждённый состав/объяснение fixed package;
- для primary package длинный состав вынесен только в раскрытое состояние;
- техническая score/rank терминология заменена практическим пользовательским объяснением вида «рекомендуемый способ покупки», «отдельная покупка сейчас не хуже по совокупной выгоде»;
- добавлены отдельные компактные mobile-friendly disclosure styles.

## Regression coverage

`web/package-deal-ui.test.js` детерминированно проверяет:

1. collapsed package omits long composition details;
2. expanded package сохраняет полный подтверждённый состав, incremental/unpriced/nonpersonalized content и purchase-equivalence note;
3. visible copy не содержит `балл покупки`, `получает не меньший`, `поднимает игру в рейтинге`, `влияние на рейтинг`;
4. collapsed visible package text существенно короче full state (`< 60%` длины контрольного текста);
5. collapsed purchase block при нескольких вариантах содержит ровно одну offer-card и hidden disclosure;
6. `fixed_package` producer route остаётся primary;
7. standalone producer route остаётся primary даже если в test fixture локально сделать package price искусственно ниже;
8. `fixed_package` producer route остаётся primary даже если package price искусственно сделать выше;
9. expanded state сохраняет package + все regular purchase options;
10. disclosure toggle корректно меняет `hidden`, `aria-expanded` и текст кнопки;
11. late-loaded `package-deal-ui.js` действительно переопределяет app-level `renderOffers`, поэтому компактный renderer используется в текущей карточке.

Локальный deterministic run перед публикацией: `compact purchase options mobile regression: PASS`; JS syntax checks прошли.

## CI / deploy acceptance

- feature renderer commit: `fe8d99f2d202403f092cd072bb598c6f3fd969b4`;
- regression commit: `78ee55bc08a8833aac3a40cd768e836f88c96393`;
- mobile disclosure styles: `fa83828df7db15afc7953a23c5821989038cd082`;
- asset wiring: `526107bf431cb7c861c11d868b12bf2555d33196`;
- deploy workflow regression gate: `368224ca162f83b48cad32651fe42dde6d013c8a`;
- deploy run: `33489817719`, rerun job `99798942975`: `success`;
- `Run UI regressions`: `success`;
- `Deploy to GitHub Pages`: `success`;
- Pages artifact: `9793337134`, digest `sha256:efac9c7abb9f13c1ac8d7bbe489b0f98bb28bee1cde34bfa10e9edc8e12077f9`.

Первый attempt этого deploy был cancelled только из-за существующего `concurrency: pages`, когда его вытеснил более новый workflow event. Тот же cancelled deploy job был rerun без изменения feature-кода и прошёл полностью.

## Сохранённые инварианты

- fixed-package eligibility не менялась;
- dynamic/personalized Complete-the-Set exclusion не менялся;
- exact included appid / verified directional purchase equivalence не менялись;
- package economics и comparable entitlement valuation не менялись;
- Taste не зависит от цены и не менялся этой задачей;
- score/ranking math не менялся;
- UI использует producer-owned purchase route и только отображает уже подготовленные commercial данные;
- unknown/unpriced/nonpersonalized content по-прежнему не получает выдуманную стоимость;
- Season Pass / constituent double-count protection не менялась.

## Остаточные риски

- regression является deterministic DOM/string structural mobile guard, а не pixel-perfect browser screenshot. Он защищает ключевые требования задачи: один видимый primary, hidden expanded state, полный expanded content и существенное сокращение collapsed текста.
- известных функциональных блокеров для этой задачи нет.

Следующая planned-задача не начиналась.
