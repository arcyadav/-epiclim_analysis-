"""Train and evaluate the district x month outbreak model (see spec.md
section 6).

Task: predict whether a district reports any disease outbreak in a given
month (binary, ~5.5% positive).

Models (each tuned on the validation year):
  - Logistic regression, no climate:  month + district history + region/location
  - Logistic regression, full:        + region rainfall/temperature (lag 0 and 1)
  - Gradient boosting, no climate
  - Gradient boosting, full
The no-climate versions are the baselines: comparing each model with its
full version isolates what climate adds beyond seasonality, geography and
a district's own outbreak history.

Split (by time -- never random):
  train      2009-05 .. 2017-12   fit
  validate   2018                 pick hyperparameters and the yes/no threshold
  test       2019                 reported once, after refitting on 2009-2018
  stress     2020-01 .. 2022-06   COVID-era reporting collapse, reported separately

Only districts with at least one outbreak in the training period are
modeled, so the test years never decide which districts are included.
Missing region-month climate values are filled from the training-period
climatology (region x calendar month mean).

Metrics: PR-AUC (primary -- accuracy is meaningless at 5% positives),
ROC-AUC, Brier score, and precision/recall/F1 at the validation-chosen
threshold.

Input:  data/district_month_grid.csv  (from 25_build_district_month_grid.py)
Output: data/outbreak_model_metrics.csv
        data/outbreak_model_importance.csv
        data/outbreak_model_results.png
"""
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_recall_curve, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

IN_PATH = "data/district_month_grid.csv"
METRICS_PATH = "data/outbreak_model_metrics.csv"
IMPORTANCE_PATH = "data/outbreak_model_importance.csv"
PLOT_PATH = "data/outbreak_model_results.png"

TRAIN_END_YEAR = 2017
VAL_YEAR = 2018
TEST_YEAR = 2019
RANDOM_SEED = 0

HISTORY = ["prev_month_outbreak", "same_month_last_year",
           "outbreaks_prev_12m", "hist_outbreak_rate"]
LOCATION = ["Latitude", "Longitude"]
CLIMATE = ["region_preci", "region_preci_lag1", "region_temp", "region_temp_lag1"]
CATEGORICAL = ["mon", "region"]

LR_C_GRID = [0.01, 0.1, 1.0, 10.0]
HGB_GRID = {
    "learning_rate": [0.05, 0.1],
    "max_leaf_nodes": [15, 31],
    "min_samples_leaf": [50, 200],
    "l2_regularization": [0.0, 1.0],
}

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
FAMILY_COLORS = {"Logistic regression": "#2a78d6", "Gradient boosting": "#eb6834"}


def fill_climate(frame, climatology):
    frame = frame.copy()
    fill = frame[["region", "mon"]].merge(climatology, on=["region", "mon"], how="left")
    for col in CLIMATE:
        frame[col] = frame[col].fillna(pd.Series(fill[col].to_numpy(), index=frame.index))
    return frame


def prepare(grid, fit_years_end):
    """Fill history NaNs (first months have no past) and climate NaNs using
    climatology from years <= fit_years_end only."""
    grid = grid.copy()
    grid[HISTORY] = grid[HISTORY].fillna(0)
    fit_rows = grid[grid["year"] <= fit_years_end]
    climatology = fit_rows.groupby(["region", "mon"])[CLIMATE].mean().reset_index()
    return fill_climate(grid, climatology)


def make_model(kind, with_climate, params):
    numeric = HISTORY + LOCATION + (CLIMATE if with_climate else [])
    features = numeric + CATEGORICAL
    if kind == "Logistic regression":
        pre = ColumnTransformer([
            ("num", StandardScaler(), numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
        ])
        model = Pipeline([("pre", pre), ("clf", LogisticRegression(
            C=params["C"], max_iter=2000))])
    else:
        pre = ColumnTransformer([
            ("num", "passthrough", numeric),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False),
             CATEGORICAL),
        ])
        model = Pipeline([("pre", pre), ("clf", HistGradientBoostingClassifier(
            max_iter=500, early_stopping=True, random_state=RANDOM_SEED, **params))])
    return model, features


def param_grid(kind):
    if kind == "Logistic regression":
        return [{"C": c} for c in LR_C_GRID]
    keys = list(HGB_GRID)
    return [dict(zip(keys, values)) for values in product(*HGB_GRID.values())]


def best_f1_threshold(y, prob):
    precision, recall, thresholds = precision_recall_curve(y, prob)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-12, None)
    return thresholds[np.argmax(f1[:-1])]


def score(y, prob, threshold):
    pred = prob >= threshold
    tp = int((pred & (y == 1)).sum())
    precision = tp / max(pred.sum(), 1)
    recall = tp / max((y == 1).sum(), 1)
    return {
        "pr_auc": average_precision_score(y, prob),
        "roc_auc": roc_auc_score(y, prob),
        "brier": brier_score_loss(y, prob),
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / max(precision + recall, 1e-12),
        "positive_rate": y.mean(),
    }


def style_axis(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=0.7)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)


def main():
    grid = pd.read_csv(IN_PATH)
    train_districts = grid.loc[(grid["year"] <= TRAIN_END_YEAR) & (grid["outbreak"] == 1),
                               "district_key"].unique()
    grid = grid[grid["district_key"].isin(train_districts)].reset_index(drop=True)
    print(f"Districts with an outbreak in training period: {len(train_districts)}")

    tuning = prepare(grid, TRAIN_END_YEAR)
    train = tuning[tuning["year"] <= TRAIN_END_YEAR]
    val = tuning[tuning["year"] == VAL_YEAR]

    final = prepare(grid, VAL_YEAR)
    refit = final[final["year"] <= VAL_YEAR]
    splits = {
        f"test {TEST_YEAR}": final[final["year"] == TEST_YEAR],
        "stress 2020-22": final[final["year"] > TEST_YEAR],
    }
    for name, frame in [("train", train), ("validate", val), ("refit 2009-18", refit),
                        *splits.items()]:
        print(f"  {name:<15} {len(frame):>6} rows, {frame['outbreak'].sum():>5} positive "
              f"({frame['outbreak'].mean():.2%})")

    metrics_rows, test_curves, fitted = [], {}, {}
    for kind, with_climate in product(FAMILY_COLORS, [False, True]):
        label = f"{kind}, {'full' if with_climate else 'no climate'}"
        best = None
        for params in param_grid(kind):
            model, features = make_model(kind, with_climate, params)
            model.fit(train[features], train["outbreak"])
            prob = model.predict_proba(val[features])[:, 1]
            val_pr_auc = average_precision_score(val["outbreak"], prob)
            if best is None or val_pr_auc > best[0]:
                best = (val_pr_auc, params, best_f1_threshold(val["outbreak"], prob))
        val_pr_auc, params, threshold = best
        print(f"\n{label}: best params {params}, validation PR-AUC {val_pr_auc:.4f}, "
              f"threshold {threshold:.3f}")

        model, features = make_model(kind, with_climate, params)
        model.fit(refit[features], refit["outbreak"])
        fitted[label] = (model, features)
        for split_name, frame in splits.items():
            prob = model.predict_proba(frame[features])[:, 1]
            row = {"model": label, "split": split_name, "params": str(params),
                   "val_pr_auc": val_pr_auc, "threshold": threshold,
                   **score(frame["outbreak"].to_numpy(), prob, threshold)}
            metrics_rows.append(row)
            if split_name.startswith("test"):
                test_curves[label] = precision_recall_curve(frame["outbreak"], prob)

    metrics = pd.DataFrame(metrics_rows)
    metrics.to_csv(METRICS_PATH, index=False)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print("\nEvaluation (models refit on 2009-2018):\n")
    print(metrics.drop(columns=["params"]).to_string(
        index=False, float_format=lambda v: f"{v:.4f}"))

    test = splits[f"test {TEST_YEAR}"]
    importance_rows = []
    for label in ["Logistic regression, full", "Gradient boosting, full"]:
        model, features = fitted[label]
        result = permutation_importance(
            model, test[features], test["outbreak"], scoring="average_precision",
            n_repeats=5, random_state=RANDOM_SEED)
        for feature, mean, std in zip(features, result.importances_mean,
                                      result.importances_std):
            importance_rows.append({"model": label, "feature": feature,
                                    "pr_auc_drop": mean, "std": std})
    importance = pd.DataFrame(importance_rows)
    importance.to_csv(IMPORTANCE_PATH, index=False)
    print(f"\nPermutation importance on test {TEST_YEAR} (drop in PR-AUC):\n")
    print(importance.pivot(index="feature", columns="model", values="pr_auc_drop")
          .sort_values("Gradient boosting, full", ascending=False)
          .to_string(float_format=lambda v: f"{v:.4f}"))

    fig, (ax_pr, ax_imp) = plt.subplots(1, 2, figsize=(13, 5.8), facecolor=SURFACE,
                                        gridspec_kw={"width_ratios": [1, 1.1]})
    for label, (precision, recall, _) in test_curves.items():
        kind = label.split(",")[0]
        pr_auc = metrics.loc[(metrics["model"] == label)
                             & metrics["split"].str.startswith("test"), "pr_auc"].iloc[0]
        ax_pr.plot(recall, precision, color=FAMILY_COLORS[kind], linewidth=2,
                   linestyle="-" if label.endswith("full") else "--",
                   label=f"{label} (PR-AUC {pr_auc:.3f})")
    ax_pr.axhline(test["outbreak"].mean(), color=MUTED, linewidth=1, linestyle=":",
                  label=f"Random guessing ({test['outbreak'].mean():.3f})")
    ax_pr.set_xlabel("Recall (share of real outbreaks caught)", color=MUTED, fontsize=9)
    ax_pr.set_ylabel("Precision (share of alerts that were real)", color=MUTED, fontsize=9)
    ax_pr.set_title(f"Precision-recall on {TEST_YEAR} (test year)", color=INK,
                    fontsize=12, loc="left", pad=12)
    ax_pr.set_xlim(0, 1)
    ax_pr.set_ylim(0, 1)
    style_axis(ax_pr)
    ax_pr.legend(fontsize=8, frameon=False, loc="upper right")

    gb = (importance[importance["model"] == "Gradient boosting, full"]
          .sort_values("pr_auc_drop"))
    bar_colors = [FAMILY_COLORS["Gradient boosting"] if f in CLIMATE else MUTED
                  for f in gb["feature"]]
    ax_imp.barh(gb["feature"], gb["pr_auc_drop"], xerr=gb["std"], color=bar_colors,
                height=0.6, error_kw={"ecolor": INK, "elinewidth": 0.8, "capsize": 2})
    ax_imp.set_xlabel("Drop in test PR-AUC when the feature is shuffled", color=MUTED,
                      fontsize=9)
    ax_imp.set_title("What the gradient boosting model relies on (climate in orange)",
                     color=INK, fontsize=12, loc="left", pad=12)
    style_axis(ax_imp)
    ax_imp.grid(axis="y", visible=False)

    fig.suptitle("Can we predict which districts report an outbreak each month?",
                 color=INK, fontsize=14, x=0.01, ha="left")
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"\nSaved to {METRICS_PATH}, {IMPORTANCE_PATH} and {PLOT_PATH}")


if __name__ == "__main__":
    main()
