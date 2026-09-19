"""
Generate the synthetic CRM + product-telemetry dataset.

Two systems that never talk to each other in real life:
  - CRM  : who bought, how much, when they renew
  - Usage: what they actually do with the product, daily

The pipeline's job is to join them. This script fabricates both sides with a
fixed seed so results are reproducible.

Run:  python src/generate_data.py
Out:  data/attribution.db
"""
import os
import random
import sqlite3
from datetime import date, timedelta

RANDOM_SEED = 7
DB_PATH = os.path.join("data", "attribution.db")
END_DATE = date(2026, 8, 31)
DAYS = 60

PLANS = {
    "Starter":    dict(entitlement=50_000,    seats=(5, 25),   arr=(12_000, 30_000)),
    "Growth":     dict(entitlement=250_000,   seats=(25, 90),  arr=(45_000, 120_000)),
    "Enterprise": dict(entitlement=1_000_000, seats=(90, 400), arr=(150_000, 480_000)),
}

INDUSTRIES = ["Fintech", "Healthcare", "Logistics", "Retail", "Media", "Manufacturing"]
REGIONS = ["North America", "EMEA", "APAC"]
OWNERS = ["A. Rao", "M. Chen", "S. Okafor", "J. Lindqvist", "P. Mehta"]

# 80 accounts; 35 are closed_won customers. Among those 35 we plant a mix of
# health profiles so the downstream thresholds have something to find.
N_ACCOUNTS = 80
N_WON = 35
PROFILE_MIX = (
    ["underuse"] * 7      # bought big, barely using it
    + ["declining"] * 5   # used to be healthy, falling off a cliff
    + ["upsell"] * 9      # running at or over entitlement
    + ["healthy"] * 14    # steady, comfortably inside plan
)

# profile -> (utilisation of entitlement in last 30d, growth vs prior 30d)
PROFILE_SHAPE = {
    "underuse":  dict(util=(0.10, 0.33), growth=(-0.10, 0.10)),
    "declining": dict(util=(0.45, 0.65), growth=(-0.55, -0.32)),
    "upsell":    dict(util=(0.88, 1.18), growth=(0.05, 0.35)),
    "healthy":   dict(util=(0.48, 0.78), growth=(-0.12, 0.18)),
    "trial":     dict(util=(0.05, 0.40), growth=(-0.30, 0.30)),
}


def daily_series(rng, entitlement, util, growth, days=DAYS):
    """Build a daily api_calls series whose last 30 days hit `util` of the
    monthly entitlement and whose prior 30 days imply `growth`."""
    recent_total = entitlement * util
    prior_total = recent_total / (1 + growth) if growth > -0.95 else recent_total * 2
    series = []
    for total in (prior_total, recent_total):          # prior 30d, then recent 30d
        base = total / 30
        noise = [rng.uniform(0.62, 1.38) for _ in range(30)]
        scale = 30 * base / sum(noise)
        series += [max(0, int(round(n * scale))) for n in noise]
    return series


def build():
    rng = random.Random(RANDOM_SEED)
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(os.path.join("sql", "01_schema.sql")) as fh:
        conn.executescript(fh.read())

    won_ids = set(rng.sample(range(1, N_ACCOUNTS + 1), N_WON))
    profiles = PROFILE_MIX[:]
    rng.shuffle(profiles)
    profile_by_account = {}

    accounts, deals, logs = [], [], []
    log_id = 0

    for account_id in range(1, N_ACCOUNTS + 1):
        tier = rng.choices(list(PLANS), weights=[0.30, 0.45, 0.25])[0]
        plan = PLANS[tier]
        entitlement = plan["entitlement"]
        seats = rng.randint(*plan["seats"])
        accounts.append((
            account_id,
            f"Account {account_id:03d}",
            rng.choice(INDUSTRIES),
            rng.choice(REGIONS),
            tier,
            entitlement,
            seats,
        ))

        if account_id in won_ids:
            profile = profiles.pop()
            close = END_DATE - timedelta(days=rng.randint(90, 400))
            deals.append((
                account_id, account_id, "closed_won",
                round(rng.uniform(*plan["arr"]), 0),
                close.isoformat(), rng.choice(OWNERS),
                (close + timedelta(days=365)).isoformat(),
            ))
        else:
            profile = "trial"
            stage = rng.choices(
                ["closed_lost", "negotiation", "discovery"], weights=[0.45, 0.25, 0.30]
            )[0]
            close_date = (END_DATE - timedelta(days=rng.randint(20, 300))).isoformat() \
                if stage == "closed_lost" else None
            deals.append((
                account_id, account_id, stage, 0.0, close_date, rng.choice(OWNERS), None
            ))

        profile_by_account[account_id] = profile
        shape = PROFILE_SHAPE[profile]
        calls = daily_series(rng, entitlement,
                             rng.uniform(*shape["util"]), rng.uniform(*shape["growth"]))

        for offset, call_count in enumerate(calls):
            log_date = END_DATE - timedelta(days=DAYS - 1 - offset)
            log_id += 1
            logs.append((
                log_id, account_id, log_date.isoformat(), call_count,
                max(1, int(seats * rng.uniform(0.15, 0.85))),
                int(call_count * rng.uniform(0.0, 0.03)),
            ))

    conn.executemany("INSERT INTO accounts VALUES (?,?,?,?,?,?,?)", accounts)
    conn.executemany("INSERT INTO deals VALUES (?,?,?,?,?,?,?)", deals)
    conn.executemany("INSERT INTO usage_logs VALUES (?,?,?,?,?,?)", logs)
    conn.commit()
    conn.close()

    print(f"Wrote {len(accounts)} accounts, {len(deals)} deals, {len(logs):,} usage rows -> {DB_PATH}")


if __name__ == "__main__":
    build()
