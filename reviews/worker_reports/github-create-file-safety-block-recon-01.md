# GitHub create-file safety block recon 01

Status: `recon_complete_cause_unobservable`

## Scope

Separate bounded READ-ONLY / RECON of the OpenAI safety-layer blocking observed on GitHub write actions. No production Taste state, Scheduled Tasks, dossier backlog, workflow, queue, runtime, or semantic data was touched.

No low-level Git tree/commit operation was used as a replacement for a blocked `create-file` action.

## Director-observed incident

The director session reported this sequence:

1. GitHub `create-file` initially succeeded for a neutral file containing only `probe`.
2. Later `create-file` calls were blocked by an OpenAI safety-system message across different filenames, including calls whose content was still only `probe`.
3. GitHub `delete-file`, `create_blob`, and reads remained available in that director session.
4. The initial probe file was subsequently removed.

Repository evidence independently confirms the successful first create/delete pair:

- create commit `0e77375503784ca89168551f072e3d55f29f701b`, file `TEMP_OPENAI_SAFETY_WRITE_PROBE.md`, content exactly `probe`;
- delete commit `72d502b346bb8ea2355f1a3fbd9e93ff3418de75`.

Blocked director calls left no repository commit, so their exact internal safety classification is not recoverable from GitHub state.

## Worker controlled reproduction

Disposable branch:
`worker/github-create-file-safety-block-recon-01-probe`

Baseline:
`72d502b346bb8ea2355f1a3fbd9e93ff3418de75`

### create-file

Six harmless `create-file` calls succeeded in this worker session:

1. `diagnostics/create-file-probe-a.txt`, content `probe` -> `4afb3f53742f7046afaa3a54b54e20fef2f8ed39`
2. `diagnostics/create-file-probe-b.txt`, content `probe` -> `d09b815131fd24e2f00711a2e8019b1a7fcf6ecc`
3. `diagnostics/create-file-probe-c.txt`, content `hello` -> `3c0ad7130a3a1848d4eca290f7ce147a622f0f68`
4. `diagnostics/TEMP_OPENAI_SAFETY_WRITE_PROBE_WORKER.md`, content `probe` -> `a9d3a5ecc9ce07548c9b9eac24c292eb888bab76`
5. `diagnostics/create-file-probe-d.txt`, content `probe` -> `54b24bc7b85df3efb8bcfa8469404f9900ed0426`
6. after a separate write-action safety block, `diagnostics/create-file-probe-e.txt`, content `probe` -> `26e7439c02fce61bcd29a7be0d2ea7744667123e`

For every successful `create-file` response the connector exposed:

- `error=null`
- `error_data=null`
- `error_code=null`
- `classification_id=null`
- `json_rpc_error_code=null`
- `error_http_status_code=null`
- `error_http_headers=null`

Therefore the director's `create-file` block is **not reproduced independently** in this worker session.

### filename/content/repetition variables

Within this bounded worker sample:

- same content `probe`: successful repeatedly;
- different content `hello`: successful;
- `.txt` and `.md`: both successful;
- filename containing `OPENAI_SAFETY_WRITE_PROBE`: successful;
- six `create-file` calls over the same worker session: all successful;
- a `create-file` immediately after a safety-block on another GitHub write action: successful.

No tested filename, content, or create-file repetition variable reproduced the director's create-file block.

### Other GitHub actions

Confirmed working in this worker session:

- repository/file reads;
- `create_branch`;
- `create-file` as above;
- `create_blob("probe")` once -> blob `24ae15ce9741d53115a9fc71c2b761790ca47995`;
- `delete-file` for four harmless probe removals before one later safety block.

The `create_blob` check was diagnostic only. It was not used to construct a tree/commit or as a workaround for `create-file`.

### Safety block reproduced on delete-file

After multiple harmless write actions, an attempted removal of `diagnostics/create-file-probe-d.txt` through the ordinary GitHub `delete-file` action was blocked before connector execution with the visible message:

`Этот вызов инструмента был заблокирован системами безопасности OpenAI. Внимательно проверьте отправляемые данные.`

No structured `classification_id`, error code, HTTP status, or policy reason was exposed with that blocked call.

A normal read immediately afterward succeeded and proved the file still existed. One subsequent harmless `create-file` then succeeded with null error/classification metadata.

The blocked `delete-file` was not retried and no low-level Git operation was used to circumvent it.

## Minimal confirmed failure domain

What is confirmed:

- an OpenAI safety layer can block an otherwise neutral GitHub write action before normal connector execution;
- the block is **not uniquely tied to `create-file`**, because this worker reproduced the same safety-layer blocking presentation on `delete-file`;
- the block is **not a repository-wide permanent write outage**, because reads and later `create-file` continued to work;
- the block is **not established as content-specific**: `probe` and `hello` both succeeded in worker `create-file` calls, and the director's first `probe` create also succeeded;
- the block is **not established as filename-specific**: different names and extensions succeeded, including a safety-themed filename;
- bounded repetition alone is insufficient to predict it: six worker create-file calls succeeded, while a later delete-file was blocked.

What is not observable:

- the exact safety-policy rule or internal classifier that fired;
- whether the director's create-file block was caused by session-specific state, a transient platform condition, or another hidden safety signal;
- any stable numeric/action threshold;
- internal classification/error metadata for blocked calls.

## Session-specific assessment

The director's create-file block does **not** reproduce independently in this worker session against the same repository and equally neutral payloads. That rules out a simple global repository/content/path prohibition.

This is consistent with a session-specific or transient safety-layer condition, but the available telemetry cannot distinguish those possibilities. Therefore the exact cause is **not observable** and no stronger attribution is justified.

## Cleanup state

The probe branch is disposable and was never merged to `main`.

Four probe files were removed successfully. Cleanup of `create-file-probe-d.txt` was the operation on which the safety block appeared, so it was intentionally not retried or bypassed. `create-file-probe-e.txt` was created afterward only to test whether `create-file` itself had become blocked and was likewise left only on the disposable branch. Neither file is in `main` or production state.

## Conclusion

Narrowest defensible classification:

`intermittent OpenAI safety-layer block on GitHub write actions; create-file-specific cause not reproduced; exact policy cause unobservable`

No safety/anti-abuse mechanism was bypassed. No low-level Git tree/commit fallback was used. No production task or backlog was executed.
