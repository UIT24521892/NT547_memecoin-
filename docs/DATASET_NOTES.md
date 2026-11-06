# Kiểm tra nhanh artifact Zenodo

**2026-10-01 [codex]**. Chỉ đọc README, header và số dòng CSV, SQL Base, các cell liên quan trong notebook wash; không chạy notebook, không sửa dữ liệu tác giả. Artifact: [thư mục đã giải nén](references/dataset/meme_coin_anon-main/), nguồn tải trong [README tham khảo](references/README.md). Số dòng dưới đây được đếm từ CSV cục bộ, không phải kết quả nghiên cứu mới.

## 1. Các bảng và nhãn tham chiếu

| File trong `data/` | Số dòng | Khoá / nội dung đáng chú ý |
|---|---:|---|
| `confirmed_meme_coins.csv` | 34.988 | `symbol,name,platform,address`; gồm cả `native`, không mặc định mọi dòng là contract EVM |
| `creation_date_tokens.csv` | 31.811 | Thêm `creation_date`; cần parse timezone và kiểm tra định dạng |
| `high_performing_meme_coins.csv` | 707 | Giá/market cap/volume hai snapshot, `price_changes_pct`, địa chỉ |
| `security_metrics_info_high_performing_tokens.csv` | 707 | Top-10, owner, fresh, bundle, airdrop, honeypot, tax, creator launches; dữ liệu có `%`, `K`, chuỗi như `>$999T`, ô trống; không có thời điểm as-of đủ rõ |
| `HP_tokens_with_anomalies.csv` | 412 | Cùng schema security; là cờ tham chiếu, không phải nhãn do người gán độc lập |
| `potential_wash_trading_activities.csv` | 3.266 | `timestamp,open,highest,lowest,closed,volume,returns,volume_pct_change,wash_trading,name,address,platform` |
| `potential_LPI_activities.csv` | 871 | OHLCV + `returns,rsi,volume_change_pct,potential_price_pump` |
| `dune_data_on_potential_wash_trading_makers_HP_coins.csv` | 64.621 | Maker/ngày/token, buy/sell/total volume, tỷ trọng và cờ có mua lẫn bán; `address` là token, `maker` là trader |
| `dune_data_on_potential_lpi_makers_HP_coins.csv` | 945 | Maker/ngày/token; `token_address` thay cho `address`; buy/sell volume và `volume_percentage` |
| `wash_trading_detected.csv` | 1.043 | `platform,address,day,unique_maker_count`; nhãn sự kiện theo rule, không có cột chỉ rõ kỹ thuật xác nhận |
| `lpi_operations_detected.csv` | 72 | `day,token_address,platform,unique_maker_count,buy_volume,sell_volume,volume,buy_ratio` |
| `rug_pulls_detected_on_performing_tokens_after_mid_january.csv` | 2 | OHLCV + `returns,rug_pull,name,address,platform,timestamp` |
| `pump_and_dumps_on_performing_tokens_after_mid_january.csv` | 91 | Thời điểm start/peak/end, % pump/dump, thời lượng, RSI, volume trước/trong/sau, severity, token |
| `delisted_tokens_popular_aggregators.csv` | 124 | Token từng bị gỡ niêm yết; không tự động coi là có manipulation |
| `delisted_tokens_with_artificial_growth.csv` | 84 | Danh sách token, không có event time trong file này |
| `delisted_tokens_profit_extraction.csv` | 30 | Danh sách token, không có event type/time trong file này |

Có ba ZIP OHLCV daily/hourly. Phiên này chỉ xác nhận file hiện diện, chưa kiểm tra toàn bộ nến, pool, khoảng thời gian và mức thiếu dữ liệu trong ZIP.

## 2. SQL và notebook: các khác biệt phải giữ lại

SQL Base đọc `dex.trades`, dùng `tx_from` làm maker và `amount_usd` làm volume. Đây là tổng USD theo maker/ngày/token, **không phải swap thô**: không xuất `tx_hash`, pool, token amount, block time chi tiết để tạo evidence link. Không thể coi các CSV maker này là bảng `swaps` của đồ án.

SQL wash có bộ lọc **`unique_addresses <= 50`**, không nằm trong bảng ngưỡng PDF. SQL LPI lọc **`<= 10`**; buy ratio cần kiểm tra ở notebook tiếp theo. Các query tham chiếu bảng upload riêng `dune.brandebille.dataset_...` và có tên chứa `delisted`, kể cả đường dẫn query tương ứng các nhóm khác. Chưa xác minh bảng đó còn truy cập được; không thể chạy nguyên xi cho mẫu mới.

Cell `check_zero_risk_market_position` trong `wash_trading_detection.ipynb` dùng **`abs(B−S)/(B+S)*100 <= 2`**, với B,S là buy/sell **USD** từ SQL. Đây là chi tiết **đã đọc trong mã artifact**, chưa được định nghĩa bằng công thức trong PDF. Lượng token gần cân bằng và USD gần cân bằng không tương đương khi giá nội ngày thay đổi. Phải báo cáo đúng đơn vị khi tái lập.

Cell `makers_buy_and_sell` dùng **`volume_percentage > 99`**, trong khi PDF viết **at least 99% (≥99%)**. Đây là khác biệt tại biên có bằng chứng; sau này kiểm tra cả hai, chọn một chế độ tái lập và ghi rõ. Cell `check_same_makers` loại token chỉ có một ngày (`total_days > 1`); đây là chi tiết trong notebook, chưa ghi số ngày tối thiểu trong PDF. Tập ngày được tính từ input `wash_trading_df`, cần truy vết đầu vào đầy đủ ở giai đoạn indicators.

Ví dụ CSV LPI có ngày **2022-11-15**, dữ liệu maker wash có **2023-11-28**, ngoài cửa sổ giữa 10/2024–1/2025 mô tả ở §5. Không suy đoán nguyên nhân; trước khi dùng nhãn phải lọc ngày, truy vết nến và notebook. Số dòng khớp bảng tổng không bảo đảm các cửa sổ lịch sử khớp.

## 3. Cách dùng trong đồ án

- Chuẩn hoá tên trường vào bảng riêng; giữ nguyên file nguồn. Khoá token là `(chain,token_address)`, sự kiện thêm `event_time/event_type`; EVM chuyển chữ thường cho khoá, Solana **giữ nguyên hoa thường**.
- Đưa nhãn vào `labels` với `source=reference_rule`, nguồn DOI/file và thời điểm sự kiện; không gọi là ground truth thủ công. Schema labels phải hỗ trợ nguồn này khi thiết kế.
- Nhóm D lấy từ artifact chỉ dùng đối chiếu hoặc tập thử thách; không tăng nhân tạo tỷ lệ biến cố trong test quần thể mà không báo cáo thiết kế lấy mẫu.
- Không đưa snapshot security không có as-of vào feature quá khứ. Không dùng tên file/ngày sau cutoff làm bằng chứng có thể dự đoán được trước cutoff.
- Tập token nhỏ tự thu ở thời kỳ khác vẫn cần được thu riêng; artifact không thay thế yêu cầu nghiên cứu đó.
