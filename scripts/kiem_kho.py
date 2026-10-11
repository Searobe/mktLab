"""Máy canh phòng marketing Lab Bàn (CLAUDE.md «Bất biến»; sổ luật autoLab A2, A3, A9). Lập 2026-10-11.

Chạy: python scripts/kiem_kho.py  (cần pyyaml==6.0.2, mccabe==0.7.0 — xem requirements-kiem.txt). Mã thoát 1 = có lỗi.

Canh 6 thứ:
1. Ảnh / video / file thiết kế không vào git (bất biến 8). Ngoại lệ: `thuong-hieu/logo/`, mỗi file ≤ 1 MB.
2. Khuôn bài `bai/<yyyy-mm>/<ten>.md` (bất biến 1, 3, 4): `trang_thai` hợp lệ; `da-duyet` / `da-dang` có `ngay_duyet`;
   `anh_ai: co` thì `nhan_ai: co`; `anh_khach` là `khong` hoặc mã đồng ý `DY-<số>`.
3. Skill `.claude/skills/<tên>/SKILL.md` theo đặc tả Agent Skills (agentskills.io/specification, rà 2026-10-09 ở
   labban-skills): `name` chữ thường / số / gạch nối ≤ 64 ký tự, trùng tên thư mục; `description` có chữ, ≤ 1024 ký tự.
4. Code sạch (autoLab `docs/chuan-code-chung.md`): file ≤ 400 dòng; hàm Python ≤ 60 dòng, lồng ≤ 4, McCabe ≤ 15.
5. Dãy ≥ 9 chữ số liền (điện thoại, tài khoản, CCCD) — dữ liệu cá nhân không vào repo (bất biến 5).
6. Địa chỉ email, trừ tên miền ở MIEN_EMAIL_DUOC.
Phần đo hàm và số dài chép từ labban-skills `scripts/kiem_kho.py` (đã thử phá ở đó).
"""
from __future__ import annotations

import ast
import datetime as dt
import re
import sys
from pathlib import Path

import mccabe
import yaml

GOC = Path(__file__).resolve().parent.parent
TEN_HOP_LE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# Cụm số cách khúc bằng một dấu cách / chấm / gạch, khúc có thể trong ngoặc. Bỏ qua số tiền chấm hàng nghìn và toạ độ SVG.
SO_DAI = re.compile(r"\(?\d+\)?(?:[ .\-]\(?\d+\)?)*")
SO_TIEN = re.compile(r"^\d{1,3}(?:[.,]\d{3})+$")
# Ngày ISO (`ngay_dang: 2026-10-20 19:00` ở mọi bài) xoá trước khi tìm số dài — không thì ngày + giờ thành cụm 12 chữ số.
NGAY_ISO = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@([A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+)")
MIEN_EMAIL_DUOC = {"labban.vn", "example.com"}
DUOI_KIEM = {".md", ".py", ".json", ".yaml", ".yml", ".txt", ".sh", ".js", ".html", ".css", ".csv", ".toml"}
DUOI_ANH = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".tif", ".tiff", ".bmp", ".svg", ".raw", ".cr2", ".nef",
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".psd", ".ai", ".indd", ".pdf", ".zip",
    # File văn phòng hay chứa danh sách khách — máy không đọc được bên trong nên cấm hẳn (bất biến 5).
    ".xlsx", ".xls", ".xlsm", ".docx", ".doc", ".pptx", ".ppt", ".numbers", ".pages", ".key",
}
THU_MUC_LOGO = "thuong-hieu/logo/"
MAX_LOGO = 1024 * 1024
TRANG_THAI = {"nhap", "da-duyet", "da-dang"}
MA_DONG_Y = re.compile(r"^DY-\d+$")
MAX_DONG_FILE, MAX_DONG_HAM, MAX_LONG, MAX_PHUC_TAP = 400, 60, 4, 15
BO_QUA = {".git", "node_modules", ".venv", "venv", "__pycache__"}

# Nợ cũ — bánh cóc: chỉ giảm. Khởi tạo 2026-10-11 không có nợ.
NO_CU: dict[str, int] = {}
NO_HAM_CU: dict[tuple[str, str], tuple[int, int, int]] = {}
NO_SO_CU: dict[str, int] = {}


def moi_file(goc: Path) -> list[Path]:
    return sorted(f for f in goc.rglob("*") if f.is_file() and not BO_QUA.intersection(f.relative_to(goc).parts))


def cac_file(goc: Path) -> list[Path]:
    return [f for f in moi_file(goc) if f.suffix.lower() in DUOI_KIEM]


def doc_frontmatter(van: str) -> dict | None:
    if not van.startswith("---\n"):
        return None
    cuoi = van.find("\n---", 4)
    if cuoi < 0:
        return None
    try:
        du_lieu = yaml.safe_load(van[4:cuoi])
    except yaml.YAMLError:
        return None
    return du_lieu if isinstance(du_lieu, dict) else None


def kiem_anh(goc: Path) -> list[str]:
    loi: list[str] = []
    for f in moi_file(goc):
        duong = f.relative_to(goc).as_posix()
        if f.suffix.lower() not in DUOI_ANH:
            continue
        if not duong.startswith(THU_MUC_LOGO):
            loi.append(f"{duong}: ảnh / video / file thiết kế không vào git — để ở Drive LabbanMarketing, bài ghi đường dẫn")
        elif f.stat().st_size > MAX_LOGO:
            loi.append(f"{duong}: logo {f.stat().st_size // 1024} KB — vượt 1 MB")
    return loi


def la_ngay(gia_tri: object) -> bool:
    if isinstance(gia_tri, dt.date):
        return True
    try:
        dt.date.fromisoformat(str(gia_tri))
    except ValueError:
        return False
    return True


def loi_khuon_bai(fm: dict) -> list[str]:
    loi: list[str] = []
    trang_thai = fm.get("trang_thai")
    if trang_thai not in TRANG_THAI:
        loi.append(f"trang_thai «{trang_thai}» phải là một trong {sorted(TRANG_THAI)}")
    if trang_thai in {"da-duyet", "da-dang"} and not la_ngay(fm.get("ngay_duyet")):
        loi.append("bài đã duyệt / đã đăng phải có ngay_duyet dạng yyyy-mm-dd (bất biến 1)")
    if fm.get("anh_ai") not in {"co", "khong"}:
        loi.append("anh_ai phải là co / khong")
    elif fm.get("anh_ai") == "co" and fm.get("nhan_ai") != "co":
        loi.append("có ảnh AI thì phải nhan_ai: co (bất biến 3 — Luật Trí tuệ nhân tạo)")
    anh_khach = str(fm.get("anh_khach", "")).strip()
    if anh_khach != "khong" and not MA_DONG_Y.match(anh_khach):
        loi.append("anh_khach phải là khong hoặc mã đồng ý DY-<số> (bất biến 4)")
    return loi


def kiem_bai(goc: Path) -> list[str]:
    loi: list[str] = []
    for f in sorted(x for x in (goc / "bai").rglob("*") if x.is_file()):
        duong = f.relative_to(goc).as_posix()
        if f.name == "README.md":
            continue
        if f.suffix != ".md":
            loi.append(f"{duong}: bài phải là file .md")
            continue
        if f.parent.parent != goc / "bai" or not re.fullmatch(r"\d{4}-\d{2}", f.parent.name):
            loi.append(f"{duong}: bài phải nằm ở bai/<yyyy-mm>/<ten-bai>.md")
            continue
        fm = doc_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None:
            loi.append(f"{duong}: thiếu hoặc hỏng frontmatter (--- … ---), khuôn ở bai/README.md")
            continue
        loi.extend(f"{duong}: {y}" for y in loi_khuon_bai(fm))
    return loi


def kiem_skill(goc: Path) -> list[str]:
    loi: list[str] = []
    thu_muc = goc / ".claude" / "skills"
    for f in sorted(thu_muc.rglob("SKILL.md")):
        duong = f.relative_to(goc).as_posix()
        if f.parent.parent != thu_muc:
            loi.append(f"{duong}: skill lồng sâu — chỉ được `.claude/skills/<tên>/SKILL.md`")
            continue
        fm = doc_frontmatter(f.read_text(encoding="utf-8"))
        if fm is None:
            loi.append(f"{duong}: thiếu hoặc hỏng frontmatter (--- … ---)")
            continue
        ten, mo_ta = fm.get("name"), fm.get("description")
        if not isinstance(ten, str) or not TEN_HOP_LE.match(ten) or len(ten) > 64:
            loi.append(f"{duong}: name «{ten}» phải là chữ thường / số / gạch nối, ≤ 64 ký tự")
        elif ten != f.parent.name:
            loi.append(f"{duong}: name «{ten}» khác tên thư mục «{f.parent.name}»")
        if not isinstance(mo_ta, str) or not mo_ta.strip() or len(mo_ta) > 1024:
            loi.append(f"{duong}: description phải có chữ và ≤ 1024 ký tự")
    return loi


def do_long(nut: ast.AST, muc: int = 0) -> int:
    khoi = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith, ast.Try, ast.Match)
    sau = muc
    for con in ast.iter_child_nodes(nut):
        if isinstance(con, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        # `elif` là một If nằm một mình trong `orelse` của If trước — cùng tầng, không phải lồng thêm.
        la_elif = isinstance(nut, ast.If) and len(nut.orelse) == 1 and con is nut.orelse[0] and isinstance(con, ast.If)
        sau = max(sau, do_long(con, muc if la_elif or not isinstance(con, khoi) else muc + 1))
    return sau


def ten_day_du(cay: ast.AST) -> dict[int, str]:
    """dòng bắt đầu hàm → tên kèm lớp / hàm cha («Lop.run») để hai hàm cùng tên ở hai lớp không đè nhau."""
    ten: dict[int, str] = {}

    def di(nut: ast.AST, cha: str) -> None:
        for con in ast.iter_child_nodes(nut):
            if isinstance(con, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                day_du = f"{cha}.{con.name}" if cha else con.name
                if not isinstance(con, ast.ClassDef):
                    ten[con.lineno] = day_du
                di(con, day_du)
            else:
                di(con, cha)

    di(cay, "")
    return ten


def do_ham(van: str) -> list[tuple[str, int, int, int]]:
    """(tên đầy đủ, số dòng, lồng, McCabe) cho MỌI hàm."""
    cay = ast.parse(van)
    tham = mccabe.PathGraphingAstVisitor()
    tham.preorder(cay, tham)
    phuc_tap = {do_thi.lineno: do_thi.complexity() for do_thi in tham.graphs.values()}
    ten = ten_day_du(cay)
    ket_qua = []
    for nut in ast.walk(cay):
        if isinstance(nut, (ast.FunctionDef, ast.AsyncFunctionDef)):
            dong = (nut.end_lineno or nut.lineno) - nut.lineno + 1
            ket_qua.append((ten[nut.lineno], dong, do_long(nut), phuc_tap.get(nut.lineno, 1)))
    return ket_qua


def kiem_code_sach(goc: Path) -> list[str]:
    loi: list[str] = []
    for f in cac_file(goc):
        duong = f.relative_to(goc).as_posix()
        van = f.read_text(encoding="utf-8", errors="replace")
        so_dong = van.count("\n") + (0 if van.endswith("\n") or not van else 1)
        if so_dong > NO_CU.get(duong, MAX_DONG_FILE):
            loi.append(f"{duong}: {so_dong} dòng — vượt {NO_CU.get(duong, MAX_DONG_FILE)}")
        if f.suffix != ".py":
            continue
        for ten, dong, long, pt in do_ham(van):
            tran = NO_HAM_CU.get((duong, ten), (MAX_DONG_HAM, MAX_LONG, MAX_PHUC_TAP))
            if dong > tran[0] or long > tran[1] or pt > tran[2]:
                loi.append(f"{duong}: hàm {ten} {dong} dòng · lồng {long} · McCabe {pt} — vượt ngưỡng {tran}")
    return loi


def la_so_tien(phan: str) -> bool:
    """Số chấm hàng nghìn là tiền khi không mở đầu bằng 0 và ≤ 10 chữ số (dưới 10 tỷ). Điện thoại, CCCD chấm theo nhóm ba
    (mở đầu bằng 0) và điện thoại có mã nước (11 chữ số) viết giống tiền nhưng là số cá nhân — ca thử ở tests/."""
    so = re.sub(r"\D", "", phan)
    return bool(SO_TIEN.match(phan)) and not so.startswith("0") and len(so) <= 10


def la_so_ca_nhan(cum: str) -> bool:
    khuc = re.findall(r"\d+", cum)
    if sum(map(len, khuc)) < 9 or all(la_so_tien(phan) for phan in cum.split()):
        return False  # các khoản tiền đứng cạnh nhau («15.000.000 12.500.000») không phải một số
    return len(khuc) == 1 or min(map(len, khuc)) >= 2


def kiem_du_lieu_ca_nhan(goc: Path) -> list[str]:
    loi: list[str] = []
    for f in cac_file(goc):
        duong = f.relative_to(goc).as_posix()
        if duong.startswith(("tests/", ".github/")):
            continue  # tests/: số giả để thử máy canh; .github/: SHA ghim action
        van = f.read_text(encoding="utf-8", errors="replace")
        so = sum(1 for m in SO_DAI.finditer(NGAY_ISO.sub(" ", van)) if la_so_ca_nhan(m.group()))
        if so > NO_SO_CU.get(duong, 0):
            loi.append(f"{duong}: {so} dãy ≥ 9 chữ số (điện thoại / tài khoản / CCCD?) — bỏ đi hoặc thay số giả")
        mail = sorted({m.group(0) for m in EMAIL.finditer(van) if m.group(1).lower() not in MIEN_EMAIL_DUOC})
        if mail:
            loi.append(f"{duong}: {len(mail)} địa chỉ email ngoài {sorted(MIEN_EMAIL_DUOC)} — dữ liệu cá nhân không vào repo")
    return loi


def kiem(goc: Path) -> list[str]:
    return kiem_anh(goc) + kiem_bai(goc) + kiem_skill(goc) + kiem_code_sach(goc) + kiem_du_lieu_ca_nhan(goc)


def main() -> int:
    loi = kiem(GOC)
    for dong in loi:
        print(f"✗ {dong}")
    print(f"{'✗' if loi else '✓'} kiem_kho: {len(loi)} lỗi")
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
