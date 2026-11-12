# Data card: tập dữ liệu meme coin của đồ án NT547

> Viết 2026-11-12 [claude]. **Sinh viên duyệt 2026-11-12 ✅. Chưa thu dữ liệu nghiên cứu.** Số liệu về nguồn là số đo thử ghi trong `MEMORY.md` Mục 4; tham số mẫu và thời gian lấy từ [PLAN.md](PLAN.md) (đã duyệt 2026-11-12). Khi thu thật, cập nhật mục 8 bằng số đếm thực tế.

**Data card là gì?**
- *Như trẻ 5 tuổi:* cái nhãn dán trên hộp dữ liệu, ghi trong hộp có gì, lấy ở đâu, dùng sai thế nào.
- *Học thuật:* tài liệu mô tả nguồn gốc, phạm vi, cách thu, giới hạn và thiên lệch của một tập dữ liệu, để người khác đánh giá và tái lập.
- *Đời thường:* như nhãn hộp sữa: thành phần, nơi sản xuất, hạn dùng, ai không nên uống.

## 1. Mục đích

Đo dấu hiệu wash trading và LPI (tái lập Mongardini & Mei, USENIX Security 2026) và kiểm tra feature trước cutoff có báo trước rug pull/sụp giá trong 30 ngày sau không (RQ1–RQ4, PLAN Mục 3).

**Không dùng để:** kết luận một token hay một ví là lừa đảo; gắn ví với danh tính người thật; ra quyết định đầu tư.

## 2. Phạm vi

| Mục | Giá trị |
|---|---|
| Chuỗi | Ethereum, Base, Solana |
| Cỡ mẫu | 300 token, 100 mỗi chuỗi, mỗi token 1 pool chính |
| Nhóm mẫu | A: tăng > 100% **trước cutoff** (40/chuỗi); B: ngẫu nhiên cùng thời kỳ tạo (40); C: token lâu đời tham chiếu (20, chỉ đo false positive); D: gán từ A/B theo nhãn rule |
| Cửa sổ dữ liệu | 2026-05-26 → 2026-11-22 (UTC) |
| Cutoff | train 2026-06-09 → 07-13; validation 08-13 → 08-30; test 09-30 → 10-23 (`configs/split.yaml`) |
| Nhãn | rug pull (paper) hoặc giá đóng cửa thấp nhất giảm ≥ 80% so với cutoff, trong 30 ngày sau cutoff |

## 3. Nguồn dữ liệu

| Bảng | Ethereum | Base | Solana |
|---|---|---|---|
| `tokens`, `pools` (khám phá) | Log tạo pool của factory qua Blockscout | Log tạo pool qua dRPC | Giao dịch `Migrate` của ví migration pump.fun qua Helius |
| `ohlcv` | GeckoTerminal (ngày + giờ) | GeckoTerminal | GeckoTerminal |
| `swaps` | Log `Swap` qua Blockscout; trader = `tx.from` | Log `Swap` qua dRPC; trader = `tx.from` | Giao dịch qua Helius; trader từ chênh lệch số dư token theo chủ ví |
| `liquidity_events` | Log `Mint/Burn/Sync` | Như Ethereum | Suy từ số dư vault của pool (chưa thử) |
| `transfers`, `holder_snapshots` | Log `Transfer` | Như Ethereum | Chỉ từ giao dịch đã thu → `complete = false` |
| Nhãn tham chiếu | Artifact Zenodo của paper (DOI 10.5281/zenodo.17830943, CC-BY-4.0), chỉ để đối chiếu indicator, **không** vào temporal split | | |

Không dùng làm feature quá khứ: GoPlus, DexScreener, `holders`/authority hiện tại của GeckoTerminal (đều là snapshot **hiện tại**, rò rỉ tương lai).

## 4. Cách thu và lưu

- Chỉ đọc, dữ liệu công khai, không ví, không gửi giao dịch.
- Mọi lời gọi qua client có cache, retry (tenacity), giới hạn tốc độ (`configs/chains.yaml`). Chạy thử vài token trước khi chạy cả tập.
- Phản hồi gốc lưu nguyên vẹn dưới `data/raw/<ngày thu>/...` kèm request và thời điểm; **không sửa tay**, chỉ ghi thêm.
- Bảng trong `docs/schema.sql` được dựng lại hoàn toàn bằng script từ `data/raw/`. Mỗi dòng có `source`, `collected_at`, `raw_ref`.
- OHLCV thu **hai đợt** (quanh 16–18/11 và từ 23/11) vì GeckoTerminal free chỉ trả 180 ngày gần nhất; đợt sau ghi thêm, không ghi đè.
- `data/` không lên git (dữ liệu lớn, tái tạo được).

## 5. Quy tắc thời điểm (as-of)

- Feature của một token chỉ dùng bản ghi có thời gian ≤ cutoff; nhãn chỉ dùng (cutoff, cutoff + 30 ngày].
- Xếp nhóm A chỉ dựa trên giá ≤ cutoff.
- `creator_history.outcome` chỉ dùng khi `outcome_time` ≤ cutoff của token đang xét.
- `holder_snapshots` dựng lại tại đúng cutoff từ `transfers`, không lấy holder hiện tại.
- Kiểm tra tự động: `tests/test_no_leakage.py` (viết ở giai đoạn Features).

## 6. Thiên lệch và giới hạn đã biết

| Vấn đề | Ảnh hưởng | Cách xử lý |
|---|---|---|
| Solana chỉ lấy token tốt nghiệp pump.fun | Thiếu token từ launchpad khác; token chết trước khi tốt nghiệp không có | Ghi rõ; so sánh với tỷ lệ nền của paper |
| EVM mới phủ factory Uniswap V2 (V3/V4/Aerodrome chưa thử) | Thiếu pool kiểu khác, nhất là Base | Thử trước khi thu; loại nào không hỗ trợ thì ghi |
| 1 pool/token | Bỏ sót wash trading ở pool khác | Ghi trong báo cáo |
| Trader EVM = `tx.from` | Router, aggregator, bot làm sai người giao dịch | Như paper (`tx_from` trên Dune); ghi là địa chỉ, không phải người |
| Trader Solana suy từ số dư | Chuyển khoản trung gian, ví uỷ quyền có thể bị quy sai | Đối chiếu ≥ 20 giao dịch / ≥ 2 sàn (cổng 22/11) |
| Trần 10.000 giao dịch/token Solana | Token sôi động thiếu dữ liệu | `swaps_partial = true`, không tính tỷ lệ cần đủ dữ liệu |
| Nhãn "sụp ≥ 80%" | Lẫn giảm chung của thị trường | Báo mức giảm trung vị của chuỗi cùng kỳ; nhãn là kết cục, không phải bằng chứng thao túng |
| Volume USD do GeckoTerminal tính | Phương pháp quy đổi không công khai đầy đủ | Ghi nguồn; zero-risk tính trên USD như artifact (khác lượng token) |
| Thời kỳ 2026 khác paper (2024–03/2025) | Không so sánh trực tiếp tỷ lệ | Chỉ giải thích khác biệt, không kết luận paper đúng/sai |

## 7. Đạo đức

- Kết quả gọi là "dấu hiệu / rủi ro / nhất quán với thao túng", không gọi "lừa đảo" khi chưa có bằng chứng hành vi.
- Địa chỉ ví là dữ liệu công khai on-chain nhưng **không** tìm cách gắn với danh tính.
- Key API chỉ nằm trong `.env` (không commit).
- Dữ liệu artifact Zenodo dùng theo CC-BY-4.0, trích dẫn đầy đủ.

## 8. Thống kê thực tế (điền sau khi thu)

| Chuỗi | Token | Pool | Nến ngày | Nến giờ | Swap | Ngày thu | Ghi chú |
|---|---:|---:|---:|---:|---:|---|---|
| Ethereum | – | – | – | – | – | – | |
| Base | – | – | – | – | – | – | |
| Solana | – | – | – | – | – | – | |
