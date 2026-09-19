"""Two panels: number of records reported per year, and total cases per year.

Checks whether surveillance reporting volume/consistency changed over the
2009-2022 span (an open item in spec.md).

Input:  data/Final_data_imputed.csv
Output: data/cases_by_year.png
"""
import pandas as pd
import matplotlib.pyplot as plt

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/cases_by_year.png"

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def style(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=11, loc="left")
    ax.grid(True, axis="y", color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)


def main():
    df = pd.read_csv(IN_PATH)

    records_per_year = df.groupby("year").size()
    cases_per_year = df.groupby("year")["Cases"].sum()

    fig, axes = plt.subplots(2, 1, figsize=(11, 9), facecolor=SURFACE, sharex=True)

    axes[0].bar(records_per_year.index, records_per_year.values, color="#2a78d6", width=0.7)
    style(axes[0], "Number of outbreak records reported per year")
    axes[0].set_ylabel("Records", color=MUTED, fontsize=9)

    axes[1].bar(cases_per_year.index, cases_per_year.values, color="#eb6834", width=0.7)
    style(axes[1], "Total reported cases per year")
    axes[1].set_ylabel("Cases", color=MUTED, fontsize=9)
    axes[1].set_xlabel("Year", color=MUTED, fontsize=9)

    fig.suptitle("Reporting volume over time", color=INK, fontsize=13, y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")
    print("\nRecords per year:")
    print(records_per_year)


if __name__ == "__main__":
    main()
