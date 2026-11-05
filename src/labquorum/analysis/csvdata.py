"""Safe CSV decoding and profiling for staged datasets."""

from __future__ import annotations

import csv
import io
import re
from collections import Counter
from collections.abc import Iterable
from typing import Any

from labquorum.domain.errors import ErrorCode, LabQuorumError

_DELIMITERS = (",", ";", "\t")
_WELL_PATTERN = re.compile(r"\A[A-H](?:[1-9]|1[0-2])\Z", re.IGNORECASE)
_EMAIL_PATTERN = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)")
_AADHAAR_PATTERN = re.compile(r"(?<!\d)\d{12}(?!\d)")
_NUMERIC_PATTERN = re.compile(r"\A[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?\Z")
_SENSITIVE_HEADER_TOKENS = {
    "aadhaar",
    "date_of_birth",
    "dob",
    "email",
    "mrn",
    "name",
    "participant",
    "participant_id",
    "participant_name",
    "phone",
    "phone_number",
    "subject_id",
}


def parse_csv(data: bytes) -> tuple[list[str], list[dict[str, str]], str, str]:
    """Decode a UTF-8 CSV and return headers, string rows, delimiter, and decimal mark."""
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Dataset CSV must be UTF-8 encoded, with or without a UTF-8 BOM.",
        ) from exc
    if not text.strip():
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Dataset CSV is empty.")

    delimiter = _sniff_delimiter(text)
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)
    try:
        raw_headers = next(reader)
    except StopIteration as exc:
        raise LabQuorumError(ErrorCode.INVALID_ARGUMENT, "Dataset CSV has no header row.") from exc
    headers = [header.strip() for header in raw_headers]
    if not headers or any(not header for header in headers) or len(set(headers)) != len(headers):
        raise LabQuorumError(
            ErrorCode.INVALID_ARGUMENT,
            "Dataset CSV headers must be nonempty and unique.",
        )

    rows: list[dict[str, str]] = []
    for row_number, values in enumerate(reader, start=2):
        if not values or (len(values) == 1 and not values[0].strip()):
            continue
        if len(values) != len(headers):
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                f"CSV row {row_number} has {len(values)} cells; expected {len(headers)}.",
            )
        rows.append({header: value.strip() for header, value in zip(headers, values, strict=True)})

    decimal_mark = "," if delimiter != "," and _has_decimal_comma(rows) else "."
    return headers, rows, delimiter, decimal_mark


def profile_csv(data: bytes) -> dict[str, Any]:
    """Summarize CSV shape and suspicious cells without evaluating cell content."""
    headers, rows, delimiter, decimal_mark = parse_csv(data)
    missing_counts = {header: sum(not row[header] for row in rows) for header in headers}
    column_types = {
        header: _column_type((row[header] for row in rows), decimal_mark) for header in headers
    }

    row_counts = Counter(tuple(row[header] for header in headers) for row in rows)
    duplicate_rows = sum(count - 1 for count in row_counts.values() if count > 1)
    duplicate_wells: list[str] = []
    if "well" in headers:
        well_counts = Counter(row["well"] for row in rows if row["well"])
        duplicate_wells = sorted(well for well, count in well_counts.items() if count > 1)

    out_of_range_od: list[dict[str, str]] = []
    if "od590" in headers:
        for row in rows:
            value = _number(row["od590"], decimal_mark)
            if value is not None and not 0 <= value <= 3:
                out_of_range_od.append({"well": row.get("well", ""), "value": row["od590"]})

    unknown_wells: list[str] = []
    if "well" in headers:
        unknown_wells = sorted(
            {
                row["well"]
                for row in rows
                if row["well"] and _WELL_PATTERN.fullmatch(row["well"]) is None
            }
        )

    formula_cells: list[dict[str, Any]] = []
    for row_number, row in enumerate(rows, start=2):
        for header, value in row.items():
            if _is_formula(value, decimal_mark):
                formula_cells.append(
                    {"row": row_number, "column": header, "value": _escape_formula(value)}
                )

    return {
        "delimiter": delimiter,
        "decimal_mark": decimal_mark,
        "rows": len(rows),
        "columns": headers,
        "column_types": column_types,
        "missing_counts": missing_counts,
        "duplicate_rows": duplicate_rows,
        "duplicate_wells": duplicate_wells,
        "out_of_range_od": out_of_range_od,
        "unknown_wells": unknown_wells,
        "requires_correction": bool(unknown_wells or duplicate_wells),
        "formula_cells": formula_cells[:100],
        "formula_cells_truncated": len(formula_cells) > 100,
    }


def contains_human_subject_data(headers: Iterable[str], rows: Iterable[dict[str, str]]) -> bool:
    """Conservatively flag common direct identifiers before a dataset is staged."""
    normalized = {
        header.casefold().strip().replace("-", "_").replace(" ", "_") for header in headers
    }
    if any(set(header.split("_")) & _SENSITIVE_HEADER_TOKENS for header in normalized):
        return True
    for row in rows:
        for value in row.values():
            phone_match = _PHONE_PATTERN.search(value)
            phone_digits = sum(character.isdigit() for character in value)
            if _EMAIL_PATTERN.search(value) or (phone_match and phone_digits >= 10):
                return True
            if _AADHAAR_PATTERN.search(value):
                return True
    return False


def _sniff_delimiter(text: str) -> str:
    sample = text[:16_384]
    try:
        return csv.Sniffer().sniff(sample, delimiters="".join(_DELIMITERS)).delimiter
    except csv.Error as exc:
        candidates: list[tuple[int, int, str]] = []
        for delimiter in _DELIMITERS:
            widths = [
                len(row) for row in csv.reader(io.StringIO(sample, newline=""), delimiter=delimiter)
            ]
            consistent = sum(width == widths[0] for width in widths) if widths else 0
            candidates.append((consistent, widths[0] if widths else 0, delimiter))
        consistent, width, delimiter = max(candidates)
        if width <= 1 or consistent < 2:
            raise LabQuorumError(
                ErrorCode.INVALID_ARGUMENT,
                "Could not determine a comma, semicolon, or tab CSV delimiter.",
            ) from exc
        return delimiter


def _has_decimal_comma(rows: Iterable[dict[str, str]]) -> bool:
    return any(
        re.fullmatch(r"[+-]?\d+,\d+(?:[eE][+-]?\d+)?", value) is not None
        for row in rows
        for value in row.values()
    )


def _number(value: str, decimal_mark: str) -> float | None:
    if not value:
        return None
    normalized = value.replace(",", ".") if decimal_mark == "," else value
    if _NUMERIC_PATTERN.fullmatch(normalized) is None:
        return None
    try:
        return float(normalized)
    except ValueError:
        return None


def _column_type(values: Iterable[str], decimal_mark: str) -> str:
    nonempty = [value for value in values if value]
    if nonempty and all(_number(value, decimal_mark) is not None for value in nonempty):
        return "numeric"
    return "text"


def _is_formula(value: str, decimal_mark: str) -> bool:
    if not value or value[0] not in "=+-@":
        return False
    return _number(value, decimal_mark) is None


def _escape_formula(value: str) -> str:
    return f"'{value}"
