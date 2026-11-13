# Hướng dẫn viết báo cáo (áp dụng skill `research-paper-writing`)

> Viết ngày 2026-11-13 [claude]. Skill gốc: `.claude/skills/research-paper-writing/` (MIT, nguồn ở `SOURCE.md` trong thư mục đó). File này chỉ ghi **phần điều chỉnh cho đồ án NT547**; quy trình chung đọc trong `SKILL.md` của skill.
>
> Lịch: viết báo cáo thuộc dòng **14–25/12** (PLAN Mục 8). Trước đó chỉ được giữ dàn ý và bản đồ claim–evidence ở `report/OUTLINE.md`; **không viết câu kết quả khi chưa có số đo**.

## 1. Cách dùng

- **Claude Code:** gõ yêu cầu kèm tên skill, ví dụ "dùng skill research-paper-writing viết lại Introduction trong `report/`". Skill nằm ở `.claude/skills/` nên tự được nạp.
- **Codex:** đọc trực tiếp `.claude/skills/research-paper-writing/SKILL.md` và file cần dùng trong `references/` (Codex không tự nạp thư mục `.claude/`).
- Mỗi lần chỉ mở **một** file hướng dẫn mục (introduction.md, method.md...), đúng quy tắc của skill.

## 2. Ba khái niệm chính của skill

**Reverse outlining (dàn ý ngược)**
1. *Như trẻ 5 tuổi:* viết xong thì đọc lại, mỗi đoạn tóm bằng một câu; câu nào không khớp ý chính của cả mục thì đoạn đó lạc đề.
2. *Học thuật:* sau khi viết một mục, liệt kê luận điểm chính của mục, câu chủ đề của từng đoạn và các bằng chứng dưới mỗi đoạn; kiểm tra ánh xạ câu chủ đề → luận điểm, bằng chứng → câu chủ đề; đoạn nào không ánh xạ được thì sửa hoặc xoá.
3. *Đời thường:* dọn tủ quần áo: lấy từng món ra, hỏi "món này thuộc ngăn nào?"; món không thuộc ngăn nào thì bỏ.

**Claim–evidence map (bản đồ luận điểm – bằng chứng)**
1. *Như trẻ 5 tuổi:* mỗi lần nói "mình tìm ra X", phải chỉ được tờ giấy chứng minh X.
2. *Học thuật:* mỗi luận điểm lớn (nhất là ở Abstract/Introduction) ghi dạng `Claim | Evidence | Status`; luận điểm không có bằng chứng phải làm yếu đi hoặc xoá.
3. *Đời thường:* hoá đơn đi chợ: mỗi dòng tiền phải có món hàng tương ứng.

**Adversarial self-review (tự phản biện)**
1. *Như trẻ 5 tuổi:* giả làm thầy giáo khó tính, tự hỏi bài của mình những câu khó nhất.
2. *Học thuật:* trả lời bộ câu hỏi 5 chiều (đóng góp, độ rõ, sức mạnh thực nghiệm, độ đủ của đánh giá, độ hợp lý của thiết kế), gắn `pass / needs revision / needs new experiment`.
3. *Đời thường:* tập phỏng vấn với bạn đóng vai nhà tuyển dụng khó tính.

## 3. Điều chỉnh vì đồ án không phải paper ML/CV

Skill viết cho paper ML/CV/NLP (đề xuất một phương pháp mới, so với SOTA). Đồ án này là **đo lường + tái lập + detector** kiểu paper bảo mật (USENIX Security). Đổi như sau:

| Skill gốc nói | Áp dụng cho đồ án |
|---|---|
| Method / pipeline figure | Mục *Data Collection* + *Indicators* + *Risk Score*; hình pipeline = phễu dữ liệu (ứng viên → có cutoff → A/B → có swap) với số thật từng chuỗi |
| Teaser figure | Bỏ, hoặc dùng một ví dụ token có dấu hiệu wash trading kèm link explorer (đã kiểm tra thủ công) |
| "Better than SOTA" | Không có SOTA. So với **baseline "giá tăng > 100%"** (RQ4) và **số của paper Mongardini & Mei** (RQ1). Không viết "vượt trội" |
| Ablation module | Ablation **theo 5 nhóm feature** (RQ3) + phân tích độ nhạy ngưỡng (`thresholds.yaml`) |
| Generalization / harder settings | Tách theo chuỗi và theo nhóm A/B/C; nhóm C chỉ đo false positive |
| Contribution type | "New experimental findings / insight": thời kỳ 2026, 3 chuỗi, lead time của precursor (PAPER_NOTES PB31). Là **tái lập có mở rộng**, không phải phương pháp mới; viết đúng như vậy |
| "Avoid incremental patching style" | Không áp dụng cho phần tái lập: nói thẳng chỗ nào theo paper, chỗ nào mình đổi và vì sao |

Skill không có mục **Limitations** và **Ethics**; đồ án bắt buộc có cả hai (xem Mục 5).

## 4. Quy tắc cứng của đồ án (thắng skill khi mâu thuẫn)

1. **Bằng chứng phải truy được nguồn.** Cột `Evidence` ghi: file/script tạo ra số, nguồn dữ liệu, ngày thu, chuỗi, khoảng thời gian. Ví dụ: `scripts/measure_positive_rate.py → data/interim/task2/gate_1811/solana/; GeckoTerminal nến ngày, thu 2026-11-12; Solana; cutoff train+val`.
2. **Status chỉ có 3 giá trị:** `supported` (có số đo, chạy lại được), `needs evidence` (chưa đo), `weakened` (đã làm yếu câu vì bằng chứng không đủ). Không có "supported" cho số chưa chạy.
3. **Từ ngữ:** "signal", "risk", "consistent with manipulation". Không viết "scam", "fraud", "rug-pulled by the creator" khi chưa có bằng chứng hành vi. "Price surge" không bao giờ là nhãn.
4. **Tập test:** số trên tập test chỉ xuất hiện sau lần chạy test duy nhất (PLAN Mục 5.3); không viết lại câu theo kết quả test rồi chỉnh tiếp mô hình.
5. **Số của paper gốc:** trích kèm trang (xem `docs/THRESHOLD_AUDIT.md`); chi tiết "chưa xác minh" phải giữ nguyên chữ đó trong báo cáo.
6. **Ngôn ngữ và định dạng:** báo cáo tiếng Anh, mẫu IEEE hai cột (PLAN Mục 10, mặc định). Hướng dẫn và ghi chú nội bộ bằng tiếng Việt.

## 5. Mục bắt buộc ngoài skill

- **Limitations** (đã biết tới 2026-11-13, bổ sung dần): Solana chỉ phủ token tốt nghiệp pump.fun; mỗi token 1 pool; OHLCV miễn phí chỉ 180 ngày; Base quét 20 ngày chọn ngẫu nhiên; cutoff ở ngày giao dịch đầy đủ thứ 7 nên token chết sớm nhất bị loại (LOG 2026-11-12); chỉ nhận token còn hoạt động tại cutoff (volume TB 7 ngày ≥ $1.000, PLAN sửa 13/11) nên kết quả RQ2 chỉ áp cho token đã sống qua tuần đầu; trần 10.000 swap/token; trader là địa chỉ, không phải người.
- **Ethics:** chỉ đọc dữ liệu công khai, không giao dịch, không gắn ví với danh tính, kết quả là dấu hiệu rủi ro.
- **Reproducibility:** lệnh chạy lại, seed, phiên bản thư viện, ngày thu dữ liệu.

## 6. Trình tự viết (14–25/12)

1. Cập nhật `report/OUTLINE.md`: chốt câu chuyện theo kết quả thật, điền claim–evidence map.
2. Viết theo thứ tự: Data & Method → Evaluation → Related Work → Introduction → Abstract → Conclusion (Abstract/Intro viết sau cùng vì phụ thuộc kết quả).
3. Sau mỗi mục: reverse outlining (skill, mục "Paragraph Clarity Check").
4. Cuối: tự phản biện 5 chiều theo `references/paper-review.md`, thêm 3 câu riêng cho đồ án:
   - Có câu nào ngầm coi "giá tăng mạnh" là bằng chứng thao túng không?
   - Có feature/ngưỡng nào chỉnh sau khi đã nhìn tập test không?
   - Mỗi cảnh báo minh hoạ đã có link explorer và đã kiểm tra thủ công chưa?
