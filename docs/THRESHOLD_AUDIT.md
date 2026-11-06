# Đối chiếu ngưỡng paper chính

Ngày: **2026-10-01 [codex]**. Đọc nội dung qua [bản Markdown](references/markdown/01_mongardini_mei_midsummer_meme_2026.md); đối chiếu trực quan các trang 9, 10, 12, 13 của [PDF gốc](references/papers/01_mongardini_mei_midsummer_meme_2026.pdf). Trang in = trang PDF + 3929; PDF có một trang bìa. Không dùng bản Markdown làm bằng chứng cuối cùng cho dấu bất đẳng thức.

## 1. Kết quả từng ngưỡng

| Chỉ báo | Kết quả đối chiếu PDF | Vị trí | Phần chưa xác minh / cần định nghĩa trước khi lập trình |
|---|---|---|---|
| Top holders | >30% supply; phần mô tả và Tab. 3 xác nhận top-10 | §5.1.1, trang in 3938–3939 / PDF 9–10 | Danh sách pool/burn/CEX loại trừ và mẫu số supply sau loại trừ |
| Bundle buy | >30% supply | §5.1.1, 3938 / PDF 9 | Cách xác định nhóm bundle trên EVM |
| Fresh address | >30%; ví không có lịch sử trước đó | §5.1.1, 3938 / PDF 9 | Phạm vi lịch sử dùng để khẳng định ví mới |
| Airdrop | >30% supply phân bổ qua airdrop | §5.1.1, 3938 / PDF 9 | Phân biệt phát thưởng hợp lệ và ví cùng chủ |
| Wash: sàng lọc | Volume tăng >500% so hôm trước; biến động giá tuyệt đối <5% | §5.2.1, 3939 / PDF 10 | Chọn giá close hay giá khác; xử lý volume hôm trước bằng 0 |
| Wash: zero-risk | Mua và bán gần cùng lượng token/ngày; cho phép chênh 2% | §5.2.2, 3939 / PDF 10 | **Chưa xác minh** mẫu số chuẩn hoá, dấu `<`/`≤`, đơn vị lượng so sánh trong notebook. Không gọi là không có rủi ro kinh tế thật: vẫn có phí, tồn kho trong ngày |
| Wash: circular volume | ≥99% volume ngày từ maker có cả mua và bán | §5.2.2, 3939 / PDF 10 | Cách cộng volume và tránh đếm đôi nhiều hop; không phải bằng chứng chu trình ví–ví |
| Wash: coordinated | Maker có mặt ở mọi ngày wash phát hiện của token | §5.2.2, 3939 / PDF 10 | Số ngày tối thiểu và tập ngày sàng lọc/xác minh **chưa xác minh**; chỉ dùng ngày ≤ cutoff |
| LPI: sàng lọc | Giá tăng >100%/24h và (volume tăng ≤20% so hôm trước hoặc volume <$1.000) | §5.3.1, 3941 / PDF 12 | Đồng bộ giá/volume theo UTC, volume trước bằng 0; đây chỉ là ứng viên |
| LPI: xác minh | Buy volume ≥90% tổng volume/ngày và số trader ≤10 | §5.3.1, 3941 / PDF 12 | Maker/router/aggregator được quy về trader thế nào; reserve và quote USD tại thời điểm đó |
| Rug pull | Giá giảm >99%/ngày và volume giảm >99% duy trì các ngày sau | §6.1, 3942 / PDF 13 | Số ngày duy trì, volume tham chiếu **chưa xác minh**; thiếu dữ liệu không bằng volume 0; cần log rút LP để củng cố nhãn |
| Pump & dump | RSI >80; đáy trong 24h trước đỉnh; pump >50%, volume tăng >500%, thời gian ≤24h; dump >30%; volume trung bình sau dump <50% volume pump | §6.2, 3942 / PDF 13 | Cửa sổ/smoothing RSI, mẫu số tăng volume, độ dài dump/post-dump **chưa xác minh** |

**Sửa AGENTS.md:** các con số tóm tắt không có sai lệch rõ so PDF; bỏ khẳng định dấu `≤2%` chưa được PDF định nghĩa bằng công thức; làm rõ volume **trung bình** sau dump, thêm đáy trước đỉnh và các chỗ chưa xác minh. Sửa dẫn chiếu deliverable lượt đầu từ Mục 14 sang Mục 15. Không sửa bản Markdown nguồn hay dataset tác giả.

## 2. Quy ước đề xuất của đồ án (chờ duyệt)

Với dữ liệu daily có ngày trước đầy đủ: `gV = V_t / V_(t−1) − 1`, `r = P_t / P_(t−1) − 1`. Do đó **tăng >500%** nghĩa là `gV > 5`, tức `V_t > 6 V_(t−1)`, khác `V_t > 5 V_(t−1)`. Đây là cách diễn giải phần trăm của đồ án; phải đối chiếu notebook trước khi tuyên bố tái lập đúng mã tác giả. Chọn close-to-close UTC là đề xuất, không phải chi tiết đã xác minh của PDF. Thiếu nến/volume gốc bằng 0 → đánh dấu không đủ dữ liệu, không tự chia hoặc điền 0.

Khi code ở giai đoạn sau, ngưỡng đã xác minh chuyển sang `configs/thresholds.yaml`; mọi quyết định còn thiếu phải có nguồn hoặc nhãn `project_choice`, kiểm tra biên và sensitivity trên train/validation. Hiện chưa tạo cấu hình detector. Bước đọc artifact sau đó xác định công thức zero-risk trong notebook là `abs(B−S)/(B+S)*100 <= 2` trên USD, coordinated yêu cầu hơn một ngày, và circular dùng `>99` thay vì `≥99` trong PDF. Xem [ghi chú dataset](DATASET_NOTES.md); phân biệt xác minh **mã** với xác minh **PDF**.

## 3. Ví dụ AMM đã đối chiếu

§5.3, trang in **3941 / PDF 12**: pool 0,01 ETH và 100 MEME, bỏ qua phí. Giữ ký hiệu nhất quán: x là ETH, y là MEME, k=xy=1. Mua 50 MEME làm y'=50; x'=1/50=0,02 ETH. ETH nạp thêm =0,01. Giá tức thời trước =x/y=0,0001 ETH/MEME; sau =x'/y'=0,0004; `(0,0004/0,0001−1)×100%=300%`. Giá khớp trung bình =0,01/50=0,0002, không phải giá cuối 0,0004. Không lấy quy đổi “khoảng $30” của paper làm giá ETH hiện tại.

## 4. Hạn chế đọc và suy luận

Markdown có thể đảo thứ tự hai cột (§5.1.1/§5.1.2); ảnh PDF giải quyết thứ tự đọc ngưỡng. Phần thu thập có bất nhất số học: §3.1.3 ghi 35.116 sau khi loại 4 khỏi 35.220, trong khi Tab. 1 cho tổng cuối 34.988 với 4+46+182 bị loại. Ghi nhận bất nhất, không sửa số liệu tác giả bằng suy đoán.

82,89% ở §5.4 là hợp các cờ tập trung sở hữu/honeypot, wash và LPI trên **707 token tăng >100% trong mẫu paper**, không phải tỷ lệ wash/LPI riêng và không phải tỷ lệ của toàn thị trường. “Không phát hiện” không chứng minh hợp lệ; liên hệ trước–sau không chứng minh quan hệ nhân quả hoặc khả năng dự báo ngoài mẫu. Daily che mất mua–bán nội ngày; ít trader và giữ tồn kho gần cân bằng có thể có giải thích hợp lệ. Dự đoán precursor phải kiểm soát cutoff và nhãn tương lai riêng.
