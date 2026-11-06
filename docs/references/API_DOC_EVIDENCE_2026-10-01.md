# Bằng chứng docs API đọc ngày 2026-10-01

Người kiểm tra: codex. GET tài liệu công khai qua curl; không gọi API thị trường, không dùng key, không chạy SQL. HTML/schema tạm ở /tmp; phần liên quan được giữ dưới đây để lần sau biết căn cứ. Hash là SHA-256 response nguyên bản, không phải hash dataset.

| URL | SHA-256 tài liệu đã đọc |
|---|---|
| [https://docs.etherscan.io/supported-chains](https://docs.etherscan.io/supported-chains) | `30673a23e2ec9c9bd6468f5e9e4feadd1c51473955942aa017c742fc25f756c5` |
| [https://docs.dexscreener.com/api/reference](https://docs.dexscreener.com/api/reference) | `41cc479c3b1242c59bb344d7c063203bfed47a86b85cfd8d75ddd8bf893bf6bb` |
| [https://api.geckoterminal.com/docs/v2/swagger.json](https://api.geckoterminal.com/docs/v2/swagger.json) | `b2d42dca2eb894e2a671e0a1d328558d10f7152a73ddf4c165b059fcb680ed78` |

## Etherscan: dữ liệu component SupportedChains

Cột cuối là `free`; component destructure `[name,id,net,free]`, lọc `tierF === free` bằng `!free`, và hiển thị theo biến đó. Các hàng đọc được:

```text
[`Ethereum Mainnet`,1,`main`,true]
[`BNB Smart Chain Mainnet`,56,`main`,false]
[`Base Mainnet`,8453,`main`,false]
```

Ngoại lệ source code/ABI free trên mọi chain nằm ở văn bản ngoài bảng. Không suy ra transfers/creator free trên Base/BSC từ ngoại lệ này.

## DexScreener: tiêu đề lookup pair

HTML hiển thị “Get one or multiple pairs by chain and pair address (rate-limit 300 requests per minute)”. Profiles ghi 60/phút. Schema có `pairCreatedAt`, liquidity, volume, fdv, marketCap. Đây là docs, chưa gọi endpoint với token cụ thể.

## GeckoTerminal: schema trực tiếp

Phần `info.description` của Swagger hiện ghi khoảng **10 calls/phút**, có thể dao động; FAQ đọc qua web ghi **30 calls/phút**. Hai nguồn chính thức không nhất quán. Đồ án đề xuất ngân sách ≤10/phút rồi giảm theo response, không khẳng định một mức đảm bảo.

Trades public mô tả 300 giao dịch gần nhất trong 24h. Schema chỉ cho lookback/cursor mở rộng ở Pro. Schema OHLCV không nêu giới hạn lookback free toàn phần. Dưới đây chỉ giữ trường và giá trị để đối chiếu:

```json
{
  "path": "/networks/{network}/pools/{pool_address}/ohlcv/{timeframe}",
  "parameters": [
    {
      "name": "before_timestamp",
      "schema": {
        "type": "string",
        "example": "1679414400"
      }
    },
    {
      "name": "limit",
      "schema": {
        "type": "integer",
        "default": 100,
        "maximum": 1000
      }
    },
    {
      "name": "include_empty_intervals",
      "schema": {
        "type": "boolean",
        "default": false
      }
    }
  ]
}
{
  "path": "/networks/{network}/pools/{pool_address}/trades",
  "parameters": [
    {
      "name": "trading_period",
      "schema": {
        "type": "string",
        "enum": [
          "1d",
          "7d",
          "30d"
        ],
        "default": "1d"
      }
    },
    {
      "name": "cursor",
      "schema": {
        "type": "string"
      }
    },
    {
      "name": "per_page",
      "schema": {
        "type": "integer",
        "default": 300,
        "maximum": 300
      }
    }
  ]
}
```

## Zenodo: metadata record

Giấy phép/DOI được kiểm tra qua [metadata công khai](https://zenodo.org/api/records/17830944). Kết quả được ghi trong PLAN; không dựa riêng vào dòng ghi nhớ của phiên trước.
