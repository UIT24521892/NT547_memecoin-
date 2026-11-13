# Kế hoạch đồ án NT547: Meme Coin Manipulation

> Viết ngày 2026-11-06 [claude]. **Sinh viên duyệt ngày 2026-11-12 ✅**, kèm 5 điểm sửa sau lần rà soát cùng ngày (đánh dấu "sửa 12/11" trong file; lý do ở `docs/LOG.md`). Đã chốt: 3 chuỗi, hạn nộp, báo cáo tiếng Anh, H = 30, ngưỡng sụp giá ≥ 80%, 300 token. Các con số ghi "đề xuất" là do mình chọn, không lấy từ paper; khi có dữ liệu sẽ xem lại trên train/validation, nhưng không được chỉnh theo kết quả tập test.
>
> **File này là nguồn chính cho phạm vi, mẫu, T0–T3, H, target, cổng quyết định và lịch.** Muốn đổi các mục đó phải được sinh viên đồng ý và ghi vào `docs/LOG.md`.

## 1. Tóm tắt

- **Làm gì:** thu khoảng 300 token trên Base, Ethereum và Solana; tái lập wash trading (bắt buộc) và LPI; xây risk score 0–100 có giải thích; đánh giá theo thời gian; kiểm tra thủ công.
- **Hạn:** 2026-12-27, còn 45 ngày tính từ 12/11, trong khi kế hoạch gốc cần 10 tuần. Nhóm **2 người** (sinh viên đính chính 2026-11-12; bản nháp ghi 3) nên phải làm song song và ít dư địa hơn dự tính.
- **Rủi ro lớn nhất:**
  1. Solana tốn công thu dữ liệu nhất (Mục 7, cổng 22/11).
  2. Có thể không lấy được danh sách token đã chết; mẫu chỉ gồm token còn sống sẽ làm sai kết quả (Mục 4.2).
  3. Số ca dương có thể quá ít để train model (Mục 7, cổng 29/11).

## 2. Phạm vi

| Trong phạm vi | Ngoài phạm vi |
|---|---|
| Base, Ethereum, Solana (sinh viên chốt 2026-11-06) | BSC: chưa thấy đường miễn phí đọc lịch sử swap |
| 5 nhóm feature của đề bài | Giao dịch, gửi tx, tương tác contract |
| IND-1 wash trading; IND-2 LPI | Gắn địa chỉ ví với danh tính ngoài đời |
| Hướng mở rộng (c): so sánh chéo chuỗi, đề xuất vì đã thu 3 chuỗi | Hướng (a), (b): chỉ làm nếu còn thời gian |

AGENTS.md Mục 5 khuyến nghị thêm Solana khi còn thời gian. Nhóm chọn đưa Solana vào ngay từ đầu nên kế hoạch tách phần việc Solana và có mức dự phòng ở Mục 7.

## 3. Câu hỏi nghiên cứu

| RQ | Câu hỏi | Dữ liệu cần | Ghi chú |
|---|---|---|---|
| RQ1 | Tỷ lệ wash/LPI trong token tăng mạnh có giống paper không? | OHLCV, swap | Thời kỳ khác paper (2026 so với 2024–2025), mẫu nhỏ hơn: so sánh để giải thích khác biệt, không để kết luận paper đúng hay sai |
| RQ2 | Feature trước cutoff có dự báo rug/sụp giá trong H ngày sau không? | Toàn bộ | Đo được lead time, điều paper không báo (PAPER_NOTES PB31) |
| RQ3 | Nhóm feature nào quan trọng nhất? | Toàn bộ | Bỏ lần lượt từng nhóm (ablation) |
| RQ4 | Baseline "giá tăng > 100% = nguy hiểm" sai nhiều đến đâu? | OHLCV, nhóm C | Báo cáo riêng nhóm tăng mạnh nhưng hợp lệ |

## 4. Mẫu dữ liệu

### 4.1 Cỡ mẫu (đề xuất)

300 token, 100 token mỗi chuỗi, mỗi token lấy 1 pool chính (thanh khoản lớn nhất tại cutoff).

| Nhóm | Mô tả | Số token/chuỗi |
|---|---|---:|
| A | Tăng giá > 100% **trước cutoff**: giá đóng cửa tại cutoff ≥ 2 lần giá đóng cửa của ngày giao dịch đầy đủ đầu tiên (đề xuất, sửa 12/11) | 40 |
| B | Chọn ngẫu nhiên cùng thời kỳ tạo | 40 |
| C | Token "hợp lệ" tham chiếu (vốn hoá/lịch sử dài, niêm yết lớn) | 20 |
| D | Không thu riêng: gán từ A/B khi rule phát hiện rug/pump & dump | n/a |

**Quy tắc nhóm (sửa 12/11):**
- Việc xếp token vào nhóm A chỉ dùng dữ liệu ≤ cutoff. Chọn theo mức tăng sau cutoff là chọn mẫu bằng thông tin tương lai (data leakage), không được làm.
- **Sửa 13/11 (sinh viên chọn phương án (a)):** chỉ nhận token **còn hoạt động tại cutoff**: volume trung bình 7 ngày lịch tới cutoff ≥ $1.000 (đề xuất; ngày không có nến tính 0; chỉ dùng dữ liệu ≤ cutoff). Áp cho cả 3 chuỗi và cả A lẫn B. Lý do: Solana 12/11 có 89% token đã sụp ≥ 80% trước cutoff, nhãn đo token đã chết. Token bị loại vẫn được đếm để báo cáo tỷ lệ sụp sớm. Độ nhạy $100 / $10.000. Tham số `configs/split.yaml` mục `sampling`.
- Nhóm C **không** dùng để train và không tính vào chỉ số chính (PR-AUC, precision@k tính trên A + B). C chỉ được chấm điểm để đo false positive cho RQ4 và báo cáo riêng. Lý do: token lâu đời bị tách ra chỉ nhờ tuổi và thanh khoản, làm chỉ số đẹp giả.

Token có nhãn trong dataset paper (2024 đến 03/2025) nằm ngoài cửa sổ OHLCV miễn phí. Chúng chỉ dùng để đối chiếu indicator, **không** đưa vào temporal split (DATASET_NOTES Mục 3).

Hạn chế đã biết: chỉ lấy 1 pool có thể bỏ sót wash trading ở pool khác; cần ghi rõ trong báo cáo.

**Cách chọn A/B (sinh viên duyệt 12/11, task 2):** sàng lọc tuần tự. Xáo ngẫu nhiên ứng viên (seed cố định), thu nến ngày từng pool. B = token đủ điều kiện (có cutoff trong một tập) gặp trước theo thứ tự ngẫu nhiên. A = token đạt tiêu chí A gặp sau đó. Mỗi nhóm 40/chuỗi chia theo **số ngày cutoff** của tập: train 18, validation 9, test 13. **Trần sàng lọc 5.000 pool/chuỗi** (sửa 13/11, sinh viên đồng ý: riêng Ethereum **10.000** vì chỉ ~0,7% token đủ điều kiện sau 925 pool; cùng thứ tự xáo nên không đổi tính ngẫu nhiên); thiếu A thì báo số thật, không nới ngưỡng ×2, không bù token khác. EVM chỉ nhận **token mới** (contract tạo ≤ 7 ngày trước pool, đề xuất) để loại USDC/WBTC/LST/meme cũ có pool mới. Tham số ở `configs/split.yaml` mục `sampling`; chi tiết `docs/DATA_CARD.md` Mục 4.1.

### 4.2 Nguồn danh sách token: có đường thu, chưa hoàn tất mẫu

Nếu chỉ lấy token còn đang giao dịch thì token đã rug sẽ vắng mặt, làm tỷ lệ ca dương thấp giả tạo (survivorship bias).

| Chuỗi | Cách dự định | Trạng thái |
|---|---|---|
| Ethereum | Log tạo pool của các factory qua Blockscout (mỗi dòng là một pool mới, kể cả pool đã chết) | **Quét toàn tầng 12/11 (task 2):** 98/98 ngày, V2 + V3 + **V4** (thêm theo quyết định sinh viên 12/11), 40.151 pool ứng viên, 442 lần gọi |
| Base | Như trên nhưng qua dRPC (Blockscout Base không còn free) | **Collector chạy thật 12/11:** dải 1.000 block có 20 log V2 + 2 log V3; dải 5.000 block có 1 log Aerodrome classic. ~100 block/lần. **Task 2 (12/11):** thêm V4; quét **20 ngày chọn ngẫu nhiên** (sinh viên chọn) thay vì toàn kỳ; một ngày có 2.700–9.000 pool, khoảng 90% là V4. Chưa có Slipstream |
| Solana | Giao dịch `Migrate`/`MigrateV2` của ví migration pump.fun `39azUYFW…jUJjg` qua Helius `getTransactionsForAddress` (lọc ngày + `status: succeeded`); giải mã theo IDL và xác nhận CPI `CreatePool` | **Collector chạy thật 12/11:** ngày 2026-06-10 có 375 tx thành công/5 trang → 358 tx có migration → **222 pool mới** sau khử trùng và xác nhận CPI. Không coi mọi tx thành công/mọi migration là một token mới. Ước tính ≈ 50 credit/ngày và ≈ 7.500 credit/cửa sổ vẫn chưa đo riêng. **Quét toàn tầng 12/11 (task 2):** 98/98 ngày, 74.094 pool, 1.222 lần gọi Helius. **Chỉ phủ token tốt nghiệp pump.fun**; token ra mắt nơi khác (LetsBonk, Meteora, Raydium LaunchLab, tạo pool trực tiếp) bị thiếu, phải ghi là hạn chế |

Nếu không có cách nào cho một chuỗi: dùng danh sách hiện tại và báo cáo rõ hạn chế; không được tính kết quả của chuỗi đó như mẫu ngẫu nhiên.

### 4.3 Khối lượng swap Solana (đề xuất)

Theo cách của paper, chỉ xác minh bằng swap ở những **ngày OHLCV đã bị gắn cờ**, cộng 7 ngày trước cutoff để tính feature. Mỗi token tối đa 10.000 giao dịch; vượt mức thì ghi `swaps_partial=true` và không tính các tỷ lệ cần đủ dữ liệu.

- **Ước tính (sửa 12/11):** 100 token × 10.000 giao dịch = 1 triệu giao dịch. Bài thử ngày 2026-11-06 đo được 10 lần gọi trong 28,42 giây (khoảng 0,35 lần/giây, có nghỉ 3 giây giữa các lần). Với tốc độ đó cần khoảng 33 ngày chạy liên tục, nên **không khả thi bằng RPC công khai**. Con số 69 giờ trước đây dựa trên 4 lần gọi/giây lý thuyết, chưa đo. Mức 1 của Solana vì vậy phụ thuộc Helius (Mục 7).
- **Với Helius (đo 12/11):** `getTransactionsForAddress` ≈ 10 credit/lần (suy ra từ dashboard, chưa đo riêng). **Collector đã gọi `full, limit=100` thành công** trên ngày 10/06, không còn chỉ thử 10. Với 100 giao dịch/lần, 1 triệu giao dịch ≈ 10.000 lần gọi ≈ 100.000 credit, khoảng 1/10 quota tháng; đây vẫn là ước tính, chưa chạy toàn tập hoặc xác minh số full tx tối đa/lần.
- **Hạn chế:** giới hạn này làm token sôi động thiếu dữ liệu nhất, cần báo cáo số token bị ảnh hưởng theo từng nhóm.

## 5. Tham số thời gian (đề xuất)

### 5.1 H = 30 ngày

H là số ngày nhìn tới trước để gán nhãn. Mình đếm thử trên OHLCV ngày của artifact paper (số token giảm ≥ 80% so với mốc 2025-01-15; chỉ gồm token đã tăng mạnh, chi tiết ở LOG.md):

| H | Base (30 token) | Ethereum (50) | Solana (267) | Nhận xét |
|---:|---:|---:|---:|---|
| 14 | 0 | 1 | 7 | Quá ít ca dương |
| **30** | **2** | **4** | **31** | Chọn: đủ ca dương, vẫn đủ chỗ chia thời gian |
| 60 | 11 | 16 | 73 | Nhiều ca, nhưng 2 khoảng đệm + phần đuôi đã dùng 180 ngày |

### 5.2 Target

Token là **dương tính** nếu trong (cutoff, cutoff + 30 ngày] có một trong hai:

- Rug pull theo tiêu chí AGENTS.md Mục 2.2.
- **Sụp giá nghiêm trọng:** giá đóng cửa thấp nhất giảm ≥ 80% so với giá tại cutoff (đề xuất; phân tích độ nhạy với 70% và 90%).

**Kiểm tra tỷ lệ ca dương trước khi dùng (sửa 12/11):** các con số ở Mục 5.1 đếm trên token đã tăng mạnh của paper tại mốc 2025-01-15, không phải trên token mới 7 ngày tuổi như mẫu của đồ án. Token meme mới có thể sụp ≥ 80% trong 30 ngày với tỷ lệ cao hơn nhiều; khi đó nhãn gần như không phân biệt được gì. Ngay khi có OHLCV đợt 1, đếm tỷ lệ ca dương trên nhóm A + B với cutoff **trước T2**, theo từng chuỗi. Nếu tỷ lệ > 50% hoặc < 5% (đề xuất) thì dừng, báo sinh viên và đề xuất đổi ngưỡng (ví dụ 90%, hoặc so với mức giảm trung vị của chuỗi). Không dùng cutoff của tập test cho việc này.

Nhãn này chỉ mô tả kết cục và **không kết luận là thao túng**, vì giá có thể giảm do toàn thị trường. Đầu năm 2025, trung vị mức giảm sâu nhất trong 30 ngày đã là −54% ở Base và −55% ở Ethereum trên nhóm token tăng mạnh. Do đó phải báo cáo thêm mức giảm trung vị của cả chuỗi trong cùng kỳ. Mỗi cảnh báo vẫn cần bằng chứng hành vi (AGENTS.md Mục 12).

### 5.3 T0–T3

**Giới hạn:** GeckoTerminal miễn phí chỉ trả 180 ngày gần nhất (lỗi 401 khi hỏi xa hơn, đo 2026-11-06). Thu lần chốt vào 2026-11-22 thì OHLCV bắt đầu từ 2026-05-26. Mỗi ngày trễ mất một ngày dữ liệu đầu cửa sổ, nên phải thu **hai đợt**: đợt 1 quanh 16–18/11, đợt 2 từ 23/11 (ghi thêm, không sửa dữ liệu cũ).

| Tập | Cutoff | Số ngày | Nhãn muộn nhất |
|---|---|---:|---|
| Feature tối thiểu | 14 ngày trước cutoff đầu tiên | | |
| Train | T0 = 2026-06-09 đến trước T1 = 2026-08-13, chỉ dùng tới 2026-07-13 | 35 | 2026-08-12 |
| Khoảng đệm | 2026-07-14 đến 2026-08-12 | 30 | |
| Validation | T1 = 2026-08-13 đến 2026-08-30 | 18 | 2026-09-29 |
| Khoảng đệm | 2026-08-31 đến 2026-09-29 | 30 | |
| Test | T2 = 2026-09-30 đến T3 = 2026-10-23 | 24 | 2026-11-22 |

**Quy tắc:**
- Mỗi token có đúng 1 cutoff, nên không token nào nằm ở hai tập.
  - Token mới: tuần đầu tiên token có ≥ 7 ngày giao dịch.
  - Token đã có từ trước T0 (chủ yếu nhóm C): gán ngẫu nhiên một cutoff trong train, validation hoặc test, với seed cố định.
- Token có cutoff rơi vào khoảng đệm hoặc ngoài T0–T3 thì loại và báo cáo số lượng.
- Mọi việc đếm thử để chỉnh ngưỡng chỉ dùng cutoff trước T2. Test chạy **một lần** vào cuối.

## 6. Nguồn dữ liệu

Nguồn kiểm tra: `MEMORY.md` Mục 4 và [API_DOC_EVIDENCE_2026-10-01.md](references/API_DOC_EVIDENCE_2026-10-01.md). Ngày trong bảng là ngày kiểm tra gần nhất. Mọi giá trị cần xem lại trước khi chạy cả tập.

**Sửa 12/11:** từ 2026-10-01 Blockscout bỏ Base khỏi gói free (key free trả HTTP 402). Base chuyển sang dRPC; Solana chuyển sang Helius. Cả hai đã thử bằng key free ngày 2026-11-12, số đo ở `MEMORY.md` Mục 4.

| Việc | Ethereum | Base | Solana |
|---|---|---|---|
| OHLCV ngày/giờ | GeckoTerminal: 180 ngày, tối đa 1.000 nến/lần, đề xuất ≤ 10 lần/phút. Collector 12/11 đã thu ngày/giờ trên 3 pool, có báo thiếu; trang ngắn vẫn phải phân tiếp | Như Ethereum | Như Ethereum |
| Danh sách pool (kể cả pool chết) | Blockscout `getLogs`, V2/V3 đã chạy thật (Mục 4.2) | dRPC `eth_getLogs`: ~100 block/lần, ~1,9 lần/giây → cả cửa sổ ≈ 65.000 lần gọi ≈ 9 giờ nếu gộp factory (**vẫn là ước tính, chưa chạy toàn kỳ**). **Task 1 xong 12/11:** collector Base gộp mặc định V2/V3/Aerodrome classic; đo 1.000 block giữ nguyên 23 log/12 ứng viên, HTTP 30 → 10, 16,325 → 5,278 giây. Chi tiết: `BASE_BATCHING.md` | Helius migration + xác nhận CPI CreatePool; Mục 4.2 |
| Lịch sử swap có địa chỉ | Blockscout `getLogs` qua `api.blockscout.com/1/api` với key free: tối đa 1.000 dòng/lần; trader qua `transaction/gettxinfo` (`proxy` trả 400 trong phép thử collector); 100.000 credit/ngày, 5 lần/giây. Đã giải mã 2 swap thật | dRPC `eth_getLogs`, có thể lọc **cùng lúc mọi pool của mẫu**; 1 ngày = 432 lần gọi ≈ 3,7 phút; khoảng 14–20 CU/lần, quota 210M CU/tháng. Đã giải mã 8 swap thật | Helius `getTransactionsForAddress`: lọc theo ngày, khớp 8/8 signature với RPC công khai trên pool HEGE; ≈ 10 credit/lần (suy ra, chưa đo riêng), quota 1M credit/tháng. RPC công khai chỉ để dự phòng |
| Creator | Blockscout (tx tạo contract) | dRPC: tx tạo contract chưa thử; dự phòng là địa chỉ gọi tạo pool | Tự suy từ giao dịch tạo mint: **chưa thử** |
| Holder tại cutoff | Dựng lại từ log `Transfer` | Như Ethereum (qua dRPC) | **Khó:** chỉ dựng được từ các giao dịch đã thu, có thể thiếu |
| Cờ contract | Mã nguồn verified; GoPlus (2026-10-01) phản ánh hiện tại nên **không** làm feature quá khứ | Như Ethereum | Authority hiện tại có cùng vấn đề; GoPlus cho Solana chưa xác minh |
| Thanh khoản | Log `Mint/Burn/Sync` với pool kiểu V2; pool V3, V4 xử lý riêng | Như Ethereum; thêm Aerodrome | Tự suy từ số dư pool: **chưa thử** |

Mọi con số dRPC và Helius ở trên đo trên vài chục lần gọi; phải đo lại khi chạy cả tập. Collector Base phải chịu được dải 100 block (chia nhỏ, lưu tiến độ để chạy tiếp sau khi dừng).

Dune không dùng: bản free không chạy query hay gọi API (2026-11-06). DexScreener chỉ cho snapshot hiện tại nên không làm feature quá khứ.

Ước tính OHLCV: 300 token × (1 lần nến ngày + khoảng 5 lần nến giờ) = 1.800 lần gọi, khoảng 3 giờ với 10 lần/phút.

### Cách đọc swap Solana (đề xuất, chưa thử)

- **Như trẻ 5 tuổi:** xem ví trước và sau giao dịch có thêm hay bớt đồng nào, để biết người đó đã mua hay bán.
- **Học thuật:** với mỗi giao dịch, so `preTokenBalances` với `postTokenBalances` theo chủ sở hữu. Token meme tăng và SOL/USDC giảm là mua, ngược lại là bán. Cách này không phụ thuộc từng sàn.
- **Đời thường:** không cần đọc hoá đơn của từng cửa hàng, chỉ cần xem ví tiền và túi hàng trước và sau khi đi chợ.

Rủi ro: ví trả phí giao dịch chưa chắc là người giao dịch; bot và aggregator có thể làm sai dấu mua/bán. Phải đối chiếu tay với explorer (cổng 22/11).

**Trạng thái (sửa 12/11):** bài thử `scripts/solana_decode_pilot.py` đi theo cách khác: đọc lệnh swap của riêng Raydium AMM (opcode 16/17), chạy trên 8 giao dịch của 1 pool. Cách đó chính xác hơn nhưng không dùng được cho sàn khác. Cách so số dư ở trên vẫn là cách chính của đồ án; bộ đọc Raydium giữ lại để đối chiếu. **Cập nhật 12/11:** đã viết `scripts/solana_balance_diff_pilot.py`; trên 8 giao dịch HEGE (Raydium) khớp 8/8 với bộ đọc Raydium về chiều, lượng HEGE, lượng WSOL và trader, kể cả ca ví trung gian. Mới 1 pool/1 sàn, chưa đạt cổng 22/11. Cổng 22/11 (≥ 2 sàn) tính trên cách so số dư.

## 7. Cổng quyết định và phương án dự phòng

| Ngày | Cổng | Đạt | Không đạt |
|---|---|---|---|
| 15/11 | Có cách lấy danh sách token, kể cả token đã chết | Dùng log tạo pool | Dùng danh sách hiện tại, báo cáo survivorship bias |
| | **Kết quả 12/11: ĐẠT cho cả 3 chuỗi**. Collector đã thử thêm V3 (Ethereum/Base), Aerodrome classic (Base); Solana xác nhận 222 pool mới từ CPI. V4/factory Slipstream và mẫu toàn kỳ chưa hoàn tất | | |
| 15/11 | Helius free: thử bằng key, đo tốc độ thật và số credit cho 1 token (sửa 12/11) | Solana được nhắm mức 1 | Solana mặc định mức 2, không chờ cổng 22/11 |
| | **Kết quả 12/11: ĐẠT** (gói free dùng được `getTransactionsForAddress`, khớp 8/8; collector đã thử full 100 tx/lần, chưa đo mức tối đa/credit riêng). Solana nhắm mức 1 | | |
| 18/11 | Có OHLCV đợt 1; tỷ lệ ca dương trên A + B trước T2 nằm trong 5–50% (Mục 5.2, sửa 12/11) | Giữ target | Dừng, đề xuất đổi ngưỡng với sinh viên |
| 22/11 | Bộ đọc swap Solana khớp tay ≥ 20 giao dịch trên ≥ 2 sàn; đã thu ≥ 30 token | Solana đủ phạm vi | Xuống mức 2 |
| 29/11 | Ca dương trên cutoff trước T2, tính cả 3 chuỗi, ≥ 20 (đề xuất) | Làm đủ logistic regression + gradient boosting | Chỉ giữ rule-based + logistic regression; RQ2 ghi là khám phá |
| 13/12 | Test có ≥ 10 ca dương (đề xuất) | Báo cáo đủ chỉ số | Không kết luận theo từng chuỗi; báo khoảng tin cậy và số ca thật |

**Các mức cho Solana:**
- **Mức 1 (mục tiêu, chỉ khi cổng Helius 15/11 đạt):** đủ mẫu, đủ feature, vào model.
- **Mức 2:** OHLCV đủ 100 token, swap trên mẫu nhỏ; làm RQ1 và RQ4, RQ2 chỉ dùng Base + Ethereum.
- **Mức 3:** chỉ sàng lọc OHLCV và ghi rõ chưa xác minh được bằng swap.

**Rủi ro khác:**

| Rủi ro | Phương án |
|---|---|
| Blockscout bỏ API không key hoặc giới hạn credit | **Đã xảy ra với Base (12/11)** → chuyển dRPC. Ethereum: key free Blockscout; dự phòng Etherscan V2 (Ethereum miễn phí) hoặc dRPC |
| dRPC đổi giới hạn hoặc hết CU | Cache, lưu tiến độ; giảm số ngày thu swap Base (chỉ ngày bị gắn cờ + 7 ngày trước cutoff); cuối cùng là Base mức 3 (chỉ OHLCV) |
| Helius hết credit hoặc đổi gói free | Hạ trần giao dịch/token; dự phòng RPC công khai (chậm, ~0,35 lần/giây) |
| Base có nhiều loại pool | Đọc V2, V3, Aerodrome classic và **Uniswap V4** (thêm 12/11: V4 chiếm ~90% pool mới trên Base). Slipstream ghi là chưa hỗ trợ. Đọc swap V4 là việc mới phải làm |
| Công thức LPI x·y=k không đúng với pool V3 | Vẫn chạy LPI theo OHLCV + swap; chỉ tính price impact cho pool kiểu V2 |
| Trễ lịch | Cắt theo thứ tự: LPI pha 2, hướng mở rộng, walk-forward. Không cắt: wash trading, temporal split, kiểm tra thủ công |

## 8. Lịch và phân công (đề xuất)

| Thời gian | Việc | Điểm dừng |
|---|---|---|
| 12/11 | Duyệt PLAN này (trễ 4 ngày so với dự kiến 06–08/11) | ✅ đã duyệt |
| 12–15/11 | DATA_CARD, schema, configs, `pyproject.toml`; đăng ký key; thử tay danh sách token, Helius và cách so số dư Solana | ✋ 15/11 — **xong và duyệt 12/11** ✅ |
| 16–29/11 | Collector, cache; OHLCV 2 đợt; swap; EDA. **Bắt đầu sớm 12/11 theo yêu cầu sinh viên:** đã chạy kỹ thuật 3 pool, 10.887 nến, 10 swap EVM; **task 1 gộp truy vấn Base đã kiểm thử xong 12/11**; **task 2 (danh sách ứng viên 3 chuỗi) chạy 12/11**, đang sàng lọc chọn A/B (cũng là OHLCV ngày đợt 1). Chưa hoàn tất mẫu 300 token hoặc các cổng sau | ✋ 29/11 — đang làm |
| 23/11–06/12 | Wash trading, LPI, rule rug/pump & dump, unit test, độ nhạy | ✋ 06/12 |
| 30/11–06/12 | 5 nhóm feature, FEATURES.md, `test_no_leakage` | cùng ✋ 06/12 |
| 07–13/12 | Baseline, rule score, model; chạy test một lần | ✋ 13/12 |
| 10–17/12 | Codebook, lấy mẫu 60–100 ca, gán nhãn, gán lại 20% sau ≥ 3 ngày | ✋ 17/12 |
| 14–25/12 | Viết báo cáo tiếng Anh, hình, slide | ✋ 25/12 |
| 26–27/12 | Dự phòng, nộp | |

| Thành viên | Phụ trách chính |
|---|---|
| 1 | Base + Ethereum: collector, liquidity và holder từ log; sau đó indicator và feature chung |
| 2 | Solana: collector, bộ đọc swap, đối chiếu explorer; sau đó model và điều phối báo cáo |

Phân công trên là mặc định do mình đặt cho nhóm 2 người (sửa 12/11); nhóm tự đổi được. Cả 2 cùng gán nhãn thủ công để tính được Cohen's kappa, và cùng viết báo cáo.

Với 2 người, phần việc chung (indicator, feature, model) không còn người riêng. Nếu trễ ở cổng 22/11 thì Solana xuống mức 2 ngay, không cố giữ mức 1.

## 9. Đánh giá

- **Tái lập:** so với số của paper theo từng chuỗi, giải thích khác biệt do thời kỳ, cỡ mẫu và nguồn dữ liệu; ngưỡng mặc định lấy từ paper, ghi trong `configs/thresholds.yaml`.
- **Detector:** PR-AUC, precision@k, recall, confusion matrix, calibration, tách theo chuỗi và nhóm A/B/C/D khi đủ ca.
- **Thủ công:** precision thực tế của từng indicator; phân tích các ca sai.
- **Chi tiết chưa xác minh trong paper:** dùng cách của artifact và ghi rõ (DATASET_NOTES Mục 2, THRESHOLD_AUDIT).

## 10. Câu hỏi cho nhóm

> Sinh viên yêu cầu bỏ qua câu 1–4 (2026-11-12). Dùng mặc định dưới đây cho tới khi nhóm nói khác; agent không hỏi lại các câu này.
>
> 1. Mẫu báo cáo: IEEE hai cột.
> 2. Phân công: theo bảng 2 người ở Mục 8.
> 3. Key: chưa có ai đăng ký. Việc cần key thì báo đúng lúc cần; cổng Helius 15/11 không có key coi như không đạt.
> 4. Lịch giảng viên: coi như không có mốc nào trước 27/12.

1. **Mẫu báo cáo:** giảng viên có yêu cầu IEEE/ACM không? Chưa rõ thì mặc định IEEE hai cột.
2. **Phân công:** phân công ở Mục 8 có ổn không? Ai có thời gian nhất nên nhận Solana.
3. **Key:** ai đăng ký Blockscout và Helius bản free? Key để trong `.env`, không gửi vào chat.
4. **Lịch giảng viên:** có mốc nộp giữa kỳ hoặc thuyết trình trước 27/12 không?
5. ~~**Tham số:** có đồng ý H = 30 ngày, ngưỡng sụp giá ≥ 80%, 300 token không?~~ Đã đồng ý khi duyệt PLAN ngày 2026-11-12.
