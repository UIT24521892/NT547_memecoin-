# Lộ trình học nền và phân tích dữ liệu

**2026-10-01 [codex] — bản đầu, chờ duyệt.** Học theo thứ tự A→E. Tuần đầu ưu tiên A–B; các tầng sau là tài liệu chuẩn bị, chưa phải yêu cầu viết code ngay. Tất cả số trong bài tập là **ví dụ minh hoạ**, không phải dữ liệu token thật; mục 7 dùng ví dụ đã đối chiếu paper chính. Mỗi mục có ba tầng giải thích, bài tập và lời giải. Không cần gửi giao dịch để làm bài.

Nguồn nghiên cứu: [hướng dẫn đọc](READING_GUIDE.md). Nguồn nền chính thức được gắn ở từng mục; các giới hạn API cần xem PLAN, không suy ra từ bài học. Thuật ngữ cũ như Ethereum proof-of-work trong paper lịch sử không dùng làm mô tả hiện tại.

## Tầng A — Nền blockchain

### 1. Blockchain, block, transaction, address/wallet, gas fee

**Như trẻ 5 tuổi:** Cả lớp giữ nhiều bản giống nhau của một cuốn sổ. Khi có một việc mới, mọi người kiểm tra rồi ghi vào sổ; muốn ghi việc phải trả một khoản phí nhỏ.

**Học thuật:** Blockchain là chuỗi block liên kết bằng hash và được mạng xác nhận theo giao thức đồng thuận. Block chứa các transaction, có số thứ tự và timestamp. Transaction có thể thay đổi trạng thái; receipt/log cho biết kết quả và sự kiện. Address là định danh tài khoản; wallet quản lý khoá và chữ ký, không phải nơi vật lý chứa token. Một người có thể dùng nhiều address; một address cũng có thể do contract quản lý. Trên EVM, phí thực trả =`gasUsed × effectiveGasPrice` (đổi wei sang native coin); `gasLimit` là mức tối đa cho phép, khác lượng đã dùng. Đọc trạng thái qua RPC không phải gửi transaction.

**Đời thường:** Số tài khoản là địa chỉ nhận tiền; ứng dụng ngân hàng là ví; hoá đơn đóng dấu là receipt. Tên trong sổ không đủ cho biết ai điều khiển tài khoản.

**Bài tập:** Receipt minh hoạ có gasUsed=21.000, effectiveGasPrice=2 gwei. Phí bao nhiêu ETH? Địa chỉ nhận có phải chắc chắn một người riêng không?

**Lời giải:** 42.000 gwei =0,000042 ETH vì 1 gwei=10⁻⁹ ETH. Không; không suy ra danh tính hay số người từ số ví. Giữ block number/time, tx hash và status khi kiểm tra bằng chứng.

**Tham khảo:** [Ethereum transactions](https://ethereum.org/en/developers/docs/transactions/), [Cernera, phần nền](references/markdown/05_cernera_token_spammers_rug_pulls_2023.md).

### 2. EVM và Solana: account, mint authority, freeze authority

**Như trẻ 5 tuổi:** Hai trường dùng hai cách cất sổ điểm khác nhau. Một trường để mỗi món quà có cuốn sổ riêng; trường kia cất số quà của mỗi bạn trong một ngăn có nhãn.

**Học thuật:** EVM thực thi contract với state/storage; token ERC-20 thường ghi balance trong contract. Solana tách program thực thi khỏi data accounts: mint account mô tả token, token account giữ balance cho một mint và owner. Mint authority là quyền phát hành thêm; freeze authority là quyền đóng băng token account theo chương trình token. Mint address không đồng nghĩa ví creator. SPL Token và Token-2022 có khả năng khác nhau; authority vắng mặt không chứng minh mọi rủi ro đều hết.

**Đời thường:** EVM giống cửa hàng có sổ tồn kho chung; Solana giống từng thẻ kho riêng cho món hàng và người giữ. Người được phép in phiếu mới và người được phép khoá phiếu là hai quyền riêng.

**Bài tập:** Ba token account cùng một owner giữ cùng mint. Có phải ba holder? Mint authority đã bỏ thì có chắc bán được?

**Lời giải:** Khi đo holder theo owner, gộp về một holder, không đếm ba account. Bỏ mint authority chỉ hạn chế phát hành theo quyền đó; còn freeze, extension/logic, liquidity và đường giao dịch phải xem riêng.

**Tham khảo:** [Solana accounts](https://solana.com/docs/core/accounts), [token basics](https://solana.com/docs/tokens/basics).

### 3. ERC-20 / BEP-20 / SPL, Transfer, totalSupply, decimals

**Như trẻ 5 tuổi:** Một túi có 1.000 hạt nhỏ nhưng cửa hàng gọi mỗi 100 hạt là một phần. Phải biết cách chia này trước khi so sánh số phần của hai người.

**Học thuật:** ERC-20 quy định giao diện balance, supply, chuyển và allowance; BEP-20 dùng trong hệ EVM BSC; SPL dùng mint/token accounts. `amount_human=amount_raw/10^decimals`; decimals là đơn vị hiển thị, không phải mức giá. EIP-20 xem decimals là metadata tuỳ chọn; không mặc định bằng 18. `Transfer` log biểu diễn di chuyển lượng token giữa địa chỉ nhưng một transaction có thể có nhiều log. `totalSupply` không đồng nhất circulating supply. Rebase/tax/nonstandard tokens cần xử lý riêng khi tái tạo balances.

**Đời thường:** Đồng và nghìn đồng là hai cách ghi cùng số tiền; đổi nhầm đơn vị làm số trông lớn gấp nghìn lần.

**Bài tập:** amount_raw=12.345.000, decimals=6. Một transaction có bốn Transfer thì có phải bốn giao dịch mua?

**Lời giải:** 12,345 token. Không: có thể router, phí và chuyển trung gian; cần Swap và dòng tài sản để xác định giao dịch kinh tế.

**Tham khảo:** [EIP-20](https://eips.ethereum.org/EIPS/eip-20), [Solana token basics](https://solana.com/docs/tokens/basics).

### 4. Quyền contract: owner, mint, blacklist, tax, honeypot, proxy

**Như trẻ 5 tuổi:** Chủ cửa hàng có thể giữ chìa khoá để đổi luật mua bán. Biết người đó giữ chìa khoá giúp ta cẩn thận, nhưng chưa có nghĩa họ đã làm việc xấu.

**Học thuật:** Contract có thể trao quyền thay đổi supply, cấm chuyển, thay thuế hoặc nâng cấp implementation qua proxy. Owner renounce là bỏ một quyền owner cụ thể; roles, proxy admin và contract phụ vẫn có thể giữ quyền khác. Honeypot là tình huống người mua không thể bán theo điều kiện giao dịch tương ứng; cờ dịch vụ có thể sai hoặc phụ thuộc thời điểm. Phải đọc mã verified và quyền tại cutoff; capability là risk signal, khác hành vi đã xảy ra.

**Đời thường:** Tiệm có quyền đổi bảng giá không chứng minh tiệm đã thu sai. Khoá một cửa cũng không bảo đảm cửa sau đã khoá.

**Bài tập:** Owner đã về địa chỉ zero nhưng proxy admin còn quyền upgrade. Ghi “không còn quyền điều khiển” có đúng không?

**Lời giải:** Không. Ghi rõ quyền owner đã bỏ, quyền nâng cấp còn và nguồn/block quan sát; không suy diễn scam. Không thử mua/bán hay gửi transaction để kiểm tra.

**Tham khảo:** [Zhou, §2–3](references/markdown/08_zhou_stop_pulling_my_rug_2024.md), [Mazorra](references/markdown/06_mazorra_do_not_rug_on_me_2022.md).

### 5. Đọc một swap thật trên explorer

**Như trẻ 5 tuổi:** Muốn biết bạn đã đổi món gì, hãy xem hoá đơn ghi rõ nhận gì, đưa gì và cửa hàng nào. Dòng tiêu đề không đủ để biết toàn bộ việc đã xảy ra.

**Học thuật:** Explorer như Etherscan/BscScan/Basescan/Solscan lập chỉ mục dữ liệu chuỗi. Với một swap thật, đọc chain, tx hash, status, block time, người gửi, contract gọi, logs và token movements. Trên EVM, `tx.to` có thể là router; `Swap.sender` có thể là contract trung gian. Trader quy về `tx_from` chỉ là một lựa chọn, cần cảnh báo smart wallet/aggregator. Một transaction có thể nhiều pool/hop, vì vậy lưu `log_index` để phân biệt.

**Đời thường:** Hoá đơn tổng ghi tên siêu thị, nhưng bên trong có nhiều quầy; số quầy không phải số khách.

**Bài tập thực hành:** Vào [Basescan](https://basescan.org/), chọn một transaction đã thành công của pool được xác nhận có event Swap. Điền chain, hash, UTC time, router, pool phát log, token vào/ra, fee. Chỉ đọc; không nối ví. Phiên này chưa chọn và xác minh một hash mẫu, không chèn hash giả.

**Lời giải/checklist:** Status=success; pool phải là address phát Swap, không tự lấy `tx.to`; lượng token được chia đúng decimals; tìm Transfer tương ứng và nhận diện multi-hop; ghi URL `/tx/<hash>` thật, block và log index. Nếu không giải mã được event hoặc không xác nhận loại pool, đánh dấu “không rõ”, giữ log thô. Số liệu cụ thể phụ thuộc transaction sinh viên chọn; bài tập chỉ hoàn thành khi điền đủ bằng chứng đó.

**Tham khảo:** [Ethereum receipts/transactions](https://ethereum.org/en/developers/docs/transactions/), [Uniswap V2](references/markdown/10_uniswap_v2_whitepaper.md).

## Tầng B — DeFi và AMM

### 6. DEX, liquidity pool, LP token, lock/burn LP

**Như trẻ 5 tuổi:** Một quầy đổi có hai giỏ hàng để khách đổi qua lại. Người góp hàng nhận phiếu ghi phần của mình; giữ phiếu thì có thể lấy lại phần hàng theo luật của quầy.

**Học thuật:** DEX là giao thức trao đổi tài sản; pool giữ tài sản cho cơ chế AMM. Với V2, LP token đại diện tỷ lệ đóng góp, cho phép redeem dự trữ. Lock LP hạn chế rút trong thời gian/điều kiện contract; burn LP gửi quyền đó đến địa chỉ không thể sử dụng theo giả định đã kiểm tra. Không nhầm burn **LP token** với burn **meme token**, cũng không nhầm với event `Burn` khi redeem pool. Lock không ngăn mint token vô hạn hoặc creator bán lượng token lớn; V3 thường biểu diễn position qua NFT ở periphery.

**Đời thường:** Phiếu góp vốn quầy hàng khác phiếu hàng bán cho khách. Cất phiếu góp vốn trong két hẹn giờ không ngăn chủ in thêm phiếu hàng.

**Bài tập:** 1.000 LP token, creator giữ 800. Có 10.000 meme token bị burn. LP có tự động bị khoá không?

**Lời giải:** Creator giữ 80% LP; burn meme không khoá LP. Cần địa chỉ locker, lượng LP, thời gian mở khoá và block chứng minh. Quyền rút chỉ áp dụng phần LP thực sự khoá.

**Tham khảo:** [Uniswap V2](references/markdown/10_uniswap_v2_whitepaper.md), [Cernera, §3/§7](references/markdown/05_cernera_token_spammers_rug_pulls_2023.md).

### 7. Constant product AMM, giá, price impact, slippage — bài +300%

**Như trẻ 5 tuổi:** Quầy đổi có ít đồ thì lấy đi một nửa sẽ khiến phần còn lại đắt hơn nhiều. Bảng giá cuối quầy không phải giá trung bình bạn đã trả cho cả túi hàng.

**Học thuật:** Mô hình pool V2 lý tưởng không phí: x là lượng quote (ETH), y là MEME, `xy=k`. Giá biên MEME theo ETH là `p=x/y`. Mua q MEME, `0<q<y`, làm `y'=y−q`, `x'=k/(y−q)`, quote phải trả `Δx=x'−x`. Vì vậy `p'/p=(y/(y−q))²`; đây là tăng giá spot cuối, không phải giá thực hiện trung bình `Δx/q`. Price impact là thay đổi giá do chính kích thước lệnh; slippage là lệch giữa báo giá kỳ vọng và kết quả thực hiện (có thể gồm thay đổi thị trường giữa hai thời điểm), không dùng hai từ thay nhau.

**Đời thường:** Mua nhiều ghế ở quầy nhỏ làm giá chiếc ghế cuối tăng. Giá trung bình của cả đơn và chênh do quầy đổi giá trong lúc bạn chờ là hai phép tính khác nhau.

**Bài tập bắt buộc:** Pool x=0,01 ETH, y=100 MEME. Mua 50 MEME, không phí, không tax. Tính k, ETH cần nạp, spot trước/sau, giá mua trung bình, % tăng spot. Tính nếu chỉ mua 10 MEME.

**Lời giải:** k=1 ETH·MEME. Với q=50: y'=50, x'=0,02 ETH; nạp 0,01 ETH; p=0,0001 và p'=0,0004 ETH/MEME. Tăng `(4−1)×100%=300%`, tức giá sau bằng **400%** giá trước. Trung bình 0,01/50=0,0002 ETH/MEME, cao hơn spot trước 100%. Với q=10: y'=90, x'=1/90≈0,011111 ETH; nạp≈0,001111; p'≈0,000123457; tăng spot≈23,4568%. Pool nhỏ có thể tăng mạnh do mua hợp lệ; cần hành vi và liquidity để kết luận risk.

**Mở rộng hiểu phí:** Với phí f trên quote đầu vào a, lượng ra `q=y·a(1−f)/(x+a(1−f))`; reserve quote thực tế thường nhận toàn a. Không áp dụng `k` cố định trước/sau khi có phí, mint/burn, tax hoặc rebase. Fee của từng fork phải kiểm tra, không mặc định bằng V2 gốc.

**Mở rộng lệnh $100:** Đổi $100 thành quote theo giá quote/USD **tại cutoff**, tính q theo pool/fee. Impact giá thực hiện so spot là `(a/q)/p−1`; công thức này bao gồm phí nếu dùng toàn a, nên báo riêng hoặc ghi rõ. Không lấy FDV thay reserve và không giả vờ mô phỏng pool V3 bằng công thức này.

**Tham khảo:** [paper chính §5.3, PDF 12](references/papers/01_mongardini_mei_midsummer_meme_2026.pdf), [audit](THRESHOLD_AUDIT.md), [V2 whitepaper](references/markdown/10_uniswap_v2_whitepaper.md).

### 8. Swap, Mint, Burn, Sync; V3 concentrated liquidity

**Như trẻ 5 tuổi:** Quầy ghi riêng lúc đổi hàng, góp thêm hàng, lấy vốn về và kiểm kê giỏ. Có quầy chỉ nhận đổi ở một khoảng giá nên nhìn tổng hàng chưa biết quầy đổi được bao nhiêu.

**Học thuật:** Với V2-style: `Swap` ghi lượng vào/ra, `Mint` thêm liquidity, `Burn` redeem liquidity, `Sync` cập nhật reserve. Cần sắp thứ tự `(block_number,transaction_index,log_index)`; Sync cung cấp reserve để tính trạng thái sau sự kiện. Với V3, liquidity được tập trung theo khoảng, swap qua tick đổi liquidity đang hoạt động. Virtual reserves trong một khoảng khác tổng balance thực của pool; giá/impact cần state tương ứng và decimals. Công thức V3 chi tiết **chưa xác minh PDF** ở phiên này.

**Đời thường:** Tiệm có kho 1.000 món nhưng chỉ 100 món đang bán ở mức giá bạn hỏi; tổng kho không bằng hàng sẵn ở quầy.

**Bài tập:** Token balances V3 cho tỷ lệ 2:1. Có thể dùng luôn làm spot price V2 không? Một Burn pool có chứng minh rug không?

**Lời giải:** Không; cần price/tick/liquidity active và cơ chế pool. Burn có thể rút LP hợp lệ; phải xem tỷ lệ rút, actor, lịch sử, migration, và trạng thái giao dịch sau đó.

**Tham khảo:** [V2](references/markdown/10_uniswap_v2_whitepaper.md), [V3 §2](references/markdown/11_uniswap_v3_whitepaper.md).

### 9. Solana: bonding curve, migration, Jito bundle

**Như trẻ 5 tuổi:** Có quầy định giá theo số món đã bán, rồi chuyển sang một quầy khác khi đủ điều kiện. Một người cũng có thể xin xử lý một nhóm việc theo thứ tự cùng nhau.

**Học thuật:** Bonding curve đặt quan hệ giá–supply/reserve theo một hàm; migration chuyển thanh khoản/cơ chế sang DEX theo quy tắc nền tảng tại thời điểm đó. Jito bundle nhóm transaction với cơ chế xử lý có thứ tự; bundle không tự là manipulation. Chi tiết pump.fun đích migration/điều kiện có thể đổi; phiên này chỉ dạy khái niệm, **chưa xác minh** thông số triển khai hiện hành, không mặc định luôn chuyển sang một DEX cụ thể.

**Đời thường:** Cửa hàng thử nghiệm chuyển hàng sang siêu thị; khách cần theo cả hai nơi để không tưởng hàng đã biến mất.

**Bài tập:** Pool cũ hết liquidity đúng khi pool mới nhận liquidity. Có đủ cơ sở gán rug không?

**Lời giải:** Chưa; kiểm tra migration, transaction liên kết và khả năng giao dịch ở pool mới. Chỉ coi mất pool cũ là dấu hiệu cần kiểm tra, không target tự động.

**Tham khảo:** [paper chính §3/§5.1](references/markdown/01_mongardini_mei_midsummer_meme_2026.md), [Solana token basics](https://solana.com/docs/tokens/basics).

### 10. Market cap, FDV và liquidity

**Như trẻ 5 tuổi:** Một chiếc kẹo vừa bán được giá cao không có nghĩa mọi viên trong kho đều bán được giá ấy. Nếu quầy chỉ có ít tiền, bạn không thể đổi cả kho lấy số tiền trên bảng.

**Học thuật:** Market cap=`price × circulating supply`; FDV thường=`price × fully diluted supply` (nguồn có thể dùng total/max supply khác nhau). Liquidity USD là giá trị tài sản trong pool theo cách định giá công bố, không phải lượng quote có thể rút bằng bán token ở giá spot. Spot price của pool nhỏ có thể làm FDV rất lớn; dữ liệu circulating supply không rõ phải ghi thiếu, không thay bằng totalSupply rồi gọi market cap.

**Đời thường:** Giá niêm yết căn nhà nhân số nhà trong khu không bằng tiền mặt đang sẵn để mua tất cả.

**Bài tập:** Giá $0,01; circulating=10 triệu; fully diluted=100 triệu; pool có $1.000 quote. Market cap, FDV là gì; có bán cả supply lấy $1 triệu không?

**Lời giải:** Market cap=$100.000; FDV=$1.000.000. Không: reserve và price impact giới hạn lượng tiền thu được; chưa kể tài sản/giá quote có thể thay đổi.

**Tham khảo:** [paper chính §4.1.2/§5.3](references/markdown/01_mongardini_mei_midsummer_meme_2026.md).

## Tầng C — Thao túng thị trường

### 11. Wash, LPI, pump & dump, rug, sniper, bundle, airdrop tập trung

**Như trẻ 5 tuổi:** Một người có thể giả làm nhiều khách để quầy trông đông, hoặc đổi ít hàng ở quầy nhỏ làm bảng giá nhảy lên. Sau đó việc lấy tiền và bỏ quầy là chuyện khác, cần nhìn thấy bằng chứng riêng.

**Học thuật:** Wash tạo volume qua giao dịch phối hợp ít thay đổi vị thế; LPI khai thác độ nhạy giá pool ít thanh khoản; pump & dump là nâng giá phối hợp rồi bán gây sụp; rug thường liên quan rút liquidity hoặc quyền hợp đồng gây mất khả năng giao dịch. Sniper bot mua ngay lúc ra mắt, bundle nhóm transaction, airdrop phân phối miễn phí; ba hoạt động sau không tự động bất hợp lệ. Supply tập trung >30% là cờ paper, không chứng minh các ví cùng chủ. Các rule đầy đủ và phần **chưa xác minh** ở audit.

**Đời thường:** Khách xếp hàng giả, thay bảng giá và chủ lấy vốn quầy là ba hành vi khác nhau; phát phiếu quà tặng cũng có thể hoàn toàn hợp lệ.

**Bài tập:** Một maker mua $101 và bán $99 trong ngày, tổng volume toàn token=$10.000. Có circular ratio ≥99% không nếu chỉ maker đó có cả mua/bán?

**Lời giải:** Maker có chênh USD `|101−99|/200=1%`, đạt rule zero-risk notebook nếu ngày đã qua sàng lọc. Circular ratio=200/10.000=2%, không đạt. Đây là dấu hiệu cần kiểm tra, không phải chắc chắn cùng chủ/không rủi ro thực.

**Tham khảo:** [paper chính §5–6](references/markdown/01_mongardini_mei_midsummer_meme_2026.md), [DATASET_NOTES.md](DATASET_NOTES.md).

### 12. Phân biệt tăng trưởng hợp lệ và manipulation

**Như trẻ 5 tuổi:** Quầy đông có thể vì món hàng được nhiều người thích. Trước khi nói có khách giả, phải xem khách thật và việc mua bán.

**Học thuật:** False positive là gắn cờ khi hiện tượng có giải thích hợp lệ. Giá tăng/volume tăng chỉ là screening; cần kiểm tra ví, liquidity, dòng swap, niêm yết/tin tức theo đúng ngày. Nhóm C là đối chứng tham chiếu, vẫn cần kiểm tra; không có cờ không bằng chứng minh hợp lệ. Baseline “price spike=risk” chỉ phục vụ so sánh, không xuất cảnh báo kết luận cho người dùng.

**Đời thường:** Tiệm nail đông sau khuyến mãi là bình thường; lượng khách đông riêng lẻ không đủ nói tiệm thuê người đóng vai.

**Bài tập:** Giá +150%, trader đa dạng, pool sâu, có tin niêm yết đúng ngày. Có gán manipulation chỉ từ +150% không?

**Lời giải:** Không. Ghi bối cảnh và bằng chứng, kiểm tra wash/LPI/creator/LP; nếu chưa đủ, nhãn “không rõ” hoặc tham chiếu hợp lệ có lý do, không khẳng định chắc chắn.

**Tham khảo:** [paper chính §5.1/§5.4/§7](references/markdown/01_mongardini_mei_midsummer_meme_2026.md).

## Tầng D — Dữ liệu và phân tích

### 13. REST API, pagination, rate limit, cache, SQL Dune

**Như trẻ 5 tuổi:** Thư viện chỉ đưa một tập sách mỗi lần và giới hạn số lần hỏi. Hãy nhớ sách đã mượn để không hỏi lại mãi.

**Học thuật:** REST endpoint trả tài nguyên theo request; pagination chia kết quả qua trang/cursor. Rate limit giới hạn tần suất; cache lưu response theo request chuẩn hoá và thời điểm thu, retry/backoff xử lý lỗi có giới hạn. HTTP 429 cần tôn trọng hướng dẫn dịch vụ; không coi lỗi/empty response là zero volume. Dune SQL lọc token/thời gian trước aggregation; credit và khả năng API theo plan hiện hành phải kiểm tra. Chuẩn bị manifest `source,request,queried_at,coverage,status`.

**Đời thường:** Lấy số thứ tự ở thư viện, nghỉ khi quầy bận, cất bản sao sách đã nhận; không ghi “không có sách” khi quầy chưa trả lời.

**Bài tập:** Cần 250 dòng, mỗi trang trả 100; trang hai bị 429. Có được chỉ ghép trang 1/3 rồi báo đầy đủ không?

**Lời giải:** Tối thiểu ba trang nếu đủ kết quả. Không; retry/backoff hữu hạn theo policy, lưu coverage thiếu nếu vẫn lỗi, resume từ cache/cursor. Không viết collector ở phiên này.

**Tham khảo:** [SQL artifact](references/dataset/meme_coin_anon-main/dune_queries/), [DATASET_NOTES.md](DATASET_NOTES.md); limits hiện hành được ghi ở PLAN.

### 14. Time series, pandas, resample, rolling window, OHLCV

**Như trẻ 5 tuổi:** Gộp hoá đơn theo ngày giúp biết ngày đó bắt đầu bán giá nào, cao/thấp nhất và bán tổng bao nhiêu. Một ô trống không có nghĩa cửa hàng bán bằng không.

**Học thuật:** OHLCV gồm open/high/low/close/volume theo interval. Resample tổng hợp về nhịp thời gian; rolling tính thống kê cửa sổ trượt. Phải sắp timestamp UTC, định nghĩa biên interval, tính open/close từ quan sát đầu/cuối, volume bằng tổng. Dữ liệu bar chỉ được dùng khi interval đã kết thúc ≤ cutoff; không dùng rolling có tâm hoặc bfill từ tương lai.

**Đời thường:** Báo cáo doanh thu cả ngày không được đưa vào dự báo lúc 9 giờ sáng hôm đó.

**Bài tập:** Ba swap trong ngày có giá 2,5,3 và volume USD 10,20,30. OHLCV? Cutoff giữa ngày có dùng bar cả ngày không?

**Lời giải:** O=2,H=5,L=2,C=3,V=60. Không; tổng hợp partial window riêng hoặc chỉ dùng ngày đã đóng. Ngày thiếu không tự forward-fill volume.

**Tham khảo:** [pandas time series](https://pandas.pydata.org/docs/user_guide/timeseries.html), [paper chính §5](references/markdown/01_mongardini_mei_midsummer_meme_2026.md).

### 15. Top-k, HHI, Gini, Nakamoto coefficient

**Như trẻ 5 tuổi:** Nếu một bạn giữ gần hết bánh thì nhóm rất phụ thuộc vào bạn ấy. Đếm số người chưa đủ; phải xem mỗi người giữ bao nhiêu.

**Học thuật:** Với share s_i không âm, tổng=1: top-k=`Σ_(i=1..k) s_(i)` sau sắp giảm; HHI=`Σs_i²`. Gini cho balances b_i, n ví và tổng B>0 là `Σ_iΣ_j|b_i−b_j|/(2nB)`. Nakamoto coefficient của đồ án là số ví nhỏ nhất có tổng share **vượt một ngưỡng τ được công bố**; không có τ mặc định chung cho token. Phải ghi universe và denominator: supply toàn token hay tổng balance holder đủ điều kiện sau loại pool/burn/CEX.

**Đời thường:** Chia bánh cho lớp: một bạn cầm 60%, hai bạn 20% mỗi người khác hẳn ba bạn chia đều.

**Bài tập:** Balances 60,20,20, tổng 100; top-1, HHI, Gini, số ví vượt 50%?

**Lời giải:** Top-1=0,6; HHI=0,36+0,04+0,04=0,44; tổng chênh lệch đôi có thứ tự=160 nên Gini=160/(2·3·100)=0,2667; một ví vượt 50%. Nếu pool nằm trong 60 thì phải tính lại và ghi denominator, không âm thầm đổi.

**Tham khảo:** [Mazorra, concentration features](references/markdown/06_mazorra_do_not_rug_on_me_2022.md), [paper chính §5.1](references/markdown/01_mongardini_mei_midsummer_meme_2026.md).

### 16. Directed graph, reciprocity, cycle, SCC, community, networkx

**Như trẻ 5 tuổi:** Vẽ mũi tên cho biết ai đưa đồ cho ai. Nếu đồ đi quanh rồi quay về, ta kiểm tra thêm; một vòng tròn chưa chứng minh các bạn cùng đóng kịch.

**Học thuật:** Directed graph có nodes và cạnh có hướng; transfer graph dùng cạnh sender→receiver. Reciprocity là tỷ lệ cạnh có chiều ngược tương ứng theo định nghĩa công bố; cycle là đường khép kín; SCC là tập cực đại mà mọi node đi tới nhau được bằng đường có hướng; community là nhóm kết nối theo thuật toán, khác SCC. AMM swap nên dùng trader–pool hoặc maker/day incidence graph; không suy ra trader A bán trực tiếp cho B chỉ vì cùng pool. Funding graph cần nguồn nạp trước cutoff và loại dịch vụ lớn.

**Đời thường:** Sơ đồ chuyền vở A→B→C→A khác ba bạn cùng mua ở một nhà sách.

**Bài tập:** Cạnh A→B, B→A, B→C, C→A. SCC lớn nhất, chu trình 2/3, reciprocity không trọng số?

**Lời giải:** SCC={A,B,C}; cycle 2 là A→B→A; cycle 3 là A→B→C→A. Có 2/4 cạnh được đáp lại nên reciprocity=0,5 theo định nghĩa này. Cần lượng/thời gian để kiểm tra cân bằng, không tự gán wash.

**Tham khảo:** [Victor §4–5](references/markdown/02_victor_weintraud_wash_trading_dex_2021.md), [La Morgia §IV](references/markdown/03_la_morgia_game_of_nfts_2023.md), [networkx](https://networkx.org/documentation/stable/).

### 17. RSI, return, volatility, drawdown, Amihud illiquidity

**Như trẻ 5 tuổi:** Nhìn các ngày tăng giảm giúp biết giá có nhảy nhiều không và đã rơi xa đỉnh bao nhiêu. Những con số này mô tả chuyển động, không nói ai cố tình làm giá.

**Học thuật:** Simple return `r_t=P_t/P_(t−1)−1`; volatility là độ lệch chuẩn return trên cửa sổ đã biết. Drawdown `D_t=1−P_t/max_(u≤t)P_u`; max drawdown là max D trên cửa sổ. RSI=`100−100/(1+RS)` với RS là average gain/average loss theo kỳ và smoothing công bố. Amihud proxy=`mean(|r_t|/V_t_USD)` trên V>0; đây là proxy, không thay mô phỏng price impact. RSI>80 của paper đã xác minh, kỳ/smoothing của paper **chưa xác minh**.

**Đời thường:** Nhiệt kế đo nóng lạnh không biết ai bật máy sưởi; giá nhảy mạnh không cho biết ý định.

**Bài tập:** Giá 100→120→90, volume $1.000 mỗi kỳ. Hai return, max drawdown và Amihud?

**Lời giải:** +20%, −25%; max drawdown=1−90/120=25%; mean(0,2/1000,0,25/1000)=0,000225 USD⁻¹. Với average gain=2/loss=1 minh hoạ thì RSI≈66,67; chưa gán kỳ RSI cụ thể.

**Tham khảo:** [paper chính §6.2](references/markdown/01_mongardini_mei_midsummer_meme_2026.md), [Xu, market features](references/markdown/04_xu_livshits_pump_dump_anatomy_2019.md).

## Tầng E — Học máy và đánh giá

### 18. Mất cân bằng lớp; logistic regression, RF/boosting, isolation forest

**Như trẻ 5 tuổi:** Nếu lớp chỉ có một bạn cần giúp, nói “không ai cần” gần như luôn đúng nhưng chẳng giúp được bạn ấy. Cần kiểm tra riêng xem có tìm được những bạn cần giúp không.

**Học thuật:** Class imbalance là tỷ lệ nhãn chênh lớn. Logistic regression `p=σ(β₀+βᵀx)` cho quan hệ tuyến tính trên log-odds; random forest gộp cây học song song; boosting thêm mô hình để sửa lỗi trước; isolation forest tìm điểm dễ tách như anomaly, không trực tiếp học nhãn rug. Imputation/scaling/class weight chỉ fit trên train; không synthetic oversample trước temporal split. Risk score rule không mặc định xác suất.

**Đời thường:** Bộ lọc thư rác chỉ nói mọi thư là bình thường thì dễ bỏ sót thư cần cảnh báo.

**Bài tập:** 1.000 token, 10 có target dương. Mô hình luôn âm có accuracy và recall dương bao nhiêu?

**Lời giải:** Accuracy=990/1000=99%; recall=0/10=0. Precision của lớp dương không xác định vì không dự đoán dương; công bố quy ước xử lý. Không dùng 99% làm bằng chứng detector tốt.

**Tham khảo:** [Mazorra §7](references/markdown/06_mazorra_do_not_rug_on_me_2022.md), [scikit-learn guide](https://scikit-learn.org/stable/user_guide.html).

### 19. Data leakage, temporal split và walk-forward

**Như trẻ 5 tuổi:** Làm bài kiểm tra phải dùng điều đã biết trước khi nhận đáp án. Nếu lấy đáp án ngày mai để đoán hôm nay, điểm cao sẽ không có ích.

**Học thuật:** Cutoff c giới hạn feature data/event time và thời điểm thông tin có thể biết; target dùng `(c,c+H]`. Temporal split train sớm, validation sau, test cuối; gap≥H để horizon nhãn không chồng lấn. As-of gồm event time **và availability**: sự kiện ngày c nhưng chỉ xác nhận sau c không được xem là đã biết tại c. Walk-forward lặp huấn luyện với lịch sử mở rộng, giữ nguyên thứ tự. Group token để không lọt các cửa sổ trùng nhau; test cuối một lần.

**Đời thường:** Giáo viên phát đề theo tuần; không dùng ghi chú tuần sau hay đáp án của bạn cùng đề để tự chấm tuần trước.

**Bài tập:** Cutoff 1/8 UTC, H=14 ngày. GoPlus gọi 1/10 trả cờ mint. Dùng cho mẫu 1/8 được không? Label 20/8 nằm trong target không?

**Lời giải:** Không, trừ khi tái tạo được state/as-of 1/8. Target kết thúc 15/8 cùng giờ, nên 20/8 ngoài horizon. Nếu không quan sát đủ tới 15/8, mẫu bị censored (chưa biết kết cục), không gán âm.

**Tham khảo:** AGENTS.md §9–10, [Mazorra hai thiết kế đánh giá](references/markdown/06_mazorra_do_not_rug_on_me_2022.md), [PLAN.md](PLAN.md).

### 20. Precision, recall, PR-AUC, precision@k, calibration, confusion matrix

**Như trẻ 5 tuổi:** Trong các bạn được gọi là cần giúp, có bao nhiêu bạn thật sự cần? Trong mọi bạn cần giúp, đã tìm được bao nhiêu? Hai câu này khác nhau.

**Học thuật:** Precision=`TP/(TP+FP)`, recall=`TP/(TP+FN)`; confusion matrix ghi TP/FP/TN/FN tại threshold đã chọn. PR curve đổi threshold; average precision (AP) và diện tích PR tích phân có cách tính khác, phải công bố dùng cái nào. Precision@k là tỷ lệ dương trong k điểm cao nhất. Calibration kiểm tra xác suất dự báo với tần suất quan sát; score 80/100 theo rule không tự có nghĩa 80% xác suất rug. Báo cỡ mẫu và khoảng bất định, đặc biệt khi ít dương.

**Đời thường:** Danh sách 10 học sinh được mời phụ đạo có thể tìm đúng 8 bạn nhưng vẫn bỏ sót nhiều bạn khác.

**Bài tập:** TP=8,FP=2,FN=12,TN=78; top-5 có 4 dương. Tính precision, recall, precision@5.

**Lời giải:** 80%,40%,80%. Precision cao chưa bảo đảm recall cao. Calibration cần nhiều dự báo/xác suất và nhãn, không suy ra từ một confusion matrix.

**Tham khảo:** [scikit-learn metrics](https://scikit-learn.org/stable/modules/model_evaluation.html), [Xu, mô hình dự báo](references/markdown/04_xu_livshits_pump_dump_anatomy_2019.md).

### 21. Manual labels, codebook, Cohen's kappa

**Như trẻ 5 tuổi:** Hai bạn xem cùng hoá đơn phải dùng cùng quy tắc để ghi nhận xét. Nếu mỗi người hiểu luật khác nhau, chữ “đúng” sẽ không có cùng nghĩa.

**Học thuật:** Codebook định nghĩa nhãn, tiêu chí, nguồn và quy tắc “không rõ”. Manual validation lấy mẫu phân tầng gồm mạnh/gần ngưỡng/âm và tăng mạnh risk thấp; làm mù score khi có thể. Cohen's kappa `κ=(p_o−p_e)/(1−p_e)` đo thoả thuận hai annotator sau trừ mức kỳ vọng từ phân bố nhãn. Một annotator gán lại 20% sau ≥3 ngày đo độ nhất quán cá nhân; không gọi là inter-annotator agreement. Precision mẫu phân tầng cần báo theo tầng hoặc có trọng số xác suất lấy mẫu.

**Đời thường:** Hai người chấm bài dùng rubric chung; sau đó xem chỗ bất đồng và bằng chứng trước khi chốt.

**Bài tập:** 100 mẫu, mỗi người gán 50 dương/50 âm, thoả thuận 80 mẫu. κ? Nếu chỉ xem positive rất mạnh, có suy precision toàn hệ thống được không?

**Lời giải:** p_o=0,8,p_e=0,5 nên κ=0,6. Không: mẫu chọn mạnh thiên lệch; báo sampling và tầng, giữ “không rõ” thay ép vào âm. Mọi nhãn có evidence links, thời điểm và người gán.

**Tham khảo:** AGENTS.md §11; [Zhou, phân tích sự cố](references/markdown/08_zhou_stop_pulling_my_rug_2024.md).

### 22. Feature importance và SHAP cho risk score

**Như trẻ 5 tuổi:** Khi đưa ra điểm cảnh báo, hãy nói những dấu hiệu nào đã làm điểm tăng. Lý do máy dùng không có nghĩa dấu hiệu đó đã gây ra chuyện xấu.

**Học thuật:** Feature importance mô tả đóng góp ở mức mô hình/tập dữ liệu; SHAP phân bổ thay đổi dự báo theo feature so với background bằng giá trị Shapley và giả định phù hợp. Với cách giải thích được chọn, `prediction=base+Σcontributions` trên thang output công bố (có thể log-odds, không phải phần trăm). Feature tương quan và background làm ảnh hưởng diễn giải. Risk score có reasons/evidence; giải thích không chứng minh nhân quả và không bù được leakage.

**Đời thường:** Giáo viên giải thích điểm bằng từng tiêu chí; trọng số chấm điểm không phải nguyên nhân học sinh làm bài theo cách đó.

**Bài tập:** Ví dụ giải thích trên log-odds: base=−2, wash +1, concentration +0,5, liquidity −0,2. Output log-odds và xác suất? Có cộng “+1” thành 100 điểm không?

**Lời giải:** Log-odds=−0,7; sigmoid≈0,3318. Không; phải đúng thang đo. Với rule score, reasons có thể là đóng góp trọng số đã công bố, không cần giả gọi là SHAP. Chỉ xuất cảnh báo có ít nhất một bằng chứng hành vi, không dùng giá tăng đơn lẻ.

**Tham khảo:** [SHAP documentation](https://shap.readthedocs.io/en/latest/), AGENTS.md §9/§12.

## Điểm dừng học nền

Sinh viên thử trả lời bài 1, 3, 5, 6, 7, 8 và giải thích được “giá tăng ≠ manipulation”. Chưa cần học mọi mô hình ngay. Bài explorer là thực hành đang chờ một transaction thật; không ghi đã hoàn thành hộ sinh viên. Chỉ chuyển sang collector sau duyệt phạm vi và chứng minh lấy được dữ liệu lịch sử cần thiết.
