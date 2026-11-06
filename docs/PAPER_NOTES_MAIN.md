# Ghi chú đọc từng mục — Mongardini & Mei, *A Midsummer Meme's Dream* (USENIX Security 2026)

**2026-10-16 [claude] — bản đầu, chờ sinh viên duyệt.** Đọc từ [bản Markdown](references/markdown/01_mongardini_mei_midsummer_meme_2026.md). Số trang in xác định theo chân trang (footer) trong Markdown; trang in = trang PDF + 3929 (xem [THRESHOLD_AUDIT.md](THRESHOLD_AUDIT.md)). Chỗ nào ghi **(mình tính)** là phép tính kiểm tra lại số học của paper, không phải kết quả nghiên cứu mới. Ngưỡng chính xác (dấu `>`/`≥`, phần chưa xác minh) lấy theo THRESHOLD_AUDIT, file này không thay thế nó.

## Cách dùng file này

1. Đọc một mục trong paper **trước**, tự tóm tắt 2–3 câu, rồi mới mở ghi chú mục đó để so. Đừng đọc ghi chú thay cho paper.
2. Keyword được giữ **nguyên văn tiếng Anh** để bạn Ctrl+F trong PDF và tô màu.
3. Câu hỏi phản biện đánh số **PB1, PB2…** Sau này trả lời trong ghi chú riêng hoặc đưa vào phần *Hạn chế* của báo cáo. Bảng cuối file cho biết câu nào đồ án sẽ trả lời.

**Quy ước màu highlight:**

| Màu | Dùng cho |
|---|---|
| 🟨 Vàng | Định nghĩa, khái niệm |
| 🟩 Xanh lá | Ngưỡng và con số sẽ tái lập hoặc so sánh |
| 🟦 Xanh dương | Nguồn dữ liệu, công cụ, phương pháp thống kê |
| 🟥 Đỏ | Hạn chế, chỗ tác giả tự thừa nhận, chỗ mơ hồ |

**Mức đọc:** ⭐⭐⭐ đọc kỹ từng câu · ⭐⭐ đọc hiểu ý · ⭐ lướt.

**Hai lỗi do chuyển PDF → Markdown cần biết:** tiêu đề §5.1.2 nằm trước §5.1.1 (đoạn dòng 280–286 thật ra thuộc §5.1.1); câu "Applying this method to the OHLCV data, we detect 3,266…" ở dòng 302 thật ra thuộc §5.2.1.

## Bản đồ bài báo

| Mục | Dòng (Markdown) | Trang in | Mức |
|---|---|---|---|
| Abstract | 23 | 3931 | ⭐⭐⭐ |
| 1 Introduction | 27–49 | 3931–3932 | ⭐⭐⭐ |
| 2 Related Work | 51–63 | 3932 | ⭐ |
| 3 Methodology (thu thập, lọc) | 65–188 | 3932–3935 | ⭐ |
| 4 Tokenomics and Price Growth | 190–272 | 3935–3937 | ⭐ (riêng 4.2.2 ⭐⭐) |
| 5.1 Market Anomalies | 274–321 | 3938–3939 | ⭐⭐ |
| **5.2 Wash Trading** | 323–377 | 3939–3940 | ⭐⭐⭐ |
| **5.3 LPI** | 379–416 | 3940–3941 | ⭐⭐⭐ |
| **5.4 Legitimate vs. Manipulated** | 422–426 | 3942 | ⭐⭐⭐ |
| **6.1 Rug Pull, 6.2 Pump & Dump** | 428–461 | 3942–3943 | ⭐⭐⭐ |
| 6.3 Delisted, 6.4 Economic Impact | 463–511 | 3943–3944 | ⭐⭐ / ⭐ |
| 7 Discussion | 513–519 | 3944 | ⭐⭐ |
| **8 Conclusion and Future Work** | 521–525 | 3944 | ⭐⭐⭐ |
| Ethical Considerations | 535–563 | 3945 | ⭐⭐ |
| Open Science, Appendix | 569–595 | 3946 | ⭐⭐ / ⭐ |

---

## Abstract ⭐⭐⭐ (dòng 23, trang 3931)

**Ý chính**
- Nghiên cứu 34.988 meme coin trên 4 chuỗi (Ethereum, BSC, Solana, Base) và theo dõi giá trong 3 tháng.
- Trong các token tăng giá > 100% (high-return), 82,89% có dấu hiệu **tăng trưởng nhân tạo** (artificial growth).
- Paper đặt tên cho một kiểu thao túng mới là **LPI**: mua một lượng nhỏ có chủ đích làm giá tăng vọt.
- Pump & dump và rug pull thường xảy ra **sau** wash trading hoặc LPI. Đây là ý "dấu hiệu báo trước" (precursor).
- Thiệt hại: hơn 17.000 địa chỉ, lỗ đã hiện thực (realized loss) hơn 9,3 triệu USD.

**Keyword:** 🟨 `artificial growth strategies` · 🟨 `Liquidity Pool-Based Price Inflation (LPI)` · 🟨 `profit extraction schemes` · 🟩 `82.89%` · 🟩 `high-return tokens (>100%)` · 🟩 `17,000 victim addresses` · 🟥 `realized losses`

**Phản biện**
- **PB1.** Abstract viết 82,89% "show **evidence** of artificial growth". Nhưng §5.1 tự nói các anomaly (ví dụ top-10 nắm > 30%) chỉ là "warning signals rather than definitive proof". Vậy 82,89% có đang gộp "dấu hiệu" với "bằng chứng" không? (Xem PB28.)
- **PB2.** "17,000 victim addresses": một **địa chỉ** có phải là một **người** không? Một người có thể dùng nhiều ví, và một ví có thể là bot.

## 1 Introduction ⭐⭐⭐ (dòng 27–49, trang 3931–3932)

**Ý chính**
- Meme coin không có giá trị sử dụng, chỉ sống nhờ "sự quan tâm cảm nhận được" (perceived interest). Vì vậy kẻ xấu có động cơ tạo ra sự quan tâm giả. Paper dùng định nghĩa meme coin của SEC.
- Câu hỏi nghiên cứu: creator và nhà đầu tư sớm có tạo hoạt động ảo để hút nhà đầu tư không, và hoạt động ảo đó có **dọn đường** cho pump & dump, rug pull không?
- Kết quả chính:
  - Có 707 token high-return.
  - 62,9% token bị rút lợi nhuận (profit extraction) trước đó đã có wash trading hoặc LPI.
  - Với token bị gỡ niêm yết (delisted), tỷ lệ này là 86,67%.
- Cơ chế tác giả đề xuất: thao túng để đạt điều kiện niêm yết → được nhiều người thấy → thoát hàng.
- Bốn đóng góp:
  1. Bộ dữ liệu meme coin.
  2. Phân tích so sánh giữa các chuỗi.
  3. Phát hiện tăng trưởng nhân tạo, gồm LPI.
  4. Chuỗi rút lợi nhuận tuần tự và thiệt hại kinh tế.

**Keyword:** 🟨 `perceived interest` · 🟨 `illusory activity` · 🟩 `707 high-performing tokens` · 🟩 `62.9%` · 🟩 `86.67%` · 🟨 `preliminary stages` · 🟨 `meet listing requirements` · 🟨 `Our main contributions`

**Phản biện**
- **PB3.** Con số 62,9% tính trên tập nào? Theo §6.2, nó bằng (37 + 2)/(60 + 2) token = 62,9% **(mình tính)**, tức chỉ 62 token. Thiếu hẳn một **nhóm đối chứng**: trong các token **không** bị pump & dump/rug, bao nhiêu % cũng từng có wash/LPI? Nếu tỷ lệ đó cũng khoảng 60% thì wash chẳng "báo trước" điều gì. Đây chính là **RQ2** của đồ án.
- **PB4.** Hai câu trong cùng mục mâu thuẫn về mẫu số. Dòng 33 viết "62.9% of tokens **subjected to these operations**". Contribution 4 (dòng 49) viết "62.9% of **high-return tokens**". Câu nào đúng? Ngoài ra, cụm "using artificial growth **to facilitate** exit scams" khẳng định **ý đồ**, trong khi dữ liệu chỉ cho thấy **thứ tự thời gian**.

## 2 Related Work ⭐ (dòng 51–63, trang 3932)

**Ý chính**
- Wash trading:
  - Victor & Weintraud [70]: ở một số sàn DEX, tới 35% volume ERC-20 là wash.
  - Le Pennec [54]: dùng học máy để phát hiện.
  - Wash trên NFT: [49], [71].
- Pump & dump: Kamps & Kleinberg [44] định nghĩa; Xu & Livshits [72] xây cơ chế phát hiện. Kẻ tổ chức phối hợp qua Telegram/Discord.
- Rug pull:
  - Zhou [73] phân tích 201 vụ.
  - "1-day rug pull" lãi 240 triệu USD, chủ yếu trên BSC.
- Ba khoảng trống tác giả nhận lấp:
  1. Tập trung vào meme coin.
  2. Xem các kiểu thao túng **kết hợp và nối tiếp nhau**, không xét riêng lẻ.
  3. Phủ 4 chuỗi, trong khi nghiên cứu trước xét tối đa 2.

**Keyword:** 🟨 `combined and executed sequentially` · 🟦 các số [70], [54], [49], [44], [72], [73] (tô để biết paper nào nằm trong danh sách đọc thêm)

**Bảng tra số trích dẫn quan trọng** (theo mục References):

| Số | Paper | Có bản đọc trong repo? |
|---|---|---|
| [9] | Cernera et al., *Ready, aim, snipe!* (WWW Companion 2023) | Chưa |
| [11] | Cernera et al., *Token spammers, rug pulls, and sniper bots* | Có (05) |
| [44] | Kamps & Kleinberg, *To the moon* (2018) | Chưa |
| [49] | La Morgia et al., *A game of NFTs* (ICDCS 2023) | Có (03) |
| [54] | Le Pennec et al., *Wash trading at cryptocurrency exchanges* (2021) | Chưa |
| [58] | Mazorra et al., *Do not rug on me* (2022) | Có (06) |
| [70] | Victor & Weintraud (WWW 2021) | Có (02) |
| [72] | Xu & Livshits (USENIX Security 2019) | Có (04) |
| [73] | Zhou et al., *Stop pulling my rug* (ICSE-SEIP 2024) | Có (08) |

**Phản biện**
- **PB5.** Câu "1-day rug pulls … $240 million" được trích là [9]. Con số này mình tìm thấy trong [11] (Abstract và Sec. 7.2.1 của paper đó). Mình chưa đọc [9] nên chưa khẳng định chắc, nhưng nhiều khả năng **tác giả trích nhầm**. Bài học: tra số trong [ ] giúp phát hiện trích dẫn sai, nên khi đưa một con số vào báo cáo, hãy dẫn về paper gốc.

## 3 Methodology: 3.1 Data Collection ⭐ (dòng 65–111, trang 3932–3934)

**Ý chính**
- **3.1.1 Meme coin đã biết:**
  - Lấy từ CoinMarketCap (2.930), CoinGecko (2.107) và GeckoTerminal (4.735, scraper theo tag animal/dog/cat/inu/pump.fun).
  - Bỏ trùng theo cặp (địa chỉ, chuỗi) → 8.852 token.
- **3.1.2 Token mới:**
  - Lấy từ DexScreener (30.771) và CoinSniper (44.611) → 65.021 token.
  - Phân loại theo tên: chạy TF-IDF trên tên của các meme coin đã biết, dùng elbow method chọn 150 từ, lọc tay còn 126 từ khoá → nhận ra 26.557 meme coin.
  - Thêm token pump.fun (địa chỉ có đuôi `.pump`) → 4.140 token. Kiểm tay 100 mẫu ngẫu nhiên thì 100% đúng là meme.
  - Gộp tất cả được 35.220.
- **3.1.3 Lọc thêm:**
  - Bỏ stablecoin: 4 token.
  - Token giá > $0,80 hoặc market cap > 10⁷: xem category trên CoinGecko và bỏ 46 token không phải meme.
  - Tên chứa `usd`/`wrapped`/`staked`: bỏ 182.
  - Còn **34.988**. Nguyên tắc lọc: ưu tiên precision hơn recall.

**Keyword:** 🟦 `TF-IDF` · 🟦 `elbow method` · 🟩 `126 meme-specific keywords` · 🟨 `.pump suffix` · 🟥 `prioritizes precision over recall` · 🟩 `34,988`

**Phản biện**
- **PB6.** Bộ phân loại theo tên không được báo precision/recall. Token tên có chữ "dog" có chắc là meme không? Meme coin mang tên lạ có bị bỏ sót không? Chỉ riêng pump.fun được kiểm tay (100 mẫu).
- **PB7.** Có lỗi số học. Văn bản ghi còn 35.116 sau khi bỏ 4 token khỏi 35.220, nhưng đúng ra phải là 35.216 **(mình tính)**. Tab. 1 vẫn khớp với kết quả cuối 34.988. Đây là lỗi đánh máy: ghi nhận, không tự sửa số của tác giả.
- *Với đồ án:* không tái lập bước này. Mình chọn mẫu theo phân tầng A/B/C/D (AGENTS.md Mục 5).

## 3.2 Dataset Overview ⭐ (dòng 113–188, trang 3934–3935)

**Ý chính**
- Snapshot dữ liệu giữa tháng 10/2024. Mỗi token lưu tên, symbol, địa chỉ, chuỗi.
- Hạn chế tác giả tự nêu: token chỉ lấy từ DEX aggregator thì chỉ thấy được giao dịch trên DEX. Tác giả lập luận điều này không tạo lỗ hổng.
- **3.2.1:** BSC chiếm 46,88%, Solana 33,80%, Ethereum 10,90%, Base 2,36%. Bốn chuỗi cộng lại có 32.876 token (93,96%).
- **3.2.2 Kiểm tra địa chỉ:**
  - Sai định dạng EVM (phải dài 42 ký tự, bắt đầu bằng `0x`, chỉ chứa ký tự hex): 791 địa chỉ.
  - Không có giao dịch tạo contract (chưa deploy): 254.
  - Solana không hợp lệ: 20.
  - Còn **31.811** token.
- **3.2.3 Diễn biến số token theo thời gian:**
  - Cuối 2020: bull run, SHIB ra đời, BSC xuất hiện.
  - 4/2023: Pepe. 10/2023: BONK.
  - Đỉnh vào hè 2024 trên Solana, do pump.fun.

**Keyword:** 🟥 `our view is limited to DEXs` · 🟦 `creation transactions` · 🟩 `31,811` · 🟨 `pump.fun`

**Phản biện**
- **PB8.** Tác giả viết "this does not introduce coverage gaps". Nhưng OHLCV ở §5 lấy từ GeckoTerminal nên chỉ có dữ liệu DEX. Với token giao dịch cả trên CEX, wash trading trên CEX hoàn toàn không thấy được. Lập luận này có đủ không?
- *Với đồ án:* collector nên kiểm tra địa chỉ y như vậy (đúng định dạng và có giao dịch tạo contract).

## 4 Tokenomics and Price Growth ⭐ (dòng 190–272, trang 3935–3937)

**Ý chính**
- **4.1:**
  - Có dữ liệu kinh tế cho 20.692 token; bỏ 4 token có giá 0 → còn 20.688.
  - Token không có pool tại lúc thu thì không có giá.
  - Chia token theo quý tạo; kiểm định Kruskal-Wallis + Dunn + Bonferroni, mức ý nghĩa p < 0,01.
- **4.1.1 Giá:**
  - Giá trung vị 4×10⁻⁶ USD; khoảng 85% token có giá < $0,00001. Giá siêu rẻ tạo "ảo giác ai cũng mua được".
  - 14 token có giá > $100, nhờ hai cách: đốt token liên tục, hoặc tổng cung chỉ 1 token.
- **4.1.2 Market cap:**
  - Trung vị chỉ $4.100.
  - 47 token có market cap > 1 tỷ USD. Hơn một nửa trong số đó có thanh khoản < $1.000, và 88,1% có thanh khoản < 0,1% market cap. Đây là manh mối dẫn tới LPI (§5.3).
- **4.1.3:** mỗi chuỗi có một kiểu kinh tế riêng.
- **4.2 Giá sau 3 tháng** (snapshot lại giữa tháng 1/2025):
  - 20.327 token có giá mới. 361 token mất giá, nhiều khả năng do pool bị rút.
  - **4.2.2 (⭐⭐):** 34,13% giảm giá; 31,79% đứng yên (volume bằng 0, tức token "chết"); 34,07% tăng.
  - Mức tăng: trung bình 10³⁵ % (do outlier), trung vị 21,46%.
- **Định nghĩa high-return:** Price_final / Price_initial giữa hai snapshot, tăng > 100%. Có **707** token như vậy.

**Keyword:** 🟥 `if a token lacks a liquidity pool` · 🟦 `Kruskal-Wallis H test` · 🟨 `psychological illusion of accessibility` · 🟩 `liquidity below 0.1% of their reported market cap` · 🟨 `Price final/Price initial` · 🟩 `707 tokens (10.21%) gained more than 100%` · 🟥 `Inactive Tokens`

**Phản biện**
- **PB9 (quan trọng).** 707 token được chọn bằng giá **cuối kỳ** so với giá đầu kỳ, tức chỉ hai điểm dữ liệu. Một token tăng 1.000% rồi sập về dưới giá đầu ngay trong 3 tháng sẽ **không** lọt vào 707. Mẫu vì thế thiên về token "còn sống và đang ở giá cao" (selection bias). Điều này làm lệch các tỷ lệ ở §5–6 thế nào? *Với đồ án:* khi dự báo, **không** được chọn mẫu bằng thông tin sau cutoff.
- **PB10.** Mức tăng trung bình 10³⁵ % là thật, hay do lỗi dữ liệu giá (giá đầu gần bằng 0)? Nếu dữ liệu có lỗi kiểu này, ngưỡng "giá tăng > 100%" của LPI có bị kích hoạt bởi lỗi dữ liệu không?
- **PB11.** Market cap = lượng cung lưu hành × giá. Trong pool mỏng, giá do một lệnh nhỏ quyết định, nên market cap thành con số ảo. Đồ án có nên dùng market cap làm feature không? (Gợi ý: dùng tỷ lệ liquidity/market cap, hoặc price impact của lệnh $100.)

## 5 Artificial Growth Strategies, đoạn mở đầu ⭐⭐ (dòng 274–276, trang 3938)

**Ý chính:** Chỉ phân tích 707 token high-return. Dùng OHLCV **theo ngày** (daily) từ giữa 10/2024 tới giữa 1/2025, lấy qua API GeckoTerminal.

**Keyword:** 🟦 `OHLCV` · 🟥 `daily granularity` · 🟦 `Gecko Terminal APIs`

**Phản biện**
- **PB12.** GeckoTerminal trả OHLCV theo **pool**. Token có nhiều pool thì lấy pool nào, hay cộng các pool lại? Bản Markdown không nói. Đồ án phải tự chọn và ghi rõ trong DATA_CARD.

## 5.1 Market Anomalies in High-Return Tokens ⭐⭐ (dòng 278–321, trang 3938–3939)

**Ý chính**
- Dùng API bảo mật bên ngoài (GoPlus, De.Fi, Soul Scanner) để lấy cờ rủi ro. Tác giả nói rõ đây là **"warning signals rather than definitive proof"**; bằng chứng thật nằm ở §5.2–5.3.
- **5.1.1 Tập trung sở hữu:**
  - 385 token (54,46%) có mức tập trung "đáng báo động". Ở các token này, top-10 nắm trung bình 77,85% (trung vị 87,01%).
  - Theo chuẩn của GoPlus/CertiK, top holders > **30%** supply là có vấn đề → 359 token (50,78%).
- **Bundle buy** (gom giao dịch thành gói, ví dụ Jito bundle): trong cùng một gói vừa thêm thanh khoản vừa swap, rồi chia token ra nhiều ví để che giấu chủ sở hữu thật.
  - 133 token có dùng bundle.
  - Bundle > 30% supply được coi là bất thường: 20 token.
- **Fresh address** (ví chưa có lịch sử): > 30% supply → 8 token.
- **Airdrop:** > 30% supply → 24 token.
- **5.1.2 Honeypot** (code chặn người mua bán ra): 28 token bị GoPlus gắn cờ.
- **5.1.3:** 412/707 token (58,27%) có ít nhất một anomaly; riêng cờ top holders chiếm 87,14% (xem Tab. 3).

**Keyword:** 🟥 `warning signals rather than definitive proof` · 🟩 `more than 30% of a token's supply` · 🟨 `bundle buys` · 🟨 `JITO bundles` · 🟨 `fresh addresses` · 🟨 `Strategic Airdrop Distribution` · 🟨 `honeypots` · 🟦 `GoPlus` · 🟦 `CertiK` · 🟩 `412 meme coins (58.27%)` · 🟩 `Table 3`

**Phản biện**
- **PB13.** Top-10 có tính cả địa chỉ pool (LP), địa chỉ burn và ví CEX không? Với meme coin nhỏ, riêng pool có thể giữ phần lớn supply, nên gần như token nào cũng vượt 30%. Paper không nói; THRESHOLD_AUDIT cũng ghi là chưa xác minh.
- **PB14.** Có hai con số: 385 token "alarming" và 359 token "> 30%". Hai con số này dùng tiêu chí khác nhau ra sao?
- **PB15.** Cờ của GoPlus/De.Fi/Soul Scanner được lấy **lúc nào**? Nếu lấy sau khi sự kiện đã xảy ra thì không dùng được để "báo trước", vì đó là rò rỉ tương lai (leakage, xem AGENTS.md Mục 9).
- **PB16.** Airdrop và ví mới đều có lý do hợp lệ (phát thưởng cộng đồng, người dùng mới). Dựa vào gì để phân biệt với che giấu sở hữu?

## 5.2 Wash Trading Analysis and Detection ⭐⭐⭐ (dòng 323–377, trang 3939–3940)

**Định nghĩa:** cùng một thực thể vừa mua vừa bán để tạo hoạt động ảo. Volume tăng nhưng quyền sở hữu không đổi và người làm không chịu rủi ro.

**5.2.1 Sàng lọc bằng OHLCV daily**
- Điều kiện: volume tăng > 500% so với hôm trước **và** |thay đổi giá| < 5%. Tác giả nói đây là heuristic "implementing definitions provided in prior works [54, 70]".
- Kết quả: 3.266 sự kiện nghi ngờ, 379 token. (Câu này bị lạc xuống dòng 302 trong Markdown.)

**5.2.2 Xác minh bằng Dune**
- Dữ liệu cấp giao dịch có địa chỉ trader (maker), **chỉ lấy cho những ngày đã bị sàng lọc**.
- **Zero-risk position** (theo [49]):
  - Cùng maker mua và bán lượng gần bằng nhau trong ngày, chênh 2% (để trừ slippage và phí).
  - Kết quả: 989 sự kiện (30,28%), 276 token, 2.687 maker.
- **Circular volume** (lấy cảm hứng từ [70]):
  - ≥ 99% volume trong ngày đến từ các maker vừa mua vừa bán trong ngày đó.
  - Kết quả: 223 sự kiện, 131 token, 1.148 maker.
- **Coordinated manipulator network:**
  - Maker xuất hiện ở **mọi** ngày wash của token.
  - Kết quả: 42 sự kiện, 17 token, 178 maker.
- **Gộp ba cách:**
  - 1.043 sự kiện (31,94% số nghi ngờ) và 287 token (75,73% số token nghi ngờ).
  - Zero-risk một mình phát hiện 74,11% sự kiện và 96,17% token (xem Tab. 4).

**5.2.3 Đặc điểm**
- **Lặp lại:** trung bình 3,63 lần/token, trung vị 3, tối đa 23.
- **Volume:**
  - Tăng trung vị 1.772% so với hôm trước.
  - Volume tuyệt đối trung bình $10.385, trung vị $859.
  - Ethereum có trung vị cao nhất ($1.673), vì phí gas cao.
- **Thời điểm:**
  - Lần wash đầu tiên xảy ra trung vị 85 ngày sau khi tạo token (Solana: 61 ngày).
  - Chiến dịch kéo dài trung bình 86 ngày.
  - Khoảng cách giữa hai lần: trung bình 33 ngày, trung vị 16.
- **Ít người:** trung bình 3,92 maker mỗi sự kiện; 49,28% sự kiện chỉ do 1 maker.
- **Mục đích (tác giả suy luận):** đạt volume tối thiểu để được niêm yết trên CMC/CoinGecko, và leo hạng trên DexScreener (sàn này xếp token theo volume).

**Keyword:** 🟨 `same entities buy and sell` · 🟩 `>500% compared to the previous day` · 🟩 `absolute price change <5%` · 🟥 `These thresholds are heuristics` · 🟦 `Dune Analytics API` · 🟨 `makers` · 🟨 `Zero-Risk Position` · 🟩 `2% difference` · 🟨 `Circular Volume` · 🟩 `at least 99%` · 🟨 `Coordinated Manipulator Network` · 🟩 `appeared in every detected wash trading day` · 🟩 `Table 4` · 🟨 `Recurrent Manipulations` · 🟨 `Few Wash Traders` · 🟨 `minimum trading volume required for listing`

**Phản biện**
- **PB17 (quan trọng).** Pha xác minh chỉ chạy trên những ngày đã qua sàng lọc. Kẻ wash đều đặn mỗi ngày, volume không bao giờ "nhảy" 500%, sẽ **không bao giờ** bị kiểm tra, nên recall thấp. Có cách sàng lọc nào khác không?
- **PB18.** Nếu volume hôm trước gần bằng 0 (ví dụ $1), thì hôm nay chỉ cần $7 là đã tăng 600%. Có nên thêm ngưỡng volume tuyệt đối tối thiểu không?
- **PB19 (quan trọng).** Zero-risk xét **từng maker riêng lẻ**. Nếu kẻ thao túng dùng ví A để mua và ví B để bán, thì không ví nào "mua–bán cân bằng", và wash lọt hoàn toàn. Muốn gom A và B phải có **đồ thị cấp vốn** (funding graph), tức hướng mở rộng (a) của đồ án.
- **PB20.** Mức "cân bằng 2%" so theo USD hay theo lượng token? Notebook tác giả dùng USD: `abs(B−S)/(B+S)*100 <= 2` (xem [DATASET_NOTES.md](DATASET_NOTES.md)). Ngoài ra, bot tạo lập thị trường (market maker) và bot arbitrage cũng mua–bán gần cân bằng trong ngày. Làm sao loại chúng?
- **PB21.** Trên Dune, "maker" là `tx_from`, tức địa chỉ gửi giao dịch. Nếu nhiều người dùng chung một router, aggregator hay bot, địa chỉ đó sẽ trông như "một maker có mặt mọi ngày", gây ra phối hợp giả. Paper có loại các địa chỉ router không?
- **PB22.** Circular volume chỉ đòi hỏi maker vừa mua vừa bán. Nó **không** kiểm tra chu trình chuyển token giữa các ví như [70] làm, nên tên "circular" có phần quá lời. Thêm nữa, PDF ghi ≥ 99% nhưng notebook dùng `> 99` (xem DATASET_NOTES).
- **PB23.** Chỉ 31,94% sự kiện nghi ngờ được xác nhận. 68% còn lại là do sàng lọc báo nhầm, hay là wash qua nhiều ví mà pha 2 không thấy? Paper không phân tích điểm này.
- **PB24.** Dữ liệu theo ngày che mất gì? Ví dụ mua lúc 9h, bán lúc 17h ở một giá khác thì có còn "zero-risk"? Còn wash diễn ra qua nửa đêm UTC thì bị cắt làm hai ngày.
- **PB25.** Giả thuyết "wash để đạt điều kiện niêm yết" có được kiểm chứng bằng ngày niêm yết thật không, hay chỉ là suy luận? (§6.3 là chỗ gần nhất có thể kiểm chứng.)
- *Số học nhỏ:* 71/287 = 24,74% **(mình tính)**, nhưng paper ghi 24,27%. Có thể là lỗi đánh máy hoặc mẫu số khác.

## 5.3 Liquidity Pool-Based Price Inflation (LPI) ⭐⭐⭐ (dòng 379–416, trang 3940–3941)

**Ý chính**
- Manh mối đến từ §4.1.2: token có market cap khổng lồ nhưng thanh khoản tí hon.
- **Định nghĩa:** khai thác công thức tích hằng số x·y = k. Trong pool ít thanh khoản, chỉ cần mua nhỏ là giá tăng mạnh, tạo ra biểu đồ giá đẹp nhưng ảo.
- **Ví dụ của paper:**
  - Pool có 0,01 ETH và 100 MEME, nên k = 1.
  - Muốn mua 50 MEME phải nạp thêm 0,01 ETH.
  - Giá đi từ 0,0001 lên 0,0004 ETH/MEME, tức **+300%**.
  - Lời giải chi tiết ở THRESHOLD_AUDIT Mục 3 và LEARNING_ROADMAP mục 7.
- **5.3.1 Pha 1 (OHLCV):**
  - Điều kiện: giá tăng > 100% trong 24h **và** (volume tăng ≤ 20% so với hôm trước **hoặc** volume < $1.000).
  - Kết quả: 871 sự kiện, 149 token.
- **Pha 2 (Dune):**
  - Điều kiện: buy volume ≥ 90% volume trong ngày **và** ≤ 10 trader duy nhất.
  - Kết quả: **72 sự kiện, 40 token** (Solana 12, BSC 11, Ethereum 10, Base 7).
- **5.3.2 Đặc điểm:**
  - **Vốn bỏ ra:** buy volume trung vị chỉ $54; chỉ 43,06% sự kiện cần hơn $100.
  - **Mức tăng giá:** 50% sự kiện làm giá tăng > 500%. Riêng Base có trung vị tăng 4×10⁸ %.
  - **Số người:** trung bình 1,96 người mỗi sự kiện; 66,67% sự kiện do 1 người.
  - **Token bị nhắm thường đã "già":** trung vị 209 ngày sau khi tạo (Solana: 115 ngày).

**Keyword:** 🟨 `constant product formula` · 🟨 `low-liquidity pools` · 🟩 `0.01 ETH and 100 MEME` · 🟩 `300% price increase` · 🟩 `exceeding 100% within a 24-hour period` · 🟩 `20% increase` · 🟩 `below $1,000` · 🟩 `at least 90%` · 🟩 `must not exceed 10` · 🟨 `unique trading entities` · 🟩 `72 price manipulations affecting 40` · 🟨 `Targets Are Old Tokens` · 🟨 `capital-efficient`

**Phản biện**
- **PB26 (quan trọng).** Một người **thật** mua token trong pool mỏng cũng tạo ra đúng mẫu hình này: giá vọt, ít trader, toàn lệnh mua. "LPI" khác "một lần mua bình thường ở pool mỏng" ở chỗ nào? Cần bằng chứng nào về **ý đồ**? Ví dụ: ví mua có liên quan tới creator không, sau đó có bán ra không, có đợt quảng bá trùng thời điểm không? Câu này liên quan RQ4.
- **PB27.** Công thức x·y = k chỉ đúng cho pool kiểu Uniswap V2. Với pool Uniswap V3 (thanh khoản tập trung) và bonding curve của pump.fun, hiện tượng có giống không, ngưỡng có còn hợp không? Đây là hướng mở rộng (b).
- **PB27b.** Điều kiện "volume tăng ≤ 20%" có lỗ hổng. Nếu volume hôm qua đã cao và hôm nay vẫn cao, trong khi giá +100%, điều kiện vẫn thoả. Vậy nó có thật sự bắt được "giá tăng mà không có giao dịch tương ứng"?
- **PB27c.** Token nhỏ hợp lệ, ít người biết, cũng chỉ có vài trader mỗi ngày. Ngưỡng 10 trader có nên khác nhau giữa các chuỗi không (Solana có rất nhiều bot)?
- **PB27d.** Trung vị +4×10⁸ % trên Base: pool gần như rỗng hay dữ liệu giá bị lỗi? Paper có kiểm tra không?
- **PB27e.** Câu "manipulators specifically seek out older tokens" là suy ra **ý đồ** chỉ từ thời điểm. Có một giải thích khác: token cũ đã "chết", pool mỏng, nên bất kỳ lệnh mua nào cũng thành đột biến giá.

## 5.4 Legitimate vs. Manipulated Growth ⭐⭐⭐ (dòng 422–426, trang 3942)

**Ý chính**
- Hợp ba nhóm: wash (287) ∪ LPI (40) ∪ anomaly (412) = **586/707 = 82,89%**.
- 120 token có cả wash lẫn anomaly. Tỷ lệ 20,48% ở đây là trên 586 token nghi ngờ, **không phải** trên 707 **(mình tính)**.
- Trong 40 token LPI, 32 token có sở hữu tập trung. 12 token có cả wash lẫn LPI.
- Còn **121 token "sạch"**: Solana 80, BSC 22, Ethereum 12, Base 7.

**Keyword:** 🟩 `586 tokens (82.89% of all high-performing tokens)` · 🟨 `at least one form of suspicious activity` · 🟥 `or conditions that facilitate it` · 🟩 `121 tokens that show no signs`

**Phản biện**
- **PB28 (quan trọng).** Nếu bỏ nhóm anomaly (vốn chỉ là cờ cảnh báo) và chỉ giữ wash ∪ LPI, ta được 287 + 40 − 12 = 315/707 ≈ **44,6%** **(mình tính)**. Như vậy con số tiêu đề 82,89% phụ thuộc nhiều vào cờ tập trung sở hữu. Báo cáo của đồ án nên tách riêng hai con số này.
- **PB29 (quan trọng).** Không có **nhóm đối chứng**. Trong các token *không* tăng giá mạnh, bao nhiêu % cũng có top-10 > 30% hoặc có wash? Nếu tỷ lệ tương tự, ta không thể kết luận "tăng giá là do thao túng". Nhóm B (token ngẫu nhiên) của đồ án sinh ra để trả lời câu này (RQ1, RQ4).
- **PB30.** 121 token "không có dấu hiệu" có thật sự hợp lệ không? "Không phát hiện được" khác với "hợp lệ", vì ngưỡng thận trọng và pha xác minh chỉ xét những ngày bị sàng lọc. Đồ án xử lý bằng nhóm C và manual validation.
- *Thói quen đọc:* mẫu số thay đổi liên tục (707, 586, 412, 379…). Mỗi lần gặp một tỷ lệ %, hãy viết mẫu số ra lề.

## 6 Profit Extraction Manipulations, đoạn mở đầu ⭐⭐ (dòng 428–430, trang 3942)

**Ý chính:** Mở rộng thêm OHLCV **theo giờ** (hourly) từ giữa 1/2025 tới giữa 3/2025, để theo dõi đoạn từ thao túng tới rút lợi nhuận.

**Keyword:** 🟦 `hourly granularity` · 🟩 `mid-January through mid-March 2025`

**Phản biện**
- **PB31 (quan trọng cho RQ2).** Wash/LPI được tìm trong khoảng 10/2024–1/2025; pump & dump và rug được tìm trong khoảng 1/2025–3/2025. Vậy chữ "previously" ở §6.2 đúng là **nhờ cách chia hai cửa sổ thời gian**, chứ không phải nhờ đo khoảng cách thời gian của từng token. Khoảng báo trước thật (lead time) là bao nhiêu ngày? Paper không báo, còn đồ án đo được. Thêm nữa, hai giai đoạn dùng hai độ phân giải khác nhau (ngày và giờ).

## 6.1 Strategic Exit via Rug Pulls ⭐⭐⭐ (dòng 432–436, trang 3942)

**Ý chính**
- **Rug pull:** nhà phát triển bỏ dự án, thường bằng cách rút toàn bộ thanh khoản khỏi pool.
- **Tiêu chí** (lấy từ [58], Mazorra et al.):
  - Giá giảm > 99% trong một ngày,
  - **và** volume giảm > 99%, kéo dài sang những ngày sau.
- **Kết quả:** chỉ **2 token** (1 Solana, 1 Ethereum). Cả hai trước đó đều có thao túng: một token có wash, một token có LPI.

**Keyword:** 🟨 `exit scam` · 🟨 `removing all liquidity` · 🟩 `single-day price drop of over 99%` · 🟩 `sustained drop in trading volume of more than 99%` · 🟦 `[58]` · 🟥 `we detect two tokens`

**Phản biện**
- **PB32.** "Những ngày sau" là bao nhiêu ngày? Volume giảm 99% là so với ngày nào? Hai chi tiết này chưa xác minh được (xem THRESHOLD_AUDIT).
- **PB33.** Rug pull chỉ được nhận ra qua giá và volume; paper không kiểm tra sự kiện rút LP (`Burn`) trên chuỗi. Giá giảm 99% cũng có thể do lỗi dữ liệu, hoặc do thanh khoản chuyển sang một pool khác (migration). Đồ án nên củng cố nhãn bằng log `Burn`.
- **PB34 (quan trọng cho PLAN).** Chỉ có 2 ca thì không thể làm thống kê. Với mẫu 150–400 token, đồ án có thể gặp rất ít rug pull. Vì vậy target nên là "rug pull **hoặc** sụp giá nghiêm trọng" (AGENTS.md Mục 9.4), và H phải chọn sao cho đủ số ca dương.

## 6.2 Orchestrated Pump and Dump Operations ⭐⭐⭐ (dòng 438–461, trang 3942–3943)

**Ý chính**
- **Quy trình phát hiện** (trên dữ liệu theo giờ):
  1. **Tìm đỉnh:** đỉnh giá có RSI > 80. Lấy đáy cục bộ trong 24h trước đỉnh làm điểm bắt đầu.
  2. **Pha pump:** giá tăng > 50% từ đáy lên đỉnh, volume tăng > 500%, tất cả diễn ra trong ≤ 24h.
  3. **Pha dump:** giá giảm > 30% sau đỉnh, và volume **trung bình** sau dump < 50% volume của pha pump.
- **Chỉnh ngưỡng:** ban đầu dùng ngưỡng của [44] (pump = giá +10%, volume +400%). Ngưỡng này cho quá nhiều false positive vì meme coin biến động mạnh, nên tác giả siết lại và "ưu tiên precision hơn recall".
- **Kết quả:**
  - 91 lần pump & dump trên 60 token, trong đó **54 token ở Solana**.
  - Pump trung vị +143,95%; dump trung vị −55,82%.
- **Liên hệ với thao túng trước đó:**
  - 37/60 token (61,67%) từng có tăng trưởng nhân tạo: 35 có wash, 3 có LPI.
  - Tính thêm 2 token rug pull thì tỷ lệ là **62,9%**.

**Keyword:** 🟦 `Relative Strength Index exceeding 80` · 🟩 `preceding 24-hour window` · 🟩 `price increase exceeding 50%` · 🟩 `volume surge exceeding 500%` · 🟩 `maximum 24-hour timeframe` · 🟩 `sharp price decline exceeding 30%` · 🟩 `below 50% of the volume observed during the pump phase` · 🟥 `excessive false positives` · 🟥 `prioritize precision over recall` · 🟩 `91 pump and dump operations affecting 60` · 🟩 `61.67% (37 tokens)` · 🟩 `62.9%`

**Phản biện**
- **PB35 (quan trọng).** Ngưỡng được đổi **sau khi** nhìn kết quả trên chính bộ dữ liệu này. Như vậy chữ "precision" có bị đánh giá lạc quan không? Mình không thấy paper đo precision bằng kiểm tra thủ công. *Với đồ án:* chỉ chỉnh ngưỡng trên tập train/validation, còn tập test chỉ chạy **một lần**.
- **PB36.** RSI tính trên cửa sổ bao nhiêu giờ? Volume "tăng > 500%" là so với cái gì (giờ trước, hay trung bình trước đáy)? Pha dump kéo dài tới đâu? Các chi tiết này chưa xác minh.
- **PB37.** 54/60 token nằm ở Solana. Do Solana thật sự có nhiều pump & dump, hay do tham số hợp với đặc điểm của Solana (nhiều bot, phí giao dịch rẻ)?
- **PB38.** Một token tăng mạnh vì tin tức thật, rồi người mua chốt lời làm giá giảm 30%, cũng thoả mọi điều kiện trên. Vậy "pump & dump" ở đây chỉ là một **mẫu hình giá–volume**, chưa phải bằng chứng có phối hợp, dù tiêu đề mục dùng chữ "Orchestrated". (Xem thêm PB3 về nhóm đối chứng.)

## 6.3 Case Study: Delisted Tokens ⭐⭐ (dòng 463–497, trang 3943)

**Ý chính**
- Xét 124 token bị CMC/CoinGecko gỡ niêm yết trong khoảng 10/2024–3/2025.
- 84 token (67,74%) có tăng trưởng nhân tạo: 70 có wash, 27 có LPI.
- 30 token (24,19%) rút lợi nhuận sau khi niêm yết: 23 pump & dump, 7 rug.
- Trong 30 token đó, 26 (86,67%) trước đó đã có tăng trưởng nhân tạo. **Mọi** token rug đều có thao túng từ trước.
- Kết luận của tác giả: thao túng giúp đạt điều kiện niêm yết → token có tiếng → thoát hàng.

**Keyword:** 🟨 `delisting` · 🟩 `124 meme coins` · 🟩 `84 tokens (67.74%)` · 🟩 `30 tokens (24.19%)` · 🟩 `26 tokens (86.67%)` · 🟩 `Table 5`

**Phản biện**
- **PB39.** Nhóm này được chọn **vì đã có kết cục xấu** (bị gỡ niêm yết), nên tỷ lệ thao túng cao cũng dễ hiểu. Paper có so với các token vẫn còn niêm yết không?
- **PB40.** Câu "dùng thao túng **để** đạt điều kiện niêm yết" cần chứng minh wash xảy ra **trước** ngày niêm yết. Bài không đưa ra ngày niêm yết, và file delisted trong artifact cũng không có thời điểm sự kiện (xem DATASET_NOTES).

## 6.4 Economic Impact ⭐ (dòng 499–511, trang 3943–3944)

**Ý chính**
- **Pump & dump** chia người tham gia làm ba nhóm:
  - **Creators:** người deploy token, **hoặc người nhận airdrop**.
  - **Early investors:** mua trước khi pump.
  - **Late investors:** mua trong pha pump.
- Bên có lời thu được $7,78M (18.568 địa chỉ). Bên lỗ mất $3,27M lỗ đã hiện thực (5.783 địa chỉ). Tác giả gọi con số lỗ này là "conservative lower bound", vì chưa tính lỗ trên giấy của người còn giữ token.
- Nhóm creators thu $2,06M qua 10.614 địa chỉ, nhiều khả năng mỗi người dùng nhiều ví.
- **Rug pull:** nạn nhân là người mua trước vụ rug và không bán được.
  - Tổng lỗ $6,04M trên 11.368 địa chỉ; trung bình $671.666 mỗi sự kiện.
  - Vụ lớn nhất lỗ hơn $2,89M.
- **Tổng cộng:** hơn **$9,3M**, hơn **17.000** địa chỉ. Đúng là 5.783 + 11.368 = 17.151 **(mình tính)**.

**Keyword:** 🟨 `realized losses` · 🟥 `conservative lower bound` · 🟨 `Creators` / `early investors` / `late investors` · 🟩 `Table 6`

**Phản biện**
- **PB41.** Cột Avg/Addr ở Tab. 6 **không bằng** Tot. PnL chia #Addr **(mình tính)**:
  - Creators: 2,06M / 10.614 ≈ $194, nhưng bảng ghi $779.
  - Rug victims: 6,04M / 11.368 ≈ $531, nhưng bảng ghi 379, lại còn mang dấu dương dù là lỗ.
  Vậy Avg/Addr được định nghĩa thế nào?
- **PB42.** Nhóm "Creators" gồm cả người **nhận airdrop**. Vì thế 10.614 "creator" có thể chứa cả người dùng bình thường được tặng token. Định nghĩa này có làm phình nhóm creator không?
- **PB43.** $6,04M / $671.666 ≈ 9 sự kiện rug **(mình suy ra)**, khớp với 2 vụ ở §6.1 cộng 7 vụ ở §6.3. Nhưng paper không ghi rõ phạm vi tính thiệt hại.
- *Với đồ án:* không bắt buộc làm phần này.

## 7 Discussion ⭐⭐ (dòng 513–519, trang 3944)

**Ý chính**
- Các nền tảng (aggregator) hiển thị những metric dễ bị thao túng như volume và liquidity, còn cờ rủi ro thì bị giấu ở cuối trang. Tác giả đề xuất hai cải cách:
  - Hiển thị rủi ro bằng ngôn ngữ dễ hiểu.
  - Giám sát liên tục dấu hiệu tăng trưởng nhân tạo.
- Kết quả cũng hỗ trợ cơ quan quản lý (khung MiCA).
- **Countermeasures (biện pháp đối phó):**
  - Exit scam diễn ra rất nhanh. Nhưng vì wash/LPI thường đi trước, có một **"actionable warning window"** (cửa sổ cảnh báo kịp hành động).
  - Ngưỡng thận trọng nên kết quả có thể là **đánh giá thấp** thực tế.
  - Hệ thống vận hành thật phải tự cân precision–recall.
  - Biện pháp bền nhất vẫn là giáo dục nhà đầu tư.

**Keyword:** 🟨 `actionable warning window` · 🟥 `likely underestimate` · 🟨 `precision-recall trade-off` · 🟨 `exit liquidity` · 🟦 `MiCA`

**Phản biện**
- **PB44 (quan trọng).** Cửa sổ cảnh báo dài bao lâu? Bao nhiêu % token có wash/LPI nhưng rồi **không** bị rút lợi nhuận (tức cảnh báo nhầm)? Khi chưa đo hai điều này thì chưa biết cảnh báo có hữu ích không. Đây là RQ2 và RQ4.
- **PB45.** Tác giả ngầm giả định "ngưỡng thận trọng thì ít false positive", nhưng chưa kiểm tra thủ công để đo. Ngưỡng thận trọng làm giảm recall, nhưng không tự đảm bảo precision cao. Ví dụ, bot market maker vẫn có thể bị bắt nhầm.

## 8 Conclusion and Future Work ⭐⭐⭐ (dòng 521–525, trang 3944)

**Ý chính**
- Nhắc lại các kết quả chính. Thêm hai con số: 67,74% token bị gỡ niêm yết có tăng trưởng nhân tạo trước khi bị gỡ; 24,19% rút lợi nhuận sau khi niêm yết.
- **Future work (nguyên văn):**
  1. Xây hệ thống **phát hiện thời gian thực** cho wash/LPI, và **theo dõi cách chúng tiến hoá** thành rút lợi nhuận.
  2. Nghiên cứu **hoạt động quảng bá off-chain** (website, mạng xã hội) và việc chúng trùng thời điểm với thao túng.

**Keyword:** 🟨 `precursors` · 🟨 `real-time detection systems` · 🟨 `tracking how these evolve into profit extraction schemes` · 🟨 `off-chain promotional activities` · 🟨 `systematic wealth transfer`

**Phản biện**
- **PB46.** Câu "more likely the result of coordinated manipulation than organic market dynamics" là một kết luận nhân quả mạnh, rút ra từ dữ liệu tương quan và không có nhóm đối chứng (xem PB29).
- *Với đồ án:* nhận hướng (1). Biến quan sát "nhìn lại" thành **risk score dự báo**, có temporal split và có đo false positive. Hướng (2) ghi vào phần "hướng phát triển".

## Ethical Considerations ⭐⭐ (dòng 535–563, trang 3945)

**Ý chính**
- **Dữ liệu:** chỉ dùng dữ liệu công khai, không có thông tin cá nhân (PII), không gắn địa chỉ ví với thông tin off-chain.
- **Cách thu:** các request cách nhau ít nhất 5 giây; không giao dịch, không tạo hay quảng bá token.
- **Ai được lợi:**
  - Nhà đầu tư.
  - Aggregator: có thể hiển thị banner cảnh báo LPI.
  - Cộng đồng nghiên cứu bảo mật (S&P).
  - Cơ quan quản lý (MiCA Art. 91).
- **Tác hại (dual-use):** bài có thể dạy kẻ xấu cách làm LPI, và giúp kẻ tinh vi lách các heuristic. Tác giả vẫn công bố vì các kỹ thuật này đã phổ biến sẵn.

**Keyword:** 🟨 `publicly available data` · 🟨 `no attempts to correlate blockchain addresses with external off-chain information` · 🟩 `spaced by at least five seconds` · 🟥 `dual-use` · 🟥 `evade the specific detection heuristics`

**Phản biện**
- **PB47.** Tác giả thừa nhận heuristic có thể bị lách. Hãy liệt kê cụ thể cách lách:
  - Wash qua 2 ví để lách zero-risk.
  - Giữ volume đều đặn để lách ngưỡng sàng lọc 500%.
  - Chia LPI ra 11 ví để lách điều kiện ≤ 10 trader.
  - Giữ mức tăng giá 99%/ngày để lách ngưỡng > 100%.
  Đồ án nên đưa danh sách này vào phần hạn chế, kèm sensitivity analysis.
- *Với đồ án:* áp dụng tinh thần này cho phần đạo đức. Rate limit của mình theo docs API đã kiểm tra.

## Open Science ⭐⭐ (dòng 569–579, trang 3946)

**Ý chính:** Zenodo công bố:
- Dữ liệu token: 34.988 token, 31.811 token đã xác thực, ngày tạo, giá trong 3 tháng.
- Các tập nhãn: high-performing, delisted, anomaly, wash, LPI, rug, pump & dump.
- OHLCV theo ngày và theo giờ.
- Dữ liệu giao dịch kèm SQL Dune.
- Notebook Python.

**Keyword:** 🟦 `Zenodo` · 🟦 `SQL queries` · 🟦 `Python notebooks`

**Phản biện**
- **PB48.** Mô tả trong bài và code có khớp nhau không? [DATASET_NOTES.md](DATASET_NOTES.md) đã thấy ba chỗ lệch:
  - Notebook dùng `> 99` thay cho ≥ 99%.
  - SQL wash có thêm bộ lọc `unique_addresses <= 50`, không có trong PDF.
  - Có dữ liệu mang ngày nằm ngoài cửa sổ nghiên cứu (2022-11-15, 2023-11-28).
  Khi tái lập, theo PDF hay theo code? Phải chọn một và ghi rõ.

## Appendix ⭐ (dòng 581–595)

Gồm Fig. 7 (điểm TF-IDF, dùng để chọn số từ khoá bằng elbow) và Fig. 8 (CDF của market cap). Chỉ cần lướt.

---

## Tổng hợp: đồ án trả lời câu phản biện nào

| Câu phản biện | Đồ án xử lý bằng | RQ / mục AGENTS.md |
|---|---|---|
| PB3, PB29, PB46: thiếu nhóm đối chứng (base rate) | Nhóm B (ngẫu nhiên) + so tỷ lệ wash/LPI giữa các nhóm | RQ1, RQ2 |
| PB31, PB44: chưa đo lead time và cảnh báo nhầm | Cutoff + nhãn trong (cutoff, cutoff+H]; đo precision@k | RQ2, Mục 10 |
| PB9: chọn mẫu bằng giá cuối kỳ | Chọn mẫu và tính feature chỉ với dữ liệu ≤ cutoff; `tests/test_no_leakage.py` | Mục 7, 10 |
| PB15: cờ GoPlus là snapshot hiện tại | Không dùng làm feature cho mẫu quá khứ | Mục 9 |
| PB35, PB45: ngưỡng chỉnh trên cùng dữ liệu, precision chưa đo | Chỉnh trên train/val; sensitivity analysis; manual validation | Mục 8, 11 |
| PB26, PB38, PB30: mẫu hình hợp lệ trông giống thao túng | Nhóm C + nhóm "tăng mạnh nhưng hợp lệ"; mỗi cảnh báo cần bằng chứng hành vi | RQ4, Mục 12 |
| PB13: top-10 có tính pool/burn | Feature loại địa chỉ pool, burn, CEX đã biết | Mục 7, FEATURES.md |
| PB19, PB21: wash qua nhiều ví, maker là router | Mở rộng (a): funding graph; lọc địa chỉ router | Mở rộng (a) |
| PB27: chỉ đúng với AMM V2 | Mở rộng (b): price impact của lệnh $100 từ reserve | Mở rộng (b) |
| PB32–PB34: rug pull hiếm, nhãn chỉ dựa giá/volume | Target rộng hơn + log `Burn`; chọn H có đủ ca dương | Mục 9, PLAN |
| PB12, PB18, PB20, PB24, PB36: chi tiết dữ liệu và công thức | Ghi rõ quy ước trong DATA_CARD và `configs/thresholds.yaml` | Mục 6, 8 |
| PB41–PB43 (thiệt hại kinh tế), off-chain | Ngoài phạm vi, chỉ nêu ở phần hạn chế / hướng phát triển | — |

## Thuật ngữ lạ trong các mục lướt

Các thuật ngữ RSI, honeypot, bundle, airdrop, x·y=k đã có trong [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md) (mục 4, 7, 9, 11, 17). Dưới đây chỉ là các thuật ngữ còn thiếu.

| Thuật ngữ | Nói đơn giản | Định nghĩa | Ví dụ đời thường |
|---|---|---|---|
| TF-IDF | Tìm từ hay xuất hiện ở nhóm này nhưng hiếm ở chỗ khác | `tf(t,d) × log(N / df(t))`: tần suất của từ trong tài liệu × độ hiếm của từ trong cả kho | Chữ "chó" hay có trong tên tiệm thú cưng nhưng hiếm trong tên quán phở → là từ đặc trưng của tiệm thú cưng |
| Elbow method | Thêm mãi thì lợi ích giảm dần; dừng ở chỗ đường cong "gập khuỷu" | Chọn k tại điểm mà độ lợi biên giảm rõ rệt trên đồ thị điểm số theo k | Cái bánh thứ nhất rất ngon, tới cái thứ năm gần như không thêm vui → dừng ở chỗ bắt đầu chán |
| CDF | Đường cho biết bao nhiêu phần trăm nằm dưới mỗi mức | `F(x) = P(X ≤ x)` | "80% học sinh trong lớp được ≤ 7 điểm" |
| Kruskal-Wallis + Dunn + Bonferroni | Kiểm tra nhiều nhóm có khác nhau thật không, không cần dữ liệu có dạng "chuông" | Kiểm định phi tham số dựa trên thứ hạng cho ≥ 3 nhóm. Dunn so từng cặp nhóm; Bonferroni chỉnh mức ý nghĩa vì làm nhiều phép so sánh | Xếp hạng chiều cao học sinh của 4 lớp, rồi xem hạng trung bình của các lớp có lệch nhau nhiều không |
| Maker (trên Dune) | Ví đứng tên gửi giao dịch | Trong SQL của tác giả là cột `tx_from` của `dex.trades`: địa chỉ ký và gửi giao dịch, khác với "maker" trong sổ lệnh của CEX | Người quẹt thẻ ở quầy thu ngân, dù có thể đang mua hộ người khác |
| Realized / unrealized loss | Lỗ đã bán xong / lỗ trên giấy | Realized = tiền thu khi bán − giá vốn; unrealized = giá trị hiện tại − giá vốn của phần còn giữ | Mua áo 500k, bán lại 200k: lỗ thật 300k. Còn giữ áo mà giờ chỉ bán được 200k: lỗ trên giấy |
| Delisting | Bị gỡ khỏi danh sách của trang lớn | Aggregator gỡ token khỏi danh mục khi token không còn đáp ứng tiêu chí niêm yết | Siêu thị gỡ một món khỏi kệ vì bán ế hoặc bị khiếu nại |
| Selection bias | Chọn mẫu kiểu "chỉ nhìn người thắng" | Mẫu được chọn theo một biến có liên quan tới kết quả, nên kết luận bị lệch | Chỉ phỏng vấn người trúng số rồi kết luận "mua vé số dễ giàu" |
