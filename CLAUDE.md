# CLAUDE.md — Hướng dẫn riêng cho Claude Code

@AGENTS.md

> `AGENTS.md` ở trên là **nguồn sự thật duy nhất** (vai trò, RQ, ngưỡng, schema, kế hoạch). File này chỉ bổ sung những gì riêng cho Claude Code. **Không sao chép nội dung AGENTS.md vào đây** để tránh lệch giữa Codex và Claude Code. Nếu hai file mâu thuẫn, AGENTS.md thắng.

## 1. Đọc gì khi bắt đầu phiên

1. `MEMORY.md` — trạng thái dự án, quyết định đã chốt, câu hỏi còn mở (dùng chung với Codex).
2. `docs/LOG.md` — nhật ký phiên gần nhất (khi file đã tồn tại).
3. `docs/PLAN.md` — mốc T0–T3, H, chuỗi đã chọn (khi file đã tồn tại).

Chỉ đọc thêm file khác khi việc đang làm cần đến. Không quét cả repo.

**Đọc paper:** dùng bản Markdown trong `docs/references/markdown/` (grep được, ít token), không đọc PDF trừ khi cần đối chiếu công thức/bảng. Danh sách tài liệu và link gốc: `docs/references/README.md`. Môi trường Python: `.venv/` (chạy `.venv/bin/python`).

## 2. Giai đoạn hiện tại

Xem mục "Giai đoạn hiện tại" trong `MEMORY.md`. Quy tắc cứng:

- Chưa được sinh viên duyệt ✋ của giai đoạn trước thì **không** sang giai đoạn sau (AGENTS.md Mục 14).
- Ở giai đoạn Tuần 1–2: **chỉ viết tài liệu, không viết code thu dữ liệu**.
- Lưu ý: AGENTS.md Mục 0 ghi "làm theo Mục 14" cho lượt đầu, nhưng deliverable lượt đầu thật sự nằm ở **Mục 15**. Dùng Mục 15.

## 3. Cách làm việc với sinh viên

- Trả lời bằng **tiếng Việt**, giữ thuật ngữ tiếng Anh trong ngoặc. Code comment và `docs/` bằng tiếng Việt.
- Sinh viên mới học lập trình và chưa có nền blockchain/DeFi. Mỗi khái niệm mới giải thích đủ 3 tầng (như trẻ 5 tuổi → định nghĩa học thuật → ví dụ đời thường), ngắn gọn.
- Trước khi viết một module, nói 2–3 câu: nó làm gì, vì sao cần. Sau đó mới code.
- Việc nhiều bước hoặc chưa rõ hướng: dùng plan mode và trình bày kế hoạch trước. Chỉ hỏi sinh viên những quyết định thật sự của họ (hạn nộp, chuỗi, key…); các lựa chọn có mặc định hợp lý thì tự chọn và ghi lại.
- Mỗi điểm dừng ✋: tóm tắt đã làm, kết quả chính, rủi ro, câu hỏi cần quyết định. Rồi dừng.

## 4. Quy tắc trung thực dữ liệu (quan trọng nhất)

- **Không bịa** số liệu, ngưỡng, trích dẫn hay kết quả. Bảng ngưỡng ở AGENTS.md Mục 2.2 chỉ là bản nháp; phải đối chiếu với PDF paper rồi ghi trang/mục vào tài liệu. Sai thì sửa AGENTS.md **và báo sinh viên**.
- Docs API, free tier, rate limit thay đổi theo thời gian: kiểm tra lại bằng WebFetch/WebSearch, ghi ngày kiểm tra. Không dựa vào trí nhớ.
- Không tạo dữ liệu giả rồi trình bày như dữ liệu thật. Dữ liệu giả chỉ dùng trong unit test và phải nằm trong `tests/`.
- Kết quả phải ghi rõ nguồn, ngày thu, chuỗi, khoảng thời gian.
- Dùng từ "dấu hiệu / rủi ro / nhất quán với thao túng". Không viết "lừa đảo" khi chưa có bằng chứng hành vi. "Giá tăng mạnh" không bao giờ là nhãn.

## 5. Ràng buộc kỹ thuật & an toàn

- Chỉ đọc dữ liệu công khai. Không giao dịch, không gửi tx, không tương tác contract, không doxxing.
- Không đọc, in hay commit `.env`. Chỉ tạo và sửa `.env.example` (khoá để trống).
- Dữ liệu thô trong `data/raw/` là bất biến: không sửa tay, chỉ ghi thêm kèm ngày thu. Mọi biến đổi phải tái tạo được bằng script.
- Mọi lời gọi API đi qua client có cache + retry (tenacity) + rate limit. Không gọi API trong vòng lặp không giới hạn. Chạy thử với mẫu nhỏ (vài token) trước khi chạy cả tập.
- Ngưỡng nằm trong `configs/thresholds.yaml`, **không hard-code** trong `src/`.
- Seed cố định. Thư viện ghi vào `pyproject.toml`/`requirements.txt` có phiên bản.
- Rò rỉ tương lai (data leakage): mọi feature có as-of time ≤ cutoff; GoPlus/DexScreener hiện tại không dùng làm feature cho mẫu quá khứ (xem AGENTS.md Mục 9–10). Khi thêm feature mới, thêm luôn kiểm tra trong `tests/test_no_leakage.py`.

## 6. Chuẩn code (Python 3.11)

- Type hints, docstring ngắn tiếng Việt, hàm nhỏ, tên biến dễ hiểu. Khớp phong cách file xung quanh.
- Cấu trúc theo AGENTS.md Mục 13: `src/memecoin/{collect,amm,features,indicators,model,viz}`.
- Mỗi indicator và công thức AMM có unit test với cả ca dương tính lẫn âm tính (pytest). Ví dụ bắt buộc: pool 0,01 ETH / 100 MEME, mua 50 MEME → giá +300%.
- Chạy `pytest` trước khi báo "xong". Nếu test fail hoặc bị bỏ qua, nói thẳng kèm output.
- Không thêm thư viện nặng khi pandas/duckdb/networkx đủ dùng.

## 7. Cập nhật bộ nhớ chung

Cuối mỗi phiên có thay đổi thực chất:

1. Thêm một mục ngắn vào `docs/LOG.md` (làm gì, quyết định gì, vì sao, còn mở gì).
2. Cập nhật `MEMORY.md`: giai đoạn hiện tại, quyết định đã chốt, câu hỏi còn mở, ghi chú API đã kiểm chứng.
3. Không nhét chi tiết dài vào `MEMORY.md`. Nội dung dài đặt ở `docs/` rồi trỏ link.

Memory tự động của Claude Code (ngoài repo) chỉ dùng cho sở thích cá nhân của sinh viên. Mọi thứ liên quan dự án phải nằm trong `MEMORY.md` để Codex cũng thấy.

## 8. Git

- Chỉ commit/push khi sinh viên yêu cầu. Không commit `data/raw/` lớn, `.env`, file API key.
- Repo git hiện nằm ở thư mục cha (`NT547/`) và có nhiều file bị xoá không liên quan đến đồ án này. Khi commit, chỉ `git add` đúng các file của `Project_2026/`, không dùng `git add -A`.
