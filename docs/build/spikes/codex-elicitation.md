# Isolated spike: MCP elicitation in Codex app-server 0.166.0

Date: 2026-11-05

## Results

| Question | Status | Evidence |
|---|---|---|
| Does a stdio MCP server `elicitation/create` during a tool call reach the app-server client as `mcpServer/elicitation/request`? | **FAIL** | The client saw no request for the server's own elicitation in any run. The only request in the manual approval runs had `_meta.codex_approval_kind: "mcp_tool_call"`, so it was Codex's tool gate. |
| Does the tool receive the app-server client's accept or decline answer to its own elicitation? | **FAIL** | No client request was delivered to answer. In the accept and decline trials the SDK returned `CancelledElicitation` with `action: "cancel"`. |
| Does the result change with Switch's `approval-required` thread settings? | **FAIL** for server elicitation | The thread used the untrusted project override, omitted `approvalPolicy`, and sent `approvalsReviewer: "user"`. The server's own elicitation still returned cancel. In the connector-style config, Codex separately asked approval for the tool call before running it. |
| Does the server's own elicitation arrive when Codex tool approval is auto-approved? | **FAIL** | The auto-approved run had zero app-server server requests, but the tool still ran and received `action: "cancel"`. |
| Does Codex issue a separate MCP tool-call approval in the manual connector-style run, and does it offer session persistence? | **PASS** | One `mcpServer/elicitation/request` arrived before the tool executed. Its `_meta.persist` was `["session", "always"]`. Switch maps this to `accept`, `acceptForSession`, `decline`, and `cancel`. |

The MCP server appeared as `spike_elicit` with tool `confirm_commit` in `mcpServerStatus/list`, and its startup status reached `ready`. Its MCP client capabilities, read by the server from the SDK session, included `elicitation.form` and `elicitation.url`. This was not a missing-tool or missing-capability case.

The chosen `accept` and `decline` values in the harness applied only if a non-tool-approval elicitation request arrived. None did. In both manual runs the harness accepted Codex's separate tool-call approval, then the MCP tool's own elicitation completed as cancel.

## Versions and isolated setup

- Codex CLI: `codex-cli 0.166.0`
- Python: `3.12.10`
- uv: `0.11.29`
- Official Python MCP SDK: `mcp 1.30.0`, resolved by `uv run --no-project --with "mcp>=1,<2"`
- Model and effort: `gpt-6-luna`, `low`
- Switch reference: `switch-v0.40.1`

The throwaway `CODEX_HOME` was `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\spike-elicit\codex-home`. Only `auth.json` was copied into it from `%USERPROFILE%\.codex`; its contents were never read or printed. Codex wrote its generated session files under this throwaway home. `UV_CACHE_DIR` was set to `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\spike-elicit\uv-cache` for the spike runs.

The server uses an empty Pydantic form schema to match Switch's accepted `{}` content response:

```python
class EmptyConfirmation(BaseModel):
    pass


@mcp.tool()
async def confirm_commit(request_id: str, ctx: Context) -> str:
    result = await ctx.elicit(
        message=f"Confirm commit request {request_id}?",
        schema=EmptyConfirmation,
    )
```

SDK source inspected:

- `Context.elicit(self, message, schema)` is in `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\spike-elicit\uv-cache\archive-v0\GKF1b_-7AJwOUMwX\Lib\site-packages\mcp\server\fastmcp\server.py:1230`.
- Validation and action mapping are in `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\spike-elicit\uv-cache\archive-v0\GKF1b_-7AJwOUMwX\Lib\site-packages\mcp\server\elicitation.py:105-139`. The SDK maps MCP action `cancel` to `CancelledElicitation`; only an accepted response has `.data`.

## JSON-RPC evidence

The client used newline-delimited JSON-RPC, matching Switch's transport. These are the exact client-to-app-server initialization and turn-start messages from the final accept run. The full traces contain every message in each run.

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"clientInfo":{"name":"switch-console","title":"Switch Console","version":"0.1.0"},"capabilities":{"experimentalApi":true,"requestAttestation":false}}}
{"jsonrpc":"2.0","method":"initialized","params":null}
{"jsonrpc":"2.0","id":2,"method":"account/read","params":{"refreshToken":false}}
{"jsonrpc":"2.0","id":3,"method":"thread/start","params":{"cwd":"C:\\Users\\Nikhil\\.claude\\jobs\\85ca08fa\\tmp\\spike-elicit","approvalsReviewer":"user","model":"gpt-6-luna"}}
{"jsonrpc":"2.0","id":4,"method":"mcpServerStatus/list","params":{"threadId":"01a1ab2d-3256-7fa3-b09c-1feada61c08e","detail":"full"}}
{"jsonrpc":"2.0","id":5,"method":"turn/start","params":{"threadId":"01a1ab2d-3256-7fa3-b09c-1feada61c08e","input":[{"type":"text","text":"Use MCP server spike_elicit to call its confirm_commit tool exactly once with request_id AR-SPIKE. Wait for its result, then report only the returned action.","text_elements":[]}],"model":"gpt-6-luna","effort":"low"}}
```

No `approvalPolicy` field was sent in `thread/start`. The app-server's thread result reported `approvalPolicy: "untrusted"`, `approvalsReviewer: "user"`, model `gpt-6-luna`, and the throwaway home's default sandbox `readOnly` with network disabled.

The one server request seen in the manual connector-style accept run was the separate Codex tool-call approval. This is the exact request line as emitted by Codex, followed by the client's exact response:

```json
{"method":"mcpServer/elicitation/request","id":0,"params":{"threadId":"01a1ab2d-3256-7fa3-b09c-1feada61c08e","turnId":"01a1ab2d-39d4-7d10-b523-629c4006a000","serverName":"spike_elicit","mode":"form","_meta":{"codex_approval_kind":"mcp_tool_call","persist":["session","always"],"tool_description":"","tool_params":{"request_id":"AR-SPIKE"},"tool_params_display":[{"name":"request_id","value":"AR-SPIKE","display_name":"request_id"}]},"message":"Allow the spike_elicit MCP server to run tool \"confirm_commit\"?","requestedSchema":{"type":"object","properties":{}}}}
{"jsonrpc":"2.0","id":0,"result":{"action":"accept","content":{},"_meta":null}}
```

The actual MCP tool result in that run was:

```json
{"action":"cancel","data":null,"mcp_client_capabilities":{"elicitation":{"form":{},"url":{}},"experimental":{"codex/auth-change":{}}},"request_id":"AR-SPIKE","result_type":"CancelledElicitation","trial":"approval-required-accept"}
```

There was no second `mcpServer/elicitation/request` containing the server's message `Confirm commit request AR-SPIKE?`. The decline trial had the same ordering and result. The auto-approved trial had no server request at all and the same tool result action `cancel`.

## Trials

| Trial | MCP tool-call approval request count | Server elicitation request count | Tool result |
|---|---:|---:|---|
| `approval-required-accept` | 1, accepted by harness | 0 | `cancel` (`CancelledElicitation`) |
| `approval-required-decline` | 1, accepted by harness | 0 | `cancel` (`CancelledElicitation`) |
| `tool-auto-accept` | 0 | 0 | `cancel` (`CancelledElicitation`) |

The `approval-required-decline` harness setting did not cause a decline response to be sent: the server's own elicitation was never surfaced to the app-server client. The only response sent in that run was `accept` for Codex's pre-tool call approval.

## Precise Codex config used

The approval-required thread config followed Switch's adapter: project trust override, no thread `approvalPolicy`, `approvalsReviewer: "user"`, model on `thread/start`, and effort on `turn/start`. The app-server process arguments for a manual connector-style run were:

```text
codex app-server --stdio
-c projects={"C:\\Users\\Nikhil\\.claude\\jobs\\85ca08fa\\tmp\\spike-elicit"={trust_level="untrusted"}}
-c mcp_servers.spike_elicit.command="uv"
-c mcp_servers.spike_elicit.args=["run","--no-project","--with","mcp>=1,<2","python","server.py"]
-c mcp_servers.spike_elicit.env={"SPIKE_TRIAL"="approval-required-accept"}
```

`default_tools_approval_mode` was omitted for this connector-style run so Codex asked before the MCP tool call. The auto-approved variant added this override:

```text
-c mcp_servers.spike_elicit.default_tools_approval_mode="approve"
```

This matches `config-args.ts`: Switch leaves the override out for connector MCP servers, but sets it to `"approve"` for ordinary MCP servers, even when the runtime mode is `approval-required`. The normal Switch MCP server case is therefore represented by the auto-approved variant. The thread itself remained `approval-required` in both cases.

The exact thread and turn request bodies were:

```json
{"cwd":"C:\\Users\\Nikhil\\.claude\\jobs\\85ca08fa\\tmp\\spike-elicit","approvalsReviewer":"user","model":"gpt-6-luna"}
```

```json
{"threadId":"01a1ab2d-3256-7fa3-b09c-1feada61c08e","input":[{"type":"text","text":"Use MCP server spike_elicit to call its confirm_commit tool exactly once with request_id AR-SPIKE. Wait for its result, then report only the returned action.","text_elements":[]}],"model":"gpt-6-luna","effort":"low"}
```

## Switch reference and interpretation

- `codex-adapter.ts:162-169` sets `approvalPolicy: null`, `approvalsReviewer: "user"`, and `projects={cwd={trust_level="untrusted"}}` for `approval-required`.
- `codex-adapter.ts:900-927` handles `mcpServer/elicitation/request`, distinguishes `_meta.codex_approval_kind === "mcp_tool_call"`, and maps acceptance to `{action:"accept",content:{},_meta:null}`.
- `protocol.ts:38-44` names the request `mcpServer/elicitation/request`; `protocol.ts:303-310` describes `_meta` for tool-call approvals.
- `config-args.ts:21-80` implements the connector versus ordinary MCP tool approval difference.
- The path named in the request, `packages/agent-providers/src/codex/app-server-client.ts`, is not present in this Switch tree. Newline framing and server-request handling are in `packages/agent-providers/src/transport/stdio-json-rpc.ts:61`.
- Codex's [app-server README](https://github.com/openai/codex/blob/main/codex-rs/app-server/README.md) and [MCP app-server protocol](https://github.com/openai/codex/blob/main/codex-rs/app-server-protocol/src/protocol/v2/mcp.rs) were reviewed. The experiment used the installed 0.166.0 binary and the Switch message sequence.

## Recommendation

The closest built-in per-commit checkpoint in this Switch/Codex version is Codex's own MCP tool-call approval. Put the commit server in Switch's `connectorMcpServers` set and leave `default_tools_approval_mode` unset for it. Expose one actual commit per tool call, and use one-shot `accept` for each call. Switch can offer `acceptForSession` because Codex advertises session persistence; choosing it would stop the per-call prompts.

For server-side enforcement that must also work when Codex tool approval is automatic, use an out-of-band confirmation record or local confirmation UI and have the commit tool fail closed unless it consumes a one-time approval bound to the prepared commit. MCP `elicitation/create` through this app-server path did not provide that confirmation channel.

## Artifacts

Scripts and complete token-redacted JSON-RPC logs are inside `C:\Users\Nikhil\.claude\jobs\85ca08fa\tmp\spike-elicit`:

- `server.py`
- `app_client.py`
- `wire-approval-required-accept.jsonl`, `wire-approval-required-decline.jsonl`, `wire-tool-auto-accept.jsonl`
- `server-requests-approval-required-accept.json`, `server-requests-approval-required-decline.json`, `server-requests-tool-auto-accept.json`
- `tool-results-approval-required-accept.jsonl`, `tool-results-approval-required-decline.jsonl`, `tool-results-tool-auto-accept.jsonl`
- `summary-approval-required-accept.json`, `summary-approval-required-decline.json`, `summary-tool-auto-accept.json`

The wire files contain all app-server input and output messages in order. Server-request files record every request the client received and its response. Token-like secret values are redacted.

Isolation note: all Codex state and intended spike files were kept in the spike folder, and no repository, Switch Console file, or `%USERPROFILE%\.codex\config.toml` was modified. One early SDK introspection `uv run` was started in a fresh shell without re-exporting `UV_CACHE_DIR`; it resolved the SDK from the default user uv cache. Subsequent SDK and server runs used the spike-local cache. I did not delete that global cache because it may have contained pre-existing packages.
