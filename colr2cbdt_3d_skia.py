#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# colr2cbdt_3d_skia.py (Phần 1/4)
# [EN] Interactive Multi-Language (EN/VI/ZH/RU) COLRv1/v0 to CBDT Converter
# [VI] Công cụ chuyển đổi font COLRv1/v0 sang CBDT đa ngôn ngữ (Anh/Việt/Trung/Nga)
# [ZH] 多语言交互式 COLRv1/v0 转 CBDT/CBLC 彩色字体转换工具 (英/越/中/俄)
# [RU] Интерактивный мультиязычный конвертер COLRv1/v0 в CBDT/CBLC (EN/VI/ZH/RU)
# ============================================================================
# ============================================================================
# CLI ARGUMENTS / THAM SỐ DÒNG LỆNH / 命令行参数 / ПАРАМЕТРЫ КОМАНДНОЙ СТРОКИ:
#
# [EN] Usage: python colr2cbdt_3d_skia.py <input.ttf> <output.ttf> [options]
#   --mode {3d,2d}        : Render 3D COLRv1 (default) or flat 2D COLRv0
#   --ppem <1-255>        : Bitmap resolution in pixels (default: 109)
#   --quality <1-100>     : PNG compression quality (default: 90)
#   --strip-colr          : Strip COLR/CPAL tables (Full 3D on Win10 & smaller mobile size)
#   --lang {en,vi,zh,ru}  : Console log language (default: en)
#
# [VI] Cách dùng: python colr2cbdt_3d_skia.py <nguồn.ttf> <đích.ttf> [tùy chọn]
#   --mode {3d,2d}        : Xuất 3D COLRv1 (mặc định) hoặc 2D phẳng COLRv0
#   --ppem <1-255>        : Độ phân giải ảnh bitmap theo pixel (mặc định: 109)
#   --quality <1-100>     : Chất lượng nén ảnh PNG (mặc định: 90)
#   --strip-colr          : Xóa bảng COLR/CPAL (Hiện Full 3D trên Win10 & nhẹ hơn cho điện thoại)
#   --lang {en,vi,zh,ru}  : Ngôn ngữ hiển thị log (mặc định: en)
#
# [ZH] 用法: python colr2cbdt_3d_skia.py <输入.ttf> <输出.ttf> [选项]
#   --mode {3d,2d}        : 渲染 3D COLRv1 (默认) 或 2D 扁平 COLRv0
#   --ppem <1-255>        : 位图像素分辨率 (默认: 109)
#   --quality <1-100>     : PNG 压缩质量 (默认: 90)
#   --strip-colr          : 移除 COLR/CPAL 表 (使 Win10 显示完整 3D 并减小手机端体积)
#   --lang {en,vi,zh,ru}  : 终端日志语言 (默认: en)
#
# [RU] Использование: python colr2cbdt_3d_skia.py <вход.ttf> <выход.ttf> [опции]
#   --mode {3d,2d}        : Рендер 3D COLRv1 (по умолчанию) или плоского 2D COLRv0
#   --ppem <1-255>        : Разрешение битмапа в пикселях (по умолчанию: 109)
#   --quality <1-100>     : Качество сжатия PNG (по умолчанию: 90)
#   --strip-colr          : Удалить таблицы COLR/CPAL (полный 3D в Win10 и меньший вес)
#   --lang {en,vi,zh,ru}  : Язык логов в консоли (по умолчанию: en)
# ============================================================================

"""
colr2cbdt_3d_skia.py
========================
Render COLRv1 3D sang CBDT/CBLC + Fix VS16 Mobile

- Dùng Skia để render từng glyph COLRv1 ra ảnh bitmap chất lượng cao
- Giữ nguyên COLRv1/CPAL để Windows vẫn hiển thị 3D
- Tự động đồng bộ các biến thể VS16 (FE0F) vào cmap → sửa lỗi thiếu emoji trên di động
- Nén ảnh PNG bằng pngquant để giảm kích thước file
"""
"""

Chạy lại 3 bước để hoàn thiện siêu phẩm 3D:

    1. python colr2cbdt_3d_skia.py seguiemj.ttf seguiemj_3d.ttf (Xuất chuẩn màu vàng 3D tròn trịa, không cắt viền).
    2. python add_emoji_smart_cbdt.py seguiemj_3d.ttf NotoColorEmoji.ttf Twemoji.Mozilla_cbdt.ttf seguiemj_3d_final.ttf
    3. python merge_emoji_into_honor_font.py template.hwt seguiemj_3d_final.ttf Win11_3D_Honor.hwt
"""
import sys
import io
import os
import time
import shutil
import tempfile
import sysconfig
import argparse
import subprocess
import urllib.request
import zipfile
import importlib.util
from concurrent.futures import ThreadPoolExecutor

# [EN] Force UTF-8 console output on Windows CMD/PowerShell for flags & Unicode
# [VI] Ép chuẩn xuất UTF-8 trên Windows CMD/PowerShell để hiển thị cờ & tiếng Việt có dấu
# [ZH] 强制 Windows 终端使用 UTF-8 编码输出，确保国旗与多语言字符正常显示
# [RU] Принудительный вывод UTF-8 в консоли Windows для отображения флагов и символов
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


# [EN] Auto-install missing Python dependencies
# [VI] Tự động cài đặt các thư viện Python còn thiếu
# [ZH] 自动检查并安装缺失的 Python 依赖库
# [RU] Автоматическая установка недостающих библиотек Python
def ensure_packages():
    required = {
        "fontTools": "fonttools",
        "skia": "skia-python",
        "PIL": "pillow",
        "uharfbuzz": "uharfbuzz",
    }
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"[*] Đang cài đặt thư viện thiếu / Installing packages: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])



ensure_packages()

import skia
from PIL import Image
from fontTools import ttLib
from fontTools.ttLib.tables import C_B_D_T_, E_B_L_C_
import uharfbuzz as hb
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables._g_l_y_f import Glyph
MAX_BYTE = 255
MIN_SIGNED = -128
MAX_SIGNED = 127
PNGQUANT_WIN_URL = "https://pngquant.org"

# [EN] 4-Language UI & Help Dictionary | [VI] Từ điển giao diện & hướng dẫn 4 ngôn ngữ
# [ZH] 四语言界面与帮助说明字典       | [RU] Словарь интерфейса и справки на 4 языках
LANG_PACK = {
    "en": {
        "label": "🇺🇸 English",
        "banner": "COLR2CBDT PRO ENGINE v4 — INTERACTIVE WIZARD (3D & 2D)",
        "help_title": "TOOL OVERVIEW & USAGE:",
        "help_lines": [
            "1. Renders Windows 11 COLRv1 (3D) or COLRv0 (Flat 2D) vectors into crisp 109px bitmaps.",
            "2. Compresses PNGs via pngquant / FASTOCTREE to keep file size under 30 MB.",
            "3. Syncs VS16 (U+FE0F) variation sequences into cmap for full mobile & desktop compatibility.",
            "4. Also supports direct CLI mode: python colr2cbdt_3d_skia_v4.py <in.ttf> <out.ttf> [--mode 3d|2d]",
        ],
        "choose_mode": "Select render mode [1 = 3D (Default), 2 = Flat 2D]: ",
        "prompt_src": "Enter source font path (Press Enter for '{default}'): ",
        "prompt_dst": "Enter output font path (Press Enter for '{default}'): ",
        "err_not_found": "[ERROR] Source font not found: {path}",
        "err_no_colr": "[ERROR] Input font does not contain COLR/CPAL tables!",
        "step_2d": "[*] Extracting flat COLRv0 vector layer for 2D mode...",
        "info_in": "[*] Source Font : {path} (Mode: {mode})",
        "info_out": "[*] Output Font : {path}",
        "info_comp": "[*] Compression : {engine}",
        "info_total": "[*] Total Glyphs: {count} | Resolution: {ppem}x{ppem} px",
        "info_families": "[+] Rendered {count} native Win11 3D ZWJ family sequences via HarfBuzz+Skia into CBDT.",
        "prog_render": "    Rendering {mode} via Skia: {done}/{total} ({pct}%)",
        "prog_compress": "[*] Compressing {count} PNG bitmaps in parallel...",
        "info_vs16": "[+] Synced {count} VS16 (U+FE0F) variants to cmap (Mobile & Keyboard fix).",
        "done_msg": "[SUCCESS] Completed in {sec:.2f}s! Saved: {path} ({mb:.2f} MB)",
        "next_action": "\nWhat would you like to do next?\n  [1] Return to main menu (Convert another font)\n  [0] Exit program\nYour choice [1/0]: ",
        "bye": "Goodbye! Happy font building!",
    },
    "vi": {
        "label": "🇻🇳 Tiếng Việt (Vietnamese)",
        "banner": "COLR2CBDT PRO ENGINE v4 — TRÌNH CHUYỂN ĐỔI TƯƠNG TÁC (3D & 2D)",
        "help_title": "GIỚI THIỆU CÔNG DỤNG & CÁCH DÙNG:",
        "help_lines": [
            "1. Chuyển đổi emoji vector Windows 11 (3D COLRv1 hoặc 2D phẳng) sang bitmap 109px sắc nét.",
            "2. Nén ảnh đa luồng qua pngquant / FASTOCTREE giúp dung lượng nhẹ dưới 30 MB.",
            "3. Tự động đồng bộ biến thể VS16 (U+FE0F) vào cmap (sửa lỗi thiếu emoji trên điện thoại).",
            "4. Hỗ trợ chạy nhanh qua dòng lệnh (CLI): python colr2cbdt_3d_skia_v4.py <nguồn.ttf> <đích.ttf> [--mode 3d|2d]",
        ],
        "choose_mode": "Chọn chế độ xuất ảnh [1 = 3D (Mặc định), 2 = 2D phẳng]: ",
        "prompt_src": "Nhập tên/đường dẫn font nguồn (Nhấn Enter để dùng '{default}'): ",
        "prompt_dst": "Nhập tên/đường dẫn font đích (Nhấn Enter để dùng '{default}'): ",
        "err_not_found": "[LỖI] Không tìm thấy file font nguồn: {path}",
        "err_no_colr": "[LỖI] File font đầu vào không chứa bảng màu COLR/CPAL!",
        "step_2d": "[*] Đang tách lớp vector phẳng COLRv0 cho chế độ 2D...",
        "info_in": "[*] Font nguồn  : {path} (Chế độ: {mode})",
        "info_out": "[*] Font đích   : {path}",
        "info_comp": "[*] Bộ nén PNG  : {engine}",
        "info_total": "[*] Tổng emoji  : {count} glyphs | Kích thước: {ppem}x{ppem} px",
        "info_families": "[+] Rendered {count} native Win11 3D ZWJ family sequences via HarfBuzz+Skia into CBDT.",
        "prog_render": "    Tiến độ render {mode} bằng Skia: {done}/{total} ({pct}%)",
        "prog_compress": "[*] Đang nén đa luồng {count} ảnh PNG...",
        "info_vs16": "[+] Đã đồng bộ {count} biến thể VS16 (U+FE0F) vào cmap (Sửa lỗi bàn phím di động).",
        "done_msg": "[THÀNH CÔNG] Hoàn tất trong {sec:.2f} giây! Đã lưu: {path} ({mb:.2f} MB)",
        "next_action": "\nBạn muốn làm gì tiếp theo?\n  [1] Quay lại menu chính để chuyển đổi tiếp\n  [0] Thoát chương trình\nLựa chọn của bạn [1/0]: ",
        "bye": "Tạm biệt! Chúc bạn build font thành công!",
    },
    "zh": {
        "label": "🇨🇳 中文 (Chinese)",
        "banner": "COLR2CBDT PRO ENGINE v4 — 多语言交互式转换器 (3D & 2D)",
        "help_title": "工具功能与使用说明：",
        "help_lines": [
            "1. 使用 Skia 引擎将 Windows 11 的 COLRv1 (3D) 或 COLRv0 (2D) 渲染为 109px 位图。",
            "2. 通过 pngquant / FASTOCTREE 多线程压缩 PNG，将字体体积控制在 30 MB 以内。",
            "3. 自动同步 VS16 (U+FE0F) 变体序列至 cmap 表，彻底解决手机键盘缺字问题。",
            "4. 同时支持命令行直接运行 (CLI): python colr2cbdt_3d_skia_v4.py <输入.ttf> <输出.ttf> [--mode 3d|2d]",
        ],
        "choose_mode": "请选择渲染模式 [1 = 3D (默认), 2 = 2D 扁平]: ",
        "prompt_src": "请输入源字体路径 (直接按回车使用 '{default}'): ",
        "prompt_dst": "请输入输出字体路径 (直接按回车使用 '{default}'): ",
        "err_not_found": "[错误] 找不到源字体文件: {path}",
        "err_no_colr": "[错误] 输入字体不包含 COLR/CPAL 彩色表！",
        "step_2d": "[*] 正在提取 2D 扁平 COLRv0 矢量图层...",
        "info_in": "[*] 源字体文件  : {path} (模式: {mode})",
        "info_out": "[*] 输出字体文件: {path}",
        "info_comp": "[*] PNG 压缩引擎: {engine}",
        "info_total": "[*] 表情总数    : {count} glyphs | 分辨率: {ppem}x{ppem} px",
        "info_families": "[+] Rendered {count} native Win11 3D ZWJ family sequences via HarfBuzz+Skia into CBDT.",
        "prog_render": "    Skia {mode} 渲染进度: {done}/{total} ({pct}%)",
        "prog_compress": "[*] 正在多线程压缩 {count} 张 PNG 位图...",
        "info_vs16": "[+] 已同步 {count} 个 VS16 (U+FE0F) 变体至 cmap (修复手机端显示)。",
        "done_msg": "[成功] 转换完成，耗时 {sec:.2f} 秒！已保存: {path} ({mb:.2f} MB)",
        "next_action": "\n接下来您想做什么？\n  [1] 返回主菜单继续转换其他字体\n  [0] 退出程序\n请输入选项 [1/0]: ",
        "bye": "再见！祝您使用愉快！",
    },
    "ru": {
        "label": "🇷🇺 Русский (Russian)",
        "banner": "COLR2CBDT PRO ENGINE v4 — ИНТЕРАКТИВНЫЙ КОНВЕРТЕР (3D & 2D)",
        "help_title": "ОПИСАНИЕ И СПОСОБЫ ЗАПУСКА:",
        "help_lines": [
            "1. Рендерит векторы Windows 11 COLRv1 (3D) или COLRv0 (2D) в четкие битмапы 109px.",
            "2. Сжимает PNG через pngquant / FASTOCTREE, уменьшая размер шрифта до < 30 МБ.",
            "3. Синхронизирует варианты VS16 (U+FE0F) в cmap для корректной работы на смартфонах.",
            "4. Поддерживает запуск из командной строки (CLI): python colr2cbdt_3d_skia_v4.py <вход.ttf> <выход.ttf> [--mode 3d|2d]",
        ],
        "choose_mode": "Выберите режим рендера [1 = 3D (По умолчанию), 2 = Плоский 2D]: ",
        "prompt_src": "Введите путь к исходному шрифту (Enter для '{default}'): ",
        "prompt_dst": "Введите имя выходного шрифта (Enter для '{default}'): ",
        "err_not_found": "[ОШИБКА] Исходный шрифт не найден: {path}",
        "err_no_colr": "[ОШИБКА] Входной шрифт не содержит таблиц COLR/CPAL!",
        "step_2d": "[*] Извлечение плоского векторного слоя COLRv0 для режима 2D...",
        "info_in": "[*] Исходный шрифт: {path} (Режим: {mode})",
        "info_out": "[*] Выходной шрифт: {path}",
        "info_comp": "[*] Сжатие PNG    : {engine}",
        "info_total": "[*] Всего эмодзи  : {count} глифов | Размер: {ppem}x{ppem} px",
        "info_families": "[+] Rendered {count} native Win11 3D ZWJ family sequences via HarfBuzz+Skia into CBDT.",
        "prog_render": "    Рендеринг {mode} через Skia: {done}/{total} ({pct}%)",
        "prog_compress": "[*] Многопоточное сжатие {count} изображений PNG...",
        "info_vs16": "[+] Синхронизировано {count} вариантов VS16 (U+FE0F) в cmap (фикс для смартфонов).",
        "done_msg": "[ГОТОВО] Завершено за {sec:.2f} сек! Сохранено: {path} ({mb:.2f} МБ)",
        "next_action": "\nЧто вы хотите сделать дальше?\n  [1] Вернуться в главное меню (конвертировать еще)\n  [0] Выйти из программы\nВаш выбор [1/0]: ",
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

def group_consecutive_glyphs(items):
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


# [EN] Sync VS16 (U+FE0F) variants from cmap Format 14 & GSUB into base cmap
# [VI] Đồng bộ các biến thể VS16 (U+FE0F) từ cmap Format 14 & GSUB vào bảng cmap chính
# [ZH] 将 cmap Format 14 和 GSUB 中的 VS16 (U+FE0F) 变体同步到主 cmap 表
# [RU] Синхронизация вариантов VS16 (U+FE0F) из cmap Format 14 и GSUB в основной cmap
def sync_vs16_to_cmap(font, rendered_glyphs):
    cmap = font.getBestCmap() or {}
    rev_cmap = {v: k for k, v in cmap.items()}
    direct_color_map = {}

    for table in font["cmap"].tables:
        if table.format == 14 and hasattr(table, "uvsDict"):
            for cp, var_gname in table.uvsDict.get(0xFE0F, []):
                actual_gname = var_gname or cmap.get(cp)
                if actual_gname and actual_gname in rendered_glyphs:
                    direct_color_map[cp] = actual_gname

    vs16_name = cmap.get(0xFE0F)
    if vs16_name and "GSUB" in font:
        gsub = font["GSUB"].table
        if gsub.LookupList:
            for lookup in gsub.LookupList.Lookup:
                subs = [getattr(s, "ExtSubTable", s) for s in lookup.SubTable] if lookup.LookupType == 7 else lookup.SubTable
                for st in subs:
                    for first, ligs in (getattr(st, "ligatures", None) or {}).items():
                        for lig in ligs:
                            if list(lig.Component) == list((vs16_name,)) and lig.LigGlyph in rendered_glyphs:
                                if first in rev_cmap:
                                    direct_color_map[rev_cmap[first]] = lig.LigGlyph

    for table in font["cmap"].tables:
        if table.isUnicode() and table.format in (4, 12):
            for cp, color_gname in direct_color_map.items():
                if table.format == 4 and cp > 0xFFFF:
                    continue
                if cp in table.cmap:
                    table.cmap[cp] = color_gname

    return len(direct_color_map)


# [EN] Downgrade COLRv1 to flat COLRv0 for 2D mode
# [VI] Hạ cấp COLRv1 xuống lớp COLRv0 phẳng cho chế độ 2D
# [ZH] 将 COLRv1 降级为扁平 COLRv0 以进行 2D 渲染
# [RU] Понижение COLRv1 до плоского COLRv0 для режима 2D
def prepare_2d_colrv0_temp(input_ttf):
    font = ttLib.TTFont(input_ttf, lazy=False)
    if "COLR" not in font:
        font.close()
        return input_ttf, None

    colr_tbl = font["COLR"].table
    if getattr(colr_tbl, "BaseGlyphRecordArray", None) and getattr(colr_tbl, "LayerRecordArray", None):
        colr_tbl.Version = 0
        for attr in ("BaseGlyphList", "LayerList", "ClipList", "VarIndexMap", "ItemVariationStore"):
            if hasattr(colr_tbl, attr):
                setattr(colr_tbl, attr, None)
        font["COLR"].version = 0

    fd, tmp_path = tempfile.mkstemp(suffix="_2d_v0.ttf")
    os.close(fd)
    font.save(tmp_path)
    font.close()
    return tmp_path, tmp_path

def collect_all_gsub_targets(font):
    """Quét toàn bộ glyph kết quả trong GSUB (bao gồm chuỗi gia đình nhiều người ZWJ) để Skia render đủ ảnh."""
    targets = set()
    if "GSUB" not in font or not font["GSUB"].table.LookupList:
        return targets
    for lookup in font["GSUB"].table.LookupList.Lookup:
        subs = [getattr(s, "ExtSubTable", s) for s in lookup.SubTable] if lookup.LookupType == 7 else lookup.SubTable
        for st in subs:
            for ligs in (getattr(st, "ligatures", None) or {}).values():
                for lig in ligs:
                    if lig.LigGlyph:
                        targets.add(lig.LigGlyph)
    return targets

import uharfbuzz as hb
from fontTools.ttLib.tables import otTables
from fontTools.ttLib.tables._g_l_y_f import Glyph


# [EN] Self-contained generator for all Win11 multi-person & skin-tone ZWJ sequences
# [VI] Hàm tự chủ sinh toàn bộ chuỗi tổ hợp ZWJ đa người & đa màu da của Windows 11
# [ZH] 自包含生成所有 Win11 多人及肤色 ZWJ 组合序列
# [RU] Автономный генератор всех многоперсональных ZWJ-серий Win11
def generate_unicode_family_sequences():
    adults = [0x1F468, 0x1F469, 0x1F9D1]  # Man, Woman, Person
    tones = [None, 0x1F3FB, 0x1F3FC, 0x1F3FD, 0x1F3FE, 0x1F3FF]
    skin_tones = [0x1F3FB, 0x1F3FC, 0x1F3FD, 0x1F3FE, 0x1F3FF]
    genders = ([0x2640, 0xFE0F], [0x2640], [0x2642, 0xFE0F], [0x2642])
    zwj = 0x200D
    seqs = []

    # 1. Gia đình 1 hoặc 2 người lớn + 1 hoặc 2 con (kèm biến thể màu da đồng nhất)
    adult_pairs = [
        [0x1F468, 0x1F469], [0x1F468, 0x1F468], [0x1F469, 0x1F469], [0x1F9D1, 0x1F9D1],
        [0x1F468], [0x1F469], [0x1F9D1],
    ]
    child_groups = [
        [0x1F466], [0x1F467],
        [0x1F467, 0x1F466], [0x1F466, 0x1F466], [0x1F467, 0x1F467],
    ]
    for ap in adult_pairs:
        for cg in child_groups:
            for t in tones:
                full = []
                for idx, cp in enumerate(ap + cg):
                    if idx > 0:
                        full.append(zwj)
                    full.append(cp)
                    if t is not None:
                        full.append(t)
                seqs.append(tuple(full))

    # 2. Tất cả các loại cặp đôi: Hôn (💋), Tim (❤️), Đánh nhau (  ), Tai thỏ (🐰), Đấu vật (🤼), Nắm tay (🤝), Đứng cạnh
    mid_connectors = [
        [zwj, 0x2764, 0xFE0F, zwj, 0x1F48B, zwj],   # Cặp đôi hôn nhau (có VS16)
        [zwj, 0x2764, zwj, 0x1F48B, zwj],           # Cặp đôi hôn nhau (không VS16)
        [zwj, 0x2764, 0xFE0F, zwj],                 # Cặp đôi với trái tim (có VS16)
        [zwj, 0x2764, zwj],                         # Cặp đôi với trái tim (không VS16)
        [zwj, 0x1FAEF, zwj],                        # Đám mây đánh nhau đa tông da (👩🏿‍  ‍👩🏾)
        [zwj, 0x1F430, zwj],                        # Người đeo tai thỏ đa tông da (👩🏿‍🐰‍👩🏾)
        [zwj, 0x1F93C, zwj],                        # Người đấu vật đa tông da (👩🏿‍🤼‍👩🏾)
        [zwj, 0x1F91D, zwj],                        # Nắm tay đa tông da (gồm cả Cặp chung 🧑🏻‍🤝‍🧑🏼)
        [zwj],                                      # Cặp đôi đứng cạnh nhau đa tông da (gồm cả Cặp chung 🧑🏻‍🧑🏼)
    ]
    for a1 in adults:
        for a2 in adults:
            for conn in mid_connectors:
                for t1 in tones:
                    for t2 in tones:
                        if (t1 is None) != (t2 is None):
                            continue
                        p1 = [a1, t1] if t1 else [a1]
                        p2 = [a2, t2] if t2 else [a2]
                        seqs.append(tuple(p1 + conn + p2))

    # 3. Cái bắt tay 2 bàn tay đa tông da (Rightwards Hand + Leftwards Hand)
    for t1 in tones:
        for t2 in tones:
            if t1 is None and t2 is None:
                continue
            h1 = [0x1FAF1, t1] if t1 else [0x1FAF1]
            h2 = [0x1FAF2, t2] if t2 else [0x1FAF2]
            seqs.append(tuple(h1 + [zwj] + h2))

    # 4. Ballet Dancer (🩰 0x1FA70) — Trung tính, Nữ, Nam + đủ 6 màu da (Emoji 17.0)
    for a in adults:
        for t in tones:
            base = [a, t] if t else [a]
            seqs.append(tuple(base + [zwj, 0x1FA70]))
            seqs.append(tuple(base + [zwj, 0x1FA70, 0xFE0F]))

    # 5. Đấu vật (🤼 0x1F93C), Tai thỏ (👯 0x1F46F) & Đám mây đánh nhau (   0x1FAEF) mọi biến thể giới tính & 2 tông da
    for base_cp in (0x1F93C, 0x1F46F, 0x1FAEF):
        for t1 in skin_tones:
            for g in genders:
                seqs.append((base_cp, t1, zwj, *g))
                seqs.append((base_cp, zwj, *g, t1))
            for t2 in skin_tones:
                seqs.append((base_cp, t1, zwj, t2))
                for g in genders:
                    seqs.append((base_cp, t1, zwj, t2, zwj, *g))
                    seqs.append((base_cp, zwj, *g, t1, zwj, t2))

    # Loại bỏ trùng lặp & SẮP XẾP PHỨC TẠP/DÀI NHẤT TRƯỚC -> ĐƠN GIẢN SAU
    seen = set()
    unique_seqs = []
    for s in seqs:
        if s not in seen:
            seen.add(s)
            unique_seqs.append(s)

    unique_seqs.sort(key=lambda s: -len(s))
    return unique_seqs



# [EN] Shape & render 100% native Win11 3D ZWJ sequences via HarfBuzz + Skia with slot recycling
# [VI] Định hình & render 100% chuỗi ZWJ 3D Win11 qua HarfBuzz + Skia (tự tái chế slot chống tràn)
# [ZH] 通过 HarfBuzz + Skia 渲染全部 Win11 原生 3D ZWJ 组合序列（自动回收空闲字形槽位）
# [RU] Рендеринг 100% 3D ZWJ-серий Win11 через HarfBuzz + Skia с переработкой слотов
def render_native_win11_zwj_families(font, skia_input_path, sk_font, ppem, quality, txt):
    with open(skia_input_path, "rb") as f:
        hb_blob = hb.Blob(f.read())
    hb_face = hb.Face(hb_blob)
    hb_font = hb.Font(hb_face)

    upm = font["head"].unitsPerEm
    scale = ppem / float(upm)
    ascender = int(round(font["hhea"].ascent * scale))
    cmap = font.getBestCmap() or {}
    order = list(font.getGlyphOrder())
    existing = set(order)
    glyf = font["glyf"]
    hmtx = font["hmtx"].metrics

    # Khóa tăng trưởng tổng glyph ở 65180 (chừa 355 slot sạch cho Bước 2); phần vượt dùng lại mảnh COLR thừa
    max_step1_glyphs = 65180
    protected_step1 = {".notdef", ".null", "nonmarkingreturn", "space"} | set(cmap.values()) | collect_all_gsub_targets(font)
    colr_tbl = font["COLR"].table
    if getattr(colr_tbl, "BaseGlyphList", None):
        for rec in colr_tbl.BaseGlyphList.BaseGlyphPaintRecord:
            protected_step1.add(rec.BaseGlyph)
    if getattr(colr_tbl, "BaseGlyphRecordArray", None):
        for rec in colr_tbl.BaseGlyphRecordArray.BaseGlyphRecord:
            protected_step1.add(rec.BaseGlyph)
    recyclable_step1 = [gn for gn in order if gn not in protected_step1]

    pad = int(ppem * 0.45)
    canvas_w = int(ppem * 2.2) + pad * 2
    canvas_h = int(ppem * 1.8) + pad * 2
    baseline_y = pad + ascender
    img_info = skia.ImageInfo.Make(
        canvas_w, canvas_h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kUnpremul_AlphaType
    )

    raw_fam_tasks = []
    fam_rules = []
    fam_idx = 0

    for seq_cps in generate_unicode_family_sequences():
        if any(cp not in cmap for cp in seq_cps):
            continue

        seq_str = "".join(chr(cp) for cp in seq_cps)
        buf = hb.Buffer()
        buf.add_str(seq_str)
        buf.guess_segment_properties()
        hb.shape(hb_font, buf)

        infos = buf.glyph_infos
        positions = buf.glyph_positions
        if len(infos) < 2:
            continue

        surface = skia.Surface.MakeRaster(img_info)
        canvas = surface.getCanvas()
        canvas.clear(skia.ColorTRANSPARENT)
        paint = skia.Paint(AntiAlias=True)

        cur_x = 0.0
        for info, pos in zip(infos, positions):
            gid = info.codepoint
            gx = float(pad) + (cur_x + pos.x_offset) * scale
            gy = float(baseline_y) - pos.y_offset * scale
            blob = skia.TextBlob.MakeFromText(
                bytes([gid & 0xFF, (gid >> 8) & 0xFF]), sk_font, skia.TextEncoding.kGlyphID
            )
            if blob is not None:
                canvas.drawTextBlob(blob, gx, gy, paint)
            cur_x += pos.x_advance

        pil_img = Image.frombytes("RGBA", (canvas_w, canvas_h), surface.makeImageSnapshot().tobytes(), "raw", "RGBA")
        bbox = pil_img.getbbox()
        if bbox is None:
            continue

        x0, y0, x1, y1 = bbox
        cropped = pil_img.crop(bbox)
        w, h = cropped.size
        bx = x0 - pad
        by = baseline_y - y0

        if w > MAX_BYTE or h > MAX_BYTE:
            s = min(MAX_BYTE / w, MAX_BYTE / h)
            w, h = max(1, int(w * s)), max(1, int(h * s))
            cropped = cropped.resize((w, h), Image.Resampling.LANCZOS)
            bx, by = int(bx * s), int(by * s)

        fam_idx += 1
        if len(order) >= max_step1_glyphs and recyclable_step1:
            fam_gname = recyclable_step1.pop()
        else:
            fam_gname = f"w11_fam_{fam_idx:03d}"
            while fam_gname in existing:
                fam_idx += 1
                fam_gname = f"w11_fam_{fam_idx:03d}"
            existing.add(fam_gname)
            order.append(fam_gname)

        g = Glyph()
        g.numberOfContours = 0
        g.xMin = g.yMin = g.xMax = g.yMax = 0
        glyf[fam_gname] = g

        ref_w, _ = hmtx.get(cmap[0x1F468], (upm, 0))
        hmtx[fam_gname] = (ref_w, 0)
        adv_px = max(1, min(MAX_BYTE, int(round(ref_w * scale))))

        png_buf = io.BytesIO()
        cropped.save(png_buf, format="PNG", optimize=True)
        raw_fam_tasks.append((fam_gname, w, h, bx, by, adv_px, png_buf.getvalue()))

        g_seq = [cmap[cp] for cp in seq_cps]
        fam_rules.append((next(iter(g_seq)), g_seq[1:], fam_gname))

    if not raw_fam_tasks:
        return {}, []

    font.setGlyphOrder(order)
    font["maxp"].numGlyphs = len(order)
    if "hhea" in font:
        font["hhea"].numberOfHMetrics = len(order)

    compressed_fam = {}
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
        futs = {ex.submit(compress_png, item[6], quality): item[0] for item in raw_fam_tasks}
        for fut in futs:
            compressed_fam[futs[fut]] = fut.result()

    fam_cbdt_dict = {}
    for fam_gname, w, h, bx, by, adv_px, _ in raw_fam_tasks:
        glyph = C_B_D_T_.cbdt_bitmap_format_17(data=b"", ttFont=font)
        glyph.metrics = C_B_D_T_.SmallGlyphMetrics()
        glyph.metrics.height = h
        glyph.metrics.width = w
        glyph.metrics.BearingX = max(MIN_SIGNED, min(MAX_SIGNED, bx))
        glyph.metrics.BearingY = max(MIN_SIGNED, min(MAX_SIGNED, by))
        glyph.metrics.Advance = adv_px
        glyph.imageData = compressed_fam[fam_gname]
        fam_cbdt_dict[fam_gname] = glyph

    if fam_rules and "GSUB" in font:
        gsub = font["GSUB"].table
        lig_sub = otTables.LigatureSubst()
        lig_sub.ligatures = {}
        fam_rules.sort(key=lambda r: len(r[1]), reverse=True)
        for d_first, d_comps, d_lig in fam_rules:
            rec = otTables.Ligature()
            rec.Component = d_comps
            rec.CompCount = len(d_comps) + 1
            rec.LigGlyph = d_lig
            lig_sub.ligatures.setdefault(d_first, []).append(rec)

        lookup = otTables.Lookup()
        lookup.LookupType = 4
        lookup.LookupFlag = 0
        lookup.SubTable = list((lig_sub,))
        lookup.SubTableCount = 1
        gsub.LookupList.Lookup.append(lookup)
        new_idx = len(gsub.LookupList.Lookup) - 1
        gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
        for fr in gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag in ("ccmp", "liga", "rlig"):
                fr.Feature.LookupListIndex.insert(0, new_idx)
                fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)

    rev_map = font.getReverseGlyphMap(rebuild=True)
    fam_valid_pairs = [(rev_map[gn], gn) for gn in fam_cbdt_dict]
    print(txt["info_families"].format(count=len(fam_cbdt_dict)))
    return fam_cbdt_dict, fam_valid_pairs


# [EN] Main conversion routine (Skia Rasterization + Parallel PNG Compression)
# [VI] Hàm chuyển đổi chính (Render Skia + Nén PNG đa luồng)
# [ZH] 核心转换流程 (Skia 栅格化渲染 + 多线程 PNG 压缩)
# [RU] Основная функция конвертации (Рендеринг Skia + Многопоточное сжатие PNG)
def render_colrv1_to_cbdt(input_ttf, output_ttf, ppem=109, quality=90, mode="3d", strip_colr=False, lang="en", pc_hybrid=False):
    t0 = time.time()
    txt = LANG_PACK.get(lang, LANG_PACK["en"])
    mode_upper = mode.upper()

    if not os.path.isfile(input_ttf):
        raise FileNotFoundError(txt["err_not_found"].format(path=input_ttf))

    skia_input_path = input_ttf
    temp_2d_file = None
    if mode.lower() == "2d":
        print(txt["step_2d"])
        skia_input_path, temp_2d_file = prepare_2d_colrv0_temp(input_ttf)

    try:
        typeface = skia.Typeface.MakeFromFile(skia_input_path)
        if typeface is None:
            raise RuntimeError(f"Skia cannot open font: {skia_input_path}")

        sk_font = skia.Font(typeface, float(ppem))
        sk_font.setEdging(skia.Font.Edging.kAntiAlias)

        font = ttLib.TTFont(input_ttf, lazy=False)
        if "COLR" not in font or "CPAL" not in font:
            raise ValueError(txt["err_no_colr"])

        original_order = list(font.getGlyphOrder())
        colr_table = font["COLR"].table
        color_glyph_names = set()
        if pc_hybrid:
            cmap_probe = font.getBestCmap() or {}
            sample_gn = cmap_probe.get(0x1F600) or next(iter(cmap_probe.values()))
            color_glyph_names.add(sample_gn)
            print("[*] Mode: Pure PC Hybrid (--pc-hybrid) -> Minimal CBDT shell (1 sample glyph) for Win11!")
        else:
            if getattr(colr_table, "BaseGlyphList", None):
                for rec in colr_table.BaseGlyphList.BaseGlyphPaintRecord:
                    color_glyph_names.add(rec.BaseGlyph)
            if getattr(colr_table, "BaseGlyphRecordArray", None):
                for rec in colr_table.BaseGlyphRecordArray.BaseGlyphRecord:
                    color_glyph_names.add(rec.BaseGlyph)
            color_glyph_names.update(collect_all_gsub_targets(font))
    
        upm = font["head"].unitsPerEm
        scale = ppem / float(upm)
        ascender = int(round(font["hhea"].ascent * scale))
        descender = int(round(font["hhea"].descent * scale))

        comp_engine = "pngquant binary" if PNGQUANT_BIN else "Pillow FASTOCTREE (Mobile Native)"
        print(txt["info_in"].format(path=input_ttf, mode=mode_upper))
        print(txt["info_out"].format(path=output_ttf))
        print(txt["info_comp"].format(engine=comp_engine))
        print(txt["info_total"].format(count=len(color_glyph_names), ppem=ppem))

        pad = int(ppem * 0.45)
        canvas_w = int(ppem * 2.0) + pad * 2
        canvas_h = int(ppem * 1.8) + pad * 2
        baseline_y = pad + ascender

        img_info = skia.ImageInfo.Make(
            canvas_w,
            canvas_h,
            skia.ColorType.kRGBA_8888_ColorType,
            skia.AlphaType.kUnpremul_AlphaType,
        )

        raw_tasks = []
        total_v1 = len(color_glyph_names)
        done = 0

        for gid, gname in enumerate(original_order):
            if gname not in color_glyph_names:
                continue

            done += 1
            if done % 300 == 0 or done == total_v1:
                print(txt["prog_render"].format(mode=mode_upper, done=done, total=total_v1, pct=done * 100 // total_v1), end="\r")

            surface = skia.Surface.MakeRaster(img_info)
            canvas = surface.getCanvas()
            canvas.clear(skia.ColorTRANSPARENT)

            paint = skia.Paint(AntiAlias=True)
            blob = skia.TextBlob.MakeFromText(
                bytes([gid & 0xFF, (gid >> 8) & 0xFF]),
                sk_font,
                skia.TextEncoding.kGlyphID,
            )
            canvas.drawTextBlob(blob, float(pad), float(baseline_y), paint)

            img_sk = surface.makeImageSnapshot()
            pil_img = Image.frombytes("RGBA", (canvas_w, canvas_h), img_sk.tobytes(), "raw", "RGBA")

            bbox = pil_img.getbbox()
            if bbox is None:
                continue

            x0, y0, x1, y1 = bbox
            cropped = pil_img.crop(bbox)
            w, h = cropped.size
            bx = x0 - pad
            by = baseline_y - y0

            if w > MAX_BYTE or h > MAX_BYTE:
                s = min(MAX_BYTE / w, MAX_BYTE / h)
                w, h = max(1, int(w * s)), max(1, int(h * s))
                cropped = cropped.resize((w, h), Image.Resampling.LANCZOS)
                bx, by = int(bx * s), int(by * s)

            adv_units, _ = font["hmtx"].metrics[gname]
            adv_px = max(1, min(MAX_BYTE, int(round(adv_units * scale))))

            buf = io.BytesIO()
            cropped.save(buf, format="PNG", optimize=True)
            raw_tasks.append((gid, gname, w, h, bx, by, adv_px, buf.getvalue()))

        print("\n" + txt["prog_compress"].format(count=len(raw_tasks)))
        compressed_map = {}

        def _compress_worker(task_item):
            _, gn, _, _, _, _, _, raw_png = task_item
            return gn, compress_png(raw_png, quality)

        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            for gn, c_bytes in ex.map(_compress_worker, raw_tasks):
                compressed_map[gn] = c_bytes

        data = {}
        valid = []
        for gid, gname, w, h, bx, by, adv_px, _ in raw_tasks:
            glyph = C_B_D_T_.cbdt_bitmap_format_17(data=b"", ttFont=font)
            glyph.metrics = C_B_D_T_.SmallGlyphMetrics()
            glyph.metrics.height = h
            glyph.metrics.width = w
            glyph.metrics.BearingX = max(MIN_SIGNED, min(MAX_SIGNED, bx))
            glyph.metrics.BearingY = max(MIN_SIGNED, min(MAX_SIGNED, by))
            glyph.metrics.Advance = adv_px
            glyph.imageData = compressed_map[gname]

            data[gname] = glyph
            valid.append((gid, gname))

        if not pc_hybrid:
            fam_data, fam_pairs = render_native_win11_zwj_families(font, skia_input_path, sk_font, ppem, quality, txt)
            data.update(fam_data)
            valid.extend(fam_pairs)

        valid.sort()

        first_gid, _ = next(iter(valid))
        last_gid, _ = valid[-1]

        strike = E_B_L_C_.Strike()
        bst = E_B_L_C_.BitmapSizeTable()
        bst.ppemX = bst.ppemY = ppem
        bst.bitDepth = 32
        bst.flags = 1
        bst.colorRef = 0
        bst.startGlyphIndex = first_gid
        bst.endGlyphIndex = last_gid

        lm = E_B_L_C_.SbitLineMetrics()
        lm.ascender = max(MIN_SIGNED, min(MAX_SIGNED, ascender))
        lm.descender = max(MIN_SIGNED, min(MAX_SIGNED, descender))
        lm.widthMax = min(MAX_BYTE, ppem)
        lm.caretSlopeNumerator = 0
        lm.caretSlopeDenominator = 1
        lm.caretOffset = 0
        lm.minOriginSB = lm.minAdvanceSB = 0
        lm.maxBeforeBL = lm.ascender
        lm.minAfterBL = lm.descender
        lm.pad1 = lm.pad2 = 0
        bst.hori = bst.vert = lm
        strike.bitmapSizeTable = bst

        subtables = []
        for grp in group_consecutive_glyphs(valid):
            g_first, _ = next(iter(grp))
            g_last, _ = grp[-1]
            sub = E_B_L_C_.eblc_index_sub_table_1(data=b"", ttFont=font)
            sub.indexFormat = 1
            sub.imageFormat = 17
            sub.firstGlyphIndex = g_first
            sub.lastGlyphIndex = g_last
            sub.names = [name for _, name in grp]
            subtables.append(sub)

        strike.indexSubTables = subtables
        bst.numberOfIndexSubTables = len(subtables)

        cbdt = ttLib.newTable("CBDT")
        cbdt.version = 3.0
        cbdt.strikeData = list((data,))

        cblc = ttLib.newTable("CBLC")
        cblc.version = 3.0
        cblc.strikes = list((strike,))

        font["CBDT"] = cbdt
        font["CBLC"] = cblc

        vs16_fixed = sync_vs16_to_cmap(font, set(data.keys()))
        print(txt["info_vs16"].format(count=vs16_fixed))

        if strip_colr or mode.lower() == "2d":
            for tag in ("COLR", "CPAL", "SVG "):
                if tag in font:
                    del font[tag]

        font.save(output_ttf)
        font.close()

        size_mb = os.path.getsize(output_ttf) / (1024 * 1024)
        print("=" * 72)
        print(txt["done_msg"].format(sec=time.time() - t0, path=output_ttf, mb=size_mb))
        print("=" * 72)
    finally:
        if temp_2d_file and os.path.exists(temp_2d_file):
            os.remove(temp_2d_file)


# [EN] Interactive 4-language menu wizard | [VI] Menu tương tác 4 ngôn ngữ
# [ZH] 四语言交互式向导菜单             | [RU] Интерактивное меню на 4 языках
def run_interactive_wizard():
    lang_keys = ("en", "vi", "zh", "ru")
    while True:
        print("\n" + "=" * 72)
        print(" SELECT LANGUAGE / CHỌN NGÔN NGỮ / 选择语言 / ВЫБЕРИТЕ ЯЗЫК")
        print("=" * 72)
        for idx, k in enumerate(lang_keys, 1):
            print(f"  [{idx}] {LANG_PACK[k]['label']}")
        print("  [0] Exit / Thoát / 退出 / Выход")

        choice = input("\n👉 Choice [1-4, default=1]: ").strip()
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

        m_in = input(txt["choose_mode"]).strip()
        mode = "2d" if m_in == "2" else "3d"

        default_src = "seguiemj.ttf" if os.path.isfile("seguiemj.ttf") else r"C:\Windows\Fonts\seguiemj.ttf"
        src_path = input(txt["prompt_src"].format(default=default_src)).strip().strip('"') or default_src

        default_dst = "seguiemj_2d_pro5.ttf" if mode == "2d" else "seguiemj_3d_pro5.ttf"
        dst_path = input(txt["prompt_dst"].format(default=default_dst)).strip().strip('"') or default_dst

        print("-" * 72)
        try:
            render_colrv1_to_cbdt(src_path, dst_path, ppem=109, quality=90, mode=mode, lang=lang)
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
        parser = argparse.ArgumentParser(description="COLRv1/v0 (3D & 2D) to CBDT/CBLC Converter")
        parser.add_argument("input", help="Source font (e.g. seguiemj.ttf)")
        parser.add_argument("output", help="Output font (e.g. seguiemj_3d_pro5.ttf)")
        parser.add_argument("--mode", choices=["3d", "2d"], default="3d", help="Render mode: 3d or 2d")
        parser.add_argument("--ppem", type=int, default=109, help="Bitmap size (Default: 109)")
        parser.add_argument("--quality", type=int, default=90, help="PNG quality 1-100 (Default: 90)")
        parser.add_argument("--pc-hybrid", action="store_true", help="Only bake missing ZWJ sequences into CBDT (Win11 PC vector priority)")
        parser.add_argument("--strip-colr", action="store_true", help="Strip COLR/CPAL tables")
        parser.add_argument("--lang", choices=["en", "vi", "zh", "ru"], default="en", help="UI language")
        args = parser.parse_args()

        try:
            render_colrv1_to_cbdt(args.input, args.output, args.ppem, args.quality, args.mode, args.strip_colr, args.lang, args.pc_hybrid)
        except Exception as exc:
            print(f"\n[FAILED] {type(exc).__name__}: {exc}")
            sys.exit(1)
