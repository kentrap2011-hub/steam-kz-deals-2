# WORKER TASK — CHAT 2

Task ID: `card-negative-analysis-gap-01`
Mode: `READ-ONLY / RECON`
Report: `reviews/worker_reports/card-negative-analysis-gap-01.md`

## Goal

Explain why some production cards can reach the user-facing UI without any grounded, confirmed negative/cons evidence, and define the smallest generic fix.

User rule:
- a normally completed game analysis should contain at least one concrete, grounded downside/negative;
- `no grounded negative evidence` is NOT a normal completed card state;
- wording such as `минус не выявлен`, `рисков не найдено`, or equivalent fallback must not masquerade as an objective property of the game;
- do not invent a negative just to fill the card.

This task is diagnosis only. Do not redesign the whole card explanation system and do not manually curate games.

## Read first

- `reviews/worker_reports/card-explanation-fix-01.md`
- `reviews/worker_reports/card-explanation-production-acceptance-01.md`
- `CHAT_PROTOCOL.md`
- relevant `PROJECT_ROUTES.md`
- relevant `KNOWN_WORKER_PITFALLS.md` entry only if a trigger matches
- canonical current card-negative/risk producer and payload fields only as needed
- current generated production payload / bounded sample only as needed

Do not perform broad history archaeology.

## Required questions

### 1. Canonical ownership

Identify the exact current route that owns:
- negative evidence / risk inputs;
- `risk_codes` / `risk_status` or their current equivalents;
- visible user-facing negative/cons text;
- final visual payload state when no grounded negative exists.

### 2. Current production incidence

Using a bounded programmatic count/sample, determine:
- how many current production cards have at least one grounded visible negative;
- how many have no grounded visible negative;
- how many are shown with filler/neutral/no-negative wording;
- whether the issue is rare or systemic.

Do not inspect the catalog item-by-item manually.

### 3. First missing-evidence point

For a bounded sample of cards with no grounded negative, trace the first point where the expected negative evidence is missing or discarded.

Classify causes such as:
- no source evidence collected;
- evidence exists but provenance/grounding rejects it;
- semantic-analysis queue/gap;
- evidence mapped to heuristic-only state;
- stale/missing upstream data;
- producer/final-payload suppression bug;
- another concrete cause proven by the route.

Do not infer a cause from final absence alone.

### 4. Correct product semantics

Define a generic state model that preserves both requirements:

A. completed/ready card analysis normally has grounded negative evidence;
B. if no grounded negative can currently be established, the card is marked as analysis-incomplete / exceptional unresolved rather than claiming the game has no downside.

The UI must not fabricate negatives and must not present absence of evidence as evidence of absence.

Determine whether an incomplete-negative card should:
- remain visible with an explicit analysis-incomplete marker;
- be withheld from final recommendation readiness;
- or follow another already-existing canonical readiness rule.

Prefer existing product/readiness semantics if one already fits; do not invent a parallel status system unnecessarily.

### 5. Owning remediation path

If missing evidence requires semantic/external analysis, bind it to the existing GitHub-owned queue/runtime architecture.

Do not create:
- a chat-owned production queue;
- a second scheduler;
- manual per-game analysis.

If current architecture lacks an authorized producer for grounded negatives, recommend a bounded CONTRACT/RECON before IMPLEMENT rather than pretending implementation is ready.

### 6. Recommended next step

Produce one bounded next task only:
- `IMPLEMENT` if producer/ownership/source are already canonical and the generic fix is clear;
- `CONTRACT/RECON` if an authority/source/runtime contract is missing;
- `none` only if current product rules already intentionally define this state and no defect exists.

## Hard boundaries

Do NOT:
- invent a negative for every game;
- turn heuristic suspicion into a definitive downside;
- weaken provenance/grounding requirements;
- manually process production games one by one;
- change paid ranking/Taste/discount logic;
- repeat the already-completed positive-explanation audit;
- bypass the existing Russian-description runtime blocker;
- claim that `no negative found` means `game has no negatives`.

## Report format

Save:
`reviews/worker_reports/card-negative-analysis-gap-01.md`

### Task
What was inspected.

### Canonical negative-analysis route
Exact producers/artifacts/fields.

### Production incidence
Counts + bounded sample.

### First missing-evidence point
Concrete cause classification with exact refs.

### Product semantics
How `no grounded negative` should behave.

### Scope of impact
Systemic vs rare, bounded evidence only.

Efficiency / reusable lesson: `none | <short candidate/ref>`

### Status
Exactly one:
- `complete`
- `blocked`
- `needs_fix`
- `needs_user_decision`

### Recommended next step
One bounded step only.

Final response must include report path and exact refs.