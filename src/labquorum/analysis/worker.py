"""Subprocess entry point for the fixed descriptive recipe."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

from labquorum.analysis.descriptive import (
    save_descriptive_figure,
    summarize_descriptive_dataset,
    write_summary_json,
)


def _inside(root: Path, candidate: Path) -> Path:
    resolved_root = root.expanduser().resolve(strict=True)
    resolved_candidate = candidate.expanduser().resolve(strict=True)
    try:
        resolved_candidate.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Analysis worker paths must stay inside the staging root.") from exc
    return resolved_candidate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="labquorum-analysis-worker")
    parser.add_argument("--staging-root", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        root = args.staging_root.expanduser().resolve(strict=True)
        dataset_path = _inside(root, args.dataset)
        output_dir = args.output_dir.expanduser().resolve(strict=False)
        try:
            output_dir.relative_to(root)
        except ValueError as exc:
            raise ValueError("Analysis outputs must stay inside the staging root.") from exc
        output_dir.mkdir(parents=True, exist_ok=True)
        content = dataset_path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        if digest != args.expected_sha256:
            raise ValueError("Staged dataset hash changed before analysis started.")
        summary = summarize_descriptive_dataset(content, digest)
        write_summary_json(summary, output_dir / "summary.json")
        save_descriptive_figure(summary, output_dir / "summary.png")
        return 0
    except Exception as exc:
        print(f"analysis worker failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
