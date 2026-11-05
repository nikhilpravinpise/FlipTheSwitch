"""Single vetted descriptive recipe for the synthetic plate-reader fixture."""

from __future__ import annotations

import importlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

from labquorum.analysis.csvdata import parse_csv
from labquorum.domain.errors import ErrorCode, LabQuorumError

RECIPE_NAME = "descriptive"
RECIPE_VERSION = "1.0.0"
CONCENTRATIONS = (0, 2, 4, 8, 16, 32, 64)
PLATE_ROWS = tuple("ABCDEFGH")
PLATE_COLUMNS = tuple(range(1, 13))
COLORBLIND_SAFE_PALETTE = (
    "#0072B2",
    "#E69F00",
    "#009E73",
    "#CC79A7",
    "#56B4E9",
    "#D55E00",
    "#F0E442",
)


def validate_descriptive_dataset(data: bytes) -> None:
    """Check plate identities and dose mapping without changing any observation."""
    headers, rows, _, decimal_mark = parse_csv(data)
    required = {"well", "row", "col", "condition", "egcg_ug_ml", "replicate", "od590"}
    missing = required - set(headers)
    if missing:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Descriptive plate CSV is missing required columns: {', '.join(sorted(missing))}.",
        )

    dose_counts: dict[int, int] = {dose: 0 for dose in CONCENTRATIONS}
    observed_wells: set[str] = set()
    treatment_count = 0
    blank_count = 0
    for item in rows:
        well, row_label, column = _well_identity(item)
        if well in observed_wells:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT, f"Duplicate well {well} needs correction."
            )
        observed_wells.add(well)
        _parse_number(item["od590"], decimal_mark, well)
        if row_label in "BCDEFG" and column in range(2, 9):
            dose = _validate_treatment_row(item, row_label, column, decimal_mark)
            dose_counts[dose] += 1
            treatment_count += 1
        else:
            _validate_blank_row(item, well)
            blank_count += 1
    expected_wells = {f"{row}{column}" for row in PLATE_ROWS for column in PLATE_COLUMNS}
    missing_wells = expected_wells - observed_wells
    if missing_wells:
        names = ", ".join(sorted(missing_wells))
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Plate is incomplete; missing wells: {names}.",
        )
    incorrect_counts = {dose: count for dose, count in dose_counts.items() if count != 6}
    if incorrect_counts:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Each concentration requires six technical wells; observed counts {incorrect_counts}.",
        )
    if treatment_count != 42 or blank_count != 54:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Plate mapping must contain exactly 42 treatment wells and 54 medium-only blanks.",
        )


def _well_identity(item: dict[str, str]) -> tuple[str, str, int]:
    well = item["well"].upper()
    row_label = item["row"].upper()
    try:
        column = int(item["col"])
    except ValueError as exc:
        raise _unknown_well(well) from exc
    if row_label not in PLATE_ROWS or column not in PLATE_COLUMNS:
        raise _unknown_well(well)
    if well != f"{row_label}{column}":
        raise _unknown_well(well)
    return well, row_label, column


def _unknown_well(well: str) -> LabQuorumError:
    return LabQuorumError(
        ErrorCode.INVALID_ARGUMENT,
        f"Unknown well mapping ({well or '<empty>'}) is staged for correction and was not auto-matched.",
    )


def _validate_treatment_row(
    item: dict[str, str],
    row_label: str,
    column: int,
    decimal_mark: str,
) -> int:
    well = item["well"]
    dose = CONCENTRATIONS[column - 2]
    if item["condition"].casefold() != "egcg":
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Well {well} is a treatment location but is not labeled EGCG.",
        )
    try:
        recorded_dose = _parse_number(item["egcg_ug_ml"], decimal_mark, well)
        replicate = int(item["replicate"])
    except ValueError as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Well {well} has an invalid dose or replicate mapping.",
        ) from exc
    expected_replicate = PLATE_ROWS.index(row_label)
    if recorded_dose != dose or replicate != expected_replicate:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Well {well} does not match its planned {dose} ug/mL technical replicate mapping.",
        )
    return dose


def _validate_blank_row(item: dict[str, str], well: str) -> None:
    if item["condition"].casefold() != "medium_only":
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Well {well} is a blank location but is not labeled medium_only.",
        )
    if item["egcg_ug_ml"] or item["replicate"]:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Blank well {well} must not contain a dose or replicate assignment.",
        )


def summarize_descriptive_dataset(data: bytes, dataset_sha256: str) -> dict[str, Any]:
    """Return deterministic counts, means and sample SDs, without inferential statistics."""
    validate_descriptive_dataset(data)
    headers, rows, _, decimal_mark = parse_csv(data)
    del headers
    groups: dict[int, list[float]] = {concentration: [] for concentration in CONCENTRATIONS}
    blanks: list[tuple[str, float]] = []
    for item in rows:
        row_label = item["row"].upper()
        column = int(item["col"])
        value = _parse_number(item["od590"], decimal_mark, item["well"])
        if row_label in "BCDEFG" and column in range(2, 9):
            groups[CONCENTRATIONS[column - 2]].append(value)
        else:
            blanks.append((item["well"].upper(), value))

    flagged_qc_blanks = sorted(
        well for well, value in blanks if well in {"A1", "H12"} and value > 0.5
    )
    retained_blanks = [value for well, value in blanks if well not in flagged_qc_blanks]
    group_summaries = [
        {
            "condition": str(concentration),
            "dose_ug_ml": concentration,
            "count": len(values),
            "mean_od590": _round(statistics.mean(values)),
            "sd_od590": _round(statistics.stdev(values)),
            "unit": "OD590",
            "replicate_type": "technical well replicate",
        }
        for concentration, values in groups.items()
    ]
    return {
        "recipe": RECIPE_NAME,
        "recipe_version": RECIPE_VERSION,
        "dataset_sha256": dataset_sha256,
        "groups": group_summaries,
        "treatment_wells": sum(len(values) for values in groups.values()),
        "experimental_unit": "technical well replicate",
        "inference": "descriptive only; no p-values or significance claims",
        "blank_summary": {
            "count": len(retained_blanks),
            "mean_od590": _round(statistics.mean(retained_blanks)),
            "sd_od590": _round(statistics.stdev(retained_blanks)),
            "flagged_wells_excluded_from_blank_summary": flagged_qc_blanks,
            "interpretation": (
                "A1 and H12 are synthetic high-OD QC anomalies, not proven evaporation; "
                "no treatment wells were removed and treatment values were not blank-subtracted."
            ),
        },
        "flagged_qc_blanks": flagged_qc_blanks,
    }


def save_descriptive_figure(summary: dict[str, Any], output_path: Path) -> None:
    """Write the fixed-style colorblind-safe PNG figure for the descriptive recipe."""
    matplotlib: Any = importlib.import_module("matplotlib")
    matplotlib.use("Agg")
    plt: Any = importlib.import_module("matplotlib.pyplot")

    groups = summary["groups"]
    concentrations = [item["dose_ug_ml"] for item in groups]
    means = [item["mean_od590"] for item in groups]
    spreads = [item["sd_od590"] for item in groups]
    with plt.rc_context(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 13,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
        }
    ):
        figure, axis = plt.subplots(figsize=(8, 4.8), layout="constrained")
        axis.bar(
            [str(value) for value in concentrations],
            means,
            yerr=spreads,
            capsize=4,
            color=COLORBLIND_SAFE_PALETTE,
            edgecolor="#222222",
            linewidth=0.6,
        )
        axis.set_title("Synthetic plate-reader assay: descriptive summary")
        axis.set_xlabel("EGCG concentration (ug/mL)")
        axis.set_ylabel("Mean absorbance (OD590) +/- SD")
        axis.set_ylim(bottom=0)
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.7)
        axis.set_axisbelow(True)
        figure.savefig(
            output_path,
            format="png",
            dpi=150,
            metadata={"Software": "LabQuorum descriptive recipe 1.0.0"},
        )
        plt.close(figure)


def write_summary_json(summary: dict[str, Any], output_path: Path) -> None:
    """Write stable UTF-8 JSON without non-finite numeric values."""
    output_path.write_text(
        json.dumps(
            summary, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _parse_number(value: str, decimal_mark: str, well: str) -> float:
    normalized = value.replace(",", ".") if decimal_mark == "," else value
    try:
        number = float(normalized)
    except ValueError as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Well {well} has a missing or invalid OD590 value.",
        ) from exc
    if not math.isfinite(number):
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            f"Well {well} has a non-finite OD590 value.",
        )
    return number


def _round(value: float) -> float:
    return round(value, 6)
