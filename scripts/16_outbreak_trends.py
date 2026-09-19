"""Monthly time trend of outbreak COUNT (number of records), alongside
climate variables — same structure as 05_time_trends.py but tracking how
many outbreaks were reported each month rather than total case volume.
Outbreak count is a steadier signal than Cases, since Cases can be
dominated by a handful of extreme records (see EDA_FINDINGS.md).

Input:  data/Final_data_imputed.csv
Output: data/outbreak_trends.png
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

IN_PATH = "data/Final_data_imputed.csv"
OUT_PATH = "data/outbreak_trends.png"

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
        outbreak_count=("Disease", "size"),
        Temp=("Temp", "mean"),
        preci=("preci", "mean"),
        LAI=("LAI", "mean"),
    ).reset_index()

    fig, axes = plt.subplots(4, 1, figsize=(11, 12), facecolor=SURFACE, sharex=True)

    ax = axes[0]
    ax.plot(monthly["date"], monthly["outbreak_count"], color="#1baf7a", linewidth=2)
    style_axis(ax, "Number of outbreak records reported per month (all diseases)")
    ax.set_ylabel("Outbreak count", color=MUTED, fontsize=8)

    ax = axes[1]
    ax.plot(monthly["date"], monthly["Temp"], color="#eb6834", linewidth=2)
    style_axis(ax, "Mean temperature per month (°C)")
    ax.set_ylabel("°C", color=MUTED, fontsize=8)

    ax = axes[2]
    ax.plot(monthly["date"], monthly["preci"], color="#2a78d6", linewidth=2)
    style_axis(ax, "Mean precipitation per month")
    ax.set_ylabel("preci", color=MUTED, fontsize=8)

    ax = axes[3]
    ax.plot(monthly["date"], monthly["LAI"], color="#4a3aa7", linewidth=2)
    style_axis(ax, "Mean Leaf Area Index per month")
    ax.set_ylabel("LAI", color=MUTED, fontsize=8)
    ax.set_xlabel("Year", color=MUTED, fontsize=8)

    fig.suptitle("EpiClim — Monthly Outbreak-Count Trends (2009–2022)", color=INK, fontsize=13, y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(OUT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"Saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
