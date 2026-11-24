# merge_emoji_into_honor_font_pro.py - Fix triet de VS16 (cmap Format 14) cho ban phim Honor/MagicOS
"""
merge_emoji_into_honor_font.py (v2.1)
=======================================
Nhúng bộ emoji Windows 11 + cờ quốc gia vào font hệ thống Honor MagicOS
- Trích xuất font gốc từ file .hwt của zFont 3
- Sao chép toàn bộ ảnh CBDT + quy tắc ZWJ/ligature từ font emoji nguồn
- Tự động đồng bộ VS16 (FE0F) → sửa lỗi thiếu emoji trên di động
- Đóng gói lại thành file .hwt hoàn chỉnh
- An toàn với MagicOS 8+

1. python colr2cbdt_3d_skia.py seguiemj.ttf seguiemj_3d.ttf (Xuất chuẩn màu vàng 3D tròn trịa, không cắt viền).
2. python add_emoji_smart_cbdt.py seguiemj_3d.ttf NotoColorEmoji.ttf Twemoji.Mozilla_cbdt.ttf seguiemj_3d_final.ttf
3. python merge_emoji_into_honor_font.py template.hwt seguiemj_3d_final.ttf Win11_3D_Honor.hwt

"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# merge_emoji_into_honor_font.py (Phần 1/3)
# [EN] Interactive Multi-Language Honor/Huawei .hwt Emoji Theme Builder
# [VI] Công cụ đóng gói Theme Emoji .hwt cho Honor/Huawei đa ngôn ngữ (Anh/Việt/Trung/Nga)
# [ZH] 荣耀/华为 MagicOS/EMUI 彩色表情主题 (.hwt) 多语言交互式打包工具
# [RU] Интерактивный мультиязычный сборщик тем эмодзи .hwt для Honor/Huawei
# ============================================================================
# ============================================================================
# CLI ARGUMENTS / THAM SỐ DÒNG LỆNH / 命令行参数 / ПАРАМЕТРЫ КОМАНДНОЙ СТРОКИ:
#
# [EN] Usage: python merge_emoji_into_honor_font.py <template.hwt> <emoji.ttf> [output.hwt] [options]
#   template.hwt          : Base Honor/Huawei theme package containing system font
#   emoji.ttf             : Patched CBDT/CBLC emoji font (3D or 2D with 262 flags & U17/U18)
#   output.hwt            : Output .hwt theme path (default: Win11_3D_Honor.hwt)
#   --lang {en,vi,zh,ru}  : Console log language (default: en)
#
# [VI] Cách dùng: python merge_emoji_into_honor_font.py <mẫu.hwt> <emoji.ttf> [đích.hwt] [tùy chọn]
#   mẫu.hwt               : File theme .hwt mẫu của Honor/Huawei chứa font hệ thống gốc
#   emoji.ttf             : File font emoji CBDT/CBLC đã vá đủ 262 cờ & U17/U18 (3D hoặc 2D)
#   đích.hwt              : Tên file theme .hwt đầu ra (mặc định: Win11_3D_Honor.hwt)
#   --lang {en,vi,zh,ru}  : Ngôn ngữ hiển thị log (mặc định: en)
#
# [ZH] 用法: python merge_emoji_into_honor_font.py <模板.hwt> <表情.ttf> [输出.hwt] [选项]
#   模板.hwt              : 包含原始系统字体的荣耀/华为 .hwt 主题模板文件
#   表情.ttf              : 已修补 262 面国旗与 U17/U18 的 CBDT/CBLC 表情字体 (3D 或 2D)
#   输出.hwt              : 输出的 .hwt 主题文件名 (默认: Win11_3D_Honor.hwt)
#   --lang {en,vi,zh,ru}  : 终端日志语言 (默认: en)
#
# [RU] Использование: python merge_emoji_into_honor_font.py <шаблон.hwt> <шрифт.ttf> [выход.hwt] [опции]
#   шаблон.hwt            : Базовый шаблон темы Honor/Huawei с системным шрифтом
#   шрифт.ttf             : Пропатченный шрифт эмодзи CBDT/CBLC с 262 флагами и U17/U18
#   выход.hwt             : Имя выходной темы .hwt (по умолчанию: Win11_3D_Honor.hwt)
#   --lang {en,vi,zh,ru}  : Язык логов в консоли (по умолчанию: en)
# ============================================================================

import os
import sys
import time
import copy
import zipfile
import argparse
import subprocess
import importlib.util

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
    if importlib.util.find_spec("fontTools") is None:
        print("[*] Installing missing package: fonttools...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "fonttools"])


ensure_packages()

from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import C_B_D_T_, otTables
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables._g_l_y_f import Glyph
from fontTools.ttLib.tables.E_B_L_C_ import eblc_index_sub_table_1

# [EN] 4-Language UI & Help Dictionary | [VI] Từ điển giao diện & hướng dẫn 4 ngôn ngữ
# [ZH] 四语言界面与帮助说明字典       | [RU] Словарь интерфейса и справки на 4 языках
LANG_PACK = {
    "en": {
        "label": "🇺🇸 English",
        "banner": "HONOR / HUAWEI .HWT THEME PACKAGER PRO v2 (3D & 2D + VS16 FIX)",
        "help_title": "TOOL OVERVIEW & USAGE:",
        "help_lines": [
            "1. Injects full Windows 11 emojis, 262 flags & Unicode 17.0/18.0 into Honor system font.",
            "2. Syncs VS16 (U+FE0F) cmap Format 14 so keyboard emojis (❤️, 🏋️, ✈️...) never show blank.",
            "3. Packages into an uncompressed (ZIP_STORED) .hwt theme ready for MagicOS / EMUI.",
            "4. CLI mode: python merge_emoji_into_honor_font_pro2.py <template.hwt> <emoji.ttf> [out.hwt]",
        ],
        "prompt_tpl": "Enter template .hwt path (Enter for '{default}'): ",
        "prompt_emj": "Enter patched emoji .ttf path (Enter for '{default}'): ",
        "prompt_out": "Enter output .hwt theme name (Enter for '{default}'): ",
        "err_missing": "[ERROR] File not found: {path}",
        "err_limit": "[ERROR] Exceeded 65,535 glyph limit ({count})!",
        "step_extract": "[*] Extracting base system font from {tpl}...",
        "step_merge": "[*] Merging Win11 emojis, 262 flags & VS16 (Format 14) into Honor font...",
        "info_stats": "[*] Integrated {bmp} bitmaps ({vs16} VS16 Format 14 synced) & {gsub} GSUB rules.",
        "info_glyphs": "[*] Total Honor font glyphs: {count} / 65535",
        "step_pack": "[*] Packaging {out} (Theme Title: {title})...",
        "done_msg": "[SUCCESS] Done in {sec:.2f}s! Theme ready: {out} ({mb:.2f} MB)",
        "next_action": "\nNext step:\n  (1) Return to main menu\n  (0) Exit program\nYour choice (1/0): ",
        "bye": "Goodbye! Copy the .hwt file to Honor/Themes and apply in Themes app!",
    },
    "vi": {
        "label": "🇻🇳 Tiếng Việt (Vietnamese)",
        "banner": "CÔNG CỤ ĐÓNG GÓI THEME .HWT CHO HONOR / HUAWEI PRO v2 (3D & 2D + FIX VS16)",
        "help_title": "GIỚI THIỆU CÔNG DỤNG & CÁCH DÙNG:",
        "help_lines": [
            "1. Cấy trọn bộ emoji Win 11, 262 quốc kỳ & Full U17/U18 vào font hệ thống Honor/Huawei.",
            "2. Đồng bộ chuẩn VS16 (cmap Format 14) giúp bàn phím hiển thị đủ ❤️, 🏋️, ✈️ không bị trống.",
            "3. Tự động đổi tên chủ đề & nén chuẩn ZIP_STORED tương thích 100% MagicOS 8 / EMUI.",
            "4. Hỗ trợ chạy dòng lệnh (CLI): python merge_emoji_into_honor_font_pro2.py <mẫu.hwt> <emoji.ttf> [đích.hwt]",
        ],
        "prompt_tpl": "Nhập đường dẫn file .hwt mẫu (Enter để dùng '{default}'): ",
        "prompt_emj": "Nhập đường dẫn file font emoji đã vá (Enter để dùng '{default}'): ",
        "prompt_out": "Nhập tên file .hwt đầu ra (Enter để dùng '{default}'): ",
        "err_missing": "[LỖI] Không tìm thấy file: {path}",
        "err_limit": "[LỖI] Vượt quá giới hạn 65.535 glyph của hệ thống ({count})!",
        "step_extract": "[*] Đang trích xuất font hệ thống gốc từ {tpl}...",
        "step_merge": "[*] Đang nhúng toàn bộ emoji Win 11, 262 cờ & VS16 (Format 14) vào font Honor...",
        "info_stats": "[*] Đã tích hợp {bmp} ảnh bitmap (đồng bộ {vs16} VS16 Format 14) & {gsub} quy tắc GSUB.",
        "info_glyphs": "[*] Tổng số glyph trong font Honor: {count} / 65535",
        "step_pack": "[*] Đang đóng gói thành {out} (Tên chủ đề: {title})...",
        "done_msg": "[THÀNH CÔNG] Xong trong {sec:.2f} giây! File theme mới: {out} ({mb:.2f} MB)",
        "next_action": "\nBạn muốn làm gì tiếp theo?\n  (1) Quay lại menu chính\n  (0) Thoát chương trình\nLựa chọn của bạn (1/0): ",
        "bye": "Tạm biệt! Hãy chép file .hwt vào thư mục Honor/Themes và áp dụng nhé!",
    },
    "zh": {
        "label": "🇨🇳 中文 (Chinese)",
        "banner": "荣耀 / 华为 .HWT 彩色表情主题打包工具 PRO v2 (3D & 2D + VS16 修复)",
        "help_title": "工具功能与使用说明：",
        "help_lines": [
            "1. 将 Windows 11 完整表情、262 面国旗及 Unicode 17.0/18.0 注入荣耀/华为系统字体。",
            "2. 同步 VS16 (cmap Format 14)，彻底解决输入法键盘中 ❤️、🏋️、✈️ 显示空白的问题。",
            "3. 自动修改主题名称并以 ZIP_STORED 无压缩打包，完美适配 MagicOS / EMUI。",
            "4. 命令行模式 (CLI): python merge_emoji_into_honor_font_pro2.py <模板.hwt> <表情.ttf> [输出.hwt]",
        ],
        "prompt_tpl": "请输入模板 .hwt 文件路径 (回车使用 '{default}'): ",
        "prompt_emj": "请输入已修补的表情 .ttf 路径 (回车使用 '{default}'): ",
        "prompt_out": "请输入输出 .hwt 主题文件名 (回车使用 '{default}'): ",
        "err_missing": "[错误] 找不到文件: {path}",
        "err_limit": "[错误] 超出系统 65,535 字形上限 ({count})！",
        "step_extract": "[*] 正在从 {tpl} 提取原始系统字体...",
        "step_merge": "[*] 正在将 Win11 表情、262 国旗及 VS16 (Format 14) 嵌入荣耀字体...",
        "info_stats": "[*] 已集成 {bmp} 张位图 (同步 {vs16} 个 VS16 Format 14) 及 {gsub} 条 GSUB 规则。",
        "info_glyphs": "[*] 荣耀字体总字形数: {count} / 65535",
        "step_pack": "[*] 正在打包生成 {out} (主题名称: {title})...",
        "done_msg": "[成功] 耗时 {sec:.2f} 秒完成！新主题文件: {out} ({mb:.2f} MB)",
        "next_action": "\n接下来您想做什么？\n  (1) 返回主菜单继续打包\n  (0) 退出程序\n请输入选项 (1/0): ",
        "bye": "再见！请将 .hwt 文件复制到 Honor/Themes 目录并在主题应用中启用！",
    },
    "ru": {
        "label": "🇷🇺 Русский (Russian)",
        "banner": "СБОРЩИК ТЕМ .HWT ДЛЯ HONOR / HUAWEI PRO v2 (3D & 2D + ФИКС VS16)",
        "help_title": "ОПИСАНИЕ И СПОСОБЫ ЗАПУСКА:",
        "help_lines": [
            "1. Внедряет эмодзи Win 11, 262 флага и полный Unicode 17.0/18.0 в системный шрифт Honor.",
            "2. Синхронизирует VS16 (cmap Format 14), исправляя пустые символы ❤️, 🏋️, ✈️ на клавиатуре.",
            "3. Упаковывает в тему .hwt без сжатия (ZIP_STORED) для MagicOS 8 / EMUI.",
            "4. Режим CLI: python merge_emoji_into_honor_font_pro2.py <шаблон.hwt> <шрифт.ttf> [выход.hwt]",
        ],
        "prompt_tpl": "Введите путь к шаблону .hwt (Enter для '{default}'): ",
        "prompt_emj": "Введите путь к шрифту эмодзи .ttf (Enter для '{default}'): ",
        "prompt_out": "Введите имя выходной темы .hwt (Enter для '{default}'): ",
        "err_missing": "[ОШИБКА] Файл не найден: {path}",
        "err_limit": "[ОШИБКА] Превышен лимит в 65 535 глифов ({count})!",
        "step_extract": "[*] Извлечение системного шрифта из {tpl}...",
        "step_merge": "[*] Внедрение эмодзи Win 11, 262 флагов и VS16 (Format 14) в шрифт Honor...",
        "info_stats": "[*] Интегрировано {bmp} битмапов (синхр. {vs16} VS16 Format 14) и {gsub} правил GSUB.",
        "info_glyphs": "[*] Всего глифов в шрифте Honor: {count} / 65535",
        "step_pack": "[*] Упаковка {out} (Название темы: {title})...",
        "done_msg": "[ГОТОВО] Завершено за {sec:.2f} сек! Тема готова: {out} ({mb:.2f} МБ)",
        "next_action": "\nЧто вы хотите сделать дальше?\n  (1) Вернуться в главное меню\n  (0) Выйти из программы\nВаш выбор (1/0): ",
        "bye": "До свидания! Скопируйте файл .hwt в папку Honor/Themes и примените его!",
    },
}
# [EN] Group consecutive GlyphIDs for compact EBLC index subtables
# [VI] Gom nhóm các GlyphID liền mạch để tạo bảng chỉ mục EBLC gọn nhẹ
# [ZH] 将连续的 GlyphID 分组以生成紧凑的 EBLC 索引子表
# [RU] Группировка последовательных GlyphID для компактных подтаблиц EBLC
def group_consecutive(items):
    if not items:
        return []
    groups, it = [], iter(items)
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


# [EN] Extract all GSUB ligature rules (LookupType 4 and Extension LookupType 7)
# [VI] Trích xuất toàn bộ quy tắc tổ hợp GSUB (LookupType 4 và Extension LookupType 7)
# [ZH] 提取所有 GSUB 连字规则 (LookupType 4 与扩展 LookupType 7)
# [RU] Извлечение всех правил лигатур GSUB (LookupType 4 и Extension LookupType 7)
def extract_ligatures(font):
    rules = []
    if "GSUB" not in font or not font["GSUB"].table.LookupList:
        return rules
    for lookup in font["GSUB"].table.LookupList.Lookup:
        subs = [getattr(s, "ExtSubTable", s) for s in lookup.SubTable] if lookup.LookupType == 7 else lookup.SubTable
        for st in subs:
            for first, records in (getattr(st, "ligatures", None) or {}).items():
                for rec in records:
                    rules.append((first, list(rec.Component), rec.LigGlyph))
    return rules


# [EN] Extract VS16 (U+FE0F) color variants from cmap Format 14 & GSUB for Mobile keyboards
# [VI] Trích xuất biến thể màu VS16 (U+FE0F) từ cmap Format 14 & GSUB cho bàn phím di động
# [ZH] 从 cmap Format 14 和 GSUB 提取 VS16 (U+FE0F) 彩色变体以适配手机键盘
# [RU] Извлечение цветных вариантов VS16 (U+FE0F) из cmap Format 14 и GSUB для клавиатур
def extract_vs16_color_map(emoji_font, emoji_cmap, lig_rules):
    if "CBDT" not in emoji_font:
        return {}
    cbdt_keys = set(next(iter(emoji_font["CBDT"].strikeData)).keys())
    rev_cmap = {v: k for k, v in emoji_cmap.items()}
    direct_map = {}

    for table in emoji_font["cmap"].tables:
        if table.format == 14 and hasattr(table, "uvsDict"):
            for cp, var_gname in table.uvsDict.get(0xFE0F, []):
                actual_gname = var_gname or emoji_cmap.get(cp)
                if actual_gname and actual_gname in cbdt_keys:
                    direct_map[cp] = actual_gname

    vs16_name = emoji_cmap.get(0xFE0F)
    if vs16_name:
        for first, comps, lig_glyph in lig_rules:
            if comps == list((vs16_name,)) and lig_glyph in cbdt_keys and first in rev_cmap:
                direct_map[rev_cmap[first]] = lig_glyph

    return direct_map


# [EN] Main packaging routine: inject emoji font into Honor .hwt system font
# [VI] Hàm đóng gói chính: nhúng font emoji vào font hệ thống Honor .hwt
# [ZH] 核心打包流程：将彩色表情字体嵌入荣耀系统字体并封装为 .hwt 主题
# [RU] Основная функция упаковки: внедрение шрифта эмодзи в системный шрифт Honor .hwt
def merge_emoji_into_hwt(template_hwt, emoji_ttf, out_hwt="Win11_3D_Pro3_Honor.hwt", lang="en"):
    import shutil
    import tempfile

    t0 = time.time()
    txt = LANG_PACK.get(lang, LANG_PACK["en"])

    if not os.path.isfile(template_hwt):
        raise FileNotFoundError(txt["err_missing"].format(path=template_hwt))
    if not os.path.isfile(emoji_ttf):
        raise FileNotFoundError(txt["err_missing"].format(path=emoji_ttf))

    tmp_dir = tempfile.mkdtemp(prefix="honor_emoji_")
    temp_base = os.path.join(tmp_dir, "_temp_base_honor.ttf")
    temp_merged = os.path.join(tmp_dir, "_temp_merged_honor.ttf")

    try:
        print(txt["step_extract"].format(tpl=template_hwt))
        with zipfile.ZipFile(template_hwt, "r") as zin:
            with open(temp_base, "wb") as f:
                f.write(zin.read("fonts/DroidSansChinese.ttf"))

        base_font = TTFont(temp_base, lazy=False)
        emoji_font = TTFont(emoji_ttf, lazy=False)

        print(txt["step_merge"])
        base_order = list(base_font.getGlyphOrder())
        base_set = set(base_order)
        base_cmap = base_font.getBestCmap() or {}
        emoji_cmap = emoji_font.getBestCmap() or {}
        lig_rules = extract_ligatures(emoji_font)
        vs16_direct = extract_vs16_color_map(emoji_font, emoji_cmap, lig_rules)

        glyf = base_font["glyf"]
        hmtx = base_font["hmtx"].metrics
        upm = base_font["head"].unitsPerEm

        target_adv = upm
        for probe in (0x1F600, 0x1F602, 0x2764):
            gname = base_cmap.get(probe)
            if gname and gname in hmtx:
                adv_w, _ = hmtx[gname]
                if adv_w > 0:
                    target_adv = int(adv_w)
                    break

        for tag in ("CBDT", "CBLC", "COLR", "CPAL", "sbix", "SVG "):
            if tag in base_font:
                del base_font[tag]

        name_map = {}

        def get_or_add_glyph(egname, zero_width=False):
            if egname in name_map:
                return name_map[egname]
            cand = "w11_" + egname
            idx = 1
            while cand in base_set:
                cand = f"w11_{egname}_{idx}"
                idx += 1
            base_set.add(cand)
            base_order.append(cand)
            name_map[egname] = cand
            g = Glyph()
            g.numberOfContours = 0
            g.xMin = g.yMin = g.xMax = g.yMax = 0
            glyf[cand] = g
            hmtx[cand] = (0 if zero_width else target_adv, 0)
            return cand

        # Các ký tự mũi tên, dấu gạch ngang & dấu câu — gỡ hẳn khỏi cmap để hệ thống tự fallback (giống theme Apple)
        FALLBACK_CHARS = {
            0x2190, 0x2191, 0x2192, 0x2193, 0x2194, 0x2195,  # ← ↑ → ↓ ↔ ↕
            0x2196, 0x2197, 0x2198, 0x2199,                 # ↖ ↗ ↘ ↙
            0x21A9, 0x21AA,                                 # ↩ ↪
            0x21D0, 0x21D1, 0x21D2, 0x21D3,                 # ⇐ ⇑ ⇒ ⇓
            0x21E6, 0x21E7, 0x21E8, 0x21E9,                 # ⇦ ⇧ ⇨ ⇩
            0x2794, 0x2798, 0x2799, 0x279A,                 # ➔ ➘ ➙ ➚
            0x279E, 0x279F, 0x27A0, 0x27A4,                 # ➞ ➟ ➠ ➤
            0x2012, 0x2013, 0x2014, 0x2015,                 # ‒ – — ―
            0x2500, 0x2501, 0x2504, 0x2505, 0x2508, 0x2509, # ─ ━ ┄ ┅ ┈ ┉
            0x2039, 0x203A, 0x00AB, 0x00BB,                 # ‹ › « »
            0x2018, 0x2019, 0x201C, 0x201D,                 # ‘ ’ “ ”
            0x2026, 0x2022,                                 # … •
        }

        vs16_direct = {cp: g for cp, g in vs16_direct.items() if cp not in FALLBACK_CHARS}
        zw_names = {emoji_cmap[c] for c in (0x200D, 0xFE0F) if c in emoji_cmap}
        effective_cmap = dict(emoji_cmap)
        effective_cmap.update(vs16_direct)

        for cp, egname in effective_cmap.items():
            if cp in FALLBACK_CHARS:
                continue
            if cp < 0x2000 and cp not in (0x00A9, 0x00AE):
                continue
            is_zw = (cp in (0x200D, 0xFE0F) or (0xE0020 <= cp <= 0xE007F))
            dest_gname = get_or_add_glyph(egname, zero_width=is_zw)
            for table in base_font["cmap"].tables:
                if table.isUnicode() and table.format in (4, 12) and getattr(table, "cmap", None) is not None:
                    if table.format == 4 and cp > 0xFFFF:
                        continue
                    table.cmap[cp] = dest_gname
        if vs16_direct:
            base_font["cmap"].tables = [t for t in base_font["cmap"].tables if t.format != 14]
            sub14 = CmapSubtable.newSubtable(14)
            sub14.platformID = 0
            sub14.platEncID = 5
            sub14.language = 0
            sub14.cmap = {}
            sub14.uvsDict = {0xFE0F: [(cp, None) for cp in sorted(vs16_direct.keys())]}
            base_font["cmap"].tables.append(sub14)

        raw_to_eff = {}
        for cp, raw_gn in emoji_cmap.items():
            eff_gn = effective_cmap.get(cp)
            if eff_gn and eff_gn != raw_gn:
                raw_to_eff[raw_gn] = eff_gn

        mapped_rules, seen_rules = [], set()
        for first, comps, lig_glyph in lig_rules:
            variants = [([first], comps)]
            eff_first = raw_to_eff.get(first, first)
            eff_comps = [raw_to_eff.get(c, c) for c in comps]
            if [eff_first] + eff_comps != [first] + comps:
                variants.append(([eff_first], eff_comps))

            for v_first_list, v_comps in variants:
                d_first = get_or_add_glyph(v_first_list[0], zero_width=(v_first_list[0] in zw_names))
                d_comps = [get_or_add_glyph(c, zero_width=(c in zw_names)) for c in v_comps]
                d_lig = get_or_add_glyph(lig_glyph)
                key = (d_first, tuple(d_comps))
                if key not in seen_rules:
                    seen_rules.add(key)
                    mapped_rules.append((d_first, d_comps, d_lig))

        if 0xFE0F in emoji_cmap:
            d_vs16 = get_or_add_glyph(emoji_cmap[0xFE0F], zero_width=True)
            for color_egname in set(vs16_direct.values()):
                d_color = get_or_add_glyph(color_egname)
                key = (d_color, (d_vs16,))
                if key not in seen_rules:
                    seen_rules.add(key)
                    mapped_rules.append((d_color, [d_vs16], d_color))

        if len(base_order) > 65535:
            raise RuntimeError(txt["err_limit"].format(count=len(base_order)))

        emoji_strike = next(iter(emoji_font["CBLC"].strikes))
        emoji_cbdt = next(iter(emoji_font["CBDT"].strikeData))
        ppem = emoji_strike.bitmapSizeTable.ppemY
        px_adv = max(1, min(255, round(target_adv * ppem / upm)))

        new_cbdt_data, valid_bitmap_names = {}, []
        for egname, dgname in name_map.items():
            if egname in emoji_cbdt:
                src_bmp = emoji_cbdt[egname]
                new_bmp = C_B_D_T_.cbdt_bitmap_format_17(data=b"", ttFont=base_font)
                new_bmp.metrics = C_B_D_T_.SmallGlyphMetrics()
                new_bmp.metrics.height = src_bmp.metrics.height
                new_bmp.metrics.width = src_bmp.metrics.width
                new_bmp.metrics.BearingX = src_bmp.metrics.BearingX
                new_bmp.metrics.BearingY = src_bmp.metrics.BearingY
                new_bmp.metrics.Advance = px_adv
                new_bmp.imageData = src_bmp.imageData
                new_cbdt_data[dgname] = new_bmp
                valid_bitmap_names.append(dgname)

        base_font.setGlyphOrder(base_order)
        base_font["maxp"].numGlyphs = len(base_order)
        if "hhea" in base_font:
            base_font["hhea"].numberOfHMetrics = len(base_order)

        reverse = base_font.getReverseGlyphMap(rebuild=True)
        valid_pairs = sorted([(reverse[n], n) for n in valid_bitmap_names])
        first_gid, _ = next(iter(valid_pairs))
        last_gid, _ = valid_pairs[-1]

        cbdt = newTable("CBDT")
        cbdt.version = 3.0
        cbdt.strikeData = list((new_cbdt_data,))
        cblc = newTable("CBLC")
        cblc.version = 3.0
        strike = copy.deepcopy(emoji_strike)
        strike.bitmapSizeTable.startGlyphIndex = first_gid
        strike.bitmapSizeTable.endGlyphIndex = last_gid

        subtables = []
        for grp in group_consecutive(valid_pairs):
            gf, _ = next(iter(grp))
            gl, _ = grp[-1]
            sub = eblc_index_sub_table_1(None, base_font)
            sub.indexFormat = 1
            sub.imageFormat = 17
            sub.imageDataOffset = 0
            sub.names = [n for _, n in grp]
            sub.firstGlyphIndex = gf
            sub.lastGlyphIndex = gl
            sub.locations = []
            subtables.append(sub)

        strike.indexSubTables = subtables
        strike.bitmapSizeTable.numberOfIndexSubTables = len(subtables)
        cblc.strikes = list((strike,))
        base_font["CBDT"], base_font["CBLC"] = cbdt, cblc

        if mapped_rules and "GSUB" in base_font:
            gsub = base_font["GSUB"].table
            mapped_rules.sort(key=lambda rule: len(rule[1]), reverse=True)

            new_indices = []
            for i in range(0, len(mapped_rules), 800):
                lig_sub = otTables.LigatureSubst()
                lig_sub.ligatures = {}
                for d_first, d_comps, d_lig in mapped_rules[i:i + 800]:
                    rec = otTables.Ligature()
                    rec.Component = d_comps
                    rec.CompCount = len(d_comps) + 1
                    rec.LigGlyph = d_lig
                    lig_sub.ligatures.setdefault(d_first, []).append(rec)

                lookup = otTables.Lookup()
                lookup.LookupType = 4
                lookup.LookupFlag = 0
                lookup.SubTable = [lig_sub]
                lookup.SubTableCount = 1
                gsub.LookupList.Lookup.append(lookup)
                new_indices.append(len(gsub.LookupList.Lookup) - 1)

            gsub.LookupList.LookupCount = len(gsub.LookupList.Lookup)
            for fr in (gsub.FeatureList.FeatureRecord or []):
                if fr.FeatureTag in ("ccmp", "liga", "rlig"):
                    fr.Feature.LookupListIndex = new_indices + list(fr.Feature.LookupListIndex or [])
                    fr.Feature.LookupCount = len(fr.Feature.LookupListIndex)

        # Gỡ hẳn các ký tự mũi tên/gạch khỏi cmap → hệ thống tự fallback (giống theme Apple)
        for table in base_font["cmap"].tables:
            if table.isUnicode() and table.format in (4, 12) and getattr(table, "cmap", None):
                for cp in FALLBACK_CHARS:
                    table.cmap.pop(cp, None)

        print(txt["info_stats"].format(bmp=len(valid_pairs), vs16=len(vs16_direct), gsub=len(mapped_rules)))
        print(txt["info_glyphs"].format(count=len(base_order)))
        base_font.save(temp_merged)
        base_font.close()
        emoji_font.close()

        theme_title, _ = os.path.splitext(os.path.basename(out_hwt))
        print(txt["step_pack"].format(out=out_hwt, title=theme_title))
        with zipfile.ZipFile(template_hwt, "r") as zin, zipfile.ZipFile(out_hwt, "w", compression=zipfile.ZIP_STORED) as zout:
            for item in zin.infolist():
                if item.filename == "fonts/DroidSansChinese.ttf":
                    zout.write(temp_merged, "fonts/DroidSansChinese.ttf")
                elif item.filename == "description.xml":
                    xml = zin.read(item.filename).decode("utf-8", errors="ignore")
                    if "<title>" in xml and "</title>" in xml:
                        s, e = xml.index("<title>") + 7, xml.index("</title>")
                        xml = xml[:s] + theme_title + xml[e:]
                    zout.writestr(item, xml.encode("utf-8"))
                else:
                    zout.writestr(item, zin.read(item.filename))

        size_mb = os.path.getsize(out_hwt) / (1024 * 1024)
        print("=" * 72)
        print(txt["done_msg"].format(sec=time.time() - t0, out=out_hwt, mb=size_mb))
        print("=" * 72)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)



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

        def_tpl = "template.hwt"
        def_emj = "seguiemj_3d_pro6_final4.ttf"
        def_out = "Win11_3D_Pro4_Honor.hwt"

        tpl_in = input(txt["prompt_tpl"].format(default=def_tpl)).strip().strip('"') or def_tpl
        emj_in = input(txt["prompt_emj"].format(default=def_emj)).strip().strip('"') or def_emj
        out_in = input(txt["prompt_out"].format(default=def_out)).strip().strip('"') or def_out

        print("-" * 72)
        try:
            merge_emoji_into_hwt(tpl_in, emj_in, out_in, lang=lang)
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
        parser = argparse.ArgumentParser(description="Honor/Huawei .hwt Emoji Theme Packager Pro v2")
        parser.add_argument("template", help="Template .hwt file (e.g. template.hwt)")
        parser.add_argument("emoji", help="Patched emoji TTF (e.g. seguiemj_3d_pro6_final4.ttf)")
        parser.add_argument("output", nargs="?", default="Win11_3D_Pro4_Honor.hwt", help="Output .hwt path")
        parser.add_argument("--lang", choices=["en", "vi", "zh", "ru"], default="en", help="UI language")
        args = parser.parse_args()

        try:
            merge_emoji_into_hwt(args.template, args.emoji, args.output, lang=args.lang)
        except Exception as exc:
            print(f"\n[FAILED] {type(exc).__name__}: {exc}")
            sys.exit(1)
