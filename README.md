# NT547 — Meme Coin Manipulation

Đồ án phát hiện **dấu hiệu/rủi ro** wash trading, LPI và tiền dấu hiệu rug pull trên Ethereum, Base, Solana. Giá tăng hoặc giảm mạnh không tự chứng minh thao túng.

Kế hoạch đã duyệt: [docs/PLAN.md](docs/PLAN.md). Thiết kế dữ liệu: [docs/DATA_CARD.md](docs/DATA_CARD.md). Trạng thái collector và cách chạy: [docs/COLLECTOR_RUNBOOK.md](docs/COLLECTOR_RUNBOOK.md).

## Cài môi trường

Python 3.11. Nếu máy chưa có `.venv`, chạy:

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Key điền vào `.env` theo tên biến trong `.env.example`; giữ nguyên `.env` đang có. Không điền key vào `.env.example` hoặc gửi vào chat. Chỉ dùng API đọc và gói free đã kiểm tra.

## Kiểm thử lại kết quả trên máy hiện tại

```bash
.venv/bin/python -m pytest
.venv/bin/python scripts/check_collection.py
.venv/bin/python scripts/benchmark_base_batching.py
```

Hai lệnh sau chạy offline và so với dữ liệu đã thu; không cần key. Benchmark Base kiểm tra gộp ba factory/hai pool và dừng rồi chạy tiếp; hướng dẫn và số đo: [docs/BASE_BATCHING.md](docs/BASE_BATCHING.md). Dữ liệu và cache ở `data/` bị gitignore: bản clone mới phải chạy các bước online trong runbook trước, hoặc được chép dữ liệu/cache từ lần thu gốc.

## Collector đang có

```bash
.venv/bin/python scripts/collect.py --help
```

- `discover`: log tạo pool Ethereum/Base, migration + CPI CreatePool Solana; Base mặc định gộp factory, `--separate-factories` để đối chiếu baseline; xuất ứng viên, chưa phải mẫu A/B/C.
- `ohlcv`: nến ngày/giờ, phân trang, bỏ nến chưa đóng, giữ khoảng thiếu; xuất CSV, JSON, Parquet, DuckDB.
- `logs`: log theo pool/token, hỗ trợ dải nhỏ và chạy tiếp bằng cache.
- `decode-evm`: swap V2/V3, lượng raw nguyên chính xác và `tx.from`; chưa quy đổi USD.
- `transactions`: lịch sử Solana qua Helius; giao dịch tham chiếu account chưa tự được coi là swap.
- `verify`: đối chiếu SHA-256 của phản hồi gốc với metadata.

Chưa thu đủ mẫu nghiên cứu 300 token và chưa đánh giá các cổng 18/11, 22/11, 29/11. Đợt 23/11 mới có đủ dữ liệu đến hết 22/11 cho đuôi nhãn test; không chạy thử model trên test trước bước cuối.
