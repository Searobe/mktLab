---
name: lam-anh
description: Làm ảnh đăng bài cho Lab Bàn — chọn kiểu ảnh, cỡ theo kênh, chữ trên ảnh, dựng trên Canva từ ảnh chụp thật; khi cần bối cảnh (khung tranh treo phòng khách, album trên bàn cưới) thì gọi Gemini qua scripts/gemini_media.py, có trần tiền và nhãn AI. Dùng khi Sếp nói «làm ảnh», «ảnh cho bài này», «ảnh khuyến mãi», «ghép ảnh sản phẩm vào phòng», «thay nền», hoặc bài trong lịch cần ảnh.
---

# Làm ảnh

Nguyên tắc số một: **sản phẩm trong ảnh phải là ảnh chụp thật** của hàng Lab Bàn làm ra. AI chỉ được dựng **bối cảnh**
xung quanh (phòng, bàn, ánh sáng). Ảnh làm khung đẹp hơn, màu in tươi hơn hàng thật là quảng cáo sai sự thật (bất biến 6).

## Chọn đường làm

| Ảnh cần | Đường làm | Nhãn AI | Tốn tiền |
|---|---|---|---|
| Sản phẩm thật + chữ + logo (khuyến mãi, mẹo, giới thiệu, trích lời khách có mã đồng ý) | **Canva** từ ảnh chụp thật | Không cần (không có AI tạo hình) | Không |
| Ảnh trước / sau (phục hồi ảnh cũ) | Ảnh thật của đơn hàng + mã đồng ý | Không (nếu không dùng AI sửa) | Không |
| Đặt sản phẩm vào bối cảnh | **Gemini** — ảnh sản phẩm thật làm gốc | **Có** | Có |
| Thay nền, làm sạch nền ảnh sản phẩm | **Gemini** | **Có** | Có |
| Minh hoạ không có sản phẩm (ý tưởng, bìa bài mẹo) | **Gemini** từ mô tả | **Có** | Có |

Canva có tính năng AI riêng (xoá nền, tạo ảnh…): dùng tính năng đó cũng là AI sửa ảnh → gắn nhãn như Gemini.

## Cỡ theo kênh (tra 2026-10-16, nguồn hướng dẫn bên thứ ba; Meta chưa có trang chính thức gom một chỗ)

| Kênh | Cỡ | Tỉ lệ |
|---|---|---|
| Facebook / Instagram bảng tin | 1080 × 1350 | 4:5 (chiếm nhiều màn hình nhất) |
| Bài vuông, carousel | 1080 × 1080 | 1:1 |
| Story / Reels / TikTok | 1080 × 1920 | 9:16 — chữ, logo tránh ~14% trên, ~35% dưới (vùng nút bấm) |

## Chữ trên ảnh

- Tối đa ~7 chữ cho dòng chính; người lướt điện thoại đọc trong 1–2 giây.
- Giá / khuyến mãi trên ảnh: **chỉ từ `san-pham/`**, khớp đúng chữ trong bài.
- Màu, phông, cách đặt logo: theo `thuong-hieu/` (chưa có thì hỏi Sếp, không tự chế bộ nhận diện).
- Đọc lại chữ tiếng Việt trên ảnh từng dấu — ảnh AI hay viết sai dấu; **không để Gemini viết chữ lên ảnh**, chữ thêm ở Canva.

## Gọi Gemini (`scripts/gemini_media.py`)

Đi từ máy có khoá `GEMINI_API_KEY` (gói trả phí — Google không dùng dữ liệu để huấn luyện). Phiên này **không** bật Gmail /
Drive / cổng TableLab.

1. **Xem giá trước**, luôn:
   `python3 scripts/gemini_media.py anh --mo-ta "<mô tả>" --ra <thư mục Drive LabbanMarketing> --ten <ten> --thu`
2. Mô tả theo khuôn: *sản phẩm gốc giữ nguyên* + *bối cảnh* + *ánh sáng* + *góc máy* + *phong cách*. Vd: «Giữ nguyên khung
   tranh và bức ảnh trong ảnh gốc, không đổi màu, không đổi kích thước. Đặt lên tường phòng khách căn hộ hiện đại, tường be,
   sofa xám, nắng chiều từ cửa sổ bên trái, góc chụp ngang tầm mắt, ảnh chụp thật, không chữ, không người.»
3. Có ảnh gốc thì **bắt buộc** khai `--anh-khach khong` (không có người thật trong ảnh) hoặc `--anh-khach DY-<số>` (khách
   đã đồng ý cho gửi AI — Sếp giữ phiếu). Script chặn nếu thiếu.
4. Chạy thật (bỏ `--thu`). Mặc định 1K (~1 nghìn đồng / ảnh); cần in to mới dùng `--co 2K` / `4K`.
5. Xem kết quả: sản phẩm có bị AI vẽ lại khác hàng thật không (khung, màu, viền, chữ)? Khác → bỏ, không dùng.
6. Thêm chữ + **nhãn «Ảnh có sử dụng AI»** (chữ nhỏ, góc ảnh, đọc được) ở Canva. Không che, không xoá nhãn.
7. Bài dùng ảnh này: `anh_ai: co` · `nhan_ai: co` · `anh:` đường dẫn Drive. Khi đăng bật ô nhãn AI của nền tảng.

Script tự làm: chặn thư mục ra nằm trong repo · cộng dồn tiền tháng, chạm trần 500 nghìn thì dừng (`... con-lai` để xem) ·
ghi `<file>.nguon.json` cạnh ảnh (mô tả, model, giá, «anh_ai: co»). Gemini cũng tự nhúng dấu SynthID vào ảnh — dấu này
**không thay** nhãn chữ.

## Không làm

- Không dựng người thật giả (mặt khách, người mẫu «trông như thật») cho ảnh khách hàng / lời khen.
- Không gửi ảnh có mặt khách khi chưa có mã đồng ý.
- Không để ảnh trong repo — chỉ Drive `LabbanMarketing` (bất biến 8).
- Không tải ảnh của đối thủ / trên mạng làm gốc.
