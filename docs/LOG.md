# Nhật ký phiên làm việc

> Mỗi phiên có thay đổi thực chất: thêm một mục ở **cuối** file (ngày, ai, làm gì, quyết định, vì sao, còn mở gì). Phiên 2026-10-01 của codex (đối chiếu ngưỡng, nguồn dữ liệu, READING_GUIDE, LEARNING_ROADMAP) được ghi tóm tắt trong `MEMORY.md` Mục 4, chưa có mục riêng ở đây.

## 2026-10-16 [claude] — Ghi chú đọc paper chính theo từng mục

- **Làm gì:** tạo [PAPER_NOTES_MAIN.md](PAPER_NOTES_MAIN.md), gồm tóm tắt từng mục, keyword nguyên văn để highlight (quy ước 4 màu), 48 câu hỏi phản biện (PB) và bảng nối PB → RQ/mục AGENTS.md. Thêm link từ READING_GUIDE.
- **Phát hiện khi kiểm tra số học** (ghi là "mình tính" trong file):
  - Tab. 6: Avg/Addr ≠ Tot/#Addr ở mọi dòng.
  - §3.1.3 ghi 35.116, đúng phải là 35.216.
  - §5.2.3: 71/287 = 24,74%, paper ghi 24,27%.
  - Contribution 4 và dòng 33 mâu thuẫn về mẫu số của 62,9%.
  - §2 trích [9] cho kết quả "$240M 1-day rug pulls", nhưng con số này nằm trong [11]; có thể trích nhầm vì chưa đọc [9].
  - Nếu chỉ tính wash ∪ LPI (bỏ cờ anomaly) thì được 315/707 ≈ 44,6%, so với con số tiêu đề 82,89%.
- **Hệ quả cho PLAN (chưa chốt):**
  - Paper chỉ tìm được 2 rug pull, nên target của đồ án nên là "rug **hoặc** sụp giá nghiêm trọng" và H phải chọn sao cho đủ ca dương.
  - Chữ "previously" của 62,9% đúng nhờ cách chia hai cửa sổ thời gian; paper không đo lead time. Đồ án đo được (RQ2).
- **Còn mở:** sinh viên chưa duyệt ghi chú; 5 câu hỏi cho sinh viên (MEMORY.md Mục 2) vẫn chưa có trả lời.

## 2026-10-16 [claude] — Snapshot thị trường meme coin 01/2026 → 16/10/2026

- **Làm gì:** tạo [MARKET_SNAPSHOT_2026-10-16.md](MARKET_SNAPSHOT_2026-10-16.md) theo yêu cầu sinh viên. Nội dung gồm:
  - Diễn biến thị trường meme từ đầu năm.
  - Top 10 theo vốn hoá (CoinGecko category Meme).
  - Độ ổn định trong 10 tháng.
  - Nguồn gốc, phân bổ ban đầu và holder hiện tại của từng coin.
  Dữ liệu API gọi tay, chỉ đọc; JSON để trong scratchpad, **không** ghi vào `data/raw/`. Không viết code collector.
- **Kết quả chính:**
  - Category meme 29,86 tỷ USD (16/10). Tổng top 10 giảm 26,9% từ 01/01 (có survivorship bias).
  - DOGE ổn định nhất (biến động năm hoá 66%, MAD 42%, max drawdown −54,5%) nhưng vẫn biến động hơn BTC.
  - Theo số thô, cả 10 coin đều vượt ngưỡng top-10 > 30%. Với DOGE, SHIB, PEPE, phần lớn top-10 là sàn hoặc burn, đúng như PB13.
- **Quyết định nhỏ:** "đang nổi" hiểu là top theo vốn hoá, vì danh sách trending CoinGecko lúc đó không có meme coin nào. Giữ nguyên PUMP và M theo phân loại của CoinGecko, có ghi chú.
- **Còn mở:**
  - Mở trang gốc các nguồn 🔎 trước khi trích vào báo cáo.
  - Nhãn top holder của TRUMP, PUMP, 币安人生 chưa xác minh.
  - Năm ra đời của SPX6900 chưa xác minh.

## 2026-11-06 [claude] — Rà tiến độ, kiểm tra lại nguồn dữ liệu, so sánh chuỗi

- **Sinh viên trả lời:** nhóm 3 người; hạn nộp tháng 12 (chưa có ngày cụ thể); báo cáo theo dạng bài báo khoa học.
- **Làm gì:** đọc lại docs Dune, Etherscan, Helius; gọi thử chỉ đọc bằng curl trên RPC công khai, Blockscout, GeckoTerminal; đếm số dòng theo chuỗi trong artifact Zenodo. Không ghi gì vào `data/raw/`, không viết collector. Kết quả ở `MEMORY.md` Mục 4.
- **Phát hiện chính:**
  - Blockscout đọc được lịch sử swap của Base và Ethereum, có `tx.from` và creator, nên Dune/Etherscan không còn bắt buộc. BSC không có đường miễn phí tương đương.
  - GeckoTerminal free chỉ trả khoảng 184 ngày nến (đo trên 1 pool), nên giới hạn T0 của đồ án.
  - Artifact: 85/91 ca pump & dump trên Solana, Base chỉ 2. Base dễ thu dữ liệu nhưng có thể thiếu ca dương.
- **Đính chính:** phiên này ban đầu nêu "tác giả có sẵn SQL cho Base" làm lý do chọn Base; thực tế artifact có SQL cho cả 4 chuỗi nên đây không phải lợi thế riêng.
- **Quyết định của sinh viên (cùng ngày):** chọn Base và Ethereum; báo cáo cuối viết bằng tiếng Anh; đồng ý commit `Project_2026/` để sao lưu.
- **Còn mở:** ngày nộp cụ thể, mẫu báo cáo; `PLAN.md`; giá credit Blockscout; đếm thử ca dương trên Base và Ethereum.

## 2026-11-06 [claude] — Duyệt tài liệu, đếm ca dương theo chuỗi, thử Solana

- **Sinh viên duyệt:** `READING_GUIDE`, `LEARNING_ROADMAP`, `PAPER_NOTES_MAIN`.
- **Đếm từ artifact Zenodo** (CSV gốc, số token khác nhau; thời kỳ 2024 đến 03/2025; chỉ 4 chuỗi):

| Chuỗi | Token tăng mạnh | Có wash | Có LPI | Pump & dump | Rug pull |
|---|---:|---:|---:|---:|---:|
| Base | 47 | 23 | 7 | 2 | 0 |
| Ethereum | 67 | 29 | 10 | 1 | 1 |
| BSC | 298 | 52 | 11 | 3 | 0 |
| Solana | 295 | 183 | 12 | 54 | 1 |

- **Mình tự tính thêm, không phải kết quả của paper:** đếm token có giá đóng cửa thấp nhất giảm ít nhất X% so với mốc 2025-01-15, trong H ngày sau, từ `ohlcv_data_day_until_mid_march.zip`. Ngày mốc do mình chọn cho "mid-January". Chỉ tính token có giá trong 3 ngày trước mốc.

| Chuỗi | Token đủ dữ liệu | H=30, giảm ≥80% | H=60, giảm ≥80% | H=60, giảm ≥90% |
|---|---:|---:|---:|---:|
| Base | 30 | 2 (6,7%) | 11 (36,7%) | 2 |
| Ethereum | 50 | 4 (8,0%) | 16 (32,0%) | 5 |
| BSC | 84 (17 thiếu giá sau mốc) | 5 (6,0%) | 11 (13,1%) | 5 |
| Solana | 267 (4 thiếu giá sau mốc ở H=30) | 31 (11,6%) | 73 (27,3%) | 37 |

- **Hạn chế của bảng trên:** chỉ gồm token đã tăng mạnh; giảm chung của thị trường đầu 2025 lẫn vào (trung vị mức giảm sâu nhất trong 30 ngày là −54% ở Base, −55% ở Ethereum); sụp giá chưa phải bằng chứng thao túng. Chỉ dùng để ước lượng khả thi.
- **Thử Solana (chỉ đọc):** kết quả ở `MEMORY.md` Mục 4. Đọc được lịch sử, nhưng phải tự dựng bảng swap và chi phí tăng theo số giao dịch.
- **Mình đề xuất:** giữ Base + Ethereum, Solana chỉ là dự phòng, vì Solana tốn công và hạn gấp. BSC không giải quyết được vì vẫn chưa thấy đường miễn phí và pump & dump cũng ít.
- **Sinh viên quyết định khác đề xuất:** dùng cả 3 chuỗi Base, Ethereum, Solana ngay từ đầu.
- **Viết [PLAN.md](PLAN.md) theo quyết định đó (bản nháp, chờ duyệt):** 300 token, H = 30, target sụp giá ≥ 80%, T0–T3 theo giới hạn 180 ngày, các cổng quyết định và 3 mức dự phòng cho Solana.
- **Còn mở:** duyệt PLAN và 5 câu hỏi ở Mục 10 của file đó; nguồn danh sách token kể cả token đã chết; thử Helius free bằng key.

## 2026-11-06 [codex] — Hướng dẫn thử Solana trước trên HEGE/SOL

- **Sinh viên yêu cầu:** hướng dẫn thử Solana ngay sau khi trao đổi vai trò Dune và ưu tiên kiểm tra phần khó. Đây là cho phép bài thử nhỏ, chưa phải duyệt toàn bộ PLAN.
- **Làm gì:** tra mint HEGE trong artifact paper; đọc danh sách pool từ GeckoTerminal, chọn pool Raydium HEGE/SOL; gọi `getSignaturesForAddress` (5 dòng), `getTransaction` (1 tx), đọc trades gần đây để đối chiếu. Các yêu cầu chỉ đọc, không key, không ví. Không viết collector.
- **Kết quả:** endpoint công khai trả được dữ liệu. Giao dịch mẫu `4PW73UprtrFYXiYkRy2J2uKWkHmTkYCeqfdAqEXn9Wk7RyAd1r9EcAtwqVHNkEzk3TMFBAjMWf4Br3rfw6r7EsHN` lúc 14:24:51 UTC ngày 06/11 bán 16268.492575658 HEGE; pool trả 0.232408308 SOL/WSOL. Lượng HEGE khớp thay đổi số dư và inner transfer, chiều/lượng khớp GeckoTerminal. SOL gốc ròng ví tăng 0.230341838; cần tách phí/chuyển khoản ngoài swap.
- **Tài liệu:** [SOLANA_PILOT.md](SOLANA_PILOT.md), [bảng 5 giao dịch](../validation/solana_pilot_sample.csv). Các cột manual để trống, trạng thái `pending`; chưa tự nhận đã xem explorer hay gán nhãn thao túng.
- **Bằng chứng:** 4 JSON nguyên bản + manifest URL/tham số lưu tại `data/raw/2026-11-06/solana_pilot_hege/` (gitignore). Bản danh sách pool toàn Solana dùng để chọn ví dụ chỉ nằm trong thư mục tạm, không phải dữ liệu mẫu nghiên cứu.
- **Còn mở:** sinh viên đối chiếu 5 dòng trên explorer; sau đó ≥20 giao dịch/≥2 sàn, một ngày lịch sử đầy đủ và ước lượng chi phí. Chưa xác minh phân trang về lịch sử xa, holder tại cutoff hay tính khả thi cho 100 token.

### Tiến độ thực hành của sinh viên trong cùng phiên

- Sinh viên gửi ảnh Terminal: tự gọi `getSignaturesForAddress` thành công, nhận 5 dòng; đây là bằng chứng bước truy cập RPC cơ bản hoạt động trên máy sinh viên.
- Đã cùng đọc ảnh Solscan của tx mẫu `4PW73Upr…` và tx `3YtVZQJ…` (bán 100 HEGE lấy 0.0014299 WSOL). Ca thứ hai khớp chiều, lượng token/quote, thời gian và signer với dòng 6 CSV; chưa xác minh độc lập tất cả trường/pool trên explorer.
- Khi sinh viên hỏi đã xong phần nào: kiểm tra file cho thấy cả 5 dòng vẫn `pending`, cột manual trống. Đã đối chiếu qua trao đổi nhưng chưa ghi thành kết quả trong CSV; không tự đánh dấu manual thay sinh viên.
- Đây là hoàn thành bước truy cập dữ liệu và thực hành đọc giao dịch ban đầu; chưa hoàn thành cổng Solana 20 tx/2 sàn, lịch sử đủ ngày, collector, indicator hay model.

## 2026-11-06 [codex] — Tự động thử một ngày lịch sử Solana

- **Sinh viên cho phép:** “ok vậy thử chuyển sang bước tiếp theo xem”, tiếp nối đề xuất tự động lấy một ngày lịch sử. Giới hạn bài thử 1 pool/1 ngày, chưa duyệt toàn bộ PLAN.
- **Làm gì:** thêm [scripts/solana_day_pilot.py](../scripts/solana_day_pilot.py) dùng Python chuẩn + curl, whitelist 2 phương thức RPC đọc. Phân trang `before`, chọn ngày UTC theo [start, end), khử trùng signature, cache, nghỉ 3 giây, retry/backoff, giới hạn số trang/tx, ghi trạng thái thiếu/lỗi. Raw giữ nguyên phản hồi cùng request/thời điểm; CSV là bảng kiểm kê giao dịch tham chiếu pool, chưa phải bảng swap.
- **Lỗi đã phát hiện và sửa:** tham số `maxSupportedTransactionVersion: 0` của ví dụ đầu không đọc được tx v1 (RPC -32015). Đối chiếu [docs Solana](https://solana.com/docs/core/transactions/versioned-transactions) và gọi thử giá trị 1 thành công; sửa script/lệnh hướng dẫn. Không loại các tx này vì lỗi client.
- **Kết quả chạy thật:** pool HEGE/SOL, ngày 2026-11-05 UTC. Quét 2 trang, 20 signature gồm ngoài cửa sổ, chọn 8; tải 8/8 chi tiết, 0 lỗi thực thi theo node, timestamp và slot khớp. Có bản ghi sau cuối ngày và đã lùi qua đầu ngày. 10 request, 28,42 giây cho lần thu thành công. Raw: `data/raw/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z/`; CSV: `data/interim/solana_day_pilot/2026-11-05/run_20261106T154943_882679Z/transactions.csv`.
- **Chi phí thử lỗi:** lần đầu 5 request/13,17 giây, giữ ở `run_20261106T154824_706202Z`. Phiên còn 2 request curl thăm dò ngoài script. 10 request là riêng lần script thành công, không phải tổng mọi request trong phiên.
- **Kiểm tra:** 7 unit test qua (biên ngày, cursor, null timestamp, giới hạn, thiếu chi tiết, lỗi thực thi, hỗ trợ v1). Chạy lại offline bằng cache: 0 request, 10 cache hit, SHA-256 CSV trước/sau giống nhau. `summary.json` mới nhất phản ánh lần offline; manifest online gốc vẫn giữ chi phí ban đầu.
- **Tài liệu:** [thu một ngày](SOLANA_PILOT.md#thu-mot-ngay), nay đã gộp vào tài liệu pilot. Không sửa kết quả manual trong `validation/solana_pilot_sample.csv`.
- **Giới hạn/còn mở:** chỉ đảm bảo các bản ghi do node trả và các biên quan sát được; chưa kiểm tra độc lập mọi dữ liệu trên chuỗi. Chưa giải mã swap/trader, chưa tính wash/LPI, chưa kiểm tra 20 giao dịch/2 sàn hay khả thi 100 token. Bước sinh viên: mở CSV mới và đọc một giao dịch từ ngày lịch sử.

## 2026-11-06 [codex] — Bước 3: giải mã swap và đường HEGE

- **Sinh viên yêu cầu:** “vậy thì làm tiếp bước 3”, tức chuyển 8 giao dịch đã thu sang bảng ví/chiều/lượng. Chỉ mở rộng bài thử này, chưa duyệt toàn bộ PLAN.
- **Triển khai:** [scripts/solana_decode_pilot.py](../scripts/solana_decode_pilot.py), chỉ đọc file, không gọi mạng. Nhận diện Raydium AMM opcode 16/17 theo mã nguồn chính thức, kiểm tra pool/vault/mint/authority, lấy transfer trong đúng phạm vi CPI theo stackHeight và đối chiếu amount/bound. Tách hai chân swap với transfer ngoài swap, giữ phí mạng riêng. Dùng số nguyên, không float cho lượng token.
- **Attribution:** từ chân HEGE lần qua đường đơn cùng lượng, kiểm tra owner có net change HEGE đúng chiều/lượng và chữ ký. Không mặc định fee payer/signer đầu là trader; nhánh/thiếu dữ liệu để unclear. Chủ token không ký (ví dụ uỷ quyền) có thể chưa được nhận diện; không coi đây là phương pháp tổng quát đã xác minh.
- **Kết quả:** cả `run_20261106T154943_882679Z` và run sinh viên `run_20261106T155457_437217Z` tạo 8 dòng, 2 buy + 6 sell; 8 chủ HEGE theo quy tắc. Tx `44CDqPn4qW…`: signer đầu `ALVM…`, nhưng token xuất phát từ `6Ve4…`, qua account tạm; giữ cả trader lẫn owner trực tiếp của pool leg để có thể kiểm tra.
- **Đầu ra:** `swaps.csv`, `token_flows.csv`, `swap_evidence.json`, `swap_decode_summary.json` dưới thư mục interim của mỗi run. CSV có đường dẫn JSON gốc/SHA-256 và link explorer. Tất cả manual pending; không sửa bảng 5 giao dịch manual trước đó.
- **Kiểm tra:** 11 unit test decoder + 7 test thu dữ liệu = 18 qua. Đối chiếu transfer vào/ra với số dư hai vault trên 8 tx thật. Decoder trên tx mẫu ngày 06/11 khớp GeckoTerminal đã lưu về side, lượng HEGE, WSOL và trader. Không gọi mạng; raw giữ nguyên.
- **Tài liệu:** [giải mã swap](SOLANA_PILOT.md#giai-ma-swap), nay đã gộp vào tài liệu pilot; giải thích 3 tầng, ví dụ thật, cách chạy và giới hạn.
- **Còn mở:** sinh viên đối chiếu buy/sell trong bảng mới; mở rộng ≥20 giao dịch/≥2 sàn trước khi tin bộ đọc rộng hơn. Chưa chỉ báo wash/LPI, chưa tính risk score; WSOL ở chân pool không phải SOL ròng của toàn tuyến và không phải mọi transfer ngoài swap đều là phí.

## 2026-11-06 [codex] — Đối chiếu chéo thay sinh viên

- **Câu hỏi:** sinh viên hỏi vì sao cần tự đối chiếu 1 buy/1 sell khi agent có thể làm. Agent có thể chuẩn bị đối chiếu và bằng chứng; việc sinh viên tự xem vài ca giúp học, nhưng không bắt buộc sinh viên lặp lại chỉ để làm bước kiểm tra kỹ thuật này. Validation thủ công của nghiên cứu vẫn là việc riêng có yêu cầu người gán và mẫu phân tầng.
- **Đã làm:** dùng phản hồi GeckoTerminal `data/raw/2026-11-06/solana_pilot_hege/recent_trades.json` đã lưu trước đó, so với 8 dòng `swaps.csv` run sinh viên. Đối chiếu theo signature, chiều, HEGE, WSOL bằng `Decimal`, địa chỉ trader và timestamp. Không gọi API mới.
- **Kết quả:** 5/8 tx có trong phản hồi tham chiếu, gồm 2 buy và 3 sell; 5/5 khớp cả 5 trường. 3 tx còn lại `reference_unavailable`, không tính là sai/đúng. [CSV kết quả](../validation/solana_gecko_crosscheck_2026-11-05.csv), `method=automated_cross_source`, `reviewer=codex`.
- **Giới hạn:** web tool không mở được trang Solscan/Explorer của giao dịch buy/sell đã chọn, nên không nhận đã kiểm tra trực quan. GeckoTerminal và RPC cùng dựa vào on-chain, có thể dùng nguồn hạ tầng liên quan. Kiểm tra chéo này không thay validation thủ công, chưa xác minh ca trung gian `44CD…`, chưa đạt ≥20 tx/2 sàn và không dùng để tính precision của indicator. Các file manual gốc vẫn pending.
- **Tài liệu:** cập nhật [phần đối chiếu](SOLANA_PILOT.md#doi-chieu) giải thích kết quả và phân biệt người/agent.

## 2026-11-06 [codex] — Khảo sát công cụ đọc trình duyệt

- **Yêu cầu:** tìm model/MCP/plugin có thể đọc trang web, dùng được cho Codex hoặc Claude Code, để hỗ trợ đối chiếu Solscan.
- **Tìm hiểu:** [Playwright MCP](https://github.com/microsoft/playwright-mcp) hỗ trợ cả hai agent và có [extension kết nối Chrome đang mở](https://github.com/microsoft/playwright.dev/blob/main/mcp/configuration/browser-extension.mdx). [Claude in Chrome](https://code.claude.com/docs/en/chrome) là phương án riêng Claude; [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) cũng là lựa chọn. Danh mục ChatGPT có TinyFish, chưa kết nối, chưa thử, điều khoản/chi phí chưa kiểm tra.
- **Máy hiện tại:** Chrome 156, Node 26.8.1, npm/npx, Codex CLI 0.157.1, Claude Code 2.1.251. `codex mcp list` chỉ có OpenAI Developer Docs, `claude mcp list` chưa có server; chưa xác minh extension Chrome. Không sửa cấu hình CLI hay cài package/extension.
- **Thử thực tế:** Chrome headless với profile tạm riêng mở trang Solscan tx `3YtVZQJ…` chỉ trả Cloudflare “Just a moment”, không có nội dung HEGE/Swap. Profile tạm đã được dọn. Chưa thử kết nối Chrome đang mở của sinh viên; không khẳng định Playwright/extension sẽ vượt hoặc đọc được trang.
- **Tài liệu và đề xuất:** [BROWSER_TOOLS_2026-11-06.md](BROWSER_TOOLS_2026-11-06.md), có hướng dẫn tuỳ chọn cho từng agent, nguồn chính thức và giới hạn. Dùng trình duyệt chỉ đọc, không mua/bán/kết nối ví. Giữ phân biệt đối chiếu do agent với nhãn kiểm tra thủ công của nhóm.

## 2026-11-06 [codex] — Gộp tài liệu thử Solana

- **Yêu cầu:** gộp ba tài liệu pilot Solana để dễ theo dõi.
- **Đã làm:** gộp bài đọc giao dịch, thu dữ liệu một ngày, giải mã swap và đối chiếu vào [SOLANA_PILOT.md](SOLANA_PILOT.md); bỏ hai file hướng dẫn cũ sau khi chuyển nội dung. Đã cập nhật liên kết trong nhật ký và bộ nhớ dự án.
- **Còn mở:** kiểm tra thủ công mẫu phân tầng và mở rộng kiểm tra bộ đọc trên ít nhất 20 giao dịch/2 sàn; các giới hạn dữ liệu giữ trong tài liệu gộp.

## 2026-11-12 [claude] — Rà soát file, kế hoạch và tiến độ

- **Yêu cầu:** kiểm tra file dư/trùng, PLAN có hợp lý và đúng hướng nghiên cứu không, đã đi tới đâu. Chỉ đọc, không xoá hay sửa file nào ngoài mục nhật ký này và `MEMORY.md`.
- **File:** không có tài liệu nào trùng nội dung đến mức phải gộp. Rác có thể xoá: 2 file `translation-service.log*`, các `.DS_Store`. `meme_coin-main.zip` trùng với thư mục đã giải nén. Trong `data/raw/solana_day_pilot/` 22/25 file `.body` giống hệt file `.json` cùng tên (do cách script ghi); raw là bất biến nên giữ, nhưng collector thật không nên ghi đôi.
- **Môi trường:** `.venv` chưa có pytest; 18 test chạy được bằng `python -m unittest discover -s tests` (OK). Chưa có `pyproject.toml`/`requirements.txt`.
- **Git:** `PLAN.md`, `SOLANA_PILOT.md`, `BROWSER_TOOLS`, `scripts/solana_*.py`, `tests/`, `validation/` chưa commit.
- **Nhận xét PLAN (mình đánh giá, chưa phải quyết định):**
  - Ước tính Solana 69 giờ dựa trên 4 lời gọi/giây lý thuyết. Pilot đo thật 10 lời gọi/28,42 giây (≈0,35/giây); với tốc độ đó 1 triệu giao dịch mất khoảng 33 ngày. Mức 1 của Solana không khả thi bằng RPC công khai.
  - Tỷ lệ ca dương ước từ token đã tăng mạnh tại mốc 2025-01-15, không phải token 7 ngày tuổi; với token mới, tỷ lệ sụp ≥80% trong 30 ngày có thể cao hơn nhiều. Cần đếm thử trước khi chốt target.
  - Nhóm A chưa định nghĩa "cửa sổ quan sát": phải nằm trước cutoff, nếu không là chọn mẫu theo tương lai.
  - Nhóm C (token lâu đời, cutoff ngẫu nhiên) dễ bị model tách chỉ bằng tuổi/thanh khoản; nên chỉ dùng để đo false positive hoặc báo cáo chỉ số có và không có C.
  - Bộ giải mã hiện tại chỉ đọc Raydium AMM opcode 16/17, khác cách "so số dư trước/sau" không phụ thuộc sàn mà PLAN đề xuất.
- **Tiến độ:** PLAN chưa duyệt (lịch ghi 06–08/11); việc 09–15/11 (DATA_CARD, schema, configs, thử danh sách token) chưa bắt đầu; cổng 15/11 còn 3 ngày. Còn 45 ngày tới hạn 27/12.
- **Còn mở:** nhóm duyệt PLAN và quyết định có hạ Solana xuống mức 2 ngay không.

## 2026-11-12 [claude] — Sinh viên duyệt PLAN; sửa AGENTS.md và CLAUDE.md để bám kế hoạch

- **Sinh viên quyết định:** duyệt `docs/PLAN.md` (gồm H = 30, sụp giá ≥ 80%, 300 token), và yêu cầu sửa hai file hướng dẫn để agent bám sát kế hoạch.
- **Sửa PLAN (5 điểm của lần rà soát, đánh dấu "sửa 12/11"):** nhóm A xếp theo mức tăng trước cutoff; nhóm C chỉ đo false positive, không train; ước tính Solana theo tốc độ đo thật (≈33 ngày, không khả thi bằng RPC công khai); thêm bước kiểm tra tỷ lệ ca dương trước T2 (ngoài 5–50% thì dừng hỏi sinh viên); ghi rõ cách so số dư Solana chưa được viết. Thêm 2 cổng: Helius 15/11, tỷ lệ ca dương 18/11. Dòng lịch 09–15/11 đổi thành 12–15/11.
- **Mình tự chọn, sinh viên chưa xác nhận riêng:** nếu cổng Helius 15/11 không đạt thì Solana mặc định mức 2. Câu hỏi "hạ Solana xuống mức 2 ngay" chưa được trả lời nên mục tiêu mức 1 vẫn giữ, chỉ thêm điều kiện.
- **AGENTS.md:** thêm mục "Bám sát kế hoạch đã duyệt" (thứ tự ưu tiên giữa AGENTS/PLAN/configs, quy trình 8 bước mỗi phiên); cập nhật các chỗ lỗi thời ở Mục 0, 5, 9, 10, 14, 15 và trỏ về PLAN thay vì chép số.
- **CLAUDE.md:** nạp sẵn `docs/PLAN.md` bằng `@docs/PLAN.md`; bỏ quy tắc "Tuần 1–2 chỉ viết tài liệu" và ghi chú Mục 14/15 đã hết hiệu lực; thêm yêu cầu nêu dòng lịch và cổng ở đầu phiên, đánh dấu trạng thái trong PLAN cuối phiên; ghi chú tạm về pytest.
- **Còn mở:** câu 1–4 ở PLAN Mục 10; xoá file rác và commit (chưa được cho phép); 3 ngày cho toàn bộ dòng lịch 12–15/11.

## 2026-11-12 [claude] — Nhóm 2 người; bỏ câu 1–4; thử log tạo pool

- **Sinh viên:** nhóm có **2** thành viên (trước ghi 3); bỏ qua câu 1–4 ở PLAN Mục 10. Mình đặt mặc định trong PLAN Mục 10 (IEEE hai cột, phân công 2 người ở Mục 8, chưa có key, không có mốc giữa kỳ); agent không hỏi lại. Sửa số thành viên ở PLAN, AGENTS.md, MEMORY.md.
- **Thử cổng 15/11 (chỉ đọc, kết quả để ở scratchpad, không ghi `data/raw/`):**
  - Ethereum: Blockscout không key trả 167 log `PairCreated` của Uniswap V2 trong ngày 2026-06-10, 1 lần gọi. Log tạo pool giữ cả pool đã chết, nên giải được survivorship bias cho pool V2.
  - Base: Blockscout không key nay trả 403 Cloudflare (4/4 lần), trong khi 06/11 chạy được. Đường Base giờ phụ thuộc key Blockscout free.
- **Còn mở:** key Blockscout cho Base; factory V3/V4 (Ethereum) và Aerodrome/V3 (Base) chưa thử; Solana chưa thử.

## 2026-11-12 [claude] — Key Blockscout; Base mất gói free

- Sinh viên tạo key Blockscout free nhưng dán vào `.env.example` (file không bị gitignore, chưa từng commit). Mình chuyển key sang `.env` (quyền 600, không in ra) và để trống lại `.env.example`.
- Ảnh dashboard của sinh viên + đo thật: từ 2026-10-01 Base không còn trên gói Free của Blockscout (HTTP 402 với key free). Ethereum vẫn chạy qua `api.blockscout.com/1/api`.
- Hệ quả: cả 3 đường đã biết cho lịch sử swap Base (Blockscout, Etherscan V2, RPC công khai) đều không miễn phí. Đây là thay đổi phạm vi chuỗi của PLAN, chờ sinh viên quyết định.
- Thử thêm đường miễn phí cho swap Base (chỉ đọc, vài lần gọi mỗi nguồn): dRPC không key đọc được log lịch sử Base nhưng dải ≤ 100 block; thông báo lỗi gợi ý gói free có tài khoản cho tới 10.000 block, chưa xác minh. Các RPC công khai khác không dùng được (bảng ở MEMORY Mục 4). The Graph là phương án dự phòng, chưa thử. Thêm `DRPC_API_KEY` trống vào `.env.example` và `.env`. Chưa đổi phạm vi chuỗi trong PLAN.
- Helius free: `getTransactionsForAddress` chạy được, lọc theo ngày, khớp 8/8 chữ ký ngày 05/11 của bài thử cũ, nhanh hơn RPC công khai nhiều lần. Lần so đầu mình dùng nhầm mốc 04/11 nên ra 0 trùng; đã sửa và so lại. Cổng Helius 15/11 có dấu hiệu đạt; còn thiếu số credit thực mỗi lần gọi trước khi ước tính cho 100 token.
- Key Helius lần nữa bị dán vào `.env.example`; đã chuyển sang `.env`. Key dRPC chưa có trong `.env`.
- dRPC có key: log lịch sử Base đọc được nhưng chỉ ~100 block/lần, 1,93 lần/giây; lọc nhiều address/topic một lần được. Mình ước tính (chưa chạy thật): danh sách pool cả cửa sổ ~150 ngày ≈ 65.000 lần gọi ≈ 9 giờ; swap của toàn bộ mẫu Base gộp address trong một lần gọi cũng cỡ đó. Khả thi nếu chạy qua đêm, phụ thuộc CU mỗi lần gọi. Đề xuất giữ Base, đổi nguồn swap Base trong PLAN Mục 6 từ Blockscout sang dRPC; chờ sinh viên đồng ý mới sửa PLAN.
- Sinh viên đồng ý sửa PLAN theo số đo: Mục 6 tách 3 cột (Ethereum: Blockscout có key; Base: dRPC; Solana: Helius), Mục 4.2 cập nhật trạng thái danh sách pool, Mục 4.3 thêm ước tính credit Helius, Mục 7 ghi cổng Helius ĐẠT và thay rủi ro Blockscout/RPC Solana. dRPC: 480 CU sau ~34 lần gọi. Không đổi phạm vi chuỗi, cỡ mẫu, T0–T3, H hay target.
- Danh sách token Solana: lọc giao dịch `Migrate` của ví migration pump.fun qua Helius (`status: succeeded`), 375 token tốt nghiệp ngày 2026-06-10, rẻ (≈ 50 credit/ngày). Cổng 15/11 "danh sách token" ĐẠT cho cả 3 chuỗi, hạn chế: chỉ Uniswap V2 (EVM) và pump.fun (Solana). Đã đánh dấu trong PLAN Mục 4.2 và Mục 7.
- Tổng gọi API phiên này (ước): Helius ~70 lần, dRPC ~40 lần (480 CU), Blockscout ~10 lần. Kết quả thử để trong scratchpad, không ghi `data/raw/`.

## 2026-11-12 [claude] — Hoàn thành dòng lịch thiết kế 12–15/11

- **Môi trường:** `pyproject.toml` (pandas, duckdb, pyyaml, requests, tenacity, python-dotenv, networkx; dev: pytest); cài bằng uv vì `.venv` không có pip; `requirements.txt` ghi phiên bản chính xác (pandas 3.1.1, duckdb 2.0.0, pytest 9.2.0…).
- **configs/:** `thresholds.yaml` ghi nguồn từng ngưỡng. Đọc notebook artifact để lấp các chỗ PDF không ghi: rug pull `window_size=3` (ngày sập + 2 ngày, docstring ghi sai "+3"), volume các ngày sau < 1% volume **ngày sập**; RSI `timeperiod=6` (giờ); dump tìm trong 48 giờ; wash screening `abs(volume_pct_change) > 500` và `abs(returns) < 5.0`; LPI có ngoặc đúng, buy_ratio `> 0.90` (PDF ≥). Các chỗ PDF/mã khác nhau giữ cả hai. `split.yaml`, `chains.yaml` (không chứa key).
- **Thiết kế dữ liệu:** `docs/schema.sql` (10 bảng, thêm `samples` và cột truy nguyên), `docs/DATA_CARD.md`.
- **Solana so số dư:** `scripts/solana_balance_diff_pilot.py`, offline. Khớp 8/8 với bộ đọc Raydium trên HEGE (chiều, lượng, trader). Quy tắc: pool = chủ ví giữ nhiều meme nhất; trader = ví khớp đúng lượng ngược dấu, ưu tiên ví ký; không khớp thì `unclear`.
- **Test:** 36 qua (thêm test configs, schema, bộ đọc số dư với dữ liệu giả lập trong `tests/`).
- **Còn mở:** sinh viên duyệt ✋ thiết kế; bộ đọc số dư mới thử 1 pool/1 sàn (cổng 22/11 cần ≥ 20 tx/≥ 2 sàn); factory V3/V4/Aerodrome; giả định "pool = ví giữ nhiều meme nhất" có thể sai khi giao dịch đi qua 2 pool.
- **Sinh viên duyệt DATA_CARD (2026-11-12)** và yêu cầu commit. Mình hiểu là duyệt cả ✋ thiết kế (DATA_CARD + schema + configs đi cùng nhau); nếu sinh viên chỉ duyệt riêng DATA_CARD thì sửa lại dòng này. Bước tiếp: collector, ưu tiên OHLCV đợt 1.
