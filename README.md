# kit/lifeway-report — ครัวของสกิล lifeway-report

ทดสอบล่าสุด 2026-11-05 บน Linux sandbox ของ Claude: Python 3.12, python-docx, pyswisseph 2.10, LibreOffice 24.2, rsvg-convert, ImageMagick

## ไฟล์ไหนทำอะไร

| ไฟล์ | หน้าที่ | รัน |
|---|---|---|
| `scripts/extract_chart.py` | แปลง JSON จาก bodygraph.com API (`hd-data` + `design=`) → `chart.json` มาตรฐาน + `chart.svg` + `chart.png` (พื้นหลัง `--bg` default `#d0e0e3` ตามดีไซน์ LifeWay) | `python3 scripts/extract_chart.py api.json work/` |
| `scripts/hd_calc.py` | **fallback** คำนวณชาร์ทเองด้วย Swiss Ephemeris (`pip install pyswisseph --break-system-packages`) ได้ `chart.json` schema เดียวกัน (ไม่มีชื่อ cross/strategy เป็นข้อความ มีแต่ gates) ตรวจแล้วตรงกับ bodygraph.com ทั้ง 13 ดาว | `python3 scripts/hd_calc.py 1989 3 21 21 8 7 > work/chart.json` (ปี เดือน วัน ชม นาที UTC offset) |
| `scripts/bodygraph_render.py` | **fallback** วาด bodygraph เองจาก `chart.json` เป็น SVG สไตล์ classic (ใช้เมื่อไม่มี SVG จาก API) | `python3 scripts/bodygraph_render.py work/chart.json work/chart.svg && rsvg-convert -w 1100 work/chart.svg -o work/chart.png` |
| `scripts/make_illustrations.py` | สร้างรูปประกอบ 15 รูป (cover + 14 บท) สไตล์มินิมอล พาเลต LifeWay เป็น SVG→PNG ไม่พึ่ง API | `python3 scripts/make_illustrations.py work/images` |
| `scripts/make_brief.py` | สร้าง `work/BRIEF.md` ให้ subagent ผู้เขียน จาก chart.json + chapter_plan + ตัวอย่างบทที่ผ่าน (มี gate แยกตามศูนย์) | `python3 scripts/make_brief.py --chart work/chart.json --kit . --out work/BRIEF.md --birth "..."` |
| `scripts/lint_chapters.py` | ตรวจ 14 บท: ตัวอักษรไทย 6,000-8,500, รูปแบบ, คำถาม 3 ข้อ, gate/ช่องที่อ้าง (exit 1 ถ้าไม่ผ่าน) | `python3 scripts/lint_chapters.py work/chapters work/chart.json` |
| `scripts/build_book.py` | ประกอบเล่ม: ปก → หน้าชาร์ท → ตารางสรุป+ดาว → สารบัญ → 14 บท → หมายเหตุ เป็น .docx แล้ว soffice → PDF | ดู docstring ในไฟล์ |
| `assets/chapter_plan.json` | system prompt (กติกาน้ำเสียง) + รายการ 14 บท พร้อมคำสั่งต่อบท (ทั่วไป ใช้กับทุกชาร์ท) | อ่านตอนสั่ง subagent เขียน |
| `assets/lifeway-chart-design.json` | export ดีไซน์ชาร์ทจาก bodygraph.com = ต้นทางพาเลตแบรนด์ | อ้างอิง |
| `assets/Sarabun-*.ttf` | ฟอนต์ไทยสำหรับ LibreOffice | `mkdir -p ~/.fonts && cp assets/*.ttf ~/.fonts && fc-cache -f` |
| `examples/order.example.json` | รูปแบบ order.json | — |
| (ไม่มีไฟล์ API ตัวอย่างใน repo สาธารณะ — ดูโครง response ใน SKILL.md ส่วน API) | | |
| `examples/approved_chapter_type_strategy.md` | บทที่ผู้ใช้อนุมัติว่า "โอเคคุณภาพ" ใช้เป็นตัวอย่างน้ำเสียงให้ผู้เขียน | แนบใน brief ของ subagent |

## พารามิเตอร์ที่ปรับได้
- พาเลต: ด้านบนของ `build_book.py` (ACCENT/GOLD/HEAD/TABLE_*) และ `make_illustrations.py` (TEAL/DTEAL/GOLD/CREAM/TERRA)
- ความยาวเล่ม: BODY_PT 13.5 / line 1.28 → 14 บท × ~1,400 คำ ≈ 64 หน้า A4; `--body-size 13` ลดได้ ~5 หน้า; อยาก 40 หน้า ลดคำต่อบทเหลือ ~900 ใน chapter_plan
- ตรวจเครื่องมือก่อนเริ่ม: `which soffice rsvg-convert pdffonts pdftoppm && python3 -c "import docx"`
- ชื่อดีไซน์ชาร์ท API: `design=lifeway` (ต้องตรงกับชื่อใน app.bodygraph.com/cms/chart-designs)

## ข้อจำกัดที่รู้แล้ว
- sandbox ของ Claude **เรียก api.bodygraphchart.com และ Gemini API ไม่ได้** (proxy allowlist) → ต้องได้ JSON จาก API มาเป็นไฟล์ (เบราว์เซอร์ Save as / n8n / เครื่องผู้ใช้ผ่าน Claude Desktop) หรือใช้ fallback hd_calc + bodygraph_render
- ReportLab วางวรรณยุกต์ไทยเพี้ยน → จัดเล่มผ่าน docx + LibreOffice เท่านั้น
- `wc -m` ใน sandbox นับไบต์ (locale C) → นับตัวอักษรไทยด้วย Python `len()`
