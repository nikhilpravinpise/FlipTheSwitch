"""Generate the synthetic 96-well plate fixtures used by the descriptive recipe."""

from __future__ import annotations

import csv
import math
import random
from pathlib import Path

SEED = 20261107
DOSES_UG_ML = (0, 2, 4, 8, 16, 32, 64)
OUTPUT_DIRECTORY = Path(__file__).resolve().parent


def plate_rows() -> list[list[str | int]]:
    """Return all wells with fixed synthetic measurements and plate mappings."""
    rng = random.Random(SEED)
    rows: list[list[str | int]] = []
    for row_index, row in enumerate("ABCDEFGH"):
        for column in range(1, 13):
            well = f"{row}{column}"
            if row in "BCDEFG" and 2 <= column <= 8:
                concentration = DOSES_UG_ML[column - 2]
                replicate = row_index
                od590 = 0.08 + 1.2 * math.exp(-0.035 * concentration) + rng.gauss(0, 0.06)
                if well == "C5":
                    od590 = 0.083
                rows.append(
                    [
                        well,
                        row,
                        column,
                        "EGCG",
                        concentration,
                        replicate,
                        f"{od590:.3f}",
                    ]
                )
            else:
                od590 = 0.08 + rng.gauss(0, 0.02)
                if well == "A1":
                    od590 = 1.5
                elif well == "H12":
                    od590 = 1.8
                rows.append([well, row, column, "medium_only", "", "", f"{od590:.3f}"])
    return rows


def write_fixtures() -> None:
    """Write v1 and corrected v2; C5 is their only differing value."""
    header = ["well", "row", "col", "condition", "egcg_ug_ml", "replicate", "od590"]
    rows = plate_rows()
    for name, corrected in (("plate3_od590.csv", False), ("plate3_od590_v2.csv", True)):
        fixture_rows = [list(row) for row in rows]
        if corrected:
            c5 = next(row for row in fixture_rows if row[0] == "C5")
            c5[-1] = "0.830"
        with (OUTPUT_DIRECTORY / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\r\n")
            writer.writerow(header)
            writer.writerows(fixture_rows)


if __name__ == "__main__":
    write_fixtures()
