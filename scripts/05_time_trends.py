"""Plot monthly time trends: total cases, cases per disease, and climate variables.

Input:  data/Final_data_imputed.csv
Output: data/time_trends.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/time_trends.png"

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


def style_axis(ax, title):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=INK, fontsize=10, loc="left")
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def main():
    df = pd.read_csv(IN_PATH)
    df["date"] = pd.to_datetime(dict(year=df["year"], month=df["mon"], day=1))

    monthly = df.groupby("date").agg(
        Cases=("Cases", "sum"),
        Temp=("Temp", "mean"),
        preci=("preci", "mean"),
        LAI=("LAI", "mean"),
    ).reset_index()

    by_disease = df.groupby(["date", "Disease"])["Cases"].sum().reset_index()

    fig, axes = plt.subplots(5, 1, figsize=(11, 15), facecolor=SURFACE, sharex=True)

    # 1. Total cases per month
    ax = axes[0]
    ax.plot(monthly["date"], monthly["Cases"], color="#2a78d6", linewidth=2)
    style_axis(ax, "Total reported cases per month (all diseases)")
    ax.set_ylabel("Cases", color=MUTED, fontsize=8)

    # 2. Cases per disease per month
    ax = axes[1]
    for disease in DISEASE_ORDER:
        sub = by_disease[by_disease["Disease"] == disease]
        ax.plot(sub["date"], sub["Cases"], color=DISEASE_COLORS[disease], linewidth=1.5, label=disease)
    style_axis(ax, "Cases per month, by disease")
    ax.set_ylabel("Cases", color=MUTED, fontsize=8)
    ax.legend(fontsize=7, frameon=False, ncol=2, loc="upper right")

    # 3. Temperature
    ax = axes[2]
    ax.plot(monthly["date"], monthly["Temp"], color="#eb6834", linewidth=2)
    style_axis(ax, "Mean temperature per month (°C)")
    ax.set_ylabel("°C", color=MUTED, fontsize=8)

    # 4. Precipitation
    ax = axes[3]
    ax.plot(monthly["date"], monthly["preci"], color="#1baf7a", linewidth=2)
    style_axis(ax, "Mean precipitation per month")
    ax.set_ylabel("preci", color=MUTED, fontsize=8)

    # 5. LAI
    ax = axes[4]
    ax.plot(monthly["date"], monthly["LAI"], color="#4a3aa7", linewidth=2)
    style_axis(ax, "Mean Leaf Area Index per month")
    ax.set_ylabel("LAI", color=MUTED, fontsize=8)
    ax.set_xlabel("Year", color=MUTED, fontsize=8)

    fig.suptitle("EpiClim — Monthly Time Trends (2009–2022)", color=INK, fontsize=13, y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
