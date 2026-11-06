# MEMORY.md — Bộ nhớ dự án dùng chung (Codex + Claude Code)

> Đọc file này đầu mỗi phiên, cập nhật cuối mỗi phiên. Giữ ngắn (< 150 dòng). Chi tiết dài → `docs/`, ở đây chỉ để link.
> Quy ước: ghi **ngày** (YYYY-MM-DD) và **ai ghi** (codex/claude/sinh viên) ở mỗi dòng quan trọng. Dòng sai thì xoá, không để lại cho đúng sai lẫn lộn.

## 1. Giai đoạn hiện tại

- Cuối Tuần 1 — Đọc paper + học nền A–B. Chưa viết code. (cập nhật: 2026-11-06 claude)
- Trạng thái ✋: chưa có gì được duyệt. `READING_GUIDE`, `LEARNING_ROADMAP`, `PAPER_NOTES_MAIN` đang chờ sinh viên duyệt.

**Việc tiếp theo, chưa viết code thu dữ liệu:**

1. Sinh viên chốt: ngày nộp cụ thể, mẫu báo cáo (Mục 2).
2. Tạo `docs/PLAN.md` (phạm vi, RQ, chuỗi, cỡ mẫu, T0–T3, H, rủi ro + phương án dự phòng); co kế hoạch 10 tuần cho kịp tháng 12.
3. **Dừng ở ✋** Tuần 1 chờ duyệt, rồi mới sang DATA_CARD/schema (Tuần 2).

## 2. Thông tin sinh viên / nhóm (điền khi biết)

| Mục | Giá trị |
|---|---|
| Hạn nộp | Tháng 12/2026; ngày cụ thể ❓ (sinh viên, 2026-11-06) |
| Số thành viên | 3 (sinh viên, 2026-11-06) |
| Chuỗi ưu tiên (Base / BSC / Solana…) | **Base và Ethereum** (sinh viên chốt, 2026-11-06) |
| Có Dune key? | ❓ (không bắt buộc, xem Mục 4) |
| Có Etherscan key? | ❓ (không bắt buộc nếu dùng Base + Blockscout, xem Mục 4) |
| Yêu cầu định dạng báo cáo của giảng viên | Dạng bài báo nghiên cứu khoa học, viết bằng **tiếng Anh** (sinh viên, 2026-11-06); mẫu cụ thể (IEEE/ACM…) ❓ |
| Công cụ đang dùng | Codex + Claude Code |

## 3. Quyết định đã chốt

- 2026-11-06 [sinh viên] Chọn 2 chuỗi Base và Ethereum. Lý do: cả hai đọc được lịch sử swap miễn phí qua Blockscout và dùng chung code EVM; BSC chưa thấy đường miễn phí, Solana quá rủi ro với hạn tháng 12.
- 2026-11-06 [sinh viên] Báo cáo cuối viết bằng tiếng Anh theo dạng bài báo. `docs/` nội bộ và code comment vẫn tiếng Việt (CLAUDE.md Mục 3).

Tham số cốt lõi chờ chốt (ghi vào đây khi có, nguồn thật là `configs/`):

- T0 / T1 / T2 / T3: ❓
- H (số ngày nhìn trước cho nhãn): ❓ (mặc định 14 hoặc 30, ghi lý do)
- Cỡ mẫu mục tiêu: 150–400 token

## 4. Đã kiểm chứng (ghi kèm ngày để biết khi nào cũ)

**Ngưỡng paper (2026-10-01, codex):** đối chiếu ảnh PDF 9/10/12/13 (trang in 3938/3939/3941/3942); các con số khớp. Sửa AGENTS.md cho rõ volume trung bình sau dump và các chi tiết **chưa xác minh PDF** (mẫu số/dấu 2%, cửa sổ rug/RSI/dump). Xem `docs/THRESHOLD_AUDIT.md`.

**Nguồn dữ liệu (2026-10-01, codex):** kiểm tra docs chính thức và schema/HTML công khai; chưa thử endpoint thị trường với key/tài khoản. Nguồn và bằng chứng: `docs/references/API_DOC_EVIDENCE_2026-10-01.md`; chi tiết sẽ nằm trong PLAN.

| Nguồn | Ngày kiểm tra | Kết luận |
|---|---|---|
| GeckoTerminal | 2026-10-01 [codex] | Swagger ~10/phút, FAQ 30/phút: mâu thuẫn; đề xuất ≤10. Tối đa 1.000 nến/request; trades 300/24h. Lookback free toàn phần **chưa xác minh** |
| DexScreener | 2026-10-01 [codex] | Lookup pair 300/phút, profiles 60/phút; snapshot hiện tại, không thấy lịch sử swap/OHLCV trong reference |
| Dune | 2026-10-01 [codex] | Billing/rate docs: free view-only, API cần trial/paid; FAQ cũ còn free 40/phút, mâu thuẫn. Credit/entitlement tài khoản **chưa xác minh** |
| Etherscan V2 | 2026-10-01 [codex] | Free 3/s, 100.000/ngày; Ethereum free, Base/BSC paid cho dữ liệu thông thường; source/ABI là ngoại lệ free. Transfers/logs free tối đa 1.000 dòng từ 2026-07-01 |
| RPC công khai | 2026-10-01 [codex] | BSC docs 10K/5min nhưng eth_getLogs tắt trên mainnet liệt kê. Base endpoint xác nhận; quota/block range/lịch sử **chưa xác minh**. Solana 100/10s/IP, 40/10s/method, có thể đổi |
| GoPlus | 2026-10-01 [codex] | Free 30/phút, token_security có ETH/BSC/Base; không xác nhận API lịch sử as-of; không dùng snapshot hiện tại làm feature quá khứ |
| CoinGecko API công khai | 2026-10-16 [claude] | Không key: 429 sau ~7 lần gọi liên tiếp; cách 20 giây thì ổn. `market_chart/range` trả nến ngày cho > 90 ngày. Category `meme-token` có cả PUMP và M (không phải meme cổ điển) |
| GeckoTerminal `tokens/{addr}/info` | 2026-10-16 [claude] | Có trường `holders` (số holder + % top-10/…; nhóm bucket khác nhau giữa EVM và Solana) và `mint/freeze_authority`. Là snapshot hiện tại → **không** dùng làm feature quá khứ. 429 khi gọi cách 8 giây |
| Solana RPC công khai / BscScan web | 2026-10-16 [claude] | RPC công khai trả 429 ngay lần gọi `getTokenSupply` đầu tiên; trang BscScan chặn fetch tự động (403). Trang holder của Etherscan đọc được |
| Zenodo (paper) | 2026-10-01 [codex] | Metadata open, CC-BY-4.0; DOI concept 17830943, v1 17830944. Artifact đọc được; nhãn rule không phải manual ground truth |
| Blockscout Base | 2026-11-06 [claude] | Thử không key: 25/25 lời gọi HTTP 200. Log Swap về tới ngày tạo pool (2025-03-07), có `tx.from`, creator, tx tạo contract; getLogs tối đa 1.000 dòng/lần. Docs + blog: API cũ không key đã lên lịch bỏ từ 2026-07-01, key free 5 req/s, 100K credit/ngày; giá credit mỗi lời gọi **chưa xác minh**. Mới thử 1 pool |
| Blockscout khác | 2026-11-06 [claude] | `eth.blockscout.com`: log pool PEPE/WETH 6 tháng trước OK. `bsc.blockscout.com`: 404 |
| RPC công khai (đo thử) | 2026-11-06 [claude] | `mainnet.base.org`, `bsc-dataseed`: từ chối mọi `eth_getLogs`. PublicNode (Base/BSC/ETH): bắt buộc lọc địa chỉ, chỉ dữ liệu gần đây; dữ liệu cũ đòi token |
| GeckoTerminal OHLCV (đo thử) | 2026-11-06 [claude] | 1 pool Base tạo 03/2025, `limit=1000`: chỉ trả 184 nến ngày (2026-05-07 → 2026-11-06), nghĩa là lookback free khoảng 6 tháng; chưa thử `before_timestamp` |
| Dune (đọc lại docs) | 2026-11-06 [claude] | Free chỉ xem; không chạy query, không API, không export. Trial 14 ngày, 2.500 credit. Analyst $75/tháng, 4.000 credit |
| Etherscan (đọc lại docs) | 2026-11-06 [claude] | Bảng chuỗi: Ethereum free, Base/BSC không free. Khớp ghi chú 2026-10-01 |
| Helius (chỉ đọc docs) | 2026-11-06 [claude] | Free 1M credit/tháng, 10 req/s; độ sâu lịch sử của gói free **chưa xác minh** |

**Tài liệu & công cụ (2026-10-01, claude):** đã tải 9/11 tài liệu vào `docs/references/papers/` (thiếu Kamps & Kleinberg, Le Pennec: cần tải tay, xem `docs/references/README.md`); dataset Zenodo đã giải nén ở `docs/references/dataset/`. PDF đã chuyển sang `docs/references/markdown/` bằng `scripts/pdf_to_md.py` (pymupdf4llm; markitdown 0.1.8 cài làm dự phòng). Venv Python 3.11 ở `.venv/` (gitignore).

## 5. Câu hỏi còn mở

- Sinh viên còn phải chốt: ngày nộp cụ thể, mẫu báo cáo. Xem bảng ở Mục 2.
- Base và Ethereum đều ít ca dương trong artifact paper (47 + 67 token tăng mạnh, 2 + 1 pump & dump): cần đếm thử ca dương trên mẫu nhỏ trước khi chốt H và target. (2026-11-06, claude)
- Pool Base hiện nhiều loại (V3, V4, Aerodrome): LPI theo x·y=k chỉ đúng với pool kiểu V2. (2026-11-06, claude)
- Từ ghi chú đọc (2026-10-16, claude): paper chỉ có 2 rug pull → target nên là "rug **hoặc** sụp giá nghiêm trọng", H phải đủ ca dương; cần chốt khi viết PLAN. Chi tiết: `docs/PAPER_NOTES_MAIN.md` PB31, PB34.

## 6. Bẫy đã gặp / lưu ý (để lần sau không dính lại)

- AGENTS.md Mục 0 ghi "làm theo Mục 14" cho lượt đầu; đúng ra là **Mục 15**. (2026-10-01, claude)
- Repo git nằm ở thư mục cha `NT547/`, có nhiều file bị xoá không liên quan. Commit phải chọn đường dẫn rõ, không `git add -A`. (2026-10-01, claude)

## 7. Con trỏ tới tài liệu

| File | Trạng thái |
|---|---|
| `AGENTS.md` | có (nguồn sự thật) |
| `CLAUDE.md` | có (import AGENTS.md) |
| `docs/PLAN.md` | chưa |
| `docs/READING_GUIDE.md` | có (2026-10-01 codex), chờ duyệt |
| `docs/LEARNING_ROADMAP.md` | có (2026-10-01 codex), chờ duyệt |
| `docs/PAPER_NOTES_MAIN.md` | có (2026-10-16 claude): ý chính + keyword + phản biện PB1–PB48 từng mục paper chính, chờ duyệt |
| `docs/THRESHOLD_AUDIT.md`, `docs/DATASET_NOTES.md` | có (2026-10-01 codex) |
| `docs/LOG.md` | có (bắt đầu 2026-10-16) |
| `docs/MARKET_SNAPSHOT_2026-10-16.md` | có (2026-10-16 claude): bối cảnh thị trường meme 2026, top 10, độ ổn định, phân bổ holder; không phải dữ liệu nghiên cứu |
