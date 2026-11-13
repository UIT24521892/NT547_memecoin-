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

## 2026-11-12 [codex] — Bắt đầu collector sớm và bàn giao đợt kiểm thử

- **Yêu cầu:** sau khi đối chiếu PLAN, sinh viên yêu cầu chạy các task rồi đưa kết quả để tự kiểm thử lại. Bắt đầu sớm dòng 16–29/11 sau ✋ thiết kế đã đóng; không đổi lịch/cỡ mẫu/nhóm/T0–T3/H/target. Việc này dùng thời gian dành cho collector; dòng thiết kế 12–15/11 đã hoàn tất. Cổng 15/11 giữ trạng thái đạt; cổng 18/11 chưa đo, 22/11 chưa đủ bằng chứng, 29/11 chưa tới.
- **Triển khai:** `src/memecoin/collect/{common,http,ohlcv,evm,solana,swaps,cli}.py`, entry `scripts/collect.py`. Chỉ GET hoặc RPC trong whitelist chỉ đọc. Cache theo request, raw body nguyên bản và bất biến, metadata che key + SHA-256, retry/backoff cho 429/408/5xx và RPC rate limit; rate limit dùng khóa chung theo provider giữa các tiến trình. Có `--offline`, `--refresh`, giới hạn request/trang/dải, báo phần thiếu và chạy tiếp từ cache. Không ghi key vào code/raw metadata; `.env` giữ nguyên.
- **Nguồn/gói free:** dùng key có sẵn trong `.env`, không in key. Đọc docs OHLCV/Helius và lưu IDL pump.fun/PumpSwap, README + IPoolFactory Aerodrome từ kho chính thức vào raw provider `protocol_docs`. Thêm eth-hash + pycryptodome để tính Keccak-256 đúng chuẩn Ethereum; cập nhật requirements (không đổi dependency cũ). `uv pip freeze` lần đầu lỗi quyền cache làm rỗng file do redirect; đã phục hồi bằng lệnh có `--cache-dir /tmp/nt547-uv-cache`, chỉ ghi sau khi lệnh thành công, kiểm tra diff chỉ thêm 2 dependency.
- **Danh sách lịch sử thật:** Ethereum ngày 10/06: 167 log V2 + 17 log V3 → 177 ứng viên có WETH. Base dải 1.000 block: 20 V2 + 2 V3 → 11 ứng viên; Aerodrome classic dải 5.000 block: 1 log → 1 ứng viên. Base là dải nhỏ, không gọi là cả ngày/cả kỳ. EVM còn phải xác minh token là meme. Collector hiện quét từng factory; ước tính 9 giờ trong PLAN chỉ áp dụng nếu gộp factory, chưa phải tốc độ code hiện tại.
- **Sửa nhận định Solana từ dữ liệu đầy đủ:** 5 trang ngày 10/06 có 375 tx thành công, nhưng chỉ 358 có Migrate/MigrateV2; đọc đúng program/discriminator/account theo IDL và xác nhận CPI CreatePool còn **222 pool mới**. Migrate có thể lặp trên cùng pool, nên không được đếm 375 hay 358 token mới. Collector đã chạy full limit=100 thành công; credit/lần vẫn chưa đo riêng. Đã cập nhật kết quả đo trong PLAN/configs/MEMORY, không đổi chiến lược nguồn pump.fun.
- **OHLCV:** 3 pool smoke PEPE (Ethereum), BRETT (Base), HEGE (Solana), [26/05,12/11) UTC. Mỗi pool 170 nến ngày, không thiếu ngày. Nến giờ lần lượt **4.067/4.077/2.233**, thiếu **13/3/1.847** trên lưới 4.080 giờ/pool. Tổng **10.887 dòng**. Bỏ nến chưa đóng, không tự điền volume 0 khi thiếu nến. Chọn pool từ snapshot hiện tại chỉ để kiểm tra kỹ thuật; không đưa vào `samples`, không gọi là mẫu nghiên cứu.
- **Lỗi phát hiện bằng chạy thật:** Blockscout getblocknobytime trả object `blockNumber`, đã sửa parser; module proxy lấy tx trả 400, chuyển legacy `transaction/gettxinfo` thành công. GeckoTerminal trả trang ít hơn 1.000 nến vẫn còn lịch sử: sửa tiếp tục phân trang đến start/trang rỗng, HEGE từ 665 lên 2.233 nến giờ. dRPC có 408, bổ sung retry; raw lỗi giữ nguyên. Khi max-chunks giới hạn, cache không ăn ngân sách dải mới để lần chạy sau tiến xa hơn.
- **Swap:** giải mã **2/2 log PEPE V2 + 8/8 log BRETT Slipstream theo ABI Swap V3**, giữ lượng raw nguyên chính xác, trader=`tx.from`, `amount_usd=NULL` vì chưa quy đổi quote USD. Flash swap phức tạp chưa hỗ trợ thì báo unresolved. Helius HEGE ngày 05/11 lấy đủ 8 tx, signature khớp **8/8** với public RPC pilot; đây là inventory, chưa phải bộ đọc swap Solana chuẩn hóa hay manual validation.
- **Đầu ra/EDA:** `data/interim/collector_check/` có CSV/JSON/Parquet/DuckDB/report và link explorer; raw dưới `data/raw/2026-11-12/`. Notebook `notebooks/01_collection_quality.ipynb` kiểm tra độ phủ, khóa, NULL và provenance; tất cả code cell đã chạy. Không đếm outcome trên test, không train/evaluate model.
- **Kiểm chứng:** **56 test + 12 subtest qua**. `scripts/check_collection.py` chạy lại **10 tình huống offline**, bỏ key khỏi môi trường và CLI không đọc `.env`: 0 request mạng, CSV giống từng byte, CSV/Parquet/DuckDB đều 10.887 dòng, 0 khác biệt DB–Parquet; Solana khớp 8/8 signature. SHA-256 CSV OHLCV: `2b7ca9500fc4920d87db5a893f92ca0381a517b333a70c85b6b9d03377a3ce35`. Raw mới kiểm tra được 157 metadata HTTP: GeckoTerminal 31, Blockscout 9, dRPC 105, Helius 7, protocol_docs 5; gồm 14 HTTP 429, 7 HTTP 408, 3 HTTP 400. Không phải số credit/CU; không tính hai lần probe GeckoTerminal đầu phiên ngoài client.
- **Bàn giao:** `README.md`, `docs/COLLECTOR_RUNBOOK.md`, lệnh `.venv/bin/python -m pytest` và `.venv/bin/python scripts/check_collection.py`. Chưa commit/push. Chưa hoàn tất thu 300 token, nhãn/cổng 18/11, bộ đọc Solana ≥20 tx/≥2 sàn/≥30 token, holder/liquidity/creator, giá USD swap, hoặc dữ liệu đợt 2 sau 23/11. Đã đánh dấu collector đang làm trong PLAN Mục 8; chưa đóng ✋ thu dữ liệu.

## 2026-11-12 [codex → claude] — Task 1: gộp truy vấn Base, khép sau khi Codex hết lượt

- **Yêu cầu:** sinh viên chọn ưu tiên task 1 trong 5 task Codex đề xuất (1 gộp Base, 2 danh sách token/pool toàn kỳ, 3 swap Solana sàn thứ hai, 4 giá USD swap EVM, 5 thanh khoản/Transfer/creator). Thuộc dòng collector 16–29/11 làm sớm; không đổi tham số PLAN.
- **Codex làm:** `discover` Base gộp V2/V3/Aerodrome classic trong một `eth_getLogs` (OR tại `topic0`, kiểm tra đúng cặp factory/event trước khi giải mã); baseline `--separate-factories`; bài đo `scripts/benchmark_base_batching.py` (online/offline). Số đo 1.000 block: 3 factory cùng 23 log/12 ứng viên, HTTP 30 → 10, 16,325 → 5,278 giây; 2 pool cùng 77 log, HTTP 27 → 10 (baseline có 7 lần 429 nên mức giảm thời gian không phải tốc độ cố định). Resume: 3 cache hit + 7 request mới. Chi tiết `docs/BASE_BATCHING.md`.
- **Subagent (sinh viên cho phép):** audit số đo xong, không thấy sai khác (87 raw khớp SHA-256). Viết hướng dẫn xong. Review code bị ngắt khi Codex hết lượt, nhưng đã thử ra lỗi đọc pointer cache trong lúc tiến trình khác ghi đè → `JSONDecodeError`.
- **Claude khép task 1:** đọc log phiên Codex (`~/.codex/sessions/2026/11/12/`), sửa `write_json`/`write_csv` thành ghi nguyên tử (file tạm + `os.replace`), thêm 3 test. Pytest 68 + 12 subtest qua; hai bài replay offline PASS, 0 request mạng, đầu ra giống byte.
- **Còn mở:** chưa đo CU dRPC khi gộp; chưa thử gộp hàng trăm pool hoặc toàn cửa sổ 150 ngày; test đồng thời mới là 2 luồng/1 tiến trình. Việc kế tiếp: task 2.

## 2026-11-12 [claude] — Task 2: danh sách ứng viên 3 chuỗi và bắt đầu sàng lọc A/B

- **Làm gì:** thuộc dòng collector 16–29/11 (làm sớm). Viết `src/memecoin/collect/window.py` (tầng ngày tạo, chọn ngày, tìm block Base bằng nội suy, gộp/khử trùng, kiểm tra token mới), `src/memecoin/model/sampling.py` (cutoff, nhóm A, phân bổ quota), lệnh `discover-window`, `scripts/pilot_funnel.py`, `scripts/screen_sample.py`. Test 2 file mới; toàn bộ test qua; replay cũ vẫn PASS.
- **Sinh viên quyết định:** (1) Base quét 20 ngày ngẫu nhiên thay vì toàn kỳ; (2) thêm Uniswap V4 vào ứng viên; (3) phân bổ A/B theo số ngày cutoff (18/9/13); (4) trần sàng lọc 5.000 pool/chuỗi, thiếu A thì báo số thật, không nới ngưỡng.
- **Mình tự chọn (đề xuất, ghi trong `split.yaml`):** đệm 7 ngày cho tầng ngày tạo; "ngày giao dịch đầy đủ" = nến sau ngày tạo có volume > 0; token mới EVM = contract tạo ≤ 7 ngày trước pool; B có thể chứa token đạt A; mỗi token xét 1 pool gặp trước theo thứ tự ngẫu nhiên.
- **Số đo V4 (10/06):** Base 240 `Initialize` trong 1.000 block (111 ghép WETH) so với 12 ứng viên V2/V3/Aerodrome; Ethereum 376/ngày (167 ghép ETH gốc). GeckoTerminal tra được PoolId. Địa chỉ PoolManager và chữ ký event lấy từ docs/v4-core chính thức ngày 12/11.
- **Kết quả quét:** Ethereum 98/98 ngày, 40.151 pool (V4 19.720), 442 lần gọi. Solana 98/98 ngày, 74.094 pool, 1.222 lần gọi; migration/ngày tăng từ ~220 (tháng 6) lên ~750–1.000 (tháng 8–10), chưa rõ nguyên nhân. Base: đang chạy, dRPC free trả 429 ("free plan rate limit"), runner nghỉ 60 giây rồi chạy tiếp từ cache.
- **Pilot phễu:** có cutoff Ethereum 3/30, Base 0/30, Solana 26/30; đạt A Solana 1/23. Danh sách EVM phần lớn là pool không giao dịch → phải sàng lọc tuần tự.
- **Lỗi bắt được bằng test:** trường `full_days_seen` đếm cả ngày sau cutoff (rò rỉ tương lai) → sửa chỉ đếm tới cutoff.
- **Còn mở:** kết quả quét Base và sàng lọc 3 chuỗi; tỷ lệ ca dương cho cổng 18/11; đọc swap V4; token nào "mới" trên Solana ngoài pump.fun.

## 2026-11-12 [claude] — Đo sơ bộ cổng 18/11 trên Solana (offline)

- **Làm gì:** sinh viên yêu cầu đo ngay. Viết `scripts/measure_positive_rate.py`: chỉ nhận cutoff train/validation (gặp test thì dừng), chỉ dùng nến trong (cutoff, cutoff+30]; tính sụp giá 70/80/90%, rug pull theo `thresholds.yaml`, số ngày im lặng cuối cửa sổ. Đầu ra `data/interim/task2/gate_1811/solana/`. Dữ liệu: nến ngày GeckoTerminal thu 2026-11-12, mới sàng lọc 250/5.000 pool Solana (đang chạy). EVM chưa có.
- **Số liệu (A+B đã chọn, n=28: 27 B + 1 A):** sụp ≥80% = 3/28 (10,7%); 70% và 90% cho cùng số. Rug pull theo rule paper = 0. Im lặng cuối cửa sổ ≥7 ngày = 6. Trung vị 13/30 ngày có nến. Tất cả token đủ điều kiện đã sàng lọc (n=52): 4/52.
- **Phát hiện quan trọng:** 89% token đã chọn **đã giảm ≥80% so với đỉnh TRƯỚC cutoff**; trung vị ngày đầu close/open = −84%; volume trung vị ngày đầu ≈ $170k, tuần trước cutoff ≈ $460/ngày. Tức token Solana (tốt nghiệp pump.fun) sụp ngay sau migration, còn cutoff (≥7 ngày giao dịch) rơi sau cú sụp → target đo biến động của token đã chết. Lọc "còn hoạt động tại cutoff" (volume TB 7 ngày trước cutoff, dữ liệu ≤ cutoff): ≥$100 → 4/31; ≥$1.000 → 4/18; ≥$10.000 → 4/12.
- **Trạng thái cổng:** theo chữ là 10,7% ∈ [5%, 50%] nhưng về ý nghĩa target chưa phân biệt được gì; mẫu nhỏ, mới 1 chuỗi. **Chưa đổi gì**; đã báo sinh viên kèm phương án, chờ quyết định. Ghi chú: `stop_reason=candidates_exhausted` trong `progress.json` khi đang chạy chỉ là giá trị khởi tạo, không phải lỗi.

### 2026-11-12 (tối) [claude] — Base quét xong; số sơ bộ sàng lọc Solana

- **Base:** 20/20 ngày (train 9 / val 5 / test 6), 58.890 pool, 55.729 token; train 36.629, val 7.105, test 15.156. V4 48.522 (82%), V2 8.260, V3 2.108, Aerodrome classic 128. dRPC 8.990 request, 2.058 cache hit. Số theo tầng là của **ngày được chọn**, chưa nhân nghịch đảo `day_sampled_fraction`.
- **Sàng lọc Solana, sau 375 pool (sơ bộ, chưa phải kết quả cuối):** 373/375 có trên GeckoTerminal; 202 không có cutoff (chưa đủ 7 ngày giao dịch), 35 rơi vào khoảng đệm, 18 ngoài cửa sổ; 120 có cutoff trong một tập (32%). B đủ 40 sau chưa tới 375 pool. Chỉ **2/120** đạt tiêu chí A (×2 từ ngày đầy đủ đầu tới cutoff) → dự kiến A Solana thiếu xa 40 dù chạy hết trần 5.000 (ước tính thô ~25, chia theo tập còn ít hơn). Theo quyết định của sinh viên: báo số thật, không nới ngưỡng.
- **Đo trước cho cổng 18/11 (Solana, chỉ train + val, n = 69 token có nến sau cutoff):** sụp ≥ 80% trong 30 ngày: train 3/41, val 2/28 → 7,2% (trong khoảng 5–50% nhưng sát biên dưới). Độ nhạy: ≥ 70% → 6/69; ≥ 90% → 3/69. Trung vị min(close sau cutoff)/close cutoff = 0,893. 3 token không có nến nào sau cutoff (có thể đã ngừng giao dịch: thiếu nến có thể che một cú sụp, cần xử lý khi gán nhãn rug).
- **Giải thích khả dĩ (giả thuyết, chưa kiểm):** cutoff = ngày giao dịch đầy đủ thứ 7, nên mẫu chỉ gồm token đã sống qua tuần đầu; token chết sớm nhất bị loại trước cutoff. Đây là hệ quả của thiết kế cutoff, không phải lỗi thu dữ liệu; cần ghi vào hạn chế/thảo luận.
- Base sàng lọc được xếp hàng sau Solana → Ethereum (GeckoTerminal 10 lần/phút dùng chung).

## 2026-11-13 [claude] — Cài skill viết paper, dàn ý báo cáo

- **Yêu cầu:** sinh viên đưa skill https://github.com/Master-cai/Research-Paper-Writing-Skills để áp dụng viết paper. Việc thuộc dòng 14–25/12; làm sớm phần nhỏ (cài + hướng dẫn + dàn ý), lấy khoảng 1 giờ của dòng collector 16–29/11. Không viết văn xuôi kết quả vì chưa có số đo.
- **Làm gì:** chép nguyên skill (MIT, commit `77e7c2c`) vào `.claude/skills/research-paper-writing/` kèm `LICENSE`, `SOURCE.md`; đã đọc toàn bộ file trước khi chép (chỉ là markdown + 1 yaml, không có lệnh chạy). Viết `docs/WRITING_GUIDE.md` (điều chỉnh skill ML/CV sang paper đo lường/bảo mật: không có SOTA → so baseline giá tăng và số paper; ablation theo 5 nhóm feature; bắt buộc thêm Limitations/Ethics; cột Evidence phải ghi script, nguồn, ngày thu, chuỗi, khoảng thời gian). Tạo `report/OUTLINE.md` (story, 9 mục, claim–evidence map C1–C7 đều `needs evidence`). Thêm con trỏ trong CLAUDE.md và AGENTS.md Mục 13.
- **Không đổi tham số PLAN.** Cổng 18/11 vẫn chờ sinh viên chọn phương án về token Solana đã chết trước cutoff.

## 2026-11-13 [claude] — Sinh viên chọn phương án (a): chỉ nhận token còn hoạt động tại cutoff

- **Quyết định (sinh viên, 13/11):** phương án (a) cho vấn đề token Solana đã sụp trước cutoff. Đổi tham số PLAN Mục 4.1 (ghi "Sửa 13/11"). Không đổi H, T0–T3, ngưỡng 80%, cỡ mẫu.
- **Định nghĩa (mình chọn, đề xuất):** volume USD trung bình 7 ngày lịch [cutoff−6, cutoff], ngày không có nến tính 0, ngưỡng $1.000. Giữ đúng định nghĩa đã trình cho sinh viên hôm 12/11 (tái tạo lại đúng 31/18/12 token với $100/$1.000/$10.000). Ngưỡng neo theo mốc "volume < $1.000" của LPI trong paper (§5.3.1, tr. 3941), không chọn theo nhãn. Cách khác "trung bình ngày đầy đủ thứ 2–7" (bỏ ngày đầy đủ đầu tiên) cho số gần như nhau (33/15/10), nên không đổi. Áp cho cả 3 chuỗi, cả A và B.
- **Code:** `split.yaml` thêm `active_window_days`, `active_min_mean_volume_usd`; `sampling.py` thêm `active_volume()` và 2 trường `active_volume_usd`, `active`; `screen_sample.py` chỉ chọn token có `active`. Thêm 2 test (dương/âm, ngày thiếu nến, chống rò rỉ). **83 test + 12 subtest qua.**
- **Chạy lại Solana:** dừng tiến trình cũ (675 pool, PID 94509), lưu bản cũ ở `data/interim/task2/screening/solana_before_active_filter_2026-11-13/`, chạy lại từ cache (log `screen_solana_active.log`), đang tiếp tục tìm A tới trần 5.000.
- **Phễu trên 675 pool đầu (offline):** có cutoff trong một tập 212 → còn hoạt động 68 (32%); train 35/73, val 17/60, test 16/79. Cả 6 token đạt A đều còn hoạt động. B đủ 40 sau 500 pool. A vẫn rất thiếu (4 sau 675 pool), như trước.
- **Đo lại sơ bộ cổng 18/11 (Solana, A+B train+val, n=28):** sụp ≥80% = **6/28 (21%)**, trước bộ lọc 3/28; ≥70% 7/28; ≥90% 3/28; rug theo rule paper 0; trung vị 18,5/30 ngày có nến (trước 13). Đầu ra `data/interim/task2/gate_1811/solana_active_2026-11-13/`. Mẫu nhỏ, mới 1 chuỗi; cổng 18/11 chính thức vẫn cần Ethereum + Base.
- **Còn mở:** sàng lọc Ethereum/Base (sẽ tự dùng bộ lọc mới); độ nhạy $100/$10.000 khi đủ mẫu; báo cáo tỷ lệ token bị loại theo chuỗi như phát hiện mô tả.
- **Bằng chứng bộ lọc có ích (13/11, Solana, 99 token đủ điều kiện train+val trong 675 pool đầu):** 62 token không còn hoạt động có **0** ca sụp ≥80%; 37 token còn hoạt động có 7. Không lọc thì chỉ riêng "token đã chết chưa" đã tách được phần lớn ca âm, mô hình sẽ học điều đó thay vì dấu hiệu thao túng. Mẫu đã chọn n=28: 3/28 (KTC 95% Wilson 3,7–27,2%) → 6/28 (10,2–39,5%); hai khoảng chồng nhau nên chưa nói được tỷ lệ "thật" khác nhau. Chưa biết bộ lọc làm mô hình dự báo tốt hơn hay không; chỉ biết sau giai đoạn model, không đánh giá trên test.

## 2026-11-13 [claude] — Chạy sàng lọc Ethereum và Base song song với Solana

- **Quyết định (sinh viên, 13/11):** chạy sàng lọc Ethereum và Base song song với Solana. Rate limit dùng chung giữa các tiến trình, nên chạy song song không vượt giới hạn, chỉ chia nhau quota 10 lần/phút. Lợi ích: Ethereum và Base có mẫu A/B sớm cho cổng 18/11, không phải chờ Solana chạy hết trần 5.000 pool. Đổi lại, phần tìm nhóm A của Solana chậm hơn (B Solana đã đủ 40 sau 500 pool; chỉ còn tìm A, A=4 sau 750 pool), việc này không gấp bằng cổng 18/11. Thuộc dòng collector 16–29/11; không đổi tham số PLAN.
- **Kiểm tra trước khi chạy:** `HttpClient._pace` (`src/memecoin/collect/http.py`) khoá file `data/interim/http_cache/<provider>/.rate.lock` bằng `fcntl.flock` → mọi tiến trình cùng provider chia chung một nhịp. Đầu ra mỗi chuỗi ở thư mục riêng (`data/interim/task2/screening/<chain>/`), không ghi đè nhau. Ethereum/Base kiểm tra token mới qua Blockscout/dRPC (provider khác, không ăn quota GeckoTerminal).
- **Đã chạy:** ~13:55 (+07) PID 29087 Ethereum, 29088 Base, cùng PID 25584 Solana (chạy từ 13:39). Log `data/interim/task2/screen_{ethereum,base,solana}_active.log`. 3 phút đầu: 33 request GeckoTerminal, 31 dRPC, 15 Blockscout mới. Ethereum tiếp tục từ 50 pool đã có cache.
- **Ước tính thô (chưa đo):** mỗi chuỗi còn ~3,3 lần gọi GeckoTerminal/phút. Pilot 12/11: có cutoff Ethereum 3/30, Base 0/30; sau bộ lọc còn hoạt động (~1/3 ở Solana) có thể cần > 1.000 pool/chuỗi cho 40 B, tức nhiều giờ. Sẽ báo số thật khi có.
- **Còn mở:** theo dõi tiến độ; nếu EVM quá chậm trước 18/11, cân nhắc tạm dừng Solana (chỉ đang tìm A) để dồn quota — cần sinh viên đồng ý.
- **13/11 14:05 (giờ máy):** tiến trình sàng lọc Solana của Claude bị dừng (SIGTERM, mã 143). Cùng lúc có 3 tiến trình mới `screen_sample.py --chain solana|ethereum|base` chạy song song, không do Claude khởi động (có thể là sinh viên hoặc Codex), log `data/interim/task2/screen_{chain}_active.log`. Cả ba dùng code đã có bộ lọc còn hoạt động (cột `active` có trong `screened.csv`). Solana đọc lại từ cache rồi chạy tiếp. Claude không can thiệp.
- **Thử 20 lần/phút (sinh viên yêu cầu, 13/11):** đo mốc 10/phút (07:00–07:05 UTC): 55 lần, 9,85/phút, 0 lần 429. Đổi `chains.yaml` lên 20, chạy lại 3 tiến trình từ cache; đo 07:06–07:15 UTC: 180 lần = 20,0/phút nhưng **89 lần HTTP 429**, chỉ 91 lần thành công = **10,1/phút**. Giới hạn thật của GeckoTerminal free (theo IP) vẫn khoảng 10/phút; con số 30/phút trong FAQ (2026-10-01) không đúng với hiện tại. Đã trả về 10/phút (PID mới chạy từ ~07:16 UTC) để tránh bị chặn lâu. Không có lỗi trong log, không mất dữ liệu (raw 429 vẫn được lưu nguyên).
- **Tiến độ lúc 07:15 UTC:** Solana 825 pool, B=40, A=4; Ethereum 105 pool, B=0, A=0; Base 76 pool, B=0, A=0. EVM chưa có token đủ điều kiện nào → rủi ro cao cho cổng 18/11.

## 2026-11-13 [claude] — Bộ lọc trước bằng log Swap cho Ethereum

- **Yêu cầu (sinh viên):** tăng tốc sàng lọc mà vẫn ngẫu nhiên. Sinh viên hỏi có thể chọn pool bằng tay không → không: phá ngẫu nhiên của B, dễ nhìn thấy thông tin sau cutoff, không tái tạo được. Làm bộ lọc tự động. Lấy khoảng nửa ngày của dòng collector 16–29/11; không đổi tham số PLAN.
- **Cách làm:** `src/memecoin/collect/activity.py` đếm ngày UTC có log Swap (V2/V3 theo địa chỉ pool; V4 theo PoolManager + PoolId ở topic1) trong (ngày tạo, cutoff_end muộn nhất = 2026-10-23] qua Blockscout, dừng ngay khi đủ 7 ngày. < 7 ngày thì chắc chắn không có cutoff trong tập nào → bỏ qua GeckoTerminal. Lỗi/không chắc → vẫn hỏi GeckoTerminal. Thứ tự ngẫu nhiên giữ nguyên; pool bị loại vẫn tính vào trần 5.000 nên tập được chọn giống hệt khi không lọc. Bật bằng `split.yaml` `sampling.prefilter_swap_days_chains: [ethereum]`; tắt bằng `--no-prefilter`.
- **Xác minh nguồn:** v4-core `PoolManager._swap` luôn `emit Swap` (không nằm trong nhánh điều kiện), kể cả pool có hooks; chữ ký `Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)` (đọc từ GitHub Uniswap/v4-core main, 2026-11-13).
- **Lỗi bắt được khi chạy thật:** Blockscout bắt buộc `topic0_1_opr` khi lọc 2 topic (trả status=0) → sửa `EvmReader.get_logs` thêm toán tử `and`. Script kiểm chứng ban đầu định nghĩa "loại nhầm" sai (12 pool V3 có cutoff 2026-10-24, ngoài mọi tập) → sửa thành "có cutoff trong train/validation/test".
- **Kiểm chứng (`scripts/validate_prefilter.py`, 175 pool Ethereum đã có nến GeckoTerminal, ảnh chụp `data/interim/task2/prefilter_validation/ethereum/`):** **0 loại nhầm**; 167 bị loại (không pool nào có cutoff trong tập); 8 giữ lại gồm cả 6/6 pool có cutoff trong tập. Mẫu kiểm chứng chỉ có 6 ca dương, nhưng quy tắc đúng về logic (nến GeckoTerminal dựng từ chính các swap). 8 test mới (dương/âm, ngày tạo, ngoài cửa sổ, chia trang, không chắc thì không loại, UTC). **91 test qua**; `check_collection.py` replay PASS, 0 request mạng.
- **Tốc độ:** khởi động lại Ethereum (PID 40003) lúc ~07:43 UTC: 125 pool mới trong 126 giây ≈ 60 pool/phút, so với ~3,3 pool/phút trước đó. Sau 300 pool: lọc trước giữ 9 (3%), B=0, A=0.
- **Base chưa lọc trước:** dRPC chỉ 100 block/lần nên đếm theo từng pool cần hàng trăm lần gọi/ngày/pool, không khả thi. Phương án còn lại (quét toàn bộ log Swap Base theo ngày, ~65.000 lần gọi ≈ 9,5 giờ) chưa làm.
- **Rủi ro:** tỷ lệ đủ điều kiện Ethereum có thể chỉ ~1% (ước tính thô) → hết trần 5.000 pool vẫn có thể thiếu B. Sẽ báo số thật.

## 2026-11-13 [claude] — Chi phí credit Blockscout thật và hướng xử lý thiếu mẫu

- **Đo (dashboard Blockscout do sinh viên chụp ~08:05 UTC):** hôm nay 2.298 lần gọi = 45.740 credit, tức **~20 credit/lần** (getLogs, getcontractcreation, getblocknobytime đều 20). Gói free 100.000 credit/ngày ⇒ chỉ **~5.000 lần gọi/ngày**, không phải 100.000 lần như đã ngầm hiểu.
- **Hệ quả:** sàng lọc Ethereum tốn ~2 lần gọi mạng/pool (đo 875→925 pool: 101 lần) ≈ 40 credit/pool ⇒ ~2.500 pool/ngày. Hết trần 5.000 pool cần ~2 ngày quota; nâng lên 10.000 cần ~4 ngày.
- **Sửa code:** `screen_sample.py` trước đây gặp lỗi khi kiểm tra tuổi token thì bỏ qua token đó; hết credit sẽ làm bỏ qua hàng loạt và đổi mẫu. Nay gặp `CollectionError` ở bước này thì dừng với `stop_reason=evm_error`; lỗi không được cache nên chạy lại là tiếp tục. 91 test qua. Khởi động lại Ethereum (PID 44781).
- **Số đo 08:05 UTC:** Ethereum 925 pool, B=6 (train 3, validation 0, test 3), 21+ token có cutoff trong tập nhưng phần lớn không còn hoạt động. Base 175 pool, B=1. Solana 975 pool, B=40 (đủ), A=4.
- **Đã đề xuất, chờ sinh viên quyết định:** (1) tạm dừng Solana để Base dùng hạn mức GeckoTerminal; (2) nâng trần riêng Ethereum lên 10.000 pool (tham số PLAN).
- **Còn mở:** cách giảm credit/pool (gộp nhiều địa chỉ trong một lần `getcontractcreation`, hoặc nguồn khác cho Ethereum) chưa kiểm chứng.

## 2026-11-13 [claude] — Nâng trần sàng lọc Ethereum lên 10.000 pool + hỏi tuổi token theo lô

- **Quyết định (sinh viên đồng ý 13/11):** trần riêng Ethereum 10.000 pool (`split.yaml` → `screening_budget_pools_by_chain`), các chuỗi khác giữ 5.000. Lý do: sau 925 pool chỉ ~0,7% token đủ điều kiện, dự kiến thiếu B ở 5.000. Đi tiếp cùng thứ tự xáo nên 5.000 pool đầu cho kết quả y như trước. Đã sửa PLAN Mục 4.1.
- **Tiết kiệm credit:** Blockscout `getcontractcreation` nhận nhiều địa chỉ/lần (thử thật: 5 và 10 đều trả đủ). `EvmReader.prefetch_contract_creations` hỏi 10 token kế tiếp theo thứ tự xáo trong một lần (`chains.yaml` → `creation_batch_size: 10`). Kết quả từng token không đổi; chỉ giảm số lần gọi (~20 credit/lần).
- **Kiểm tra:** thêm test lô = tra từng địa chỉ; 92 test qua. Chạy lại (PID 45618): 105 dòng đầu khớp 105/105 với ảnh chụp trước đó (order, token_new, prefilter, split, selected_group). Lần chạy lại tốn thêm ~110 lần gọi vì khoá cache của lô khác khoá cũ.
- **Ước tính:** ~1,1 lần gọi/pool cho tuổi token + ~1–2 cho lọc trước ⇒ ~3.000–4.000 pool/ngày quota; 10.000 pool xong khoảng 15–16/11 nếu tỷ lệ giữ nguyên (chưa đo).

## 2026-11-13 [claude] — Tạm dừng sàng lọc Solana để ưu tiên Base

- **Quyết định (sinh viên, 13/11 ~08:20 UTC):** dừng tiến trình Solana (PID 34187) để Base dùng gần trọn hạn mức GeckoTerminal ~10 lần/phút. Lý do: Solana đã đủ B 40/40 (train 18, validation 9, test 13) cho cổng 18/11; phần còn lại chỉ là tìm A (đang 4/40 sau 1.025 pool), không gấp. Base mới B=1 sau ~175 pool.
- **Chạy tiếp Solana sau:** cùng lệnh `screen_sample.py --chain solana`, đọc lại cache, đi tiếp đúng thứ tự xáo.
