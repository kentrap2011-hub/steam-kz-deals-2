#!/usr/bin/env python3
"""One-shot read-only Copilot CLI worker harness for Pilot 02.

This process never writes the repository. It writes evidence only under --temp-dir.
It performs an official Copilot SDK quota preflight and calls Copilot CLI at most once.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

TASK_ID = "epic-ru-availability-source-probe-02"
TASK_FILE = "WORKER_TASK_EPIC_RU_AVAILABILITY_SOURCE_PROBE_02.md"
TASK_BLOB = "8270487fb3019135adc5662d0b67f0f37e189bed"
REPORT = "reviews/worker_reports/epic-ru-availability-source-probe-02.md"
ATTEMPT_ID = f"{TASK_ID}:r1:a1"
LEASE_ID = f"slot_2:{ATTEMPT_ID}"


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run(cmd, *, cwd=None, env=None, capture=False):
    return subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )


def validate_request(repo: Path, request: dict) -> None:
    expected = {
        "task_id": TASK_ID,
        "task_revision": 1,
        "attempt_number": 1,
        "attempt_id": ATTEMPT_ID,
        "lease_id": LEASE_ID,
        "mode": "READ_ONLY_RECON",
        "task_file": TASK_FILE,
        "task_file_blob_sha": TASK_BLOB,
        "expected_report_path": REPORT,
    }
    for k, v in expected.items():
        assert request.get(k) == v, f"request binding mismatch: {k}"
    for k in (
        "repository_write_authority",
        "github_write_credential",
        "state_write_authority",
        "product_write_authority",
        "worker_can_choose_next_task",
    ):
        assert request.get(k) is False, f"worker authority changed: {k}"
    assert request.get("secret_values") == []
    data = (repo / TASK_FILE).read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    assert blob == TASK_BLOB


def quota_script() -> str:
    return r"""
import { CopilotClient } from '@github/copilot-sdk';
import fs from 'node:fs';
const out=process.argv[2];
const token=process.env.GITHUB_TOKEN;
const clean=s=>({
  isUnlimitedEntitlement:s?.isUnlimitedEntitlement ?? null,
  entitlementRequests:s?.entitlementRequests ?? null,
  usedRequests:s?.usedRequests ?? null,
  usageAllowedWithExhaustedQuota:s?.usageAllowedWithExhaustedQuota ?? null,
  remainingPercentage:s?.remainingPercentage ?? null,
  overage:s?.overage ?? null,
  overageAllowedWithExhaustedQuota:s?.overageAllowedWithExhaustedQuota ?? null,
  resetDate:s?.resetDate ?? null
});
let result={ok:false,reason:'quota_unavailable',quotaSnapshots:{},safeForZeroAdditionalPayment:false};
if (!token) { fs.writeFileSync(out,JSON.stringify({...result,reason:'GITHUB_TOKEN_missing'})); process.exit(0); }
const client=new CopilotClient({gitHubToken:token,useLoggedInUser:false});
try {
  const q=await client.rpc.account.getQuota({});
  const snaps={}; for (const [k,v] of Object.entries(q?.quotaSnapshots||{})) snaps[k]=clean(v);
  const p=snaps.premium_interactions;
  let safe=!!p;
  safe=safe && p.overageAllowedWithExhaustedQuota===false;
  safe=safe && (p.overage===null || Number(p.overage)<=0);
  safe=safe && (p.isUnlimitedEntitlement===true || p.entitlementRequests===-1 || Number(p.remainingPercentage)>0);
  result={ok:true,reason:safe?'included_premium_quota_with_paid_overage_disabled':'cannot_prove_included_premium_quota_without_overage',quotaSnapshots:snaps,safeForZeroAdditionalPayment:safe};
} catch (e) { result.reason='quota_auth_or_entitlement_error:'+String(e?.message||e).slice(0,500); }
try { await client.stop(); } catch {}
fs.writeFileSync(out,JSON.stringify(result));
"""


def get_quota(sdk_dir: Path, out: Path, env: dict) -> dict:
    script = sdk_dir / "quota.mjs"
    script.write_text(quota_script(), encoding="utf-8")
    proc = run(["node", str(script), str(out)], cwd=sdk_dir, env=env, capture=True)
    if proc.returncode != 0 or not out.exists():
        return {
            "ok": False,
            "reason": "quota_runtime_failure:" + " ".join((proc.stderr or proc.stdout or "").split())[-500:],
            "quotaSnapshots": {},
            "safeForZeroAdditionalPayment": False,
        }
    try:
        return json.loads(out.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "reason": f"quota_parse_failure:{type(exc).__name__}:{exc}",
            "quotaSnapshots": {},
            "safeForZeroAdditionalPayment": False,
        }


def sanitize(text: str) -> str:
    text = re.sub(r"(github_pat_[A-Za-z0-9_]+|gh[ousr]_[A-Za-z0-9_]+|Bearer\s+\S+)", "[REDACTED]", text, flags=re.I)
    return " ".join(text.split())[-1000:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--request", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--temp-dir", required=True)
    a = ap.parse_args()

    repo = Path(a.repo_root).resolve()
    request = json.loads(Path(a.request).read_text(encoding="utf-8"))
    validate_request(repo, request)
    tmp = Path(a.temp_dir).resolve()
    tmp.mkdir(parents=True, exist_ok=True)
    sdk = tmp / "sdk"
    sdk.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()

    evidence = {
        "provider_outcome": "provider_unavailable_zero_cost_gate",
        "provider_diagnostic": None,
        "copilot_invocation_count": 0,
        "semantic_result": None,
        "quota_preflight": None,
        "quota_postflight": None,
        "copilot_cli_version": "unavailable",
    }

    cli_install = run(["npm", "install", "-g", "@github/copilot@latest"], env=env, capture=True)
    init = run(["npm", "init", "-y"], cwd=sdk, env=env, capture=True)
    sdk_install = run(["npm", "install", "@github/copilot-sdk@latest"], cwd=sdk, env=env, capture=True)
    if cli_install.returncode != 0 or init.returncode != 0 or sdk_install.returncode != 0:
        evidence["provider_diagnostic"] = "official Copilot CLI/SDK installation failed; inference not attempted"
        write_json(Path(a.evidence), evidence)
        return 0

    version = run(["copilot", "--version"], cwd=repo, env=env, capture=True)
    evidence["copilot_cli_version"] = (version.stdout or version.stderr or "unknown").strip()[:300]

    pre = get_quota(sdk, tmp / "quota-pre.json", env)
    evidence["quota_preflight"] = pre
    if not pre.get("safeForZeroAdditionalPayment"):
        evidence["provider_diagnostic"] = pre.get("reason")
        write_json(Path(a.evidence), evidence)
        return 0

    prompt = f"""Execute exactly the already-bound Director worker task {TASK_FILE} in strict READ_ONLY_RECON mode.
Read relevant repository evidence and use web access only for public Epic-owned URLs needed to prove or disprove the acquisition-availability signal. Do not modify any file, repository, issue, PR, state, product, credential, billing setting, or task. Do not choose another task. Do not ask for a PAT, OPENAI_API_KEY, provider secret, or paid fallback. If the required proof bar cannot be met, return status blocked rather than guessing.
Return ONLY one JSON object with fields: schema_version, task_id, task_revision, attempt_number, attempt_id, lease_id, mode, task_file, task_file_blob_sha, base_sha, report_path, status, report_content, requested_repository_mutations, state_mutation_requested, product_mutation_requested, secret_values.
Copy binding fields exactly from REQUEST_JSON below. status is complete, blocked, or needs_user_evidence. report_content is a durable Markdown report with exact Epic-owned endpoints/fields/evidence, RU semantics, available/unavailable cases if proven, acquisition-vs-catalog distinction, failure behavior, limitations, and recommendation. requested_repository_mutations and secret_values are []; state_mutation_requested and product_mutation_requested are false.
REQUEST_JSON={json.dumps(request, separators=(',', ':'))}"""

    cmd = [
        "copilot", "-s", "-p", prompt,
        "--stream=off", "--no-banner", "--no-color", "--no-ask-user", "--no-auto-update",
        "--no-custom-instructions", "--no-experimental", "--no-remote", "--no-remote-export",
        "--disable-builtin-mcps", "--model=auto", "--max-ai-credits=30",
        "--available-tools=view,glob,grep,web_fetch", "--allow-tool=read",
        "--allow-url=www.epicgames.com", "--allow-url=store.epicgames.com", "--allow-url=*.epicgames.com",
    ]
    call = run(cmd, cwd=repo, env=env, capture=True)
    evidence["copilot_invocation_count"] = 1
    if call.returncode != 0:
        evidence["provider_outcome"] = "provider_runtime_failure"
        evidence["provider_diagnostic"] = f"copilot_exit_{call.returncode}: {sanitize(call.stderr or call.stdout or '')}"
    else:
        try:
            result = json.loads((call.stdout or "").strip())
            exact = {
                "schema_version": 1,
                "task_id": request["task_id"],
                "task_revision": request["task_revision"],
                "attempt_number": request["attempt_number"],
                "attempt_id": request["attempt_id"],
                "lease_id": request["lease_id"],
                "mode": request["mode"],
                "task_file": request["task_file"],
                "task_file_blob_sha": request["task_file_blob_sha"],
                "base_sha": request["base_sha"],
                "report_path": request["expected_report_path"],
            }
            assert isinstance(result, dict)
            for k, v in exact.items():
                assert result.get(k) == v, k
            assert result.get("status") in request["allowed_result_statuses"]
            assert isinstance(result.get("report_content"), str) and result["report_content"].strip()
            assert result.get("requested_repository_mutations") == []
            assert result.get("state_mutation_requested") is False
            assert result.get("product_mutation_requested") is False
            assert result.get("secret_values") == []
            evidence["provider_outcome"] = "semantic_result"
            evidence["provider_diagnostic"] = None
            evidence["semantic_result"] = result
        except Exception as exc:
            evidence["provider_outcome"] = "provider_runtime_failure"
            evidence["provider_diagnostic"] = f"invalid_machine_result:{type(exc).__name__}:{exc}"

    evidence["quota_postflight"] = get_quota(sdk, tmp / "quota-post.json", env)
    write_json(Path(a.evidence), evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
