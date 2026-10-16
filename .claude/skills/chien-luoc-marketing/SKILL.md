---
name: chien-luoc-marketing
description: Lập chiến lược marketing khách lẻ cho Lab Bàn từ báo cáo thị trường, báo cáo đối thủ và dữ kiện công ty — SWOT, chọn nhóm khách, câu định vị, 4P, kế hoạch 90 ngày có chỉ số. Dùng khi Sếp nói «lên chiến lược», «kế hoạch marketing quý tới», «định vị Lab Bàn», «90 ngày tới làm gì», «nên tập trung khách nào». Ghi ở chien-luoc/.
---

# Chiến lược marketing

Mục tiêu: một bản chiến lược **ngắn, chọn lựa rõ ràng** — nói được Lab Bàn **không** làm gì. Chiến lược mà cái gì cũng làm
là không có chiến lược.

## Đầu vào — thiếu thì dừng, hỏi

| Cần | Ở đâu | Thiếu thì |
|---|---|---|
| Báo cáo thị trường | `chien-luoc/nghien-cuu/` | Đề nghị chạy skill `nghien-cuu-thi-truong` trước |
| Báo cáo đối thủ | `chien-luoc/doi-thu/` | Đề nghị chạy `nghien-cuu-doi-thu` trước |
| Sản phẩm, giá đã duyệt | `san-pham/` | Hỏi Sếp; không tự đặt giá |
| Năng lực xưởng (máy, công suất, thời gian giao) | Hỏi Sếp | Ghi «chưa rõ», không đoán |
| Ngân sách | CLAUDE.md bất biến 2: 5 triệu / tháng quảng cáo Meta, 500 nghìn / tháng AI làm ảnh / video | — |
| Kênh đang mở | CLAUDE.md «Kênh — mở theo đợt» | Không lập kế hoạch cho kênh chưa mở như thể đã có |

Số liệu kinh doanh (doanh thu, khách sỉ…): chỉ dùng bản tóm tắt Sếp đưa, không đọc TableLab trong phiên này. Không ghi doanh
thu, lương, giá vốn vào file — chiến lược là tài liệu nhiều người đọc (sổ luật A8). Cần thì viết «biên lợi nhuận: Sếp nắm».

## Cấu trúc — 7 phần

1. **Tóm tắt một trang**: chọn khách nào · hứa gì · 3 việc lớn trong 90 ngày · chỉ số đo.
2. **SWOT** — mỗi ô tối đa 4 dòng, mỗi dòng có bằng chứng (link báo cáo). Sau đó **ghép chéo** thành hướng đi:
   mạnh × cơ hội (tấn công) · yếu × cơ hội (sửa để giành) · mạnh × thách thức (phòng thủ) · yếu × thách thức (tránh).
3. **Chọn khách** (phân khúc → chọn → định vị, STP): liệt kê nhóm khách từ báo cáo thị trường, chấm 1–5 theo: cỡ nhóm ·
   khả năng chi · Lab Bàn phục vụ tốt · đối thủ bỏ trống. Chọn **1 nhóm chính, tối đa 1 nhóm phụ**. Ghi nhóm bị loại và lý do.
4. **Câu định vị**: «Với <nhóm khách> cần <việc cần làm xong>, Lab Bàn là <loại sản phẩm> mang lại <lợi ích chính>, khác
   <lựa chọn thay thế> ở chỗ <lý do tin được>». Lý do tin được phải có thật (bất biến 6) — không viết «chất lượng số 1».
5. **4P** cho nhóm chính: Sản phẩm (gói nào, bỏ gì) · Giá (chỉ từ `san-pham/`; đề xuất giá mới thì ghi «đề xuất, chờ Sếp
   duyệt») · Kênh bán (online / xưởng / đối tác) · Truyền thông (kênh đang mở, nhóm chủ đề nội dung, tỷ lệ).
6. **Kế hoạch 90 ngày**: chia 3 tháng; mỗi việc có người làm (Sếp / nhân viên / Claude), hạn, chi phí ước và chỉ số. Việc
   tốn tiền ghi rõ tiền từ trần nào.
7. **Chỉ số và cách đo**: tối đa 5 chỉ số. Mỗi chỉ số: định nghĩa · đo ở đâu · mốc hiện tại (chưa có thì «chưa có số»,
   không ghi 0) · đích 90 ngày.

## Luật

- Không hứa khuyến mãi, cam kết, giá mới trong chiến lược như thể đã chốt — ghi «đề xuất».
- Không lên kế hoạch chạy quảng cáo bằng tài khoản cá nhân, không dùng tệp số điện thoại khách chưa đồng ý (bất biến 5).
- Không kế hoạch nào để AI tự bật chi tiền (bất biến 2).
- Kênh chưa mở → để ở «sau 90 ngày», không trộn vào kế hoạch chính.

## Đầu ra

`chien-luoc/<yyyy>-q<n>-chien-luoc.md`. Kết luận ngay dưới tiêu đề, «👉» cuối là các quyết định Sếp cần chốt (chọn khách,
giá đề xuất, ngân sách). Sếp duyệt qua PR; khi đã duyệt, ghi `Sếp duyệt ngày <…>` ở đầu file.

## Tự kiểm

- [ ] Có ghi rõ nhóm khách **bị loại**?
- [ ] Lý do tin được trong câu định vị có bằng chứng?
- [ ] Mỗi việc 90 ngày có người làm + hạn + chỉ số?
- [ ] Tổng chi phí trong trần 5 triệu / 500 nghìn mỗi tháng?
- [ ] Không có doanh thu / lương / giá vốn trong file?
