"""P1 ledger gate.

P1 includes the minimal ``lq init``, ``lq seed --demo`` and ``lq audit verify``
commands so the ledger can be created, seeded idempotently and checked end to end.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RACE_PREFIX = "test_I_01"
RACE_REPETITIONS_SOURCE = "RACE_REPETITIONS = 50"


class Gate:
    """Run commands and aggregate failures without stopping early."""

    def __init__(self) -> None:
        self.failures = 0

    def command(self, name: str, args: Sequence[str], *, cwd: Path = ROOT) -> bool:
        try:
            result = subprocess.run(
                list(args),
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )
        except OSError as exc:
            print(f"FAIL {name}: could not start {' '.join(args)}: {exc}")
            self.failures += 1
            return False
        output = (result.stdout + result.stderr).strip()
        if output:
            print(output)
        if result.returncode == 0:
            print(f"PASS {name}")
            return True
        self.failures += 1
        print(f"FAIL {name}: exited {result.returncode}")
        return False

    def fail(self, name: str, reason: str) -> None:
        self.failures += 1
        print(f"FAIL {name}: {reason}")


def _collect_i01_nodes(gate: Gate) -> list[str]:
    try:
        collected = subprocess.run(
            ["uv", "run", "pytest", "--collect-only", "-q"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        gate.fail("I-01 race collection", f"could not start pytest collection: {exc}")
        return []
    if collected.returncode != 0:
        detail = "; ".join(collected.stderr.splitlines()[-5:] + collected.stdout.splitlines()[-5:])
        gate.fail(
            "I-01 race collection", f"pytest collection exited {collected.returncode}: {detail}"
        )
        return []
    nodes = [
        line.strip()
        for line in collected.stdout.splitlines()
        if "::" in line and line.rsplit("::", maxsplit=1)[-1].startswith(RACE_PREFIX)
    ]
    if not nodes:
        gate.fail("I-01 race test", "no collected test function starts with test_I_01")
        return []
    sources = {ROOT / node.split("::", maxsplit=1)[0] for node in nodes}
    if not any(
        path.is_file() and RACE_REPETITIONS_SOURCE in path.read_text(encoding="utf-8")
        for path in sources
    ):
        gate.fail(
            "I-01 race repetition constant", f"source must contain {RACE_REPETITIONS_SOURCE!r}"
        )
        return []
    return nodes


def main() -> int:
    gate = Gate()
    gate.command(
        "common gate p1", ["uv", "run", "python", "scripts/gates/common.py", "--phase", "p1"]
    )
    gate.command(
        "P1 domain and store coverage >= 90%",
        [
            "uv",
            "run",
            "pytest",
            "--cov=labquorum.domain",
            "--cov=labquorum.store",
            "--cov-fail-under=90",
        ],
    )

    race_nodes = _collect_i01_nodes(gate)
    if race_nodes:
        gate.command("I-01 race tests", ["uv", "run", "pytest", "-q", *race_nodes])

    with tempfile.TemporaryDirectory(prefix="labquorum-p1-") as temp_name:
        database = Path(temp_name) / "g.sqlite"
        gate.command("lq init", ["uv", "run", "lq", "init", "--db", str(database)])
        seed_args = [
            "uv",
            "run",
            "lq",
            "seed",
            "--demo",
            "--db",
            str(database),
            "--anchor-date",
            "2026-11-06",
        ]
        gate.command("lq seed --demo first load", seed_args)
        gate.command("lq seed --demo idempotent reload", seed_args)
        gate.command(
            "lq audit verify", ["uv", "run", "lq", "audit", "verify", "--db", str(database)]
        )

    if gate.failures:
        print(f"FAIL P1 gate: {gate.failures} check(s) failed")
        return 1
    print("PASS P1 gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
