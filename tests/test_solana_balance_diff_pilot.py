"""Unit test cho bộ đọc swap Solana bằng chênh lệch số dư. Giao dịch ở đây là GIẢ LẬP."""
import importlib.util
from pathlib import Path
from typing import Any

SPEC = importlib.util.spec_from_file_location(
    "solana_balance_diff_pilot",
    Path(__file__).resolve().parents[1] / "scripts/solana_balance_diff_pilot.py",
)
bd = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bd)

MEME = "MemeMint1111111111111111111111111111111111"
WSOL = bd.WSOL
POOL = "PoolAuth111111111111111111111111111111111"
USER = "UserWallet11111111111111111111111111111111"
MID = "Intermediary1111111111111111111111111111111"


def bal(idx: int, mint: str, owner: str, amount: int, decimals: int = 6) -> dict[str, Any]:
    return {"accountIndex": idx, "mint": mint, "owner": owner,
            "uiTokenAmount": {"amount": str(amount), "decimals": decimals}}


def make_tx(pre: list, post: list, signer_list: list[str], err: Any = None) -> dict[str, Any]:
    keys = [{"pubkey": s, "signer": True} for s in signer_list] + [{"pubkey": "Other", "signer": False}]
    return {"transaction": {"message": {"accountKeys": keys}, "signatures": ["sig"]},
            "meta": {"err": err, "preTokenBalances": pre, "postTokenBalances": post}}


def test_mua_pool_mat_meme_nhan_wsol() -> None:
    tx = make_tx(
        pre=[bal(1, MEME, POOL, 1_000_000_000), bal(2, WSOL, POOL, 50_000, 9), bal(3, MEME, USER, 0)],
        post=[bal(1, MEME, POOL, 999_000_000), bal(2, WSOL, POOL, 60_000, 9), bal(3, MEME, USER, 1_000_000)],
        signer_list=[USER],
    )
    r = bd.decode_balance_diff(tx, MEME, WSOL)
    assert (r["status"], r["side"], r["trader"], r["trader_status"]) == ("ok", "buy", USER, "exact_signer")
    assert r["amount_token"] == "1" and r["amount_quote_raw"] == "10000"


def test_ban_qua_vi_trung_gian_khong_lay_signer_dau() -> None:
    """Fee payer ký đầu tiên nhưng token đi ra từ ví khác (như tx 44CD… thật)."""
    payer = "FeePayer1111111111111111111111111111111111"
    tx = make_tx(
        pre=[bal(1, MEME, POOL, 1_000_000_000), bal(2, WSOL, POOL, 50_000, 9), bal(3, MEME, USER, 5_000_000)],
        post=[bal(1, MEME, POOL, 1_005_000_000), bal(2, WSOL, POOL, 40_000, 9), bal(3, MEME, USER, 0)],
        signer_list=[payer, USER],
    )
    r = bd.decode_balance_diff(tx, MEME, WSOL)
    assert (r["side"], r["trader"]) == ("sell", USER)


def test_giao_dich_loi_khong_tinh_la_swap() -> None:
    tx = make_tx(pre=[bal(1, MEME, POOL, 10)], post=[bal(1, MEME, POOL, 10)], signer_list=[USER],
                 err={"InstructionError": [0, "Custom"]})
    assert bd.decode_balance_diff(tx, MEME, WSOL)["status"] == "execution_failed"


def test_them_thanh_khoan_khong_phai_swap() -> None:
    """Pool nhận cả meme lẫn WSOL: là nạp thanh khoản, không được gán mua/bán."""
    tx = make_tx(
        pre=[bal(1, MEME, POOL, 1_000), bal(2, WSOL, POOL, 1_000, 9), bal(3, MEME, USER, 500)],
        post=[bal(1, MEME, POOL, 1_500), bal(2, WSOL, POOL, 2_000, 9), bal(3, MEME, USER, 0)],
        signer_list=[USER],
    )
    r = bd.decode_balance_diff(tx, MEME, WSOL)
    assert r["status"] == "not_simple_swap" and r["side"] is None


def test_meme_di_tiep_noi_khac_thi_khong_doan_trader() -> None:
    """Người mua chuyển tiếp meme đi một phần trong cùng giao dịch: không ví nào khớp đúng lượng."""
    tx = make_tx(
        pre=[bal(1, MEME, POOL, 1_000_000), bal(2, WSOL, POOL, 100, 9), bal(3, MEME, USER, 0), bal(4, MEME, MID, 0)],
        post=[bal(1, MEME, POOL, 900_000), bal(2, WSOL, POOL, 200, 9), bal(3, MEME, USER, 60_000), bal(4, MEME, MID, 40_000)],
        signer_list=[USER],
    )
    r = bd.decode_balance_diff(tx, MEME, WSOL)
    assert r["side"] == "buy" and r["trader"] is None and r["trader_status"] == "no_exact_match"


def test_khong_co_token_meme() -> None:
    tx = make_tx(pre=[bal(2, WSOL, POOL, 1, 9)], post=[bal(2, WSOL, POOL, 2, 9)], signer_list=[USER])
    assert bd.decode_balance_diff(tx, MEME, WSOL)["status"] == "no_token_balance"


def test_doi_don_vi_khong_qua_float() -> None:
    assert bd.ui(1_234_567_890_123_456_789, 9) == "1234567890.123456789"
    assert bd.ui(0, 6) == "0"
