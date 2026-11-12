# Thử nghiệm Solana: từ giao dịch đến bảng mua/bán HEGE

> 2026-11-06 [codex]. Bài thử chỉ đọc trên một pool HEGE/SOL của Raydium, chưa phải mẫu nghiên cứu hay phê duyệt toàn bộ PLAN. Địa chỉ Solana phân biệt chữ hoa/thường. Không cần ví hay API key cho các bước dưới đây.

**Luồng thực hành:** đọc một giao dịch → tự động lấy giao dịch của một ngày → giải mã swap → đối chiếu kết quả.

| Kết quả hiện tại | Chi tiết |
|---|---|
| Lấy dữ liệu một ngày | Ngày 05/11/2026 UTC, 8 giao dịch liên quan pool; tải được 8/8 chi tiết theo node |
| Giải mã | 8 swap: 2 mua và 6 bán HEGE; 8 địa chỉ theo quy tắc nhận diện giới hạn |
| Kiểm tra chéo | 5 giao dịch có dữ liệu GeckoTerminal đã lưu đều khớp; 3 giao dịch chưa có nguồn đối chiếu |
| Còn mở | Kiểm tra ≥20 giao dịch trên ≥2 sàn; chưa tính wash trading hoặc risk score |

## Các khái niệm cần biết

| Khái niệm | Hiểu đơn giản | Định nghĩa | Ví dụ đời thường |
|---|---|---|---|
| Token mint address | Mã của đồng coin | Địa chỉ mint account nhận diện token trên Solana; tên/symbol có thể trùng | Mã sản phẩm |
| Pool và vault | Quầy đổi và các ngăn đựng tiền | Pool quản lý thị trường; vault là token account giữ một loại tài sản của pool | Quầy đổi tiền có hai ngăn USD và VND |
| Swap và signature | Lần đổi và mã hoá đơn | Swap là thao tác đổi tài sản; signature nhận diện transaction, có thể gồm nhiều thao tác | Một hoá đơn có nhiều dòng hàng |
| Token account và owner | Hộp chứa token và người quản lý hộp | Token account có mint và owner; địa chỉ account khác địa chỉ chủ | Tài khoản ngân hàng và chủ tài khoản |
| RPC | Quầy tra cứu dữ liệu | Giao diện gọi các phương thức đọc dữ liệu từ node | Xin danh sách hoá đơn rồi xem chi tiết |
| CPI / inner instruction | Một quầy nhờ quầy khác xử lý | Một chương trình gọi chương trình khác trong cùng transaction; `stackHeight` thể hiện độ sâu | Ứng dụng đặt đồ nhờ nhà hàng chuẩn bị |
| Opcode | Mã loại thao tác | Byte đầu instruction Raydium chọn biến thể lệnh; bộ đọc thử hỗ trợ 16/17 | Nút đổi tiền khác nút thêm tiền vào quầy |
| Raw amount / decimals | Lượng ghi bằng đơn vị rất nhỏ | Lượng hiển thị = lượng nguyên raw / 10^decimals | 100 xu = 1 đồng |
| Phân trang | Đọc từng trang sổ | Dùng signature cuối trang làm `before` để lấy trang cũ hơn | Lật sổ hoá đơn từ mới về cũ |
| Cache và retry/backoff | Giữ bản cũ; quầy bận thì đợi | Lưu phản hồi thành công theo yêu cầu; thử lại lỗi tạm thời với thời gian nghỉ tăng dần | Giữ bản photo, quay lại sau khi quầy bớt đông |

<a id="doc-giao-dich"></a>
## 1. Đọc một giao dịch thật

- **Token HEGE:** `ULwSJmmpxmnRfpu6BjnK6rprKXqD5jXUmPpS1FxHXFy`
- **Pool HEGE/SOL:** `CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd`
- [Token trên Solscan](https://solscan.io/token/ULwSJmmpxmnRfpu6BjnK6rprKXqD5jXUmPpS1FxHXFy) · [Pool trên GeckoTerminal](https://www.geckoterminal.com/solana/pools/CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd)

HEGE được chọn vì có trong artifact paper và pool ít giao dịch, thuận tiện cho học. Nó không đại diện cho toàn thị trường.

Mở [giao dịch mẫu trên Solscan](https://solscan.io/tx/4PW73UprtrFYXiYkRy2J2uKWkHmTkYCeqfdAqEXn9Wk7RyAd1r9EcAtwqVHNkEzk3TMFBAjMWf4Br3rfw6r7EsHN) hoặc [Solana Explorer](https://explorer.solana.com/tx/4PW73UprtrFYXiYkRy2J2uKWkHmTkYCeqfdAqEXn9Wk7RyAd1r9EcAtwqVHNkEzk3TMFBAjMWf4Br3rfw6r7EsHN). Theo RPC và GeckoTerminal đã lưu:

| Trường | Kết quả |
|---|---|
| Thời gian | 2026-11-06 14:24:51 UTC, tức 21:24:51 giờ Việt Nam |
| Ví ký, khớp trader GeckoTerminal trong ca này | `DVKLweWcgUSnLYihdD1TZxyxAGE72fkQSk6K4MBAM4Zy` |
| Chiều và lượng swap | Bán `16268.492575658` HEGE; pool trả `0.232408308` SOL/WSOL |
| Số dư HEGE trước → sau | `16391.751621397` → `123.259045739`; giảm `16268.492575658` |
| Thay đổi SOL gốc ròng của ví | `+0.230341838` SOL; khác lượng swap vì có phí và chuyển khoản khác |

Số dư trước/sau nằm trong `preTokenBalances`/`postTokenBalances` của JSON, không nhất thiết hiện ở Summary của explorer. WSOL là SOL được giữ trong token account; account có thể được tạo rồi đóng ngay trong giao dịch. Fee mạng ca này là `0.000085` SOL; ngoài swap còn chuyển `0.001975470` WSOL và `0.000006` SOL. Không lấy ngay thay đổi SOL ròng làm lượng swap.

<details>
<summary>Tự hỏi RPC bằng Terminal</summary>

Lệnh sau lấy 5 signature tham chiếu pool, xếp từ mới đến cũ:

```bash
curl --silent --show-error --max-time 30 \
  'https://api.mainnet-beta.solana.com' \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","id":1,"method":"getSignaturesForAddress","params":["CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd",{"limit":5,"commitment":"finalized"}]}'
```

`signature` là mã giao dịch; `blockTime` là giây từ 01/01/1970 UTC; `err: null` nghĩa là không báo lỗi thực thi. Mỗi giao dịch tham chiếu pool chưa chắc là swap.

Lấy chi tiết giao dịch mẫu:

```bash
curl --silent --show-error --max-time 30 \
  'https://api.mainnet-beta.solana.com' \
  -H 'Content-Type: application/json' \
  --data '{"jsonrpc":"2.0","id":2,"method":"getTransaction","params":["4PW73UprtrFYXiYkRy2J2uKWkHmTkYCeqfdAqEXn9Wk7RyAd1r9EcAtwqVHNkEzk3TMFBAjMWf4Br3rfw6r7EsHN",{"encoding":"jsonParsed","maxSupportedTransactionVersion":1,"commitment":"finalized"}]}'
```

Tìm `meta.err`, `preTokenBalances`, `postTokenBalances` và mint HEGE. Tham số phiên bản `0` từng gây lỗi `-32015` với tx v1; số nguyên `1` cho phép đọc legacy/v0/v1 theo tài liệu Solana. HTTP 429: nghỉ 30–60 giây rồi thử lại một lần; 403: ghi nhận bị từ chối; `result: null` chưa đủ để kết luận giao dịch không tồn tại.

</details>

Mẫu học đầu tiên nằm trong [solana_pilot_sample.csv](../validation/solana_pilot_sample.csv). Các cột `manual_*` hiện là `pending`; agent không tự đánh dấu thay người kiểm tra.

<a id="thu-mot-ngay"></a>
## 2. Tự động thu một ngày UTC

[scripts/solana_day_pilot.py](../scripts/solana_day_pilot.py) tự xin các trang lịch sử, lọc thời gian, tải chi tiết và lưu dữ liệu. Lệnh chạy từ thư mục dự án:

```bash
cd /Users/macos/UIT/NT547/Project_2026
python3 scripts/solana_day_pilot.py --day 2026-11-05
```

Chương trình dùng Python chuẩn và curl; giới hạn mặc định 20 trang × 10 signature, tối đa 100 chi tiết, nghỉ 3 giây giữa request và có cache/backoff. Ngày UTC dùng khoảng **[00:00 ngày 05/11, 00:00 ngày 06/11)**, tương ứng 07:00 ngày 05/11 đến trước 07:00 ngày 06/11 giờ Việt Nam.

**Lần thu thành công ngày 06/11:** 2 trang, quét 20 signature gồm ngoài ngày, có 8 trong ngày, tải 8/8 chi tiết, 0 lỗi thực thi theo node; 10 request trong 28,42 giây. Có bản ghi ở hai phía cửa sổ. Chạy lại offline từ cache: 0 request, 10 cache hit, CSV giống hệt. Lần đầu thử sai phiên bản mất 5 request/13,17 giây và được lưu riêng; 10 request chỉ tính lần thành công.

- [Bảng kiểm kê transactions.csv](../data/interim/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z/transactions.csv) và [summary.json](../data/interim/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z/summary.json).
- JSON gốc, request và manifest: `data/raw/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z/`; raw/interim nằm trong gitignore. `summary.json` mới nhất phản ánh lần offline; manifest online giữ số request ban đầu.
- Raw của bài đọc 5 giao dịch: `data/raw/2026-11-06/solana_pilot_hege/`. Giữ nguyên raw; lần thu mới dùng thư mục riêng.

`window_bracketed = true` nghĩa là đã thấy bản ghi ở phía sau cửa sổ và lùi qua đầu ngày, không có thời gian rỗng trong phần đã quét. `details_all_downloaded = true` nghĩa là tải được mọi chi tiết đã chọn và timestamp/slot khớp. `provider_window_retrieved = true` nghĩa là cả hai điều kiện đạt **theo node đang dùng**, chưa chứng minh node không bỏ sót dữ liệu. Trang rỗng, hết giới hạn, lỗi RPC hay timestamp rỗng không chứng minh đã đủ.

Chạy lại từ cache, thay đường dẫn bằng `raw_dir` đã in ở lần trước:

```bash
python3 scripts/solana_day_pilot.py --day 2026-11-05 \
  --run-dir '/đường/dẫn/raw_dir/đã/in/ở/lần/trước' --offline
```

Giữ cùng ngày, pool và các giới hạn. Mỗi lần xử lý có manifest riêng; cache là ảnh chụp cũ, muốn cập nhật dữ liệu thì chạy lần mới.

<a id="giai-ma-swap"></a>
## 3. Giải mã swap thành bảng mua/bán

[scripts/solana_decode_pilot.py](../scripts/solana_decode_pilot.py) đọc JSON đã lưu, không gọi mạng:

```bash
python3 scripts/solana_decode_pilot.py --day 2026-11-05
```

Script chọn lần thu thành công mới nhất và in đường dẫn. Muốn chọn lần cụ thể:

```bash
python3 scripts/solana_decode_pilot.py --day 2026-11-05 \
  --run-dir data/raw/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z
```

Mở [bảng swaps.csv của lần sinh viên chạy](../data/interim/solana_day_pilot/2026-11-05/run_20261106T155457_437217Z/swaps.csv) hoặc [bản mẫu ban đầu](../data/interim/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z/swaps.csv).

### Cách xác định chiều và ví

1. Tìm đúng pool, program Raydium và lệnh `SwapBaseInV2`/`SwapBaseOutV2` opcode 16/17; kiểm tra layout, vault, mint và authority.
2. Chỉ lấy transfer trong lời gọi Raydium tương ứng, kiểm tra hai chân vào/ra và amount/bound. HEGE vào pool → `sell`; HEGE ra khỏi pool → `buy`.
3. Lần đường HEGE qua trung gian, kiểm tra chủ token có thay đổi số dư ròng đúng chiều/lượng và có ký transaction. Không mặc định signer đầu là trader.
4. Đường rẽ nhánh, thiếu dữ liệu, lượng không khớp hay chủ token không ký → `trader_status = unclear`; opcode/layout chưa hỗ trợ → `decode_status = unclear`. Trường hợp uỷ quyền hợp lệ có thể chưa nhận diện được.

Ở đây `trader` chỉ là **chủ tài khoản HEGE theo quy tắc trên**, không khẳng định danh tính hay người hưởng lợi cuối cùng. Lượng WSOL là chân pool; phí AMM có thể nằm trong input, còn phí mạng ghi riêng theo `meta.fee`. Không cộng thêm phí mạng nhiều lần nếu một transaction có nhiều swap.

**Ví dụ trung gian:** tx `44CDqPn4qW…` có signer đầu `ALVMJ9bny8…`, nhưng `100138.007820604` HEGE từ token account của `6Ve4JM25nb…` đi qua account tạm trước khi vào pool. Chủ HEGE ban đầu cũng ký và giảm đúng lượng đó; bộ đọc ghi `6Ve4…` theo quy tắc, đồng thời giữ các địa chỉ trung gian làm bằng chứng.

### Cách đọc và truy nguyên kết quả

| Cột/file | Ý nghĩa |
|---|---|
| `time_utc`, `signature`, `explorer_url` | Thời gian, mã và link giao dịch |
| `side`, `amount_token`, `amount_quote` | Mua/bán HEGE, lượng HEGE và WSOL của chân pool |
| `trader`, `trader_status`, `trader_basis` | Địa chỉ theo quy tắc, trạng thái và lý do |
| `pool_input_owner`, `pool_output_owner`, `transaction_signers` | Các owner trực tiếp và toàn bộ signer; có thể gồm trung gian |
| `transaction_fee_sol` | Phí mạng của cả transaction |
| `decode_status`, `manual_status` | Trạng thái giải mã; manual tự tạo là `pending` |
| `source_json`, `source_sha256` | JSON gốc và mã băm để truy nguyên |
| `token_flows.csv` | Chân swap (`swap_leg`) và chuyển khoản ngoài swap (`outside_decoded_swap`) |
| `swap_evidence.json`, `swap_decode_summary.json` | Instruction, transfer, đường lần ví và thống kê |

Không phải mọi transfer ngoài swap đều là phí. Chương trình chưa dựng sổ cái đầy đủ của SOL native/tài khoản tạo hoặc đóng, và chỉ mô tả chân pool được chọn. `swaps.csv` được tạo lại khi chạy script; ghi nhận xét thủ công riêng trong `validation/`.

### Kết quả và kiểm tra

| Giờ UTC 05/11 | Chiều | HEGE | WSOL |
|---|---|---:|---:|
| 09:37:50 | sell | 100138.007820604 | 1.436568944 |
| 14:41:39 | sell | 65043.481664093 | 0.931708040 |
| 14:51:31 | sell | 1000.000000000 | 0.014315794 |
| 15:26:39 | buy | 77422.314304849 | 1.114698420 |
| 18:05:49 | sell | 75210.934707444 | 1.077477628 |
| 18:06:09 | sell | 39175.462815221 | 0.560648264 |
| 20:14:31 | sell | 18446.484201134 | 0.263853512 |
| 22:06:14 | buy | 69.010755052 | 0.000991900 |

18 test cục bộ đã qua: 7 test thu dữ liệu, 11 test decoder. Hai chân transfer khớp biến động hai vault trên 8 tx; tx mẫu ngày 06/11 khớp GeckoTerminal về chiều, lượng và trader. Chạy lại decoder không gọi mạng. Lệnh test:

```bash
python3 -m unittest discover -s tests -p 'test_solana*.py' -v
```

<a id="doi-chieu"></a>
## 4. Đối chiếu và giới hạn

Codex so bảng 8 dòng với GeckoTerminal đã lưu: **5/8 có nguồn tham chiếu**, gồm 2 buy và 3 sell; cả 5 khớp chiều, lượng HEGE/WSOL, địa chỉ và thời gian. **3/8 chưa có nguồn**, không tính đúng hay sai. Chi tiết: [solana_gecko_crosscheck_2026-11-05.csv](../validation/solana_gecko_crosscheck_2026-11-05.csv).

Đây là đối chiếu tự động của agent, không phải kiểm tra trực quan trên explorer hoặc nhãn do sinh viên gán. Hai nguồn cùng dựa trên blockchain và có thể liên quan về hạ tầng; 5 ca được chọn theo khả năng có nguồn, không dùng để báo cáo precision indicator. Đánh giá detector sau này vẫn cần mẫu phân tầng và ghi người kiểm tra.

Bộ đọc chỉ hỗ trợ Raydium AMM opcode 16/17, chưa hỗ trợ mọi opcode, Raydium CLMM, PumpSwap hay Meteora; chưa chứng minh quy tắc trader đúng tổng quát. Một pool ít giao dịch không đại diện khả năng thu 100 token. Chưa kiểm tra độc lập ≥20 giao dịch/≥2 sàn, chưa tính wash/LPI/risk score; giá tăng không tự chứng minh thao túng.

## 5. Nguồn tham khảo

- [Solana getSignaturesForAddress](https://solana.com/docs/rpc/http/getsignaturesforaddress) · [getTransaction](https://solana.com/docs/rpc/http/gettransaction) · [RPC JSON structures](https://solana.com/docs/rpc/json-structures) · [phiên bản transaction](https://solana.com/docs/core/transactions/versioned-transactions) · [giới hạn RPC công khai](https://solana.com/docs/references/clusters).
- [Raydium instruction.rs](https://github.com/raydium-io/raydium-amm/blob/master/program/src/instruction.rs) và [processor.rs](https://github.com/raydium-io/raydium-amm/blob/master/program/src/processor.rs), đối chiếu ngày 06/11/2026. “V2” trong tên lệnh Raydium không có nghĩa pool Uniswap V2.
- [GeckoTerminal: danh sách pool](https://api.geckoterminal.com/api/v2/networks/solana/tokens/ULwSJmmpxmnRfpu6BjnK6rprKXqD5jXUmPpS1FxHXFy/pools?page=1) · [giao dịch gần đây của pool](https://api.geckoterminal.com/api/v2/networks/solana/pools/CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd/trades). Endpoint gần đây chỉ hỗ trợ đối chiếu, chưa thay thế nguồn lịch sử.
