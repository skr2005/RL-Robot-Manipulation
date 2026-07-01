import json
import re
from pathlib import Path
import csv
import wunderbar

# source data directory containing run1.wandb ... run10.wandb
SOURCE_DIR = Path(__file__).parent / "source_data"
# output folder alongside source_data
OUTDIR = SOURCE_DIR.parent / "output"
OUTDIR.mkdir(parents=True, exist_ok=True)

BOUNDARY = 1_000_000


def output_text(record):
    for key in ("text", "line", "stdout"):
        if key in record.data:
            return record.data[key]
    return json.dumps(record.data, ensure_ascii=False)


def _find_success_value(item: dict):
    candidates = ("success_rate", "eval/success_rate", "success", "success_rate_mean")
    for k in candidates:
        if k in item:
            try:
                return float(item[k])
            except Exception:
                pass
    for k, v in item.items():
        if "success" in k.lower():
            try:
                return float(v)
            except Exception:
                continue
    return None


def _find_success_in_text(text: str):
    if not text:
        return None
    # try patterns like 'success_rate 0.75' or 'success_rate: 75.0%'
    m = re.search(
        r"success[_/ ]*rate[^0-9\-+\.eE%]*([-+]?\d+(?:\.\d+)?)(%)?", text, re.IGNORECASE
    )
    if m:
        val = float(m.group(1))
        if m.group(2) == "%":
            val = val / 100.0
        return val
    # fallback: lines containing 'success' then a number somewhere nearby
    for line in text.splitlines():
        if "success" in line.lower():
            m2 = re.search(r"([-+]?\d+(?:\.\d+)?)", line)
            if m2:
                return float(m2.group(1))
    return None


def _find_timesteps_in_text(text: str):
    if not text:
        return None
    # common patterns: '|    total_timesteps | 200      |' or 'Eval num_timesteps=2000' or 'total_timesteps | 200'
    m = re.search(r"total[_ ]?timesteps[^0-9\-+]*([0-9]+)", text, re.IGNORECASE)
    if m:
        return int(m.group(1))
    m2 = re.search(r"num_timesteps\s*=\s*([0-9]+)", text, re.IGNORECASE)
    if m2:
        return int(m2.group(1))
    # fallback: look for a standalone 'total_timesteps' line followed by a number in the same block
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if "total_timesteps" in line.lower():
            # try to find number in same line
            m3 = re.search(r"([0-9]+)", line)
            if m3:
                return int(m3.group(1))
            # else check next few lines
            for j in range(i + 1, min(i + 4, len(lines))):
                m4 = re.search(r"([0-9]+)", lines[j])
                if m4:
                    return int(m4.group(1))
    return None


def open_next_file(outdir, prefix, boundary):
    return outdir / f"{prefix}_output_{boundary-BOUNDARY}_{boundary}.json"


def process_input(input_path: Path):
    prefix = input_path.stem
    records = []
    x_list = []
    y_list = []
    last_ts = None
    pending_success = None

    for record in wunderbar.parse_filepath(input_path):
        # store a minimal parsed representation for JSON export
        if record.type == "output_raw":
            text = output_text(record)
            records.append({"type": "output_raw", "output": text})
            succ = _find_success_in_text(text)
            ts_from_text = _find_timesteps_in_text(text)
            if ts_from_text is not None:
                last_ts = int(ts_from_text)
                if pending_success is not None:
                    x_list.append(int(last_ts))
                    y_list.append(float(pending_success))
                    pending_success = None
            if succ is not None:
                if last_ts is not None:
                    x_list.append(int(last_ts))
                    y_list.append(float(succ))
                else:
                    pending_success = succ
        elif record.type == "history":
            item = record.data.get("item", {})
            records.append({"type": "history", "item": item})
            if "total_timesteps" in item:
                last_ts = int(item["total_timesteps"])
                if pending_success is not None:
                    x_list.append(int(last_ts))
                    y_list.append(float(pending_success))
                    pending_success = None
            succ = _find_success_value(item)
            if succ is not None:
                ts_for_pair = (
                    int(item.get("total_timesteps", last_ts))
                    if ("total_timesteps" in item or last_ts is not None)
                    else None
                )
                if ts_for_pair is not None:
                    x_list.append(int(ts_for_pair))
                    y_list.append(float(succ))

    # write parsed wandb records to JSON
    parsed_path = OUTDIR / f"{prefix}_parsed.json"
    with parsed_path.open("w", encoding="utf-8") as fp:
        json.dump(records, fp, ensure_ascii=False, indent=2)

    # write xy pairs as JSON and CSV (no npz)
    if x_list:
        pairs = list(zip([int(v) for v in x_list], [float(v) for v in y_list]))
        with (OUTDIR / f"{prefix}_xy_pairs.json").open("w", encoding="utf-8") as fp:
            json.dump(pairs, fp, ensure_ascii=False)
        csv_path = OUTDIR / f"{prefix}_xy.csv"
        with csv_path.open("w", encoding="utf-8", newline="") as fp:
            writer = csv.writer(fp)
            writer.writerow(["total_timesteps", "success_rate"])
            for a, b in pairs:
                writer.writerow([a, b])
        print(
            f"saved parsed JSON and xy CSV/JSON for {prefix}: {parsed_path}, {csv_path}"
        )
    else:
        print(f"no (total_timesteps, success) pairs found for {prefix}")


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
