"""Minimal ledger initialization, demo seed, and audit commands."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any

from labquorum.domain.errors import ErrorCode, LabQuorumError
from labquorum.store.audit import tail, verify
from labquorum.store.db import (
    database_info,
    default_database_path,
    init_database,
    open_database,
)
from labquorum.store.seed import seed_demo


def _date_argument(value: str) -> date:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise argparse.ArgumentTypeError("anchor date must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("anchor date is invalid") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="lq", description="LabQuorum booking ledger utilities")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="create or inspect a ledger")
    init.add_argument("--db", type=Path, default=default_database_path())

    seed = commands.add_parser("seed", help="load the demo booking fixtures")
    seed.add_argument("--demo", action="store_true", required=True)
    seed.add_argument("--db", type=Path, default=default_database_path())
    seed.add_argument("--anchor-date", type=_date_argument, required=True)

    audit = commands.add_parser("audit", help="inspect the ledger audit chain")
    audit_commands = audit.add_subparsers(dest="audit_command", required=True)
    audit_verify = audit_commands.add_parser("verify", help="verify the hash chain")
    audit_verify.add_argument("--db", type=Path, default=default_database_path())
    audit_tail = audit_commands.add_parser("tail", help="show recent audit rows")
    audit_tail.add_argument("--db", type=Path, default=default_database_path())
    audit_tail.add_argument("-n", type=int, default=20)
    return parser


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _run(args: argparse.Namespace) -> int:
    path: Path = args.db
    if args.command == "init":
        connection = init_database(path)
        try:
            info = database_info(connection)
            print(
                _json(
                    {
                        "database": str(path.resolve()),
                        "schema_version": info.schema_version,
                        "sqlite_version": info.sqlite_version,
                        "journal_mode": info.journal_mode,
                    }
                )
            )
        finally:
            connection.close()
        return 0

    connection = open_database(path)
    try:
        if args.command == "seed":
            result = seed_demo(connection, args.anchor_date)
            print(_json(result))
            return 0
        if args.audit_command == "verify":
            bad_sequence = verify(connection)
            valid = bad_sequence is None
            print(
                _json(
                    {
                        "valid": valid,
                        "first_bad_seq": bad_sequence,
                        "scope": "internal chain consistency",
                        "limitation": "Truncation and recomputed chains are not detectable without an external checkpoint.",
                    }
                )
            )
            return 0 if valid else 1
        if args.audit_command == "tail":
            if args.n <= 0:
                raise LabQuorumError(
                    ErrorCode.INVALID_ARGUMENT,
                    "Audit tail count must be positive.",
                )
            print(_json(tail(connection, limit=args.n)))
            return 0
    finally:
        connection.close()
    raise RuntimeError("Argument parser produced an unsupported command.")


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        return _run(args)
    except LabQuorumError as error:
        print(
            _json({"error": error.code.value, "message": error.message, "details": error.details}),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
