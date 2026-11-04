#!/usr/bin/env python3
"""build_book.py — ประกอบเล่มรายงาน Human Design (LifeWay) เป็น .docx แล้วแปลงเป็น PDF ด้วย LibreOffice

ใช้:
  python3 build_book.py --order order.json --chart chart.json --chart-image chart.png \
      --chapters chapters/ --images images/ --out out/ [--title "..."] [--no-pdf]

order.json  : {"name": "...", "email": "...", "birth_date": "1989-03-21", "birth_time": "21:08", "birth_place": "Bangkok, Thailand"}
chart.json  : จาก extract_chart.py (bodygraph API) หรือ hd_calc.py (fallback)
chapters/   : chNN.md บรรทัดแรก "# ชื่อบท", หัวข้อย่อย "## ", คำถาม "1. 2. 3."
images/     : cover.png, chapter_NN.png (จาก make_illustrations.py) — ไม่มีก็ข้ามได้
ผลลัพธ์     : out/<name>_LifeWay_Report.docx และ .pdf  (ฟอนต์ Sarabun ต้องติดตั้งใน ~/.fonts ก่อน soffice)
"""
import os, re, json, glob, argparse, subprocess, shutil
from docx import Document
from docx.shared import Pt, Mm, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# ---------- LifeWay brand palette (จาก lifeway-chart-design.json) ----------
FONT = "Sarabun"
BODY_PT = 13.5      # ขนาดฟอนต์เนื้อหา (ปรับผ่าน --body-size)
BODY_LINE = 1.28
ACCENT = RGBColor(0xBF,0x5A,0x0F)   # ส้ม-น้ำตาล (หัวข้อย่อย)
GOLD   = RGBColor(0xC9,0x96,0x2E)   # ทอง (เลขบท, eyebrow)
HEAD   = RGBColor(0x65,0x44,0x22)   # น้ำตาลเข้ม (ชื่อบท)
BODY   = RGBColor(0x2B,0x2B,0x2B)
MUTED  = RGBColor(0x77,0x77,0x77)
TABLE_KEY_FILL = "D0E0E3"; TABLE_HEAD_FILL = "654422"; TABLE_ALT_FILL = "F7F7F5"

PLANET_ORDER = ['Sun','Earth','NorthNode','SouthNode','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
PLANET_LABEL = {'Sun':'Sun ☉','Earth':'Earth ⊕','NorthNode':'North Node ☊','SouthNode':'South Node ☋','Moon':'Moon ☽','Mercury':'Mercury ☿','Venus':'Venus ♀','Mars':'Mars ♂','Jupiter':'Jupiter ♃','Saturn':'Saturn ♄','Uranus':'Uranus ♅','Neptune':'Neptune ♆','Pluto':'Pluto ♇'}
STRATEGY_TH = {'Manifestor':'Inform — แจ้งให้รู้ก่อนลงมือ','Generator':'Respond — รอแล้วตอบสนอง','Manifesting Generator':'Respond — รอแล้วตอบสนอง (แล้วแจ้ง)','Projector':'Wait for the invitation — รอคำเชิญ','Reflector':'Wait a lunar cycle — รอ 1 รอบจันทร์'}
SIGNATURE_TH = {'Manifestor':'ความสงบ (Peace) / ความโกรธ (Anger)','Generator':'ความพึงพอใจ (Satisfaction) / ความหงุดหงิด (Frustration)','Manifesting Generator':'ความพึงพอใจ (Satisfaction) / ความหงุดหงิด (Frustration)','Projector':'ความสำเร็จ (Success) / ความขมขื่น (Bitterness)','Reflector':'ความประหลาดใจ (Surprise) / ความผิดหวัง (Disappointment)'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--order', required=True); ap.add_argument('--chart', required=True); ap.add_argument('--chart-image', required=True)
    ap.add_argument('--chapters', required=True); ap.add_argument('--images', default=''); ap.add_argument('--out', required=True)
    ap.add_argument('--title', default='รายงานการออกแบบชีวิตฉบับเต็ม'); ap.add_argument('--no-pdf', action='store_true'); ap.add_argument('--body-size', type=float, default=BODY_PT)
    a = ap.parse_args()
    body_pt = a.body_size
    order = json.load(open(a.order, encoding='utf-8')); chart = json.load(open(a.chart, encoding='utf-8'))
    os.makedirs(a.out, exist_ok=True)

    doc = Document(); sec = doc.sections[0]
    sec.page_width, sec.page_height = Mm(210), Mm(297)
    sec.top_margin, sec.bottom_margin, sec.left_margin, sec.right_margin = Mm(22), Mm(22), Mm(26), Mm(22)

    def set_font(run, size=14, bold=False, color=BODY, italic=False):
        run.font.name = FONT; run.font.size = Pt(size); run.font.bold = bold; run.font.italic = italic; run.font.color.rgb = color
        rpr = run._element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
        if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
        for k in ('w:ascii','w:hAnsi','w:cs','w:eastAsia'): rf.set(qn(k), FONT)

    st = doc.styles['Normal']; st.font.name = FONT; st.font.size = Pt(14)
    st.element.rPr.rFonts.set(qn('w:cs'), FONT); st.element.rPr.rFonts.set(qn('w:eastAsia'), FONT)
    for lvl, size, col in ((1, 26, HEAD), (2, 17, ACCENT)):
        hs = doc.styles[f'Heading {lvl}']; hs.font.name = FONT; hs.font.size = Pt(size); hs.font.bold = True; hs.font.color.rgb = col
        rpr = hs.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
        if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
        for k in ('w:ascii','w:hAnsi','w:cs','w:eastAsia'): rf.set(qn(k), FONT)
        for k in ('w:asciiTheme','w:hAnsiTheme','w:cstheme','w:eastAsiaTheme'):
            if rf.get(qn(k)) is not None: del rf.attrib[qn(k)]   # กัน LibreOffice ใช้ theme font แทน Sarabun
        hs.paragraph_format.space_before = Pt(18 if lvl == 2 else 0); hs.paragraph_format.space_after = Pt(8); hs.paragraph_format.keep_with_next = True

    def para(text, size=14, bold=False, color=BODY, align=None, after=8, before=0, indent=False, line=BODY_LINE, italic=False):
        p = doc.add_paragraph(); r = p.add_run(text); set_font(r, size, bold, color, italic)
        pf = p.paragraph_format; pf.space_after = Pt(after); pf.space_before = Pt(before); pf.line_spacing = line
        if align: p.alignment = align
        if indent: pf.first_line_indent = Cm(0.9)
        return p
    def page_break(): doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    def picture(path, width_mm):
        if not path or not os.path.exists(path): return
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(path, width=Mm(width_mm)); p.paragraph_format.space_after = Pt(10)
    def shade(cell, hexcol):
        tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear'); shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), hexcol); tcPr.append(shd)

    # footer page numbers
    fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER; r = fp.add_run(); set_font(r, 10, color=MUTED)
    for tag, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
        if tag: fc = OxmlElement('w:fldChar'); fc.set(qn('w:fldCharType'), tag); r._element.append(fc)
        else: it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = txt; r._element.append(it)
    sec.different_first_page_header_footer = True

    typ = chart.get('type', ''); prof = chart.get('profile', ''); auth = str(chart.get('authority', '')).split(' (')[0]
    cross = chart.get('incarnation_cross') or ('Cross gates ' + '/'.join(str(g) for g in chart.get('incarnation_cross_gates', [])))
    img = lambda n: os.path.join(a.images, n) if a.images else ''

    # ---------- COVER ----------
    picture(img('cover.png'), 162)
    para("LifeWay · Human Design", 16, color=GOLD, align=WD_ALIGN_PARAGRAPH.CENTER, after=0, before=10)
    para(a.title, 32, bold=True, color=HEAD, align=WD_ALIGN_PARAGRAPH.CENTER, after=4, line=1.1)
    para(f"{typ} · Profile {prof} · {auth} Authority", 16, color=ACCENT, align=WD_ALIGN_PARAGRAPH.CENTER, after=24)
    para(f"จัดทำสำหรับ {order.get('name','')}", 14, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(f"เกิดวันที่ {order.get('birth_date','')}  เวลา {order.get('birth_time','')}  {order.get('birth_place','')}", 13, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    para(cross, 13, color=MUTED, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
    page_break()

    # ---------- CHART PAGE ----------
    doc.add_heading("ชาร์ทของคุณ", 1)
    picture(a.chart_image, 108)
    page_break()
    para("สรุปองค์ประกอบของชาร์ท", 13, bold=True, color=HEAD, after=6)
    rows = [("Type", typ), ("Strategy", STRATEGY_TH.get(typ, chart.get('strategy', ''))), ("Authority", chart.get('authority', '')),
            ("Profile", prof), ("Definition", chart.get('definition', '')), ("Incarnation Cross", cross),
            ("Signature / Not-self", SIGNATURE_TH.get(typ, '')),
            ("Centers ที่ defined", ', '.join(chart.get('defined_centers', []))), ("Centers ที่ open", ', '.join(chart.get('open_centers', []))),
            ("Channels", ' · '.join(f"{x}-{y}" for x, y in chart.get('channels', [])) or '—'),
            ("Personality Sun / Earth", f"Gate {chart['activations']['personality']['Sun']['gate']}.{chart['activations']['personality']['Sun']['line']} / Gate {chart['activations']['personality']['Earth']['gate']}.{chart['activations']['personality']['Earth']['line']}"),
            ("Design Sun / Earth", f"Gate {chart['activations']['design']['Sun']['gate']}.{chart['activations']['design']['Sun']['line']} / Gate {chart['activations']['design']['Earth']['gate']}.{chart['activations']['design']['Earth']['line']}")]
    t = doc.add_table(rows=0, cols=2); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = 'Table Grid'
    for i, (k, v) in enumerate(rows):
        c = t.add_row().cells; c[0].width, c[1].width = Mm(48), Mm(112); shade(c[0], TABLE_KEY_FILL)
        if i % 2: shade(c[1], TABLE_ALT_FILL)
        r0 = c[0].paragraphs[0].add_run(k); set_font(r0, 11, True, ACCENT); r1 = c[1].paragraphs[0].add_run(str(v)); set_font(r1, 11)
    para("", after=4)
    para("ตารางดาวทั้ง 13 ดวง (Personality = ฝั่งดำ · Design = ฝั่งแดง)", 12, bold=True, color=HEAD, before=8, after=4)
    t2 = doc.add_table(rows=1, cols=3); t2.alignment = WD_TABLE_ALIGNMENT.CENTER; t2.style = 'Table Grid'
    for j, hdr in enumerate(("ดาว", "Personality (gate.line)", "Design (gate.line)")):
        cell = t2.rows[0].cells[j]; shade(cell, TABLE_HEAD_FILL); rr = cell.paragraphs[0].add_run(hdr); set_font(rr, 11, True, RGBColor(255, 255, 255))
    for k in PLANET_ORDER:
        P = chart['activations']['personality'].get(k); D = chart['activations']['design'].get(k)
        if not P or not D: continue
        c = t2.add_row().cells
        for j, txt in enumerate((PLANET_LABEL[k], f"{P['gate']}.{P['line']}", f"{D['gate']}.{D['line']}")):
            rr = c[j].paragraphs[0].add_run(txt); set_font(rr, 11, j == 0, BODY if j else HEAD); c[j].width = Mm(50)
    page_break()

    # ---------- TOC ----------
    files = sorted(glob.glob(os.path.join(a.chapters, 'ch*.md')))
    titles = [open(f, encoding='utf-8').readline().lstrip('#').strip() for f in files]
    nums = [int(re.search(r'ch(\d+)', os.path.basename(f)).group(1)) for f in files]   # เลขบทจากชื่อไฟล์ chNN
    doc.add_heading("สารบัญ", 1)
    for n, tt in zip(nums, titles): para(f"บทที่ {n}   {tt}", 14, after=4, line=1.5)
    page_break()

    # ---------- CHAPTERS ----------
    for idx, (f, tt, i) in enumerate(zip(files, titles, nums), 1):
        lines = open(f, encoding='utf-8').read().split('\n')[1:]
        doc.add_heading(f"บทที่ {i}", 1).runs[0].font.color.rgb = GOLD
        doc.paragraphs[-1].paragraph_format.space_after = Pt(0)
        para(tt, 26, bold=True, color=HEAD, after=10, line=1.15)
        picture(img(f'chapter_{i:02d}.png'), 140)
        first = True
        for ln in lines:
            s = ln.rstrip()
            if not s.strip() or s.startswith('# '): continue
            if s.startswith('## '): doc.add_heading(s[3:].strip(), 2); first = True; continue
            m = re.match(r'^\s*(\d+)[\.\)]\s+(.*)', s)
            if m:
                p = para(f"{m.group(1)}.  {m.group(2)}", 14, after=6); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.6); continue
            if s.lstrip().startswith(('- ', '• ', '* ')):
                p = para("•  " + s.lstrip()[2:], 14, after=4); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.first_line_indent = Cm(-0.5); continue
            if s.startswith('>'):
                para(s.lstrip('> ').strip(), 14, color=ACCENT, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=10, before=6); continue
            p = para(s.replace('**', ''), body_pt, after=7, indent=not first); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY; first = False
        if idx < len(files): page_break()

    # ---------- NOTE ----------
    page_break(); doc.add_heading("หมายเหตุ", 1)
    para("รายงานฉบับนี้คำนวณจากตำแหน่งดาว ณ วันเวลาเกิด และเรียบเรียงเนื้อหาโดยระบบปัญญาประดิษฐ์ตามหลักการของระบบ Human Design เนื้อหาทั้งหมดมีไว้เพื่อการสำรวจและทำความเข้าใจตนเอง ไม่ใช่คำวินิจฉัยทางการแพทย์ จิตวิทยา กฎหมาย หรือการเงิน การตัดสินใจใดๆ ในชีวิตยังคงเป็นของคุณ และควรพิจารณาร่วมกับข้อมูลจากผู้เชี่ยวชาญในด้านนั้นๆ", 13, color=MUTED, line=1.4)
    para("หากเวลาเกิดคลาดเคลื่อนเกิน 1 ชั่วโมง บางองค์ประกอบของชาร์ท (โดยเฉพาะ gate ของดวงจันทร์และ line ของดาวบางดวง) อาจเปลี่ยนแปลงได้ โปรดตรวจสอบเวลาเกิดจากสูติบัตรเพื่อความแม่นยำสูงสุด", 13, color=MUTED, line=1.4)

    safe = re.sub(r'[\\/:*?"<>|\s]+', '_', order.get('name', 'customer'))
    docx_path = os.path.join(a.out, f"{safe}_LifeWay_Report.docx"); doc.save(docx_path); print("docx:", docx_path, f"({len(files)} chapters)")
    if not a.no_pdf:
        subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', a.out, docx_path], check=True, capture_output=True, timeout=300)
        pdf = docx_path.replace('.docx', '.pdf'); print("pdf:", pdf)
        try: print(subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout.split('Pages:')[1].split('\n')[0].strip(), 'pages')
        except Exception: pass

if __name__ == '__main__':
    main()
