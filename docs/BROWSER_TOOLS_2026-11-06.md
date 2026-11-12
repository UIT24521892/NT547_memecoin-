# Công cụ cho Codex/Claude Code đọc trang trình duyệt

> Khảo sát 2026-11-06 [codex] theo yêu cầu sinh viên. Chưa cài hay kết nối MCP/extension. Không thay đổi cấu hình Codex, Claude hay Chrome.

## 1. Muốn giải quyết việc gì?

Mở trang giao dịch Solscan có giao diện động, đọc thông tin mua/bán và đối chiếu `swaps.csv`. Tính năng tìm trang/web hiện có đã không mở được trang Solscan trong lần thử trước.

## 2. Các khái niệm

| Khái niệm | Như cho trẻ 5 tuổi | Định nghĩa | Ví dụ đời thường |
|---|---|---|---|
| Model | Người suy nghĩ và trả lời | Mô hình AI xử lý đầu vào và tạo câu trả lời; khả năng mở website tuỳ công cụ được nối | Người đọc và giải thích một tờ hoá đơn |
| MCP | Ổ cắm cho công cụ | Model Context Protocol cho phép ứng dụng AI kết nối các server cung cấp công cụ; server trình duyệt thực hiện thao tác và trả kết quả | Người đọc dùng ổ cắm để nối kính lúp |
| Browser extension | Tiện ích gắn vào trình duyệt | Phần mềm chạy trong Chrome, có các quyền do người dùng cấp, có thể giúp công cụ truy cập tab | Gắn một phụ kiện vào kính lúp |
| Trang động | Trang được lắp thêm nội dung sau khi mở | Website dùng JavaScript để lấy/render dữ liệu sau HTML ban đầu | Bảng giá tự cập nhật sau khi cửa hàng mở cửa |

Không cần tự động đổi model để đọc văn bản: [Playwright mô tả cơ chế đọc accessibility snapshot](https://github.com/microsoft/playwright/blob/main/docs/src/getting-started-mcp.md), không bắt buộc model thị giác. Ảnh chụp giao diện là một cách khác; phải có model/client hỗ trợ nhận ảnh để diễn giải ảnh.

## 3. Các lựa chọn

| Lựa chọn | Dùng với | Điểm phù hợp | Trạng thái |
|---|---|---|---|
| **Playwright MCP + Playwright Extension** | Codex và Claude Code | Một MCP dùng được cho cả hai; extension cho phép gắn vào tab Chrome đang mở | Chưa cấu hình, chưa thử kết nối extension/Solscan |
| **Claude in Chrome** | Claude Code | Tích hợp chính thức của Anthropic, cho Claude làm việc trên Chrome | Chưa kiểm tra extension, tài khoản và kết nối |
| **Chrome DevTools MCP** | Các agent hỗ trợ MCP, gồm Codex/Claude Code | Điều khiển và kiểm tra Chrome; hữu ích khi cần xem giao diện và debug | Chưa cấu hình, chưa thử Solscan |
| **TinyFish** | Plugin ChatGPT nếu tài khoản hỗ trợ | Browser trên cloud để đọc trang/tự động hoá | Có trong danh mục nhưng chưa cài/kết nối; chưa thử Solscan, giới hạn/chi phí chưa xác minh |

Khuyến nghị: **Playwright MCP + Playwright Extension** nếu muốn một cách dùng được cho cả Codex và Claude Code. Nếu muốn thử riêng Claude Code nhanh hơn, xem Claude in Chrome.

## 4. Máy hiện có gì?

Kiểm tra chỉ đọc ngày 06/11/2026:

- Có Chrome `156.0.8078.81`, Node.js `v26.8.1`, npm/npx, Codex CLI `0.157.1` và Claude Code `2.1.251`.
- `codex mcp list`: chỉ thấy OpenAI Developer Docs. `claude mcp list`: chưa có MCP server. Đây là danh sách cấu hình CLI hiện tại, không chứng minh extension của Chrome đã hoặc chưa cài.
- Không thấy `playwright` hoặc `@playwright/mcp` trong các dependency mà Node tìm thấy từ project. Điều này không loại trừ một bản được cài/cache ở nơi khác.
- Dùng Chrome headless với **profile tạm độc lập** mở trang Solscan mẫu: trả trang Cloudflare **“Just a moment…”**, không thấy nội dung giao dịch. Profile tạm đã được dọn sau phép thử.

Kết luận của phép thử: **không thể bảo đảm cài MCP sẽ đọc được Solscan**. Kết nối với Chrome người dùng đang mở là một phương án đáng thử vì đó là môi trường sinh viên đã xem được trang, nhưng chưa được thử trong phiên này. Nếu có trang xác minh, để người dùng xử lý qua giao diện hợp lệ.

## 5. Cách thiết lập Playwright khi nhóm muốn thử

1. Mở Chrome, cài [Playwright Extension chính thức](https://chromewebstore.google.com/detail/playwright-extension/mmlmfjhmonkocbjadbfplnigmagldckm) của Microsoft/Playwright.
2. Nếu muốn dùng ở **Codex**, mở Terminal và thêm server:

```bash
codex mcp add playwright -- npx -y @playwright/mcp@latest --extension
```

3. Nếu muốn dùng ở **Claude Code**, chạy thêm lệnh sau từ thư mục dự án:

```bash
claude mcp add --scope local playwright -- npx -y @playwright/mcp@latest --extension
```

Mỗi ứng dụng có cấu hình MCP riêng: muốn cả hai dùng được thì cấu hình cả hai. Theo [tài liệu MCP Codex](https://learn.chatgpt.com/docs/extend/mcp), lệnh Codex mặc định thay đổi `~/.codex/config.toml`; Claude `--scope local` cấu hình theo người dùng/dự án. Hai lệnh trên **chưa được chạy trong phiên này**. `@latest` cho phép tải phiên bản thay đổi theo thời gian; nên cố định phiên bản sau khi kiểm tra ổn định.

4. Dùng `codex mcp list` hoặc `claude mcp list` để xem đã được khai báo. Khởi động lại phiên/extension nếu công cụ chưa hiện. Danh sách server không thay thế việc thử kết nối thật.
5. Mở trang giao dịch Solscan trong Chrome và yêu cầu agent: “Chỉ đọc trang này; trích signature, chiều swap và lượng HEGE/WSOL; không thực hiện giao dịch hay nhấn nút mua/bán.”
6. Xem agent có thực sự đọc được trang và đối chiếu lại bằng chứng hay vẫn gặp trang chặn. Không coi việc cài xong là đã xác minh Solscan hoạt động.

Extension cho agent khả năng tương tác với tab và trạng thái đăng nhập đã cấp quyền. Chỉ cấp quyền trên site cần dùng; đồ án chỉ cho phép đọc, không nhấn mua/bán hoặc kết nối ví.

Nguồn: [hướng dẫn kết nối extension Playwright](https://github.com/microsoft/playwright.dev/blob/main/mcp/configuration/browser-extension.mdx), [cấu hình Playwright MCP](https://github.com/microsoft/playwright-mcp), [MCP của Codex](https://learn.chatgpt.com/docs/extend/mcp).

## 6. Phương án Claude in Chrome

Theo [tài liệu Anthropic](https://code.claude.com/docs/en/chrome): cần Claude in Chrome extension, Claude Code, đăng nhập trực tiếp bằng gói Anthropic hỗ trợ. Kết nối này không hoạt động khi Claude Code chỉ xác thực qua API key/nhà cung cấp bên thứ ba theo tài liệu hiện tại.

Sau khi cài extension và đủ điều kiện, khởi động `claude --chrome`; trong Claude Code dùng `/chrome` để xem trạng thái. Chưa xác minh máy/tài khoản sinh viên đáp ứng điều kiện này, và chưa thử đọc Solscan.

## 7. Giới hạn của kết quả

- Agent có thể đối chiếu thông tin bằng trình duyệt và lưu bằng chứng; vẫn cần ghi rõ `annotator = agent` nếu agent làm. Không tự nhận là nhãn do sinh viên gán.
- Bảng phân tầng để đánh giá detector, kiểm tra bằng chứng hành vi và nhãn thủ công của nhóm vẫn là một phần riêng của nghiên cứu.
- Không kết luận Solscan hay trình duyệt luôn sẵn sàng; site có thể chặn, thay giao diện hoặc giới hạn truy cập.
