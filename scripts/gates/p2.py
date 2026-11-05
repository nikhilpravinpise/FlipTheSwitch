"""P2 MCP and CLI gate runner."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_step(name: str, args: Sequence[str]) -> bool:
    try:
        result = subprocess.run(
            list(args),
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        print(f"FAIL {name}: could not start {' '.join(args)}: {exc}")
        return False
    output = (result.stdout + result.stderr).strip()
    if output:
        print(output)
    if result.returncode == 0:
        print(f"PASS {name}")
        return True
    print(f"FAIL {name}: exited {result.returncode}")
    return False


def main() -> int:
    failures = 0
    if not run_step(
        "common gate p2",
        ["uv", "run", "python", "scripts/gates/common.py", "--phase", "p2"],
    ):
        failures += 1
    if not run_step(
        "P2 stdio probe",
        ["uv", "run", "python", "scripts/gates/p2_stdio_probe.py"],
    ):
        failures += 1
    if failures:
        print(f"FAIL P2 gate: {failures} check(s) failed")
        return 1
    print("PASS P2 gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
