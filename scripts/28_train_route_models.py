"""Transmission-route outbreak models (see spec.md section 6).

Three district x month models, one per transmission route, since H1/H4
showed the routes respond to rainfall with different lags and occupy
different regions -- mixing them (26_train_outbreak_model.py) blurs both:
  - Waterborne:  Acute Diarrhoeal Disease, Cholera, Acute Gastroenteritis
  - Aedes:       Dengue, Chikungunya  (same mosquito, lag-1 rainfall in H1)
  - Anopheles:   Malaria
AES is left out: it is a syndrome with mixed causes and fits no one route.

Each model predicts whether a district reports an outbreak of any disease
in its group in a given month. Model: gradient boosting
(HistGradientBoostingClassifier); the same model without climate features
is reported alongside as the baseline, isolating what climate adds beyond
month, location and the district's own history for that group.

Reuses the grid from 25_build_district_month_grid.py for districts,
regions, months and region-month climate; builds each group's target and
history features (past months only) here, using the same district
canonicalization.

Split (by time): train 2009-05..2017, validate 2018 (hyperparameters and
threshold), test 2019 after refitting on 2009-2018, stress 2020-01..2022-06.
Each model covers only districts with a group outbreak in the training
period.

Input:  data/district_month_grid.csv, data/Final_data_imputed.csv
Output: data/route_model_metrics.csv
        data/route_model_importance.csv
        data/route_model_results.png
"""
from itertools import product

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             precision_recall_curve, roc_auc_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

GRID_PATH = "data/district_month_grid.csv"
RECORDS_PATH = "data/Final_data_imputed.csv"
METRICS_PATH = "data/route_model_metrics.csv"
IMPORTANCE_PATH = "data/route_model_importance.csv"
PLOT_PATH = "data/route_model_results.png"

GROUPS = {
    "Waterborne": ["Acute Diarrhoeal Disease", "Cholera", "Acute Gastroenteritis"],
    "Aedes": ["Dengue", "Chikungunya"],
    "Anopheles": ["Malaria"],
}
GROUP_COLORS = {"Waterborne": "#2a78d6", "Aedes": "#eb6834", "Anopheles": "#1baf7a"}

TRAIN_END_YEAR = 2017
VAL_YEAR = 2018
TEST_YEAR = 2019
RANDOM_SEED = 0

# Same as 25_build_district_month_grid.py
DISTRICT_ALIASES = {
    ("Assam", "karbianglongdiphu"): ("Assam", "karbianglong"),
    ("Andhra Pradesh", "rangareddy"): ("Telangana", "rangareddy"),
}

HISTORY = ["prev_month", "same_month_last_year", "prev_12m", "hist_rate"]
LOCATION = ["Latitude", "Longitude"]
CLIMATE = ["region_preci", "region_preci_lag1", "region_temp", "region_temp_lag1"]
CATEGORICAL = ["mon", "region"]

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


def district_keys(records):
    norm = records["district"].str.lower().str.replace(r"[^a-z]", "", regex=True)
    keys = [DISTRICT_ALIASES.get((s, n), (s, n))
            for s, n in zip(records["state_ut"], norm)]
    return [f"{s}|{n}" for s, n in keys]


def build_group_grid(base_grid, records, diseases):
    group = records[records["Disease"].isin(diseases)]
    positives = (pd.DataFrame({"district_key": district_keys(group),
                               "year": group["year"], "mon": group["mon"]})
                 .drop_duplicates().assign(target=1))
    grid = base_grid.merge(positives, on=["district_key", "year", "mon"], how="left")
    grid["target"] = grid["target"].fillna(0).astype(int)

    by_district = grid.groupby("district_key")["target"]
    grid["prev_month"] = by_district.shift(1)
    grid["same_month_last_year"] = by_district.shift(12)
    grid["prev_12m"] = by_district.transform(
        lambda s: s.shift(1).rolling(12, min_periods=1).sum())
    grid["hist_rate"] = by_district.transform(lambda s: s.shift(1).expanding().mean())

    train_districts = grid.loc[(grid["year"] <= TRAIN_END_YEAR) & (grid["target"] == 1),
                               "district_key"].unique()
    return grid[grid["district_key"].isin(train_districts)].reset_index(drop=True)


def prepare(grid, fit_years_end):
    """Fill history NaNs (first months have no past) and climate NaNs from
    the region x calendar-month climatology of years <= fit_years_end."""
    grid = grid.copy()
    grid[HISTORY] = grid[HISTORY].fillna(0)
    climatology = (grid[grid["year"] <= fit_years_end]
                   .groupby(["region", "mon"])[CLIMATE].mean().reset_index())
    fill = grid[["region", "mon"]].merge(climatology, on=["region", "mon"], how="left")
    for col in CLIMATE:
        grid[col] = grid[col].fillna(pd.Series(fill[col].to_numpy(), index=grid.index))
    return grid


def make_model(with_climate, params):
    numeric = HISTORY + LOCATION + (CLIMATE if with_climate else [])
    pre = ColumnTransformer([
        ("num", "passthrough", numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL),
    ])
    model = Pipeline([("pre", pre), ("clf", HistGradientBoostingClassifier(
        max_iter=500, early_stopping=True, random_state=RANDOM_SEED, **params))])
    return model, numeric + CATEGORICAL


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
        "n_positive": int(y.sum()),
        "positive_rate": y.mean(),
    }


def run_group(name, grid):
    tuning = prepare(grid, TRAIN_END_YEAR)
    train = tuning[tuning["year"] <= TRAIN_END_YEAR]
    val = tuning[tuning["year"] == VAL_YEAR]
    final = prepare(grid, VAL_YEAR)
    refit = final[final["year"] <= VAL_YEAR]
    splits = {
        f"test {TEST_YEAR}": final[final["year"] == TEST_YEAR],
        "stress 2020-22": final[final["year"] > TEST_YEAR],
    }
    print(f"\n=== {name}: {GROUPS[name]} -- {grid['district_key'].nunique()} districts")
    for split_name, frame in [("train", train), ("validate", val), *splits.items()]:
        print(f"  {split_name:<15} {len(frame):>6} rows, {frame['target'].sum():>5} "
              f"positive ({frame['target'].mean():.2%})")

    param_grid = [dict(zip(HGB_GRID, v)) for v in product(*HGB_GRID.values())]
    metrics_rows, curves, full_model = [], {}, None
    for with_climate in [False, True]:
        label = "with climate" if with_climate else "no climate (baseline)"
        best = None
        for params in param_grid:
            model, features = make_model(with_climate, params)
            model.fit(train[features], train["target"])
            prob = model.predict_proba(val[features])[:, 1]
            val_pr_auc = average_precision_score(val["target"], prob)
            if best is None or val_pr_auc > best[0]:
                best = (val_pr_auc, params, best_f1_threshold(val["target"], prob))
        val_pr_auc, params, threshold = best
        print(f"  {label}: best params {params}, validation PR-AUC {val_pr_auc:.4f}")

        model, features = make_model(with_climate, params)
        model.fit(refit[features], refit["target"])
        if with_climate:
            full_model = (model, features)
        for split_name, frame in splits.items():
            prob = model.predict_proba(frame[features])[:, 1]
            metrics_rows.append({
                "group": name, "model": label, "split": split_name,
                "params": str(params), "val_pr_auc": val_pr_auc, "threshold": threshold,
                **score(frame["target"].to_numpy(), prob, threshold)})
            if split_name.startswith("test"):
                curves[label] = precision_recall_curve(frame["target"], prob)

    test = splits[f"test {TEST_YEAR}"]
    model, features = full_model
    result = permutation_importance(model, test[features], test["target"],
                                    scoring="average_precision", n_repeats=10,
                                    random_state=RANDOM_SEED)
    importance = pd.DataFrame({"group": name, "feature": features,
                               "pr_auc_drop": result.importances_mean,
                               "std": result.importances_std})
    return pd.DataFrame(metrics_rows), importance, curves, test["target"].mean()


def style_axis(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, color=GRID, linewidth=0.7)
    ax.tick_params(colors=MUTED, labelsize=8)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(GRID)


def main():
    base_grid = pd.read_csv(GRID_PATH)
    base_grid = base_grid[["district_key", "region", "Latitude", "Longitude", "year",
                           "mon", *CLIMATE]].sort_values(["district_key", "year", "mon"])
    records = pd.read_csv(RECORDS_PATH)

    all_metrics, all_importance, plot_data = [], [], {}
    for name, diseases in GROUPS.items():
        grid = build_group_grid(base_grid, records, diseases)
        metrics, importance, curves, base_rate = run_group(name, grid)
        all_metrics.append(metrics)
        all_importance.append(importance)
        plot_data[name] = (metrics, importance, curves, base_rate)

    metrics = pd.concat(all_metrics, ignore_index=True)
    importance = pd.concat(all_importance, ignore_index=True)
    metrics.to_csv(METRICS_PATH, index=False)
    importance.to_csv(IMPORTANCE_PATH, index=False)

    pd.set_option("display.width", 220)
    pd.set_option("display.max_columns", None)
    print("\nEvaluation (refit on 2009-2018):\n")
    print(metrics.drop(columns=["params"]).to_string(
        index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"\nPermutation importance of the with-climate models on test {TEST_YEAR} "
          "(drop in PR-AUC):\n")
    print(importance.pivot(index="feature", columns="group", values="pr_auc_drop")
          [list(GROUPS)].to_string(float_format=lambda v: f"{v:.4f}"))

    fig, axes = plt.subplots(2, 3, figsize=(17, 10), facecolor=SURFACE,
                             gridspec_kw={"height_ratios": [1, 1.1]})
    for col, (name, (group_metrics, group_imp, curves, base_rate)) in enumerate(
            plot_data.items()):
        color = GROUP_COLORS[name]
        ax_pr, ax_imp = axes[0, col], axes[1, col]
        for label, (precision, recall, _) in curves.items():
            pr_auc = group_metrics.loc[(group_metrics["model"] == label)
                                       & group_metrics["split"].str.startswith("test"),
                                       "pr_auc"].iloc[0]
            climate = label == "with climate"
            ax_pr.plot(recall, precision, linewidth=2, color=color if climate else MUTED,
                       linestyle="-" if climate else "--",
                       label=f"{label.capitalize()} ({pr_auc:.3f})")
        ax_pr.axhline(base_rate, color=MUTED, linewidth=1, linestyle=":",
                      label=f"Random guessing ({base_rate:.3f})")
        ax_pr.set_title(f"{name}: {', '.join(GROUPS[name])}", color=INK, fontsize=11,
                        loc="left", pad=10)
        ax_pr.set_xlabel("Recall", color=MUTED, fontsize=9)
        ax_pr.set_xlim(0, 1)
        ax_pr.set_ylim(0, 1)
        style_axis(ax_pr)
        ax_pr.legend(fontsize=8, frameon=False, loc="upper right", title="PR-AUC on 2019",
                     title_fontsize=8)

        group_imp = group_imp.sort_values("pr_auc_drop")
        ax_imp.barh(group_imp["feature"], group_imp["pr_auc_drop"], xerr=group_imp["std"],
                    color=[color if f in CLIMATE else MUTED for f in group_imp["feature"]],
                    height=0.6, error_kw={"ecolor": INK, "elinewidth": 0.8, "capsize": 2})
        ax_imp.set_xlabel("Drop in 2019 PR-AUC when shuffled", color=MUTED, fontsize=9)
        ax_imp.set_title("Feature importance (climate in color)", color=INK,
                         fontsize=10, loc="left", pad=8)
        style_axis(ax_imp)
        ax_imp.grid(axis="y", visible=False)
    axes[0, 0].set_ylabel("Precision", color=MUTED, fontsize=9)

    fig.suptitle("Predicting district outbreaks by transmission route",
                 color=INK, fontsize=14, x=0.01, ha="left")
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=150, facecolor=fig.get_facecolor())
    print(f"\nSaved to {METRICS_PATH}, {IMPORTANCE_PATH} and {PLOT_PATH}")


if __name__ == "__main__":
    main()
