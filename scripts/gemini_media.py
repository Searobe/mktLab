"""Gọi Gemini làm ảnh / video cho bài Lab Bàn — có trần tiền, chặn ảnh khách chưa đồng ý, không ghi file vào repo.

Dùng (skill `lam-anh`, `kich-ban-video` hướng dẫn chi tiết):
    python3 scripts/gemini_media.py anh   --mo-ta "…" --ra ~/LabbanMarketing/ai --ten khung-phong-khach [--anh-goc a.jpg --anh-khach khong]
    python3 scripts/gemini_media.py video --mo-ta "…" --ra ~/LabbanMarketing/ai --ten xuong-in --giay 8
    python3 scripts/gemini_media.py con-lai          # tháng này đã tiêu bao nhiêu
Thêm `--thu` để xem trước giá và yêu cầu, không gọi mạng, không tính tiền.

Luật mktLab giữ ở đây (CLAUDE.md «Bất biến»):
- Bất biến 2: cộng dồn chi phí tháng vào sổ ngoài repo; vượt trần 500 nghìn thì dừng, không gọi.
- Bất biến 4: có ảnh gốc thì bắt buộc khai `--anh-khach khong` hoặc mã đồng ý `DY-<số>`.
- Bất biến 8: thư mục ra phải nằm NGOÀI repo (ảnh / video không vào git).
- Bất biến 3: mỗi file ra kèm `<tên>.nguon.json` ghi «anh_ai: co» — nhãn AI người làm bài phải gắn trước khi đăng.
Khoá: chỉ đọc `GEMINI_API_KEY` từ biến môi trường hoặc dòng đó trong `~/.labban-mkt/gemini.env` — NGOÀI repo, để phiên đọc
repo / web không vô tình đọc được. Khoá chỉ gửi tới máy chủ Gemini, không đi theo chuyển hướng, không in ra màn hình.
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import fcntl
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
THU_MUC_RIENG = Path.home() / ".labban-mkt"  # khoá + sổ chi phí, ngoài repo
MAY_CHU = "https://generativelanguage.googleapis.com/v1beta"
TRAN_THANG = 500_000  # VND / tháng — Sếp chốt 2026-10-11 (bất biến 2)
# VND cho 1 USD. Vietcombank bán 26.465 ngày 02/07/2026; làm tròn LÊN để trần chạm sớm hơn, không muộn hơn. Đổi thì ghi ngày.
TY_GIA = 27_000
# Giá bản trả phí, tra ai.google.dev/gemini-api/docs/pricing ngày 2026-10-16 (trang cập nhật 2026-10-15). USD.
GIA_ANH = {
    "gemini-nano-banana-2.1": {"1K": 0.0336, "2K": 0.0504, "4K": 0.113},
    "gemini-3.1-flash-lite-image": {"1K": 0.0336},
}
GIA_VIDEO_GIAY = {
    "veo-3.1-lite-generate-preview": {"720p": 0.05, "1080p": 0.08},
    "veo-3.1-fast-generate-preview": {"720p": 0.10, "1080p": 0.12},
}
TI_LE_ANH = ("1:1", "4:5", "9:16", "16:9", "3:4", "4:3")
TI_LE_VIDEO = ("9:16", "16:9")
DUOI_VAO = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
MAX_ANH_VAO = 20 * 1024 * 1024
MAX_VIDEO = 500 * 1024 * 1024
MA_DONG_Y = re.compile(r"DY-\d+")
TEN_HOP_LE = re.compile(r"[a-z0-9][a-z0-9-]{0,59}")
TEN_TAC_VU = re.compile(r"(models/[\w.-]+/)?operations/[\w.-]+")
SO_LAN_HOI, GIAY_CHO = 60, 10  # video: hỏi tối đa 10 phút
cho = time.sleep  # test thay bằng hàm không ngủ


class Loi(Exception):
    """Lỗi nói được bằng lời cho người dùng — không bao giờ chứa khoá."""


class TuChoi(Loi):
    """Gemini từ chối yêu cầu (HTTP 4xx) — chắc chắn không tính tiền."""


def doc_khoa() -> str:
    khoa = os.environ.get("GEMINI_API_KEY", "").strip()
    tep = THU_MUC_RIENG / "gemini.env"
    if not khoa and tep.is_file():
        for dong in tep.read_text(encoding="utf-8").splitlines():
            if dong.strip().startswith("GEMINI_API_KEY="):
                khoa = dong.split("=", 1)[1].strip().strip("'\"")
    if not khoa:
        raise Loi("Chưa có GEMINI_API_KEY (biến môi trường hoặc dòng GEMINI_API_KEY=… trong ~/.labban-mkt/gemini.env)")
    return khoa


def thu_muc_ra(ra: str) -> Path:
    duong = Path(ra).expanduser().resolve()
    if duong == GOC or GOC in duong.parents:
        raise Loi("thư mục ra nằm trong repo — ảnh / video không vào git (bất biến 8); chọn thư mục Drive LabbanMarketing")
    duong.mkdir(parents=True, exist_ok=True)
    return duong


def ghi_file(dich: Path, du_lieu: bytes) -> None:
    """Không ghi xuyên liên kết tắt (symlink trỏ vào repo sẽ đưa ảnh vào git — bất biến 8)."""
    if dich.is_symlink() or GOC in dich.resolve().parents:
        raise Loi(f"«{dich.name}» là liên kết tắt hoặc trỏ vào repo — không ghi")
    if dich.exists():
        raise Loi(f"«{dich.name}» đã có — đổi --ten, không ghi đè")
    co = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    with os.fdopen(os.open(dich, co, 0o644), "wb") as f:
        f.write(du_lieu)


def doc_anh_goc(cac_duong: list[str], anh_khach: str | None) -> list[tuple[str, str]]:
    """[(mime, base64)] — chặn khi chưa khai ảnh có khách hay không (bất biến 4)."""
    if anh_khach is not None and anh_khach != "khong" and not MA_DONG_Y.fullmatch(anh_khach):
        raise Loi("--anh-khach chỉ là khong hoặc mã đồng ý DY-<số> — không ghi tên khách (bất biến 4, 5)")
    if not cac_duong:
        return []
    if anh_khach is None:
        raise Loi("có ảnh gốc thì phải khai --anh-khach khong (không có người thật) hoặc mã đồng ý DY-<số> (bất biến 4)")
    if len(cac_duong) > 3:
        raise Loi("tối đa 3 ảnh gốc")
    ket_qua = []
    for chuoi in cac_duong:
        duong = Path(chuoi).expanduser()
        mime = DUOI_VAO.get(duong.suffix.lower())
        if mime is None or not duong.is_file():
            raise Loi(f"ảnh gốc «{duong.name}» không có hoặc không phải jpg / png / webp")
        if duong.stat().st_size > MAX_ANH_VAO:
            raise Loi(f"ảnh gốc «{duong.name}» lớn hơn 20 MB")
        ket_qua.append((mime, base64.b64encode(duong.read_bytes()).decode()))
    return ket_qua


# ---------- sổ chi phí (ngoài repo) ----------
# Mỗi lần ghi: khoá file → đọc lại sổ mới nhất → sửa đúng khoản theo mã → ghi. Hai lệnh chạy cùng lúc không đè nhau.
# Trạng thái: dang-goi / xong / chua-ro (hết giờ, mất mạng — có thể Google đã tính) đều CỘNG vào trần; chỉ `loi` (Gemini
# từ chối yêu cầu) là không cộng.

def tep_so() -> Path:
    return THU_MUC_RIENG / "chi-phi-ai.json"


def doc_so() -> dict:
    tep = tep_so()
    if not tep.is_file():
        return {}
    try:
        so = json.loads(tep.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise Loi(f"sổ chi phí {tep} hỏng — không gọi Gemini nữa, báo Sếp") from None
    if not isinstance(so, dict):
        raise Loi(f"sổ chi phí {tep} hỏng — không gọi Gemini nữa, báo Sếp")
    return so


def sua_so(sua) -> dict:
    tep = tep_so()
    tep.parent.mkdir(parents=True, exist_ok=True)
    with open(tep.with_suffix(".khoa"), "a") as khoa_file:
        fcntl.flock(khoa_file, fcntl.LOCK_EX)
        so = doc_so()
        sua(so)
        tam = tep.with_suffix(".tam")
        tam.write_text(json.dumps(so, ensure_ascii=False, indent=1), encoding="utf-8")
        tam.replace(tep)
    return so


def thang_nay() -> str:
    return dt.date.today().strftime("%Y-%m")


def da_tieu(so: dict, thang: str) -> int:
    return sum(m.get("vnd", 0) for m in so.get(thang, []) if m.get("trang_thai") != "loi")


def giu_tien(usd: float, mo_ta: str) -> str:
    """Ghi trước khoản sắp tiêu; vượt trần thì dừng trước khi gọi mạng (bất biến 2). Trả mã khoản."""
    vnd = round(usd * TY_GIA)
    luc = dt.datetime.now().isoformat(timespec="microseconds")
    ma = f"{luc}-{os.getpid()}"

    def them(so: dict) -> None:
        thang = thang_nay()
        if da_tieu(so, thang) + vnd > TRAN_THANG:
            raise Loi(f"vượt trần {TRAN_THANG:,} đ/tháng (đã tiêu {da_tieu(so, thang):,} đ, việc này ~{vnd:,} đ) — hỏi Sếp")
        so.setdefault(thang, []).append({"ma": ma, "luc": luc, "viec": mo_ta, "usd": usd, "vnd": vnd,
                                         "trang_thai": "dang-goi"})

    sua_so(them)
    return ma


def chot_tien(ma: str, trang_thai: str, usd: float | None = None) -> None:
    def doi(so: dict) -> None:
        for muc in (m for cac in so.values() for m in cac if m.get("ma") == ma):
            muc["trang_thai"] = trang_thai
            if usd is not None:
                muc["usd"], muc["vnd"] = usd, round(usd * TY_GIA)

    sua_so(doi)


# ---------- gọi mạng ----------

def goi(url: str, khoa: str, than: dict | None = None, han: int = 180) -> dict:
    if not url.startswith(MAY_CHU + "/"):
        raise Loi("chỉ được gọi máy chủ Gemini")
    du_lieu = json.dumps(than).encode() if than is not None else None
    yeu_cau = urllib.request.Request(url, data=du_lieu, method="POST" if than is not None else "GET")
    yeu_cau.add_unredirected_header("x-goog-api-key", khoa)
    yeu_cau.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(yeu_cau, timeout=han) as tra_loi:
            return json.loads(tra_loi.read())
    except urllib.error.HTTPError as loi:
        chu = loi.read().decode("utf-8", "replace")[:300].replace(khoa, "***")
        lop = TuChoi if 400 <= loi.code < 500 else Loi
        raise lop(f"Gemini báo lỗi {loi.code}: {chu}") from None
    except (OSError, ValueError) as loi:  # mất mạng, hết giờ, trả lời không phải JSON
        raise Loi(f"không gọi được Gemini: {getattr(loi, 'reason', loi)}") from None


def tai_ve(uri: str, khoa: str, dich: Path) -> None:
    if not uri.startswith("https://generativelanguage.googleapis.com/"):
        raise Loi("địa chỉ video lạ — không tải")
    yeu_cau = urllib.request.Request(uri)
    yeu_cau.add_unredirected_header("x-goog-api-key", khoa)
    try:
        with urllib.request.urlopen(yeu_cau, timeout=300) as tra_loi:
            du_lieu = tra_loi.read(MAX_VIDEO + 1)
    except OSError as loi:
        raise Loi(f"không tải được video: {getattr(loi, 'code', loi)}") from None
    if len(du_lieu) > MAX_VIDEO:
        raise Loi("video tải về lớn quá 500 MB — dừng")
    ghi_file(dich, du_lieu)


def tim_anh(nut: object) -> list[bytes]:
    if isinstance(nut, dict):
        if nut.get("type") == "image" and isinstance(nut.get("data"), str):
            return [base64.b64decode(nut["data"])]
        trong = nut.get("inlineData") or nut.get("inline_data")
        if isinstance(trong, dict) and str(trong.get("mimeType", trong.get("mime_type", ""))).startswith("image/"):
            return [base64.b64decode(trong["data"])]
        return [anh for gia_tri in nut.values() for anh in tim_anh(gia_tri)]
    if isinstance(nut, list):
        return [anh for con in nut for anh in tim_anh(con)]
    return []


def anh_tra_ve(tra_loi: dict) -> list[bytes]:
    """Chỉ lấy ảnh ở bước model trả ra (không lấy lại ảnh gốc mình gửi), bỏ trùng."""
    buoc = [b for b in tra_loi.get("steps", []) if isinstance(b, dict) and b.get("type") == "model_output"]
    ket_qua: list[bytes] = []
    for anh in tim_anh(buoc or tra_loi):
        if anh not in ket_qua:
            ket_qua.append(anh)
    return ket_qua


# ---------- việc chính ----------

def ghi_nguon(dich: Path, model: str, a: argparse.Namespace, vnd: int) -> None:
    nguon = {"ngay": dt.date.today().isoformat(), "model": model, "mo_ta": a.mo_ta,
             "anh_goc": [Path(p).name for p in a.anh_goc], "anh_khach": a.anh_khach or "khong", "chi_phi_vnd": vnd,
             "anh_ai": "co", "nhan_ai": "PHẢI gắn nhãn AI trước khi đăng (bất biến 3)"}
    ghi_file(Path(f"{dich}.nguon.json"), json.dumps(nguon, ensure_ascii=False, indent=1).encode("utf-8"))


def goi_co_so(ma: str, ham):
    """Gemini từ chối (4xx) → khoản không tính; lỗi khác (mất mạng, hết giờ) → vẫn tính, vì Google có thể đã làm."""
    try:
        return ham()
    except TuChoi:
        chot_tien(ma, "loi")
        raise
    except Loi:
        chot_tien(ma, "chua-ro")
        raise


def lam_anh(a: argparse.Namespace) -> list[Path]:
    gia = GIA_ANH[a.model].get(a.co)
    if gia is None:
        raise Loi(f"{a.model} không làm cỡ {a.co}; chọn {sorted(GIA_ANH[a.model])}")
    anh_goc = doc_anh_goc(a.anh_goc, a.anh_khach)
    phan = [{"type": "text", "text": a.mo_ta}] + [{"type": "image", "mime_type": m, "data": d} for m, d in anh_goc]
    than = {"model": a.model, "input": phan if anh_goc else a.mo_ta,
            "response_format": {"type": "image", "mime_type": "image/png", "aspect_ratio": a.ti_le, "image_size": a.co}}
    if a.thu:
        print(f"[thử] ảnh {a.model} {a.co} {a.ti_le} · ~{round(gia * TY_GIA):,} đ · {len(anh_goc)} ảnh gốc")
        return []
    ra, khoa = thu_muc_ra(a.ra), doc_khoa()
    ma = giu_tien(gia, f"anh {a.ten}")
    cac_anh = goi_co_so(ma, lambda: anh_tra_ve(goi(f"{MAY_CHU}/interactions", khoa, than)))
    if not cac_anh:
        chot_tien(ma, "loi")
        raise Loi("Gemini không trả ảnh (có thể bộ lọc an toàn chặn) — sửa mô tả rồi thử lại")
    chot_tien(ma, "xong", gia * len(cac_anh))
    ket_qua = []
    for thu_tu, du_lieu in enumerate(cac_anh, 1):
        dich = ra / f"{a.ten}-{thu_tu}.png"
        ghi_file(dich, du_lieu)
        ghi_nguon(dich, a.model, a, round(gia * TY_GIA))
        ket_qua.append(dich)
    return ket_qua


def than_video(a: argparse.Namespace, anh_goc: list[tuple[str, str]]) -> dict:
    canh: dict = {"prompt": a.mo_ta}
    if anh_goc:
        canh["image"] = {"inlineData": {"mimeType": anh_goc[0][0], "data": anh_goc[0][1]}}
    # allow_adult: không cho AI dựng hình trẻ em; cũng là giá trị duy nhất được nhận khi có ảnh gốc.
    tham_so = {"aspectRatio": a.ti_le, "resolution": a.do_net, "durationSeconds": str(a.giay),
               "personGeneration": "allow_adult"}
    return {"instances": [canh], "parameters": tham_so}


def doi_video(ten_tac_vu: str, khoa: str) -> str:
    if not TEN_TAC_VU.fullmatch(ten_tac_vu):
        raise Loi("Gemini trả tên tác vụ lạ")
    for _ in range(SO_LAN_HOI):
        trang_thai = goi(f"{MAY_CHU}/{ten_tac_vu}", khoa, han=60)
        if trang_thai.get("done"):
            if "error" in trang_thai:
                loi = trang_thai["error"]
                chu = loi.get("message", "") if isinstance(loi, dict) else loi
                raise Loi(f"Gemini không làm được video: {str(chu)[:200]}")
            try:
                return trang_thai["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
            except (KeyError, IndexError, TypeError):
                raise Loi("Gemini không trả video (có thể bộ lọc an toàn chặn)") from None
        cho(GIAY_CHO)
    raise Loi(f"chờ quá 10 phút chưa xong — tác vụ {ten_tac_vu} vẫn chạy trên Gemini và vẫn tính tiền (đã cộng vào sổ)")


def lam_video(a: argparse.Namespace) -> list[Path]:
    if a.ti_le not in TI_LE_VIDEO:
        raise Loi(f"video chỉ có tỉ lệ {TI_LE_VIDEO}")
    if a.do_net == "1080p" and a.giay != 8:
        raise Loi("1080p chỉ làm được video 8 giây")
    gia = GIA_VIDEO_GIAY[a.model][a.do_net] * a.giay
    anh_goc = doc_anh_goc(a.anh_goc[:1], a.anh_khach)
    if a.thu:
        print(f"[thử] video {a.model} {a.do_net} {a.giay}s {a.ti_le} · ~{round(gia * TY_GIA):,} đ")
        return []
    ra, khoa = thu_muc_ra(a.ra), doc_khoa()
    ma = giu_tien(gia, f"video {a.ten}")
    tac_vu = goi_co_so(ma, lambda: goi(f"{MAY_CHU}/models/{a.model}:predictLongRunning", khoa, than_video(a, anh_goc)))
    try:
        uri = doi_video(str(tac_vu.get("name", "")), khoa)
    except Loi:
        chot_tien(ma, "chua-ro")  # tác vụ đã nhận — Google có thể vẫn làm và vẫn tính tiền
        raise
    chot_tien(ma, "xong")
    dich = ra / f"{a.ten}.mp4"
    tai_ve(uri, khoa, dich)
    ghi_nguon(dich, a.model, a, round(gia * TY_GIA))
    return [dich]


def con_lai(_: argparse.Namespace) -> list[Path]:
    so, thang = doc_so(), thang_nay()
    print(f"Tháng {thang}: đã tiêu {da_tieu(so, thang):,} đ / trần {TRAN_THANG:,} đ")
    return []


def tao_lenh() -> argparse.ArgumentParser:
    goc = argparse.ArgumentParser(description="Gemini làm ảnh / video cho bài Lab Bàn")
    con = goc.add_subparsers(dest="viec", required=True)
    for ten, mac_dinh_model, cac_model in (("anh", "gemini-nano-banana-2.1", GIA_ANH),
                                          ("video", "veo-3.1-lite-generate-preview", GIA_VIDEO_GIAY)):
        p = con.add_parser(ten)
        p.add_argument("--mo-ta", required=True, help="mô tả cảnh muốn tạo")
        p.add_argument("--ra", required=True, help="thư mục lưu, NGOÀI repo (Drive LabbanMarketing)")
        p.add_argument("--ten", required=True, type=ten_file, help="tên file: chữ thường, số, gạch nối")
        p.add_argument("--anh-goc", nargs="*", default=[], help="ảnh chụp thật làm gốc (≤ 3; video dùng ảnh đầu)")
        p.add_argument("--anh-khach", help="khong hoặc DY-<số> — bắt buộc khi có ảnh gốc")
        p.add_argument("--model", default=mac_dinh_model, choices=sorted(cac_model))
        p.add_argument("--thu", action="store_true", help="xem trước giá, không gọi mạng")
    con.choices["anh"].add_argument("--ti-le", default="4:5", choices=TI_LE_ANH)
    con.choices["anh"].add_argument("--co", default="1K", choices=("1K", "2K", "4K"))
    con.choices["video"].add_argument("--ti-le", default="9:16", choices=TI_LE_VIDEO)
    con.choices["video"].add_argument("--giay", type=int, default=8, choices=(4, 6, 8))
    con.choices["video"].add_argument("--do-net", default="720p", choices=("720p", "1080p"))
    con.add_parser("con-lai")
    return goc


def ten_file(chuoi: str) -> str:
    if not TEN_HOP_LE.fullmatch(chuoi):
        raise argparse.ArgumentTypeError("chỉ chữ thường không dấu, số, gạch nối (≤ 60 ký tự)")
    return chuoi


def main(doi_so: list[str] | None = None) -> int:
    a = tao_lenh().parse_args(doi_so)
    viec = {"anh": lam_anh, "video": lam_video, "con-lai": con_lai}[a.viec]
    try:
        cac_file = viec(a)
    except Loi as loi:
        print(f"✗ {loi}", file=sys.stderr)
        return 1
    for f in cac_file:
        print(f"✓ {f}")
    if cac_file:
        print("👉 Bài dùng file này: anh_ai: co · nhan_ai: co · gắn chữ «Ảnh / video có sử dụng AI» và bật ô nhãn AI khi đăng.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
