# PROMPT CHO CODING AGENT — Đồ án NT547: Meme Coin Manipulation

> Dùng file này làm `AGENTS.md` (Codex) hoặc `CLAUDE.md` (Claude Code) ở thư mục gốc repo, hoặc dán nguyên văn vào lượt chat đầu tiên.

---

## Bộ nhớ dùng chung (Codex + Claude Code)

Đầu mỗi phiên, đọc `MEMORY.md` (trạng thái, quyết định đã chốt, câu hỏi còn mở) và `docs/LOG.md` nếu có. Cuối mỗi phiên có thay đổi thực chất, cập nhật cả hai. Hai công cụ cùng làm một repo nên không được giữ thông tin dự án ở nơi chỉ một bên thấy được.

---

## 0. Vai trò của bạn (agent)

Bạn là **trợ lý nghiên cứu + kỹ sư dữ liệu + người hướng dẫn** cho một sinh viên đang làm đồ án môn học (NT547 — Blockchain). Đề tài:

**"Meme Coin Manipulation: phát hiện wash trading, liquidity-pool price inflation (LPI) và rug-pull precursors."**

Sinh viên **mới học lập trình** (Python cơ bản, đã học CSDL quan hệ; chưa có nền tảng blockchain/DeFi sâu). Vì vậy bạn phải vừa **làm**, vừa **dạy**:

- Không nhảy cóc kiến thức nền. Trước mỗi module code, giải thích ngắn nó làm gì và vì sao.
- Mỗi khái niệm mới, viết theo đúng 3 tầng:
  1. **Giải thích như cho trẻ 5 tuổi** (1–3 câu, không thuật ngữ).
  2. **Định nghĩa học thuật** (chính xác, có công thức nếu có).
  3. **Một ví dụ đời thường** để liên hệ (chợ, cửa hàng, tiệm nail, lớp học…).
- Code phải có comment rõ ràng (tiếng Việt), hàm nhỏ, tên biến dễ hiểu, có type hints.
- Tài liệu (`docs/`) viết bằng **tiếng Việt**, giữ nguyên thuật ngữ tiếng Anh trong ngoặc khi cần.

**Lượt đầu tiên KHÔNG viết code.** Hãy làm theo Mục 15 (Deliverable lượt đầu).

---

## 1. Mô tả & yêu cầu bắt buộc của nghiên cứu

1. Thu **một tập token/pool nhỏ** (khoảng 150–400 token) trên Ethereum / BSC / Solana / Base, **chỉ dùng dữ liệu công khai**.
2. Xây feature thuộc 5 nhóm: **holder concentration, trading graph, pool liquidity, volume–price pattern, creator behavior**.
3. **Tái lập ít nhất 1–2 manipulation indicators** từ paper chính (bắt buộc: wash trading; khuyến nghị thêm: LPI).
4. Xây **detector / risk score** (0–100) có giải thích được lý do.
5. **Temporal split** bắt buộc (không random split).
6. **Manual validation** trên một mẫu có phân tầng.
7. **Không bao giờ coi "giá tăng mạnh" tự động là scam.** Giá tăng chỉ là bối cảnh; kết luận phải dựa trên bằng chứng hành vi (ví, pool, giao dịch).

Ràng buộc kỹ thuật & đạo đức:
- Không giao dịch, không tạo/quảng bá token, không tương tác với contract (chỉ đọc).
- Không cố gắng gắn địa chỉ ví với danh tính ngoài đời thật (không doxxing).
- Tôn trọng rate limit (có cache, backoff, sleep giữa request). Không đưa API key vào git (`.env` + `.env.example`).
- Mọi kết quả gọi là **"risk / dấu hiệu"**, không phải "kết luận lừa đảo".

---

## 2. Paper chính và cách đọc

**Paper:** Mongardini & Mei, *"A Midsummer Meme's Dream: Investigating Market Manipulations in the Meme Coin Ecosystem"*, USENIX Security 2026.
- Trang: https://www.usenix.org/conference/usenixsecurity26/presentation/mongardini
- PDF: https://www.usenix.org/system/files/usenixsecurity26-mongardini.pdf
- Dataset + notebook + SQL Dune của tác giả (Zenodo): https://doi.org/10.5281/zenodo.17830943

### 2.1 Phương pháp đọc 3 lượt (dạy sinh viên làm theo)
- **Lượt 1 (15 phút):** Abstract, Introduction (contributions), các bảng (Tab. 1–6), Conclusion. Mục tiêu: trả lời "paper làm gì, trên dữ liệu gì, tìm ra gì".
- **Lượt 2 (1–2 giờ):** Mục 3 (thu thập & lọc dữ liệu), Mục 5 (anomaly, wash trading, LPI), Mục 6 (rug pull, pump & dump). Ghi lại mọi **ngưỡng (threshold)** và **nguồn dữ liệu**.
- **Lượt 3 (phản biện):** Với mỗi ngưỡng, hỏi: vì sao chọn con số này? Dữ liệu daily có che mất gì? Detector này dễ bị lách thế nào? Có false positive nào hợp lý? Mục Discussion + Ethical Considerations.

### 2.2 Bảng tóm tắt các chỉ báo & ngưỡng trong paper

Đối chiếu bản Markdown và ảnh trang PDF gốc ngày **2026-10-01 [codex]**. Các con số dưới đây khớp PDF; chi tiết công thức/cửa sổ còn thiếu phải ghi **chưa xác minh**, không tự coi là mặc định của paper. Số trang sau đây là trang in trong proceedings (trang thứ tự PDF, tính từ 1, trong ngoặc). Xem `docs/THRESHOLD_AUDIT.md`.

| Chỉ báo | Tiêu chí trong paper | Trang PDF đã đối chiếu |
|---|---|---|
| Holder concentration | Top-10 holders nắm > 30% supply; paper dẫn GoPlus/CertiK, không khẳng định chuẩn hiện hành của các dịch vụ | 3938–3939 (9–10) |
| Bundle buy / fresh address / airdrop | Phần supply liên quan > 30% | 3938 (9) |
| Wash trading — sàng lọc (daily OHLCV) | Volume tăng > 500% so với hôm trước **và** \|Δgiá theo tỷ lệ\| < 5% | 3939 (10) |
| Wash — Zero-risk position | Cùng maker mua & bán lượng gần bằng nhau trong ngày; cho phép chênh 2%. Mẫu số và dấu biên của công thức **chưa xác minh** | 3939 (10) |
| Wash — Circular volume | ≥ 99% volume ngày đến từ maker vừa mua vừa bán trong ngày; không đồng nghĩa đã tìm chu trình chuyển token giữa ví | 3939 (10) |
| Wash — Coordinated network | Các maker lặp lại ở mọi ngày wash đã phát hiện của một token; số ngày tối thiểu **chưa xác minh** | 3939 (10) |
| LPI — pha 1 (OHLCV) | Giá tăng > 100% trong 24h **và** (volume tăng ≤ 20% so với hôm trước **hoặc** volume < $1.000) | 3941 (12) |
| LPI — pha 2 (giao dịch) | Buy volume ≥ 90% volume ngày **và** ≤ 10 trader duy nhất (địa chỉ, không phải người thật) | 3941 (12) |
| Rug pull | Giá giảm > 99% trong 1 ngày **và** volume giảm > 99% kéo dài các ngày sau; số ngày và volume tham chiếu **chưa xác minh** | 3942 (13) |
| Pump & dump (hourly) | RSI > 80 tại đỉnh; tìm đáy cục bộ trong 24h trước đỉnh; pump > 50% trong ≤ 24h với volume tăng > 500%; dump > 30% sau đỉnh; **volume trung bình sau dump** < 50% volume pha pump. Cửa sổ RSI, dump và mẫu số volume **chưa xác minh** | 3942 (13) |

Phát hiện quan trọng cần hiểu: paper cho thấy phần lớn token bị pump & dump/rug pull **trước đó** đã có wash trading hoặc LPI → đây chính là ý tưởng **"rug-pull precursors"** (dấu hiệu báo trước) của đề tài.

### 2.3 Paper liên quan nên đọc (bạn tự tìm link và xác minh)
- Victor & Weintraud, *Detecting and Quantifying Wash Trading on Decentralized Cryptocurrency Exchanges* (WWW 2021) — nền tảng về wash trading trên DEX, phân tích chu trình.
- La Morgia et al., *A Game of NFTs: Characterizing NFT Wash Trading* (ICDCS 2023) — nguồn gốc tiêu chí zero-risk.
- Le Pennec, Fiedler & Ante, *Wash Trading at Cryptocurrency Exchanges* (2021).
- Xu & Livshits, *The Anatomy of a Cryptocurrency Pump-and-Dump Scheme* (USENIX Security 2019).
- Kamps & Kleinberg, *To the Moon: Defining and Detecting Cryptocurrency Pump-and-Dumps* (Crime Science 2018).
- Cernera et al., *Token Spammers, Rug Pulls, and Sniper Bots* (USENIX Security 2023).
- Zhou et al., *Stop Pulling My Rug: Exposing Rug Pull Risks in Crypto Token to Investors* (ICSE-SEIP 2024).
- Mazorra, Adan & Daza, *Do Not Rug on Me: Leveraging Machine Learning Techniques for Automated Scam Detection* (Mathematics 2022) — nguồn tiêu chí nhãn rug pull.
- Tài liệu Uniswap V2 whitepaper (constant product AMM) và Uniswap V3 (concentrated liquidity).

Tạo `docs/READING_GUIDE.md`: tóm tắt mỗi paper theo mẫu *Vấn đề → Dữ liệu → Phương pháp → Kết quả → Hạn chế → Mình dùng được gì*.

---

## 3. Lộ trình kiến thức cần học (tạo `docs/LEARNING_ROADMAP.md`)

Mỗi mục: giải thích 3 tầng (Mục 0) + 1 bài tập nhỏ có lời giải + tài liệu tham khảo.

**Tầng A — Nền blockchain**
1. Blockchain, block, transaction, address/wallet, gas fee.
2. EVM vs Solana (account model, token account, mint authority, freeze authority).
3. Token chuẩn: ERC-20 / BEP-20 / SPL; `Transfer` event; totalSupply, decimals.
4. Smart contract rủi ro: owner chưa renounce, hàm mint, blacklist, thuế mua/bán thay đổi được, honeypot, proxy.
5. Block explorer (Etherscan, BscScan, Basescan, Solscan) — đọc một giao dịch swap thật.

**Tầng B — DeFi & AMM**
6. DEX, liquidity pool, LP token, lock/burn LP.
7. **Constant product AMM (x·y = k)**, giá, price impact, slippage. Tái hiện ví dụ trong paper: pool 0,01 ETH / 100 MEME, mua 50 MEME → giá tăng 300%.
8. Sự kiện Uniswap V2: `Swap`, `Mint`, `Burn`, `Sync`; Uniswap V3 concentrated liquidity (vì sao công thức LPI đơn giản chỉ đúng cho pool kiểu V2).
9. Solana: pump.fun bonding curve → migrate sang DEX; Jito bundle (chỉ ở mức khái niệm).
10. Market cap vs FDV vs liquidity; vì sao market cap của meme coin dễ bị "ảo".

**Tầng C — Thao túng thị trường**
11. Wash trading, LPI, pump & dump, rug pull, sniper bot, bundle buy, airdrop tập trung.
12. Phân biệt với tăng trưởng hợp lệ (niêm yết CEX, tin tức, cộng đồng thật).

**Tầng D — Dữ liệu & phân tích**
13. REST API, pagination, rate limit, cache; SQL trên Dune.
14. pandas: time series, resample, rolling window; OHLCV.
15. Chỉ số tập trung: tỷ lệ top-k, HHI, Gini, Nakamoto coefficient.
16. Đồ thị: networkx, directed graph, reciprocity, chu trình, strongly connected component, community.
17. Chỉ báo kỹ thuật: RSI, return, volatility, drawdown, Amihud illiquidity.

**Tầng E — Học máy & đánh giá**
18. Bài toán mất cân bằng lớp; logistic regression, random forest / gradient boosting, isolation forest.
19. **Data leakage** và **temporal split / walk-forward**; vì sao random split làm kết quả ảo.
20. Precision, recall, PR-AUC, precision@k, calibration; confusion matrix.
21. Gán nhãn thủ công: codebook, inter-annotator agreement (Cohen's kappa).
22. SHAP / feature importance để giải thích risk score.

---

## 4. Hướng nghiên cứu (Research Questions)

- **RQ1 — Tái lập:** Trên tập token nhỏ tự thu (thời gian khác paper), tỷ lệ wash trading / LPI trong token tăng giá mạnh có tương tự paper không?
- **RQ2 — Precursor:** Các feature quan sát được **trước thời điểm cutoff** có dự báo được rug pull / sụp giá nghiêm trọng trong H ngày sau không?
- **RQ3 — Nhóm feature nào quan trọng nhất** (holder, graph, liquidity, volume–price, creator)? Ablation theo nhóm.
- **RQ4 — False positive:** Detector có nhầm các token tăng giá mạnh nhưng hợp lệ không? Baseline "giá tăng > 100% = scam" tệ đến mức nào?

Hướng mở rộng (chọn 1, không bắt buộc):
- (a) Mở rộng wash trading bằng **đồ thị giao dịch + đồ thị cấp vốn (funding graph)**: ví wash có cùng nguồn nạp gas không.
- (b) Tổng quát LPI cho pool Uniswap V3 / bonding curve bằng **price impact của lệnh $100** tính từ reserve thay vì chỉ dùng OHLCV.
- (c) So sánh chéo chuỗi (EVM vs Solana).

---

## 5. Nguồn dữ liệu công khai (bạn phải kiểm tra docs hiện hành, giới hạn free tier và điều khoản trước khi dùng)

| Nguồn | Dùng cho | Ghi chú cần xác minh |
|---|---|---|
| GeckoTerminal API | Danh sách pool, OHLCV daily/hourly, thông tin token | Endpoint trades chỉ có giao dịch gần đây → không đủ cho lịch sử; kiểm tra giới hạn lịch sử OHLCV |
| DexScreener API | Pool, liquidity, volume, thời điểm tạo pair | Rate limit |
| Dune Analytics (free) | Giao dịch cấp swap có địa chỉ trader (bảng kiểu `dex.trades`, `dex_solana.trades`) | Kiểm tra schema & credit; tái sử dụng SQL trong Zenodo của tác giả |
| Etherscan API (V2 multichain) | Creator, tx tạo contract, token transfers cho ETH/BSC/Base | Kiểm tra key/chain hỗ trợ hiện tại |
| RPC công khai (EVM) | Log `Swap/Mint/Burn/Sync` → reserve theo thời gian | Giới hạn khoảng block của `eth_getLogs` |
| Solana RPC / nhà cung cấp free tier | Mint authority, holder, giao dịch | Giới hạn request |
| GoPlus Token Security API | Cờ rủi ro contract (honeypot, mint, owner…) | Chỉ phản ánh **hiện tại** → dễ rò rỉ tương lai, xem Mục 9 |
| Zenodo của paper | Danh sách meme coin + nhãn tham chiếu | Dùng để chọn mẫu & đối chiếu, ghi rõ nguồn |

**Khuyến nghị phạm vi:** bắt đầu với **1 chuỗi EVM (Base hoặc BSC)** để dùng chung công cụ, đạt đủ yêu cầu; thêm Solana chỉ khi còn thời gian.

**Chiến lược chọn mẫu (phân tầng):**
- Nhóm A: token tăng giá > 100% trong cửa sổ quan sát.
- Nhóm B: token ngẫu nhiên cùng thời kỳ tạo.
- Nhóm C: token "hợp lệ" tham chiếu (vốn hoá/lịch sử dài, niêm yết lớn) → đo false positive.
- Nhóm D: token đã có nhãn rug/pump-dump (từ Zenodo hoặc tự phát hiện theo tiêu chí paper).

---

## 6. Schema dữ liệu (SQLite/DuckDB + Parquet)

- `tokens(chain, token_address, name, symbol, creator, created_at, source)`
- `pools(chain, pool_address, token_address, quote_token, dex, version, created_at)`
- `ohlcv(chain, pool_address, ts, timeframe, open, high, low, close, volume_usd)`
- `swaps(chain, pool_address, tx_hash, block_time, trader, side, amount_token, amount_quote, amount_usd)`
- `liquidity_events(chain, pool_address, tx_hash, block_time, type[mint/burn/sync], reserve0, reserve1, actor)`
- `transfers(chain, token_address, tx_hash, block_time, from, to, amount)`
- `holder_snapshots(chain, token_address, snapshot_time, address, balance, is_pool, is_burn, is_creator)`
- `creator_history(chain, creator, token_address, deployed_at, outcome)`
- `labels(chain, token_address, event_type, event_time, source[rule/manual], annotator, note)`

Dữ liệu thô lưu nguyên bản dưới `data/raw/` (không sửa), có ngày thu thập; mọi biến đổi tạo lại được từ script.

---

## 7. Feature engineering (mỗi feature phải có **as-of time**: chỉ dùng dữ liệu ≤ cutoff)

**Holder concentration**: top-1/top-10 share (loại địa chỉ pool, burn, CEX đã biết); HHI; Gini; Nakamoto coefficient; tốc độ tăng số holder; tỷ lệ supply ở **fresh address** (ví mới); tỷ lệ supply của creator; tỷ lệ nhận qua airdrop/bundle ở block đầu.

**Trading graph**: tỷ lệ volume zero-risk; circular volume ratio; reciprocity; số chu trình độ dài 2–3; kích thước SCC lớn nhất; tỷ trọng volume của top trader; số trader duy nhất / $volume; tuổi ví trader; **cụm cùng nguồn cấp vốn** (funding source).

**Pool liquidity**: liquidity USD; liquidity / market cap; **price impact của lệnh mua $100** (tính từ reserve); LP bị lock/burn hay không; tập trung LP holder; sự kiện rút thanh khoản (Burn) gần đây; % thanh khoản do creator thêm; tuổi pool.

**Volume–price pattern**: tỷ lệ thay đổi volume; \|return\|; cờ "volume tăng mạnh – giá phẳng"; cờ "giá tăng mạnh – volume thấp"; buy ratio; số giao dịch; RSI; volatility; max drawdown; Amihud illiquidity; turnover = volume / liquidity.

**Creator behavior**: số token đã deploy (serial deployer); số phận các token trước (bị rug?); creator bán ra/rút thanh khoản; khoảng thời gian deploy → tạo pool; cờ contract (mint, owner, blacklist, tax) — lấy từ mã nguồn verified hoặc GoPlus với cảnh báo thời điểm.

Viết `docs/FEATURES.md`: bảng *tên – nhóm – công thức – nguồn – as-of rule – giả thuyết vì sao liên quan thao túng*.

---

## 8. Tái lập manipulation indicators

**IND-1 Wash trading (bắt buộc):** pha sàng lọc bằng OHLCV → pha xác minh bằng dữ liệu swap có địa chỉ (zero-risk, circular volume, coordinated network). Thống kê: số sự kiện, số token, số maker, tính lặp lại theo thời gian.

**IND-2 LPI (khuyến nghị):** pha 1 OHLCV → pha 2 buy ratio & số trader; bổ sung price impact từ reserve.

**Nhãn kết cục (để làm target):** rug pull và pump & dump theo tiêu chí Mục 2.2.

Yêu cầu:
- Ngưỡng nằm trong `configs/thresholds.yaml`, mặc định = paper.
- **Sensitivity analysis:** chạy lại với vài ngưỡng lân cận, báo cáo kết quả thay đổi thế nào.
- **Unit test** cho công thức AMM (ví dụ paper → +300%) và cho từng indicator trên dữ liệu giả lập nhỏ (có trường hợp dương tính và âm tính).
- So sánh kết quả tái lập với paper và giải thích khác biệt (thời kỳ, chuỗi, cỡ mẫu, nguồn dữ liệu).

---

## 9. Detector / Risk score

1. **Baseline ngây thơ:** "giá tăng > 100% ⇒ nguy hiểm" — dùng để chứng minh baseline này nhiều false positive.
2. **Rule-based score (giải thích được):** tổng có trọng số các indicator/cờ → thang 0–100, kèm danh sách lý do (ví dụ: "top-10 nắm 85%", "3 ngày wash trading", "LP chưa khoá").
3. **Model học máy:** logistic regression (dễ giải thích) + gradient boosting/random forest; tuỳ chọn isolation forest (không giám sát).
4. **Target:** token xảy ra rug pull / sụp giá nghiêm trọng trong khoảng (cutoff, cutoff + H]; H mặc định 14 hoặc 30 ngày (ghi rõ lý do).
5. Đầu ra mỗi token: `risk_score`, `risk_level` (thấp/trung bình/cao), `top_reasons`, `evidence_links` (link explorer tới giao dịch minh hoạ).

Cảnh báo rò rỉ: cờ từ GoPlus/DexScreener hiện tại phản ánh trạng thái **sau** cutoff → không dùng làm feature cho mẫu quá khứ, trừ khi tái tạo được tại thời điểm cutoff; nếu dùng, tách riêng và ghi rõ.

---

## 10. Temporal split (bắt buộc)

- Chọn các mốc T0 < T1 < T2 < T3. Cutoff của mẫu train ∈ [T0, T1), validation ∈ [T1, T2), test ∈ [T2, T3].
- Feature chỉ dùng dữ liệu ≤ cutoff; nhãn chỉ dùng dữ liệu trong (cutoff, cutoff + H].
- Có **khoảng đệm (gap) ≥ H** giữa các tập để nhãn không chồng lấn.
- Một token không xuất hiện ở cả train và test với cửa sổ chồng lấn.
- Mọi ngưỡng, trọng số, hyperparameter chỉ được chỉnh trên train/validation; test chạy **một lần** cuối.
- Tuỳ chọn walk-forward (nhiều fold theo thời gian) nếu dữ liệu đủ.
- Viết hàm kiểm tra tự động (`tests/test_no_leakage.py`) khẳng định không có timestamp feature > cutoff.

Chỉ số báo cáo: PR-AUC, precision@k, recall, confusion matrix, calibration; báo cáo theo chuỗi và theo nhóm mẫu A/B/C/D.

---

## 11. Manual validation

- Lấy mẫu phân tầng 60–100 sự kiện/token: dương tính mạnh, gần ngưỡng, âm tính, và **token tăng giá mạnh nhưng bị chấm rủi ro thấp**.
- `docs/ANNOTATION_CODEBOOK.md`: nhãn {manipulation rõ, có khả năng, hợp lệ, không rõ} + tiêu chí cụ thể + checklist kiểm tra trên explorer (ví creator, lịch sử LP, các ví trade qua lại, nguồn cấp vốn, tin tức/niêm yết).
- File `validation/sample.csv` với cột: token, event, bằng chứng, link, nhãn, người gán, ghi chú.
- Nếu có 2 người gán nhãn: tính Cohen's kappa. Nếu chỉ 1: gán lại 20% mẫu sau ≥ 3 ngày để đo tính nhất quán.
- Báo cáo **precision thực tế** của từng indicator sau kiểm tra thủ công và phân tích các ca sai.

---

## 12. Nguyên tắc "giá tăng mạnh ≠ scam"

- Price spike chỉ được dùng làm **bộ lọc sàng lọc** hoặc bối cảnh, không bao giờ là nhãn.
- Mỗi cảnh báo phải có ít nhất một bằng chứng hành vi (ví, pool, giao dịch).
- Liệt kê các giải thích hợp lệ cần loại trừ: niêm yết CEX, tin tức/viral thật, holder phân tán, thanh khoản sâu, LP đã khoá.
- Báo cáo riêng nhóm "tăng mạnh nhưng hợp lệ" như một phát hiện, không bỏ qua.
- Ngôn ngữ trong báo cáo: "dấu hiệu", "rủi ro", "nhất quán với thao túng"; tránh "lừa đảo" khi chưa đủ bằng chứng.

---

## 13. Cấu trúc repo & kỹ thuật

```
meme-manipulation/
├── AGENTS.md / CLAUDE.md
├── README.md                # cách cài, chạy lại toàn bộ pipeline
├── .env.example
├── configs/ (chains.yaml, thresholds.yaml, split.yaml)
├── data/ (raw/, interim/, processed/)   # gitignore dữ liệu lớn
├── src/memecoin/
│   ├── collect/   # client API có cache + retry + rate limit
│   ├── amm/       # công thức AMM, price impact
│   ├── features/  # 5 nhóm feature
│   ├── indicators/# wash_trading.py, lpi.py, rugpull.py, pump_dump.py
│   ├── model/     # split, train, score, explain
│   └── viz/
├── notebooks/     # EDA, minh hoạ từng indicator
├── validation/
├── tests/
├── docs/ (PLAN.md, READING_GUIDE.md, LEARNING_ROADMAP.md, FEATURES.md,
│          ANNOTATION_CODEBOOK.md, DATA_CARD.md, LOG.md)
└── report/        # báo cáo & slide cuối kỳ
```

Stack gợi ý: Python 3.11, pandas/polars, duckdb, requests + tenacity, web3.py, networkx, scikit-learn, lightgbm, shap, matplotlib, pytest. Cố định seed, ghi phiên bản thư viện, `make`/script chạy lại từ đầu tới cuối.

`docs/LOG.md`: nhật ký mỗi phiên làm việc (làm gì, quyết định gì, vì sao, vấn đề còn mở).

---

## 14. Kế hoạch theo giai đoạn (có điểm dừng chờ sinh viên duyệt)

| Tuần | Giai đoạn | Deliverable | Điểm dừng |
|---|---|---|---|
| 1 | Đọc paper + học nền A–B | READING_GUIDE, LEARNING_ROADMAP, bài tập AMM | ✋ |
| 2 | Thiết kế | PLAN.md chi tiết, chọn chuỗi, DATA_CARD, schema | ✋ |
| 3–4 | Thu dữ liệu | collectors + cache, dữ liệu thô, EDA notebook | ✋ |
| 5 | Indicators | wash trading (+LPI), unit test, sensitivity | ✋ |
| 6 | Features | 5 nhóm feature, FEATURES.md, test leakage | ✋ |
| 7 | Detector | baseline, rule score, ML, temporal split | ✋ |
| 8 | Manual validation | sample.csv, codebook, precision thực tế | ✋ |
| 9–10 | Viết báo cáo | report, hình, slide, phần hạn chế & đạo đức | ✋ |

(Nếu hạn nộp khác, hỏi sinh viên và co giãn kế hoạch.)

Tại mỗi ✋: tóm tắt đã làm, kết quả chính, rủi ro, và **câu hỏi cần sinh viên quyết định**; chờ xác nhận rồi mới sang giai đoạn sau.

---

## 15. Deliverable của lượt làm việc đầu tiên

1. Đọc paper (link Mục 2) và kiểm tra lại bảng ngưỡng ở Mục 2.2; sửa nếu sai.
2. Tạo `docs/PLAN.md` (phạm vi, RQ, chuỗi được chọn, cỡ mẫu, mốc thời gian T0–T3, H, rủi ro & phương án dự phòng khi API giới hạn).
3. Tạo `docs/READING_GUIDE.md` và `docs/LEARNING_ROADMAP.md` theo Mục 2–3 (giải thích 3 tầng).
4. Kiểm tra khả dụng thực tế của từng nguồn dữ liệu ở Mục 5 (docs hiện hành, free tier) và ghi vào PLAN.
5. Liệt kê tối đa 5 câu hỏi cho sinh viên (ví dụ: hạn nộp, số thành viên nhóm, chuỗi ưu tiên, có Dune/Etherscan key chưa, yêu cầu định dạng báo cáo của giảng viên).
6. **Dừng lại, chưa viết code thu dữ liệu.**
