<!-- Mẫu PR chung phòng IT Lab Bàn (autoLab docs/mau/pull_request_template.md). Viết cho Sếp đọc. -->

## Tóm tắt cho Sếp
<Đổi gì, vì sao, người dùng thấy gì khác — 2–5 dòng, không chữ kỹ thuật khi không cần.>

**Kế hoạch đã duyệt:** <link file kế hoạch / «việc nhỏ, làm luôn» / «Sếp nói làm luôn»>

## Bằng chứng
- Lệnh đã chạy + kết quả: <vd `npm test` 365/365 · build OK>
- Ảnh màn (nếu đổi giao diện): máy tính + 390px

## Thế nào là xong (autoLab `docs/phong-it-chuyen-nghiep.md` mục 4)
- [ ] Đúng kế hoạch đã duyệt; phần ngoài kế hoạch đã hỏi Sếp
- [ ] Test mới cho luật nghiệp vụ / lỗi đã sửa; CI xanh
- [ ] Người rà (agent riêng) + Codex: lỗi chạm tính đúng đã sửa, phần không sửa có lý do
- [ ] `/security-review` nếu đụng quyền / tiền / SQL / bí mật / tin nhắn
- [ ] Tài liệu + quyết định cập nhật cùng commit
- [ ] Người dùng thấy: mục «Cập nhật» Sếp đã duyệt (repo có mục này)
- [ ] Đụng hạ tầng: đã thử trên máy thật, hoặc ghi rõ «chưa thử được»
- [ ] Đụng cửa với repo khác (sổ luật A19 — autoLab `docs/ban-do-he-thong.md`)? Không / Có: mã cửa __ · ghi «autoLab#<số PR>» (đã cập nhật trung tâm) hoặc «không đổi giao kèo»
