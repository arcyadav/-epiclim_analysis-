"""Horizontal bar chart: total reported cases by state/UT, sorted descending.

Input:  data/Final_data_imputed.csv
Output: data/cases_by_state.png
"""
import pandas as pd
import matplotlib.pyplot as plt

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/cases_by_state.png"

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
BAR_COLOR = "#2a78d6"


def main():
    df = pd.read_csv(IN_PATH)
    by_state = df.groupby("state_ut")["Cases"].sum().sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(9, 10), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    ax.barh(by_state.index, by_state.values, color=BAR_COLOR, height=0.65)

    ax.set_xlabel("Total cases", color=MUTED, fontsize=9)
    ax.set_title("Total reported cases by state / UT (2009–2022)", color=INK, fontsize=13, loc="left", pad=14)
    ax.grid(True, axis="x", color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.tick_params(axis="y", colors=INK)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")
    print("\nTop 10 states by total cases:")
    print(by_state.sort_values(ascending=False).head(10))


if __name__ == "__main__":
    main()
