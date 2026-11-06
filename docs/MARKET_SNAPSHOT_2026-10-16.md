# Thị trường meme coin 01/2026 → 16/10/2026: snapshot và top 10

**2026-10-16 [claude] — tài liệu tham khảo bối cảnh, chưa phải dữ liệu nghiên cứu của đồ án.** Dữ liệu API được lấy thủ công lúc **03:13 UTC ngày 16/10/2026**, chỉ để đọc. File JSON gốc nằm trong scratchpad của phiên, **không** lưu vào `data/raw/`. Vì vậy các con số dưới đây là ảnh chụp tại một thời điểm, và gọi lại API sau này sẽ ra số khác.

**Ký hiệu độ tin cậy của nguồn:**
- ✅ Mình đã mở trang hoặc gọi API trực tiếp.
- 🔎 Chỉ thấy qua kết quả tìm kiếm, chưa mở trang gốc. Cần mở lại trước khi trích vào báo cáo.

**Quy ước "mình tính":** phép tính của mình trên dữ liệu API, không phải số do nguồn công bố.

## 1. Phạm vi và định nghĩa

- **"Meme coin":** theo cách CoinGecko phân loại (category `meme-token`). Cách phân loại này có hai ca đáng ngờ:
  - **PUMP** là token của nền tảng phát hành pump.fun (launchpad).
  - **M (MemeCore)** là coin gốc của một blockchain Layer 1.
  Cả hai không phải meme coin kiểu cổ điển (DOGE, PEPE), nhưng mình giữ nguyên danh sách để trung thành với nguồn. Nếu loại hai coin này, hạng 11–12 là FLOKI (0,24 tỷ USD) và WIF (0,20 tỷ USD).
- **"Đang nổi":** hiểu là **top 10 theo vốn hoá** trong category Meme. Không dùng danh sách *trending* của CoinGecko, vì lúc 03:13 UTC ngày 16/10 trong 15 coin trending không có meme coin nào (toàn INJ, STRK, NEAR, BTC…). Bản thân điều đó đã nói lên mức nhiệt của thị trường meme hiện tại.
- **"10 tháng qua":** từ 01/01/2026 đến 16/10/2026, gồm 289 điểm giá theo ngày (00:00 UTC).

## 2. Thị trường meme coin từ 01/2026 đến nay

| Thời điểm | Diễn biến | Nguồn |
|---|---|---|
| 01/01/2026 | Tổng vốn hoá **của 10 coin top hiện tại** là 32,04 tỷ USD (mình tính) | ✅ CoinGecko API `market_chart/range` |
| 01–06/01 | Rally đầu năm: tổng 10 coin lên đỉnh 41,92 tỷ USD ngày 06/01 (mình tính). PEPE +75% trong 4 ngày đầu năm | ✅ CoinGecko API; ✅ [Sherwood News, 09/02/2026](https://sherwood.news/crypto/meme-coins-have-lost-all-their-2026-gains-and-continue-to-dive/) |
| 09/02/2026 | Cả category meme **−25,8% từ đầu năm** (theo Artemis); toàn bộ phần tăng đầu năm đã mất | ✅ Sherwood News (dẫn Artemis) |
| ~15–16/06/2026 | Vốn hoá meme khoảng **24,5 tỷ USD**, giảm ~82% (hơn 110 tỷ USD) so với đỉnh khoảng 135 tỷ USD năm 2024; **−31% từ đầu năm**. DOGE chiếm hơn một nửa | ✅ [Yellow.com, 16/06/2026](https://yellow.com/news/meme-coins-82-110b-crash-dogecoin-last-anchor) (dẫn CryptoRank; trang [CryptoRank](https://cryptorank.io/news/feed/9df40-meme-coin-market-cap-crash-2026) chặn truy cập, 403) |
| 24–26/06/2026 | **MemeCore (M) sập khoảng 70%** trong một ngày: từ ~3 USD xuống ~0,50 USD, vốn hoá từ ~3 tỷ còn ~1,1 tỷ USD. Không rõ nguyên nhân kích hoạt; bài viết nêu thanh khoản mỏng và nguồn cung tập trung ở một nhóm nhỏ người trong cuộc (insider) | ✅ [Motley Fool, 26/06/2026](https://www.fool.com/investing/2026/06/26/how-the-memecore-crypto-crashed-71-this-week/) |
| 06/10/2026 | Category meme khoảng **35,1 tỷ USD**; DOGE ~14,7 tỷ, SHIB ~3,4 tỷ, PEPE ~1,8 tỷ USD | ✅ [crypto.news, 06/10/2026](https://crypto.news/best-memecoins-to-buy-in-october-2026-five-names-and-their-limits/) (dẫn CoinGecko) |
| **16/10/2026 03:13 UTC** | Category meme **29,86 tỷ USD**, volume 24h 2,91 tỷ USD. DOGE chiếm 42,7%, top 10 chiếm 78,8% category (mình tính). Tổng 10 coin là 23,43 tỷ USD, **−26,9% so với 01/01** (mình tính) | ✅ CoinGecko API `coins/categories`, `coins/markets` |

**Đối chiếu chéo:** theo chuỗi giá CoinGecko, vốn hoá DOGE là 14,91 tỷ USD ngày 06/10 và 12,67 tỷ ngày 16/10, khớp với crypto.news. Như vậy riêng 10 ngày gần đây, meme đã giảm khoảng 15%.

**Chú ý khi trích số:** CoinGecko, CoinMarketCap, CryptoRank và Artemis định nghĩa "meme" khác nhau, nên tổng vốn hoá **không so trực tiếp** giữa các nhà cung cấp được. Khi trích một con số, luôn ghi kèm nhà cung cấp và ngày.

**Meme theo chuỗi / nền tảng phát hành** (category con của CoinGecko lúc 16/10, ✅ API). Các category chồng lấn nhau nên **không được cộng lại**:

| Category | Vốn hoá (tỷ USD) | Volume 24h (tỷ USD) |
|---|---|---|
| Solana Meme | 3,20 | 0,63 |
| Four.meme Ecosystem (BNB Chain) | 0,67 | 0,04 |
| Robinhood Chain Meme | 0,48 | 0,09 |
| Base Meme | 0,27 | 0,02 |
| TON Meme | 0,11 | 0,008 |

## 3. Top 10 meme coin theo vốn hoá (CoinGecko, 16/10/2026 03:13 UTC, ✅ API)

| # | Coin | Chuỗi gốc | Vốn hoá (tỷ USD) | Volume 24h / vốn hoá | Thay đổi từ 01/01 | Cách ATH |
|---|---|---|---|---|---|---|
| 1 | Dogecoin (DOGE) | Chuỗi riêng (PoW) | 12,76 | 9,8% | −31,0% | −88,8% |
| 2 | Shiba Inu (SHIB) | Ethereum | 3,02 | 2,0% | −26,0% | −94,0% |
| 3 | Pump.fun (PUMP)* | Solana | 2,11 | 10,6% | **+136,7%** | −48,3% |
| 4 | MemeCore (M)* | L1 riêng (CoinGecko ghi bản BSC) | 1,83 | **0,06%** | −48,8% | −85,8% |
| 5 | Pepe (PEPE) | Ethereum | 1,72 | 16,8% | +1,2% | −85,4% |
| 6 | Official Trump (TRUMP) | Solana | 0,53 | 32,2% | −60,8% | −97,5% |
| 7 | 币安人生 ("Binance Life") | BNB Chain | 0,48 | 0,79% | **+307,1%** | −46,3% |
| 8 | Pudgy Penguins (PENGU) | Solana | 0,48 | 28,1% | −12,3% | −88,9% |
| 9 | SPX6900 (SPX) | Ethereum | 0,32 | 2,4% | −27,3% | −84,7% |
| 10 | Bonk (BONK) | Solana | 0,27 | 12,3% | −59,0% | −94,7% |

\* Không phải meme coin kiểu cổ điển (xem Mục 1). Các cột "từ 01/01" và "cách ATH" là mình tính từ dữ liệu CoinGecko.

**Ba điểm cần để ý (nối với paper):**
- **MemeCore:** vốn hoá 1,83 tỷ USD nhưng volume 24h chỉ 1,07 triệu USD (0,06%/ngày). Đây đúng kiểu "vốn hoá lớn nhưng giao dịch mỏng" mà paper §4.1.2 coi là đáng ngờ. Nó cũng là coin sập 70% trong một ngày hồi tháng 6.
- **Phân bố chuỗi:** 4/10 coin ở Solana, 3 ở Ethereum, 1 ở BNB Chain, cộng DOGE và MemeCore có chuỗi riêng.
- **Dữ liệu CoinGecko có lỗi:** hạng 24 trong danh sách là "Baby Claw", hiện +56.177% trong 7 ngày, với volume 5 USD và lần cập nhật cuối từ tháng 3/2026. Đây là dữ liệu cũ, không phải tăng giá thật. Bài học giống PB10: phải lọc dữ liệu hỏng trước khi chạy ngưỡng.

## 4. Coin nào ổn định nhất trong 10 tháng?

Tính từ giá đóng cửa ngày (00:00 UTC), giai đoạn 01/01–16/10/2026, nguồn CoinGecko API ✅. Tất cả là mình tính. BTC đưa vào làm mốc so sánh. Bảng xếp theo độ biến động "bền" (cột thứ ba), từ ổn định nhất xuống.

| Coin | Biến động năm hoá | Biến động "bền" (MAD) | % ngày dao động > 10% | Sụt tối đa (max drawdown) |
|---|---|---|---|---|
| *BTC (mốc)* | *45%* | *33%* | *0,7%* | *−39,6%* |
| **DOGE** | **66%** | **42%** | **2,1%** | **−54,5%** |
| SHIB | 68% | 49% | 2,1% | −55,5% |
| PEPE | 97% | 59% | 5,6% | −67,7% |
| TRUMP | 90% | 67% | 3,5% | −76,2% |
| BONK | 129% | 83% | 9,4% | −81,6% |
| M | 182% | 83% | 9,7% | −87,1% |
| PENGU | 97% | 88% | 6,2% | −57,1% |
| 币安人生 | 164% | 96% | 14,9% | −84,4% |
| SPX | 197%† | 109% | 16,0% | −62,7% |
| PUMP | 118% | 110% | 11,5% | −62,2% |

† Dữ liệu SPX tháng 3/2026 có dấu hiệu lỗi giá. Giá giảm 35% rồi tăng lại 52–91% ngay hôm sau, volume chỉ 4–7 triệu USD, còn vốn hoá nhảy từ 0,28 lên 0,54 tỷ USD rồi rơi về 0,25 tỷ. Vì vậy biến động thường của SPX bị thổi phồng. Cột MAD ít bị ảnh hưởng bởi những điểm lỗi như vậy.

**Kết luận:** **DOGE là coin ổn định nhất**, đứng đầu ở cả 4 chỉ số; SHIB sát sau. Nhưng "ổn định" chỉ là **so với các meme coin khác**:
- DOGE vẫn biến động hơn BTC khoảng 1,5 lần (66% so với 45%).
- DOGE giảm 31% từ đầu năm và từng sụt 54,5% so với đỉnh trong giai đoạn này.

**"Ổn định" khác "giữ giá":**
- PEPE gần như về đúng giá đầu năm (+1,2%), nhưng giữa chừng từng sụt 67,7%.
- PUMP (+137%) và 币安人生 (+307%) tăng mạnh nhất, nhưng cũng biến động mạnh nhất. 币安人生 từng sụt 84%.

## 5. Nguồn gốc và phân bổ

### 5.1 Nguồn gốc và phân bổ lúc phát hành

| Coin | Ra đời, ai tạo | Phân bổ ban đầu | Nguồn |
|---|---|---|---|
| **DOGE** | 06/12/2013, Billy Markus và Jackson Palmer, ban đầu như một trò đùa. Chuỗi riêng, Proof of Work (Scrypt) | **Không có trần cung**: 10.000 DOGE/khối, khoảng 5 tỷ DOGE/năm. Không có phân bổ cho đội ngũ; coin sinh ra qua đào. Hiện lưu hành 156,34 tỷ | 🔎 [Wikipedia](https://en.wikipedia.org/wiki/Dogecoin), 🔎 [The Block](https://www.theblock.co/post/245715/a-brief-history-of-dogecoin); ✅ CoinGecko (lượng lưu hành) |
| **SHIB** | 2020, người sáng lập ẩn danh "Ryoshi". Token ERC-20 trên Ethereum | Tổng cung 1 triệu tỷ (10¹⁵). Khoảng một nửa được gửi cho Vitalik Buterin; ông đốt 410,24 nghìn tỷ (90%) và quyên góp 10% còn lại. Năm gửi chưa thống nhất (các nguồn ghi 2020 hoặc 2021) | 🔎 [Decrypt](https://decrypt.co/84645/remember-all-that-shib-vitalik-buterin-burned-now-worth-32-5-billion); ✅ Etherscan: địa chỉ burn giữ 41,04% |
| **PUMP** | 07/2025, token của launchpad pump.fun trên Solana (chính nền tảng sinh ra nhiều meme coin mà paper §3.1.2 thu thập) | Tổng cung 1.000 tỷ: 33% ICO, 24% cộng đồng và hệ sinh thái, 20% đội ngũ, 13% nhà đầu tư cũ, 2,4% quỹ hệ sinh thái, 2% foundation. Các mục này cộng lại 94,4%; phần còn lại chưa xác minh. Có chương trình mua lại và đốt token (buyback-burn) bằng một phần doanh thu. Hiện lưu hành 46,3% | 🔎 [The Defiant](https://thedefiant.io/news/tokens/pumpfun-confirms-pump-token-launch-tokenomics-ico-details), 🔎 [The Block](https://www.theblock.co/post/399288/pump-fun-burns-370-million-pump); ✅ CoinGecko |
| **M (MemeCore)** | Blockchain Layer 1 "Meme 2.0", ra mắt 2025 | Trần cung 10 tỷ: 58% cộng đồng, 15% foundation, 13% người đóng góp cốt lõi, 12% nhà đầu tư, 2% Meme Treasury. Hiện lưu hành 22,9% trần cung | 🔎 [Chainwire, 09/09/2025](https://chainwire.org/2025/09/09/memecore-launches-layer-1-blockchain-to-structure-the-meme-coin-economy/); ✅ CoinGecko |
| **PEPE** | 04/2023, Ethereum. Phát hành công bằng (fair launch): không presale, không thuế giao dịch | Tổng cung 420,69 nghìn tỷ: 93,1% bỏ vào pool Uniswap, **LP token bị đốt**; 6,9% vào ví multisig của đội ngũ để niêm yết sàn. Multisig bị đánh cắp tháng 8/2023, sau đó đội ngũ đốt 6,9 nghìn tỷ (10/2023) | 🔎 [Blockworks Token Transparency](https://blockworks.com/token-transparency/filing/pepe); ✅ Etherscan: địa chỉ `0x…dEaD` giữ 6,92 nghìn tỷ, khớp con số đốt |
| **TRUMP** | 01/2025 (đỉnh giá 19/01/2025), Solana. Gắn với CIC Digital (thuộc Trump) và Fight Fight Fight LLC | Tổng cung 1 tỷ: **80% cho creators và CIC Digital**, khoá rồi mở dần (vesting) trong khoảng 3 năm, kéo sang 2028; 10% thanh khoản; 10% phân phối công khai. Hiện lưu hành 28,2% | 🔎 [The Block / K33](https://www.theblock.co/amp/post/336340/k33-research-flags-trump-memecoins-horrendous-tokenomics-but-highlights-no-immediate-supply-concerns), 🔎 [Tokenomist](https://tokenomist.ai/official-trump/unlock-events); ✅ CoinGecko |
| **币安人生** | 04/10/2025, phát hành qua launchpad Four.Meme trên BNB Chain. Do cộng đồng tạo, **không phải CZ**. Bùng lên sau khi Yi He và CZ (hai đồng sáng lập Binance) đăng cụm từ này trên X | Tổng cung 1 tỷ, lưu hành 100%. Không thấy công bố phân bổ đội ngũ | 🔎 [DL News](https://www.dlnews.com/articles/defi/binance-life-memecoin-mints-millionaires-after-boost-from-cz-and-yi-he), 🔎 [Decrypt](https://decrypt.co/343290/bnb-meme-season-arrives-binance-cz-coins-get-hot); ✅ CoinGecko |
| **PENGU** | 12/2024, Solana. Thương hiệu NFT Pudgy Penguins | Trần cung 88.888.888.888: 25,9% cộng đồng Pudgy (người giữ NFT), 24,12% cộng đồng khác, 17,8% đội ngũ (khoá 1 năm, vesting 3 năm), 12,35% thanh khoản, 11,48% công ty, 4% public good, 4% mở rộng, 0,35% người giữ FTT. Hiện lưu hành 70,7% | 🔎 [Decrypt](https://decrypt.co/296507/pengu-pudgy-penguins-solana-token-airdrop-tokenomics), 🔎 [Transak](https://transak.com/blog/what-is-pengu-meme-coin-pudgy-penguins); ✅ CoinGecko (trần cung) |
| **SPX6900** | Ethereum, đội ngũ ẩn danh; nhại chỉ số S&P 500. **Năm ra đời chưa xác minh** | Không tìm thấy công bố phân bổ. Lưu hành 93,1% trần cung 1 tỷ. Có bản bridged trên Base, Solana, Avalanche | ✅ CoinGecko; nguồn khác chỉ có trang tự sinh của sàn, không đủ tin cậy |
| **BONK** | 25/12/2022, Solana | Cung ban đầu 100 nghìn tỷ: **50% airdrop** cho cộng đồng Solana (dự án NFT, nghệ sĩ, developer); 20% cho người đóng góp sớm (vesting 3 năm từ 01/2023); phần còn lại cho DAO, thanh khoản, marketing. Một phần đã bị đốt; hiện lưu hành 87,99 nghìn tỷ | 🔎 [Capital.com](https://capital.com/how-many-bonk-coins-are-there-in-the-world) (nguồn thứ cấp; nên đối chiếu bonkcoin.com); ✅ CoinGecko |

### 5.2 Phân bổ holder hiện tại

Nguồn ✅: GeckoTerminal API `tokens/{addr}/info` (thời điểm `last_updated` 15–16/10/2026); Etherscan; bitinfocharts.

| Coin | Số holder | Top-10 nắm | Top-10 thật ra là ai |
|---|---|---|---|
| DOGE | (không có) | 44,3% (bitinfocharts, 16/10 02:50 UTC) | ✅ Phần lớn là **sàn**: Robinhood 17,37%, Upbit 7,44%, ba ví Binance 9,99%, "Cryptsy" 3,22%, Bithumb 0,96%. Thêm 1,19% đã đốt và 4,11% chưa có nhãn |
| SHIB | 1,70 triệu | 63,2% | ✅ **41,04% là địa chỉ burn**, 14,3% là sàn (Robinhood, Binance, Crypto.com, Bithumb, OKX), 7,8% chưa có nhãn |
| PEPE | 594.875 | 38,0% | ✅ Khoảng 24,3% là sàn (Binance, OKX, Bybit, Bithumb, BtcTurk), 1,64% burn, ~11,4% chưa có nhãn |
| SPX | 49.334 | 35,1% | Chưa kiểm tra nhãn |
| BONK | 1,03 triệu | 38,3% | Chưa kiểm tra nhãn |
| PENGU | 563.781 | 43,6% | Chưa kiểm tra nhãn |
| PUMP | 354.665 | 60,4% | Chưa kiểm tra nhãn. Nhiều khả năng gồm ví vesting của đội ngũ/nhà đầu tư và kho token mua lại (**chưa xác minh**) |
| 币安人生 | 104.349 | **81,2%** | BscScan chặn truy cập (403) nên **chưa có nhãn**. Không thể kết luận |
| TRUMP | 684.991 | **88,5%** | Chưa kiểm tra nhãn. Con số này **nhất quán với** việc 80% supply được phân cho creators/CIC Digital và vẫn đang khoá dần, nhưng chưa xác minh từng ví |
| M (bản BSC) | 8.225 | **96,6%** | Chỉ là bản token trên BSC, **không phải** toàn bộ cung trên chuỗi L1 gốc, nên không đại diện cho cả coin |

**Lưu ý so sánh:** GeckoTerminal chia nhóm holder khác nhau theo chuỗi (EVM: 11–30, 31–50; Solana: 11–20, 21–40). Vì vậy chỉ cột top-10 là so sánh trực tiếp được.

**Bài học (đúng PB13 trong [PAPER_NOTES_MAIN.md](PAPER_NOTES_MAIN.md)):** nếu áp ngưỡng "top-10 > 30% = rủi ro" của paper lên số thô, **cả 10 coin đều bị gắn cờ**, kể cả DOGE. Nhưng với DOGE, SHIB, PEPE, phần lớn top-10 là ví sàn giữ hộ hàng triệu người, hoặc địa chỉ đã đốt. Feature tập trung sở hữu của đồ án **bắt buộc** phải loại địa chỉ burn, pool và sàn đã biết trước khi tính. Ngược lại, TRUMP và 币安人生 có top-10 rất cao mà chưa có nhãn: đó mới là chỗ cần điều tra, chưa được kết luận.

## 6. Ý nghĩa cho đồ án (đề xuất, chờ sinh viên duyệt)

1. **Nhóm C (token "hợp lệ" để tham chiếu):** DOGE, SHIB, PEPE là ứng viên tự nhiên. Chúng lâu đời, có nhiều holder, và sự tập trung giải thích được bằng sàn/burn. Không nên xếp TRUMP, M, 币安人生 vào nhóm C khi chưa kiểm tra.
2. **Chọn chuỗi:** Solana chiếm phần lớn meme theo category; BNB Chain có Four.Meme; Base nhỏ (0,27 tỷ USD). Đây là dữ kiện cho PLAN, chưa phải quyết định.
3. **Survivorship bias:** top 10 hôm nay được chọn **vì đang còn lớn**. Con số "−26,9% từ đầu năm" của nhóm này còn đẹp hơn thực tế, vì đã bỏ sót các coin đầu năm từng nằm top nhưng nay đã rơi khỏi top. Đây cũng là lỗi PB9 của paper; khi chọn mẫu, không được chọn bằng thông tin sau cutoff.
4. **Kiểm tra chất lượng giá** (SPX tháng 3, Baby Claw) trước khi chạy indicator.
5. **Ca nghiên cứu tình huống (case study) gợi ý:** MemeCore. Vốn hoá lớn, volume rất mỏng, sập 70% trong một ngày tháng 6/2026. Hợp để minh hoạ, nhưng không phải meme coin trên AMM kiểu V2 nên **không** áp được công thức LPI.

## 7. Thuật ngữ mới

| Thuật ngữ | Nói đơn giản | Định nghĩa | Ví dụ đời thường |
|---|---|---|---|
| Biến động năm hoá (annualized volatility) | Giá "nhảy" mạnh cỡ nào | `stdev(ln(P_t/P_{t−1})) × √365` | Nhiệt độ một nơi dao động 2 độ hay 15 độ mỗi ngày |
| Biến động "bền" (MAD) | Như trên, nhưng không để vài ngày lỗi kéo lệch | `median(|r − median(r)|) × 1,4826 × √365` | Chấm điểm thi mà bỏ bớt ảnh hưởng của vài bài chấm nhầm |
| Max drawdown | Từ đỉnh rơi xuống sâu nhất bao nhiêu | `min_t (P_t / max_{s≤t} P_s − 1)` | Leo lên đỉnh núi rồi tụt xuống thung lũng sâu nhất |
| Survivorship bias | Chỉ nhìn kẻ còn sống sót | Mẫu được chọn theo một kết cục đã biết, nên kết luận lệch | Chỉ hỏi những quán còn mở rồi kết luận "mở quán dễ thành công" |
| Lưu hành / trần cung / FDV | Bao nhiêu token đang lưu thông, tối đa có bao nhiêu, và giá trị nếu tất cả lưu thông | Vốn hoá = lưu hành × giá; FDV = trần cung × giá | Một công ty mới phát hành 30% cổ phiếu; 70% còn lại sẽ ra thị trường sau |

## 8. Hạn chế

- Đây là ảnh chụp tại một thời điểm từ một nhà cung cấp chính (CoinGecko). Vốn hoá và phân loại "meme" khác nhau giữa CoinGecko, CoinMarketCap và CryptoRank.
- Chỉ đo holder trên **chuỗi gốc**. PEPE, BONK, PENGU, SPX còn có bản trên chuỗi khác (bridged).
- Nhãn ví (sàn, burn) là do bên thứ ba gắn (Etherscan, bitinfocharts), không phải tự mình xác minh.
- Nguồn 🔎 cần mở trang gốc trước khi đưa vào báo cáo.
- Trang CryptoRank và BscScan chặn truy cập tự động (403).
- Không có mục nào ở đây là kết luận "lừa đảo". Mọi điểm bất thường chỉ là **dấu hiệu cần kiểm tra**.

## 9. Cách lấy lại dữ liệu (endpoint, ngày gọi 16/10/2026)

- CoinGecko (API công khai, không cần key, bị giới hạn khoảng 5–10 lần gọi/phút, đã gặp 429):
  - `/api/v3/coins/markets?vs_currency=usd&category=meme-token&order=market_cap_desc`
  - `/api/v3/coins/categories`
  - `/api/v3/search/trending`
  - `/api/v3/coins/{id}/market_chart/range?vs_currency=usd&from=1767139200&to=<now>`
  - `/api/v3/coins/{id}`
- GeckoTerminal: `/api/v2/networks/{eth|solana|bsc}/tokens/{address}/info` (trường `holders`). Gặp 429 khi gọi cách nhau 8 giây.
- Etherscan: trang `token/tokenholderchart/{address}` của SHIB và PEPE. bitinfocharts: `top-100-richest-dogecoin-addresses.html`.
- RPC công khai của Solana (`api.mainnet-beta.solana.com`) trả 429 ngay lần gọi đầu, nên không dùng được.
