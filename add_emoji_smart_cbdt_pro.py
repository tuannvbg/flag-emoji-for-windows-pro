#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
add_emoji_smart_cbdt_pro.py (v3 — Full 262 Flags + Full U17 & U18 Sequences)
=============================================================================
Smart CBDT patcher cho Windows Segoe CBDT & Mobile:
- Tự động lấy đủ 262 cờ (258 Quốc kỳ + 4 Cờ tiểu vùng: England, Scotland, Wales, Texas)
- Tự động quét & cấy FULL Unicode 17.0 (7 đơn + 156 chuỗi ZWJ/màu da: Ballet Dancer, Bunny Ears, Wrestling...)
- Tự động quét & cấy FULL Unicode 18.0 (9 đơn + toàn bộ biến thể màu da ngón cái trái/phải)
- Tự động resize bitmap về đúng ppem của font gốc & nén pngquant

Cách chạy:
    python add_emoji_smart_cbdt_pro4.py seguiemj_3d_pro3.ttf NotoColorEmoji.ttf Twemoji.Mozilla_cbdt3a.ttf seguiemj_3d_pro3_final.ttf
    final python: 
    1. python colr2cbdt_3d_skia_v4.py seguiemj.ttf seguiemj_3d_pro3.ttf (Xuất chuẩn màu vàng 3D tròn trịa, không cắt viền).
    2. python add_emoji_smart_cbdt_pro5.py seguiemj_3d_pro6.ttf NotoColorEmoji.ttf Twemoji.Mozilla_cbdt3b.ttf seguiemj_3d_pro6_final5.ttf
    3. python merge_emoji_into_honor_font_pro.py template.hwt seguiemj_3d_pro3_final.ttf Win11_3D_Pro2_Honor.hwt
note: 2026-11-22 11h59: fix cờ bằng nhau hết
""" 
# ============================================================================
# add_emoji_smart_cbdt_pro4.py (Phần 1/5)
# [EN] Interactive Multi-Language Smart CBDT Patcher (262 Flags + Full U17/U18)
# [VI] Công cụ cấy 262 cờ & Full Unicode 17.0/18.0 đa ngôn ngữ (Anh/Việt/Trung/Nga)
# [ZH] 多语言交互式智能 CBDT 补丁工具 (262国旗 + 完整 Unicode 17.0/18.0)
# [RU] Интерактивный мультиязычный патчер CBDT (262 флага + полный Unicode 17/18)
# ============================================================================

import sys
import io
import os
import time
import shutil
import sysconfig
import argparse
import subprocess
import urllib.request
import zipfile
import importlib.util
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

# [EN] Force UTF-8 console output on Windows CMD/PowerShell
# [VI] Ép chuẩn xuất UTF-8 trên Windows CMD/PowerShell để hiển thị cờ & tiếng Việt có dấu
# [ZH] 强制 Windows 终端使用 UTF-8 编码输出
# [RU] Принудительный вывод UTF-8 в консоли Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# [EN] Auto-install missing Python packages
# [VI] Tự động cài đặt các thư viện Python còn thiếu
# [ZH] 自动检查并安装缺失的 Python 依赖库
# [RU] Автоматическая установка недостающих библиотек Python
def ensure_packages():
    required = {"fontTools": "fonttools", "PIL": "pillow"}
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"[*] Đang cài đặt thư viện thiếu / Installing packages: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])


ensure_packages()

from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import C_B_D_T_, otTables
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.E_B_L_C_ import eblc_index_sub_table_1

# [EN] Unicode 17.0 & 18.0 codepoints and 262 Flag definitions
# [VI] Danh sách mã Unicode 17.0 & 18.0 và định nghĩa 262 lá cờ
# [ZH] Unicode 17.0 & 18.0 码位及 262 面国旗定义
# [RU] Коды Unicode 17.0 и 18.0 и определения 262 флагов
U17_BASE = [0x1FAEA, 0x1FAEF, 0x1FAC8, 0x1FACD, 0x1F6D8, 0x1FA8A, 0x1FA8E]
U18_BASE = [0x1FAEB, 0x1FAF9, 0x1FAFA, 0x1FACC, 0x1FADD, 0x1F6D9, 0x1FA8B, 0x1FA8C, 0x1FA8D]
#U17_U18_SEQ_TRIGGERS = {0x1FA70, 0x1F46F, 0x1F93C, 0x1FAF9, 0x1FAFA}
#U17_U18_SEQ_TRIGGERS = {0x1FA70, 0x1F46F, 0x1F93C, 0x1FAF9, 0x1FAFA, 0x1F91D}
U17_U18_SEQ_TRIGGERS = {0x1FA70, 0x1F46F, 0x1F93C, 0x1FAEF, 0x1FAF9, 0x1FAFA, 0x1F91D}
RI_CP = list(range(0x1F1E6, 0x1F200))

SUBDIVISION_FLAGS = {
    "England":  [0x1F3F4, 0xE0067, 0xE0062, 0xE0065, 0xE006E, 0xE0067, 0xE007F],
    "Scotland": [0x1F3F4, 0xE0067, 0xE0062, 0xE0073, 0xE0063, 0xE0074, 0xE007F],
    "Wales":    [0x1F3F4, 0xE0067, 0xE0062, 0xE0077, 0xE006C, 0xE0073, 0xE007F],
    "Texas":    [0x1F3F4, 0xE0075, 0xE0073, 0xE0074, 0xE0078, 0xE007F],
}

PNGQUANT_WIN_URL = "https://pngquant.org"

LANG_PACK = {
    "en": {
        "label": "🇺🇸 English",
        "banner": "SMART CBDT PATCHER PRO v4 — 262 FLAGS + FULL UNICODE 17.0 & 18.0",
        "help_title": "TOOL OVERVIEW & USAGE:",
        "help_lines": [
            "1. Injects all 262 country & subdivision flags from Twemoji into your base CBDT font.",
            "2. Auto-scans & merges full Unicode 17.0 & 18.0 emojis (including ZWJ & skin tones) from Noto.",
            "3. Resizes bitmaps to match base ppem (109px) and compresses via pngquant / FASTOCTREE.",
            "4. CLI mode: python add_emoji_smart_cbdt_pro4.py <base.ttf> <noto.ttf> <twemoji.ttf> [out.ttf]",
        ],
        "prompt_base": "Enter base font path (Enter for '{default}'): ",
        "prompt_noto": "Enter NotoColorEmoji CBDT path (Enter for '{default}'): ",
        "prompt_tw": "Enter Twemoji CBDT path (Enter for '{default}'): ",
        "prompt_out": "Enter output font path (Enter for '{default}'): ",
        "err_missing": "[ERROR] File not found: {path}",
        "err_tables": "[ERROR] Base font must contain CBDT, CBLC and GSUB tables!",
        "chk_header": "FEATURE DETECTION ON BASE FONT:",
        "chk_u17": "  Unicode 17.0 : {status}",
        "chk_u18": "  Unicode 18.0 : {status}",
        "chk_flg": "  262 Flags    : {status}",
        "st_ok": "Already present (Skipped)",
        "st_add": "Missing -> Will inject",
        "all_done_skip": "[INFO] All requested emojis and 262 flags are already in the font!",
        "step_u1718": "[*] Injecting Unicode 17.0/18.0 single emojis & {seq} ZWJ/skin-tone sequences...",
        "step_flags": "[*] Injecting {nat} country flags & {sub} subdivision flags...",
        "step_bmp": "[*] Resizing & compressing {count} bitmaps in parallel...",
        "done_msg": "[SUCCESS] Done in {sec:.2f}s! Glyphs: {glyphs}/65535 | Saved: {path} ({mb:.2f} MB)",
        "next_action": "\nNext step:\n  (1) Return to main menu\n  (0) Exit program\nYour choice (1/0): ",
        "bye": "Goodbye! Happy font building!",
    },
    "vi": {
        "label": "🇻🇳 Tiếng Việt (Vietnamese)",
        "banner": "SMART CBDT PATCHER PRO v4 — CẤY 262 CỜ + FULL UNICODE 17.0 & 18.0",
        "help_title": "GIỚI THIỆU CÔNG DỤNG & CÁCH DÙNG:",
        "help_lines": [
            "1. Cấy đủ 262 quốc kỳ & cờ tiểu vùng từ Twemoji vào font nền (hết lỗi chữ cái VN, US...).",
            "2. Tự động quét & vá trọn bộ Unicode 17.0 & 18.0 (gồm chuỗi ZWJ & màu da) từ Noto CBDT.",
            "3. Tự căn chỉnh kích thước bitmap về đúng chuẩn ppem gốc (109px) và nén siêu nhẹ.",
            "4. Hỗ trợ chạy dòng lệnh (CLI): python add_emoji_smart_cbdt_pro4.py <nền.ttf> <noto.ttf> <twemoji.ttf> [đích.ttf]",
        ],
        "prompt_base": "Nhập tên/đường dẫn font nền (Enter để dùng '{default}'): ",
        "prompt_noto": "Nhập đường dẫn font NotoColorEmoji CBDT (Enter để dùng '{default}'): ",
        "prompt_tw": "Nhập đường dẫn font Twemoji CBDT (Enter để dùng '{default}'): ",
        "prompt_out": "Nhập tên/đường dẫn font đích (Enter để dùng '{default}'): ",
        "err_missing": "[LỖI] Không tìm thấy file: {path}",
        "err_tables": "[LỖI] Font nền bắt buộc phải có các bảng CBDT, CBLC và GSUB!",
        "chk_header": "KIỂM TRA TÍNH NĂNG HIỆN CÓ TRÊN FONT NỀN:",
        "chk_u17": "  Unicode 17.0 : {status}",
        "chk_u18": "  Unicode 18.0 : {status}",
        "chk_flg": "  Full 262 Cờ  : {status}",
        "st_ok": "Đã có sẵn (Bỏ qua)",
        "st_add": "Chưa có -> Sẽ cấy mới",
        "all_done_skip": "[THÔNG BÁO] Font của bạn đã có đầy đủ U17, U18 và 262 cờ rồi!",
        "step_u1718": "[*] Đang cấy emoji đơn U17/U18 & {seq} chuỗi tổ hợp ZWJ/màu da...",
        "step_flags": "[*] Đang cấy {nat} quốc kỳ & {sub} cờ tiểu vùng...",
        "step_bmp": "[*] Đang căn chỉnh & nén đa luồng {count} ảnh bitmap...",
        "done_msg": "[THÀNH CÔNG] Xong trong {sec:.2f}s! Tổng glyph: {glyphs}/65535 | Đã lưu: {path} ({mb:.2f} MB)",
        "next_action": "\nBạn muốn làm gì tiếp theo?\n  (1) Quay lại menu chính\n  (0) Thoát chương trình\nLựa chọn của bạn (1/0): ",
        "bye": "Tạm biệt! Chúc bạn build font thành công!",
    },
    "zh": {
        "label": "🇨🇳 中文 (Chinese)",
        "banner": "SMART CBDT PATCHER PRO v4 — 262 面国旗 + 完整 UNICODE 17.0 & 18.0",
        "help_title": "工具功能与使用说明：",
        "help_lines": [
            "1. 从 Twemoji 注入全部 262 面国家/地区旗帜（彻底修复 VN、US 等双字母显示问题）。",
            "2. 自动扫描并合并 Noto 中的完整 Unicode 17.0 & 18.0 表情（含 ZWJ 与肤色变体）。",
            "3. 自动将位图缩放至目标 ppem (109px) 并通过 pngquant / FASTOCTREE 多线程压缩。",
            "4. 命令行模式 (CLI): python add_emoji_smart_cbdt_pro4.py <基础.ttf> <noto.ttf> <twemoji.ttf> [输出.ttf]",
        ],
        "prompt_base": "请输入基础字体路径 (直接按回车使用 '{default}'): ",
        "prompt_noto": "请输入 NotoColorEmoji CBDT 路径 (回车使用 '{default}'): ",
        "prompt_tw": "请输入 Twemoji CBDT 路径 (回车使用 '{default}'): ",
        "prompt_out": "请输入输出字体路径 (回车使用 '{default}'): ",
        "err_missing": "[错误] 找不到文件: {path}",
        "err_tables": "[错误] 基础字体必须包含 CBDT、CBLC 和 GSUB 表！",
        "chk_header": "基础字体功能检测：",
        "chk_u17": "  Unicode 17.0 : {status}",
        "chk_u18": "  Unicode 18.0 : {status}",
        "chk_flg": "  完整 262 国旗: {status}",
        "st_ok": "已存在（跳过）",
        "st_add": "缺失 -> 准备注入",
        "all_done_skip": "[提示] 您的字体已包含全部 U17、U18 表情和 262 面国旗！",
        "step_u1718": "[*] 正在注入 U17/U18 单体表情及 {seq} 个 ZWJ/肤色组合序列...",
        "step_flags": "[*] 正在注入 {nat} 面国家旗帜与 {sub} 面地区旗帜...",
        "step_bmp": "[*] 正在多线程缩放并压缩 {count} 张位图...",
        "done_msg": "[成功] 耗时 {sec:.2f} 秒完成！字形总数: {glyphs}/65535 | 已保存: {path} ({mb:.2f} MB)",
        "next_action": "\n接下来您想做什么？\n  (1) 返回主菜单继续操作\n  (0) 退出程序\n请输入选项 (1/0): ",
        "bye": "再见！祝您使用愉快！",
    },
    "ru": {
        "label": "🇷🇺 Русский (Russian)",
        "banner": "SMART CBDT PATCHER PRO v4 — 262 ФЛАГА + ПОЛНЫЙ UNICODE 17.0 & 18.0",
        "help_title": "ОПИСАНИЕ И СПОСОБЫ ЗАПУСКА:",
        "help_lines": [
            "1. Внедряет все 262 флага стран и регионов из Twemoji (вместо буквенных кодов VN, US).",
            "2. Автоматически добавляет полный набор Unicode 17.0 и 18.0 (включая ZWJ и оттенки кожи).",
            "3. Масштабирует битмапы под ppem (109px) и сжимает через pngquant / FASTOCTREE.",
            "4. Режим CLI: python add_emoji_smart_cbdt_pro4.py <база.ttf> <noto.ttf> <twemoji.ttf> [выход.ttf]",
        ],
        "prompt_base": "Введите путь к базовому шрифту (Enter для '{default}'): ",
        "prompt_noto": "Введите путь к NotoColorEmoji CBDT (Enter для '{default}'): ",
        "prompt_tw": "Введите путь к Twemoji CBDT (Enter для '{default}'): ",
        "prompt_out": "Введите имя выходного шрифта (Enter для '{default}'): ",
        "err_missing": "[ОШИБКА] Файл не найден: {path}",
        "err_tables": "[ОШИБКА] Базовый шрифт должен содержать таблицы CBDT, CBLC и GSUB!",
        "chk_header": "ПРОВЕРКА ПОДДЕРЖКИ В БАЗОВОМ ШРИФТЕ:",
        "chk_u17": "  Unicode 17.0 : {status}",
        "chk_u18": "  Unicode 18.0 : {status}",
        "chk_flg": "  Все 262 флага: {status}",
        "st_ok": "Уже есть (Пропуск)",
        "st_add": "Отсутствует -> Будет добавлено",
        "all_done_skip": "[ИНФО] Шрифт уже содержит все эмодзи U17/U18 и 262 флага!",
        "step_u1718": "[*] Внедрение одиночных U17/U18 и {seq} последовательностей ZWJ/оттенков кожи...",
        "step_flags": "[*] Внедрение {nat} флагов стран и {sub} флагов регионов...",
        "step_bmp": "[*] Многопоточное сжатие и ресайз {count} битмапов...",
        "done_msg": "[ГОТОВО] Завершено за {sec:.2f} сек! Глифов: {glyphs}/65535 | Файл: {path} ({mb:.2f} МБ)",
        "next_action": "\nЧто вы хотите сделать дальше?\n  (1) Вернуться в главное меню\n  (0) Выйти из программы\nВаш выбор (1/0): ",
        "bye": "До свидания! Удачи в сборке шрифтов!",
    },
}


# [EN] Locate or auto-download pngquant (Windows / Linux / Termux)
# [VI] Tìm kiếm hoặc tự động tải pngquant (Windows / Linux / Termux)
# [ZH] 查找或自动下载 pngquant 压缩工具 (Windows / Linux / Termux)
# [RU] Поиск или автозагрузка pngquant (Windows / Linux / Termux)
def ensure_pngquant_binary():
    sys_bin = shutil.which("pngquant")
    if sys_bin:
        return sys_bin

    if "com.termux" in os.environ.get("PREFIX", ""):
        try:
            subprocess.run(["pkg", "install", "-y", "pngquant"], check=True)
            return shutil.which("pngquant")
        except Exception:
            pass

    scripts_dirs = []
    for scheme in (None, f"{os.name}_user"):
        d = sysconfig.get_path("scripts", scheme) if scheme else sysconfig.get_path("scripts")
        if d:
            scripts_dirs.append(d)

    for d in scripts_dirs:
        if os.path.isdir(d):
            for fname in ("pngquant.exe", "pngquant"):
                cand = os.path.join(d, fname)
                if os.path.isfile(cand):
                    return cand

    if os.name == "nt" and scripts_dirs:
        tdir = next(iter(scripts_dirs))
        os.makedirs(tdir, exist_ok=True)
        texe = os.path.join(tdir, "pngquant.exe")
        try:
            req = urllib.request.Request(PNGQUANT_WIN_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                zdata = r.read()
            with zipfile.ZipFile(io.BytesIO(zdata), "r") as zf:
                for m in zf.namelist():
                    if m.lower().endswith("pngquant.exe"):
                        with open(texe, "wb") as f:
                            f.write(zf.read(m))
                        return texe
        except Exception:
            pass
    return None


PNGQUANT_BIN = ensure_pngquant_binary()


# [EN] Compress RGBA PNG with pngquant or Pillow FASTOCTREE fallback
# [VI] Nén ảnh PNG RGBA bằng pngquant hoặc dự phòng Pillow FASTOCTREE trên di động
# [ZH] 使用 pngquant 或 Pillow FASTOCTREE 压缩 RGBA PNG 图像
# [RU] Сжатие PNG RGBA через pngquant или резервный Pillow FASTOCTREE
def compress_png(raw_bytes, quality=90):
    if PNGQUANT_BIN:
        q_min = max(40, quality - 15)
        try:
            proc = subprocess.run(
                [PNGQUANT_BIN, "--quality", f"{q_min}-{quality}", "--speed", "1", "-"],
                input=raw_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            if proc.stdout:
                return proc.stdout
        except Exception:
            pass

    try:
        im = Image.open(io.BytesIO(raw_bytes)).convert("RGBA")
        quantized = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
        out = io.BytesIO()
        quantized.save(out, format="PNG", optimize=True)
        compressed = out.getvalue()
        return compressed if len(compressed) < len(raw_bytes) else raw_bytes
    except Exception:
        return raw_bytes

# [EN] Helper utilities for glyph naming, cmap, metrics, and bitmap resizing
# [VI] Các hàm tiện ích quản lý tên glyph, cmap, metrics và căn chỉnh kích thước bitmap
# [ZH] 字形命名、cmap、度量及位图缩放辅助函数
# [RU] Вспомогательные функции для имен глифов, cmap, метрик и масштабирования битмапов
def ensure_unique(name, existing, prefix="cb_"):
    if name not in existing:
        return name
    cand = prefix + name
    counter = 1
    while cand in existing:
        cand = f"{prefix}{name}_{counter}"
        counter += 1
    return cand


def has_cbdt(font):
    return "CBDT" in font and "CBLC" in font


def add_to_cmap(dst, codepoint, glyph_name):
    for table in dst["cmap"].tables:
        if not table.isUnicode():
            continue
        if table.format == 4 and codepoint > 0xFFFF:
            continue
        if table.format in (4, 12):
            table.cmap[codepoint] = glyph_name

# [EN] Read XAdvance spacing compensation from Windows 11 GPOS table (if present)
# [VI] Đọc mức bù trừ khoảng cách XAdvance trong bảng GPOS của Windows 11 (nếu có)
# [ZH] 读取 Windows 11 GPOS 表中的 XAdvance 字距补偿值（如果存在）
# [RU] Чтение компенсации интервала XAdvance из таблицы GPOS Windows 11 (при наличии)
def get_gpos_xadvance_delta(font, target_gname):
    if "GPOS" not in font or not font["GPOS"].table.LookupList:
        return 0
    delta = 0
    for lookup in font["GPOS"].table.LookupList.Lookup:
        subs = [getattr(s, "ExtSubTable", s) for s in lookup.SubTable] if lookup.LookupType == 9 else lookup.SubTable
        for st in subs:
            cov = getattr(st, "Coverage", None)
            glyphs = getattr(cov, "glyphs", None) or []
            if target_gname not in glyphs:
                continue
            fmt = getattr(st, "Format", None)
            if fmt == 1:
                val = getattr(st, "Value", None)
                if val and hasattr(val, "XAdvance"):
                    delta += int(val.XAdvance)
            elif fmt == 2 and hasattr(st, "Value"):
                idx = glyphs.index(target_gname)
                if idx < len(st.Value) and hasattr(st.Value[idx], "XAdvance"):
                    delta += int(st.Value[idx].XAdvance)
    return delta


def measure_segoe_advance(dst):
    cmap = dst.getBestCmap() or {}
    hmtx = dst["hmtx"].metrics

    # Tính độ rộng thực tế (hmtx + bù trừ GPOS) của emoji 3D gốc trên Windows 11
    effective_widths = []
    for cp in list(U17_BASE) + [0x1F600, 0x1F602, 0x1F60E]:
        gname = cmap.get(cp)
        if gname and gname in hmtx:
            w, _ = hmtx[gname]
            if w > 0:
                real_w = int(w) + get_gpos_xadvance_delta(dst, gname)
                if real_w > 0:
                    effective_widths.append(real_w)

    if effective_widths:
        val, _ = next(iter(Counter(effective_widths).most_common(1)))
        return int(val)
    return int(dst["head"].unitsPerEm)

def reference_bitmap_metrics(font, strike_index):
    cmap = font.getBestCmap() or {}
    sd_list = getattr(font["CBDT"], "strikeData", None)
    if sd_list and strike_index < len(sd_list):
        strike_data = sd_list[strike_index]
        probe_list = list(U17_BASE) + [0x1F600, 0x1F602, 0x1F44D]
        for cp in probe_list:
            gname = cmap.get(cp)
            if gname and gname in strike_data:
                m = getattr(strike_data[gname], "metrics", None)
                if m and hasattr(m, "Advance") and hasattr(m, "BearingY"):
                    return int(m.Advance), int(m.BearingX), int(m.BearingY)
    ppem = font["CBLC"].strikes[strike_index].bitmapSizeTable.ppemY
    return ppem, 0, int(round(ppem * 0.85))


def pick_best_donor_strike(src, target_ppem):
    best_idx = 0
    best_score = -100000
    for i, strike in enumerate(src["CBLC"].strikes):
        ppem = strike.bitmapSizeTable.ppemY or strike.bitmapSizeTable.ppemX
        if ppem == target_ppem:
            return i
        score = ppem if ppem > target_ppem else ppem - 1000
        if score > best_score:
            best_score = score
            best_idx = i
    return best_idx


def build_resized_cbdt_glyph(dst, src_bitmap, target_ppem, source_ppem, ref_bx, ref_by, px_advance, is_flag=False):
    raw_png = getattr(src_bitmap, "imageData", None)
    if not raw_png:
        return None

    img = Image.open(io.BytesIO(raw_png)).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)

    orig_w, orig_h = img.size
    if is_flag:
        # Khóa chiều cao tối đa 0.70 * ppem (~76px) & chiều rộng tối đa 0.92 * ppem (~100px)
        # Giúp cờ Bỉ 🇧🇪, Thụy Sĩ 🇨🇭, Vatican 🇻🇦 bằng phẳng tuyệt đối với mọi quốc kỳ chữ nhật
        max_w = max(1, int(round(target_ppem * 0.92)))
        max_h = max(1, int(round(target_ppem * 0.70)))
        scale = min(max_w / float(orig_w), max_h / float(orig_h))
        new_w = max(1, min(255, int(round(orig_w * scale))))
        new_h = max(1, min(255, int(round(orig_h * scale))))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        bx = max(-128, min(127, (px_advance - new_w) // 2))
        # Căn giữa theo trục dọc so với các lá cờ chữ nhật
        by = max(-128, min(127, (ref_by - int(round(target_ppem * 0.10))) - (max_h - new_h) // 2))
    else:
        target_box = max(1, int(round(target_ppem * 0.90)))
        scale = target_box / float(max(orig_w, orig_h))
        new_w = max(1, min(255, int(round(orig_w * scale))))
        new_h = max(1, min(255, int(round(orig_h * scale))))
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        bx = max(-128, min(127, (px_advance - new_w) // 2))
        by = max(-128, min(127, ref_by - 2))

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    png_bytes = compress_png(buf.getvalue())

    glyph = C_B_D_T_.cbdt_bitmap_format_17(data=b"", ttFont=dst)
    glyph.metrics = C_B_D_T_.SmallGlyphMetrics()
    glyph.metrics.height = new_h
    glyph.metrics.width = new_w
    glyph.metrics.BearingX = bx
    glyph.metrics.BearingY = by
    glyph.metrics.Advance = max(1, min(255, px_advance))
    glyph.imageData = png_bytes
    return glyph



def group_consecutive(items):
    if not items:
        return []
    groups = []
    it = iter(items)
    curr = list((next(it),))
    for item in it:
        gid, _ = item
        prev_gid, _ = curr[-1]
        if gid == prev_gid + 1:
            curr.append(item)
        else:
            groups.append(curr)
            curr = list((item,))
    groups.append(curr)
    return groups

# [EN] GSUB Ligature extraction, detection, and priority injection
# [VI] Trích xuất, kiểm tra và tiêm quy tắc GSUB ưu tiên chuỗi dài
# [ZH] GSUB 连字规则提取、检测及长序列优先注入
# [RU] Извлечение, проверка и приоритетная инъекция правил лигатур GSUB
def extract_all_ligatures(font):
    rules = []
    if "GSUB" not in font or not font["GSUB"].table.LookupList:
        return rules
    for lookup in font["GSUB"].table.LookupList.Lookup:
        subs = list(lookup.SubTable)
        if lookup.LookupType == 7:
            subs = [getattr(st, "ExtSubTable", st) for st in subs]
        for st in subs:
            ligs = getattr(st, "ligatures", None)
            if not ligs:
                continue
            for first, lst in ligs.items():
                for lig in lst:
                    rules.append((first, list(lig.Component), lig.LigGlyph))
    return rules


def has_u17(cmap):
    return sum(1 for cp in U17_BASE if cp in cmap) >= 5


def has_u18(cmap):
    return sum(1 for cp in U18_BASE if cp in cmap) >= 5


def count_flag_ligatures(font):
    ri_names = {f"u{c:04X}" for c in RI_CP} | {f"u{c:04x}" for c in RI_CP}
    count = 0
    for first, comps, _ in extract_all_ligatures(font):
        if first in ri_names and len(comps) == 1 and next(iter(comps)) in ri_names:
            count += 1
    return count


def has_flags(font):
    return count_flag_ligatures(font) >= 100


def find_twemoji_flag_ligatures(src):
    src_cmap = src.getBestCmap() or {}
    ri_names = {src_cmap[c] for c in RI_CP if c in src_cmap}
    results = []
    for first, comps, lig in extract_all_ligatures(src):
        if first in ri_names and len(comps) == 1 and next(iter(comps)) in ri_names:
            results.append((first, comps, lig))
    return results


def find_ligature_for_sequence(font, seq_gnames):
    if len(seq_gnames) < 2:
        return None
    first = next(iter(seq_gnames))
    rest = seq_gnames[1:]
    for f, comps, lig in extract_all_ligatures(font):
        if f == first and comps == rest:
            return lig
    return None


def inject_into_segoe_ccmp_liga(dst, rules, prepend_lookup=False):
    if not rules or "GSUB" not in dst:
        return
    gsub = dst["GSUB"].table

    def _rule_len(r):
        _, comps_list, _ = r
        return len(comps_list)

    rules.sort(key=_rule_len, reverse=True)

    if prepend_lookup:
        lig_subst = otTables.LigatureSubst()
        lig_subst.ligatures = {}
        for first, comps, lig in rules:
            ligature = otTables.Ligature()
            ligature.Component = comps
            ligature.CompCount = len(comps) + 1
            ligature.LigGlyph = lig
            lig_subst.ligatures.setdefault(first, []).append(ligature)

        lookup = otTables.Lookup()
        lookup.LookupType = 4
        lookup.LookupFlag = 0
        lookup.SubTable = list((lig_subst,))
        lookup.SubTableCount = 1

        if gsub.LookupList is None:
            gsub.LookupList = otTables.LookupList()
            gsub.LookupList.Lookup = []
        gsub.LookupList.Lookup.append(lookup)
        new_idx = len(gsub.LookupList.Lookup) - 1
        gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)

        for fr in gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag in ("ccmp", "liga", "rlig"):
                fr.Feature.LookupListIndex.insert(0, new_idx)
                fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)
        return

    target_subst, target_lookup_idx = None, None
    if gsub.FeatureList:
        for fr in gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag != "ccmp":
                continue
            for lookup_idx in fr.Feature.LookupListIndex:
                lookup = gsub.LookupList.Lookup[lookup_idx]
                subs = lookup.SubTable
                if lookup.LookupType == 7:
                    subs = [getattr(st, "ExtSubTable", st) for st in subs]
                for st in subs:
                    if getattr(st, "ligatures", None) is None:
                        continue
                    if target_subst is None or len(st.ligatures) > len(target_subst.ligatures):
                        target_subst, target_lookup_idx = st, lookup_idx

    if target_subst is None:
        inject_into_segoe_ccmp_liga(dst, rules, prepend_lookup=True)
        return

    for first, comps, lig in rules:
        ligature = otTables.Ligature()
        ligature.Component = comps
        ligature.CompCount = len(comps) + 1
        ligature.LigGlyph = lig
        bucket = target_subst.ligatures.setdefault(first, [])
        if any(list(x.Component) == comps for x in bucket):
            continue
        bucket.append(ligature)

# [EN] Main patching function (U17/U18 + 262 Flags + Multi-threaded CBDT resizing)
# [VI] Hàm ghép emoji chính (U17/U18 + 262 cờ + Căn chỉnh & nén đa luồng CBDT)
# [ZH] 核心补丁主函数 (U17/U18 + 262国旗 + 多线程 CBDT 位图缩放与压缩)
# [RU] Основная функция патчинга (U17/U18 + 262 флага + многопоточный CBDT)
def patch_emoji_font(base_path, noto_path, tw_path, out_path, lang="en"):
    t0 = time.time()
    txt = LANG_PACK.get(lang, LANG_PACK["en"])

    for p in (base_path, noto_path, tw_path):
        if not os.path.isfile(p):
            raise FileNotFoundError(txt["err_missing"].format(path=p))

    dst = TTFont(base_path, lazy=False)
    dst.ensureDecompiled()
    if not has_cbdt(dst) or "GSUB" not in dst:
        dst.close()
        raise ValueError(txt["err_tables"])

    dst_cmap = dict(dst.getBestCmap() or {})
    do_u17 = not has_u17(dst_cmap)
    do_u18 = not has_u18(dst_cmap)
    do_flags = not has_flags(dst)

    print("=" * 72)
    print(txt["chk_header"])
    print(txt["chk_u17"].format(status=txt["st_ok"] if not do_u17 else txt["st_add"]))
    print(txt["chk_u18"].format(status=txt["st_ok"] if not do_u18 else txt["st_add"]))
    print(txt["chk_flg"].format(status=txt["st_ok"] if not do_flags else txt["st_add"]))
    print("=" * 72)

    if not do_u17 and not do_u18 and not do_flags:
        print(txt["all_done_skip"])
        dst.close()
        return

    existing = set(dst.getGlyphOrder())
    order = list(dst.getGlyphOrder())
    target_adv = measure_segoe_advance(dst)
    upm = dst["head"].unitsPerEm
    glyf = dst["glyf"]
    hmtx = dst["hmtx"].metrics

    pending_bitmaps = []
    open_donors = []

    # Bảo vệ toàn bộ glyph đang dùng ở cmap, GSUB, CBDT và BaseGlyph của COLR
    protected_glyphs = {".notdef", ".null", "nonmarkingreturn", "space"} | set(dst_cmap.values())
    for f_g, comps_g, lig_g in extract_all_ligatures(dst):
        protected_glyphs.add(f_g)
        protected_glyphs.add(lig_g)
        protected_glyphs.update(comps_g)
    if "COLR" in dst:
        ct = dst["COLR"].table
        if getattr(ct, "BaseGlyphList", None):
            for rec in ct.BaseGlyphList.BaseGlyphPaintRecord:
                protected_glyphs.add(rec.BaseGlyph)
        if getattr(ct, "BaseGlyphRecordArray", None):
            for rec in ct.BaseGlyphRecordArray.BaseGlyphRecord:
                protected_glyphs.add(rec.BaseGlyph)
    for sd in dst["CBDT"].strikeData:
        protected_glyphs.update(sd.keys())

    # Tận dụng các glyph mảnh ghép vector rời rạc của COLR (không bao giờ gọi trực tiếp)
    recyclable_slots = [gn for gn in order if gn not in protected_glyphs]

    def alloc_slot(src_f, src_gname, preferred):
        if len(order) >= 65515 and recyclable_slots:
            dg = recyclable_slots.pop()
            g = Glyph()
            g.numberOfContours = 0
            g.xMin = g.yMin = g.xMax = g.yMax = 0
            glyf[dg] = g
            hmtx[dg] = (target_adv, 0)
            pending_bitmaps.append((src_f, src_gname, dg))
            return dg

        dg = ensure_unique(preferred, existing, prefix="cb_")
        existing.add(dg)
        order.append(dg)
        g = Glyph()
        g.numberOfContours = 0
        g.xMin = g.yMin = g.xMax = g.yMax = 0
        glyf[dg] = g
        hmtx[dg] = (target_adv, 0)
        pending_bitmaps.append((src_f, src_gname, dg))
        return dg


    seq_added = flag_glyphs = subflag_added = 0

    if do_u17 or do_u18:
        noto = TTFont(noto_path, lazy=False)
        open_donors.append(noto)
        src_cmap = noto.getBestCmap() or {}
        noto_rev = {v: k for k, v in src_cmap.items()}

        base_list = (U17_BASE if do_u17 else []) + (U18_BASE if do_u18 else [])
        for cp in base_list:
            if cp not in src_cmap or cp in dst_cmap:
                continue
            dg = alloc_slot(noto, src_cmap[cp], f"u{cp:04X}")
            add_to_cmap(dst, cp, dg)
            dst_cmap[cp] = dg

        existing_dst_rules = {(f, tuple(c)) for f, c, _ in extract_all_ligatures(dst)}
        seq_rules = []
        allocated_lig_cache = {}

        for first_src, comps_src, lig_src in extract_all_ligatures(noto):
            full_src_seq = [first_src] + comps_src
            src_cps = [noto_rev.get(g) for g in full_src_seq]
            if any(cp is None for cp in src_cps):
                continue
            if not any(cp in U17_U18_SEQ_TRIGGERS for cp in src_cps):
                continue

            dst_seq = []
            valid_seq = True
            for cp, g_src in zip(src_cps, full_src_seq):
                if cp in dst_cmap:
                    dst_seq.append(dst_cmap[cp])
                elif cp in src_cmap:
                    new_comp = alloc_slot(noto, g_src, f"u{cp:04X}")
                    add_to_cmap(dst, cp, new_comp)
                    dst_cmap[cp] = new_comp
                    dst_seq.append(new_comp)
                else:
                    valid_seq = False
                    break

            if not valid_seq:
                continue

            d_first = next(iter(dst_seq))
            d_rest = dst_seq[1:]
            rule_key = (d_first, tuple(d_rest))
            if rule_key in existing_dst_rules:
                continue
            existing_dst_rules.add(rule_key)

            if lig_src not in allocated_lig_cache:
                allocated_lig_cache[lig_src] = alloc_slot(noto, lig_src, f"seq_{lig_src}")
            seq_rules.append((d_first, d_rest, allocated_lig_cache[lig_src]))
            seq_added += 1

        print(txt["step_u1718"].format(seq=seq_added))
        if seq_rules:
            inject_into_segoe_ccmp_liga(dst, seq_rules, prepend_lookup=True)

    if do_flags:
        tw = TTFont(tw_path, lazy=False)
        open_donors.append(tw)

        tw_flags = find_twemoji_flag_ligatures(tw)
        unique_flags = sorted({lig for _, _, lig in tw_flags})
        tw_cmap = tw.getBestCmap() or {}
        tw_name_to_cp = {tw_cmap[c]: c for c in RI_CP if c in tw_cmap}

        segoe_ri = {}
        for tw_name, cp in tw_name_to_cp.items():
            seg_name = dst_cmap.get(cp) or (f"u{cp:04X}" if f"u{cp:04X}" in existing else None)
            if seg_name:
                segoe_ri[tw_name] = seg_name

        lig_map = {src_flag: alloc_slot(tw, src_flag, f"flag_{src_flag}") for src_flag in unique_flags}
        rules = []
        for tw_a, tw_comps, tw_lig in tw_flags:
            a = segoe_ri.get(tw_a)
            b = segoe_ri.get(next(iter(tw_comps)))
            g = lig_map.get(tw_lig)
            if a and b and g:
                rules.append((a, [b], g))

        flag_glyphs = len(lig_map)
        if rules:
            inject_into_segoe_ccmp_liga(dst, rules)

        all_tag_cps = sorted({cp for seq in SUBDIVISION_FLAGS.values() for cp in seq})
        for cp in all_tag_cps:
            if cp not in dst_cmap:
                tag_name = ensure_unique(f"u{cp:05X}", existing, prefix="tag_")
                existing.add(tag_name)
                order.append(tag_name)
                g = Glyph()
                g.numberOfContours = 0
                g.xMin = g.yMin = g.xMax = g.yMax = 0
                glyf[tag_name] = g
                hmtx[tag_name] = (0, 0)
                add_to_cmap(dst, cp, tag_name)
                dst_cmap[cp] = tag_name

        sub_rules = []
        for label, seq in SUBDIVISION_FLAGS.items():
            tw_seq = [tw_cmap[c] for c in seq if c in tw_cmap]
            dst_seq = [dst_cmap[c] for c in seq if c in dst_cmap]
            if len(tw_seq) != len(seq) or len(dst_seq) != len(seq):
                continue
            src_sub_glyph = find_ligature_for_sequence(tw, tw_seq)
            if not src_sub_glyph:
                continue
            dst_sub_glyph = alloc_slot(tw, src_sub_glyph, f"subflag_{label.lower()}")
            sub_rules.append((next(iter(dst_seq)), dst_seq[1:], dst_sub_glyph))
            subflag_added += 1

        print(txt["step_flags"].format(nat=flag_glyphs, sub=subflag_added))
        if sub_rules:
            inject_into_segoe_ccmp_liga(dst, sub_rules, prepend_lookup=True)

    dst.setGlyphOrder(order)
    dst["maxp"].numGlyphs = len(order)
    if "hhea" in dst:
        dst["hhea"].numberOfHMetrics = len(order)
    reverse_gid = dst.getReverseGlyphMap(rebuild=True)

    print(txt["step_bmp"].format(count=len(pending_bitmaps)))
    for strike_idx, dest_strike in enumerate(dst["CBLC"].strikes):
        target_ppem = dest_strike.bitmapSizeTable.ppemY or dest_strike.bitmapSizeTable.ppemX
        dest_data = dst["CBDT"].strikeData[strike_idx]
        ref_adv, ref_bx, ref_by = reference_bitmap_metrics(dst, strike_idx)
        px_adv = max(1, min(255, ref_adv))
        exact_hmtx_w = int(round(px_adv * upm / float(target_ppem)))
        for _, _, d_gn in pending_bitmaps:
            hmtx[d_gn] = (exact_hmtx_w, 0)
        added_pairs = []


        def _bmp_worker(item):
            src_f, src_gname, dst_gname = item
            s_idx = pick_best_donor_strike(src_f, target_ppem)
            s_strike = src_f["CBLC"].strikes[s_idx]
            s_ppem = s_strike.bitmapSizeTable.ppemY or s_strike.bitmapSizeTable.ppemX
            s_bmp = src_f["CBDT"].strikeData[s_idx].get(src_gname)
            if s_bmp is None:
                return dst_gname, None
            flag_item = dst_gname.startswith(("flag_", "subflag_"))
            return dst_gname, build_resized_cbdt_glyph(dst, s_bmp, target_ppem, s_ppem, ref_bx, ref_by, px_adv, is_flag=flag_item)


        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            for dst_gname, resized_bmp in ex.map(_bmp_worker, pending_bitmaps):
                if resized_bmp is not None:
                    dest_data[dst_gname] = resized_bmp
                    added_pairs.append((reverse_gid[dst_gname], dst_gname))

        if added_pairs:
            added_pairs.sort()
            for group in group_consecutive(added_pairs):
                first_gid, _ = next(iter(group))
                last_gid, _ = group[-1]
                sub_table = eblc_index_sub_table_1(None, dst)
                sub_table.indexFormat = 1
                sub_table.imageFormat = 17
                sub_table.imageDataOffset = 0
                sub_table.names = [name for _, name in group]
                sub_table.firstGlyphIndex = first_gid
                sub_table.lastGlyphIndex = last_gid
                dest_strike.indexSubTables.append(sub_table)
                dest_strike.bitmapSizeTable.numberOfIndexSubTables = len(dest_strike.indexSubTables)

            all_first = [st.firstGlyphIndex for st in dest_strike.indexSubTables]
            all_last = [st.lastGlyphIndex for st in dest_strike.indexSubTables]
            if all_first and all_last:
                dest_strike.bitmapSizeTable.startGlyphIndex = min(all_first)
                dest_strike.bitmapSizeTable.endGlyphIndex = max(all_last)

    if "DSIG" in dst:
        del dst["DSIG"]

    dst.save(out_path)
    dst.close()
    for donor_font in open_donors:
        donor_font.close()

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print("=" * 72)
    print(txt["done_msg"].format(sec=time.time() - t0, glyphs=len(order), path=out_path, mb=size_mb))
    print("=" * 72)


# [EN] Interactive 4-language menu wizard | [VI] Menu tương tác 4 ngôn ngữ
# [ZH] 四语言交互式向导菜单             | [RU] Интерактивное меню на 4 языках
def run_interactive_wizard():
    lang_keys = ("en", "vi", "zh", "ru")
    while True:
        print("\n" + "=" * 72)
        print(" SELECT LANGUAGE / CHỌN NGÔN NGỮ / 选择语言 / ВЫБЕРИТЕ ЯЗЫК")
        print("=" * 72)
        for idx, k in enumerate(lang_keys, 1):
            print(f"  ({idx}) {LANG_PACK[k]['label']}")
        print("  (0) Exit / Thoát / 退出 / Выход")

        choice = input("\n👉 Choice (1-4, default=1): ").strip()
        if choice == "0":
            print(LANG_PACK["en"]["bye"])
            break

        lang_idx = int(choice) - 1 if choice in ("1", "2", "3", "4") else 0
        lang = lang_keys[lang_idx]
        txt = LANG_PACK[lang]

        print("\n" + "=" * 72)
        print(f" {txt['banner']}")
        print("=" * 72)
        print(f"💡 {txt['help_title']}")
        for line in txt["help_lines"]:
            print(f"   {line}")
        print("-" * 72)

        def_base = "seguiemj_3d_pro5.ttf"
        def_noto = "NotoColorEmoji.ttf"
        def_tw = "Twemoji.Mozilla.ttf"

        base_in = input(txt["prompt_base"].format(default=def_base)).strip().strip('"') or def_base
        noto_in = input(txt["prompt_noto"].format(default=def_noto)).strip().strip('"') or def_noto
        tw_in = input(txt["prompt_tw"].format(default=def_tw)).strip().strip('"') or def_tw

        stem_base, _ = os.path.splitext(base_in)
        def_out = f"{stem_base}_final.ttf"
        out_in = input(txt["prompt_out"].format(default=def_out)).strip().strip('"') or def_out

        print("-" * 72)
        try:
            patch_emoji_font(base_in, noto_in, tw_in, out_in, lang=lang)
        except Exception as exc:
            print(f"\n[FAILED] {type(exc).__name__}: {exc}")

        again = input(txt["next_action"]).strip()
        if again == "0":
            print(txt["bye"])
            break


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_interactive_wizard()
    else:
        parser = argparse.ArgumentParser(description="Smart CBDT Patcher Pro v4 (262 Flags + Full U17/U18)")
        parser.add_argument("base", help="Base CBDT font (e.g. seguiemj_3d_pro5.ttf)")
        parser.add_argument("noto", help="NotoColorEmoji CBDT font")
        parser.add_argument("twemoji", help="Twemoji CBDT font")
        parser.add_argument("output", nargs="?", help="Output TTF path")
        parser.add_argument("--lang", choices=["en", "vi", "zh", "ru"], default="en", help="UI language")
        args = parser.parse_args()

        stem_b, _ = os.path.splitext(args.base)
        out_file = args.output or f"{stem_b}_final.ttf"
        try:
            patch_emoji_font(args.base, args.noto, args.twemoji, out_file, lang=args.lang)
        except Exception as exc:
            print(f"\n[FAILED] {type(exc).__name__}: {exc}")
            sys.exit(1)

