# WORKER TASK — EXISTING CHAT 2

Task ID: `itad-terms-permission-prep-01`
Mode: `CONTRACT / RECON`
Report: `reviews/worker_reports/itad-terms-permission-prep-01.md`

## Context

Direct continuation of `reviews/worker_reports/giveaway-identity-provider-alternatives-01.md`.

Known result:
- Twitch/IGDB remains fallback;
- IsThereAnyDeal (ITAD) exact shop-ID lookup is the strongest non-Twitch route;
- current bounded Epic sample proves 2/2 exact Epic offer IDs -> ITAD game UUID -> exact Steam appid without title matching;
- implementation must not begin until the Terms question about private API use is clarified.

Do not repeat provider comparison.

## Goal

Reduce the remaining ITAD blocker to one exact permission request the user can send, and define how to classify the reply.

## Required work

1. Re-check only the current ITAD Terms/API documentation text needed to word the permission request accurately.
2. Prepare one concise English email addressed to `api@isthereanydeal.com` that truthfully states:
   - project is personal and non-commercial;
   - public GitHub Pages output;
   - server-side exact store-ID identity lookup only;
   - bounded/cached low-frequency daily use;
   - no copying/reselling of ITAD price/deal data;
   - no competitor/commercial service;
   - willing to provide attribution/link if required;
   - asks whether this use is permitted and whether API key/authentication is required or recommended for the exact lookup endpoints.
3. Do not send the email yourself unless the user explicitly asks in that chat and the available tool supports it. Never ask for email passwords/tokens.
4. Define reply classification exactly:
   - `permission_confirmed`
   - `permission_confirmed_with_conditions`
   - `permission_denied`
   - `needs_clarification`
5. If confirmed, state the exact next implementation task scope: existing Epic/GOG exact IDs -> ITAD exact lookup -> unique Steam appid -> existing canonical analysis path; no title/fuzzy fallback, no new scheduler/runtime/browser fetch.
6. If denied, next fallback is Wikidata exact external-ID binding with fail-closed incomplete coverage; Twitch/IGDB remains separate fallback.

## Hard boundaries

Do NOT:
- implement ITAD production integration yet;
- use title/slug matching as authority;
- create manual per-game mappings;
- broaden into price/deal ingestion;
- create another scheduler/queue/runtime;
- repeat Twitch troubleshooting.

## Report

Save `reviews/worker_reports/itad-terms-permission-prep-01.md` with:

### Current terms point
Exact concise blocker.

### Email to send
Final ready-to-send English email, including subject.

### Reply classification
The four allowed outcomes and what each means.

### Next after approval
One bounded implementation scope.

### Status
Exactly one:
- `ready_for_user_send`
- `blocked`
- `needs_user_decision`

Efficiency / reusable lesson: `none | <short candidate/ref>`

Final reply must include the exact report path.