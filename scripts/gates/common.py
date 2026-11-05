"""Universal phase checks for LabQuorum.

The gate intentionally uses only the Python standard library. Invoke it with
``uv run python scripts/gates/common.py [--phase pN] [--ci]``.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Sequence
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "build" / "evidence"
PHASE_IDS_PATH = REPO_ROOT / "scripts" / "gates" / "phase_ids.json"
EXCLUDED_PREFIXES = ("docs/plan/", "docs/review/", "docs/inputs/")
EM_DASH = "\u2014"
SECRET_PATTERNS: tuple[tuple[str, re.Pattern[bytes]], ...] = (
    ("OpenAI-style key", re.compile(rb"sk-[A-Za-z0-9]{20,}")),
    ("GitHub token", re.compile(rb"ghp_[A-Za-z0-9]{30,}")),
    ("AWS access key", re.compile(rb"AKIA[0-9A-Z]{16}")),
    (
        "private key header",
        re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    ),
)


class GateResults:
    """Collect and print gate outcomes."""

    def __init__(self) -> None:
        self.failures = 0

    def passed(self, name: str) -> None:
        print(f"PASS {name}")

    def failed(self, name: str, reason: str) -> None:
        self.failures += 1
        print(f"FAIL {name}: {reason}")

    def skipped(self, name: str, reason: str) -> None:
        print(f"SKIP {name}: {reason}")


def scan_em_dash(path: Path) -> bool:
    """Return whether a supported text file contains U+2014."""
    try:
        contents = path.read_bytes()
    except OSError:
        return False
    try:
        return EM_DASH in contents.decode("utf-8-sig")
    except UnicodeDecodeError:
        if contents.startswith((b"\xff\xfe", b"\xfe\xff")):
            try:
                return EM_DASH in contents.decode("utf-16")
            except UnicodeDecodeError:
                return False
        return False


def scan_secret_patterns(contents: bytes) -> list[str]:
    """Return the names of simple credential patterns found in bytes."""
    return [name for name, pattern in SECRET_PATTERNS if pattern.search(contents)]


def expand_id_ranges(tokens: Iterable[str]) -> list[str]:
    """Expand tokens such as U-B01..U-B03 while preserving their numeric width."""
    expanded: list[str] = []
    for token in tokens:
        if ".." not in token:
            expanded.append(token)
            continue
        match = re.fullmatch(r"(.+?)(\d+)\.\.(.+?)(\d+)", token)
        if match is None:
            raise ValueError(f"invalid plan ID range: {token}")
        start_prefix, start_text, end_prefix, end_text = match.groups()
        if start_prefix != end_prefix:
            raise ValueError(f"plan ID range prefixes differ: {token}")
        start, end = int(start_text), int(end_text)
        if end < start:
            raise ValueError(f"plan ID range ends before it starts: {token}")
        width = len(start_text)
        expanded.extend(f"{start_prefix}{number:0{width}d}" for number in range(start, end + 1))
    return expanded


def test_name_prefix(plan_id: str) -> str:
    """Convert a plan ID to the required pytest function-name prefix."""
    return f"test_{plan_id.replace('-', '_')}"


def node_function_name(node_id: str) -> str:
    """Extract a pytest function name from a collected node ID."""
    return node_id.rsplit("::", maxsplit=1)[-1].split("[", maxsplit=1)[0]


def id_has_test(plan_id: str, node_ids: Iterable[str]) -> bool:
    """Return whether a collected pytest node starts with the plan ID prefix."""
    prefix = test_name_prefix(plan_id)
    return any(node_function_name(node_id).startswith(prefix) for node_id in node_ids)


def parse_collected_node_ids(output: str) -> list[str]:
    """Read pytest's quiet collection output into node IDs."""
    return [line.strip() for line in output.splitlines() if "::" in line and "test_" in line]


def _run(args: Sequence[str], *, cwd: Path = REPO_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _output_summary(result: subprocess.CompletedProcess[str]) -> str:
    output = (result.stderr + "\n" + result.stdout).strip()
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    return "; ".join(lines[-6:]) if lines else "no command output"


def _tracked_paths() -> tuple[list[str] | None, str | None]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None, result.stderr.decode("utf-8", errors="replace").strip()
    return [path for path in result.stdout.decode("utf-8").split("\0") if path], None


def _is_excluded(path: str) -> bool:
    return path.startswith(EXCLUDED_PREFIXES)


def _check_universal(results: GateResults, phase: str | None, ci: bool) -> None:
    sync = _run(["uv", "sync", "--locked"])
    if sync.returncode == 0:
        results.passed("check 1 uv sync --locked")
    else:
        results.failed("check 1 uv sync --locked", _output_summary(sync))

    lint_failures: list[str] = []
    for command in (
        ["uv", "run", "ruff", "check", "."],
        ["uv", "run", "ruff", "format", "--check", "."],
    ):
        lint = _run(command)
        if lint.returncode != 0:
            lint_failures.append(f"{' '.join(command)}: {_output_summary(lint)}")
    if lint_failures:
        results.failed("check 2 ruff", " | ".join(lint_failures))
    else:
        results.passed("check 2 ruff check and format")

    pyright = _run(["uv", "run", "pyright"])
    if pyright.returncode == 0:
        results.passed("check 3 pyright")
    else:
        results.failed("check 3 pyright", _output_summary(pyright))

    with tempfile.TemporaryDirectory(prefix="labquorum-pytest-") as temp_name:
        junit_path = Path(temp_name) / "pytest.xml"
        pytest = _run(["uv", "run", "pytest", "--junitxml", str(junit_path)])
        pytest_problem: str | None = None
        if pytest.returncode != 0:
            pytest_problem = f"pytest exited {pytest.returncode}: {_output_summary(pytest)}"
        elif not junit_path.is_file():
            pytest_problem = "pytest did not create its JUnit XML report"
        else:
            pytest_problem = _check_junit_skips(junit_path)
        if pytest_problem is None:
            results.passed("check 4 full pytest suite")
        else:
            results.failed("check 4 full pytest suite", pytest_problem)

    tracked, tracked_problem = _tracked_paths()
    if tracked is None:
        results.failed("check 5 em-dash scan", f"git ls-files failed: {tracked_problem}")
    else:
        matches = [
            path
            for path in tracked
            if not _is_excluded(path)
            and (REPO_ROOT / path).is_file()
            and scan_em_dash(REPO_ROOT / path)
        ]
        if matches:
            results.failed("check 5 em-dash scan", f"U+2014 found in: {', '.join(matches)}")
        else:
            results.passed("check 5 em-dash scan")

    if ci:
        results.skipped("check 6 gate baseline", "--ci skips the baseline check")
    else:
        baseline_problem = _check_gate_baseline()
        if baseline_problem is None:
            results.passed("check 6 gate baseline")
        else:
            results.failed("check 6 gate baseline", baseline_problem)

    if tracked is None:
        results.failed("check 7 tracked-secret scan", "could not list tracked files")
    else:
        secret_hits: list[str] = []
        if ".env" in tracked:
            secret_hits.append(".env is tracked")
        for relpath in tracked:
            if _is_excluded(relpath):
                continue
            path = REPO_ROOT / relpath
            if not path.is_file():
                continue
            for pattern_name in scan_secret_patterns(path.read_bytes()):
                secret_hits.append(f"{relpath} ({pattern_name})")
        if secret_hits:
            results.failed("check 7 tracked-secret scan", ", ".join(secret_hits))
        else:
            results.passed("check 7 tracked-secret scan")

    if ci:
        results.skipped("check 8 red replay", "--ci skips behavioral-red replay")
    elif phase is None:
        results.skipped("check 8 red replay", "no --phase was specified")
    else:
        replay_problem = _check_red_replay(phase)
        if replay_problem is None:
            results.passed(f"check 8 red replay {phase}")
        else:
            results.failed(f"check 8 red replay {phase}", replay_problem)

    if phase is None:
        results.skipped("check 9 claimed test IDs", "no --phase was specified")
    else:
        id_problem = _check_claimed_ids(phase)
        if id_problem is None:
            results.passed(f"check 9 claimed test IDs {phase}")
        else:
            results.failed(f"check 9 claimed test IDs {phase}", id_problem)


def _check_junit_skips(junit_path: Path) -> str | None:
    try:
        root = ET.parse(junit_path).getroot()
    except (ET.ParseError, OSError) as exc:
        return f"could not read JUnit XML: {exc}"
    allowed, issue = _allowed_skip_ids()
    if issue is not None:
        return issue
    unexpected: list[str] = []
    for case in root.findall(".//testcase"):
        skipped = case.find("skipped")
        failure = case.find("failure")
        if failure is not None and "XPASS" in failure.attrib.get("message", ""):
            unexpected.append(_junit_node_id(case) + " unexpectedly passed an xfail")
            continue
        if skipped is None:
            continue
        node_id = _junit_node_id(case)
        allowed_case = any(fnmatch.fnmatchcase(node_id, pattern) for pattern in allowed)
        if not allowed_case:
            unexpected.append(node_id)
    if unexpected:
        return "unlisted skips or xfails: " + ", ".join(unexpected)
    return None


def _junit_node_id(case: ET.Element) -> str:
    classname = case.attrib.get("classname", "")
    name = case.attrib.get("name", "unknown")
    parts = classname.split(".") if classname else []
    class_names: list[str] = []
    while parts and parts[-1].startswith("Test"):
        class_names.insert(0, parts.pop())
    module_path = PurePosixPath(*parts).with_suffix(".py") if parts else PurePosixPath("unknown.py")
    parts_for_node = [module_path.as_posix(), *class_names, name]
    return "::".join(parts_for_node)


def _allowed_skip_ids() -> tuple[list[str], str | None]:
    path = EVIDENCE_DIR / "allowed-skips.md"
    if not path.is_file():
        return [], "docs/build/evidence/allowed-skips.md is missing"
    allowed: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0].lower() in {"test node id", "node id"}:
            continue
        if not cells[0] or set(cells[0]) <= {"-", ":"}:
            continue
        if not cells[1]:
            return [], f"allowed skip {cells[0]!r} has no reason"
        allowed.append(cells[0])
    return allowed, None


def _check_gate_baseline() -> str | None:
    baseline_path = EVIDENCE_DIR / "gate-baseline.txt"
    if not baseline_path.is_file():
        return "docs/build/evidence/gate-baseline.txt is missing"
    contents = baseline_path.read_text(encoding="utf-8").strip()
    match = re.search(r"(?<![0-9a-fA-F])[0-9a-fA-F]{7,64}(?![0-9a-fA-F])", contents)
    if match is None:
        return "gate-baseline.txt does not contain a commit SHA"
    sha = match.group(0)
    resolved = _run(["git", "rev-parse", "--verify", f"{sha}^{{commit}}"])
    if resolved.returncode != 0:
        return f"baseline SHA {sha} is not a commit"
    diff = _run(["git", "diff", "--quiet", sha, "HEAD", "--", "scripts/gates"])
    if diff.returncode != 0:
        return f"scripts/gates changed since baseline {sha}"
    status = _run(["git", "status", "--porcelain", "--untracked-files=all", "--", "scripts/gates"])
    if status.returncode != 0:
        return f"git status failed: {_output_summary(status)}"
    if status.stdout.strip():
        return "working tree has changes under scripts/gates"
    return None


def _load_phase_evidence(phase: str) -> tuple[dict[str, object] | None, str | None]:
    path = EVIDENCE_DIR / f"{phase}.json"
    if not path.is_file():
        return None, f"docs/build/evidence/{phase}.json is missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"could not read {path.relative_to(REPO_ROOT)}: {exc}"
    if not isinstance(data, dict):
        return None, f"{path.relative_to(REPO_ROOT)} must contain a JSON object"
    red_commit = data.get("red_commit")
    red_tests = data.get("red_tests")
    if not isinstance(red_commit, str) or re.fullmatch(r"[0-9a-fA-F]{7,64}", red_commit) is None:
        return None, "red_commit must be a commit SHA"
    if (
        not isinstance(red_tests, list)
        or not red_tests
        or not all(isinstance(node_id, str) and "::" in node_id for node_id in red_tests)
    ):
        return None, "red_tests must be a non-empty list of pytest node IDs"
    return data, None


def _check_red_replay(phase: str) -> str | None:
    evidence, issue = _load_phase_evidence(phase)
    if issue is not None or evidence is None:
        return issue or "phase evidence is invalid"
    red_commit = str(evidence["red_commit"])
    red_tests = [str(node_id) for node_id in evidence["red_tests"]]  # type: ignore[union-attr]
    resolved = _run(["git", "rev-parse", "--verify", f"{red_commit}^{{commit}}"])
    if resolved.returncode != 0:
        return f"red_commit {red_commit} is not an available commit"
    commit_sha = resolved.stdout.strip()
    ancestor = _run(["git", "merge-base", "--is-ancestor", commit_sha, "HEAD"])
    if ancestor.returncode != 0:
        return f"red_commit {red_commit} is not an ancestor of HEAD"
    temp_root = Path(tempfile.mkdtemp(prefix="labquorum-red-")).resolve()
    worktree_path = temp_root / "worktree"
    junit_path = temp_root / "red-junit.xml"
    worktree_added = False
    failure: str | None = None
    try:
        add = _run(["git", "worktree", "add", "--detach", str(worktree_path), commit_sha])
        if add.returncode != 0:
            failure = f"git worktree add failed: {_output_summary(add)}"
        else:
            worktree_added = True
            command = [
                "uv",
                "run",
                "--locked",
                "--directory",
                str(worktree_path),
                "pytest",
                "-p",
                "no:cacheprovider",
                "-q",
                f"--junitxml={junit_path}",
                *red_tests,
            ]
            replay = _run(command, cwd=REPO_ROOT)
            if replay.returncode != 1:
                failure = (
                    f"red replay exited {replay.returncode}, expected 1: {_output_summary(replay)}"
                )
            elif not junit_path.is_file():
                failure = "red replay did not create JUnit XML"
            else:
                failure = _validate_red_junit(junit_path, len(red_tests))
        if failure is None:
            changed, changed_issue = _test_files_changed(commit_sha)
            if changed_issue is not None:
                failure = changed_issue
            elif changed:
                failure = _check_test_change_reasons(phase, changed)
    finally:
        if worktree_added:
            remove = _run(["git", "worktree", "remove", "--force", str(worktree_path)])
            if remove.returncode != 0:
                cleanup_issue = f"git worktree remove failed: {_output_summary(remove)}"
                failure = f"{failure}; {cleanup_issue}" if failure else cleanup_issue
        shutil.rmtree(temp_root, ignore_errors=True)
    return failure


def _validate_red_junit(junit_path: Path, expected_count: int) -> str | None:
    try:
        root = ET.parse(junit_path).getroot()
    except (ET.ParseError, OSError) as exc:
        return f"could not read red replay JUnit XML: {exc}"
    cases = root.findall(".//testcase")
    if len(cases) != expected_count:
        return f"red replay reported {len(cases)} test cases for {expected_count} node IDs"
    suites = [root] if root.tag == "testsuite" else root.findall(".//testsuite")
    errors = sum(int(suite.attrib.get("errors", "0")) for suite in suites)
    if errors:
        return f"red replay had {errors} collection or test errors"
    for case in cases:
        if case.find("error") is not None:
            return f"red test errored: {_junit_node_id(case)}"
        if case.find("skipped") is not None:
            return f"red test skipped: {_junit_node_id(case)}"
        if case.find("failure") is None:
            return f"red test did not fail: {_junit_node_id(case)}"
    return None


def _test_files_changed(red_commit: str) -> tuple[list[str] | None, str | None]:
    diff = _run(["git", "diff", "--name-only", red_commit, "HEAD", "--", "tests"])
    if diff.returncode != 0:
        return None, f"git diff for test files failed: {_output_summary(diff)}"
    return [line.replace("\\", "/") for line in diff.stdout.splitlines() if line.strip()], None


def _check_test_change_reasons(phase: str, changed: list[str]) -> str | None:
    path = EVIDENCE_DIR / f"{phase}-test-changes.md"
    if not path.is_file():
        return f"{path.relative_to(REPO_ROOT)} is missing; list changed test files with reasons"
    lines = path.read_text(encoding="utf-8").splitlines()
    missing: list[str] = []
    for test_path in changed:
        reason_found = False
        for line in lines:
            if test_path not in line or "|" not in line:
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2 and cells[0] == test_path and cells[1] and set(cells[1]) != {"-"}:
                reason_found = True
                break
        if not reason_found:
            missing.append(test_path)
    return (
        f"test changes need reason lines in {path.relative_to(REPO_ROOT)}: {', '.join(missing)}"
        if missing
        else None
    )


def _check_claimed_ids(phase: str) -> str | None:
    if not PHASE_IDS_PATH.is_file():
        return "scripts/gates/phase_ids.json is missing"
    try:
        phases = json.loads(PHASE_IDS_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return f"could not read phase_ids.json: {exc}"
    if not isinstance(phases, dict) or not isinstance(phases.get(phase), list):
        return f"phase_ids.json has no ID list for {phase}"
    raw_ids = phases[phase]
    if not all(isinstance(item, str) for item in raw_ids):
        return f"phase_ids.json contains a non-string ID for {phase}"
    try:
        ids = expand_id_ranges(raw_ids)
    except ValueError as exc:
        return str(exc)
    collected = _run(["uv", "run", "pytest", "--collect-only", "-q"])
    if collected.returncode != 0:
        return f"pytest collection exited {collected.returncode}: {_output_summary(collected)}"
    node_ids = parse_collected_node_ids(collected.stdout)
    missing = [plan_id for plan_id in ids if not id_has_test(plan_id, node_ids)]
    if missing:
        return "missing test functions for plan IDs: " + ", ".join(missing)
    return None


def _phase_argument(value: str) -> str:
    normalized = value.lower()
    if re.fullmatch(r"p\d+", normalized) is None:
        raise argparse.ArgumentTypeError("phase must look like p1")
    return normalized


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", type=_phase_argument)
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args(argv)
    results = GateResults()
    _check_universal(results, args.phase, args.ci)
    if results.failures:
        print(f"FAIL common gate: {results.failures} check(s) failed")
        return 1
    print("PASS common gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
