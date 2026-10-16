---
name: lich-noi-dung
description: Lên lịch nội dung tháng cho Lab Bàn theo chiến lược — nhóm chủ đề và tỷ lệ, ngày lễ / mùa cưới, giờ đăng, mã bài nối sang bai/. Dùng khi Sếp nói «lên lịch tháng», «lịch nội dung», «tháng sau đăng gì», «kế hoạch bài tuần này», «làm hết bài trong lịch». Ghi lich-noi-dung/<yyyy-mm>.md; Sếp duyệt lịch rồi mới viết bài.
---

# Lịch nội dung

Lịch là **cam kết đều đặn**: đăng ít mà đều tốt hơn đăng nhiều rồi bỏ. Mỗi dòng trong lịch thành một bài ở `bai/`.

## Đầu vào

- `chien-luoc/` bản mới nhất: nhóm khách chính, câu định vị, nhóm chủ đề, kênh. Chưa có thì hỏi Sếp 3 câu: khách chính
  là ai · tháng này bán gì là chính · mỗi tuần đăng được mấy bài.
- CLAUDE.md «Kênh»: chỉ xếp bài cho kênh **đã mở**. Kênh chưa mở thì ghi «chờ mở kênh», không xếp.
- `san-pham/`: chương trình đã duyệt trong tháng (nếu có).
- `ngay-dang-chu-y.md` cạnh file này: ngày lễ, mùa vụ của ngành.

## Cách lên lịch

1. **Nhóm chủ đề** (3–5 nhóm, lấy từ chiến lược). Gợi ý cho Lab Bàn: *Nghề & xưởng* (quy trình in, chọn giấy, làm khung) ·
   *Kỷ niệm của khách* (chỉ khi có mã đồng ý) · *Mẹo* (chọn cỡ ảnh, treo tranh, bảo quản album) · *Sản phẩm & ưu đãi* ·
   *Mùa / dịp*.
2. **Tỷ lệ**: bài bán hàng **không quá 1/3** — còn lại cho biết và cho tin. Ghi tỷ lệ thực của tháng ở đầu file.
3. **Nhịp**: chọn số bài / tuần vừa sức (Sếp duyệt từng bài tháng đầu, đừng xếp quá số Sếp kịp đọc). Gợi ý khởi đầu:
   Facebook 3 bài / tuần, Instagram dùng lại ảnh Facebook.
4. **Giờ đăng**: mặc định 11:30–12:30 và 19:30–21:30 giờ Việt Nam (giờ người ta lướt điện thoại); đây là phỏng đoán ban
   đầu. Khi kênh nối và có số thật, thay bằng giờ đo được, ghi nguồn.
5. **Dịp**: rà `ngay-dang-chu-y.md`; bài cho dịp phải lên **trước 7–14 ngày** (khách in / đóng khung cần thời gian).
6. **Mã bài**: `MT-<mmdd>-<số thứ tự trong ngày>`, vd `MT-1105-01`. Mã là tên file bài.

## Đầu ra

`lich-noi-dung/<yyyy-mm>.md`:

```markdown
# Lịch nội dung <tháng/năm>

**Sếp duyệt ngày:** <…> · **Kênh:** <đã mở> · **Bài / tuần:** <…> · **Tỷ lệ:** biết <…>% · tin <…>% · bán <…>%

| Mã bài | Ngày giờ | Kênh | Nhóm chủ đề | Mục tiêu | Ý bài (1 câu) | Ảnh / video | Bài |
|---|---|---|---|---|---|---|---|
| MT-1105-01 | 05/11 19:30 | facebook | Mẹo | cho biết | <…> | ảnh thật xưởng | [bai](../bai/2026-11/MT-1105-01.md) |

## Dịp trong tháng
- <ngày>: <dịp> — bài <mã>

👉 <việc Sếp cần quyết>
```

Lịch mở PR riêng; Sếp duyệt lịch → mới viết bài (skill `viet-bai`). Sếp nói «làm hết bài trong lịch» thì viết từng bài,
gom vào **một PR mỗi tuần** để Sếp duyệt một lần.

## Luật

- Lịch không phải lệnh đăng: kênh chưa nối thì không có gì tự lên. Khi nối kênh, vẫn chỉ đăng bài `da-duyet`.
- Ngày lễ âm lịch đổi theo năm: **tra lại mỗi năm**, ghi nguồn; không tự đổi âm → dương bằng trí nhớ.
- Bài «Kỷ niệm của khách» chỉ xếp khi Sếp có mã đồng ý `DY-<số>`.
