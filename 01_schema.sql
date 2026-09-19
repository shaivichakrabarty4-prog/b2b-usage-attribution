-- =====================================================================
-- B2B Revenue & Usage Attribution Pipeline
-- Schema definition (SQLite)
-- =====================================================================

DROP TABLE IF EXISTS usage_logs;
DROP TABLE IF EXISTS deals;
DROP TABLE IF EXISTS accounts;

-- Enterprise accounts, one row each
CREATE TABLE accounts (
    account_id    INTEGER PRIMARY KEY,
    account_name  TEXT NOT NULL,
    industry      TEXT NOT NULL,
    region        TEXT NOT NULL,
    plan_tier     TEXT NOT NULL,   -- Starter / Growth / Enterprise
    monthly_api_entitlement INTEGER NOT NULL,  -- contracted API calls per month
    seats_licensed INTEGER NOT NULL
);

-- CRM deal record, one row per account
CREATE TABLE deals (
    deal_id       INTEGER PRIMARY KEY,
    account_id    INTEGER NOT NULL REFERENCES accounts(account_id),
    stage         TEXT NOT NULL,   -- closed_won / closed_lost / negotiation / discovery
    arr_usd       REAL NOT NULL,   -- annual recurring revenue if won, else 0
    close_date    TEXT,
    owner         TEXT NOT NULL,
    renewal_date  TEXT
);

-- Product telemetry, one row per account per day
CREATE TABLE usage_logs (
    log_id       INTEGER PRIMARY KEY,
    account_id   INTEGER NOT NULL REFERENCES accounts(account_id),
    log_date     TEXT NOT NULL,
    api_calls    INTEGER NOT NULL,
    active_users INTEGER NOT NULL,
    error_count  INTEGER NOT NULL
);

CREATE INDEX idx_usage_account ON usage_logs(account_id, log_date);
CREATE INDEX idx_deals_account ON deals(account_id);
CREATE INDEX idx_deals_stage   ON deals(stage);
