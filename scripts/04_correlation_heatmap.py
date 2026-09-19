"""Plot a correlation heatmap for the numerical columns of the cleaned dataset.

Input:  data/Final_data_cleaned.csv
Output: data/correlation_heatmap.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

IN_PATH = "data/Final_data_cleaned.csv"
OUT_PATH = "data/correlation_heatmap.png"

# Diverging pair (blue <-> neutral gray <-> red) from the project's dataviz palette.
CMAP = LinearSegmentedColormap.from_list("blue_gray_red", ["#2a78d6", "#f0efec", "#e34948"], N=256)


def main():
    df = pd.read_csv(IN_PATH)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(9, 7.5), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    im = ax.imshow(corr, cmap=CMAP, vmin=-1, vmax=1, aspect="auto")

    n = len(numeric_cols)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(numeric_cols, rotation=45, ha="right", color="#0b0b0b", fontsize=9)
    ax.set_yticklabels(numeric_cols, color="#0b0b0b", fontsize=9)

    for i in range(n):
        for j in range(n):
            val = corr.iloc[i, j]
            text_color = "#ffffff" if abs(val) > 0.55 else "#0b0b0b"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=7.5)

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

    ax.set_title("Correlation Heatmap — Numerical Features (Final_data_cleaned)", color="#0b0b0b", fontsize=12, pad=14)

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
