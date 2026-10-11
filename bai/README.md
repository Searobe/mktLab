# Bài đăng

Mỗi bài một file `bai/<yyyy-mm>/<ten-bai>.md`, tháng theo ngày dự kiến đăng. Máy canh `scripts/kiem_kho.py` kiểm khuôn.
Chiến lược, trụ nội dung, cách đo: `chien-luoc/organic.md`.

## Khuôn

```yaml
---
kenh: [tiktok, facebook, instagram, youtube]   # một video đăng nhiều kênh
ngay_dang: 2026-10-20 20:00   # giờ Việt Nam
dinh_dang: video        # video · anh · chu
tru: bien-hinh          # bien-hinh · hau-truong · cau-chuyen · meo · bat-song
trang_thai: nhap        # nhap · da-duyet · da-dang
ngay_duyet:             # yyyy-mm-dd — bắt buộc khi da-duyet / da-dang
anh_ai: khong           # co · khong — ảnh / video có do AI tạo hoặc sửa không
nhan_ai: khong          # co · khong — đã gắn nhãn AI chưa (anh_ai: co thì phải co)
dong_y: khong           # khong · [DY-12, DY-15] — mã phiếu đồng ý, MỖI người lộ mặt (khách, nhân viên) một mã; không ghi tên
anh: []                 # đường dẫn Drive LabbanMarketing, không để ảnh trong git
so_7_ngay:              # điền sau 7 ngày; chưa có số thì để trống, KHÔNG ghi 0
  xem:
  giu_3_giay:           # %
  xem_het:              # %
  chia_se:              # gồm gửi tin nhắn
  luu:
  hoi_gia:              # số tin nhắn hỏi giá / đặt hàng
---
Câu mở đầu (3 giây đầu):

Kịch bản / nội dung:

Danh sách cảnh cần quay (video):

Chú thích đăng kèm:
```

## Luật (CLAUDE.md «Bất biến»)

- Chỉ ghi `da-duyet` khi Sếp đã duyệt đúng bài đó.
- Giá, khuyến mãi, cam kết lấy từ `san-pham/`.
- Ảnh AI dễ tưởng là thật thì gắn nhãn. Ảnh khách, nhân viên lộ mặt phải có mã đồng ý.
