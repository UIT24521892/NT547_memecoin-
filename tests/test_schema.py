"""Kiểm tra docs/schema.sql tạo được đủ bảng trong DuckDB (cơ sở dữ liệu tạm trong RAM)."""
from pathlib import Path

import duckdb

SCHEMA = Path(__file__).resolve().parents[1] / "docs" / "schema.sql"
BANG_BAT_BUOC = {
    # AGENTS.md Mục 6
    "tokens", "pools", "ohlcv", "swaps", "liquidity_events", "transfers",
    "holder_snapshots", "creator_history", "labels",
    # bổ sung của đồ án
    "samples",
}


def _tao_db() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect(":memory:")
    con.execute(SCHEMA.read_text(encoding="utf-8"))
    return con


def test_schema_tao_du_bang() -> None:
    con = _tao_db()
    bang = {r[0] for r in con.execute("SELECT table_name FROM information_schema.tables").fetchall()}
    assert BANG_BAT_BUOC <= bang


def test_khoa_chinh_chan_swap_trung() -> None:
    """Cùng (chain, tx_hash, event_index) không được ghi hai lần."""
    con = _tao_db()
    row = ("base", "0xpool", "0xtx", 0, 1, "2026-06-10 00:00:00", "0xtrader", "evm_tx_from",
           "buy", "100", "1", None, None, None, None, True, "drpc", "2026-11-12 00:00:00", None)
    sql = "INSERT INTO swaps VALUES (" + ",".join(["?"] * len(row)) + ")"
    con.execute(sql, row)
    try:
        con.execute(sql, row)
    except duckdb.ConstraintException:
        return
    raise AssertionError("swap trùng khoá vẫn được ghi")


def test_volume_thieu_khac_volume_0() -> None:
    """Nến thiếu volume lưu NULL, không bị ép thành 0."""
    con = _tao_db()
    con.execute(
        "INSERT INTO ohlcv (chain, pool_address, ts, timeframe, close, volume_usd, source, collected_at) "
        "VALUES ('ethereum', '0xp', '2026-06-10', 'day', 1.0, NULL, 'geckoterminal', '2026-11-12')"
    )
    assert con.execute("SELECT volume_usd FROM ohlcv").fetchone()[0] is None
