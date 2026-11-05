"""Unit tests for reusable universal gate checks."""

from pathlib import Path

from scripts.gates.common import expand_id_ranges, id_has_test, scan_em_dash, scan_secret_patterns


def test_em_dash_scanner_reads_temp_text_file(tmp_path: Path) -> None:
    sample = tmp_path / "sample.txt"
    sample.write_text("plain text", encoding="utf-8")
    assert not scan_em_dash(sample)

    sample.write_text("text" + chr(0x2014), encoding="utf-8")
    assert scan_em_dash(sample)


def test_secret_scanner_reports_patterns_from_temp_file(tmp_path: Path) -> None:
    sample = tmp_path / "credentials.txt"
    private_header = b"-" * 5 + b"BEGIN " + b"TEST " + b"PRIVATE KEY" + b"-" * 5
    contents = b"\n".join(
        [
            b"sk-" + b"A" * 20,
            b"ghp_" + b"B" * 30,
            b"AKIA" + b"C" * 16,
            private_header,
        ]
    )
    sample.write_bytes(contents)

    assert scan_secret_patterns(sample.read_bytes()) == [
        "OpenAI-style key",
        "GitHub token",
        "AWS access key",
        "private key header",
    ]


def test_id_name_matcher_uses_function_name_prefix(tmp_path: Path) -> None:
    collection = tmp_path / "collected.txt"
    collection.write_text(
        "tests/unit/test_booking.py::test_U_B02_conflict_names_booking\n"
        "tests/unit/test_booking.py::test_U_B03_half_open_interval\n",
        encoding="utf-8",
    )
    node_ids = collection.read_text(encoding="utf-8").splitlines()

    assert id_has_test("U-B02", node_ids)
    assert not id_has_test("U-B04", node_ids)


def test_range_expansion_reads_temp_claim_file(tmp_path: Path) -> None:
    claims = tmp_path / "claims.txt"
    claims.write_text("U-B01..U-B03\nP-01..P-02\nU-G06\n", encoding="utf-8")

    assert expand_id_ranges(claims.read_text(encoding="utf-8").splitlines()) == [
        "U-B01",
        "U-B02",
        "U-B03",
        "P-01",
        "P-02",
        "U-G06",
    ]
