-- =====================================================================
-- B2B Revenue & Usage Attribution Pipeline
-- Multi-stage CTE pipeline: raw telemetry -> account health -> account flags
-- =====================================================================
--
-- Stage 1  window_bounds   : anchor the analysis on the latest log date
-- Stage 2  windowed_usage  : tag every usage row as recent (0-29d) or prior (30-59d)
-- Stage 3  usage_rollup    : conditional aggregation into one row per account
-- Stage 4  account_health  : derive utilisation, trend and overage days
-- Stage 5  flagged         : apply the business thresholds
-- =====================================================================

WITH window_bounds AS (
    SELECT DATE(MAX(log_date))                AS anchor_date,
           DATE(MAX(log_date), '-29 day')     AS recent_start,
           DATE(MAX(log_date), '-59 day')     AS prior_start
    FROM usage_logs
),

windowed_usage AS (
    SELECT
        u.account_id,
        u.api_calls,
        u.active_users,
        u.error_count,
        CASE WHEN u.log_date >= w.recent_start THEN 'recent' ELSE 'prior' END AS window_label,
        -- daily entitlement, used to count days the account blew past its plan
        a.monthly_api_entitlement / 30.0 AS daily_entitlement
    FROM usage_logs u
    JOIN accounts   a ON a.account_id = u.account_id
    CROSS JOIN window_bounds w
    WHERE u.log_date >= w.prior_start
),

usage_rollup AS (
    SELECT
        account_id,
        SUM(CASE WHEN window_label = 'recent' THEN api_calls ELSE 0 END) AS calls_recent_30d,
        SUM(CASE WHEN window_label = 'prior'  THEN api_calls ELSE 0 END) AS calls_prior_30d,
        SUM(CASE WHEN window_label = 'recent' AND api_calls > daily_entitlement
                 THEN 1 ELSE 0 END)                                      AS overage_days_30d,
        MAX(CASE WHEN window_label = 'recent' THEN active_users END)     AS peak_active_users,
        ROUND(100.0 * SUM(CASE WHEN window_label = 'recent' THEN error_count ELSE 0 END)
              / NULLIF(SUM(CASE WHEN window_label = 'recent' THEN api_calls ELSE 0 END), 0), 2)
                                                                          AS error_rate_pct
    FROM windowed_usage
    GROUP BY account_id
),

account_health AS (
    SELECT
        a.account_id,
        a.account_name,
        a.industry,
        a.plan_tier,
        a.seats_licensed,
        a.monthly_api_entitlement,
        d.arr_usd,
        d.renewal_date,
        d.owner,
        r.calls_recent_30d,
        r.calls_prior_30d,
        r.overage_days_30d,
        r.error_rate_pct,
        ROUND(1.0 * r.calls_recent_30d / a.monthly_api_entitlement, 3) AS plan_utilisation,
        ROUND(1.0 * (r.calls_recent_30d - r.calls_prior_30d)
              / NULLIF(r.calls_prior_30d, 0), 3)                       AS usage_trend,
        ROUND(1.0 * r.peak_active_users / a.seats_licensed, 2)         AS seat_activation
    FROM accounts     a
    JOIN deals        d ON d.account_id = a.account_id
    JOIN usage_rollup r ON r.account_id = a.account_id
    WHERE d.stage = 'closed_won'          -- attribution only applies to paying customers
),

flagged AS (
    SELECT
        *,
        CASE
            WHEN plan_utilisation < 0.40                           THEN 'churn_risk'
            WHEN usage_trend <= -0.25 AND plan_utilisation < 0.80  THEN 'churn_risk'
            WHEN plan_utilisation >= 0.85 OR overage_days_30d >= 5 THEN 'upsell'
            ELSE 'healthy'
        END AS account_flag,
        CASE
            WHEN plan_utilisation < 0.40                           THEN 'Low plan utilisation'
            WHEN usage_trend <= -0.25 AND plan_utilisation < 0.80  THEN 'Sharp usage decline'
            WHEN plan_utilisation >= 0.85 OR overage_days_30d >= 5 THEN 'At or above entitlement'
            ELSE 'Within expected band'
        END AS flag_reason
    FROM account_health
)

SELECT
    account_id,
    account_name,
    plan_tier,
    ROUND(arr_usd, 0)            AS arr_usd,
    renewal_date,
    calls_recent_30d,
    calls_prior_30d,
    plan_utilisation,
    usage_trend,
    overage_days_30d,
    seat_activation,
    error_rate_pct,
    account_flag,
    flag_reason,
    owner
FROM flagged
ORDER BY
    CASE account_flag WHEN 'churn_risk' THEN 1 WHEN 'upsell' THEN 2 ELSE 3 END,
    arr_usd DESC;
