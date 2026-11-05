"""CLI for live P4 scenarios. Unit tests use the fake Mattermost server."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from contextlib import ExitStack
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from labquorum.e2e.config import (
    HarnessConfigError,
    default_personas_path,
    load_config,
    override_config,
)
from labquorum.e2e.evidence import sha256_file
from labquorum.e2e.ledger import LedgerInspector
from labquorum.e2e.mattermost import MattermostClient
from labquorum.e2e.runner import ScenarioOptions, ScenarioRunner

SCENARIOS = ("e2e01", "refusal", "approval", "decline", "e2e11", "injection", "e2e15")
ATTACKS = ("I-36", "I-37", "I-38", "I-39", "I-40", "I-41")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True, choices=SCENARIOS)
    parser.add_argument("--personas", type=Path, default=default_personas_path())
    parser.add_argument("--channel", help="Override channel_id in personas.json")
    parser.add_argument("--ledger", type=Path, help="Override ledger_path in personas.json")
    parser.add_argument("--evidence-dir", type=Path, default=Path("docs/build/evidence/p4"))
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--observation-seconds", type=float, default=30.0)
    parser.add_argument("--attack", choices=ATTACKS)
    parser.add_argument(
        "--stale-request-id", help="Current request ID for the I-41 stale-reference probe"
    )
    parser.add_argument("--stale-revision", type=int, help="Older revision used in the I-41 probe")
    parser.add_argument("--stale-hash", help="Older 64-character content hash used in I-41")
    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--session-id", help="Switch Console session ID for E2E-11 correlation")
    parser.add_argument(
        "--confirm-session-id",
        action="store_true",
        help="Confirm the session ID was checked in the Switch Console for the target channel",
    )
    parser.add_argument("--binding", choices=("off", "on"), default="off")
    parser.add_argument("--codex-cli-version")
    parser.add_argument("--switch-console-version")
    parser.add_argument("--template", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.scenario == "injection" and args.attack is None:
        parser.error("--scenario injection requires --attack I-36 through I-41")
    if args.scenario != "injection" and args.attack is not None:
        parser.error("--attack is only valid with --scenario injection")
    stale_values = (args.stale_request_id, args.stale_revision, args.stale_hash)
    if (
        args.scenario == "injection"
        and args.attack == "I-41"
        and any(value is None for value in stale_values)
    ):
        parser.error("I-41 requires --stale-request-id, --stale-revision, and --stale-hash")
    if any(value is not None for value in stale_values) and not (
        args.scenario == "injection" and args.attack == "I-41"
    ):
        parser.error(
            "stale-reference options are only valid for --scenario injection --attack I-41"
        )
    if args.scenario == "e2e15" and not args.manual:
        parser.error("--scenario e2e15 requires --manual operator checkpoints")
    if args.scenario == "e2e11" and not args.session_id:
        parser.error("--scenario e2e11 requires --session-id from the Switch Console")
    if args.session_id and not args.confirm_session_id:
        parser.error("--session-id requires --confirm-session-id")
    if args.confirm_session_id and (not args.session_id or args.scenario != "e2e11"):
        parser.error("--confirm-session-id is only valid with --scenario e2e11 and --session-id")
    try:
        binding_tuple = _binding_tuple(args)
        config = override_config(
            load_config(args.personas),
            channel_id=args.channel,
            ledger_path=args.ledger,
        )
    except (HarnessConfigError, ValueError, OSError) as exc:
        parser.error(str(exc))

    with ExitStack() as stack:
        clients: dict[str, MattermostClient] = {}
        try:
            for name, persona in config.personas.items():
                clients[name] = stack.enter_context(
                    MattermostClient(
                        config.mattermost_url,
                        persona.login_id,
                        persona.password,
                    )
                )
        except Exception as exc:
            print(f"Persona login failed: {exc}")
            return 1
        runner = ScenarioRunner(
            personas=clients,
            ledger=LedgerInspector(config.ledger_path),
            channel_id=config.channel_id,
            evidence_dir=args.evidence_dir,
            options=ScenarioOptions(
                timeout=args.timeout,
                poll_interval=args.poll_interval,
                observation_seconds=args.observation_seconds,
                binding=args.binding == "on",
                binding_tuple=binding_tuple,
                session_id=args.session_id,
                session_id_confirmed=args.confirm_session_id,
                stale_request_id=args.stale_request_id,
                stale_revision=args.stale_revision,
                stale_hash=args.stale_hash,
                manual=args.manual,
            ),
        )
        result = runner.run(args.scenario, attack_id=args.attack)
    print(f"{result.scenario}: {result.status}; evidence: {result.evidence_path}")
    if result.failure:
        print(result.failure)
    return 0 if result.status == "pass" else 1


def _binding_tuple(args: argparse.Namespace) -> dict[str, str]:
    if args.binding == "off":
        return {}
    missing = [
        name
        for name, value in (
            ("--codex-cli-version", args.codex_cli_version),
            ("--switch-console-version", args.switch_console_version),
            ("--template", args.template),
        )
        if not value
    ]
    if missing:
        raise ValueError(f"--binding on requires {', '.join(missing)}.")
    template = args.template
    if not isinstance(template, Path) or not template.is_file():
        raise ValueError("--binding on requires an existing template file.")
    try:
        labquorum_version = version("labquorum")
    except PackageNotFoundError as exc:
        raise ValueError("Could not read the installed LabQuorum version.") from exc
    return {
        "codex_cli_version": str(args.codex_cli_version),
        "switch_console_version": str(args.switch_console_version),
        "labquorum_version": labquorum_version,
        "template_sha256": sha256_file(template),
    }


if __name__ == "__main__":
    raise SystemExit(main())
