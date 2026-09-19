# Attribution Pipeline - Results

Scope: **35 closed-won accounts** scored against 30 days of product telemetry.

## Portfolio split

| account_flag   |   accounts |          arr_usd |   median_utilisation |   pct_of_customers |
|:---------------|-----------:|-----------------:|---------------------:|-------------------:|
| churn_risk     |         12 | 860766           |               0.321  |               34.3 |
| upsell         |          9 | 933638           |               1.074  |               25.7 |
| healthy        |         14 |      1.38475e+06 |               0.6245 |               40   |

- ARR sitting in churn-risk accounts: **$860,766**
- ARR in accounts at or above entitlement (upsell): **$933,638**

## Churn-risk accounts

| account_name   | plan_tier   |   arr_usd |   plan_utilisation |   usage_trend |   seat_activation | renewal_date   | flag_reason          | owner        |
|:---------------|:------------|----------:|-------------------:|--------------:|------------------:|:---------------|:---------------------|:-------------|
| Account 008    | Enterprise  |    321023 |              0.306 |        -0.034 |              0.84 | 2026-11-05     | Low plan utilisation | M. Chen      |
| Account 041    | Growth      |     79771 |              0.327 |         0.028 |              0.84 | 2026-10-23     | Low plan utilisation | J. Lindqvist |
| Account 015    | Growth      |     74506 |              0.219 |        -0.028 |              0.84 | 2026-10-16     | Low plan utilisation | P. Mehta     |
| Account 003    | Growth      |     58722 |              0.526 |        -0.441 |              0.79 | 2026-12-02     | Sharp usage decline  | S. Okafor    |
| Account 036    | Growth      |     53309 |              0.315 |        -0.065 |              0.82 | 2027-05-24     | Low plan utilisation | J. Lindqvist |
| Account 053    | Growth      |     50645 |              0.549 |        -0.442 |              0.84 | 2026-09-02     | Sharp usage decline  | S. Okafor    |
| Account 042    | Growth      |     50433 |              0.223 |        -0.001 |              0.82 | 2026-12-01     | Low plan utilisation | M. Chen      |
| Account 069    | Growth      |     50416 |              0.254 |        -0.052 |              0.81 | 2027-04-14     | Low plan utilisation | A. Rao       |
| Account 006    | Growth      |     50034 |              0.536 |        -0.529 |              0.83 | 2027-04-09     | Sharp usage decline  | S. Okafor    |
| Account 052    | Starter     |     29207 |              0.532 |        -0.406 |              0.77 | 2026-08-23     | Sharp usage decline  | M. Chen      |
| Account 059    | Starter     |     23434 |              0.18  |         0     |              0.79 | 2027-04-12     | Low plan utilisation | M. Chen      |
| Account 037    | Starter     |     19266 |              0.602 |        -0.422 |              0.8  | 2026-09-04     | Sharp usage decline  | S. Okafor    |

## Upsell candidates

| account_name   | plan_tier   |   arr_usd |   plan_utilisation |   overage_days_30d |   usage_trend | renewal_date   | owner        |
|:---------------|:------------|----------:|-------------------:|-------------------:|--------------:|:---------------|:-------------|
| Account 007    | Enterprise  |    338212 |              1.117 |                 19 |         0.167 | 2027-02-03     | S. Okafor    |
| Account 065    | Enterprise  |    192064 |              1.103 |                 19 |         0.119 | 2026-10-31     | J. Lindqvist |
| Account 058    | Enterprise  |    159126 |              1.138 |                 21 |         0.269 | 2026-09-01     | A. Rao       |
| Account 055    | Growth      |     66396 |              1.05  |                 16 |         0.135 | 2026-12-01     | P. Mehta     |
| Account 060    | Growth      |     64196 |              0.975 |                 14 |         0.134 | 2027-02-06     | A. Rao       |
| Account 067    | Growth      |     56448 |              1.124 |                 22 |         0.283 | 2027-03-08     | S. Okafor    |
| Account 031    | Starter     |     22750 |              0.9   |                 11 |         0.065 | 2026-09-09     | S. Okafor    |
| Account 004    | Starter     |     21860 |              0.907 |                 11 |         0.153 | 2027-03-23     | M. Chen      |
| Account 072    | Starter     |     12586 |              1.074 |                 16 |         0.182 | 2026-11-28     | P. Mehta     |
