"""District-level scatter: location (lat/long), marker size = total cases,
color = the disease responsible for the most cases in that district.

One point per district (not one per record) to avoid overplotting, since each
district repeats across many weekly records.

Input:  data/Final_data_imputed.csv
Output: data/disease_location_scatter.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/disease_location_scatter.png"

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

MIN_MARKER, MAX_MARKER = 15, 1200  # marker area (points^2) range


def main():
    df = pd.read_csv(IN_PATH)

    # District centroid (constant per district) + total cases per district.
    district_loc = df.groupby("district")[["Latitude", "Longitude"]].first()
    district_total = df.groupby("district")["Cases"].sum().rename("total_cases")

    # Dominant disease per district = disease with the most cases there.
    by_district_disease = df.groupby(["district", "Disease"])["Cases"].sum()
    dominant = by_district_disease.groupby("district").idxmax().apply(lambda t: t[1]).rename("dominant_disease")

    plot_df = district_loc.join(district_total).join(dominant).reset_index()

    # Area-proportional marker sizing (sqrt scale), not linear.
    sqrt_cases = np.sqrt(plot_df["total_cases"])
    plot_df["marker_size"] = MIN_MARKER + (sqrt_cases - sqrt_cases.min()) / (sqrt_cases.max() - sqrt_cases.min()) * (MAX_MARKER - MIN_MARKER)

    fig, ax = plt.subplots(figsize=(10, 10), facecolor=SURFACE)
    ax.set_facecolor(SURFACE)

    for disease in DISEASE_ORDER:
        sub = plot_df[plot_df["dominant_disease"] == disease]
        if sub.empty:
            continue
        ax.scatter(
            sub["Longitude"], sub["Latitude"],
            s=sub["marker_size"], color=DISEASE_COLORS[disease],
            alpha=0.75, edgecolors="white", linewidths=0.6, label=disease,
        )

    ax.set_xlabel("Longitude", color=MUTED, fontsize=9)
    ax.set_ylabel("Latitude", color=MUTED, fontsize=9)
    ax.set_title(
        "District hotspots: dominant disease (color) & total cases (marker size)",
        color=INK, fontsize=13, loc="left", pad=14,
    )
    ax.grid(True, color=GRID, linewidth=0.7)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.set_aspect("equal")

    # Categorical (identity) legend.
    disease_legend = ax.legend(
        title="Dominant disease", loc="upper left", fontsize=8, title_fontsize=9,
        frameon=False, markerscale=0.6,
    )
    ax.add_artist(disease_legend)

    # Size legend (reference bubbles for total-case magnitude).
    ref_cases = [100, 1_000, 10_000, 50_000]
    ref_sizes = [
        MIN_MARKER + (np.sqrt(c) - sqrt_cases.min()) / (sqrt_cases.max() - sqrt_cases.min()) * (MAX_MARKER - MIN_MARKER)
        for c in ref_cases
    ]
    size_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=MUTED, alpha=0.6,
               markeredgecolor="white", markersize=np.sqrt(s), label=f"{c:,}")
        for c, s in zip(ref_cases, ref_sizes)
    ]
    ax.legend(
        handles=size_handles, title="Total cases (district)", loc="lower left",
        fontsize=8, title_fontsize=9, frameon=False, labelspacing=1.3,
    )

    plt.tight_layout()
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")
    print("\nDominant-disease district counts:")
    print(plot_df["dominant_disease"].value_counts())


if __name__ == "__main__":
    main()
