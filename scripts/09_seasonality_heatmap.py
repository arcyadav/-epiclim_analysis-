"""Disease x Month seasonality heatmap, with climate variables added as rows
so disease peak-months can be visually compared against climate peak-months.

Each row is normalized independently (disease rows: % of that disease's total
cases falling in each month; climate rows: that month's mean value, min-max
scaled 0-1 within the row) so every row's OWN seasonal peak is visible
regardless of how different the underlying scales/units are. Color encodes
each row's relative position (darkest = that row's peak month); the printed
number in each cell is the real value (% for disease, actual units for
climate), not the normalized color value.

Input:  data/Final_data_imputed.csv
Output: data/seasonality_heatmap.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/seasonality_heatmap.png"

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
CLIMATE_VARS = [
    ("Temp", "°C", "{:.1f}"),
    ("preci", "", "{:.2f}"),
    ("LAI", "", "{:.1f}"),
]
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

INK = "#0b0b0b"
MUTED = "#898781"
SURFACE = "#fcfcfb"

# Sequential single-hue ramp (blue, light -> dark) from the project's dataviz palette.
SEQ_CMAP = LinearSegmentedColormap.from_list(
    "blue_seq", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"], N=256
)


def main():
    df = pd.read_csv(IN_PATH)

    # --- Disease rows: % of each disease's total cases per month ---
    disease_month = df.groupby(["Disease", "mon"])["Cases"].sum().unstack(fill_value=0)
    disease_month = disease_month.reindex(index=DISEASE_ORDER, columns=range(1, 13), fill_value=0)
    disease_pct = disease_month.div(disease_month.sum(axis=1), axis=0) * 100

    row_labels = list(DISEASE_ORDER)
    annot_rows = [[f"{v:.1f}%" for v in disease_pct.loc[d].values] for d in DISEASE_ORDER]

    # Normalize each disease row 0-1 too (peak month = darkest), so a
    # flatter-but-still-seasonal disease isn't out-colored by a spikier one.
    color_rows_norm = []
    for d in DISEASE_ORDER:
        row = disease_pct.loc[d].values.astype(float)
        span = row.max() - row.min()
        color_rows_norm.append((row - row.min()) / span if span > 0 else np.zeros_like(row))

    # --- Climate rows: mean per month, min-max scaled 0-1 within row ---
    for col, unit, fmt in CLIMATE_VARS:
        month_mean = df.groupby("mon")[col].mean().reindex(range(1, 13))
        span = month_mean.max() - month_mean.min()
        norm = (month_mean - month_mean.min()) / span if span > 0 else month_mean * 0
        row_labels.append(f"{col}{f' ({unit})' if unit else ''}")
        color_rows_norm.append(norm.values)
        annot_rows.append([fmt.format(v) for v in month_mean.values])

    grid = np.array(color_rows_norm)

    fig, ax = plt.subplots(figsize=(11, 7), facecolor=SURFACE)
    im = ax.imshow(grid, cmap=SEQ_CMAP, vmin=0, vmax=1, aspect="auto")

    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_LABELS, color=MUTED, fontsize=9)
    ax.set_yticks(range(len(row_labels)))
    ax.set_yticklabels(row_labels, color=INK, fontsize=9)
    ax.tick_params(length=0)

    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            text_color = "#ffffff" if grid[i, j] > 0.6 else INK
            ax.text(j, i, annot_rows[i][j], ha="center", va="center", color=text_color, fontsize=7.5)

    # Separator line between the disease block and the climate block.
    ax.axhline(len(DISEASE_ORDER) - 0.5, color=SURFACE, linewidth=3)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        "Seasonality: disease share of annual cases vs. climate, by month\n"
        "(color = each row's own relative peak; numbers are real values, not the color scale)",
        color=INK, fontsize=11, loc="left", pad=14,
    )

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
