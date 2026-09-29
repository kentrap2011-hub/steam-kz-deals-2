# WORKER TASK — KOF XV MISSING POSITIVE REASONS DIAGNOSTIC 01

Repository: `kentrap2011-hub/steam-kz-deals-2`
Base branch / source of truth: `main`

Task ID: `kof-xv-missing-positive-reasons-diagnostic-01`
Mode: `READ-ONLY / RECON`
Worker slot: `НОВЫЙ ФИЗИЧЕСКИЙ ЧАТ — ЧАТ 1`

Durable report:
`reviews/worker_reports/kof-xv-missing-positive-reasons-diagnostic-01.md`

## User symptom

On the current live card for:
- title: `THE KING OF FIGHTERS XV`
- AppID: `1498570`
- family: `game:1498570`

the game is near the top of the feed, but the block `Почему может зайти` shows the placeholder:

`Персональная причина пока не подготовлена.`

The user considers this semantically wrong because the system already ranks the game highly as a fit.

## Already verified facts — do not rediscover from scratch

Current canonical Fast/PASS1 state for `game:1498570` contains:
- `outcome = analyzed_fit`
- `fit_level = moderate`
- `confidence = medium`
- non-empty `positive_evidence`
- detailed `taste_factors`

The accepted Fast positive evidence explicitly says:
1. the pinned profile shows strong enjoyment of fighting games with distinctive fighters and rewarding character mastery, citing Tekken 3 and Ultimate Mortal Kombat 3 rated 4/5;
2. KOF XV is a fast 3-on-3 fighter with a large varied roster and mastery-oriented systems matching those preferences.

Current Dossier `data/cache/taste_steam_review_dossiers/App_1498570.json` is also valid and contains positive observations about:
- fast combo-focused 3-on-3 combat;
- substantial mastery depth;
- large roster / team combinations / long-tail variety.

Therefore this is **not** a request to invent positives and not primarily a ranking-policy question. The diagnostic must trace why already-existing grounded positive evidence does not reach the visible card.

## START gate

First read current `CHAT_PROTOCOL.md` from `main` and fully execute its START gate.

Then read this task fully and create the required checklist.

Read minimally:
1. `CHAT_CONTEXT.md`;
2. current top of `DIRECTOR_TASK_BOARD.md`;
3. `PROJECT_ROUTES.md` sections for Progressive visual/card explanation;
4. relevant current decisions, especially the current positive-card explanation/provenance policy;
5. `config/execution_ownership_contract.json`;
6. current canonical Fast/PASS1 state for `game:1498570`;
7. current canonical Dossier for `App_1498570`;
8. current canonical Deep/PASS2 state for this family, if any;
9. current canonical visual card for `game:1498570`;
10. the exact producer path that selects semantic authority and creates `why_fit` / positive explanation fields;
11. the exact final visual mapping/validation path;
12. browser rendering only as needed to prove whether the loss is producer-side or display-side.

Do not inspect unrelated project history.

## Required diagnostic questions

Answer all of these with exact current GitHub evidence.

### A. What semantic authority is currently selected for KOF XV?

Determine exactly which layer the current visual producer uses for `game:1498570`:
- current authoritative Deep;
- current Fast;
- reusable Taste cache;
- fallback/unresolved state;
- or another documented path.

Do not infer this from icons alone.

### B. Where do the positives exist?

Pin the exact current fields containing positive evidence before card generation:
- semantic result;
- Dossier if relevant;
- selected semantic/taste entry;
- any intermediate projected structure.

### C. First divergence

Trace one exact KOF XV record through:

`accepted semantic state -> selected semantic entry -> card explanation policy -> intermediate visual -> final canonical visual -> web/data/current.json -> browser rendering`

Find the **first exact boundary** where the positive evidence is:
- dropped;
- rejected;
- considered stale/unbound;
- replaced with a compatibility projection;
- filtered by provenance validation;
- overwritten;
- or rendered incorrectly.

Do not stop at “the UI shows placeholder.” Identify the first causal divergence.

### D. Is fail-closed behavior correct or defective?

If the positive evidence is intentionally rejected by a provenance/binding guard, determine:
- which exact guard;
- which required binding mismatches or is missing;
- whether the upstream semantic state genuinely lacks required proof, or whether a downstream transform loses proof that already exists.

Do not weaken provenance rules in the diagnostic.

### E. Scope

Determine whether the defect is:
- only KOF XV;
- only Fast cards;
- only Fast cards from a particular generation/compatibility path;
- only cards whose Dossier arrived after Fast;
- or a broader Fast/Deep positive-explanation projection defect.

Use a small deterministic comparison set:
- KOF XV as the pinned broken case;
- at least one current visible card whose `Почему может зайти` displays correctly;
- if useful, one other card with non-empty semantic `positive_evidence` but placeholder output.

Do not perform an unbounded catalogue audit unless needed to establish the class of defect.

### F. Ranking relationship

Confirm whether the missing positive text changes the ranking score/order or is only a presentation/projection problem.

Do not redesign ranking in this task.

## Hard boundaries

READ-ONLY diagnostic:
- do not modify production code;
- do not modify contracts;
- do not modify semantic results;
- do not rerun Fast/Dossier/Deep;
- do not change ranking;
- do not change publication;
- do not change UI;
- do not create implementation PR;
- do not create or modify Scheduled Tasks or automations;
- do not interfere with the concurrently running manual Russian-description semantic worker;
- do not rewrite current visual/data merely to test a theory.

The only durable write permitted is the required diagnostic report.

## Required report

Write:
`reviews/worker_reports/kof-xv-missing-positive-reasons-diagnostic-01.md`

Required sections:
1. `Task`
2. `Pinned symptom`
3. `Current semantic authority for KOF XV`
4. `Positive evidence before projection`
5. `Exact projection chain`
6. `First divergence / root cause`
7. `Why the placeholder appears`
8. `Affected scope`
9. `Ranking impact`
10. `What is healthy / do not reopen`
11. `Unresolved`
12. `Status`
13. exact file/blob/commit references
14. `Recommended next step` — exactly one smallest bounded IMPLEMENT task if a fix is needed
15. `Efficiency / reusable lesson`

Allowed final statuses:
- `diagnosed_needs_fix`
- `no_defect_current_state`
- `needs_user_decision`
- `blocked`

Do not start implementation after diagnosis.
