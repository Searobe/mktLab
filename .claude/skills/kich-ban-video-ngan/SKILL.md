---
name: kich-ban-video-ngan
description: Viết kịch bản video ngắn dọc (TikTok, Reels, Shorts) cho Lab Bàn kèm danh sách cảnh cho nhân viên xưởng quay. Dùng khi Sếp nói «viết kịch bản video», «làm video về…», «quay gì hôm nay», hoặc khi lịch tuần có một ô video cần kịch bản.
---

# Kịch bản video ngắn

## Đọc trước
1. `CLAUDE.md` (bất biến 3, 4, 6), `chien-luoc/organic.md` (trụ nội dung, cách đo).
2. `thuong-hieu/` — giọng văn. Thư mục còn trống thì viết giọng mộc, thân thiện, xưng «Lab Bàn», và nói với Sếp là chưa có
   hồ sơ giọng văn.
3. `chien-luoc/thu-vien-hook.md` — ưu tiên kiểu mở đầu ở mục «Đã thắng»; mục «Mẫu để thử» chỉ là giả thuyết.
4. `san-pham/` — mọi giá, thời gian làm, chất liệu nói trong video phải có ở đây. Không có thì không nói.

## Khuôn kịch bản (15–45 giây)
1. **0–3 giây — câu mở đầu:** một cảnh + một dòng chữ trên màn. Hình gây tò mò hoặc hé lộ kết quả trước. Không mở bằng
   logo, không chào hỏi.
2. **3–25 giây — thân:** quá trình thật ở xưởng, mỗi cảnh 1–3 giây, chữ trên màn ngắn (≤ 8 chữ / dòng).
3. **Kết:** kết quả cuối + một lời mời nhẹ («Nhà bạn có tấm ảnh cũ nào không?»). Không ép mua, không hứa điều `san-pham/`
   không có.

## Danh sách cảnh cho nhân viên quay
Viết như dặn người không chuyên, mỗi cảnh một dòng:
- Cảnh số · quay gì · góc (cận tay / toàn bàn / từ trên xuống) · dài bao nhiêu giây · có cần âm thanh thật không.
- Luôn dặn: điện thoại **dọc 9:16**, lau ống kính, quay chỗ sáng, giữ máy yên, quay dư mỗi cảnh 2–3 giây.
- Cảnh có mặt khách / nhân viên / ảnh khách: ghi «cần mã đồng ý DY-…». Chưa có thì đổi cảnh (chỉ quay tay, không quay mặt).

## Ghi ra
- Tạo file `bai/<yyyy-mm>/<ten-bai>.md` theo khuôn `bai/README.md`: `dinh_dang: video`, đúng `tru`, `trang_thai: nhap`.
- Viết thêm 2 câu mở đầu dự phòng để thử nếu bản chính yếu.
- Có cảnh AI tạo / sửa: `anh_ai: co`, `nhan_ai: co`, ghi chỗ đặt nhãn trên video.

## Không làm
- Không tự đăng. Không bịa câu chuyện, lời khen, số liệu («90% nhà…» chỉ khi có nguồn).
- Không lấy video người khác, không dùng nhạc ngoài thư viện có bản quyền của nền tảng.
