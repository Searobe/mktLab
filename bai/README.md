# Bài đăng

Mỗi bài một file `bai/<yyyy-mm>/<ten-bai>.md`, tháng theo ngày dự kiến đăng. Máy canh `scripts/kiem_kho.py` kiểm khuôn.

## Khuôn

```yaml
---
kenh: facebook          # facebook · instagram · zalo-oa · google · tiktok
ngay_dang: 2026-10-20 19:00   # giờ Việt Nam
trang_thai: nhap        # nhap · da-duyet · da-dang
ngay_duyet:             # yyyy-mm-dd — bắt buộc khi da-duyet / da-dang
anh_ai: khong           # co · khong — ảnh / video có do AI tạo hoặc sửa không
nhan_ai: khong          # co · khong — đã gắn nhãn AI chưa (anh_ai: co thì phải co)
anh_khach: khong        # khong · DY-<số> — mã phiếu khách đồng ý, không ghi tên
anh: []                 # đường dẫn Drive LabbanMarketing, không để ảnh trong git
---
Nội dung bài.
```

## Luật (CLAUDE.md «Bất biến»)

- Chỉ ghi `da-duyet` khi Sếp đã duyệt đúng bài đó.
- Giá, khuyến mãi, cam kết lấy từ `san-pham/`.
- Ảnh AI dễ tưởng là thật thì gắn nhãn. Ảnh khách phải có mã đồng ý.
