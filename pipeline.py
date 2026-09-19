"""
Run the attribution pipeline end to end.

  1. execute the multi-stage CTE query in sql/02_attribution.sql
  2. write the per-account flag table to results/account_flags.csv
  3. write a human-readable summary to results/summary.md
  4. render the portfolio health chart used in the README

Run:  python src/pipeline.py
"""
import os
import sqlite3

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

DB_PATH = os.path.join("data", "attribution.db")
SQL_PATH = os.path.join("sql", "02_attribution.sql")
RESULTS = "results"

FLAG_COLOURS = {"churn_risk": "#b03a2e", "upsell": "#2f6f4e", "healthy": "#7b8794"}


def load(conn):
    with open(SQL_PATH) as fh:
        return pd.read_sql_query(fh.read(), conn)


def summarise(df):
    total = len(df)
    by_flag = (
        df.groupby("account_flag")
          .agg(accounts=("account_id", "count"),
               arr_usd=("arr_usd", "sum"),
               median_utilisation=("plan_utilisation", "median"))
          .reindex(["churn_risk", "upsell", "healthy"])
          .reset_index()
    )
    by_flag["pct_of_customers"] = (100 * by_flag["accounts"] / total).round(1)
    by_flag["arr_usd"] = by_flag["arr_usd"].round(0)
    return by_flag


def chart(df):
    fig, ax = plt.subplots(figsize=(8, 5), dpi=160)
    for flag, group in df.groupby("account_flag"):
        ax.scatter(group["plan_utilisation"], group["usage_trend"] * 100,
                   s=group["arr_usd"] / 700, alpha=0.8,
                   color=FLAG_COLOURS.get(flag, "#7b8794"),
                   label=flag.replace("_", " ").title(), edgecolor="white", linewidth=0.8)

    ax.axvline(0.40, color="#b03a2e", linestyle="--", linewidth=1)
    ax.axvline(0.85, color="#2f6f4e", linestyle="--", linewidth=1)
    ax.axhline(-25, color="#b03a2e", linestyle=":", linewidth=1)
    ax.text(0.405, ax.get_ylim()[1] * 0.92, "churn threshold 40%", fontsize=8, color="#b03a2e")
    ax.text(0.855, ax.get_ylim()[1] * 0.92, "upsell threshold 85%", fontsize=8, color="#2f6f4e")

    ax.set_xlabel("Plan utilisation (API calls / entitlement, last 30d)", fontsize=9)
    ax.set_ylabel("Usage trend vs prior 30 days (%)", fontsize=9)
    ax.set_title("35 closed-won accounts: usage against what they pay for\n(bubble size = ARR)",
                 fontsize=12, loc="left", pad=12)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(RESULTS, "portfolio_health.png"))
    plt.close(fig)


def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit("data/attribution.db not found - run src/generate_data.py first")
    os.makedirs(RESULTS, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    df = load(conn)
    conn.close()

    df.to_csv(os.path.join(RESULTS, "account_flags.csv"), index=False)
    by_flag = summarise(df)
    chart(df)

    churn = df[df.account_flag == "churn_risk"]
    upsell = df[df.account_flag == "upsell"]

    lines = [
        "# Attribution Pipeline - Results",
        "",
        f"Scope: **{len(df)} closed-won accounts** scored against 30 days of product telemetry.",
        "",
        "## Portfolio split",
        "",
        by_flag.to_markdown(index=False),
        "",
        f"- ARR sitting in churn-risk accounts: **${churn.arr_usd.sum():,.0f}**",
        f"- ARR in accounts at or above entitlement (upsell): **${upsell.arr_usd.sum():,.0f}**",
        "",
        "## Churn-risk accounts",
        "",
        churn[["account_name", "plan_tier", "arr_usd", "plan_utilisation",
               "usage_trend", "seat_activation", "renewal_date", "flag_reason", "owner"]]
            .to_markdown(index=False),
        "",
        "## Upsell candidates",
        "",
        upsell[["account_name", "plan_tier", "arr_usd", "plan_utilisation",
                "overage_days_30d", "usage_trend", "renewal_date", "owner"]]
            .to_markdown(index=False),
        "",
    ]
    with open(os.path.join(RESULTS, "summary.md"), "w") as fh:
        fh.write("\n".join(lines))

    print(df.account_flag.value_counts().to_string())
    print(f"\nWrote {RESULTS}/account_flags.csv, {RESULTS}/summary.md, {RESULTS}/portfolio_health.png")


if __name__ == "__main__":
    main()
