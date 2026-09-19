"""District-level location scatter, split into one panel per disease.

Each panel shows every district as a faint gray dot for geographic context,
with a colored bubble on top sized by that disease's total cases in that
district (sqrt-scaled per panel, since disease case volumes differ by orders
of magnitude — a shared scale would make rarer diseases invisible).

Input:  data/Final_data_imputed.csv
Output: data/disease_location_small_multiples.png
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/disease_location_small_multiples.png"

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
BG_DOT = "#c3c2b7"

MIN_MARKER, MAX_MARKER = 6, 500  # marker area (points^2), scaled per panel


def main():
    df = pd.read_csv(IN_PATH)

    district_loc = df.groupby("district")[["Latitude", "Longitude"]].first()
    cases_by_district_disease = (
        df.groupby(["district", "Disease"])["Cases"].sum().unstack(fill_value=0)
    )

    fig, axes = plt.subplots(2, 4, figsize=(18, 9), facecolor=SURFACE)
    axes = axes.flatten()

    for ax, disease in zip(axes, DISEASE_ORDER):
        ax.set_facecolor(SURFACE)

        # All districts, faint, for geographic context.
        ax.scatter(
            district_loc["Longitude"], district_loc["Latitude"],
            s=5, color=BG_DOT, alpha=0.5, linewidths=0,
        )

        cases = cases_by_district_disease.get(disease)
        if cases is None:
            cases = pd.Series(0, index=district_loc.index)
        sub = district_loc.join(cases.rename("cases"))
        sub = sub[sub["cases"] > 0]

        if not sub.empty:
            sqrt_cases = np.sqrt(sub["cases"])
            span = sqrt_cases.max() - sqrt_cases.min()
            if span == 0:
                sizes = np.full(len(sub), (MIN_MARKER + MAX_MARKER) / 2)
            else:
                sizes = MIN_MARKER + (sqrt_cases - sqrt_cases.min()) / span * (MAX_MARKER - MIN_MARKER)
            ax.scatter(
                sub["Longitude"], sub["Latitude"], s=sizes,
                color=DISEASE_COLORS[disease], alpha=0.75,
                edgecolors="white", linewidths=0.4,
            )

        ax.set_title(f"{disease} ({int(cases.sum()):,} cases)", color=INK, fontsize=9)
        ax.set_aspect("equal")
        ax.tick_params(colors=MUTED, labelsize=6)
        ax.grid(True, color=GRID, linewidth=0.5)
        for spine in ax.spines.values():
            spine.set_color(GRID)

    fig.suptitle(
        "District hotspots per disease (bubble size = that disease's cases; scale differs per panel)",
        color=INK, fontsize=13,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
