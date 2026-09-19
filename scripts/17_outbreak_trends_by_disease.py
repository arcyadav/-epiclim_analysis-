"""Number of outbreak records per month, faceted by disease (small
multiples, each with its own y-scale) — outbreak-count analog of
06_disease_trends.py.

Input:  data/Final_data_imputed.csv
Output: data/outbreak_trends_by_disease.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/outbreak_trends_by_disease.png"

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
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))

    by_disease = df.groupby(["date", "Disease"]).size().rename("outbreak_count").reset_index()

    fig, axes = plt.subplots(2, 4, figsize=(16, 7), facecolor=SURFACE)
    axes = axes.flatten()

    for ax, disease in zip(axes, DISEASE_ORDER):
        sub = by_disease[by_disease["Disease"] == disease]
        ax.plot(sub["date"], sub["outbreak_count"], color=DISEASE_COLORS[disease], linewidth=1.5)
        ax.set_facecolor(SURFACE)
        ax.set_title(disease, color=INK, fontsize=10)
        ax.grid(True, color=GRID, linewidth=0.7)
        ax.tick_params(colors=MUTED, labelsize=7)
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]:
            ax.spines[spine].set_color(GRID)
        ax.xaxis.set_major_locator(mdates.YearLocator(4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.set_ylabel("Outbreak count", color=MUTED, fontsize=7)

    fig.suptitle(
        "Outbreak records per month, by disease — each panel has its own y-scale",
        color=INK, fontsize=13,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
