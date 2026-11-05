#!/usr/bin/env python3
"""Call the Switch Console's own RPC handlers over its trusted renderer IPC.

Switch Console v0.40.1 creates the renderer client in
``console/apps/switch-console-desktop/src/renderer/lib/ipc.ts:5`` and exposes
``window.electronAPI.invoke`` in
``console/apps/switch-console-desktop/src/preload/index.ts:5-6``. The channel
format and handler registration are defined in
``console/apps/switch-console-desktop/src/shared/lib/ipc/rpc.ts:44-63,109-129``;
the active router is declared in
``console/apps/switch-console-desktop/src/main/rpc.ts:34-66``. ``list-procedures`` prints the reviewed subset
needed by LabQuorum environment setup and later template/E2E work. The app
does not expose an RPC introspection handler, so this catalog is explicit.

Arguments to ``call`` are JSON. An array supplies positional RPC arguments;
any other JSON value is passed as the single argument. Values whose key names
look like credentials are redacted from output.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from typing import Any

DEFAULT_CDP_URL = "http://127.0.0.1:9333"
PROCEDURES: dict[str, str] = {
    "agents.advancedSettings": "[object] provider settings field schema",
    "agents.getAgentById": "[string] agent id",
    "agents.getAgents": "[optional string] location id",
    "agents.readAdvancedConfig": "[object] {agentId}",
    "agents.updateAdvancedConfig": "[object] {agentId, attributes}",
    "agents.addAgent": "[object] AddAgentParams",
    "agentTemplates.form": "[object] {yamlText}",
    "agentTemplates.parse": "[object] {yamlText, instructions?}",
    "managedAgents.advancedConfigSchema": "[string] server id",
    "managedAgents.list": "[string] server id",
    "managedAgents.setDesiredState": "[object] {serverId, agentId, desiredState}",
    "managedAgents.update": "[object] {serverId, agentId, changes}",
    "providers.catalogue": "no arguments",
    "providers.get": "[string] provider id, [optional string] connection id",
    "providers.list": "[optional string] connection id",
    "providers.listAgentInstallationStatus": "[optional string] connection id",
    "roomTemplates.getExampleTemplate": "no arguments",
    "roomTemplates.parse": "[object] {yamlText, schema?}",
    "sessions.getSession": "[string] session id",
    "sessions.getSessions": "[optional string] location id",
    "switchRooms.getConnections": "no arguments",
    "switchServers.acceptInvitation": "[object] {serverId, token}",
    "switchServers.getAuthConfig": "[string] server id",
    "switchServers.getBundledChatSignIn": "[string] server id; password is redacted",
    "switchServers.getConnectionStatus": "[string] server id",
    "switchServers.listServers": "no arguments",
    "switchServers.openGatewayPage": "[object] {serverId, url}",
    "switchServers.passwordLogin": "[object] {serverId, email, password}",
    "switchServers.signup": "[object] SignupParams",
    "workspaces.addRoomAgents": "[object] {workspaceId, roomId, agentIds}",
    "workspaces.createInvitation": "[object] {workspaceId, role, email, expiresInHours, usesRemaining}",
    "workspaces.claimBridgeIdentity": "[object] {workspaceId, bridgeId, externalUserId, username}",
    "workspaces.createRoom": "[object] {workspaceId, name, description, bridgeId, agentIds, instructions?}",
    "workspaces.createRoomFromTemplate": "[string] workspace id, [string] yaml, [object] inputs, [string] template name",
    "workspaces.getActiveId": "no arguments",
    "workspaces.list": "no arguments",
    "workspaces.listAgents": "[string] workspace id",
    "workspaces.listBridges": "[string] workspace id",
    "workspaces.listExternalUsers": "[string] workspace id",
    "workspaces.listMyIdentities": "[string] workspace id",
    "workspaces.listRooms": "[string] workspace id",
    "workspaces.runTemplateWithAgents": "[string] workspace id, [object] run body",
    "workspaces.runTemplateDocument": "[string] workspace id, [object] template run body",
    "workspaces.searchBridgeDirectory": "[object] {workspaceId, bridgeId, query}",
}

SECRET_KEY = re.compile(
    r"password|token|secret|authorization|cookie|api[_-]?key|credential|private[_-]?key",
    re.IGNORECASE,
)
RPC_ERROR_MARKER = "__switchConsoleRpcError"


def redact(value: Any) -> Any:
    """Hide credential-like object fields before writing RPC results to stdout."""
    if isinstance(value, dict):
        return {
            key: "[REDACTED]"
            if SECRET_KEY.search(str(key))
            or (
                str(key).lower() in {"link", "url"}
                and isinstance(child, str)
                and ("invite" in child.lower() or "token=" in child.lower())
            )
            else redact(child)
            for key, child in value.items()
        }
    if isinstance(value, list):
        return [redact(child) for child in value]
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cdp-url", default=DEFAULT_CDP_URL, help="Switch Console CDP endpoint")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list-procedures", help="list the reviewed RPC procedure catalog")
    call_parser = subparsers.add_parser("call", help="invoke one Console RPC procedure")
    call_parser.add_argument("procedure", help="dot-joined RPC procedure name")
    call_parser.add_argument("json_args", help="JSON array of positional args or one JSON value")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.command == "list-procedures":
        for name, shape in sorted(PROCEDURES.items()):
            print(f"{name}\t{shape}")
        return 0

    try:
        result = invoke_procedure(args.procedure, args.json_args, args.cdp_url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except Exception as exc:  # the error text is emitted without request arguments
        print(f"Console RPC call failed: {exc}", file=sys.stderr)
        return 4

    if isinstance(result, dict) and result.get(RPC_ERROR_MARKER) is True:
        error = {key: result.get(key) for key in ("code", "message", "data") if key in result}
        print(json.dumps(redact(error), ensure_ascii=True, indent=2), file=sys.stderr)
        return 1
    print(json.dumps(redact(result), ensure_ascii=True, indent=2, default=str))
    return 0


def invoke_procedure(procedure: str, json_args: str, cdp_url: str) -> Any:
    """Parse arguments and invoke one Console RPC procedure over CDP."""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*(?:\.[A-Za-z][A-Za-z0-9]*)+", procedure):
        print("procedure must be a dot-joined RPC name", file=sys.stderr)
        raise ValueError("invalid procedure name")

    try:
        parsed = json.loads(json_args)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON args: {exc}") from exc
    rpc_args = parsed if isinstance(parsed, list) else [parsed]

    playwright_api: Any = importlib.import_module("playwright.sync_api")
    with playwright_api.sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(cdp_url)
        page = next(
            (
                candidate
                for context in browser.contexts
                for candidate in context.pages
                if not candidate.is_closed() and "switch-console" in candidate.url.lower()
            ),
            None,
        )
        if page is None:
            raise RuntimeError("no Switch Console renderer page found at the CDP endpoint")
        return page.evaluate(
            """async ({channel, args}) => {
                const api = window.electronAPI;
                if (!api || typeof api.invoke !== 'function') {
                    throw new Error('window.electronAPI.invoke is unavailable');
                }
                return await api.invoke(channel, ...args);
            }""",
            {"channel": procedure, "args": rpc_args},
        )


if __name__ == "__main__":
    raise SystemExit(main())
