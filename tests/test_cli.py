import pytest

from research_check.cli import main


@pytest.mark.parametrize(
    ("options", "measurements", "expected_ranges"),
    [
        ([], [-1, 0, 100, 101], 2),
        (["--minimum", "5"], [4, 5, 100], 1),
        (["--maximum", "20"], [0, 20, 21], 1),
    ],
)
def test_cli_applies_measurement_limits(
    tmp_path, monkeypatch, capsys, options, measurements, expected_ranges
):
    csv_file = tmp_path / "observations.csv"
    csv_file.write_text(
        "sample_id,measurement\n"
        + "".join(
            f"sample-{index},{value}\n"
            for index, value in enumerate(measurements)
        ),
        encoding="utf-8",
    )
    original = csv_file.read_bytes()
    monkeypatch.setattr("sys.argv", ["research_check", str(csv_file), *options])

    assert main() == 0

    output = capsys.readouterr().out
    assert f"range: {expected_ranges}" in output
    assert csv_file.read_bytes() == original


def test_cli_applies_custom_inclusive_limits(tmp_path, monkeypatch, capsys):
    csv_file = tmp_path / "observations.csv"
    csv_file.write_text(
        "sample_id,measurement\n"
        "below,4\n"
        "minimum,5\n"
        "maximum,20\n"
        "above,21\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["research_check", str(csv_file), "--minimum", "5", "--maximum", "20"],
    )

    assert main() == 0

    output = capsys.readouterr().out
    assert "range: 2" in output
    assert "measurement=4.0 is outside [5.0, 20.0]" in output
    assert "measurement=21.0 is outside [5.0, 20.0]" in output
    assert "measurement=5.0" not in output
    assert "measurement=20.0" not in output


def test_cli_rejects_minimum_above_maximum(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        [
            "research_check",
            str(tmp_path / "observations.csv"),
            "--minimum",
            "5",
            "--maximum",
            "4",
        ],
    )

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2
    assert (
        "--minimum must be less than or equal to --maximum"
        in capsys.readouterr().err
    )
