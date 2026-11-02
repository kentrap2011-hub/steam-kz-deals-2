# НОВЫЙ ЧАТ 1 — исправление nine rejected Dossier V1 source-binding masks
Repository: kentrap2011-hub/steam-kz-deals-2
Source of truth: main
Task ID: dossier-v1-exact-product-binding-null-mask-implement-01
Mode: BOUNDED IMPLEMENT + offline regressions; ONE draft source PR
Report: reviews/worker_reports/dossier-v1-exact-product-binding-null-mask-implement-01.md

Полностью прочитай CHAT_PROTOCOL.md, выполни START gate. Затем task, релевантные owner/worker/schema/web evidence/pin contracts и завершённый отчёт reviews/worker_reports/dossier-v1-rejected-buffers-exact-product-binding-root-cause-01.md из PR #367 HEAD e787c5df924f2255ad31e56b5472e95b00c12574. Это уже доказанная причина, НЕ новый общий аудит и НЕ semantic execution.

Проверенные факты: 9 submitted groups Dossier V1 (27 dossiers), 0 canonical accepted. 72/72 exact_product_binding objects нарушают basis-specific field masks: 57 source_appid с лишними non-null title/release_year; 15 source_title_release с лишним appid. Strict GitHub validator и canonical web evidence contract корректны, ошибка формируется semantic worker-ом и insufficiently explicit source serialization instruction.

Реализуй ровно одну рекомендацию отчёта PR #367: уточнить config/taste_steam_review_dossier_worker_prompt.md непосредственно после перечисления allowed bases. Все четыре keys basis,appid,title,release_year должны присутствовать: source_appid -> source-proven exact appid, title:null, release_year:null; source_title_release -> appid:null, actual-source title/release_year; source_appid_title_release -> все три поля only with genuine source-evidence all three. Дать три коротких точных JSON примера. Дополнительные непустые поля при неверном basis — ошибка strict ingest. Не придумывать AppID по поисковому запросу, не копировать название/год из dossier, не смешивать base/edition/DLC.

Разрешённый source write set: config/taste_steam_review_dossier_worker_prompt.md; один существующий адресный offline test file scripts/test_taste_dossier_pragmatic_evidence_model.py (либо существующий prepublication test только если доказана необходимость); один worker-report reviews/worker_reports/dossier-v1-exact-product-binding-null-mask-implement-01.md. НЕ менять contract, strict validator, schema, runtime/launcher, queue, marker, writer, ownership, production, Dossier V2, Deep, Scheduled Tasks или GitHub Actions; НЕ републиковать/исправлять immutable quarantine.

Positive fixtures: корректная AppID-only, title/year-only, all-three с реально подкреплённой identity; 3-dossier frozen group; strict validator pass. Negative: historical g1/g2/g7 source_appid+extra title/year, g6/g9 source_title_release+extra appid, wrong exact AppID/edition/title/year, one malformed source among correct, query-only attribution, wrong marker/descriptor. Test strict failure, preserve zero acceptance; do not hardcode current production AppIDs in generic CI. PITFALL-006 prompt SHA/pin change: document existing GitHub reprepare compatibility, never rebind old descriptor to new hash.

Record actual executed offline tests and CI exact final HEAD, risk/rollback, and one targeted independent L2/L3 delta QA (source evidence binding risk). ONE draft implementation PR. Verdict READY_FOR_INDEPENDENT_DELTA_QA or BLOCKED_EVIDENCE; no worker self merge/real semantic run. Later manual one-shot requires NEW explicit user launch after canonical GitHub work refresh.
