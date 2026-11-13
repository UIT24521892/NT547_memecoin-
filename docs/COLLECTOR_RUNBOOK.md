# Collector: cách chạy và kiểm thử lại

> 2026-11-12 [codex]. Sinh viên yêu cầu bắt đầu ngay các task collector sau khi thiết kế được duyệt. Đây là khởi động sớm dòng lịch 16–29/11, không đổi lịch/cổng hay tham số nghiên cứu. Đã có một đợt kiểm tra kỹ thuật trên dữ liệu thật; **chưa phải mẫu nghiên cứu 300 token**.

**Cập nhật task 1 (12/11):** đã gộp truy vấn Base theo nhiều factory/pool, kiểm tra tương đương với quét riêng và dừng/chạy tiếp. Đo ba factory 1.000 block: 30 → 10 HTTP, cùng 23 log/12 ứng viên; cả hai pool có 77 log khớp nhau. Hướng dẫn và giới hạn số đo: [BASE_BATCHING.md](BASE_BATCHING.md). Lệnh kiểm thử offline riêng: `.venv/bin/python scripts/benchmark_base_batching.py`.

## 1. Module làm gì?

| Khái niệm | Như trẻ 5 tuổi | Định nghĩa | Ví dụ đời thường |
|---|---|---|---|
| Collector | Chép dữ liệu ở nơi công khai vào quyển sổ của mình | Chương trình gọi API chỉ đọc, phân trang và lưu phản hồi cùng thời điểm, nguồn, tham số | Nhân viên chép hóa đơn từng trang vào sổ |
| Cache | Đã chép rồi thì đọc lại quyển sổ | Ánh xạ request đã chuẩn hóa sang phản hồi gốc bằng SHA-256; offline chỉ dùng cache | Giữ hóa đơn để không phải quay lại cửa hàng |
| Nến OHLCV | Ghi giá đầu, cao nhất, thấp nhất, cuối và lượng mua bán trong một khoảng | Một bản ghi `(timestamp, open, high, low, close, volume)`; timestamp là lúc mở nến UTC | Ghi giá và số hàng bán của một sạp mỗi ngày |
| SHA-256 | Dấu kiểm để biết trang giấy có bị đổi không | Hàm băm tạo dấu vân tay 256 bit; so hash body gốc với hash ghi khi tải | Kiểm tra dấu niêm phong của hộp hồ sơ |

Code chính ở `src/memecoin/collect/`. Lệnh vào là `scripts/collect.py`. Các giới hạn nguồn đọc từ `configs/chains.yaml`; không chứa key.

## 2. Kết quả chạy thật 12/11

Nến trong khoảng **[26/05/2026, 12/11/2026) UTC**, tức hết 11/11. Ba pool PEPE, BRETT, HEGE chỉ dùng kiểm tra kỹ thuật, chọn từ snapshot hiện tại và **không vào bảng `samples`**.

| Chuỗi / token | Nến ngày | Khoảng ngày thiếu | Nến giờ | Khoảng giờ thiếu trên 4.080 giờ |
|---|---:|---:|---:|---:|
| Ethereum / PEPE | 170 | 0 | 4.067 | 13 |
| Base / BRETT | 170 | 0 | 4.077 | 3 |
| Solana / HEGE | 170 | 0 | 2.233 | 1.847 |
| Tổng | 510 | 0 | 10.377 | 1.863 |

Tổng **10.887 dòng**. Thiếu nến giờ có thể do giờ không có swap hoặc nguồn không trả dữ liệu; chưa phân biệt được hai nguyên nhân, không tự điền volume 0. Tham số `include_empty_intervals=false` nhằm tránh nến tổng hợp. Trang ngắn vẫn được phân tiếp: HEGE từ 665 lên 2.233 nến khi đọc hết các trang. Nến ngày cũng chưa được xác minh độc lập với blockchain toàn kỳ.

| Việc | Phạm vi đo | Kết quả |
|---|---|---|
| Ethereum: danh sách pool | 10/06 UTC; block 25.283.319–25.290.492 | 167 log V2 + 17 log V3; 177 ứng viên có WETH |
| Base: danh sách pool V2/V3 | Block 47.130.126–47.131.125; **chỉ 1.000 block**, gồm block ngay trước ngày 10/06 | 20 log V2 + 2 log V3; 11 ứng viên có WETH |
| Base: Aerodrome classic | Block 47.130.126–47.135.125; **chỉ 5.000 block** | 1 log tạo pool, 1 ứng viên có WETH |
| Solana: danh sách pool | Ngày 10/06 UTC; 5 trang Helius | 375 tx thành công → 358 tx có Migrate/MigrateV2 → **222 pool mới**, xác nhận CPI CreatePool; đã loại lời gọi lặp |
| Swap Ethereum | PEPE; 100 block | 2/2 log giải mã; có trader theo `tx.from` |
| Swap Base | BRETT Slipstream; 1.000 block | 8/8 log giải mã theo ABI Swap V3; có trader theo `tx.from` |
| Giao dịch Solana | HEGE/Raydium; 05/11 UTC | 8 tx; cùng 8/8 signature của bài thử RPC public trước đây |

`amount_usd` của swap EVM còn NULL vì chưa có nguồn giá quote USD tương ứng. Chưa tính zero-risk/circular volume trên dữ liệu thiếu USD. `tx.from` là địa chỉ gửi giao dịch, chưa khẳng định người giao dịch cuối cùng. Swap Solana vẫn cần bộ đọc + đối chiếu thủ công theo cổng 22/11; inventory tx chưa phải bảng swap chuẩn hóa.

Đầu ra tại `data/interim/collector_check/`:

- `ohlcv_online/ohlcv.csv`, `ohlcv.json`, `ohlcv.parquet`, `collection.duckdb`, `report.json`.
- `{ethereum,base,aerodrome,solana}_discovery/`: ứng viên + báo cáo độ đầy đủ. EVM còn phải xác minh token là meme; Solana chỉ phủ pump.fun.
- `{ethereum,base}_swap_logs/`: log gốc đã chuẩn hóa metadata; `{ethereum,base}_swaps/swaps.csv`: lượng và trader.
- `solana_transactions/transactions.csv`: signature, timestamp, link Solscan và `raw_ref`.
- `offline_replay/check_results.json`: kết quả kiểm thử lại, lưu riêng với đợt online.

Raw bất biến ở `data/raw/<ngày thu>/<provider>/`. Mỗi request/retry lưu một `.body` và `.meta.json`; metadata che key, có SHA-256, timestamp, HTTP status. Cache trỏ đến raw ở `data/interim/http_cache/`. Có khóa theo provider để các tiến trình chia sẻ giới hạn tốc độ. Giới hạn request không phải phép đo credit/CU thực tế.

## 3. Kiểm thử lại trên máy đang có dữ liệu

Từ thư mục gốc repo:

```bash
.venv/bin/python -m pytest
.venv/bin/python scripts/check_collection.py
```

Mong đợi: test qua; 10 tình huống replay đều **0 request mạng**; CSV/Parquet/DuckDB cùng 10.887 dòng, nội dung DB và Parquet bằng nhau; CSV replay giống từng byte; Solana khớp 8/8 signature. Chế độ offline không đọc `.env`; kiểm tra raw hash gồm cả phản hồi HTTP lỗi đã lưu.

Để tự xem dữ liệu thay vì chỉ đọc thông báo PASS:

```bash
.venv/bin/python -c "import pandas as pd; print(pd.read_csv('data/interim/collector_check/ohlcv_online/ohlcv.csv').groupby(['chain','timeframe']).size())"
.venv/bin/python -c "import pandas as pd; print(pd.read_csv('data/interim/collector_check/ethereum_swaps/swaps.csv').to_string(index=False))"
```

Mở `solana_transactions/transactions.csv`, chọn link explorer rồi đối chiếu thời gian/chiều/lượng với bài thử ở `SOLANA_PILOT.md`. Kiểm thử tự động của agent không thay nhãn thủ công của nhóm.

## 4. Chạy online từ đầu hoặc thử tải lại

Các key đọc từ `.env`: `BLOCKSCOUT_API_KEY`, `DRPC_API_KEY`, `HELIUS_API_KEY`. Không copy đè `.env` đang có. Đọc `README.md` để cài Python 3.11 và dependency.

Tạo danh sách pool **chỉ cho kiểm tra kỹ thuật**:

```bash
.venv/bin/python scripts/collect.py resolve-smoke \
  --output data/interim/collector_check/smoke
```

Thu nến ngày trước, rồi cả ngày/giờ:

```bash
.venv/bin/python scripts/collect.py ohlcv \
  --pools data/interim/collector_check/smoke/pools.csv \
  --start 2026-05-26 --end 2026-11-12 --timeframes day hour \
  --max-pages 12 --max-requests 60 \
  --output data/interim/collector_check/ohlcv_online
```

`--end` **không bao gồm ngày đó**. Thêm `--offline` để cấm mạng, hoặc `--refresh` để tải phản hồi mới; mỗi phản hồi mới có raw riêng. Refresh không đảm bảo CSV giống bản cũ nếu nhà cung cấp điều chỉnh lịch sử. Thiếu/lỗi một pool vẫn xuất phần đã lấy được và ghi lỗi trong report. Exit code 2 là lỗi/chưa hết phân trang; exit code 0 vẫn phải xem `coverage_complete` vì nguồn có thể bỏ giờ không có giao dịch.

Các lệnh danh sách lịch sử đã chạy:

Thêm `--separate-factories` vào lệnh Base V2/V3 dưới đây để tái lập đúng raw/CSV của đợt đầu. Khi thu đợt mới, bỏ cờ này để dùng cách gộp mặc định; chỉ định thêm `aerodrome` nếu cần quét ba factory cùng lúc. Đầu ra mới nên để thư mục riêng.

```bash
.venv/bin/python scripts/collect.py discover --chain ethereum \
  --start 2026-06-10 --end 2026-06-11 --factories uniswap_v2 uniswap_v3 \
  --output data/interim/collector_check/ethereum_discovery

.venv/bin/python scripts/collect.py discover --chain base \
  --start 2026-06-10 --end 2026-06-11 \
  --from-block 47130126 --to-block 47131125 --factories uniswap_v2 uniswap_v3 \
  --max-chunks 10 --separate-factories --output data/interim/collector_check/base_discovery

.venv/bin/python scripts/collect.py discover --chain base \
  --start 2026-06-10 --end 2026-06-11 \
  --from-block 47130126 --to-block 47135125 --factories aerodrome \
  --max-chunks 50 --output data/interim/collector_check/aerodrome_discovery

.venv/bin/python scripts/collect.py discover --chain solana \
  --start 2026-06-10 --end 2026-06-11 --page-size 100 --max-pages 15 \
  --output data/interim/collector_check/solana_discovery
```

EVM truyền `--from-block/--to-block` thì dải block đó thắng ngày start/end. Bỏ hai tham số này để client tìm block theo ngày. `--max-chunks` giới hạn dải **mới cần gọi mạng**; cache không ăn ngân sách này. Chạy lại cùng tham số để tiếp tục. Blockscout chạm trần 1.000 dòng thì chia nhỏ dải; một block vẫn chạm trần sẽ báo thiếu, không coi là đầy đủ. Solana chạm trần 10.000 tx/token hoặc giới hạn trang thì `swaps_partial=true`.

Các lệnh swap có thể xem lại trong `scripts/check_collection.py`: bỏ `--offline` để bổ sung cache còn thiếu. `logs` còn dùng được cho `Transfer`, `Mint/Burn/Sync`; bỏ `--topic` để lấy mọi log của địa chỉ. Chưa có bước dựng holder/liquidity/creator hoàn chỉnh.

## 5. Việc còn lại trước các cổng

1. **16–18/11:** mở rộng danh sách lịch sử trên toàn cửa sổ; xác minh meme, chọn pool theo thanh khoản **tại cutoff**, chốt 40 A + 40 B + 20 C mỗi chuỗi rồi thu OHLCV đợt 1. Không dùng bảng smoke hoặc thanh khoản hiện tại để thay quy tắc này. Các ứng viên đã thu chưa phải mẫu ngẫu nhiên của cả kỳ.
2. **18/11:** đếm target trên A+B với cutoff trước T2, theo từng chuỗi; chỉ kết luận cổng 5–50% khi có mẫu đủ điều kiện và nhãn đầy đủ. Đợt kỹ thuật này chưa đo cổng.
3. **22/11:** chuẩn hóa swap Solana, xác minh thủ công ≥20 tx/≥2 sàn và thu ≥30 token; chưa đạt cổng bằng 8 tx/1 sàn hiện tại. Hoàn thiện giá USD cho swap EVM và log holder/liquidity/creator.
4. **Từ 23/11:** lấy phần đuôi đến hết 22/11 vào thư mục đợt 2 riêng; giữ nguyên raw đợt 1, hợp nhất từ các đợt khi chuẩn hóa. Chưa có dữ liệu tương lai này ngày 12/11.
5. **29/11:** thống kê độ phủ cuối, EDA, ≥20 ca dương trước T2 và trình ✋ thu dữ liệu. Các cổng/nhánh dự phòng giữ nguyên PLAN.

Ước tính chạy toàn tập trong PLAN vẫn chưa được thay bằng phép đo toàn tập. Đợt này kiểm tra chức năng và độ đầy đủ trên dải nhỏ; không chứng minh thời gian/CU cho 300 token.

## 6. Nguồn đối chiếu khi triển khai

- [GeckoTerminal API](https://www.geckoterminal.com/dex-api), [OHLCV endpoint](https://docs.coingecko.com/reference/pool-ohlcv-contract-address): cursor, token address, tối đa 1.000 nến, skip giờ không swap. Giới hạn free 180 ngày lấy từ phép đo 06/11 trong PLAN; không suy free tier từ tài liệu Pro.
- [Helius getTransactionsForAddress](https://www.helius.dev/docs/rpc/gettransactionsforaddress): lọc blockTime/status, encoding, paginationToken. Đã chạy `full, limit=100`, không còn chỉ thử 10; chưa đo credit thực tế riêng.
- [pump.fun IDL](https://github.com/pump-fun/pump-public-docs/blob/main/idl/pump.json), [PumpSwap IDL](https://github.com/pump-fun/pump-public-docs/blob/main/idl/pump_amm.json): program ID, discriminator, account index của Migrate/MigrateV2/CreatePool. Raw tài liệu đã lưu trong provider `protocol_docs`.
- [Aerodrome contracts](https://github.com/aerodrome-finance/contracts), [IPoolFactory](https://github.com/aerodrome-finance/contracts/blob/main/contracts/interfaces/factories/IPoolFactory.sol): địa chỉ deployment, chữ ký `PoolCreated(address,address,bool,address,uint256)`. Pool stable không áp dụng công thức x·y=k; classic và Slipstream có factory khác nhau, chưa có collector khám phá factory Slipstream riêng.
- Ethereum lấy trader qua legacy `transaction/gettxinfo`, vì module `proxy` đã trả HTTP 400 trong phép thử; Base dùng RPC `eth_getTransactionByHash`. Các raw lỗi giữ để truy nguyên.

## 7. Bàn giao sàng lọc Solana cho thành viên 2 (2026-11-13)

**Vì sao:** GeckoTerminal giới hạn ~10 lần/phút **theo IP**. Máy thành viên 1 dành hạn mức cho Base + Ethereum; máy thành viên 2 (mạng khác, không dùng chung Wi-Fi) chạy Solana để tìm nhóm A. Solana đã đủ B 40/40; dừng ở 1.025/5.000 pool.

**Quy tắc:** trong lúc thành viên 2 chạy, máy thành viên 1 **không** chạy `--chain solana`. Mỗi máy vẫn giữ 10 lần/phút.

### Cài trên máy thành viên 2 (macOS hoặc Linux; Windows phải dùng WSL vì `http.py` dùng `fcntl`)

```bash
git clone https://github.com/UIT24521892/NT547_memecoin-.git && cd NT547_memecoin-
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python -m pytest -q          # phải qua hết
```

Giải nén gói dữ liệu nhận từ thành viên 1 **ở thư mục gốc repo**, rồi kiểm tra mã băm (so với file `.sha256` đi kèm):

```bash
shasum -a 256 solana_handoff_2026-11-13.tar.gz
tar -xzf solana_handoff_2026-11-13.tar.gz   # tạo data/... và MEMORY.md
```

Gói gồm: danh sách ứng viên Solana, cache + raw GeckoTerminal (để không gọi lại 1.025 pool đã xét), kết quả sàng lọc hiện tại và `MEMORY.md` (không có trên GitHub). Sàng lọc Solana **không cần key**.

### Chạy

```bash
mkdir -p data/interim/task2
nohup .venv/bin/python scripts/screen_sample.py --chain solana >> data/interim/task2/screen_solana_active.log 2>&1 &
tail -f data/interim/task2/screen_solana_active.log
```

Vài phút đầu đọc lại cache (không gọi mạng), sau đó in tiến độ mỗi 25 pool. Dừng bằng `kill <PID>`; chạy lại cùng lệnh sẽ tiếp tục. Kiểm tra đúng: 1.025 dòng đầu của `screening/solana/screened.csv` phải giống bản trong gói.

### Trả kết quả về

Khi `progress.json` có `stop_reason` là `quotas_filled` hoặc `budget_exhausted`, nén và gửi lại:

```bash
tar -czf solana_result_$(date +%F).tar.gz data/raw/*/geckoterminal data/interim/http_cache/geckoterminal data/interim/task2/screening/solana data/interim/task2/screen_solana_active.log
```

Thành viên 1 giải nén **không ghi đè** (`tar -xzkf`) vì file raw có tên ngẫu nhiên, rồi chạy `screen_sample.py --chain solana --offline` để kiểm tra kết quả tái tạo được không cần mạng.

### Dùng Claude Code trên máy thành viên 2

Mở Claude Code ở thư mục gốc repo (`CLAUDE.md`, `AGENTS.md`, `docs/PLAN.md` tự nạp; `MEMORY.md` có sau khi giải nén gói). Lệnh mẫu:

> Đọc docs/COLLECTOR_RUNBOOK.md Mục 7. Kiểm tra mã băm gói, giải nén, chạy pytest, rồi chạy sàng lọc Solana nền theo đúng lệnh. Theo dõi đến khi xong; báo tiến độ B/A. Không sửa code, configs hay tham số; không chạy chuỗi khác; gặp lỗi thì dừng và báo. Cuối cùng nén kết quả theo mục "Trả kết quả về" và ghi một mục ngắn vào docs/LOG.md.
