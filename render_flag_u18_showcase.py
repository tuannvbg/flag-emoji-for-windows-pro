#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# render_flag_u18_showcase.py (Part 1/2)
# [EN] Multi-Language Grid Showcase Renderer (262 Flags + Full U17 & U18)
# [VI] Trình xuất ảnh lưới kiểm thử đa ngôn ngữ (262 cờ + Full U17 & U18)
# [ZH] 多语言表情网格预览图生成器 (262 面国旗 + 完整 Unicode 17.0 & 18.0)
# [RU] Мультиязычный генератор сетки превью (262 флага + полный U17 и U18)
# ============================================================================
# ============================================================================
# CLI ARGUMENTS / THAM SỐ DÒNG LỆNH / 命令行参数 / ПАРАМЕТРЫ КОМАНДНОЙ СТРОКИ:
#
# [EN] Usage: python render_flag_u18_showcase.py <font.ttf> [output.png] [options]
#   output.png                  : Output PNG filename (default: flags_showcase.png)
#   --cols <int>                : Number of columns per row (default: 24)
#   --size <int>                : Emoji icon size in pixels (default: 72)
#   --bg {white,dark,transparent}: Canvas background color (default: white)
#   --include-u17-u18           : Append full Unicode 17.0 & 18.0 emojis below flags
#   --lang {en,vi,zh,ru}        : Console log language (default: en)
#
# [VI] Cách dùng: python render_flag_u18_showcase.py <font.ttf> [ảnh_đích.png] [tùy chọn]
#   ảnh_đích.png                : Tên file ảnh PNG xuất ra (mặc định: flags_showcase.png)
#   --cols <số nguyên>          : Số cột biểu tượng trên mỗi hàng (mặc định: 24)
#   --size <số nguyên>          : Kích thước mỗi emoji tính theo pixel (mặc định: 72)
#   --bg {white,dark,transparent}: Màu nền ảnh: trắng, tối hoặc trong suốt (mặc định: white)
#   --include-u17-u18           : Xuất kèm trọn bộ emoji Unicode 17.0 & 18.0 dưới lưới cờ
#   --lang {en,vi,zh,ru}        : Ngôn ngữ hiển thị log (mặc định: en)
#
# [ZH] 用法: python render_flag_u18_showcase.py <字体.ttf> [输出.png] [选项]
#   输出.png                    : 输出 PNG 图片文件名 (默认: flags_showcase.png)
#   --cols <整数>               : 每行显示的图标列数 (默认: 24)
#   --size <整数>               : 单个表情图标的像素尺寸 (默认: 72)
#   --bg {white,dark,transparent}: 画布背景颜色：白色、深色或透明 (默认: white)
#   --include-u17-u18           : 在国旗网格下方附加完整 Unicode 17.0 & 18.0 表情
#   --lang {en,vi,zh,ru}        : 终端日志语言 (默认: en)
#
# [RU] Использование: python render_flag_u18_showcase.py <шрифт.ttf> [выход.png] [опции]
#   выход.png                   : Имя выходного PNG-файла (по умолчанию: flags_showcase.png)
#   --cols <целое>              : Количество столбцов в строке (по умолчанию: 24)
#   --size <целое>              : Размер иконки эмодзи в пикселях (по умолчанию: 72)
#   --bg {white,dark,transparent}: Цвет фона: белый, темный или прозрачный (по умолчанию: white)
#   --include-u17-u18           : Добавить полный набор Unicode 17.0 и 18.0 под флагами
#   --lang {en,vi,zh,ru}        : Язык логов в консоли (по умолчанию: en)
# ============================================================================

import os
import sys
import argparse
import subprocess
import importlib.util

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def ensure_packages():
    required = {"fontTools": "fonttools", "skia": "skia-python"}
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"[*] Installing missing packages: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])


ensure_packages()

import skia
from fontTools.ttLib import TTFont

LANG_PACK = {
    "en": {
        "label": "🇺🇸 English",
        "banner": "FLAG & UNICODE 17.0/18.0 SHOWCASE RENDERER",
        "help_title": "TOOL OVERVIEW & USAGE:",
        "help_lines": [
            "1. Renders a crisp PNG grid of all 262 flags (259 ISO countries + 3 subdivisions).",
            "2. Optionally appends full Unicode 17.0 & 18.0 emojis (including ZWJ & skin tones).",
            "3. CLI mode: python render_flag_u18_showcase.py <font.ttf> [out.png] [--include-u17-u18]",
        ],
        "prompt_font": "Enter font path to preview (Enter for '{default}'): ",
        "prompt_out": "Enter output PNG filename (Enter for '{default}'): ",
        "prompt_u18": "Include Unicode 17.0 & 18.0 emojis? [1 = Yes (Default), 2 = Flags only]: ",
        "prompt_bg": "Select background [1 = White (Default), 2 = Dark, 3 = Transparent]: ",
        "err_missing": "[ERROR] Font file not found: {path}",
        "info_font": "[*] Font       : {path}",
        "info_size": "[*] Resolution : {w}x{h} px ({rows} rows x {cols} cols)",
        "info_match": "[*] Rendered   : {matched}/{total} emojis matched GSUB/CMAP",
        "done_msg": "[SUCCESS] Showcase saved: {out} ({kb:.1f} KB)",
        "next_action": "\nNext step:\n  (1) Return to main menu\n  (0) Exit program\nYour choice (1/0): ",
        "bye": "Goodbye!",
    },
    "vi": {
        "label": "🇻🇳 Tiếng Việt (Vietnamese)",
        "banner": "TRÌNH XUẤT ẢNH LƯỚI KIỂM THỬ 262 CỜ & UNICODE 17.0/18.0",
        "help_title": "GIỚI THIỆU CÔNG DỤNG & CÁCH DÙNG:",
        "help_lines": [
            "1. Xuất ảnh lưới PNG sắc nét gồm toàn bộ 262 lá cờ (259 quốc kỳ + 3 cờ tiểu vùng).",
            "2. Tùy chọn hiển thị kèm trọn bộ Unicode 17.0 & 18.0 (gồm chuỗi ZWJ & màu da).",
            "3. Hỗ trợ chạy dòng lệnh (CLI): python render_flag_u18_showcase.py <font.ttf> [ảnh.png] [--include-u17-u18]",
        ],
        "prompt_font": "Nhập đường dẫn file font cần xuất ảnh (Enter để dùng '{default}'): ",
        "prompt_out": "Nhập tên file ảnh PNG đầu ra (Enter để dùng '{default}'): ",
        "prompt_u18": "Xuất kèm trọn bộ Unicode 17.0 & 18.0? [1 = Có (Mặc định), 2 = Chỉ 262 cờ]: ",
        "prompt_bg": "Chọn màu nền ảnh [1 = Trắng (Mặc định), 2 = Tối (Dark), 3 = Trong suốt]: ",
        "err_missing": "[LỖI] Không tìm thấy file font: {path}",
        "info_font": "[*] Font nguồn : {path}",
        "info_size": "[*] Kích thước : {w}x{h} px ({rows} hàng x {cols} cột)",
        "info_match": "[*] Hiển thị   : {matched}/{total} biểu tượng khớp GSUB/CMAP",
        "done_msg": "[THÀNH CÔNG] Đã xuất ảnh showcase: {out} ({kb:.1f} KB)",
        "next_action": "\nBạn muốn làm gì tiếp theo?\n  (1) Quay lại menu chính\n  (0) Thoát chương trình\nLựa chọn của bạn (1/0): ",
        "bye": "Tạm biệt!",
    },
    "zh": {
        "label": "🇨🇳 中文 (Chinese)",
        "banner": "262 面国旗与 UNICODE 17.0/18.0 网格预览图生成器",
        "help_title": "工具功能与使用说明：",
        "help_lines": [
            "1. 生成包含全部 262 面旗帜（259 个国家/地区 + 3 个子区域）的高清 PNG 网格图。",
            "2. 可选附加完整 Unicode 17.0 & 18.0 表情（含 ZWJ 与肤色变体）。",
            "3. 命令行模式 (CLI): python render_flag_u18_showcase.py <字体.ttf> [输出.png] [--include-u17-u18]",
        ],
        "prompt_font": "请输入要预览的字体路径 (回车使用 '{default}'): ",
        "prompt_out": "请输入输出 PNG 图片名称 (回车使用 '{default}'): ",
        "prompt_u18": "是否包含 Unicode 17.0 & 18.0 表情？[1 = 是 (默认), 2 = 仅国旗]: ",
        "prompt_bg": "请选择背景颜色 [1 = 白色 (默认), 2 = 深色, 3 = 透明]: ",
        "err_missing": "[错误] 找不到字体文件: {path}",
        "info_font": "[*] 字体文件   : {path}",
        "info_size": "[*] 图片尺寸   : {w}x{h} px ({rows} 行 x {cols} 列)",
        "info_match": "[*] 成功匹配   : {matched}/{total} 个表情匹配 GSUB/CMAP",
        "done_msg": "[成功] 已生成预览图: {out} ({kb:.1f} KB)",
        "next_action": "\n接下来您想做什么？\n  (1) 返回主菜单\n  (0) 退出程序\n请输入选项 (1/0): ",
        "bye": "再见！",
    },
    "ru": {
        "label": "🇷🇺 Русский (Russian)",
        "banner": "ГЕНЕРАТОР ПРЕВЬЮ-СЕТКИ 262 ФЛАГОВ И UNICODE 17.0/18.0",
        "help_title": "ОПИСАНИЕ И СПОСОБЫ ЗАПУСКА:",
        "help_lines": [
            "1. Создает четкую PNG-сетку всех 262 флагов (259 стран + 3 региона).",
            "2. По желанию добавляет полный набор Unicode 17.0 и 18.0 (включая ZWJ и оттенки кожи).",
            "3. Режим CLI: python render_flag_u18_showcase.py <шрифт.ttf> [выход.png] [--include-u17-u18]",
        ],
        "prompt_font": "Введите путь к шрифту для превью (Enter для '{default}'): ",
        "prompt_out": "Введите имя выходного PNG-файла (Enter для '{default}'): ",
        "prompt_u18": "Добавить эмодзи Unicode 17.0 и 18.0? [1 = Да (По умолчанию), 2 = Только флаги]: ",
        "prompt_bg": "Выберите фон [1 = Белый (По умолчанию), 2 = Темный, 3 = Прозрачный]: ",
        "err_missing": "[ОШИБКА] Файл шрифта не найден: {path}",
        "info_font": "[*] Шрифт      : {path}",
        "info_size": "[*] Разрешение : {w}x{h} px ({rows} строк x {cols} столбцов)",
        "info_match": "[*] Отображено : {matched}/{total} эмодзи совпали с GSUB/CMAP",
        "done_msg": "[ГОТОВО] Превью сохранено: {out} ({kb:.1f} КБ)",
        "next_action": "\nЧто вы хотите сделать дальше?\n  (1) Вернуться в главное меню\n  (0) Выйти из программы\nВаш выбор (1/0): ",
        "bye": "До свидания!",
    },
}

ISO_REGIONS = [
    "AC", "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ",
    "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS", "BT", "BV", "BW", "BY", "BZ",
    "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN", "CO", "CP", "CQ", "CR", "CU", "CV", "CW", "CX", "CY", "CZ",
    "DE", "DG", "DJ", "DK", "DM", "DO", "DZ",
    "EA", "EC", "EE", "EG", "EH", "ER", "ES", "ET", "EU",
    "FI", "FJ", "FK", "FM", "FO", "FR",
    "GA", "GB", "GD", "GE", "GF", "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY",
    "HK", "HM", "HN", "HR", "HT", "HU",
    "IC", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT",
    "JE", "JM", "JO", "JP",
    "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ",
    "LA", "LB", "LC", "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY",
    "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK", "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ",
    "NA", "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ",
    "OM",
    "PA", "PE", "PF", "PG", "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY",
    "QA",
    "RE", "RO", "RS", "RU", "RW",
    "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS", "ST", "SV", "SX", "SY", "SZ",
    "TA", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO", "TR", "TT", "TV", "TW", "TZ",
    "UA", "UG", "UM", "UN", "US", "UY", "UZ",
    "VA", "VC", "VE", "VG", "VI", "VN", "VU",
    "WF", "WS",
    "XK",
    "YE", "YT",
    "ZA", "ZM", "ZW",
]
SUBDIVISION_FLAGS = [
    "\U0001F3F4\U000E0067\U000E0062\U000E0065\U000E006E\U000E0067\U000E007F",  # England
    "\U0001F3F4\U000E0067\U000E0062\U000E0073\U000E0063\U000E0074\U000E007F",  # Scotland
    "\U0001F3F4\U000E0067\U000E0062\U000E0077\U000E006C\U000E0073\U000E007F",  # Wales
]

U17_SHOWCASE = [
    "\U0001FAEA", "\U0001FAEF", "\U0001FAC8", "\U0001FACD", "\U0001F6D8", "\U0001FA8A", "\U0001FA8E",
    "\U0001F9D1\u200D\U0001FA70",
    "\U0001F9D1\U0001F3FB\u200D\U0001FA70",
    "\U0001F9D1\U0001F3FC\u200D\U0001FA70",
    "\U0001F9D1\U0001F3FD\u200D\U0001FA70",
    "\U0001F9D1\U0001F3FE\u200D\U0001FA70",
    "\U0001F9D1\U0001F3FF\u200D\U0001FA70",
]

U18_SHOWCASE = [
    "\U0001FAEB", "\U0001FACC", "\U0001FADD", "\U0001F6D9", "\U0001FA8B", "\U0001FA8C", "\U0001FA8D",
    "\U0001FAF9", "\U0001FAF9\U0001F3FB", "\U0001FAF9\U0001F3FC", "\U0001FAF9\U0001F3FD", "\U0001FAF9\U0001F3FE", "\U0001FAF9\U0001F3FF",
    "\U0001FAFA", "\U0001FAFA\U0001F3FB", "\U0001FAFA\U0001F3FC", "\U0001FAFA\U0001F3FD", "\U0001FAFA\U0001F3FE", "\U0001FAFA\U0001F3FF",
]



def code_to_flag(code):
    return "".join(chr(0x1F1E6 + ord(ch) - ord("A")) for ch in code)


def build_ligature_index(ttfont):
    lig_map = {}
    if "GSUB" not in ttfont:
        return lig_map

    gsub = ttfont["GSUB"].table
    if not gsub.LookupList:
        return lig_map

    for lookup in gsub.LookupList.Lookup:
        subtables = []
        if lookup.LookupType == 4:
            subtables = lookup.SubTable
        elif lookup.LookupType == 7:
            for ext in lookup.SubTable:
                if getattr(ext, "ExtensionLookupType", None) == 4:
                    subtables.append(ext.ExtSubTable)

        for st in subtables:
            ligs = getattr(st, "ligatures", None) or {}
            for first, records in ligs.items():
                for rec in records:
                    seq = (first, *rec.Component)
                    if seq not in lig_map:
                        lig_map[seq] = rec.LigGlyph
    return lig_map


def resolve_sequence_glyph(gnames, lig_map):
    seq = list(gnames)
    changed = True
    while changed and len(seq) > 1:
        changed = False
        for i in range(len(seq)):
            for length in range(len(seq) - i, 1, -1):
                sub = tuple(seq[i : i + length])
                if sub in lig_map:
                    seq = seq[:i] + [lig_map[sub]] + seq[i + length :]
                    changed = True
                    break
            if changed:
                break
    return next(iter(seq)) if len(seq) == 1 else None


def render_grid(font_path, output_png, cols=24, icon_size=72, gap_x=28, gap_y=20, padding=24, bg_mode="white", tier="u18", lang="en"):
    txt = LANG_PACK.get(lang, LANG_PACK["en"])
    if not os.path.isfile(font_path):
        raise FileNotFoundError(txt["err_missing"].format(path=font_path))

    tt = TTFont(font_path, lazy=False)
    cmap = tt.getBestCmap() or {}
    lig_map = build_ligature_index(tt)

    items = [code_to_flag(c) for c in ISO_REGIONS] + SUBDIVISION_FLAGS
    if tier in ("u17", "u18"):
        items.extend(U17_SHOWCASE)
    if tier == "u18":
        items.extend(U18_SHOWCASE)


    resolved_gids = []
    matched_count = 0

    for seq_str in items:
        gnames = tuple(cmap.get(ord(ch)) for ch in seq_str)
        if any(g is None for g in gnames):
            resolved_gids.append(None)
            continue

        if len(gnames) == 1:
            resolved_gids.append(tt.getGlyphID(next(iter(gnames))))
            matched_count += 1
        else:
            target_glyph = resolve_sequence_glyph(gnames, lig_map)
            if target_glyph:
                resolved_gids.append(tt.getGlyphID(target_glyph))
                matched_count += 1
            else:
                resolved_gids.append(tt.getGlyphID(next(iter(gnames))))

    tt.close()

    typeface = skia.Typeface.MakeFromFile(font_path)
    if typeface is None:
        raise RuntimeError(f"Skia cannot open font: {font_path}")

    sk_font = skia.Font(typeface, float(icon_size))
    sk_font.setEdging(skia.Font.Edging.kAntiAlias)

    total = len(resolved_gids)
    rows = (total + cols - 1) // cols

    cell_w = icon_size + gap_x
    cell_h = icon_size + gap_y
    canvas_w = padding * 2 + cols * cell_w - gap_x
    canvas_h = padding * 2 + rows * cell_h - gap_y

    info = skia.ImageInfo.Make(canvas_w, canvas_h, skia.ColorType.kRGBA_8888_ColorType, skia.AlphaType.kPremul_AlphaType)
    surface = skia.Surface.MakeRaster(info)
    canvas = surface.getCanvas()

    if bg_mode == "transparent":
        canvas.clear(skia.ColorTRANSPARENT)
    elif bg_mode == "dark":
        canvas.clear(skia.ColorSetRGB(24, 26, 31))
    else:
        canvas.clear(skia.ColorWHITE)

    paint = skia.Paint(AntiAlias=True)
    metrics = sk_font.getMetrics()
    baseline_offset = -metrics.fAscent * 0.92

    print("=" * 72)
    print(txt["info_font"].format(path=font_path))
    print(txt["info_size"].format(w=canvas_w, h=canvas_h, rows=rows, cols=cols))
    print(txt["info_match"].format(matched=matched_count, total=total))
    print("=" * 72)

    for idx, gid in enumerate(resolved_gids):
        if gid is None:
            continue
        r = idx // cols
        c = idx % cols

        x = float(padding + c * cell_w)
        y = float(padding + r * cell_h + baseline_offset)

        blob = skia.TextBlob.MakeFromText(bytes([gid & 0xFF, (gid >> 8) & 0xFF]), sk_font, skia.TextEncoding.kGlyphID)
        if blob is not None:
            canvas.drawTextBlob(blob, x, y, paint)

    img = surface.makeImageSnapshot()
    img.save(output_png, skia.kPNG)
    print(txt["done_msg"].format(out=output_png, kb=os.path.getsize(output_png) / 1024))


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

        def_font = "seguiemj_3d_win11.ttf" if os.path.isfile("seguiemj_3d_win11.ttf") else "seguiemj.ttf"
        font_in = input(txt["prompt_font"].format(default=def_font)).strip().strip('"') or def_font

        u18_in = input(txt["prompt_u18"]).strip()
        inc_u18 = (u18_in != "2")

        bg_in = input(txt["prompt_bg"]).strip()
        bg_mode = "dark" if bg_in == "2" else ("transparent" if bg_in == "3" else "white")

        def_out = "full_showcase.png" if inc_u18 else "flags_showcase.png"
        out_in = input(txt["prompt_out"].format(default=def_out)).strip().strip('"') or def_out

        print("-" * 72)
        try:
            render_grid(font_in, out_in, bg_mode=bg_mode, tier=("u18" if inc_u18 else "flags"), lang=lang)
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
        parser = argparse.ArgumentParser(description="Render 262 Flags + Full U17/U18 Showcase Grid")
        parser.add_argument("font", help="Input font file (e.g. seguiemj_win11_hybrid.ttf)")
        parser.add_argument("output", nargs="?", default="flags_showcase.png", help="Output PNG path")
        parser.add_argument("--cols", type=int, default=24, help="Columns per row (Default: 24)")
        parser.add_argument("--size", type=int, default=72, help="Icon size in px (Default: 72)")
        parser.add_argument("--bg", choices=["white", "dark", "transparent"], default="white", help="Background color")
        parser.add_argument("--tier", choices=["flags", "u17", "u18"], default="flags", help="Showcase tier: flags, u17, or u18")
        parser.add_argument("--include-u17-u18", action="store_true", help="Alias for --tier u18")
        parser.add_argument("--lang", choices=["en", "vi", "zh", "ru"], default="en", help="UI language")
        args = parser.parse_args()

        selected_tier = "u18" if args.include_u17_u18 else args.tier
        try:
            render_grid(args.font, args.output, args.cols, args.size, bg_mode=args.bg, tier=selected_tier, lang=args.lang)
        except Exception as exc:
            print(f"\n[FAILED] {type(exc).__name__}: {exc}")
            sys.exit(1)

