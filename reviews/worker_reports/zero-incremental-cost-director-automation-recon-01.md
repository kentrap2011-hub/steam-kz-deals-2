# Zero-Incremental-Cost Director Automation Recon 01

Task: `zero-incremental-cost-director-automation-recon-01`  
Task file: `WORKER_TASK_ZERO_INCREMENTAL_COST_DIRECTOR_AUTOMATION_RECON_01.md`  
Mode: `READ-ONLY / RECON`  
Status: `complete_recon_no_implementation`

## 1. Status

Recon is complete. No workflow, secret, orchestration state, product code, billing setting, or external paid service was changed. The only repository mutation made by this task is this required durable report.

### Bottom line

There is now a **real GitHub-native, headless, zero-additional-payment candidate** that did not exist in the Phase 2B design: **GitHub Copilot CLI inside GitHub Actions, using the repository's built-in `GITHUB_TOKEN` and the repository owner's included Copilot entitlement/AI credits**. GitHub documents that Copilot CLI is available on all Copilot plans, including Copilot Free, that it can run programmatically in Actions, and that a `GITHUB_TOKEN` run in a personally owned repository is billed against the repository owner's Copilot seat. Copilot Free requires no paid plan and includes a monthly AI-credit allowance.

However, this is **quota-bounded rather than durably capacity-guaranteed**. GitHub does not currently publish a fixed numeric monthly AI-credit allowance for Copilot Free. If included AI credits are exhausted, the no-payment choice is to wait for the next monthly reset. Therefore:

- a fully headless worker loop with **zero user actions per normal worker cycle** is technically available without separately billed OpenAI API usage;
- it should be classified `FREE_TIER_BUT_NOT_DURABLY_RELIABLE`, not as guaranteed unlimited production capacity;
- there is **no verified unlimited/always-available autonomous LLM worker** with guaranteed zero incremental cost;
- the deterministic non-LLM control plane can be fully automated at zero incremental cost on this public repository.

The safest future direction is therefore **hybrid**: preserve GitHub as the deterministic owner of queue/state/retry/publication, use Copilot CLI only as a constrained semantic worker while included AI credits are available, and park/retry LLM work after the free allowance resets rather than ever enabling paid overage.

## 2. Architecture preflight and current repository truth

The required protocol preflight was performed before evaluating alternatives.

Canonical ownership remains unchanged:

- `config/execution_ownership_contract.json` assigns queue construction, scope selection, retries, completeness, validation, and orchestration to GitHub/repository code;
- interactive chats are operator/developer sessions, not the production scheduler;
- any semantic worker must be a constrained data-plane worker, not a second control plane.

Current Phase 2A/2B truth was re-read from GitHub:

- Phase 2A established the single-writer state model, immutable intake, two logical worker slots, exact task/revision/attempt/lease/report bindings, stale/CAS barriers, strict read-only worker schemas, and a separate trusted report publisher.
- Phase 2B reached a real pinned OpenAI Codex/Responses API model session under the intended read-only security boundary, then failed specifically because the API account had no credits: `You have no credits remaining. Add credits to continue using the API`.
- Phase 2B closed fail-closed: both slots are free, `dispatch_enabled` is false, no second task was dispatched, and no autonomous IMPLEMENT was enabled.
- The repository is public and personally owned by `kentrap2011-hub`, which matters because standard GitHub-hosted Actions runners are free/unlimited for public repositories and Copilot CLI usage with `GITHUB_TOKEN` in a personally owned repository is attributed to the repository owner's Copilot seat.

No responsibility needs to move out of GitHub to adopt a different inference substrate. The correct migration boundary is the worker engine only.

## 3. Official-source findings as of 2026-09-05

All external claims below were checked against current official vendor documentation on 2026-09-05.

### 3.1 ChatGPT Plus / Codex / OpenAI

#### ChatGPT-plan Codex usage is separate from OpenAI API billing

OpenAI documents that signing in to Codex with ChatGPT uses the ChatGPT plan's usage/billing, while using an API key uses API pricing. Plus has included Work/Codex usage; optional ChatGPT credits may extend that usage after plan limits.

Sources:

- https://help.openai.com/en/articles/20001275
- https://help.openai.com/en/articles/11369540-using-codex-with-your-chatgpt-plan
- https://help.openai.com/en/articles/12642688

This confirms that the user's existing ChatGPT Plus subscription can fund interactive/ChatGPT-authenticated Codex usage, but it does **not** fund an `OPENAI_API_KEY` request made from GitHub Actions.

#### Official `openai/codex-action` still requires a provider API key

The current official Codex GitHub Action states that it configures Codex through a secure proxy to the Responses API and that users **must provide an API key** such as `OPENAI_API_KEY` or an Azure provider key as a GitHub Actions secret.

Source:

- https://github.com/openai/codex-action/blob/main/README.md

Therefore the exact Phase 2B `openai/codex-action + OPENAI_API_KEY` route remains `REQUIRES_ADDITIONAL_PAYMENT` under the user's cost policy. It must not be retried merely because ChatGPT Plus exists.

#### Codex CLI can use ChatGPT login, including headless/device-code flows, but there is no first-class official Actions bridge for persisting a Plus login

The current OpenAI Codex CLI source supports ChatGPT login and headless device-code authentication. Technically this proves a headless Codex process can authenticate with ChatGPT rather than an API key.

But the official Codex GitHub Action does not expose that mechanism; it requires a provider API key. This recon did not find an official production recipe that safely carries a personal ChatGPT OAuth/session credential across ephemeral GitHub-hosted runners and refreshes it as a supported Actions credential.

Accordingly, a custom scheme that copies `auth.json`/ChatGPT session credentials into an Actions secret is classified `NOT_RECOMMENDED_SECURITY_OR_RELIABILITY`. It would turn a personal session credential into infrastructure, introduce refresh/expiry risk, and bypass the supported GitHub Action authentication model.

Relevant source/code:

- https://github.com/openai/codex
- current Codex CLI login implementation includes a device-code flow for headless environments.

#### ChatGPT Work scheduled/event-triggered tasks are useful, but not a complete GitHub worker transport

OpenAI currently documents Work on web/mobile, scheduled/event-triggered tasks, and GitHub pull-request event triggers for eligible users. This is genuinely Android-friendly and uses the ChatGPT plan's included Work/Codex allowance.

However, OpenAI also documents that the GitHub app connected to ChatGPT is read-only for repository analysis/search; direct GitHub code changes/pushes require Codex. Scheduled tasks also remain plan-limited and can pause when they need additional action or after inactivity.

Sources:

- https://help.openai.com/en/articles/20001275
- https://help.openai.com/en/articles/11145903
- https://help.openai.com/en/articles/10291617

Therefore ChatGPT Work is valuable as an Android-first human-facing worker/reviewer or notification layer, but **not** as the durable autonomous GitHub queue/report transport by itself. Classification: `NOT_PROGRAMMABLE_FOR_THIS_USE` for the complete Director loop.

### 3.2 GitHub-native inference and automation

#### Standard GitHub Actions compute is free/unlimited for this repository

GitHub states that standard GitHub-hosted runners are free and unlimited for public repositories. Current public Linux `ubuntu-latest` standard runners provide sufficient general-purpose CI compute for the deterministic controller/tests/publisher layer.

Source:

- https://docs.github.com/en/actions/reference/runners/github-hosted-runners

Repository metadata confirms `kentrap2011-hub/steam-kz-deals-2` is public. Thus ordinary Actions minutes are not the cost blocker here.

#### GitHub Models cannot be used: it was fully retired on 2026-07-30

GitHub's current documentation states that GitHub Models was fully retired on July 30, 2026; its playground, model catalog, inference API, and BYOK are no longer available to any customer.

Source:

- https://docs.github.com/en/github-models

Classification: `NOT_PROGRAMMABLE_FOR_THIS_USE` because the service no longer exists.

#### GitHub Copilot CLI can now run programmatically inside GitHub Actions

GitHub currently documents all of the following:

- Copilot CLI is available with **all Copilot plans**.
- It can run non-interactively in GitHub Actions on schedule, repository events, or manual dispatch.
- Direct Actions use can authenticate with the built-in `GITHUB_TOKEN`, with `copilot-requests: write`; no additional stored secret is required for that authentication path.
- When `GITHUB_TOKEN` is used in a **personally owned repository**, AI-credit usage is billed to the repository owner's Copilot seat.
- Programmatic CLI supports `--no-ask-user`, tool allow/deny controls, URL allowlists, secret redaction, JSON output, and auditable session export.
- Tool controls can restrict file writes/shell commands and can expose only selected read/search/web-fetch capabilities.

Sources:

- https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/automate-with-actions
- https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli-in-actions
- https://docs.github.com/en/copilot/concepts/agents/copilot-cli/copilot-cli-in-github-actions
- https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference
- https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools

This is the strongest current replacement candidate for the Phase 2B inference layer.

#### Copilot Free is genuinely zero subscription cost, but its AI allowance is finite and numerically unspecified

GitHub documents Copilot Free as a free individual plan and says most individual developers can start using it with no paid plan required. GitHub also documents that all individual Copilot plans, including Copilot Free, have a monthly GitHub AI Credits allowance and that Copilot CLI consumes those credits.

The current plan/billing pages publish exact paid-plan allowances but do **not** publish a fixed numeric monthly AI-credit amount for Copilot Free. When included credits are exhausted, the documented choices are to pay/upgrade or wait for the next monthly reset. Under this project's policy, only waiting for the reset is permissible.

Sources:

- https://docs.github.com/en/copilot/get-started/plans
- https://docs.github.com/en/copilot/how-tos/manage-your-account/get-started-with-a-copilot-plan
- https://docs.github.com/en/copilot/concepts/billing/usage-based-billing-for-individuals

Classification for `Copilot Free + Actions`: `FREE_TIER_BUT_NOT_DURABLY_RELIABLE`.

If the repository owner already has a paid Copilot plan for unrelated reasons, the same mechanism can consume that already-included allowance without a *new* automation payment, but that entitlement was not verified in this task. Classification for that branch: `VIABLE_ONLY_WITH_EXISTING_UNCONFIRMED_SUBSCRIPTION`.

#### GitHub Agentic Workflows now adds another useful engine option

GitHub Agentic Workflows (`gh-aw`) can run GitHub Copilot as an AI engine, and current GitHub documentation also supports running the **OpenAI Codex engine with a `copilot/...` model**, with inference hosted/billed through GitHub Copilot rather than an OpenAI API key.

Sources:

- https://github.github.com/gh-aw/reference/engines/
- https://github.github.com/gh-aw/engines/codex/
- https://github.github.com/gh-aw/reference/auth/

This is strategically important: even the Codex engine is no longer necessarily tied to separately billed OpenAI API usage.

However, the current `gh-aw` authentication documentation says that personal-repository Copilot inference should use a fine-grained `COPILOT_GITHUB_TOKEN` PAT when centralized organization billing is unavailable, while the direct Copilot CLI documentation separately supports built-in `GITHUB_TOKEN` authentication and documents personal-repository billing to the owner. For this personal repository, **direct Copilot CLI is therefore the smaller credential surface for a first pilot**. A future pilot must validate the exact personal-repo behavior before replacing Phase 2B.

No PAT or new secret was created by this recon.

### 3.3 Other official free cloud inference options

These are technically programmable but are inferior to the GitHub-native route because they introduce another provider/account/token and have free-tier limits that are not a durable production SLA.

#### Google Gemini Developer API

Google publishes free-tier inference for multiple Gemini models. Free-tier data may be used to improve Google products, and availability/quotas vary by model. Some current models/grounding features are paid-only while others have free inference.

Source:

- https://ai.google.dev/gemini-api/docs/pricing

Classification: `FREE_TIER_BUT_NOT_DURABLY_RELIABLE`.

It is not recommended as the first route because it requires a second provider credential and changes the privacy/operational boundary.

#### Cloudflare Workers AI

Cloudflare currently provides 10,000 Neurons per day free; above that, additional operations fail unless the Workers Paid plan is used. Limits reset daily.

Source:

- https://developers.cloudflare.com/workers-ai/platform/pricing/

Classification: `FREE_TIER_BUT_NOT_DURABLY_RELIABLE`.

#### Hugging Face Inference Providers

Hugging Face currently gives free users only `$0.10` in monthly inference-provider credits, explicitly subject to change; extra use requires purchased credits.

Source:

- https://huggingface.co/docs/inference-providers/pricing

Classification: `FREE_TIER_BUT_NOT_DURABLY_RELIABLE`, and not practically attractive for this Director workload.

### 3.4 Local/open models inside GitHub-hosted Actions

Because the repository is public, a GitHub runner can in principle download and run a small open model without an inference bill. That is a real zero-cost compute possibility for narrow classification/summarization tasks.

This recon did **not** benchmark any local model against the project's actual RECON/AUDIT workload, current-source web research requirements, context size, or time limits. A small CPU model cannot be assumed to substitute for the existing semantic worker simply because it launches successfully.

Classification for a general Director worker today: `NOT_RECOMMENDED_SECURITY_OR_RELIABILITY` until a representative quality/latency benchmark proves otherwise. It remains a possible future optimization for bounded deterministic-adjacent subtasks.

## 4. Candidate comparison

| Candidate | Headless automation | Extra payment required | Main limitation | Classification |
|---|---|---:|---|---|
| GitHub Actions + deterministic scripts only | Yes | No | No open-ended semantic reasoning | `VIABLE_ZERO_INCREMENTAL_COST` for scriptable subset |
| Direct GitHub Copilot CLI + Actions + Copilot Free allowance | Yes | No | Finite/undisclosed monthly AI-credit allowance | `FREE_TIER_BUT_NOT_DURABLY_RELIABLE` |
| Direct Copilot CLI + already-existing paid Copilot entitlement | Yes | No *new* payment | Existing entitlement unverified; still finite included allowance | `VIABLE_ONLY_WITH_EXISTING_UNCONFIRMED_SUBSCRIPTION` |
| GitHub Agentic Workflows + Copilot engine | Yes | No if using included Copilot allowance | Personal-repo auth currently adds PAT/secret path in gh-aw docs | `FREE_TIER_BUT_NOT_DURABLY_RELIABLE` |
| GitHub Agentic Workflows + Codex engine + `copilot/auto` inference | Yes | No if using included Copilot allowance | Same Copilot quota; personal-repo credential path must be validated | `FREE_TIER_BUT_NOT_DURABLY_RELIABLE` |
| GitHub Copilot cloud coding agent | Yes | Only if a paid Copilot plan already exists | Cloud agent is a paid-plan feature; broader repository mutation model | `VIABLE_ONLY_WITH_EXISTING_UNCONFIRMED_SUBSCRIPTION` |
| GitHub Models inference API | No | N/A | Retired 2026-07-30 | `NOT_PROGRAMMABLE_FOR_THIS_USE` |
| `openai/codex-action` + OpenAI API | Yes | Yes under current account state | API billing separate from Plus; Phase 2B had zero credits | `REQUIRES_ADDITIONAL_PAYMENT` |
| Codex CLI in Actions by persisting personal ChatGPT `auth.json` | Technically plausible | No API charge | Unsupported session-secret lifecycle/refresh/security | `NOT_RECOMMENDED_SECURITY_OR_RELIABILITY` |
| ChatGPT Work scheduled/event tasks + GitHub app | Partly | No beyond existing Plus allowance | GitHub app is read-only; not a durable result transport | `NOT_PROGRAMMABLE_FOR_THIS_USE` for end-to-end loop |
| Gemini Developer API free tier | Yes | No while within free tier | Provider/key/privacy/quota variability | `FREE_TIER_BUT_NOT_DURABLY_RELIABLE` |
| Cloudflare Workers AI free allocation | Yes | No while within free tier | 10k Neurons/day; new provider/token; hard daily limit | `FREE_TIER_BUT_NOT_DURABLY_RELIABLE` |
| Hugging Face free inference credits | Yes | No while within $0.10/mo | Too small/variable for reliable worker capacity | `FREE_TIER_BUT_NOT_DURABLY_RELIABLE` |
| Small local model on public Actions runner | Yes in principle | No | Quality/latency/web capability unproven | `NOT_RECOMMENDED_SECURITY_OR_RELIABILITY` pending benchmark |

## 5. Does a fully autonomous zero-additional-cost option exist?

### Practical answer: yes, but quota-bounded

A documented end-to-end **headless inference mechanism** now exists without OpenAI API billing:

`GitHub deterministic controller -> read-only Copilot CLI worker in GitHub Actions -> validated structured output -> existing trusted publisher -> GitHub state/reconciliation`

For this personally owned public repository, the preferred first implementation candidate is **direct Copilot CLI using the built-in `GITHUB_TOKEN`**, not a personal ChatGPT OAuth token and not a new external provider key.

Normal successful worker cycle after setup: **0 user actions**.

A quota-exhausted cycle can also require **0 user actions** if the controller records a `waiting_for_included_credit_reset`/equivalent blocked state and retries only after the documented monthly allowance reset. No paid overage should ever be enabled.

### Strict reliability answer: no unlimited guarantee

If “fully autonomous” is defined as “must have enough LLM inference capacity continuously, with no quota-induced pause and no additional payment,” then **no verified option meets that stronger requirement**.

Copilot Free is free and automatable, but the allowance is finite and its exact Free-plan amount is not currently published. Other free cloud providers are also quota-bounded. Local runner inference has not been proven adequate for the representative workload.

Therefore the zero-cost architecture must be designed to **degrade by waiting**, not by charging money or silently switching provider credentials.

## 6. What can be automated completely with GitHub Actions and scripts without any LLM

The following can remain fully autonomous and zero incremental cost regardless of AI allowance:

- immutable intake event validation;
- queue ordering and dependency resolution;
- conflict-key enforcement;
- exactly two logical slot leases;
- task revision / task-file blob / base-SHA binding;
- attempt IDs and retry counters;
- stale/current-state/CAS checks;
- timeout/lease-expiry reconciliation;
- deterministic failure classification;
- schema validation;
- exact expected-report-path validation;
- trusted publication of already-validated output;
- CI/tests/builds/static checks;
- deterministic repository/API/HTTP probes against known endpoints;
- parsing, normalization, sorting, filtering, scoring, and comparison where rules are explicit;
- evidence snapshots from known machine-readable sources;
- notification/status bookkeeping;
- fail-closed completeness checks;
- blocking unsupported `IMPLEMENT` dispatch;
- parking AI-requiring work when the included inference allowance is unavailable.

The main tasks that still need an LLM or human are open-ended semantic synthesis, architecture judgment, ambiguous requirement interpretation, nuanced source-quality evaluation, and novel implementation work whose exact edits cannot be generated deterministically.

A future queue schema could therefore distinguish a deterministic `SCRIPTABLE` capability from `LLM_RECON/AUDIT`, allowing the free Actions-only path to continue even when AI credits are exhausted. That is an architectural recommendation only; no schema/workflow was changed here.

## 7. Best Android-first semi-automated fallback

If the Copilot allowance is unavailable/exhausted and the user does not want to wait for reset, the best zero-new-payment human fallback uses the **existing ChatGPT Plus/Work allowance on Android** for the semantic reasoning while GitHub remains the durable control plane.

Because the standard ChatGPT GitHub app is officially read-only, the fallback cannot honestly be called a zero-touch durable publisher without an additional supported intake bridge. The minimal robust pattern is:

1. GitHub/Director prepares the exact bound task and a ready-to-send worker prompt.
2. The user starts one Work worker task on Android using that prepared prompt.
3. The user submits the finished structured result once to a narrow GitHub-owned result-intake surface; deterministic validation/publisher logic performs the report commit and state transition.

### Exact residual user interaction count

Counted as **user intervention steps per worker cycle, not literal screen taps**:

- **Autonomous Copilot CLI path:** `0` user interventions per normal cycle.
- **Quota exhausted but willing to wait for monthly reset:** `0` user interventions; queue pauses and resumes later.
- **Android Plus/Work fallback instead of waiting:** `2` user interventions per worker cycle:
  1. start/send the prebuilt task in Work;
  2. submit the completed structured result to the GitHub result-intake surface.

No separate “tell Director that the worker is done” relay should be required; GitHub publication/state should be the completion signal.

The exact intake surface does not exist as a newly implemented feature from this task and must be designed separately if this fallback is selected. A browser/cloud-browser path that directly edits GitHub could reduce apparent steps but is not recommended as canonical infrastructure because website automation/sign-in can block or require confirmations.

## 8. Best zero-cost autonomous design candidate

Subject to a one-shot validation of the owner's Copilot Free/other existing entitlement and personal-repository `GITHUB_TOKEN` behavior, the preferred design is:

1. **Keep the existing deterministic controller** as the only queue/state writer.
2. Controller chooses only a bound `READ_ONLY_RECON` or `AUDIT` task; `IMPLEMENT` remains rejected.
3. Dispatch a GitHub-hosted worker job on the public repository.
4. Give the LLM job only `contents: read` plus the minimum Copilot inference permission needed for built-in-token authentication. Do not give it `contents: write`.
5. Invoke current Copilot CLI programmatically with a strict tool set: repository reads/search, only necessary shell read commands, and allowlisted official web domains when web research is required. Do not use a blanket permissive `--yolo`/all-tools policy for the production worker.
6. Return machine-readable output to a non-LLM trusted publisher job.
7. Reuse the current exact task/revision/attempt/lease/base/blob/report validation before publication.
8. Publisher alone receives narrowly scoped GitHub write authority and writes only the expected `reviews/worker_reports/...` path.
9. Controller consumes the publication/result, closes the lease, and advances only allowed state transitions.
10. If Copilot reports exhausted included AI credits, fail closed into a quota-wait state. Do **not** enable paid overage and do **not** silently switch to Gemini/Cloudflare/Hugging Face/OpenAI API.

This architecture is materially similar to Phase 2A/2B; the inference engine changes, not the control plane.

## 9. Phase 2A / Phase 2B reuse and retirement map

### Preserve essentially unchanged

- `config/execution_ownership_contract.json` ownership model;
- `scripts/director_orchestration_controller.py` single-writer/controller role;
- `orchestration/state_writer_manifest.json`;
- `orchestration/state.json` state/revision model;
- immutable `orchestration/intake/*.json` concept;
- exactly two logical slots;
- dependency/conflict-key logic;
- stable task revision / attempt / lease identities;
- exact task-file blob SHA and base-SHA binding;
- stale/CAS/current-HEAD barriers;
- read-only worker request/result boundary concept;
- `scripts/director_report_publisher.py` trusted narrow publisher role;
- exact expected report-path confinement;
- secret/mutation detection in worker results;
- deterministic tests and fail-closed validation philosophy;
- no worker selection of the next major task;
- no autonomous IMPLEMENT until separately authorized;
- billing/quota failure must close the lease without queue draining.

### Adapt, not discard

- worker request/result schemas need provider-neutral engine metadata instead of assuming Codex Action/Responses fields;
- failure taxonomy should generalize `openai_api_billing_no_credits` into provider-neutral included-quota/auth/runtime classes while preserving the old evidence;
- worker launcher should become a provider adapter boundary so the controller does not care whether the semantic engine is Copilot CLI or another explicitly authorized engine;
- quota reconciliation should allow “wait for free allowance reset” without treating it as a payable failure.

### Retire as an active dependency under current cost policy

- `OPENAI_API_KEY` as a prerequisite for Director automation;
- live `openai/codex-action`/Responses API as the sole worker runtime;
- any instruction asking the user to add API credits;
- OpenAI-API-specific model/proxy assumptions in the live worker launcher.

Historical Phase 2A/2B evidence, exact action pin, reports, and tests should remain in Git history/reports; they are valuable proof that the security boundary works and identify what should be preserved.

## 10. Security and privacy comparison

### Preferred GitHub Copilot CLI route

Security requirements for a future pilot:

- LLM job: repository `contents: read` only; no GitHub write credential available to the model process.
- Use the shortest-lived/built-in GitHub token path when it proves valid for this personal repository.
- Grant only the Copilot request permission needed for inference.
- Restrict Copilot CLI tools with explicit available/allowed/denied sets; deny repository write and `git push`/GitHub mutation tools.
- Allow web access only to domains required by the bounded task when practical; external web content is untrusted input and can carry prompt injection.
- Keep trusted publisher in a separate deterministic job/step with exact path validation.
- Preserve current stale/revision/attempt/lease/CAS barriers.
- Do not expose Steam/provider secrets to a generic semantic worker.
- Never enable Copilot paid-overage budget for this automation under current user policy.

Privacy note: GitHub states that, starting April 24, 2026, interactions on personal Copilot Free/Pro/Pro+/Max plans may be used to train/improve AI models unless the individual disables that setting in Copilot settings. This must be checked before sending repository context if the user does not want such use.

Source:

- https://docs.github.com/en/copilot/how-tos/manage-your-account/manage-policies

### ChatGPT Work fallback

OpenAI states that for eligible personal-account content, model improvement depends on the `Improve the model for everyone` setting. GitHub access in the standard ChatGPT app remains read-only.

Source:

- https://help.openai.com/en/articles/11145903

### Gemini free tier

Google's pricing table marks Free Tier content as usable to improve Google products for the relevant free models. This is another reason not to adopt Gemini silently as a fallback.

### Second-provider credentials

Gemini, Cloudflare, and Hugging Face would each add a separate provider/account/token boundary. They must never be auto-selected merely because Copilot quota is unavailable. A provider change requires an explicit future architecture/security decision.

## 11. Validation performed

Repository reads performed:

- `CHAT_PROTOCOL.md`
- `CHAT_CONTEXT.md`
- `DIRECTOR_PROTOCOL.md`
- `PROJECT_ROUTES.md`
- `WORKER_TASK_ZERO_INCREMENTAL_COST_DIRECTOR_AUTOMATION_RECON_01.md`
- `config/execution_ownership_contract.json`
- `orchestration/state.json`
- `reviews/worker_reports/autonomous-director-orchestration-recon-01.md`
- `reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md`
- `reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md`

Current official-source families checked:

- OpenAI Help / official `openai/codex-action` repository;
- GitHub Actions documentation;
- GitHub Copilot plans, AI-credit billing, Copilot CLI Actions/programmatic/security documentation;
- GitHub Agentic Workflows engine/authentication documentation;
- GitHub Models retirement notice;
- Google Gemini Developer API pricing;
- Cloudflare Workers AI pricing;
- Hugging Face Inference Providers pricing.

No live inference pilot was run because the task explicitly forbids implementation/new workflows/secrets and is RECON-only.

## 12. Unresolved facts / limits of this recon

1. The current Copilot entitlement on the `kentrap2011-hub` owner account was not introspected. GitHub documentation says most individual developers can use Copilot Free, but the repository/account must be checked in a future authorized pilot.
2. GitHub currently does not publish a fixed numeric monthly AI-credit allowance for Copilot Free, so this recon cannot honestly estimate “N worker tasks per month.”
3. No representative task has yet been run through direct Copilot CLI with this personal repository's built-in `GITHUB_TOKEN`; the official docs establish the mechanism/billing model, but project-specific compatibility and per-task credit consumption remain unmeasured.
4. No Copilot CLI structured-result adapter has been tested against the current Phase 2A result schema.
5. A small local open model on a public Actions runner has not been benchmarked for quality/latency, so it is not promoted to a production recommendation.
6. The Android Work fallback still needs a narrow supported result-intake surface if it is to avoid manual GitHub file editing; none was added here.

## 13. Required explicit conclusions

### 1. Does a fully autonomous option without additional expense exist?

**Yes, in a quota-bounded sense:** current GitHub documentation supports Copilot CLI running headlessly in GitHub Actions, Copilot CLI is included across Copilot plans, Copilot Free has a free monthly AI-credit allowance, and personally owned repository runs can charge included Copilot entitlement rather than OpenAI API. This can reach **0 user actions per ordinary worker cycle** after setup.

**No, if the requirement means guaranteed uninterrupted/unlimited LLM capacity:** every verified free inference option is quota-bounded, and Copilot Free's exact monthly AI-credit amount is not published. The no-payment response to quota exhaustion must be “wait for reset,” not buy usage.

### 2. If guaranteed autonomous free LLM capacity is unavailable, what minimizes manual user work?

Primary: let GitHub automate every deterministic step and use the quota-bounded Copilot worker whenever included credits are available.

Fallback when the user chooses not to wait for reset: Android ChatGPT Work using existing Plus allowance for the semantic worker, with a future narrow GitHub result-intake/publisher bridge. Do not use the ordinary read-only ChatGPT GitHub app as if it could publish repository results itself.

### 3. Exactly how many user actions remain per worker cycle?

- Copilot CLI autonomous cycle: **0 user intervention steps**.
- Copilot quota exhausted and system waits for monthly reset: **0 user intervention steps**, but work is delayed.
- Android Plus/Work fallback instead of waiting: **2 user intervention steps** per worker cycle — start/send the prepared worker task, then submit the finished structured result once to GitHub's result-intake surface.

These are intervention steps, not literal screen-tap counts.

### 4. What from Phase 2A/2B can be preserved?

**Almost all of the control/security infrastructure.** Preserve the controller/single-writer model, state/intake, two slots, dependency/conflict logic, exact revision/attempt/lease/blob/base/report binding, CAS/stale barriers, read-only worker contract, trusted narrow publisher, tests, no-next-task authority for workers, and fail-closed semantics. Replace only the OpenAI-API-specific worker invocation/authentication/model/proxy layer and generalize provider/quota metadata.

## 14. Changes

Created only:

`reviews/worker_reports/zero-incremental-cost-director-automation-recon-01.md`

No other file, workflow, secret, state, billing setting, external account, or product behavior was changed.

## 15. One bounded recommended next step

Run a **separately authorized one-shot READ-ONLY Copilot CLI validation** against one small representative RECON task, with no persistent dispatch and no paid overage: verify the repository owner's Copilot Free/existing entitlement, verify direct personal-repository `GITHUB_TOKEN` inference, measure actual AI-credit consumption, prove the LLM process has no GitHub write authority, and feed its output through the existing trusted result-validation boundary.

Do not enable queue draining or autonomous IMPLEMENT in that pilot. Do not create a PAT/secret unless the direct built-in-token path is proven unavailable and a later explicit security decision authorizes it.

## 16. Exact durable refs

Repository and task refs observed during this recon:

- repository: `kentrap2011-hub/steam-kz-deals-2`
- recon starting HEAD: `f38424633a08e95438a403096ffa9be83c435679`
- task file blob: `WORKER_TASK_ZERO_INCREMENTAL_COST_DIRECTOR_AUTOMATION_RECON_01.md` -> `cc2235bcb9b552dbed263a24f2b69cb150745c30`
- ownership contract blob: `config/execution_ownership_contract.json` -> `f0b5f48756489965ec223a42f3b234f62ac4bae1`
- Phase 2A report blob: `reviews/worker_reports/director-orchestration-phase2a-security-boundary-implement-01.md` -> `3f972aa5fb20676d6b9040896f4fcfe892fde7a6`
- Phase 2B report blob: `reviews/worker_reports/director-orchestration-phase2b-live-readonly-pilot-01.md` -> `8e803abc0471d4d7d44a6967fd24592b7ca6f65a`
- current orchestration state blob read during recon: `6d76fd149872654b15997852f23f769708ee67d2`
- Phase 2B final real worker source run: `33980979557`
- Phase 2B final real worker job: `101346057158`

## 17. Efficiency / reusable lesson

This task took longer than a normal worker cycle because the external capability landscape changed materially after the Phase 2B design: GitHub Models is gone, while GitHub Copilot CLI/Agentic Workflows now provide official Actions-native inference paths that can consume Copilot entitlement rather than OpenAI API credits. The high-value reusable lesson is to separate **control-plane durability** from **inference-provider selection**. Phase 2A already did that well enough that a future migration should replace one worker adapter instead of rebuilding orchestration.

The main reads/searches were the three chat/director protocols, execution ownership/state, Phase 2A/2B reports, OpenAI Codex/Work authentication and GitHub integration docs, GitHub Actions/Copilot billing/CLI/Agentic Workflows docs, GitHub Models retirement, and official free-tier pricing pages for Google, Cloudflare, and Hugging Face.

A future similar recon would be faster if provider-neutral worker-engine/quota metadata and a maintained official-capability matrix were added in a separately authorized governance task. `PROJECT_ROUTES.md` was not changed here because this task explicitly permits only the durable report write.