"""Thử phá máy canh `scripts/kiem_kho.py`: mỗi bất biến có một ca vi phạm phải ĐỎ và một ca đúng phải XANH.

Số điện thoại, email trong file này là số giả để thử (máy canh bỏ qua thư mục tests/ khi quét repo thật).
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import kiem_kho  # noqa: E402

BAI_DUNG = """---
kenh: facebook
dinh_dang: video
tru: bien-hinh
trang_thai: da-duyet
ngay_duyet: 2026-10-20
anh_ai: co
nhan_ai: co
anh_khach: khong
---
Nội dung bài.
"""


class CoKho(unittest.TestCase):
    def setUp(self) -> None:
        self._tam = tempfile.TemporaryDirectory()
        self.goc = Path(self._tam.name)

    def tearDown(self) -> None:
        self._tam.cleanup()

    def ghi(self, duong: str, noi_dung: str | bytes) -> None:
        f = self.goc / duong
        f.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(noi_dung, bytes):
            f.write_bytes(noi_dung)
        else:
            f.write_text(noi_dung, encoding="utf-8")


class KiemAnh(CoKho):
    def test_anh_ngoai_logo_bi_chan(self) -> None:
        self.ghi("bai/2026-10/anh.jpg", b"\xff\xd8")
        self.ghi("quang-cao/video.MP4", b"0")
        self.assertEqual(len(kiem_kho.kiem_anh(self.goc)), 2)

    def test_file_van_phong_bi_chan(self) -> None:
        self.ghi("chien-luoc/khach.xlsx", b"PK")
        self.ghi("san-pham/gia.DOCX", b"PK")
        self.assertEqual(len(kiem_kho.kiem_anh(self.goc)), 2)

    def test_logo_nho_duoc_qua(self) -> None:
        self.ghi("thuong-hieu/logo/logo.png", b"\x89PNG")
        self.assertEqual(kiem_kho.kiem_anh(self.goc), [])

    def test_logo_qua_1mb_bi_chan(self) -> None:
        self.ghi("thuong-hieu/logo/to.png", b"0" * (kiem_kho.MAX_LOGO + 1))
        self.assertIn("vượt 1 MB", kiem_kho.kiem_anh(self.goc)[0])


class KiemBai(CoKho):
    def test_bai_dung_khuon_xanh(self) -> None:
        self.ghi("bai/2026-10/khung-tranh.md", BAI_DUNG)
        self.ghi("bai/README.md", "khuôn bài, không phải bài")
        self.assertEqual(kiem_kho.kiem_bai(self.goc), [])

    def test_da_duyet_thieu_ngay_duyet(self) -> None:
        self.ghi("bai/2026-10/a.md", BAI_DUNG.replace("ngay_duyet: 2026-10-20\n", ""))
        self.assertIn("ngay_duyet", kiem_kho.kiem_bai(self.goc)[0])

    def test_anh_ai_thieu_nhan(self) -> None:
        self.ghi("bai/2026-10/a.md", BAI_DUNG.replace("nhan_ai: co", "nhan_ai: khong"))
        self.assertIn("nhan_ai", kiem_kho.kiem_bai(self.goc)[0])

    def test_anh_khach_khong_co_ma_dong_y(self) -> None:
        self.ghi("bai/2026-10/a.md", BAI_DUNG.replace("anh_khach: khong", "anh_khach: Chị Lan"))
        self.assertIn("DY-", kiem_kho.kiem_bai(self.goc)[0])

    def test_anh_khach_co_ma_dong_y_xanh(self) -> None:
        self.ghi("bai/2026-10/a.md", BAI_DUNG.replace("anh_khach: khong", "anh_khach: DY-12"))
        self.assertEqual(kiem_kho.kiem_bai(self.goc), [])

    def test_trang_thai_la(self) -> None:
        self.ghi("bai/2026-10/a.md", BAI_DUNG.replace("da-duyet", "xong"))
        self.assertIn("trang_thai", kiem_kho.kiem_bai(self.goc)[0])

    def test_dinh_dang_va_tru_la(self) -> None:
        self.ghi("bai/2026-10/a.md", BAI_DUNG.replace("dinh_dang: video", "dinh_dang: reel").replace("tru: bien-hinh", "tru: khac"))
        loi = kiem_kho.kiem_bai(self.goc)
        self.assertEqual(len(loi), 2)
        self.assertIn("dinh_dang", loi[0])
        self.assertIn("tru", loi[1])

    def test_bai_sai_cho_va_thieu_frontmatter(self) -> None:
        self.ghi("bai/a.md", BAI_DUNG)
        self.ghi("bai/2026-10/b.md", "không có frontmatter")
        self.ghi("bai/2026-10/c.txt", BAI_DUNG)
        loi = kiem_kho.kiem_bai(self.goc)
        self.assertEqual(len(loi), 3)


class KiemSkill(CoKho):
    def test_skill_dung(self) -> None:
        self.ghi(".claude/skills/viet-bai-fb/SKILL.md", "---\nname: viet-bai-fb\ndescription: Dùng khi viết bài FB.\n---\n")
        self.assertEqual(kiem_kho.kiem_skill(self.goc), [])

    def test_skill_sai_ten_long_sau(self) -> None:
        self.ghi(".claude/skills/viet-bai-fb/SKILL.md", "---\nname: viet-bai\ndescription: x\n---\n")
        self.ghi(".claude/skills/nhom/con/SKILL.md", "---\nname: con\ndescription: x\n---\n")
        self.assertEqual(len(kiem_kho.kiem_skill(self.goc)), 2)


class KiemCodeSach(CoKho):
    def test_file_qua_dai(self) -> None:
        self.ghi("chien-luoc/dai.md", "dòng\n" * 401)
        self.assertIn("vượt 400", kiem_kho.kiem_code_sach(self.goc)[0])

    def test_ham_qua_dai(self) -> None:
        than = "".join(f"    x{i} = {i}\n" for i in range(61))
        self.ghi("scripts/a.py", f"def dai():\n{than}")
        self.assertIn("hàm dai", kiem_kho.kiem_code_sach(self.goc)[0])


class KiemDuLieuCaNhan(CoKho):
    def test_so_dien_thoai_bi_bat(self) -> None:
        self.ghi("bai/2026-10/a.md", "Gọi 0912 345 678 nhé")
        self.ghi("chien-luoc/b.md", "SĐT.0987654321")
        self.assertEqual(len(kiem_kho.kiem_du_lieu_ca_nhan(self.goc)), 2)

    def test_so_viet_nhu_tien_van_bi_bat(self) -> None:
        self.ghi("a.md", "SĐT 091.234.567")
        self.ghi("b.md", "CCCD 001.234.567.890")
        self.ghi("c.md", "gọi 84.912.345.678")
        self.assertEqual(len(kiem_kho.kiem_du_lieu_ca_nhan(self.goc)), 3)

    def test_so_tien_khong_bi_bat(self) -> None:
        self.ghi("san-pham/gia.md", "Khung 60x90: 1.250.000 đồng, album 15.000.000 12.500.000, quỹ 1.250.000.000")
        self.assertEqual(kiem_kho.kiem_du_lieu_ca_nhan(self.goc), [])

    def test_ngay_gio_khong_bi_bat(self) -> None:
        self.ghi("bai/2026-10/a.md", "ngay_dang: 2026-10-20 19:00\nngay_duyet: 2026-10-18")
        self.assertEqual(kiem_kho.kiem_du_lieu_ca_nhan(self.goc), [])

    def test_email_ca_nhan_bi_bat_email_cong_ty_qua(self) -> None:
        self.ghi("a.md", "liên hệ khach.hang@gmail.com")
        self.ghi("b.md", "hộp thư info@labban.vn và demo@example.com")
        loi = kiem_kho.kiem_du_lieu_ca_nhan(self.goc)
        self.assertEqual(len(loi), 1)
        self.assertTrue(loi[0].startswith("a.md"))


class KiemRepoThat(unittest.TestCase):
    def test_repo_hien_tai_sach(self) -> None:
        self.assertEqual(kiem_kho.kiem(kiem_kho.GOC), [])


if __name__ == "__main__":
    unittest.main()
