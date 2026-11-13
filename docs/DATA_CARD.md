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

### 4.1 Liệt kê ứng viên và chọn mẫu A/B (task 2, 2026-11-12)

**Tầng ngày tạo pool.** Cutoff = ngày giao dịch đầy đủ thứ 7, nên pool chỉ có thể vào một tập nếu được tạo trong [cutoff_start − 7 − 7 ngày đệm, cutoff_end − 7]: train 2026-05-26 → 07-06, validation 07-30 → 08-23, test 09-16 → 10-16 (`configs/split.yaml` mục `discovery`). Pool tạo ngoài các khoảng này có cutoff rơi vào khoảng đệm nên vốn bị loại.

**Nguồn và độ phủ ngày.**

| Chuỗi | Nguồn | Ngày quét | Ghi chú |
|---|---|---|---|
| Ethereum | Blockscout: `PairCreated` V2, `PoolCreated` V3, `Initialize` V4 (PoolManager) | Mọi ngày trong 3 tầng (98) | |
| Base | dRPC: V2, V3, Aerodrome classic, V4 (gộp một bộ lọc) | **20 ngày chọn ngẫu nhiên** (train 9 / val 5 / test 6, seed trong `split.yaml`) | Xác suất chọn ngày khác nhau giữa tầng: cột `day_sampled_fraction` |
| Solana | Helius: `Migrate`/`MigrateV2` của pump.fun, xác nhận CPI `CreatePool` | Mọi ngày (98) | Chỉ token tốt nghiệp pump.fun |

Pool V4 dùng PoolId (32 byte) làm `pool_address`; GeckoTerminal tra được bằng id này. ETH gốc (Currency 0x0) tính là đồng quote. Chỉ giữ pool có đúng một phía là WETH/ETH (EVM) hoặc WSOL (Solana); pool ghép USDC/USDT bị bỏ.

**Lọc token mới (EVM).** Contract token phải được tạo không sớm hơn 7 ngày trước ngày tạo pool. Ethereum: `getcontractcreation` của Blockscout; Base: `eth_getCode` tại block của mốc 7 ngày trước. Mục đích: loại token cũ có pool mới (USDC, USDT, WBTC, LST, UNI, PEPE…), quan sát được trong danh sách ứng viên. Tiêu chí chỉ dùng thông tin có lúc tạo pool. Không loại theo "xuất hiện nhiều ngày" vì meme thành công cũng được tạo thêm pool về sau (chọn theo tương lai).

**Sàng lọc tuần tự (`scripts/screen_sample.py`).** Xáo ngẫu nhiên ứng viên, mỗi token xét một pool (pool gặp trước), thu nến ngày GeckoTerminal từ ngày tạo pool. Gán cutoff và nhóm A bằng `src/memecoin/model/sampling.py` (chỉ nến ≤ cutoff; có test chống rò rỉ). B = token đủ điều kiện gặp trước, A = token đạt tiêu chí A gặp sau, quota mỗi nhóm train 18 / val 9 / test 13. Trần 5.000 pool/chuỗi. B có thể chứa token đạt tiêu chí A.

**Lọc "còn hoạt động tại cutoff" (sinh viên chọn phương án (a) ngày 2026-11-13).** Token chỉ đủ điều kiện khi volume USD trung bình trong 7 ngày lịch kết thúc ở cutoff (gồm cutoff) ≥ $1.000; ngày không có nến tính volume 0. Chỉ dùng nến ≤ cutoff (có test chống rò rỉ). Lý do: đo sơ bộ Solana 12/11 cho thấy 89% token đã giảm ≥ 80% so với đỉnh trước cutoff, nên nhãn sụp giá đo token đã chết. Ngưỡng $1.000 là đề xuất, neo theo mốc volume < $1.000 của LPI trong paper (§5.3.1, tr. 3941); độ nhạy $100 / $10.000 phải báo cáo. Token bị loại vì đã ngừng hoạt động vẫn giữ trong `screened.csv` (cột `active`, `active_volume_usd`) để báo cáo tỷ lệ sụp sớm như một phát hiện mô tả. Kết quả sàng lọc trước khi có bộ lọc: `data/interim/task2/screening/solana_before_active_filter_2026-11-13/`.

**Pilot phễu (30 pool/chuỗi, 1 ngày train, `data/interim/task2/pilot_funnel/`):** có cutoff Ethereum 3/30, Base 0/30, Solana 26/30; đạt A: Ethereum 0/3, Solana 1/23. Danh sách EVM phần lớn là pool không giao dịch; danh sách Solana đã qua ngưỡng tốt nghiệp nên đủ điều kiện nhiều hơn hẳn. Đây là khác biệt về cách định nghĩa tổng thể giữa các chuỗi, phải ghi khi so sánh chéo chuỗi.

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
| EVM đọc V2/V3/V4 (+ Aerodrome classic trên Base); Slipstream chưa hỗ trợ | Thiếu pool Slipstream | Ghi rõ |
| Base chỉ quét 20/98 ngày (ngẫu nhiên) | Mẫu vẫn ngẫu nhiên theo tầng nhưng ít ngày | Báo `day_sampled_fraction`; không suy ra tổng số pool Base |
| Chỉ pool ghép WETH/ETH/WSOL | Bỏ token chỉ ghép USDC/USDT | Ghi rõ |
| Token kích hoạt muộn (cần > 14 ngày để đủ 7 ngày giao dịch) | Có thể bị bỏ vì pool tạo ngoài tầng | Ghi rõ |
| 1 pool/token | Bỏ sót wash trading ở pool khác | Ghi trong báo cáo |
| Chỉ nhận token còn hoạt động tại cutoff (volume TB 7 ngày ≥ $1.000) | Bỏ ngoài phạm vi các cú sụp ngay sau khi ra mắt; mẫu là "token đã sống qua tuần đầu" | Báo tỷ lệ token bị loại theo chuỗi; độ nhạy $100 / $10.000 |
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

**Đợt kỹ thuật 12/11 [codex]:** đã thu 10.887 nến trên 3 pool PEPE/BRETT/HEGE và giải mã 10 swap EVM; các pool chọn từ snapshot hiện tại chỉ để kiểm tra collector, **không phải mẫu nghiên cứu**, không điền vào bảng dưới hoặc bảng `samples`. Kết quả độ phủ, replay và giới hạn: [COLLECTOR_RUNBOOK.md](COLLECTOR_RUNBOOK.md). Mẫu 300 token vẫn chờ xác minh meme/cutoff/pool theo thanh khoản tại cutoff.

| Chuỗi | Token | Pool | Nến ngày | Nến giờ | Swap | Ngày thu | Ghi chú |
|---|---:|---:|---:|---:|---:|---|---|
| Ethereum | – | – | – | – | – | – | |
| Base | – | – | – | – | – | – | |
| Solana | – | – | – | – | – | – | |
