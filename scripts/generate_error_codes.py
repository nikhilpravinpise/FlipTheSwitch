"""Update the README error-code table from the closed domain enum."""

from __future__ import annotations

from pathlib import Path

from labquorum.domain.errors import error_codes_markdown

README_PATH = Path(__file__).resolve().parents[1] / "README.md"
START_MARKER = "<!-- error-codes:start -->"
END_MARKER = "<!-- error-codes:end -->"


def update_readme(path: Path = README_PATH) -> bool:
    """Replace the marked README table and report whether the file changed."""
    contents = path.read_text(encoding="utf-8")
    if contents.count(START_MARKER) != 1 or contents.count(END_MARKER) != 1:
        raise ValueError("README must contain exactly one pair of error-code table markers.")
    start = contents.index(START_MARKER)
    end = contents.index(END_MARKER)
    if end < start:
        raise ValueError("README error-code markers are out of order.")
    rendered = f"{START_MARKER}\n{error_codes_markdown()}\n{END_MARKER}"
    updated = contents[:start] + rendered + contents[end + len(END_MARKER) :]
    if updated == contents:
        return False
    path.write_text(updated, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    changed = update_readme()
    print(
        "README.md error-code table updated."
        if changed
        else "README.md error-code table is current."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
