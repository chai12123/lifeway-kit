#!/usr/bin/env python3
"""make_brief.py — สร้าง work/BRIEF.md สำหรับ subagent ผู้เขียน จาก chart.json + chapter_plan.json + ตัวอย่างบทที่ผ่าน
ใช้: python3 make_brief.py --chart work/chart.json --kit <kit dir> --out work/BRIEF.md [--birth "21 มีนาคม 1989 เวลา 21:08 กรุงเทพฯ"]
"""
import json, argparse, os

PLANETS = ['Sun','Earth','NorthNode','SouthNode','Moon','Mercury','Venus','Mars','Jupiter','Saturn','Uranus','Neptune','Pluto']
CH_NAMES = {(1,8):'Inspiration',(2,14):'The Beat',(3,60):'Mutation',(4,63):'Logic',(5,15):'Rhythm',(6,59):'Mating',(7,31):'The Alpha',(9,52):'Concentration',(10,20):'Awakening',(10,34):'Exploration',(10,57):'Perfected Form',(11,56):'Curiosity',(12,22):'Openness',(13,33):'The Prodigal',(16,48):'The Wavelength',(17,62):'Acceptance',(18,58):'Judgment',(19,49):'Synthesis',(20,34):'Charisma',(20,57):'The Brainwave',(21,45):'Money',(23,43):'Structuring',(24,61):'Awareness',(25,51):'Initiation',(26,44):'Surrender',(27,50):'Preservation',(28,38):'Struggle',(29,46):'Discovery',(30,41):'Recognition',(32,54):'Transformation',(34,57):'Power',(35,36):'Transitoriness',(37,40):'Community',(39,55):'Emoting',(42,53):'Maturation',(47,64):'Abstraction'}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--chart', required=True); ap.add_argument('--kit', required=True); ap.add_argument('--out', required=True); ap.add_argument('--birth', default='')
    a = ap.parse_args()
    c = json.load(open(a.chart, encoding='utf-8'))
    plan = json.load(open(os.path.join(a.kit, 'assets', 'chapter_plan.json'), encoding='utf-8'))
    sample = open(os.path.join(a.kit, 'examples', 'approved_chapter_type_strategy.md'), encoding='utf-8').read().split('\n')
    sample_excerpt = '\n'.join(l for l in sample[2:14] if l.strip())[:1800]
    P, D = c['activations']['personality'], c['activations']['design']
    chans = '\n'.join(f"  - **{x}-{y} Channel of {CH_NAMES.get((x,y),'')}** ({c.get('gate_to_center',{}).get(str(x))} ↔ {c.get('gate_to_center',{}).get(str(y))})" for x, y in c.get('channels', [])) or '  - (ไม่มี channel ที่ defined)'
    by_center = '\n'.join(f"  - {k}: {', '.join(map(str, v)) if v else '—'}" for k, v in c.get('gates_by_center', {}).items())
    rows = '\n'.join(f"| {p} | {P[p]['gate']}.{P[p]['line']} | {D[p]['gate']}.{D[p]['line']} |" for p in PLANETS if p in P and p in D)
    cross = c.get('incarnation_cross') or ('gates ' + '/'.join(map(str, c.get('incarnation_cross_gates', []))))
    md = f"""# BRIEF — รายงาน Human Design ฉบับเต็ม (ภาษาไทย) สำหรับชาร์ทนี้

## กติกาน้ำเสียงและรูปแบบ (บังคับทุกบท)
{plan['system_prompt']}

## ชาร์ทของผู้อ่าน (ข้อมูลจริง — ใช้เฉพาะที่ให้นี้ ห้ามแต่งเพิ่ม)
- เรียกผู้อ่านว่า "คุณ" ตลอด ไม่ระบุชื่อ ไม่ระบุเพศ ไม่สมมติอาชีพ{(' เกิด ' + a.birth) if a.birth else ''}
- Type: **{c.get('type','')}** · Strategy: **{c.get('strategy','')}**
- Authority: **{c.get('authority','')}**
- Profile: **{c.get('profile','')}** · Definition: **{c.get('definition','')}**
- Incarnation Cross: **{cross}**
- Signature / Not-self: {c.get('signature','')} / {c.get('not_self','')}
- Defined centers ({len(c.get('defined_centers',[]))}): **{', '.join(c.get('defined_centers',[])) or 'ไม่มี (Reflector)'}**
- Open centers ({len(c.get('open_centers',[]))}): **{', '.join(c.get('open_centers',[]))}**
- Channels ที่ defined:
{chans}
- Gates ที่เปิดใช้งานทั้งหมด: {', '.join(map(str, c.get('all_gates',[])))}
- Hanging gates (มี gate แต่ไม่ครบช่อง): {', '.join(map(str, c.get('hanging_gates',[]))) or '—'}
- Gates แยกตามศูนย์ (ใช้ตอบว่า gate ไหนอยู่ศูนย์ไหน — ห้ามเดาเอง):
{by_center}

### Activations (Personality = ฝั่งดำ/จิตสำนึก, Design = ฝั่งแดง/กาย)
| ดาว | Personality | Design |
|---|---|---|
{rows}

## ตัวอย่างน้ำเสียงที่ผู้ซื้ออนุมัติแล้ว (จากบท Type ของเคสจริง — เลียนแบบจังหวะและความลึก ไม่ใช่เนื้อหา)
> {sample_excerpt.replace(chr(10), chr(10)+'> ')}

## รูปแบบไฟล์
- ไฟล์ละ 1 บท ชื่อ chNN.md บรรทัดแรก `# ชื่อบท` หัวข้อย่อย `## ` เท่านั้น 4-6 หัวข้อ
- ความยาว: ตัวอักษรไทย 6,000-7,500 ตัว (นับเฉพาะอักขระไทย U+0E00-0E7F ด้วย scripts/lint_chapters.py)
- ไม่ใส่ bold/italic/emoji/เส้นคั่น ไม่มี "ครับ/ค่ะ"
- ปิดท้าย `## คำถามให้สำรวจตัวเอง` + คำถาม 3 ข้อ 1. 2. 3. เจาะจงกับชาร์ทนี้

## รายการบทและสิ่งที่แต่ละบทต้องครอบคลุม
""" + '\n'.join(f"### {ch['index']}. {ch['title']}  → {ch['file']}\n{ch['instructions']}\n" for ch in plan['chapters'])
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    open(a.out, 'w', encoding='utf-8').write(md); print('BRIEF ->', a.out, len(md), 'chars')

if __name__ == '__main__':
    main()
