#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================================
# make_apple_multistrike.py
# [EN] Interactive 4-Language Apple + Noto Ultra HD Multi-Strike CBDT Builder
# [VI] Công cụ tạo Font Emoji CBDT Đa Độ Phân Giải 8 Mức (20 -> 192px)
# [ZH] 多语言 Apple + Noto 超清多分辨率 (20 -> 192px) CBDT 表情字体生成器
# [RU] Интерактивный мультиязычный генератор многоразмерных шрифтов CBDT (20 -> 192px)
# ============================================================================
'''
### Quy trình 3 lệnh xuất trọn bộ **Ultra HD 8-Strike (`20, 32, 40, 48, 64, 96, 160, 192` px)**

```bash
# Bước 1: Render 1 lần ở đỉnh Ultra HD 192px + xóa sạch COLR/CPAL
python colr2cbdt_3d_skia.py seguiemj.ttf seguiemj_192_base.ttf --ppem 192 --strip-colr

# Bước 2: Bơm đủ 262 cờ + Full Unicode 18.0 ở chuẩn 192px
python add_emoji_smart_cbdt_pro.py seguiemj_192_base.ttf NotoColorEmoji.ttf Twemoji.Mozilla_cbdt.ttf seguiemj_192_final.ttf

# Bước 3: Xuất đủ 8 mức phân giải chuẩn Apple + Noto Ultra HD (20 -> 192px)
python make_apple_multistrike.py seguiemj_192_final.ttf Win11_Ultra8Strikes_3D.ttf
hạ cấp bản nhỏ hơn
python make_apple_multistrike.py seguiemj_192_final.ttf seguiemj_109_from192.ttf --strikes 109
'''
import io
import os
import sys
import copy
import time
import shutil
import argparse
import subprocess
import importlib.util
from concurrent.futures import ThreadPoolExecutor

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def ensure_packages():
    required = {"fontTools": "fonttools", "PIL": "pillow"}
    missing = [pkg for mod, pkg in required.items() if importlib.util.find_spec(mod) is None]
    if missing:
        print(f"[*] Installing missing packages: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", *missing])


ensure_packages()

from PIL import Image
from fontTools import ttLib
from fontTools.ttLib.tables import C_B_D_T_

ULTRA_8_STRIKES = (20, 32, 40, 48, 64, 96, 160, 192)
PNGQUANT_BIN = shutil.which("pngquant")

LANG_PACK = {
    "en": {
        "label": "🇺🇸 English",
        "banner": "APPLE + NOTO ULTRA HD 8-STRIKE CBDT BUILDER (20 -> 192px)",
        "help_title": "TOOL OVERVIEW & USAGE:",
        "help_lines": [
            "1. Strips COLR/CPAL tables for 100% pure bitmap rendering (like Apple Color Emoji).",
            "2. Downscales master 192px bitmaps in parallel into 8 crisp strikes: 20, 32, 40, 48, 64, 96, 160, 192 px.",
            "3. CLI: python make_apple_multistrike.py <master_192.ttf> <out.ttf> [--strikes 20,32,40,48,64,96,160,192]",
        ],
        "prompt_src": "Enter master 192px CBDT font path (Enter for '{default}'): ",
        "prompt_dst": "Enter output multi-strike font path (Enter for '{default}'): ",
        "prompt_stk": "Enter PPEM strikes (Enter for '{default}'): ",
        "err_missing": "[ERROR] File not found: {path}",
        "err_no_cbdt": "[ERROR] Input font must contain CBDT and CBLC tables!",
        "step_load": "[*] Loading master CBDT font: {path}...",
        "info_master": "[*] Master Strike : {ppem}px ({count} glyphs) | Compression: {comp}",
        "info_target": "[*] Target Strikes: {strikes}",
        "prog_reuse": "  [+] Strike {ppem:>3}px : Reused master strike directly.",
        "prog_gen": "  [*] Strike {ppem:>3}px : Resizing & compressing {count} bitmaps (scale={scale:.3f})...",
        "done_msg": "[SUCCESS] Done in {sec:.2f}s! Multi-strike font ready: {out} ({mb:.2f} MB)",
        "next_action": "\nNext step:\n  (1) Return to main menu\n  (0) Exit program\nYour choice (1/0): ",
        "bye": "Goodbye! Enjoy your Ultra HD 8-Strike 3D Emoji font!",
    },
    "vi": {
        "label": "🇻🇳 Tiếng Việt (Vietnamese)",
        "banner": "CÔNG CỤ TẠO FONT EMOJI ĐA ĐỘ PHÂN GIẢI 8 MỨC CHUẨN APPLE + NOTO (20 -> 192px)",
        "help_title": "GIỚI THIỆU CÔNG DỤNG & CÁCH DÙNG:",
        "help_lines": [
            "1. Xóa sạch bảng COLR/CPAL để hiển thị 100% ảnh bitmap 3D đồng nhất như Apple Color Emoji.",
            "2. Nội suy đa luồng từ bản gốc 192px ra đủ 8 mức sắc nét: 20, 32, 40, 48, 64, 96, 160, 192 px.",
            "3. CLI: python make_apple_multistrike.py <nguồn_192.ttf> <đích.ttf> [--strikes 20,32,40,48,64,96,160,192]",
        ],
        "prompt_src": "Nhập đường dẫn font gốc 192px (Enter để dùng '{default}'): ",
        "prompt_dst": "Nhập tên file font đa độ phân giải đầu ra (Enter để dùng '{default}'): ",
        "prompt_stk": "Nhập các mức PPEM cách nhau dấu phẩy (Enter để dùng '{default}'): ",
        "err_missing": "[LỖI] Không tìm thấy file: {path}",
        "err_no_cbdt": "[LỖI] Font đầu vào không chứa bảng CBDT và CBLC!",
        "step_load": "[*] Đang nạp font CBDT gốc: {path}...",
        "info_master": "[*] Mức gốc (Master): {ppem}px ({count} glyphs) | Bộ nén: {comp}",
        "info_target": "[*] Các mức xuất ra : {strikes}",
        "prog_reuse": "  [+] Mức {ppem:>3}px : Giữ nguyên trực tiếp từ bản gốc.",
        "prog_gen": "  [*] Mức {ppem:>3}px : Đang thu phóng & nén đa luồng {count} ảnh (tỷ lệ={scale:.3f})...",
        "done_msg": "[THÀNH CÔNG] Hoàn tất trong {sec:.2f} giây! Đã lưu: {out} ({mb:.2f} MB)",
        "next_action": "\nBạn muốn làm gì tiếp theo?\n  (1) Quay lại menu chính\n  (0) Thoát chương trình\nLựa chọn của bạn (1/0): ",
        "bye": "Tạm biệt! Chúc bạn trải nghiệm bộ font Ultra HD 8 mức tuyệt đẹp!",
    },
    "zh": {
        "label": "🇨🇳 中文 (Chinese)",
        "banner": "APPLE + NOTO 超清 8 级多分辨率 CBDT 表情字体生成器 (20 -> 192px)",
        "help_title": "工具功能与使用说明：",
        "help_lines": [
            "1. 移除 COLR/CPAL 表，实现类似 Apple Color Emoji 的纯位图 3D 渲染。",
            "2. 从 192px 母版多线程缩放生成 8 个清晰尺寸：20, 32, 40, 48, 64, 96, 160, 192 px。",
            "3. CLI: python make_apple_multistrike.py <母版192.ttf> <输出.ttf> [--strikes 20,32,40,48,64,96,160,192]",
        ],
        "prompt_src": "请输入 192px 母版字体路径 (回车使用 '{default}'): ",
        "prompt_dst": "请输入输出多分辨率字体路径 (回车使用 '{default}'): ",
        "prompt_stk": "请输入 PPEM 分辨率列表 (回车使用 '{default}'): ",
        "err_missing": "[错误] 找不到文件: {path}",
        "err_no_cbdt": "[错误] 输入字体必须包含 CBDT 和 CBLC 表！",
        "step_load": "[*] 正在加载 192px 母版 CBDT 字体: {path}...",
        "info_master": "[*] 母版分辨率: {ppem}px ({count} glyphs) | 压缩引擎: {comp}",
        "info_target": "[*] 目标分辨率: {strikes}",
        "prog_reuse": "  [+] 分辨率 {ppem:>3}px : 直接复用母版数据。",
        "prog_gen": "  [*] 分辨率 {ppem:>3}px : 正在多线程缩放并压缩 {count} 张位图 (比例={scale:.3f})...",
        "done_msg": "[成功] 耗时 {sec:.2f} 秒完成！已保存: {out} ({mb:.2f} MB)",
        "next_action": "\n接下来您想做什么？\n  (1) 返回主菜单\n  (0) 退出程序\n请输入选项 (1/0): ",
        "bye": "再见！祝您使用愉快！",
    },
    "ru": {
        "label": "🇷🇺 Русский (Russian)",
        "banner": "ГЕНЕРАТОР 8-УРОВНЕВЫХ ШРИФТОВ CBDT APPLE + NOTO ULTRA HD (20 -> 192px)",
        "help_title": "ОПИСАНИЕ И СПОСОБЫ ЗАПУСКА:",
        "help_lines": [
            "1. Удаляет таблицы COLR/CPAL для 100% растрового 3D-рендеринга как в Apple Color Emoji.",
            "2. Масштабирует исходник 192px в 8 четких размеров: 20, 32, 40, 48, 64, 96, 160, 192 px.",
            "3. CLI: python make_apple_multistrike.py <исходник192.ttf> <выход.ttf> [--strikes 20,32,40,48,64,96,160,192]",
        ],
        "prompt_src": "Введите путь к исходному шрифту 192px (Enter для '{default}'): ",
        "prompt_dst": "Введите имя выходного шрифта (Enter для '{default}'): ",
        "prompt_stk": "Введите список размеров PPEM (Enter для '{default}'): ",
        "err_missing": "[ОШИБКА] Файл не найден: {path}",
        "err_no_cbdt": "[ОШИБКА] Входной шрифт должен содержать таблицы CBDT и CBLC!",
        "step_load": "[*] Загрузка исходного шрифта CBDT: {path}...",
        "info_master": "[*] Исходный размер: {ppem}px ({count} глифов) | Сжатие: {comp}",
        "info_target": "[*] Целевые размеры: {strikes}",
        "prog_reuse": "  [+] Размер {ppem:>3}px : Использован исходный слой напрямую.",
        "prog_gen": "  [*] Размер {ppem:>3}px : Масштабирование и сжатие {count} битмапов (масштаб={scale:.3f})...",
        "done_msg": "[ГОТОВО] Завершено за {sec:.2f} сек! Сохранено: {out} ({mb:.2f} МБ)",
        "next_action": "\nЧто вы хотите сделать дальше?\n  (1) Вернуться в главное меню\n  (0) Выйти из программы\nВаш выбор (1/0): ",
        "bye": "До свидания! Наслаждайтесь шрифтом Ultra HD 8-Strike 3D!",
    },
}


def compress_png_fast(raw_bytes, quality=88):
    if PNGQUANT_BIN:
        q_min = max(40, quality - 15)
        try:
            proc = subprocess.run(
                [PNGQUANT_BIN, "--quality", f"{q_min}-{quality}", "--speed", "3", "-"],
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
        q_im = im.quantize(colors=256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.FLOYDSTEINBERG)
        out = io.BytesIO()
        q_im.save(out, format="PNG", optimize=True)
        res = out.getvalue()
        return res if len(res) < len(raw_bytes) else raw_bytes
    except Exception:
        return raw_bytes


def clamp_s8(val):
    return max(-128, min(127, int(round(val))))


def clamp_u8(val, min_v=1):
    return max(min_v, min(255, int(round(val))))
def build_apple_multistrike(input_ttf, output_ttf, strikes=ULTRA_8_STRIKES, quality=88, lang="en"):
    t0 = time.time()
    txt = LANG_PACK.get(lang, LANG_PACK["en"])

    if not os.path.isfile(input_ttf):
        raise FileNotFoundError(txt["err_missing"].format(path=input_ttf))

    print(txt["step_load"].format(path=input_ttf))
    font = ttLib.TTFont(input_ttf, lazy=False)

    if "CBDT" not in font or "CBLC" not in font:
        raise ValueError(txt["err_no_cbdt"])

    for tag in ("COLR", "CPAL", "SVG "):
        if tag in font:
            del font[tag]

    master_strike = font["CBLC"].strikes[-1]
    master_data = font["CBDT"].strikeData[-1]
    src_ppem = master_strike.bitmapSizeTable.ppemY

    sorted_ppems = sorted(set(strikes))
    comp_name = "pngquant binary" if PNGQUANT_BIN else "Pillow FASTOCTREE"
    print(txt["info_master"].format(ppem=src_ppem, count=len(master_data), comp=comp_name))
    print(txt["info_target"].format(strikes=sorted_ppems))

    decoded_masters = {}
    for gname, bmp in master_data.items():
        im = Image.open(io.BytesIO(bmp.imageData)).convert("RGBA")
        decoded_masters[gname] = (im, bmp)

    new_cblc_strikes = []
    new_cbdt_strike_data = []

    for target_ppem in sorted_ppems:
        if target_ppem == src_ppem:
            new_cblc_strikes.append(copy.deepcopy(master_strike))
            new_cbdt_strike_data.append(copy.deepcopy(master_data))
            print(txt["prog_reuse"].format(ppem=target_ppem))
            continue

        scale = target_ppem / float(src_ppem)
        print(txt["prog_gen"].format(ppem=target_ppem, count=len(decoded_masters), scale=scale))

        def _resize_worker(item):
            gn, (pil_im, src_bmp) = item
            nw = max(1, int(round(src_bmp.metrics.width * scale)))
            nh = max(1, int(round(src_bmp.metrics.height * scale)))
            resized = pil_im.resize((nw, nh), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            resized.save(buf, format="PNG", optimize=True)
            c_png = compress_png_fast(buf.getvalue(), quality=quality)

            nbmp = C_B_D_T_.cbdt_bitmap_format_17(data=b"", ttFont=font)
            nbmp.metrics = C_B_D_T_.SmallGlyphMetrics()
            nbmp.metrics.width = clamp_u8(nw)
            nbmp.metrics.height = clamp_u8(nh)
            nbmp.metrics.BearingX = clamp_s8(src_bmp.metrics.BearingX * scale)
            nbmp.metrics.BearingY = clamp_s8(src_bmp.metrics.BearingY * scale)
            nbmp.metrics.Advance = clamp_u8(src_bmp.metrics.Advance * scale)
            nbmp.imageData = c_png
            return gn, nbmp

        strike_dict = {}
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as ex:
            for gn, nbmp in ex.map(_resize_worker, decoded_masters.items()):
                strike_dict[gn] = nbmp

        s_copy = copy.deepcopy(master_strike)
        bst = s_copy.bitmapSizeTable
        bst.ppemX = bst.ppemY = target_ppem
        bst.widthMax = clamp_u8(target_ppem)
        for lm in (bst.hori, bst.vert):
            lm.ascender = clamp_s8(lm.ascender * scale)
            lm.descender = clamp_s8(lm.descender * scale)
            lm.maxBeforeBL = lm.ascender
            lm.minAfterBL = lm.descender

        new_cblc_strikes.append(s_copy)
        new_cbdt_strike_data.append(strike_dict)

    font["CBLC"].strikes = new_cblc_strikes
    font["CBDT"].strikeData = new_cbdt_strike_data

    font.save(output_ttf)
    font.close()
    mb = os.path.getsize(output_ttf) / (1024 * 1024)
    print("=" * 72)
    print(txt["done_msg"].format(sec=time.time() - t0, out=output_ttf, mb=mb))
    print("=" * 72)


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

        def_src = "seguiemj_192_final.ttf"
        def_dst = "Win11_Ultra8Strikes_3D.ttf"
        def_stk = "20,32,40,48,64,96,160,192"

        src_in = input(txt["prompt_src"].format(default=def_src)).strip().strip('"') or def_src
        dst_in = input(txt["prompt_dst"].format(default=def_dst)).strip().strip('"') or def_dst
        stk_in = input(txt["prompt_stk"].format(default=def_stk)).strip() or def_stk

        print("-" * 72)
        try:
            strike_list = [int(x.strip()) for x in stk_in.split(",") if x.strip()]
            build_apple_multistrike(src_in, dst_in, strikes=strike_list, quality=88, lang=lang)
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
        parser = argparse.ArgumentParser(description="Apple + Noto Ultra HD Multi-Strike CBDT Emoji Font Builder")
        parser.add_argument("input", help="Master 192px CBDT font (e.g. seguiemj_192_final.ttf)")
        parser.add_argument("output", help="Output multi-strike TTF (e.g. Win11_Ultra8Strikes_3D.ttf)")
        parser.add_argument("--strikes", default="20,32,40,48,64,96,160,192", help="Comma-separated PPEM strikes")
        parser.add_argument("--quality", type=int, default=88, help="PNG quality 1-100 (Default: 88)")
        parser.add_argument("--lang", choices=["en", "vi", "zh", "ru"], default="en", help="UI language")
        args = parser.parse_args()

        try:
            strike_list = [int(x.strip()) for x in args.strikes.split(",") if x.strip()]
            build_apple_multistrike(args.input, args.output, strikes=strike_list, quality=args.quality, lang=args.lang)
        except Exception as exc:
            print(f"\n[FAILED] {type(exc).__name__}: {exc}")
            sys.exit(1)
