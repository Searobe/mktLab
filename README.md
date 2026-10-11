# mktLab — phòng marketing Lab Bàn

Nơi phòng marketing của **Lab Bàn** làm việc: hồ sơ thương hiệu, dữ kiện sản phẩm, lịch nội dung, bài đăng, kế hoạch
quảng cáo. Luật làm việc ở `CLAUDE.md`. Kế hoạch dựng phòng ở autoLab `docs/ke-hoach/2026-10-11-mktlab.md`.

## Dùng thế nào

Mở phiên Claude ở repo này rồi nói việc cần làm, ví dụ «viết 5 bài Facebook tuần này về khung tranh cho khách lẻ».
Claude đọc giọng văn ở `thuong-hieu/` và dữ kiện ở `san-pham/`, viết nháp vào `bai/`, mở PR. Sếp duyệt rồi mới đăng.

## Kiểm

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements-kiem.txt
.venv/bin/python -m unittest discover -s tests && .venv/bin/python scripts/kiem_kho.py
```
