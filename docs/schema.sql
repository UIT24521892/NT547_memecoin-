-- Schema dữ liệu đồ án (DuckDB). Thiết kế 2026-11-12 [claude], sinh viên duyệt cùng DATA_CARD 2026-11-12.
-- Dựa trên AGENTS.md Mục 6, thêm cột truy nguyên (nguồn, ngày thu, file raw) và bảng mẫu/cutoff.
-- Quy ước:
--   * Thời gian là TIMESTAMP UTC. Ngày (DATE) là ngày UTC.
--   * Địa chỉ EVM lưu chữ thường; địa chỉ Solana GIỮ NGUYÊN hoa thường (DATASET_NOTES Mục 3).
--   * Lượng token lưu dạng chuỗi số nguyên gốc (raw, chưa chia decimals) + decimals,
--     để không mất chính xác; cột *_ui là số đã chia, chỉ để đọc.
--   * Mọi bảng dữ liệu thu được có `source`, `collected_at`, `raw_ref` (đường dẫn file trong data/raw/).
--   * data/raw/ là bất biến; các bảng này được tạo lại hoàn toàn bằng script.

CREATE TABLE IF NOT EXISTS tokens (
    chain           VARCHAR   NOT NULL,          -- ethereum | base | solana
    token_address   VARCHAR   NOT NULL,          -- EVM: contract; Solana: mint
    name            VARCHAR,
    symbol          VARCHAR,
    decimals        INTEGER,
    creator         VARCHAR,                     -- ví tạo contract / mint; NULL nếu chưa xác định
    created_at      TIMESTAMP,
    discovery       VARCHAR   NOT NULL,          -- factory_log | pumpfun_migration | reference_list | ...
    source          VARCHAR   NOT NULL,
    collected_at    TIMESTAMP NOT NULL,
    raw_ref         VARCHAR,
    PRIMARY KEY (chain, token_address)
);

CREATE TABLE IF NOT EXISTS pools (
    chain           VARCHAR   NOT NULL,
    pool_address    VARCHAR   NOT NULL,          -- EVM: pair/pool; Solana: pool account
    token_address   VARCHAR   NOT NULL,
    quote_token     VARCHAR   NOT NULL,          -- WETH, WSOL, USDC...
    dex             VARCHAR   NOT NULL,          -- uniswap_v2 | uniswap_v3 | aerodrome | raydium | pumpswap ...
    version         VARCHAR,                     -- v2 | v3 | v4 | cpmm ...; LPI x*y=k chỉ đúng với kiểu v2
    created_at      TIMESTAMP,
    created_tx      VARCHAR,
    source          VARCHAR   NOT NULL,
    collected_at    TIMESTAMP NOT NULL,
    raw_ref         VARCHAR,
    PRIMARY KEY (chain, pool_address)
);

CREATE TABLE IF NOT EXISTS ohlcv (
    chain           VARCHAR   NOT NULL,
    pool_address    VARCHAR   NOT NULL,
    ts              TIMESTAMP NOT NULL,          -- thời điểm MỞ nến (UTC)
    timeframe       VARCHAR   NOT NULL,          -- day | hour
    open            DOUBLE,
    high            DOUBLE,
    low             DOUBLE,
    close           DOUBLE,
    volume_usd      DOUBLE,                      -- NULL = thiếu nến, KHÁC volume 0
    currency        VARCHAR   NOT NULL DEFAULT 'usd',
    source          VARCHAR   NOT NULL,
    collected_at    TIMESTAMP NOT NULL,
    raw_ref         VARCHAR,
    PRIMARY KEY (chain, pool_address, timeframe, ts)
);

CREATE TABLE IF NOT EXISTS swaps (
    chain           VARCHAR   NOT NULL,
    pool_address    VARCHAR   NOT NULL,
    tx_hash         VARCHAR   NOT NULL,          -- EVM tx hash; Solana signature
    event_index     INTEGER   NOT NULL,          -- EVM log index; Solana thứ tự swap trong tx
    block_number    BIGINT,                      -- EVM block; Solana slot
    block_time      TIMESTAMP NOT NULL,
    trader          VARCHAR,                     -- NULL nếu không quy được (ghi lý do ở trader_method)
    trader_method   VARCHAR   NOT NULL,          -- evm_tx_from | sol_balance_diff | sol_raydium_decode | unclear
    side            VARCHAR   NOT NULL,          -- buy | sell (theo token meme)
    amount_token_raw VARCHAR  NOT NULL,
    amount_quote_raw VARCHAR  NOT NULL,
    amount_token_ui DOUBLE,
    amount_quote_ui DOUBLE,
    amount_usd      DOUBLE,                      -- NULL nếu chưa quy đổi được
    usd_method      VARCHAR,                     -- vd: quote_usd_daily_close; ghi rõ vì ảnh hưởng zero-risk (USD)
    execution_ok    BOOLEAN   NOT NULL,
    source          VARCHAR   NOT NULL,
    collected_at    TIMESTAMP NOT NULL,
    raw_ref         VARCHAR,
    PRIMARY KEY (chain, tx_hash, event_index)
);

CREATE TABLE IF NOT EXISTS liquidity_events (
    chain           VARCHAR   NOT NULL,
    pool_address    VARCHAR   NOT NULL,
    tx_hash         VARCHAR   NOT NULL,
    event_index     INTEGER   NOT NULL,
    block_time      TIMESTAMP NOT NULL,
    type            VARCHAR   NOT NULL,          -- mint | burn | sync
    reserve0_raw    VARCHAR,
    reserve1_raw    VARCHAR,
    actor           VARCHAR,
    source          VARCHAR   NOT NULL,
    collected_at    TIMESTAMP NOT NULL,
    raw_ref         VARCHAR,
    PRIMARY KEY (chain, tx_hash, event_index)
);

CREATE TABLE IF NOT EXISTS transfers (
    chain           VARCHAR   NOT NULL,
    token_address   VARCHAR   NOT NULL,
    tx_hash         VARCHAR   NOT NULL,
    event_index     INTEGER   NOT NULL,
    block_time      TIMESTAMP NOT NULL,
    from_address    VARCHAR,                     -- "from"/"to" là từ khoá SQL nên đổi tên
    to_address      VARCHAR,
    amount_raw      VARCHAR   NOT NULL,
    source          VARCHAR   NOT NULL,
    collected_at    TIMESTAMP NOT NULL,
    raw_ref         VARCHAR,
    PRIMARY KEY (chain, tx_hash, event_index)
);

CREATE TABLE IF NOT EXISTS holder_snapshots (
    chain           VARCHAR   NOT NULL,
    token_address   VARCHAR   NOT NULL,
    snapshot_time   TIMESTAMP NOT NULL,          -- = cutoff; dựng lại từ transfers <= snapshot_time
    address         VARCHAR   NOT NULL,
    balance_raw     VARCHAR   NOT NULL,
    is_pool         BOOLEAN   NOT NULL DEFAULT FALSE,
    is_burn         BOOLEAN   NOT NULL DEFAULT FALSE,
    is_creator      BOOLEAN   NOT NULL DEFAULT FALSE,
    is_known_cex    BOOLEAN   NOT NULL DEFAULT FALSE,
    complete        BOOLEAN   NOT NULL,          -- FALSE nếu transfers trước snapshot chưa đầy đủ (Solana)
    PRIMARY KEY (chain, token_address, snapshot_time, address)
);

CREATE TABLE IF NOT EXISTS creator_history (
    chain           VARCHAR   NOT NULL,
    creator         VARCHAR   NOT NULL,
    token_address   VARCHAR   NOT NULL,
    deployed_at     TIMESTAMP NOT NULL,
    outcome         VARCHAR,                     -- chỉ được dùng khi outcome xảy ra <= cutoff của token đang xét
    outcome_time    TIMESTAMP,
    PRIMARY KEY (chain, creator, token_address)
);

-- Mẫu nghiên cứu: mỗi token đúng 1 cutoff (PLAN Mục 5.3)
CREATE TABLE IF NOT EXISTS samples (
    chain           VARCHAR   NOT NULL,
    token_address   VARCHAR   NOT NULL,
    pool_address    VARCHAR   NOT NULL,          -- pool chính: thanh khoản lớn nhất tại cutoff
    sample_group    VARCHAR   NOT NULL,          -- A | B | C (D gán sau từ nhãn rule)
    group_rule      VARCHAR   NOT NULL,          -- lý do xếp nhóm; nhóm A chỉ dùng dữ liệu <= cutoff
    cutoff          DATE      NOT NULL,
    split_set       VARCHAR   NOT NULL,          -- train | validation | test | excluded_gap | excluded_range
    swaps_partial   BOOLEAN   NOT NULL DEFAULT FALSE,
    PRIMARY KEY (chain, token_address)
);

CREATE TABLE IF NOT EXISTS labels (
    chain           VARCHAR   NOT NULL,
    token_address   VARCHAR   NOT NULL,
    event_type      VARCHAR   NOT NULL,          -- wash_trading | lpi | rug_pull | pump_and_dump | severe_crash | manual_*
    event_time      TIMESTAMP NOT NULL,
    source          VARCHAR   NOT NULL,          -- rule | manual | reference_rule (artifact paper)
    rule_version    VARCHAR,                     -- hash/phiên bản configs/thresholds.yaml khi source = rule
    annotator       VARCHAR,                     -- người gán khi source = manual; KHÔNG ghi tên thật lên repo công khai
    evidence        VARCHAR,                     -- tx hash / link explorer
    note            VARCHAR
);
