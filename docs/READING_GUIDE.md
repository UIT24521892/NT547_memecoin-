# Hướng dẫn đọc tài liệu nghiên cứu

**2026-10-01 [codex] — bản đầu, chờ sinh viên duyệt.** Đọc bản Markdown cục bộ; đối chiếu ngưỡng paper chính bằng PDF theo [THRESHOLD_AUDIT.md](THRESHOLD_AUDIT.md). Các paper liên quan được đọc ở mức Abstract, phần phương pháp liên quan và kết luận; chưa kiểm toán đầy đủ thực nghiệm. Không mang số đo hiệu năng chưa đối chiếu PDF vào báo cáo. Hai paper thiếu bản cục bộ được ghi **chưa đọc**.

## Cách đọc ba lượt

1. **15 phút:** Abstract → đóng góp Introduction → Tab. 1–6 → Conclusion của paper chính. Viết ba câu: nghiên cứu câu hỏi gì, mẫu nào, thấy dấu hiệu nào. Phân biệt tổng token, token địa chỉ hợp lệ, token có giá, token high-return.
2. **1–2 giờ:** §3 → §5 → §6. Lập bảng `chỉ báo / input / threshold / đơn vị / ngày / nguồn / trang`. Sau đó đối chiếu PDF ngưỡng và đọc notebook/SQL; không giả định prose và code luôn giống nhau.
3. **Phản biện:** §7 Discussion + Ethical Considerations. Hỏi: daily che mất gì? arbitrage có tạo mua–bán cân bằng không? dữ liệu có bị thiếu vì pool chết không? nhãn có dùng tương lai không? thời kỳ/chuỗi khác có cần đổi ngưỡng không? Ghi câu hỏi chưa trả lời thay vì đoán.

Bài đọc đầu: tự giải ví dụ AMM ở [LEARNING_ROADMAP.md](LEARNING_ROADMAP.md), mục 7; giải thích vì sao giá +300% không tự chứng minh thao túng.

## 1. Mongardini & Mei — A Midsummer Meme's Dream (USENIX Security 2026)

Nguồn: [Markdown](references/markdown/01_mongardini_mei_midsummer_meme_2026.md), [trang tác giả tại USENIX](https://www.usenix.org/conference/usenixsecurity26/presentation/mongardini), [artifact](https://doi.org/10.5281/zenodo.17830943). Ghi chú từng mục (ý chính, keyword để highlight, câu hỏi phản biện PB1–PB48): [PAPER_NOTES_MAIN.md](PAPER_NOTES_MAIN.md).

- **Vấn đề:** tăng giá meme coin có đi kèm tăng trưởng nhân tạo không; wash/LPI có xuất hiện trước các kết cục rút lợi nhuận không?
- **Dữ liệu:** token từ aggregators và phân loại tên; Ethereum, BSC, Solana, Base; snapshot giữa 10/2024–1/2025, theo dõi kết cục tới giữa 3/2025; OHLCV, security signals và maker/ngày từ Dune. Phải đọc §3.2.2 để hiểu lọc địa chỉ trước phân tích.
- **Phương pháp:** sàng lọc daily rồi xác minh maker; wash gồm zero-risk, circular, coordinated; LPI sàng lọc giá tăng–volume thấp rồi kiểm tra buy ratio/trader; rug/pump-dump dùng diễn biến sau đó. Cờ sở hữu tập trung là dấu hiệu riêng, không tự xác nhận wash.
- **Kết quả:** §5.4, trang in 3942 / PDF 13 (đã xem ảnh): 586/707 high-return token =82,89% có ít nhất một cờ trong hợp wash, LPI, anomaly. §6.2 cùng trang báo 62,9% token có profit extraction từng có wash/LPI. Không diễn giải 82,89% là tỷ lệ toàn thị trường, hay 62,9% là precision dự đoán precursor.
- **Hạn chế:** chọn high-return bằng thông tin cuối kỳ, thiếu dữ liệu token mất hoạt động, daily làm mất chi tiết nội ngày; cờ dịch vụ không có lịch sử as-of rõ; ngưỡng heuristic và một số cửa sổ thiếu định nghĩa. Có bất nhất prose/code và ngày sự kiện trong artifact; xem [DATASET_NOTES.md](DATASET_NOTES.md). Liên hệ thời gian không chứng minh nhân quả.
- **Mình dùng được gì:** tái lập IND-1, thêm IND-2; dùng artifact đối chiếu, rồi thu mẫu thời kỳ khác; biến ý tưởng precursor thành target trong H ngày với temporal split. Cần nhóm tăng mạnh có giải thích hợp lệ để đánh giá false positive.

## 2. Victor & Weintraud — Detecting and Quantifying Wash Trading on DEX (WWW 2021)

Nguồn: [Markdown](references/markdown/02_victor_weintraud_wash_trading_dex_2021.md), [bản tác giả](https://arxiv.org/abs/2102.07001), [DOI](https://doi.org/10.1145/3442381.3449824). Đọc §4.2 và §5 trước.

- **Vấn đề:** tìm giao dịch tạo volume mà vị thế của nhóm trader gần như không đổi.
- **Dữ liệu:** giao dịch trên IDEX và EtherDelta, DEX theo sổ lệnh (limit order book) của Ethereum; có người mua và người bán trực tiếp.
- **Phương pháp:** đồ thị đa cạnh có hướng theo dòng token; SCC lặp lại tạo tập ứng viên; khớp volume trong cửa sổ để tìm tập giao dịch cân bằng vị thế.
- **Kết quả:** tác giả nhận diện cả self-trade, nhóm hai ví và cấu trúc phức tạp; đo một cận dưới volume nghi vấn. Số định lượng: **chưa đối chiếu PDF** trong phiên này, không dùng làm mục tiêu hiệu năng đồ án.
- **Hạn chế:** chu trình tự nó chưa đủ; cần thời gian và cân bằng lượng. Đối tác giao dịch trên sổ lệnh khác pool AMM, nơi người dùng đổi với pool; không chuyển thẳng seller→buyer thành đồ thị người–người cho swap AMM.
- **Mình dùng được gì:** SCC/volume matching cho transfer hoặc funding graph; dùng để giải thích vì sao circular ratio của paper chính không tương đương phát hiện chu trình thật.

## 3. La Morgia et al. — A Game of NFTs (ICDCS 2023)

Nguồn: [Markdown](references/markdown/03_la_morgia_game_of_nfts_2023.md), [bản tác giả](https://arxiv.org/abs/2212.01225). Đọc §IV.C và phần lợi nhuận.

- **Vấn đề:** NFT chuyển vòng để tăng volume/giá hoặc lấy thưởng marketplace.
- **Dữ liệu:** ERC-721 transfers và giao dịch thanh toán Ethereum; NFT marketplaces. NFT được phân biệt bởi contract và token ID, khác ERC-20 có thể thay thế nhau.
- **Phương pháp:** SCC ứng viên; zero-risk sau tính phí, nguồn cấp vốn chung (common funder), điểm nhận tiền cuối chung (common exit), self-trade; loại dịch vụ exchange/DeFi khỏi suy luận nguồn chung.
- **Kết quả:** phát hiện cấu trúc mua–bán vòng và động cơ hưởng thưởng volume; các phương pháp xác nhận bổ sung cho nhau. Không chép số USD/tỷ lệ chưa đối chiếu PDF.
- **Hạn chế:** các địa chỉ cùng nhận từ CEX có thể độc lập; cấu trúc NFT không tương đương AMM; dùng common exit sau cutoff gây leakage nếu coi là precursor.
- **Mình dùng được gì:** củng cố cơ sở zero-risk; mở rộng funding graph nếu còn thời gian; chỉ dùng nạp tiền xảy ra trước cutoff, không gắn ví với người thật.

## 4. Xu & Livshits — The Anatomy of a Cryptocurrency Pump-and-Dump Scheme (USENIX Security 2019)

Nguồn: [Markdown](references/markdown/04_xu_livshits_pump_dump_anatomy_2019.md), [bản tác giả](https://arxiv.org/abs/1811.10109). Đọc §4–5 và §7.

- **Vấn đề:** cấu trúc pump phối hợp qua Telegram và khả năng nhận diện token mục tiêu trước sự kiện.
- **Dữ liệu:** lịch sử thông báo Telegram và thị trường giao dịch tập trung (CEX), khác hệ sinh thái pool mới trên EVM.
- **Phương pháp:** ghép thông báo với thời điểm thị trường; phân tích feature trước pump; mô hình hồi quy và random forest cho likelihood mục tiêu.
- **Kết quả:** tác giả báo tín hiệu có trước thời điểm pump và hiệu năng ngoài mẫu trong thiết kế của họ. Chưa xác minh số hiệu năng PDF; không xem lợi nhuận giao dịch là mục tiêu đồ án.
- **Hạn chế:** mô hình điều kiện theo thời gian/sàn có thông báo pump, khác dự báo rug tự phát trong H ngày; off-chain coverage và sampling bias cần được xét.
- **Mình dùng được gì:** chọn feature trước sự kiện và so sánh với detection sau sự kiện; không thu danh tính Telegram hoặc triển khai chiến lược giao dịch.

## 5. Cernera et al. — Token Spammers, Rug Pulls, and Sniper Bots (USENIX Security 2023)

Nguồn: [Markdown](references/markdown/05_cernera_token_spammers_rug_pulls_2023.md), [USENIX](https://www.usenix.org/conference/usenixsecurity23/presentation/cernera), [bản tác giả](https://arxiv.org/abs/2206.08202). Đọc §6–9, §11 Discussion.

- **Vấn đề:** token sống rất ngắn, creator deploy hàng loạt, pool thêm rồi rút thanh khoản, và bot mua sớm.
- **Dữ liệu:** token/pool và giao dịch Ethereum/BSC từ lịch sử chuỗi tới kỳ nghiên cứu; Uniswap V2 và forks.
- **Phương pháp:** tái tạo lifetime, liên kết creator, quan sát mẫu one-day rug và hoạt động mua ngay khi pool ra đời; dùng log/on-chain thay vì giá đơn thuần.
- **Kết quả:** tìm thấy mối liên hệ serial deployment–pool tồn tại ngắn–rút LP, cùng bot tham gia; số tiền/tỷ lệ **chưa đối chiếu PDF** trong phiên này.
- **Hạn chế:** phạm vi thu deployment/contract nội bộ có thể thiếu; lifetime nhìn bằng lịch sử kết thúc là biến hậu nghiệm; creator nhiều token không tự đủ kết luận.
- **Mình dùng được gì:** `creator_history` chỉ tính deployment/kết cục đã biết trước cutoff; LP concentration, Burn và tuổi pool; không dùng “ngày hoạt động cuối cùng” biết từ tương lai làm feature.

## 6. Mazorra, Adan & Daza — Do Not Rug on Me (2022)

Nguồn: [Markdown bản arXiv](references/markdown/06_mazorra_do_not_rug_on_me_2022.md), [arXiv](https://arxiv.org/abs/2201.07220), [bản tạp chí](https://doi.org/10.3390/math10060949). **Bản đang đọc có tiêu đề “Zero-dimensional Scam Detection”; chưa đối chiếu nội dung với bản Mathematics.** Đọc §6.1 và §7.

- **Vấn đề:** phân biệt nguy cơ trước rug với nhận diện sau khi mất thanh khoản/giá.
- **Dữ liệu:** Uniswap V2, pool ghép wETH; Sync/Mint/Burn/Transfer, token code và nhóm đối chiếu từ nguồn audit.
- **Phương pháp:** nhãn theo drop thanh khoản/giá, không hồi phục và inactivity; feature phân bố token, HHI, graph, smart contract; đánh giá theo điểm trước sự kiện và giai đoạn sớm của pool.
- **Kết quả:** tác giả báo khả năng nhận diện trước sự kiện trong dữ liệu của họ; LP lock không bảo đảm tránh mọi đường rút lợi nhuận. Không sao chép accuracy/recall chưa đối chiếu PDF.
- **Hạn chế:** nhãn được xây bằng dữ liệu kết thúc lịch sử; đối chứng audit có thể khác quần thể; split và điểm đánh giá cần kiểm toán trước khi so sánh đồ án.
- **Mình dùng được gì:** HHI, liquidity drop/recovery và tránh nhầm nhãn hậu nghiệm với feature. Paper chính dẫn nguồn này cho rug rule, nhưng bản arXiv cục bộ không trình bày y hệt “daily >99% + volume >99%”; không khẳng định đã xác minh nguồn gốc rule ở bản tạp chí.

## 7. Zhou et al. — Stop Pulling My Rug (ICSE-SEIP 2024)

Nguồn: [Markdown](references/markdown/08_zhou_stop_pulling_my_rug_2024.md), [PDF tác giả](http://www.wingtecher.com/themes/WingTecherResearch/assets/papers/Tokeer_CameraReady.pdf). Đọc §2, §3 và §6.

- **Vấn đề:** rủi ro ẩn trong logic chuyển token có thể khiến holder mất khả năng chuyển/bán.
- **Dữ liệu:** các sự cố rug thực tế và token contracts dùng đánh giá công cụ Tokeer; báo cáo từ đội bảo mật hỗ trợ phân tích sự cố.
- **Phương pháp:** mô hình các thành phần transfer, phân tích EVM bytecode/IR bằng datalog; oracle cho BlackList, ModifyBalance, TimeLimit, AlienDepend.
- **Kết quả:** tác giả báo công cụ tìm được nhiều rủi ro hợp đồng; phần Lessons Learned phân biệt **có quyền nguy hiểm** với **đã gây thiệt hại**. Chưa đối chiếu PDF các số hiệu năng.
- **Hạn chế:** phụ thuộc decompilation và phạm vi mẫu rủi ro; không thay thế bằng chứng wash/LPI hoặc dự báo kết cục trong H ngày; trạng thái quyền/proxy có thể đổi theo thời gian.
- **Mình dùng được gì:** thiết kế codebook contract flags và creator behavior; chỉ dùng mã/trạng thái có thể tái tạo as-of. Không cần triển khai hệ phân tích bytecode đầy đủ trong đồ án nhỏ.

## 8. Uniswap V2 Core whitepaper (2020)

Nguồn: [Markdown](references/markdown/10_uniswap_v2_whitepaper.md), [PDF chính thức](https://uniswap.org/whitepaper.pdf). Đọc §1, §2.2 và cơ chế reserve/core.

- **Vấn đề:** swap phi tập trung và giá tham chiếu qua pool hai tài sản.
- **Dữ liệu:** tài liệu thiết kế, không phải tập nhãn manipulation.
- **Phương pháp:** constant product, pair/factory/router, reserve, phí và giá trung bình theo thời gian (TWAP).
- **Kết quả:** giải thích kiến trúc core và lý do spot price tức thời dễ bị dịch chuyển; không cung cấp accuracy detector.
- **Hạn chế:** `xy=k` cố định là mô hình lý tưởng bỏ phí, mint/burn, token tax/rebase; thực tế invariant có điều chỉnh và k có thể tăng khi thu phí.
- **Mình dùng được gì:** công thức bài AMM, log reserve và price impact; dùng đúng decimals, định hướng quote và loại pool. Ví dụ +300% không mô phỏng phí thực tế.

## 9. Uniswap V3 Core whitepaper (2021)

Nguồn: [Markdown](references/markdown/11_uniswap_v3_whitepaper.md), [PDF chính thức](https://uniswap.org/whitepaper-v3.pdf). Đọc §2 Concentrated Liquidity, sau đó tick và oracle.

- **Vấn đề:** tăng hiệu quả vốn bằng cách tập trung thanh khoản trong khoảng giá.
- **Dữ liệu:** tài liệu thiết kế; không có nhãn scam/wash.
- **Phương pháp:** liquidity positions và virtual reserves theo khoảng; tick xác định thanh khoản hoạt động, swap đi qua tick làm thay đổi L đang hoạt động.
- **Kết quả:** cung cấp cơ chế pool và oracle; không phải nghiên cứu tỷ lệ manipulation.
- **Hạn chế:** công thức toán trong Markdown có chỗ mất ký tự; **chưa xác minh** chi tiết công thức virtual reserves với ảnh PDF trong phiên này; balance toàn pool không đủ làm reserve V2.
- **Mình dùng được gì:** giới hạn bài LPI cơ học ở V2-style; nếu muốn V3 phải có tick/liquidity/fee và mô phỏng, không thay x,y bằng token balances rồi tính như V2.

## 10. Kamps & Kleinberg — To the Moon (Crime Science 2018)

Nguồn link trong [README tham khảo](references/README.md): [trang nhà xuất bản](https://link.springer.com/article/10.1186/s40163-018-0093-5). **Chưa đọc**, chưa có Markdown/PDF cục bộ.

- **Vấn đề:** theo tiêu đề: định nghĩa và phát hiện pump-and-dump.
- **Dữ liệu → Phương pháp → Kết quả → Hạn chế:** **chưa đọc / chưa xác minh**.
- **Mình dùng được gì:** dự kiến đối chiếu nguồn ngưỡng pump ban đầu paper chính dẫn; chưa dùng ngưỡng 10%/400% như kết quả đã đọc của paper này.

## 11. Le Pennec, Fiedler & Ante — Wash Trading at Cryptocurrency Exchanges (2021)

Nguồn link trong [README tham khảo](references/README.md): [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3815093). **Chưa đọc**, chưa có Markdown/PDF cục bộ.

- **Vấn đề:** theo tiêu đề: wash trading ở cryptocurrency exchanges.
- **Dữ liệu → Phương pháp → Kết quả → Hạn chế:** **chưa đọc / chưa xác minh**. Không suy diễn nghiên cứu dùng ERC-20 hoặc machine learning chỉ từ Related Work paper chính.
- **Mình dùng được gì:** dự kiến kiểm tra định nghĩa volume và phương pháp phát hiện; chưa đưa thành bằng chứng cho threshold.

## Phiếu tự kiểm sau đọc

Trả lời bằng một đoạn cho mỗi ý: (1) anomaly khác xác minh wash thế nào? (2) tại sao circular ratio không chứng minh ví cùng chủ? (3) timestamp nào được phép nằm trong feature? (4) vì sao 82,89% không đại diện thị trường? (5) trường hợp nào giá tăng +300% vẫn có giải thích hợp lệ? Lời giải nền và ví dụ ở roadmap; thông số nghiên cứu đề xuất ở PLAN sau khi kiểm tra nguồn API.
