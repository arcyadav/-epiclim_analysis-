"""Impute missing climate values in the cleaned EpiClim dataset.

Strategy:
  - Temp:  linear regression on Latitude + Longitude (location explains some
           variance in temperature; fit on rows with observed Temp).
  - LAI:   linear regression on Latitude + Longitude + Temp (Temp is filled
           first so it can be used as a predictor here).
  - preci: median fill (missingness is small and it barely correlates with
           anything else).

A boolean `<column>_imputed` flag is added for each imputed column so
downstream analysis/modeling can filter or weight imputed rows differently.

Input:  data/Final_data_cleaned.csv
Output: data/Final_data_imputed.csv
"""
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

IN_PATH = "data/Final_data_cleaned.csv"
OUT_PATH = "data/Final_data_imputed.csv"


def main():
    df = pd.read_csv(IN_PATH)
    print("Missing before:")
    print(df[["Temp", "LAI", "preci"]].isna().sum())

    # --- flags (captured before any filling happens) ---
    df["Temp_imputed"] = df["Temp"].isna()
    df["LAI_imputed"] = df["LAI"].isna()
    df["preci_imputed"] = df["preci"].isna()

    # --- 1. Temp: regression on Latitude, Longitude ---
    temp_train = df.dropna(subset=["Temp"])
    X_temp = temp_train[["Latitude", "Longitude"]]
    y_temp = temp_train["Temp"]

    temp_model = LinearRegression().fit(X_temp, y_temp)
    temp_r2 = r2_score(y_temp, temp_model.predict(X_temp))
    print(f"\nTemp ~ Latitude + Longitude | R^2 = {temp_r2:.4f}")

    temp_missing_mask = df["Temp_imputed"]
    df.loc[temp_missing_mask, "Temp"] = temp_model.predict(df.loc[temp_missing_mask, ["Latitude", "Longitude"]])

    # --- 2. LAI: regression on Latitude, Longitude, Temp (Temp now fully filled) ---
    lai_train = df.dropna(subset=["LAI"])
    X_lai = lai_train[["Latitude", "Longitude", "Temp"]]
    y_lai = lai_train["LAI"]

    lai_model = LinearRegression().fit(X_lai, y_lai)
    lai_r2 = r2_score(y_lai, lai_model.predict(X_lai))
    print(f"LAI ~ Latitude + Longitude + Temp | R^2 = {lai_r2:.4f}")

    lai_missing_mask = df["LAI_imputed"]
    df.loc[lai_missing_mask, "LAI"] = lai_model.predict(df.loc[lai_missing_mask, ["Latitude", "Longitude", "Temp"]])
    df["LAI"] = df["LAI"].clip(lower=0)  # LAI can't be negative

    # --- 3. preci: median fill ---
    preci_median = df["preci"].median()
    df["preci"] = df["preci"].fillna(preci_median)
    print(f"preci median used for fill: {preci_median:.4f}")

    print("\nMissing after:")
    print(df[["Temp", "LAI", "preci"]].isna().sum())
    print("\nImputed row counts:")
    print(df[["Temp_imputed", "LAI_imputed", "preci_imputed"]].sum())

    df.to_csv(OUT_PATH, index=False)
    print(f"\nSaved to {OUT_PATH}")


if __name__ == "__main__":
    main()
