# WORKER TASK — Zero-Incremental-Cost Director Automation Recon 01

## Task ID
`zero-incremental-cost-director-automation-recon-01`

## Mode
`READ-ONLY / RECON`

## Priority
`VERY_HIGH_INFRASTRUCTURE_PRIORITY`

## Expected report
`reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`

## User constraint — authoritative
The user will NOT pay additional money for OpenAI API usage or any other new paid automation service unless they explicitly reverse that decision later.

Do not propose a solution that silently depends on separately billed OpenAI API credits.
Do not ask for new credentials or subscriptions during this recon.
Do not modify product code, orchestration runtime, workflows, secrets, billing, or repository state beyond writing the final recon report.

## Context
The Phase 2B pilot proved the existing GitHub-hosted Codex/OpenAI API architecture can reach a real read-only cloud worker, but it failed because the OpenAI API account had no credits. ChatGPT Plus does not fund that API route.

The user still wants the original operational goal:
- primarily Android use;
- user speaks only to Director in natural language;
- GitHub remains durable truth/control state;
- worker execution should not require an always-on home PC;
- ideally two worker slots can be kept busy automatically when safe;
- user should not have to manually relay `chat finished`, paste worker prompts, or create routine worker chats;
- user should be interrupted only for genuine user gates;
- no additional recurring or usage-based payment.

## Recon goal
Determine whether there is a CURRENT, PRACTICALLY USABLE architecture that achieves materially similar automation with **zero incremental paid cost** under the user's current situation.

This is a current-facts recon. Verify present documentation/terms rather than relying on remembered product behavior.

## Required alternatives to investigate
At minimum investigate and clearly classify:

1. **ChatGPT Plus / Codex capabilities**
   - Is there any supported way to programmatically dispatch ChatGPT/Codex work from GitHub Actions or another cloud trigger using the user's Plus entitlement without separately billed API usage?
   - Distinguish interactive ChatGPT/Codex features from programmable API access.
   - Check whether any official GitHub integration/coding-agent path included with ChatGPT Plus can be triggered autonomously and persist reports to a repo without user relay.

2. **GitHub-native options**
   - GitHub Actions free allowance for this public repo and what it covers.
   - GitHub Models / model inference free tiers or included quotas, if currently available.
   - Whether those free quotas are usable from Actions for the required research/reasoning workload, and whether they require a paid plan after a small quota.
   - GitHub Copilot coding agent / Copilot features only if relevant; classify clearly whether they require a separate subscription or included quota the user is not known to have.

3. **Other genuinely free cloud inference routes**
   - Only official/reputable options suitable for repository automation.
   - No “free trial” disguised as a durable solution.
   - Note hard rate limits, data/privacy tradeoffs, model quality, web-search ability, and whether autonomous repo/report workflows are permitted.

4. **Non-LLM deterministic automation**
   - Which parts of Director orchestration can be automated for free with GitHub Actions/scripts alone: slot/state handling, queue selection by deterministic rules, report existence checks, CI/deploy observation, stale detection, reminders/notifications.
   - Which parts fundamentally still need an LLM/reasoning worker.
   - Could the system automatically prepare/queue worker prompts and reduce user work even if the final LLM chat remains manual?

5. **Android-first semi-automation fallback**
   - If fully autonomous LLM execution is not possible at zero incremental cost, design the best practical fallback that minimizes user actions from Android.
   - Quantify exactly what the user would still need to do per worker cycle (for example one tap/create chat/paste prompt, or less).
   - Prefer an architecture that preserves GitHub durable state and Director control.

## Strict classification
For every candidate, classify as one of:
- `VIABLE_ZERO_INCREMENTAL_COST`
- `VIABLE_ONLY_WITH_EXISTING_UNCONFIRMED_SUBSCRIPTION`
- `FREE_TIER_BUT_NOT_DURABLY_RELIABLE`
- `NOT_PROGRAMMABLE_FOR_THIS_USE`
- `REQUIRES_ADDITIONAL_PAYMENT`
- `NOT_RECOMMENDED_SECURITY_OR_RELIABILITY`

Do not call something “free” if it requires a credit card, paid subscription, expiring trial, or likely paid overage for ordinary operation without clearly stating that limitation.

## Security constraints
Preserve accepted Phase 2A/2B principles in any proposed future design:
- LLM worker should not directly own GitHub write authority if avoidable;
- trusted deterministic publisher should own narrow report publication;
- stale/current-state/CAS barrier;
- exact task/report binding;
- no secret values in reports;
- no autonomous IMPLEMENT until separately authorized;
- no silent second provider credential.

## Required report contents
The final report must include:

1. `Status: complete | blocked | needs_followup`
2. Current official-source findings with dates/links or exact source references.
3. A comparison table of candidate architectures and strict classification.
4. The best **fully autonomous zero-cost** option, if one genuinely exists.
5. If none exists, say that explicitly — do not force a solution.
6. The best **semi-automated Android-first zero-cost** fallback.
7. Exact residual user actions per worker cycle under the fallback.
8. What existing Phase 2A/2B infrastructure can be reused vs retired.
9. Any security/privacy tradeoffs.
10. One recommended next bounded step only.

## Prohibitions
- No implementation.
- No new workflows.
- No secret changes.
- No billing changes.
- No paid-service signup.
- No assumptions that ChatGPT Plus equals API credits.
- No broad product work outside Director automation.
- Do not choose or launch the next major task.
