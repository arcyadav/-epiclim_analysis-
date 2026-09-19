"""Disease-to-disease correlation: does one disease's monthly outbreak
frequency move together with another's?

Pivots monthly outbreak COUNT (number of records) into one column per
disease, then computes the Pearson correlation matrix across those 8
columns. Outbreak count is used instead of total cases since cases are
dominated by a handful of extreme records (see EDA_FINDINGS.md), which
would distort a correlation. Caveat: most diseases share the same
monsoon-driven seasonality, so some positive correlation is expected just
from riding the same annual wave, not necessarily a mechanistic link — a
real co-occurrence signal should stand out above that.

Input:  data/Final_data_imputed.csv
Output: data/disease_correlation_heatmap.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/disease_correlation_heatmap.png"

DISEASE_ORDER = [
    "Acute Diarrhoeal Disease",
    "Dengue",
    "Chikungunya",
    "Cholera",
    "Malaria",
    "Acute Encephalitis Syndrome",
    "Acute Gastroenteritis",
    "Other",
]

# Diverging pair (blue <-> neutral gray <-> red), same as 04_correlation_heatmap.py.
CMAP = LinearSegmentedColormap.from_list("blue_gray_red", ["#2a78d6", "#f0efec", "#e34948"], N=256)


def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))

    monthly_by_disease = (
        df.groupby(["date", "Disease"]).size().unstack(fill_value=0)
        .reindex(columns=DISEASE_ORDER, fill_value=0)
    )

    corr = monthly_by_disease.corr()

    fig, ax = plt.subplots(figsize=(8.5, 7), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    im = ax.imshow(corr, cmap=CMAP, vmin=-1, vmax=1, aspect="auto")

    n = len(DISEASE_ORDER)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(DISEASE_ORDER, rotation=45, ha="right", color="#0b0b0b", fontsize=9)
    ax.set_yticklabels(DISEASE_ORDER, color="#0b0b0b", fontsize=9)

    for i in range(n):
        for j in range(n):
            val = corr.iloc[i, j]
            text_color = "#ffffff" if abs(val) > 0.55 else "#0b0b0b"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8)

    ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
    ax.grid(which="minor", color="#fcfcfb", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Pearson correlation", color="#52514e", fontsize=9)
    cbar.ax.tick_params(labelcolor="#52514e")
    cbar.outline.set_visible(False)

    ax.set_title(
        "Disease-to-disease correlation (monthly outbreak count)",
        color="#0b0b0b", fontsize=13, pad=14,
    )

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")
    print("\nCorrelation matrix:\n", corr.round(3))


if __name__ == "__main__":
    main()
