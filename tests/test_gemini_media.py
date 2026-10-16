"""Thử phá scripts/gemini_media.py — không gọi mạng thật (thay urlopen bằng hàm giả)."""
from __future__ import annotations

import base64
import io
import json
import os
import sys
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import gemini_media as gm  # noqa: E402

KHOA = "khoa-gia-de-thu"
ANH_PNG = b"\x89PNG-anh-gia"


class TraLoiGia(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def tra_json(du_lieu: dict) -> TraLoiGia:
    return TraLoiGia(json.dumps(du_lieu).encode())


class CoSo(unittest.TestCase):
    def setUp(self) -> None:
        self.tam = tempfile.TemporaryDirectory()
        self.goc = Path(self.tam.name)
        self.ra = self.goc / "ra"
        env = {"LABBAN_SO_CHI_PHI": str(self.goc / "so.json"), "GEMINI_API_KEY": KHOA}
        self.env = mock.patch.dict(os.environ, env)
        self.env.start()
        self.goi_mang: list = []

    def tearDown(self) -> None:
        self.env.stop()
        self.tam.cleanup()

    def chay(self, *doi_so: str, tra_loi=None) -> tuple[int, str]:
        cac_tra_loi = list(tra_loi or [])

        def urlopen_gia(yeu_cau, timeout=0):
            self.goi_mang.append(yeu_cau)
            kq = cac_tra_loi.pop(0)
            if isinstance(kq, Exception):
                raise kq
            return kq

        ra, loi = io.StringIO(), io.StringIO()
        with mock.patch.object(gm.urllib.request, "urlopen", urlopen_gia), mock.patch.object(gm, "cho", lambda _: None):
            with redirect_stdout(ra), redirect_stderr(loi):
                ma = gm.main(list(doi_so))
        return ma, ra.getvalue() + loi.getvalue()

    def anh_goc(self) -> str:
        duong = self.goc / "goc.jpg"
        duong.write_bytes(b"jpg")
        return str(duong)


class TestChan(CoSo):
    def test_ra_trong_repo_bi_chan(self):
        ma, chu = self.chay("anh", "--mo-ta", "x", "--ra", str(gm.GOC / "bai"), "--ten", "a", tra_loi=[])
        self.assertEqual(ma, 1)
        self.assertIn("bất biến 8", chu)
        self.assertEqual(self.goi_mang, [])

    def test_anh_goc_khong_khai_khach_bi_chan(self):
        ma, chu = self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a", "--anh-goc", self.anh_goc())
        self.assertEqual(ma, 1)
        self.assertIn("bất biến 4", chu)

    def test_anh_goc_khai_ten_khach_bi_chan(self):
        ma, _ = self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a", "--anh-goc", self.anh_goc(),
                          "--anh-khach", "Nguyen Van A")
        self.assertEqual(ma, 1)

    def test_vuot_tran_khong_goi_mang(self):
        gm.ghi_so({gm.thang_nay(): [{"vnd": gm.TRAN_THANG, "trang_thai": "xong"}]})
        ma, chu = self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a", tra_loi=[])
        self.assertEqual(ma, 1)
        self.assertIn("vượt trần", chu)
        self.assertEqual(self.goi_mang, [])

    def test_ten_file_la_bi_chan(self):
        with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
            gm.main(["anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "../thoat"])

    def test_dia_chi_video_la_khong_tai(self):
        with self.assertRaises(gm.Loi):
            gm.tai_ve("https://ke-xau.example.com/v.mp4", KHOA, self.goc / "v.mp4")

    def test_loi_mang_khong_lo_khoa(self):
        loi = urllib.error.HTTPError("u", 400, "x", {}, io.BytesIO(f"sai khoa {KHOA}".encode()))
        ma, chu = self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a", tra_loi=[loi])
        self.assertEqual(ma, 1)
        self.assertNotIn(KHOA, chu)
        self.assertEqual(gm.da_tieu(gm.doc_so(), gm.thang_nay()), 0)  # lỗi thì không tính tiền

    def test_khoa_khong_theo_chuyen_huong(self):
        self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a",
                  tra_loi=[tra_json({"steps": []})])
        yeu_cau = self.goi_mang[0]
        self.assertNotIn("X-goog-api-key", yeu_cau.headers)
        self.assertEqual(yeu_cau.unredirected_hdrs.get("X-goog-api-key"), KHOA)

    def test_thieu_khoa(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": ""}), mock.patch.object(gm, "GOC", self.goc):
            with self.assertRaises(gm.Loi):
                gm.doc_khoa()


class TestChay(CoSo):
    def test_thu_khong_goi_mang_khong_tinh_tien(self):
        ma, chu = self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a", "--thu", tra_loi=[])
        self.assertEqual(ma, 0)
        self.assertIn("[thử]", chu)
        self.assertEqual(self.goi_mang, [])
        self.assertEqual(gm.doc_so(), {})

    def test_lam_anh_ghi_file_nguon_va_so(self):
        tra = {"steps": [{"type": "user_input", "content": [{"type": "image", "data": base64.b64encode(b"goc").decode()}]},
                         {"type": "model_output", "content": [{"type": "image", "data": base64.b64encode(ANH_PNG).decode()}]}]}
        ma, chu = self.chay("anh", "--mo-ta", "khung tranh phòng khách", "--ra", str(self.ra), "--ten", "khung",
                            "--anh-goc", self.anh_goc(), "--anh-khach", "khong", tra_loi=[tra_json(tra)])
        self.assertEqual(ma, 0, chu)
        self.assertEqual((self.ra / "khung-1.png").read_bytes(), ANH_PNG)
        self.assertFalse((self.ra / "khung-2.png").exists())  # không lấy lại ảnh gốc
        nguon = json.loads((self.ra / "khung-1.png.nguon.json").read_text(encoding="utf-8"))
        self.assertEqual(nguon["anh_ai"], "co")
        self.assertEqual(nguon["anh_goc"], ["goc.jpg"])  # chỉ tên, không đường dẫn
        self.assertGreater(gm.da_tieu(gm.doc_so(), gm.thang_nay()), 0)
        self.assertIn("nhan_ai: co", chu)

    def test_khong_tra_anh_thi_khong_tinh_tien(self):
        ma, _ = self.chay("anh", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "a", tra_loi=[tra_json({"steps": []})])
        self.assertEqual(ma, 1)
        self.assertEqual(gm.da_tieu(gm.doc_so(), gm.thang_nay()), 0)

    def test_lam_video(self):
        uri = "https://generativelanguage.googleapis.com/v1beta/files/abc:download?alt=media"
        xong = {"done": True, "response": {"generateVideoResponse": {"generatedSamples": [{"video": {"uri": uri}}]}}}
        ma, chu = self.chay("video", "--mo-ta", "xưởng in", "--ra", str(self.ra), "--ten", "xuong", "--giay", "4",
                            tra_loi=[tra_json({"name": "models/veo-3.1-lite-generate-preview/operations/op1"}),
                                     tra_json({"done": False}), tra_json(xong), TraLoiGia(b"mp4")])
        self.assertEqual(ma, 0, chu)
        self.assertEqual((self.ra / "xuong.mp4").read_bytes(), b"mp4")
        than = json.loads(self.goi_mang[0].data)
        self.assertEqual(than["parameters"]["personGeneration"], "allow_adult")
        self.assertEqual(than["parameters"]["durationSeconds"], "4")

    def test_video_1080p_phai_8_giay(self):
        ma, chu = self.chay("video", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "v", "--giay", "4",
                            "--do-net", "1080p", tra_loi=[])
        self.assertEqual(ma, 1)
        self.assertIn("8 giây", chu)

    def test_ten_tac_vu_la_bi_chan(self):
        ma, chu = self.chay("video", "--mo-ta", "x", "--ra", str(self.ra), "--ten", "v",
                            tra_loi=[tra_json({"name": "../../ke-xau"})])
        self.assertEqual(ma, 1)
        self.assertIn("tên tác vụ lạ", chu)


if __name__ == "__main__":
    unittest.main()
