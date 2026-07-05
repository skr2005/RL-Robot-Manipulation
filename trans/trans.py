import json
import re
from pathlib import Path
import csv
from wunderbar.parsers import parse_filepath, LogRecord
from typing import cast, Iterable

# source data directory containing run1.wandb ... run10.wandb
SOURCE_DIR = Path(__file__).parent / "source_data"
# output folder alongside source_data
OUTDIR = SOURCE_DIR.parent / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

BOUNDARY = 1_000_000


def process_input(input_path: Path):
    prefix = input_path.stem

    parsed = cast(Iterable[LogRecord], parse_filepath(input_path))

    # write parsed wandb records to JSON
    parsed_path = OUTDIR / f"{prefix}_parsed.json"
    with parsed_path.open("w", encoding="utf-8") as fp:
        json.dump(
            list(
                map(
                    lambda r: {"type": r.type, "number": r.number, "data": r.data},
                    parse_filepath(input_path),
                )
            ),
            fp,
            ensure_ascii=False,
            indent=2,
        )

    _ = filter(
        lambda r: r.type == "output_raw" and r.data.get("output_type") == "STDOUT",
        parsed,
    )

    _ = map(lambda r: r.data["line"], _)

    _ = filter(lambda ln: "success_rate" in ln and "total_timesteps" in ln, _)

    find_first_float_after_marker = lambda text, marker: float(
        re.search(
            re.escape(marker) + r".*?([-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?)",
            text,
        ).group(1)
    )

    _ = map(
        lambda ln: (
            find_first_float_after_marker(ln, "total_timesteps"),
            find_first_float_after_marker(ln, "success_rate"),
        ),
        _,
    )

    # write xy pairs as JSON and CSV (no npz)
    pairs = list(_)
    with (OUTDIR / f"{prefix}_xy_pairs.json").open("w", encoding="utf-8") as fp:
        json.dump(pairs, fp, ensure_ascii=False)
    csv_path = OUTDIR / f"{prefix}_xy.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.writer(fp)
        writer.writerow(["total_timesteps", "success_rate"])
        for a, b in pairs:
            writer.writerow([a, b])
    print(f"saved parsed JSON and xy CSV/JSON for {prefix}: {parsed_path}, {csv_path}")


def _extract_run_number(p: Path):
    m = re.search(r"(\d+)", p.stem)
    return int(m.group(1)) if m else 0


def main():
    if not SOURCE_DIR.exists():
        raise SystemExit(f"source_data directory not found: {SOURCE_DIR}")

    files = list(SOURCE_DIR.glob("run*.wandb"))
    files = sorted(files, key=_extract_run_number)
    for f in files:
        print(f"processing {f.name}...")
        process_input(f)


if __name__ == "__main__":
    main()
