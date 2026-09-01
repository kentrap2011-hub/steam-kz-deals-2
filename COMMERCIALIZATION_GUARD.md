# COMMERCIALIZATION GUARD

## Current project status

As of 2026-09-01 this project is **personal / non-commercial**.

The user does **not currently plan to monetize it**. Current provider/source decisions may therefore rely on non-commercial usage assumptions where the relevant provider terms allow that.

This is **not** a permanent statement that the project can never be monetized. It is a hard reminder that the current architecture and source approvals must **not be assumed safe for commercial use**.

## Mandatory stop before any monetization

Before doing any of the following, stop implementation and perform a dedicated licensing/commercial-use review:

- paid access or subscription;
- advertisements or sponsorships;
- affiliate/referral monetization;
- selling the service, data, reports, feeds, or access to them;
- integrating the project into a commercial product/company workflow;
- monetized public launch or any other use that materially changes the project from personal/non-commercial to commercial.

Do **not** silently reuse current provider assumptions after that point.

## What must be re-checked

At minimum, re-check the then-current terms, licensing, attribution, caching, redistribution and partnership requirements for every external source/provider actually used by production.

Particular known examples:

- **IGDB / Twitch** — the duration architecture currently selects IGDB `game_time_to_beats`. The duration contract intentionally leaves commercial/licensing/attribution provisioning as a gate. Before commercial use, verify the current IGDB/Twitch commercial/partnership and attribution requirements and satisfy them before enabling or continuing production collection.
- **Steam data** — re-check applicable Steam/API/store-data usage terms for the intended commercial model.
- **Wikimedia/Wikipedia**, if ever enabled — CC BY-SA attribution/share-alike requirements must be satisfied; do not treat existing text as unrestricted commercial copy.
- **Any future provider/API** — re-check current terms rather than relying on an old worker report or historical documentation.
- **AI-generated/translated content**, if used — verify the then-current provider terms for the intended commercial use and any relevant data/content obligations.

## Required project behavior

1. Any ChatGPT/worker/director task that proposes monetization or commercial deployment must read this file first.
2. Commercialization must be treated as a **new architecture/product decision**, not a minor deployment toggle.
3. No worker may remove or bypass a provider's `provisioning_required`, licensing, attribution, partnership, or commercial-use gate merely because the code technically works.
4. If commercial rights/obligations are unclear, production use of that provider remains blocked until resolved.
5. After a future commercial review is completed, update this file and the relevant provider contracts with the new approved status and evidence/date.

## Current reminder

**Current assumption: personal/non-commercial only.**

If the user later says something like “давай монетизировать”, “добавим рекламу”, “сделаем платную версию”, “запустим для клиентов” or otherwise turns this into a commercial product, surface this guard immediately and re-audit provider rights before implementation.