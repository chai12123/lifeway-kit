---
name: lifeway-report
description: ผลิตรายงาน Human Design ฉบับเต็มภาษาไทย (PDF 40-65 หน้า) แบรนด์ LifeWay จากวันเดือนปี เวลา และเมืองเกิดของลูกค้า — ดึง/คำนวณชาร์ท ใส่ bodygraph ดีไซน์ LifeWay เขียน 14 บทด้วย subagent ประกอบเล่ม docx→PDF ฟอนต์ Sarabun ส่งอีเมล ใช้ทุกครั้งที่ผู้ใช้พูดว่า ทำรายงาน HD, ทำเล่ม human design, lifeway report, รายงาน lifeway, ออเดอร์ HD ใหม่, ทำเล่มให้ลูกค้าคนนี้, มีออเดอร์เข้ามา, รันรายงานจาก sheet, ส่งไฟล์ test.json/ผล bodygraph มาแล้วขอให้ทำเล่ม, สร้างชาร์ท human design, คำนวณ human design จากวันเกิด — ไม่ใช้กับโพสต์เฟซบุ๊กหรือคอนเทนต์ขาย (ใช้สกิลโพสต์ของ MiB) และไม่ใช้กับการออกแบบแพลตฟอร์ม/n8n (คุยปกติ)
---

# lifeway-report — รายงาน Human Design ฉบับเต็ม (LifeWay)

> ถอดจาก: แชตทำเล่มตัวอย่างชาร์ทผู้ใช้เอง 64 หน้า + ต่อ bodygraph.com API, 2026-11-04→05 | ทดสอบล่าสุด: 2026-11-05 | stack: Python 3.12, python-docx, pyswisseph 2.10, LibreOffice 24.2, rsvg-convert, Sarabun TTF, bodygraph.com API v221006 | kit: `kit/lifeway-report/` (Project files หรือ Google Drive โฟลเดอร์ LifeWay/kit หรือ zip ที่ผู้ใช้เก็บ)
> ทดสอบด้วย subagent สด 2026-11-05: ผ่านรอบ 0-3 ครั้งแรก พบช่องว่าง 12 จุด แก้แล้ว (ดูบทเรียน)
> สมมติฐานที่อาจล้าสมัย: (1) sandbox ยังเรียก api.bodygraphchart.com ไม่ได้ → ต้องรับ JSON เป็นไฟล์ (2) ชื่อดีไซน์ชาร์ทใน bodygraph.com คือ `lifeway` (3) โครง response ของ API ยังมี Properties/Personality/Design/Channels/DefinedCenters/SVG และค่าอยู่ใน `option` (4) LibreOffice + Sarabun ยังเป็นตัวจัดหน้าที่วรรณยุกต์ไทยถูก (5) ความยาวเป้าหมาย 14 บท × 1,300-1,600 คำ ≈ 64 หน้า — เมื่อถูกเรียก ตรวจ 5 ข้อนี้ 1 นาที ถ้าเปลี่ยนให้บอกผู้ใช้ก่อนทำตาม

## หลักการที่ละเมิดไม่ได้
1. ข้อมูลชาร์ทต้องมาจาก bodygraph.com API หรือ `hd_calc.py` เท่านั้น — ห้ามให้โมเดล "จำ" gate/channel เอง และทุกบทเขียนจาก chart.json ที่ส่งให้ ห้ามแต่ง gate/center/channel ที่ไม่มีในชาร์ท
2. เวลาเกิดบังคับ ถ้าลูกค้าไม่ทราบให้ใช้ 12:00 และต้องเขียนในปกว่า "เวลาเกิดโดยประมาณ" + หน้าหมายเหตุ
3. เขียนไทยตรงจากข้อมูล ไม่เขียนอังกฤษแล้วแปล (decision 2026-11-05)
4. ภาพชาร์ทในเล่ม = SVG ดีไซน์ LifeWay จาก API เป็นหลัก; ตัววาดเองเป็น fallback เท่านั้นและต้องบอกผู้ใช้
5. ทุกเล่มมีหน้าหมายเหตุว่าเป็นเครื่องมือสำรวจตัวเอง ไม่ใช่คำวินิจฉัยทางการแพทย์/การเงิน/กฎหมาย — ห้ามตัดออก
6. ไม่ใส่ API key ลงในแชต ไฟล์ในเล่ม หรือสกิล — key อยู่บนเครื่องผู้ใช้/credentials ของ n8n เท่านั้น
7. ห้ามใช้ reportlab/skill book-layout-gemini จัดหน้าเล่มภาษาไทย (วรรณยุกต์ผิด)

## แผนที่รอบ
| รอบ | ชิ้นงาน | รูปแบบ | จุดหยุด | ถ้าผู้ใช้ตัดสินไม่ได้ |
|---|---|---|---|---|
| 0 รับออเดอร์ | order.json | ชื่อ อีเมล วันเกิด เวลา เมืองเกิด timezone | ขาดเวลาเกิด/เมือง → ถาม 1 ครั้ง | default เวลา 12:00 + timezone Asia/Bangkok และติดป้าย "โดยประมาณ" |
| 1 ชาร์ท | chart.json + chart.png | extract_chart.py จาก API JSON | ไม่มี SVG หรือไม่มีไฟล์ API → fallback | fallback = hd_calc.py + bodygraph_render.py แจ้งผู้ใช้ว่าใช้ชาร์ทวาดเอง |
| 2 เขียน 14 บท | chapters/ch01-14.md | subagent 4 ตัว (บท 1-4, 5-8, 9-11, 12-14) | ตรวจความยาว/กติกาก่อนประกอบ | บทสั้นเกิน → ให้ agent เดิมเติมฉากชีวิต ไม่เติมน้ำ |
| 3 ประกอบเล่ม | .docx + .pdf | build_book.py | เปิดดูหน้า 1-3 และ 1 หน้าเนื้อหา | หน้าเกิน 70 → ลดฟอนต์ 13pt ก่อนตัดเนื้อหา |
| 4 ส่งมอบ | อีเมล + log | Gmail connector + Sheet/Drive | ผู้ใช้ไม่ได้บอกให้ส่ง → ส่งไฟล์ในแชตก่อน | ไม่ส่งอีเมลลูกค้าเองถ้าไม่มีคำสั่งชัด |

## โครงโฟลเดอร์และ path (ทำตามนี้ทุกครั้ง)
```
<โฟลเดอร์งาน>/
  kit/        ← สำเนา kit (scripts/ assets/ examples/ README.md)
  work/       ← ของออเดอร์นี้: order.json chart.json chart.png BRIEF.md chapters/ images/ out/
```
ทุกคำสั่งในสกิลรันจาก <โฟลเดอร์งาน> และอ้าง `kit/scripts/...` กับ `work/...` เสมอ

## สิ่งที่ต้องรู้ก่อนเริ่ม (สกิลหาให้ไม่ได้)
- ข้อมูลการเกิดลูกค้า + อีเมล (จากเพจ/ฟอร์ม/Sheet ของผู้ใช้)
- ผล bodygraph.com API เป็นไฟล์ .json: ผู้ใช้เปิด URL `https://api.bodygraphchart.com/v221006/hd-data?api_key=KEY&date=YYYY-MM-DD HH:MM&timezone=Asia/Bangkok&design=lifeway` ในเบราว์เซอร์แล้ว Save as, หรือ n8n/เครื่องผู้ใช้ (Claude Desktop) ยิงให้ — ถ้าไม่มี ใช้ fallback (รอบ 1)
- kit อยู่ที่ไหน: ตรวจ Project files `kit/lifeway-report/` → Google Drive `LifeWay/kit` → ถ้าไม่มีทั้งคู่ สร้างตามสเปกด้านล่างแล้วอัปเป็น kit ให้ครั้งหน้า
- จะส่งอีเมลลูกค้าเลยหรือให้ผู้ใช้ตรวจก่อน (default: ส่งไฟล์ให้ผู้ใช้ตรวจ)

## รายรอบ

### รอบ 0 — รับออเดอร์
input: ข้อความ/แถว Sheet/ไฟล์ → สร้าง `work/order.json` ตาม `examples/order.example.json` (birth_date `YYYY-MM-DD`, birth_time `HH:MM` 24 ชม., timezone IANA) → เกณฑ์: ครบ 5 ช่อง

### รอบ 1 — ชาร์ท
- ตรวจเครื่องมือ 1 บรรทัด: `which soffice rsvg-convert pdffonts pdftoppm && python3 -c "import docx"` — ถ้าไม่มี soffice ให้หยุดและบอกผู้ใช้ (ไม่มีทางจัดเล่มไทยที่ถูกต้องโดยไม่มีมัน); pyswisseph ใช้เฉพาะ fallback: `pip install pyswisseph --break-system-packages`
- ฟอนต์: `mkdir -p ~/.fonts && cp kit/assets/*.ttf ~/.fonts && fc-cache -f`
- ทางหลัก: `python3 kit/scripts/extract_chart.py <api.json> work/` → chart.json (มี hanging_gates, gates_by_center, gate_to_center ให้แล้ว) + chart.svg + chart.png พื้น `#d0e0e3`
- fallback: `python3 kit/scripts/hd_calc.py Y M D h m <UTC offset> > work/chart.json` แล้ว `python3 kit/scripts/bodygraph_render.py work/chart.json work/chart.svg && rsvg-convert -w 1100 work/chart.svg -o work/chart.png`; เทียบ Type/Profile/Authority กับที่ลูกค้าหรือ API บอก (เคยตรง 13/13 ดาว)
- เกณฑ์: chart.json มี type, authority, profile, definition, defined_centers, channels, hanging_gates, gates_by_center, activations ครบ 13 ดาว 2 ฝั่ง; chart.png กว้าง ≥1000px

### รอบ 2 — เขียน 14 บท
- `python3 kit/scripts/make_brief.py --chart work/chart.json --kit kit --out work/BRIEF.md --birth "<วันเวลาเมืองเกิดภาษาไทย>"` → BRIEF รวม system prompt + ข้อมูลชาร์ท (รวม gate แยกตามศูนย์ ผู้เขียนไม่ต้องจำเอง) + ตัวอย่างน้ำเสียงที่ผ่าน + คำสั่ง 14 บท
- ส่ง Agent (general-purpose) 4 ตัวขนานใน message เดียว (บท 1-4, 5-8, 9-11, 12-14): ให้ path ของ `work/BRIEF.md` + บอกว่ารับผิดชอบบทไหน + เขียนลง `work/chapters/chNN.md` + รายงานกลับเฉพาะชื่อไฟล์และจำนวนตัวอักษรไทย
- `python3 kit/scripts/lint_chapters.py work/chapters work/chart.json` → ต้อง 14/14 ผ่าน: ตัวอักษรไทย 6,000-8,500 (นับเฉพาะอักขระไทย U+0E00-0E7F — เล่มที่ผู้ใช้อนุมัติอยู่ที่ 7,100-8,300), บรรทัดแรก `# `, หัวข้อ `## ` 4-7 (รวมคำถาม), ไม่มี `**` `###` ครับ/ค่ะ emoji, คำถาม 3 ข้อ; WARN เรื่อง gate/ช่องที่ไม่มีในชาร์ทให้เปิดอ่านประโยคนั้น (อ้างถึง gate คู่ของคนอื่นได้ แต่ห้ามบอกว่าเป็นของผู้อ่าน)
- บทที่ FAIL: ส่งกลับ agent เดิมพร้อมข้อความ lint ให้แก้ (สูงสุด 1 รอบ) — ยาวเกินให้ตัดน้ำ ไม่ตัดฉากชีวิต; สั้นเกินให้เติมฉากชีวิต

### รอบ 3 — ประกอบเล่ม
- `python3 kit/scripts/make_illustrations.py work/images` (15 รูป พาเลต LifeWay) — ถ้ารันบนเครื่องที่เรียก Gemini ได้และผู้ใช้ต้องการรูป AI ให้ใช้ skill book-layout-gemini **เฉพาะขั้น gen รูป** แล้วเซฟชื่อ `chapter_NN.png` แทน
- `python3 kit/scripts/build_book.py --order work/order.json --chart work/chart.json --chart-image work/chart.png --chapters work/chapters --images work/images --out work/out` (เลขบทมาจากชื่อไฟล์ chNN — ทดสอบด้วยบทไม่ครบได้; หน้าเกิน 70 ใส่ `--body-size 13`)
- เกณฑ์: PDF 55-70 หน้า A4; `pdffonts` ต้องมี **เฉพาะ** Sarabun-Regular/Bold + ฟอนต์สัญลักษณ์ดาว (DejaVu/Inter/NotoColorEmoji) — ถ้าเห็น FreeSerif/Carlito/Liberation แปลว่า theme font หลุด ห้ามส่ง; rasterize หน้า 1-3 + หน้าเนื้อหา 1 หน้าดูด้วยตา: ชาร์ทเต็มหน้า 2, ตารางไม่ล้นหน้า, วรรณยุกต์ไทยไม่ซ้อน

### รอบ 4 — ส่งมอบ
- ส่ง PDF (+docx) ให้ผู้ใช้ด้วย SendUserFile พร้อม 1 บรรทัดสรุป Type/Profile/Authority/จำนวนหน้า
- ถ้าผู้ใช้สั่งให้ส่งลูกค้า: Gmail connector ส่งถึงอีเมลในออเดอร์ หัวข้อ "รายงาน Human Design ฉบับเต็มของคุณ <ชื่อ>" เนื้อหา: สรุป 3 ค่า + แนะนำอ่านตามลำดับ + ทำแผน 30 วัน; แนบ PDF
- บันทึก log: วันที่ ชื่อ อีเมล Type Profile สถานะ ลิงก์ไฟล์ (Google Sheet "LifeWay Orders" ถ้ามี)

## สเปก/ค่าคงที่ (ยืนยันจากไฟล์จริง)
- A4 ขอบ บน/ล่าง 22mm ซ้าย 26mm ขวา 22mm; Sarabun 13.5pt line 1.28; H1 26pt `#654422`; H2 17pt `#BF5A0F`; เลขบท `#C9962E`; ตารางคีย์ `#D0E0E3` หัวตาราง `#654422`
- ชาร์ทหน้า 2 กว้าง 108mm; รูปบทกว้าง 140mm; ปกรูปกว้าง 162mm
- พาเลตรูปประกอบ: `#654422 #3B2612 #E4B54B #EEF3F4 #BF5A0F` พื้น gradient `#F4F8F9→#D0E0E3`
- 14 บท: ภาพรวม / Type+Strategy / Authority / Profile / ศูนย์ defined / ศูนย์ open / Channels / Sun-Earth-Moon-Nodes / Incarnation Cross / งาน / เงิน / ความสัมพันธ์ / สุขภาพ-พลังงาน / แผน 30 วัน (รายละเอียดใน chapter_plan.json)
- API: `GET https://api.bodygraphchart.com/v221006/hd-data` พารามิเตอร์ `api_key, date "YYYY-MM-DD HH:MM", timezone, design`; timezone จากเมือง: `GET /v210502/locations?query=`; ค่าอยู่ใน `Properties.<X>.option`; SVG ใน key `SVG`

## Pipeline + kit
ลำดับ: order.json → extract_chart (หรือ hd_calc+bodygraph_render) → make_brief → 4 agents → lint_chapters → make_illustrations → build_book → ตรวจ → ส่ง — 7 สคริปต์นี้อยู่ใน kit ครบ อ่าน `kit/README.md` ก่อนรัน; ถ้าต้องเขียนสคริปต์เพิ่ม ให้ใส่กลับเข้า kit และบันทึกใน README

## QA ก่อนส่ง
- [ ] Type/Authority/Profile บนปก = ค่าใน chart.json = ค่าที่ API/ลูกค้าแจ้ง
- [ ] `lint_chapters.py` 14/14 ผ่าน และอ่านทุก WARN แล้ว
- [ ] PDF 55-70 หน้า, pdffonts มีเฉพาะ Sarabun + ฟอนต์สัญลักษณ์, หน้า 2 เป็นชาร์ท LifeWay (ไม่ใช่ fallback ถ้ามี API)
- [ ] หน้าหมายเหตุท้ายเล่มอยู่ครบ

## บทเรียนสะสม
- 2026-11-05 | ReportLab (TTFont Sarabun) วางวรรณยุกต์ซ้อนสระบน ("ปั้น" "ที่") | ไม่มี GPOS shaping | ใช้ docx→LibreOffice หรือ Chrome headless — ผูกกับ stack ReportLab เท่านั้น
- 2026-11-05 | free API/ Gemini/ bodygraph API เรียกจาก sandbox ไม่ได้ (403 proxy) | allowlist | รับไฟล์จากผู้ใช้/n8n/เครื่องผู้ใช้ — ผูกกับ sandbox ของ Claude
- 2026-11-05 | `wc -m` รายงาน 24k สำหรับบท 8k ตัวอักษร | locale C นับไบต์ | นับด้วย Python len()
- 2026-11-05 | Canva generate-image ให้ภาพ 200px | ไม่มี export ขนาดเต็มผ่าน MCP ที่ใช้ได้ | อย่าใช้ Canva gen รูปสำหรับพิมพ์
- 2026-11-05 | โค้ด n8n ใช้ `o.name` ได้คำว่า "Type" แทนค่า | API ใส่ label ใน name, ค่าใน option | ใช้ `option` เสมอ
- 2026-11-05 | ตารางสรุปล้น 1 แถวไปหน้าถัดไป | ชาร์ท 96mm + ฟอนต์ 12 | ชาร์ทแยกหน้าเดี่ยว ตารางฟอนต์ 11 — ผูกกับ python-docx+LibreOffice
- 2026-11-05 | ชื่อไฟล์ไทยถูก `\w` ตัดสระ | regex | ใช้ `[\\/:*?"<>|\s]` แทน
- 2026-11-05 | หัวข้อในเล่มเป็น FreeSerif ทั้งที่ตั้ง Sarabun | python-docx ทิ้ง w:asciiTheme/w:cstheme ไว้ LibreOffice ให้ theme ชนะ | build_book ลบ attribute theme ออก + QA ด้วย pdffonts — ผูกกับ python-docx+LibreOffice
- 2026-11-05 | ทดสอบด้วยบท 1 และ 3 แล้วสารบัญขึ้น "บทที่ 2" | ใช้ index ของรายการไฟล์ | เลขบทมาจากชื่อไฟล์ chNN
- 2026-11-05 | subagent ทดสอบต้องเดา path, สูตรนับตัวอักษร, gate→center, วิธีสร้าง BRIEF | สกิลเขียนจากความจำของผู้ทำ | เพิ่ม make_brief.py, lint_chapters.py, โครงโฟลเดอร์, field gates_by_center

## Decision records สำคัญ (เต็มใน kit/decisions.md)
- ชาร์ทวาดเอง 2 เวอร์ชันถูกปฏิเสธ "ชาร์ทมันไม่ค่อยสวย" / "ยังไม่สวย" → ผู้ใช้ซื้อ bodygraph.com และสร้างดีไซน์ `lifeway` → ชาร์ท API เป็นมาตรฐาน; ตัววาดเองคง fallback
- ไม่ใช้ Claude API ("ไม่ค่อยอยากใช้ claude api") → สกิลนี้เป็นเครื่องยนต์ผ่าน subscription; n8n workflow (LifeWay_HD_Report_Workflow.json) เป็นแผนสำรองเมื่อยอด > ~20 เล่ม/วัน
- ความยาว 64 หน้าได้รับการยอมรับโดยไม่ท้วง ("30-40 หน้าขึ้นไป") — ถ้าลูกค้าจริงบ่นว่ายาว ลดคำต่อบท ไม่ตัดจำนวนบท
- ตัวอย่างจากเคสจริง: ชาร์ทผู้ใช้เอง Manifestor 3/5 Emotional Single RAC Vessel of Love (25/46|10/15) ช่อง 1-8, 10-20, 25-51, 37-40 — ใช้เป็นเคสทดสอบ regression (`examples/`)
