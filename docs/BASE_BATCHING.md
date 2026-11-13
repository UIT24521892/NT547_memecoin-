# Gộp truy vấn Base: kết quả và cách kiểm thử

> 2026-11-12 [codex]. Task 1 thuộc dòng collector 16–29/11, được sinh viên yêu cầu làm sớm sau khi thiết kế đã duyệt. Phạm vi, cỡ mẫu, cutoff và các cổng trong PLAN giữ nguyên. Kết quả dưới đây đo trên **1.000 block**, chưa phải lần thu toàn tập nghiên cứu.

## 1. Module này làm gì?

| Khái niệm | Như trẻ 5 tuổi | Định nghĩa chính xác | Ví dụ đời thường |
|---|---|---|---|
| Gộp truy vấn | Hỏi nhiều nơi trong một lần rồi chia các câu trả lời về đúng chỗ | Một lời gọi `eth_getLogs` lọc nhiều địa chỉ và nhiều lựa chọn event trong cùng dải block; client kiểm tra nguồn phát log trước khi giải mã | Đi một chuyến chợ lấy hàng ở ba quầy |
| Đo hiệu năng (benchmark) | Làm cùng một việc bằng hai cách, xem cách nào cần ít lượt và ít thời gian hơn | So sánh trên cùng bộ lọc/dải block; kiểm tra tập kết quả bằng nhau, rồi đo request thực và thời gian | So hai cách giao cùng một danh sách hàng |
| Chạy tiếp (resume) | Đọc lại những trang đã chép rồi chép phần còn thiếu | Tiến trình mới dựng lại phần đã thu từ cache và chỉ gọi API cho dải chưa có; raw cũ được giữ nguyên | Mở sổ ở phần đã ghi khi quay lại làm tiếp |

Code thực hiện nằm trong `src/memecoin/collect/evm.py`, `http.py`, `cli.py`; bài đo và đối chiếu nằm ở `scripts/benchmark_base_batching.py`.

## 2. Bộ lọc gộp và điều kiện dùng

Base tự gộp khi chọn nhiều factory và `base.logs.multi_address=true` trong `configs/chains.yaml`. Ethereum giữ cách quét riêng. Thêm `--separate-factories` vào lệnh `discover` để chạy cách quét riêng làm đối chứng.

Theo [đặc tả JSON-RPC của Ethereum](https://ethereum.org/developers/docs/apis/json-rpc/#eth_getlogs), `address` nhận được danh sách địa chỉ; mỗi vị trí trong `topics` có thể chứa nhiều lựa chọn OR. Vì vậy, ba event khác nhau tại `topic0` phải viết thành **một danh sách lồng trong vị trí đầu tiên**:

```json
{
  "address": ["<factory V2>", "<factory V3>", "<factory Aerodrome>"],
  "topics": [["<event V2>", "<event V3>", "<event Aerodrome>"]]
}
```

`topics: [event_V2, event_V3]` biểu diễn hai vị trí topic khác nhau, nên không thay thế được cấu trúc OR ở trên. Bộ lọc gộp nhận mọi tổ hợp của danh sách địa chỉ và event; client còn kiểm tra đúng **cặp địa chỉ factory/event** trước khi chọn ABI giải mã. Log sai địa chỉ, sai topic, ngoài dải hoặc `removed=true` sẽ báo lỗi.

Lệnh `logs` hỗ trợ nhiều `--addresses` và `--topics` để lấy các lựa chọn OR tại `topic0`. Bài đo hai pool dùng cùng bộ lọc Swap V2/V3 cho cả cách riêng và cách gộp.

Giới hạn vẫn lấy từ configs: tối đa **100 block/dải**, tốc độ **1,9 request/giây**. Gộp địa chỉ không làm tăng các giới hạn này.

## 3. Kết quả đo ngày 12/11/2026

Run được dùng làm kết quả cuối: `run_20261112T125120_608621Z`, đo xong lúc **12:52:31 UTC**. Nguồn số liệu là [comparison.json](../data/interim/base_batch_check/run_20261112T125120_608621Z/comparison.json) và [measurements.json](../data/interim/base_batch_check/run_20261112T125120_608621Z/measurements.json).

Cả hai cách quét dùng block **47.130.126–47.131.125**, bao gồm hai đầu: 1.000 block, chia thành 10 dải. Dải này có block ngay trước ngày 10/06 UTC; không gọi đây là cả ngày 10/06.

| Đối tượng | Kết quả hai cách cùng trả | Request logic riêng → gộp | HTTP thực riêng → gộp | Thời gian riêng → gộp |
|---|---|---:|---:|---:|
| 3 factory: Uniswap V2, Uniswap V3, Aerodrome classic | **23 log**: 20 V2 + 2 V3 + 1 Aerodrome; **12 ứng viên pool có WETH** | 30 → 10 | **30 → 10** | **16,325 → 5,278 giây** |
| 2 pool, dùng bộ lọc Swap V2/V3 | **77 log**: 8 của pool V3 + 69 của pool V2 | 20 → 10 | **27 → 10** | **38,610 → 5,470 giây** |

Với ba factory, số HTTP giảm **66,67%**, thời gian lần đo giảm **67,67%**. Với hai pool, số HTTP giảm **62,96%**, nhưng baseline có **7 lượt HTTP thêm do retry**, nên chênh lệch thời gian chịu ảnh hưởng của lỗi mạng/backoff. Không coi mức giảm thời gian **85,83%** của lượt đo pool là tốc độ cố định cho mọi lần chạy.

Hai pool dùng làm fixture kỹ thuật:

- Pool V3 BRETT/WETH: `0x4e829f8a5213c42535ab84aa40bd4adcce9cba02`.
- Pool Uniswap V2: `0x6298bf80e26bf2228e9e8e9bcdd0d4c80be369cb`, đã quan sát có swap trong dải thử.

Các địa chỉ chỉ phục vụ kiểm tra chức năng gộp; chưa được chọn vào mẫu nghiên cứu theo thanh khoản tại cutoff. Các ứng viên tạo pool cũng chưa được xác minh toàn bộ là meme coin.

So sánh gộp/riêng kiểm tra nội dung log on-chain sau chuẩn hóa biểu diễn hex: địa chỉ, block hash/number, transaction hash/index, log index, topics, data và trạng thái removed. `raw_ref`/`collected_at` khác nhau giữa hai lần thu được giữ riêng làm provenance. Bảng ứng viên được so nội dung sau khi bỏ hai cột metadata này. **Cả 9 điều kiện trong `comparison.json` đều đạt**; không chỉ so số dòng.

## 4. Kiểm tra dừng rồi chạy tiếp

Bài đo dùng cache riêng cho tình huống resume, không lấy cache của lượt gộp đã hoàn tất để giả lập dừng:

| Bước | Kết quả quan sát |
|---|---|
| Tiến trình thứ nhất chạy với `--max-chunks 3` | 3 request mới, dừng sau block **47.130.425**; `complete=false`, `error=null`, `next_block=47130426`; exit code 2 vì chưa thu hết |
| Khởi động tiến trình thứ hai trên cùng cửa sổ/cache | **3 cache hit + 7 request mới**, đủ 10 dải; `complete=true`, exit code 0 |
| Đối chiếu kết quả cuối | Cùng 23 log và 12 ứng viên với lượt gộp đầy đủ |

`--max-chunks` giới hạn số dải **mới cần gọi mạng**; các dải đọc từ cache không ăn ngân sách này. Vì vậy chạy lại trên cache đầy đủ có thể trả hết cửa sổ dù giới hạn dải mới nhỏ. Đây là kiểm tra dừng có kiểm soát qua hai tiến trình, chưa phải thử mất điện hoặc hỏng ổ đĩa.

## 5. Kiểm thử lại

Từ thư mục gốc repo, chạy:

```bash
.venv/bin/python -m pytest
.venv/bin/python scripts/benchmark_base_batching.py
```

Bộ test tại thời điểm bàn giao có **68 test + 12 subtest qua** (65 của Codex + 3 test ghi nguyên tử thêm khi khép task 1, xem Mục 7). Lệnh benchmark không có `--online` sẽ replay run được trỏ bởi `data/interim/base_batch_check/latest.json`, bỏ key khỏi môi trường và dùng CLI offline không đọc `.env`. Nó chạy lại 6 tình huống đầy đủ, yêu cầu **0 request mạng**, so byte các file đầu ra với bản online và kiểm tra SHA-256 raw. Báo cáo dừng `resume_paused` ban đầu được giữ làm bằng chứng; cache lúc replay đã đầy đủ nên không tái tạo một lần thiếu dữ liệu giả.

Để chỉ định đúng run nêu trong tài liệu:

```bash
.venv/bin/python scripts/benchmark_base_batching.py \
  --run data/interim/base_batch_check/run_20261112T125120_608621Z
```

Để tạo **một lần đo mới có gọi API**, dùng key dRPC đã có trong `.env`:

```bash
.venv/bin/python scripts/benchmark_base_batching.py --online
```

Mỗi lần online tạo thư mục run và cache namespace mới, nên thời gian đo không lấy lợi thế từ cache cũ. Lần đo mới có thể có số retry/thời gian khác. Dữ liệu/cache trong `data/` bị gitignore; bản clone mới chưa có raw/cache sẽ không chạy replay được cho tới khi có một đợt online hoặc được chép dữ liệu từ máy thu gốc.

Để dùng gộp trong collector thông thường:

```bash
.venv/bin/python scripts/collect.py discover --chain base \
  --start 2026-06-10 --end 2026-06-11 \
  --from-block 47130126 --to-block 47131125 \
  --factories uniswap_v2 uniswap_v3 aerodrome \
  --output data/interim/base_discovery_grouped
```

Thêm `--separate-factories` và chọn thư mục output khác để thu bản đối chứng. Khi đã truyền dải block, dải đó thắng ngày start/end. Với nhiều pool, truyền tất cả vào `logs --addresses ...`; dùng `--topics ...` cho các lựa chọn `topic0` hoặc `--topic ...` cho một event.

## 6. Tổ chức bằng chứng và giới hạn

- `data/interim/base_batch_check/<run>/manifest.json`: dải block, danh sách tham số từng tiến trình, cache namespace và hash configs.
- `measurements.json`: thời gian, số request/cache hit và trạng thái từng tình huống.
- `comparison.json`: kết quả đối chiếu và mức giảm đo được; bản tổng hợp mới nhất nằm ở `data/interim/base_batch_check/comparison.json`.
- Các thư mục `factories_*`, `pool_*`, `pools_grouped`, `resume_*`: JSON log, CSV ứng viên nếu có và `report.json` của từng collector.
- `offline_replay/results.json`: kết quả kiểm tra lại sau khi chạy lệnh offline.
- Raw nguyên bản ở `data/raw/<ngày>/drpc/`, kèm metadata request đã che key, namespace và SHA-256. Lượt đo cuối có **87 metadata raw, 0 lỗi hash**.
- Cache riêng dưới `data/interim/http_cache/drpc/<namespace>/`; mọi namespace vẫn chia sẻ `data/interim/http_cache/drpc/.rate.lock`, nên không tăng tốc bằng cách né giới hạn provider. Cache mặc định của đợt collector trước được giữ nguyên.

Chưa đo CU trên dashboard, nên giảm HTTP không đồng nghĩa đã chứng minh giảm CU đúng cùng tỷ lệ. Đây là một lượt đo trên 1.000 block; chưa đo toàn cửa sổ 150 ngày, độ ổn định dài hạn hoặc giới hạn khi gộp hàng trăm pool. Ước tính khoảng 9 giờ trong PLAN vẫn là ước tính; kết quả task 1 chưa đóng ✋ thu dữ liệu hoặc các cổng 18/11–22/11.

## 7. Khép task 1: ghi file cache nguyên tử (2026-11-12 [claude])

Subagent review của Codex bị ngắt vì hết lượt, nhưng trước đó đã thử ra một lỗi: tiến trình A đang ghi đè pointer cache thì tiến trình B đọc đúng file đó và gặp `JSONDecodeError`. Nguyên nhân là `write_json` ghi thẳng lên file thật. Vì các tiến trình collector dùng chung cache và rate limit, tình huống này có thể xảy ra khi chạy song song.

| Khái niệm | Như trẻ 5 tuổi | Định nghĩa chính xác | Ví dụ đời thường |
|---|---|---|---|
| Ghi nguyên tử (atomic write) | Viết xong hẳn rồi mới cho người khác xem | Ghi vào file tạm cùng thư mục, `fsync`, rồi `os.replace` sang tên thật. Thao tác đổi tên trên cùng hệ thống file là nguyên tử, nên người đọc chỉ thấy bản cũ hoặc bản mới hoàn chỉnh | Viết nháp ra giấy khác, viết xong mới dán lên bảng tin |

- Sửa `src/memecoin/collect/common.py`: `write_json` và `write_csv` dùng chung `_atomic_open`. File tạm có đuôi `.tmp` nên các lệnh glob `*.json`/`*.meta.json` không nhặt nhầm. Lỗi giữa chừng thì xoá file tạm và giữ bản cũ. Quyền file vẫn là 644.
- Raw body không đổi: vẫn ghi `xb` vào tên duy nhất, không ghi đè.
- Test thêm trong `tests/test_collectors.py`: đọc pointer đúng lúc đang ghi đè thì nhận bản cũ đầy đủ; ghi CSV hỏng giữa chừng thì giữ bản cũ, không sót file tạm; quyền 644.
- Kiểm chứng sau khi sửa: pytest 68 + 12 subtest qua; `benchmark_base_batching.py` và `check_collection.py` đều PASS, 0 request mạng, đầu ra giống từng byte với bản online.
- Giới hạn: test đồng thời chạy hai luồng trong một tiến trình, chưa thử hai tiến trình thật hoặc hệ thống file mạng.

