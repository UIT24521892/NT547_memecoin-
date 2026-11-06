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
