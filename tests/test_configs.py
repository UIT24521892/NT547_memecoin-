"""Kiểm tra configs/ đọc được và tự nhất quán (không gọi mạng)."""
from datetime import date, timedelta
from pathlib import Path

import pytest
import yaml

CONFIGS = Path(__file__).resolve().parents[1] / "configs"


def _load(name: str) -> dict:
    return yaml.safe_load((CONFIGS / name).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def split() -> dict:
    return _load("split.yaml")


def test_tap_tach_theo_thu_tu_thoi_gian(split: dict) -> None:
    sets = split["sets"]
    order = [sets["train"], sets["validation"], sets["test"]]
    for s in order:
        assert s["cutoff_start"] <= s["cutoff_end"]
    for a, b in zip(order, order[1:]):
        assert a["cutoff_end"] < b["cutoff_start"]


def test_nhan_tap_truoc_khong_chong_sang_tap_sau(split: dict) -> None:
    """Nhãn muộn nhất của một tập (cutoff_end + H) phải trước cutoff đầu của tập sau."""
    h = timedelta(days=split["horizon_days"])
    sets = split["sets"]
    for a, b in (("train", "validation"), ("validation", "test")):
        assert sets[a]["cutoff_end"] + h < sets[b]["cutoff_start"]


def test_khoang_dem_toi_thieu_bang_h(split: dict) -> None:
    for start, end in split["gaps"]:
        assert (end - start).days + 1 >= split["horizon_days"]


def test_du_lieu_bat_dau_du_som_cho_feature(split: dict) -> None:
    first_cutoff = split["sets"]["train"]["cutoff_start"]
    assert split["data_start"] <= first_cutoff - timedelta(days=split["feature_lookback_days"])


def test_nhom_c_khong_vao_train(split: dict) -> None:
    assert split["group_c_in_training"] is False


def test_nguong_paper_dung_gia_tri_mac_dinh() -> None:
    """Giá trị mặc định phải trùng paper (AGENTS.md Mục 2.2); đổi thì phải sửa có chủ đích."""
    t = _load("thresholds.yaml")
    assert t["wash_trading"]["screening"]["volume_change_pct_gt"] == 500
    assert t["wash_trading"]["screening"]["abs_return_pct_lt"] == 5.0
    assert t["wash_trading"]["zero_risk"]["max_imbalance_pct"] == 2
    assert t["wash_trading"]["circular_volume"]["min_share_pct"] == 99
    assert t["lpi"]["screening"]["return_pct_gt"] == 100
    assert t["lpi"]["screening"]["volume_change_pct_le"] == 20
    assert t["lpi"]["screening"]["low_volume_usd_lt"] == 1000
    assert t["lpi"]["verification"]["min_buy_ratio"] == 0.90
    assert t["lpi"]["verification"]["max_unique_traders"] == 10
    assert t["rug_pull"]["return_pct_lt"] == -99
    assert t["pump_and_dump"]["rsi_min"] == 80
    assert t["pump_and_dump"]["pump_min_return_pct"] == 50
    assert t["pump_and_dump"]["dump_min_drop_pct"] == 30


def test_ty_le_nam_trong_mien_0_1() -> None:
    t = _load("thresholds.yaml")
    ratios = [
        t["lpi"]["verification"]["min_buy_ratio"],
        t["rug_pull"]["later_volume_max_ratio"],
        t["pump_and_dump"]["post_dump_volume_max_ratio"],
        t["target"]["severe_crash_min_drop"],
        *t["target"]["sensitivity"],
    ]
    assert all(0 < r < 1 for r in ratios)


def test_chains_khong_chua_key() -> None:
    """chains.yaml chỉ được trỏ tên biến môi trường, không chứa key."""
    text = (CONFIGS / "chains.yaml").read_text(encoding="utf-8")
    assert "proapi_" not in text
    assert "api-key=" not in text.replace('"?api-key=<key>"', "")
    chains = yaml.safe_load(text)
    for name in ("ethereum", "base", "solana"):
        assert chains[name]["sample_size"] == 100
