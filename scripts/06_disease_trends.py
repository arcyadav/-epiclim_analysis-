"""Plot a cleaner per-disease monthly case trend as small multiples.

The combined overlay in 05_time_trends.py puts all 8 diseases on one shared
y-axis, which flattens every disease except Dengue's 2015 spike to near-zero.
This script instead gives each disease its own subplot with its own y-scale,
so every disease's actual pattern is visible.

Input:  data/Final_data_imputed.csv
Output: data/disease_trends.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/disease_trends.png"

# Fixed categorical order (by overall frequency), from the project's dataviz palette.
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
    "Acute Diarrhoeal Disease": "#2a78d6",  # blue
    "Dengue": "#eb6834",                    # orange
    "Chikungunya": "#1baf7a",               # aqua
    "Cholera": "#eda100",                   # yellow
    "Malaria": "#e87ba4",                   # magenta
    "Acute Encephalitis Syndrome": "#008300",  # green
    "Acute Gastroenteritis": "#4a3aa7",     # violet
    "Other": "#e34948",                     # red
}

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))

    by_disease = df.groupby(["date", "Disease"])["Cases"].sum().reset_index()

    fig, axes = plt.subplots(2, 4, figsize=(16, 7), facecolor=SURFACE)
    axes = axes.flatten()

    for ax, disease in zip(axes, DISEASE_ORDER):
        sub = by_disease[by_disease["Disease"] == disease]
        ax.plot(sub["date"], sub["Cases"], color=DISEASE_COLORS[disease], linewidth=1.5)
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
        ax.set_ylabel("Cases", color=MUTED, fontsize=7)

    fig.suptitle(
        "Cases per month, by disease — each panel has its own y-scale",
        color=INK, fontsize=13,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
