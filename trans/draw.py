from pathlib import Path
import csv
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def read_csv_xy(csv_path: Path):
    x = []
    y = []
    with csv_path.open("r", encoding="utf-8") as fp:
        reader = csv.reader(fp)
        next(reader, None)
        for row in reader:
            if not row or len(row) < 2:
                continue
            try:
                tx = int(float(row[0]))
                sy = float(row[1])
            except Exception:
                continue
            if sy > 1.0 and sy <= 100.0:
                sy = sy / 100.0
            elif sy > 100.0:
                sy = 1.0
            if sy < 0.0:
                sy = 0.0
            x.append(tx)
            y.append(sy)
    return x, y


def smooth_values(y_values):
    y = np.asarray(y_values, dtype=float)
    n = y.shape[0]
    if n < 3:
        return y
    window = min(11, n)
    if window % 2 == 0:
        window -= 1
    weights = np.ones(window, dtype=float) / window
    pad = window // 2
    padded = np.pad(y, pad_width=pad, mode="edge")
    return np.convolve(padded, weights, mode="valid")


def plot_xy(x, y, title, save_path: Path):
    smoothed = smooth_values(y)
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, y, color="gray", alpha=0.3, linewidth=1)
    ax.plot(x, smoothed, color="tab:blue", linewidth=2, label="smoothed")
    if len(x) > 0:
        step = max(1, len(x) // 60)
        ax.scatter(x[::step], smoothed[::step], color="tab:blue", s=20)
    ax.set_xlabel("total_timesteps")
    ax.set_ylabel("success_rate")
    ax.set_title(title)
    ax.set_ylim(-0.01, 1.01)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def main():
    base = Path(__file__).parent
    data_dir = base / "manipulated"
    result_dir = base / "result"
    if not data_dir.exists():
        print(f"Directory not found: {data_dir}")
        return
    result_dir.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {data_dir}")
        return

    for csv_path in csv_files:
        x, y = read_csv_xy(csv_path)
        if not x:
            print(f"Skipping empty or invalid CSV: {csv_path.name}")
            continue
        stem = csv_path.stem
        title = f"{stem}: success_rate vs total_timesteps (smoothed)"
        out_png = result_dir / f"{stem}.png"
        plot_xy(x, y, title, out_png)
        print(f"Saved plot to: {out_png}")


if __name__ == "__main__":
    main()
