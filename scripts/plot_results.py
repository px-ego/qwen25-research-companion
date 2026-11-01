"""Render final-manuscript results. No training or model evaluation is performed."""

import json
import platform
from io import StringIO

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from check_results import BENCHMARKS, MODELS, ROOT, load_results, sha256

BLUE = "#225E8A"
GRAY = "#5A626B"
INK = "#202B35"


def save(fig, stem):
    fig.savefig(ROOT / f"figures/{stem}.png", facecolor="white", dpi=180,
                metadata={"Software": "Research companion, Matplotlib"})
    stream = StringIO()
    fig.savefig(stream, format="svg", facecolor="white", metadata={"Date": None})
    svg = "\n".join(line.rstrip() for line in stream.getvalue().splitlines()) + "\n"
    (ROOT / f"figures/{stem}.svg").write_text(svg, encoding="utf-8", newline="\n")
    plt.close(fig)


def format_axis(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#DDE2E6", linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color("#939BA2")
        ax.spines[spine].set_linewidth(0.8)
    ax.tick_params(colors=INK, length=3)


def plot_1p5b(rows):
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.8))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.22, top=0.83, hspace=0.50, wspace=0.20)
    fig.suptitle("Qwen2.5-Coder-1.5B-Instruct: data-scale comparison", x=0.08, y=0.97, ha="left", fontsize=16, weight="bold")
    fig.text(0.08, 0.915, "Final manuscript, Table 2. Exact labels show pass@1 (%) and reported sample SD.", fontsize=11, color=GRAY)
    fig.text(0.08, 0.045, "Open circle: baseline, one evaluation. Squares: mean ± sample SD over three training runs.\nError bars describe run-to-run spread; they are not confidence intervals. Focused y-axis: 55-75%.", fontsize=10, color=GRAY, linespacing=1.6)
    for ax, benchmark in zip(axes.flat, BENCHMARKS):
        group = [r for r in rows if r["model"] == MODELS[0] and r["benchmark"] == benchmark]
        baseline = float(group[0]["pass_at_1_pct"])
        ax.axhline(baseline, linestyle=(0, (4, 3)), linewidth=1, color=GRAY, alpha=0.65)
        ax.plot(0, baseline, marker="o", mfc="white", mec=GRAY, mew=1.5, markersize=7)
        for i, row in enumerate(group):
            mean = float(row["pass_at_1_pct"])
            sd = float(row["sample_sd_pp"]) if row["sample_sd_pp"] else 0
            if i:
                ax.errorbar(i, mean, yerr=sd, fmt="s", color=BLUE, markersize=6,
                            capsize=4, elinewidth=1.4, capthick=1.4)
            label = row["pass_at_1_pct"] + (" ± " + row["sample_sd_pp"] if i else "")
            ax.annotate(label, (i, mean + sd), xytext=(0, 8), textcoords="offset points",
                        ha="center", fontsize=10, color=INK)
        ax.set_title(benchmark, loc="left", fontsize=12, pad=12, weight="bold")
        ax.set_xticks(range(4), ["0\nBaseline", "5K", "10K", "15K"])
        ax.set_xlim(-0.55, 3.55)
        ax.set_ylim(55, 75)
        ax.set_yticks([55, 60, 65, 70, 75])
        ax.set_ylabel("pass@1 (%)")
        ax.set_xlabel("Fine-tuning samples")
        format_axis(ax)
    save(fig, "1p5b_data_scale")


def plot_3b(rows):
    fig, ax = plt.subplots(figsize=(12, 6.4))
    fig.subplots_adjust(left=0.08, right=0.98, bottom=0.20, top=0.73)
    fig.suptitle("Qwen2.5-Coder-3B-Instruct: before and after fine-tuning", x=0.08, y=0.97, ha="left", fontsize=16, weight="bold")
    fig.text(0.08, 0.90, "Final manuscript, Table 3. One baseline and one 15K fine-tuned checkpoint.", fontsize=11, color=GRAY)
    index = {(r["training_samples"], r["benchmark"]): r for r in rows if r["model"] == MODELS[1]}
    for offset, samples, label, color, hatch in [
        (-0.19, "0", "Baseline", GRAY, "///"),
        (0.19, "15000", "15K fine-tuned", BLUE, None),
    ]:
        values = [float(index[(samples, b)]["pass_at_1_pct"]) for b in BENCHMARKS]
        bars = ax.bar([i + offset for i in range(4)], values, width=0.32, label=label,
                      color="white" if samples == "0" else color, edgecolor=color,
                      hatch=hatch, linewidth=1.2)
        ax.bar_label(bars, labels=[index[(samples, b)]["pass_at_1_pct"] for b in BENCHMARKS],
                     padding=5, fontsize=11, color=INK)
    for i, benchmark in enumerate(BENCHMARKS):
        delta = float(index[("15000", benchmark)]["pass_at_1_pct"]) - float(index[("0", benchmark)]["pass_at_1_pct"])
        ax.text(i, 98, f"Change {delta:+.2f} pp", ha="center", va="top", fontsize=10, color=GRAY)
    ax.set_xticks(range(4), BENCHMARKS)
    ax.set_ylim(0, 100)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("pass@1 (%)")
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.04), ncol=2, frameon=False, borderaxespad=0)
    fig.text(0.08, 0.065, "Exploratory single-run comparison. No run-to-run SD or confidence intervals are available.\nChanges are descriptive percentage-point differences, with no statistical-significance claim.", fontsize=10, color=GRAY, linespacing=1.6)
    format_axis(ax)
    save(fig, "3b_before_after")


def main():
    rows = load_results()
    (ROOT / "figures").mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10.5, "text.color": INK,
                         "axes.labelcolor": INK, "svg.fonttype": "none", "svg.hashsalt": "qwen25-companion"})
    plot_1p5b(rows)
    plot_3b(rows)
    outputs = [f"figures/{stem}.{ext}" for stem in ("1p5b_data_scale", "3b_before_after") for ext in ("png", "svg")]
    inputs = ["results/paper_results.csv", "scripts/plot_results.py", "scripts/check_results.py",
              "evidence/paper_table_2.csv", "evidence/paper_table_3.csv"]
    manifest = {
        "artifact_origin": "POST_HOC", "scope": "Rendering manuscript summary data only",
        "environment": {"python": platform.python_version(), "matplotlib": matplotlib.__version__, "os": platform.system()},
        "inputs_sha256": {p: sha256(ROOT / p) for p in inputs},
        "outputs_sha256": {p: sha256(ROOT / p) for p in outputs},
    }
    (ROOT / "figures/figure_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("Rendered two charts as PNG and SVG; wrote figure_manifest.json. No model evaluation performed.")


if __name__ == "__main__":
    main()
