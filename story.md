# 📖 story.md

**🌐 Language / Ngôn ngữ / 语言 / Язык:**

🇺🇸 [English](#-english) | 🇻🇳 [Tiếng Việt](#-tiếng-việt) | 🇨🇳 [中文](#-中文) | 🇷🇺 [Русский](#-русский)

---

## 🇺🇸 English

This project started because I wanted full control over the emoji‑font pipeline instead of depending on external repositories or release schedules.

While experimenting with ZFont 3, I discovered that Honor supports replacing emoji fonts through `.hwt` packages. That discovery became a key feature of this project.

This repository is not the result of luck. It is the result of studying existing projects, fixing real issues, and building my own improvements.

I began by learning from Chasmical’s flag‑emoji‑for‑windows repository. The original font added the missing country flags, but it still had limits. I wanted to go further: keep the beautiful native Fluent 3D look of Windows 11, while making that same complete emoji set also work reliably on Windows 10 and Android MagicOS.

That is how the **COLRv1 + CBDT Hybrid Engine** was born.

On Windows 11, the system prioritises the COLRv1 table. So I kept Segoe’s original 3D vector emojis completely untouched. I only injected new CBDT bitmap entries for the 262 country flags and the brand‑new Unicode 18.0 emojis.

For Windows 10 and Android, which do not support COLRv1, I used HarfBuzz and Skia to render all 3136 native multi‑skin‑tone ZWJ sequences into 7079 high‑quality bitmap images. Those bitmaps are stored inside the CBDT table as a fallback.

One of the hardest challenges was the 65535 OpenType glyph ceiling. Instead of overloading the font, I found a smarter way: recycle unused glyph slots. This trick let me safely pack thousands of ZWJ sequences, all the flags, and the new Unicode 18.0 emojis without hitting the hard limit.

I built four different editions. There is the lightweight Win11 Pure Hybrid version, the full Win10 Hybrid pack, the Ultra HD 8‑Strike bitmap version for 2K and 4K screens, and the ready‑to‑use `.hwt` theme package for Honor and Huawei phones.

This project was made together with open‑source tools including FontTools, Skia, HarfBuzz, pngquant and Pillow. It also took many nights of testing, failing, debugging, and trying again.

My goal is simple: to make the full set of modern Unicode emojis display correctly, beautifully, and consistently across Windows 11, Windows 10, and Android MagicOS.

👉 **Read the full technical documentation here: [README.md](./README.md)**

---

## 🇻🇳 Tiếng Việt

Dự án này bắt đầu vì mình muốn tự chủ hoàn toàn quy trình tạo font emoji, thay vì phải phụ thuộc vào các repo khác hoặc lịch phát hành của người khác.

Khi thử nghiệm với ZFont 3, mình phát hiện ra rằng điện thoại Honor có thể thay đổi font emoji thông qua tệp `.hwt`. Khám phá đó đã trở thành một tính năng quan trọng của toàn bộ dự án.

Repo này không phải là thành quả của sự may mắn. Nó là kết quả của quá trình học hỏi từ các dự án có sẵn, sửa lỗi thực tế và tự mình xây dựng những cải tiến riêng.

Mình bắt đầu bằng việc tham khảo repo `flag-emoji-for-windows` của Chasmical. Bản gốc đã bổ sung các cờ quốc gia bị thiếu, nhưng vẫn còn nhiều hạn chế. Mình muốn đi xa hơn: giữ nguyên vẻ đẹp 3D Fluent gốc của Windows 11, đồng thời làm cho bộ emoji đầy đủ đó cũng có thể chạy ổn định trên Windows 10 và Android MagicOS.

Và từ đó, **Cơ chế Hybrid COLRv1 + CBDT** ra đời.

Trên Windows 11, hệ thống ưu tiên bảng COLRv1. Vì vậy mình giữ nguyên toàn bộ các emoji vector 3D gốc của Segoe. Mình chỉ chèn thêm các mục bitmap CBDT mới cho 262 cờ quốc gia và bộ emoji Unicode 18.0 mới nhất.

Với Windows 10 và Android — hai nền tảng không hỗ trợ COLRv1 — mình dùng HarfBuzz và Skia để render toàn bộ 3136 chuỗi ZWJ đa tông da gốc của Win11 thành 7079 ảnh bitmap chất lượng cao. Những ảnh này được lưu vào bảng CBDT để dùng làm bản dự phòng.

Một trong những thử thách khó nhất là giới hạn 65535 glyph của OpenType. Thay vì làm font bị quá tải, mình đã tìm ra cách thông minh hơn: **tái sử dụng các slot glyph trống**. Mẹo này giúp mình đóng gói hàng nghìn chuỗi ZWJ, toàn bộ cờ và bộ emoji Unicode 18.0 mà không đụng đến giới hạn cứng của OpenType.

Mình đã tạo ra bốn phiên bản khác nhau: bản Win11 Pure Hybrid nhẹ, bản Full Hybrid cho Win10, bản Ultra HD 8‑Strike bitmap cho màn hình 2K/4K, và gói theme `.hwt` sẵn sàng dùng cho điện thoại Honor, Huawei.

Dự án này được xây dựng nhờ các công cụ nguồn mở như FontTools, Skia, HarfBuzz, pngquant và Pillow. Nó cũng đòi hỏi rất nhiều đêm thử nghiệm, gặp lỗi, gỡ lỗi và thử lại.

Mục tiêu của mình rất đơn giản: làm cho toàn bộ bộ emoji Unicode hiện đại hiển thị đúng, đẹp và nhất quán trên Windows 11, Windows 10 và Android MagicOS.

👉 **Xem tài liệu kỹ thuật đầy đủ tại đây: [README.vi.md](./README.vi.md)**

---

## 🇨🇳 中文

这个项目的初衷，是我希望能够完全掌控 emoji 字体的制作流程，而不是依赖别人的仓库或者别人的发布时间表。

在使用 ZFont 3 进行测试的时候，我发现 Honor 手机可以通过 `.hwt` 主题包替换系统 emoji 字体。这个发现，后来就成了本项目的核心功能之一。

这个仓库并不是靠运气做出来的。它是参考现有项目、解决真实问题，并且不断做出属于自己的改进之后得到的成果。

我一开始参考了 Chasmical 的 `flag-emoji-for-windows` 仓库。原版字体补上了缺失的各国国旗，但仍然存在很多限制。我想要做得更进一步：保留 Windows 11 原生流畅的 3D Fluent 风格，同时让这一套完整的 emoji 也能够在 Windows 10 和 Android MagicOS 上面稳定显示。

于是，**COLRv1 + CBDT 混合引擎**就这样诞生了。

在 Windows 11 上面，系统会优先读取 COLRv1 表格。所以我完整保留了 Segoe 原生的 3D 矢量 emoji，只新增 CBDT 位图条目，用来存放全部 262 面国旗以及最新的 Unicode 18.0 表情符号。

而 Windows 10 和 Android 并不支持 COLRv1。针对这两个平台，我使用 HarfBuzz 和 Skia，把全部 3136 个 Win11 原生多肤色 ZWJ 序列渲染成 7079 张高质量位图，统一存放在 CBDT 表格里面作为备用方案。

项目当中最难的挑战之一，就是 OpenType 65535 字形上限。我没有盲目把字体撑爆，而是找到了更巧妙的办法：**复用已经空置的字形槽位**。依靠这个方法，我可以安全地存放数千条 ZWJ 序列、全部国旗以及 Unicode 18.0 的新表情，而不会触碰 OpenType 的硬性上限。

我一共制作了四个不同版本：轻量的 Win11 Pure Hybrid 版、完整的 Win10 Hybrid 版、面向 2K/4K 屏幕的 Ultra HD 8‑Strike 位图版，还有可以直接在 Honor、华为手机上使用的 `.hwt` 主题包。

这个项目离不开 FontTools、Skia、HarfBuzz、pngquant、Pillow 这些开源工具的支持。同时它也耗费了无数个夜晚，不断测试、报错、排错、重来。

我的目标很简单：让整套现代 Unicode emoji，能够在 Windows 11、Windows 10 和 Android MagicOS 上面，正确、美观、统一地显示出来。

👉 **查看完整技术文档：[README.zh.md](./README.zh.md)**

---

## 🇷🇺 Русский

Этот проект начался потому, что я хотел полностью контролировать процесс создания шрифта эмодзи, вместо того чтобы зависеть от чужих репозиториев и графиков релизов.

Экспериментируя с ZFont 3, я обнаружил, что на телефонах Honor можно заменять системный шрифт эмодзи с помощью пакетов тем `.hwt`. Эта находка стала одной из ключевых возможностей проекта.

Этот репозиторий — не результат удачи. Он появился благодаря изучению готовых проектов, исправлению реальных ошибок и созданию собственных улучшений.

Сначала я изучил репозиторий Chasmical `flag-emoji-for-windows`. Исходный шрифт добавлял недостающие флаги стран, но у него всё ещё было много ограничений. Я захотел пойти дальше: сохранить красивый родной 3D-стиль Fluent из Windows 11 и при этом сделать этот же полный набор эмодзи стабильно работающим на Windows 10 и Android MagicOS.

Так родился **гибридный движок COLRv1 + CBDT**.

В Windows 11 система в первую очередь читает таблицу COLRv1. Поэтому я полностью сохранил оригинальные векторные 3D-эмодзи Segoe и добавил только новые битмап-записи CBDT для всех 262 флагов стран и новых эмодзи Unicode 18.0.

Windows 10 и Android не поддерживают COLRv1. Для этих платформ я использовал HarfBuzz и Skia, чтобы отрендерить все 3136 родных ZWJ-последовательностей Win11 с разными оттенками кожи в 7079 качественных битмапов. Все эти изображения сохраняются в таблице CBDT в качестве запасного варианта.

Одной из самых сложных задач был предел OpenType в 65535 глифов. Вместо того чтобы перегружать шрифт, я нашёл более умное решение: **повторно использовать свободные слоты глифов**. Благодаря этому приёму я смог безопасно упаковать тысячи ZWJ-последовательностей, все флаги и новые эмодзи Unicode 18.0, не достигая жёсткого лимита OpenType.

Я подготовил четыре разные версии: облегчённую версию Win11 Pure Hybrid, полную версию для Win10, битмап-версию Ultra HD 8‑Strike для экранов 2K/4K и готовый пакет тем `.hwt` для телефонов Honor и Huawei.

Проект создан с помощью открытых библиотек FontTools, Skia, HarfBuzz, pngquant и Pillow. На него ушло много вечеров тестирования, ошибок, отладки и новых попыток.

Моя цель проста: сделать так, чтобы весь современный набор эмодзи Unicode отображался правильно, красиво и единообразно на Windows 11, Windows 10 и Android MagicOS.

👉 **Полная техническая документация: [README.ru.md](./README.ru.md)**
