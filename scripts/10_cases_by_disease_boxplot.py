"""Box plot of Cases per record, grouped by Disease, on a log y-axis.

Cases are heavily right-skewed (median ~10, but outliers like the 51,225-case
2009 Cholera record), so a log scale is required to see the distribution
shape at all; the outlier is kept visible rather than removed.

Input:  data/Final_data_imputed.csv
Output: data/cases_by_disease_boxplot.png
"""
import pandas as pd
import matplotlib.pyplot as plt

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/cases_by_disease_boxplot.png"

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
DISEASE_COLORS = {
    "Acute Diarrhoeal Disease": "#2a78d6",
    "Dengue": "#eb6834",
    "Chikungunya": "#1baf7a",
    "Cholera": "#eda100",
    "Malaria": "#e87ba4",
    "Acute Encephalitis Syndrome": "#008300",
    "Acute Gastroenteritis": "#4a3aa7",
    "Other": "#e34948",
}

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def main():
    df = pd.read_csv(IN_PATH)

    data = [df.loc[df["Disease"] == d, "Cases"].values for d in DISEASE_ORDER]

    fig, ax = plt.subplots(figsize=(11, 7), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    bp = ax.boxplot(
        data, tick_labels=DISEASE_ORDER, patch_artist=True, showfliers=True,
        widths=0.55,
        flierprops=dict(marker="o", markersize=3, markerfacecolor=MUTED, markeredgecolor="none", alpha=0.5),
        medianprops=dict(color=INK, linewidth=1.5),
        whiskerprops=dict(color=MUTED),
        capprops=dict(color=MUTED),
    )
    for patch, disease in zip(bp["boxes"], DISEASE_ORDER):
        patch.set_facecolor(DISEASE_COLORS[disease])
        patch.set_alpha(0.75)
        patch.set_edgecolor("white")

    ax.set_yscale("log")
    ax.set_ylabel("Cases per record (log scale)", color=MUTED, fontsize=9)
    ax.set_title(
        "Distribution of reported cases per record, by disease",
        color=INK, fontsize=13, loc="left", pad=14,
    )
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", color=INK)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")

    print("\nMedian cases per disease:")
    print(df.groupby("Disease")["Cases"].median().reindex(DISEASE_ORDER))


if __name__ == "__main__":
    main()
