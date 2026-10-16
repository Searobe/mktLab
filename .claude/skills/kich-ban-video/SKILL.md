---
name: kich-ban-video
description: Viết kịch bản video ngắn dọc (Reels, TikTok, Facebook) cho Lab Bàn — câu móc 3 giây, cảnh quay từng giây, phụ đề, thẻ kết, danh sách cảnh cần quay bằng điện thoại; cảnh không quay được thì dựng bằng Gemini Veo qua scripts/gemini_media.py, có trần tiền và nhãn AI. Dùng khi Sếp nói «làm video», «kịch bản TikTok», «video Reels», «quay gì ở xưởng», «video khuyến mãi».
---

# Kịch bản video ngắn

Video tốt nhất của một xưởng là **cảnh thật**: máy in chạy, tay thợ vào khung, album mở ra. Khách tin cái họ thấy được
làm thật. AI chỉ lấp cảnh không quay được (bối cảnh nhà khách, cảnh mở đầu), và phải gắn nhãn.

## Đọc trước

`thuong-hieu/` (giọng, màu, logo) · `san-pham/` (giá, ưu đãi) · `lich-noi-dung/` (mã bài, mục tiêu) · `chien-luoc/`.

## Khung kịch bản (15–45 giây)

| Giây | Phần | Viết gì |
|---|---|---|
| 0–3 | **Câu móc** | Hình động mạnh + một câu chữ trên màn hình. Viết 3 câu móc khác kiểu để Sếp chọn: câu hỏi · kết quả trước · điều bất ngờ về nghề |
| 3–25 | **Thân** | 3–5 cảnh, mỗi cảnh 2–5 giây, mỗi cảnh một ý. Thứ tự: vấn đề → quá trình làm → thành phẩm |
| cuối 3–5 giây | **Thẻ kết** | Logo + một lời mời (nhắn tin / ghé xưởng). Không «mua ngay kẻo hết» khi không có hạn thật |

Phụ đề: luôn có (nhiều người xem tắt tiếng), ≤ 2 dòng, đặt giữa màn hình — tránh ~14% trên và ~35% dưới (vùng nút của
Reels / TikTok, số đo từ hướng dẫn bên thứ ba). Chữ chính tô màu nhấn theo `thuong-hieu/`.

## Đầu ra

Kịch bản ghi vào bài: `bai/<yyyy-mm>/<ma-bai>.md` (kênh `tiktok` hoặc `facebook`), thân bài là chú thích, kèm mục:

```markdown
## Kịch bản
| Giây | Hình | Chữ trên màn hình | Lời đọc | Nguồn hình |
|---|---|---|---|---|
| 0–3 | Cận máy in đẩy tờ ảnh ra | <câu móc> | — | quay thật |
| 3–6 | Phòng khách treo khung | — | — | Gemini Veo (nhãn AI) |

## Cảnh cần quay (gửi thợ)
- [ ] <cảnh> — điện thoại dọc, 4K nếu có, giữ máy 5 giây, có ánh sáng cửa sổ
```

Bài có cảnh AI → `anh_ai: co`, `nhan_ai: co`. Có mặt khách / nhân viên → cần đồng ý (khách: mã `DY-<số>`; nhân viên: Sếp
xác nhận nhân viên đồng ý xuất hiện).

## Nhạc, giọng

- Nhạc: chỉ dùng thư viện nhạc có sẵn **trong** ứng dụng đăng (TikTok, Reels — có quyền dùng trên nền tảng đó) hoặc nhạc
  miễn phí bản quyền ghi rõ nguồn. Không lấy nhạc từ YouTube / bài hát đang hot về ghép.
- Giọng: ưu tiên giọng thật của Sếp / nhân viên. Không giả giọng người thật bằng AI.

## Cảnh dựng bằng Gemini Veo (`scripts/gemini_media.py video`)

1. Xem giá trước: `python3 scripts/gemini_media.py video --mo-ta "<cảnh>" --ra <Drive LabbanMarketing> --ten <ten> --thu`.
   Mặc định Veo 3.1 Lite, 720p, 8 giây, dọc 9:16 — ~10–11 nghìn đồng / cảnh (giá tra 2026-10-16). `--giay 4` rẻ một nửa.
2. Mô tả: một cảnh, một chuyển động máy, ánh sáng, phong cách «quay thật», không chữ, không logo, không người lạ nhìn thẳng
   máy. Có ảnh sản phẩm thật làm khung đầu: `--anh-goc <ảnh> --anh-khach khong` (hoặc mã `DY-<số>`).
3. Script không cho AI dựng trẻ em (chỉ người lớn), chặn khi vượt trần 500 nghìn / tháng, ghi `<file>.nguon.json`.
4. Xem lại: sản phẩm có bị biến dạng khác hàng thật không → khác thì bỏ.
5. Ghép ở CapCut / Canva: phụ đề, logo, thẻ kết, **nhãn «Video có sử dụng AI»** hiện suốt đoạn có cảnh AI. Khi đăng bật ô
   nhãn AI của nền tảng.

## Không làm

- Không đăng, không hẹn giờ (kênh chưa nối).
- Không dựng cảnh khách hàng giả đang khen sản phẩm.
- Không để video trong repo (bất biến 8).
