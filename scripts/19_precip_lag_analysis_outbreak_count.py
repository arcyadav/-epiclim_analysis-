"""Precipitation-lag analysis using outbreak COUNT instead of case totals
(see 15_precip_lag_analysis.py for the Cases version). Outbreak count is a
steadier signal than Cases, which is dominated by a handful of extreme
records, so this checks whether the lag pattern holds up on the cleaner
metric.

For each disease, computes Pearson correlation between national mean
precipitation at month (t - lag) and that disease's outbreak count at
month t, for lag = 0..6 months, and plots correlation vs. lag per disease.

Input:  data/Final_data_imputed.csv
Output: data/precip_lag_correlation_outbreak_count.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/precip_lag_correlation_outbreak_count.png"

DISEASE_ORDER = [
    "Acute Diarrhoeal Disease",
    "Dengue",
    "Chikungunya",
    "Cholera",
    "Malaria",
]
DISEASE_COLORS = {
    "Acute Diarrhoeal Disease": "#2a78d6",
    "Dengue": "#eb6834",
    "Chikungunya": "#1baf7a",
    "Cholera": "#eda100",
    "Malaria": "#e87ba4",
}

MAX_LAG = 6
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"


def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))

    monthly_preci = df.groupby("date")["preci"].mean().sort_index()
    outbreaks_by_disease = (
        df.groupby(["date", "Disease"]).size().unstack(fill_value=0).sort_index()
    )

    fig, ax = plt.subplots(figsize=(9, 6.5), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    lags = list(range(0, MAX_LAG + 1))
    for disease in DISEASE_ORDER:
        outbreak_count = outbreaks_by_disease[disease].reindex(monthly_preci.index)
        correlations = []
        for lag in lags:
            shifted_preci = monthly_preci.shift(lag)
            valid = shifted_preci.notna() & outbreak_count.notna()
            corr = np.corrcoef(shifted_preci[valid], outbreak_count[valid])[0, 1]
            correlations.append(corr)
        ax.plot(lags, correlations, marker="o", markersize=5, linewidth=2,
                color=DISEASE_COLORS[disease], label=disease)

    ax.axhline(0, color=MUTED, linewidth=1, linestyle="--")
    ax.set_xlabel("Lag (months precipitation leads outbreak count)", color=MUTED, fontsize=9)
    ax.set_ylabel("Pearson correlation (precip[t-lag] vs. outbreak count[t])", color=MUTED, fontsize=9)
    ax.set_title(
        "Does rainfall predict outbreak frequency some months later?",
        color=INK, fontsize=13, loc="left", pad=14,
    )
    ax.set_xticks(lags)
    ax.grid(True, color=GRID, linewidth=0.7)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)
    ax.legend(fontsize=8, frameon=False, loc="best")

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
