#!/usr/bin/env python3
"""lint_chapters.py — ตรวจบททุกไฟล์ใน chapters/ ตามเกณฑ์ของสกิล lifeway-report
ใช้: python3 lint_chapters.py work/chapters work/chart.json [--min 6000 --max 7500]
ออก exit code 1 ถ้ามีบทไม่ผ่าน (พิมพ์รายการปัญหาต่อไฟล์)
"""
import re, sys, glob, os, json, argparse

def thai_len(s): return sum(1 for ch in s if '฀' <= ch <= '๿')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('chapters'); ap.add_argument('chart'); ap.add_argument('--min', type=int, default=6000); ap.add_argument('--max', type=int, default=8500); ap.add_argument('--expect', type=int, default=14)
    a = ap.parse_args()
    chart = json.load(open(a.chart, encoding='utf-8'))
    all_gates = set(chart.get('all_gates', [])); channels = {tuple(sorted(c)) for c in chart.get('channels', [])}
    files = sorted(glob.glob(os.path.join(a.chapters, 'ch*.md'))); bad = 0
    if len(files) != a.expect: print(f"WARN: มี {len(files)} บท (คาด {a.expect})")
    for f in files:
        t = open(f, encoding='utf-8').read(); probs = []
        n = thai_len(t)
        if not (a.min <= n <= a.max): probs.append(f"ตัวอักษรไทย {n} (เกณฑ์ {a.min}-{a.max})")
        if not t.lstrip().startswith('# '): probs.append("บรรทัดแรกไม่ใช่ '# ชื่อบท'")
        for pat, name in ((r'\*\*', 'bold **'), (r'^###', '### heading'), (r'ครับ|ค่ะ', 'ครับ/ค่ะ'), (r'[\U0001F300-\U0001FAFF☀-➿]', 'emoji'), (r'^---\s*$', 'เส้นคั่น')):
            if re.search(pat, t, re.M): probs.append(f"พบ {name}")
        h2 = len(re.findall(r'^## ', t, re.M))
        if not (4 <= h2 <= 7): probs.append(f"หัวข้อ ## = {h2} (เกณฑ์ 4-7 รวมคำถาม)")
        if 'คำถามให้สำรวจตัวเอง' not in t: probs.append("ไม่มี ## คำถามให้สำรวจตัวเอง")
        else:
            tail = t.split('คำถามให้สำรวจตัวเอง')[-1]
            q = len(re.findall(r'^\s*\d+[\.\)]\s', tail, re.M))
            if q != 3: probs.append(f"คำถามท้ายบท {q} ข้อ (ต้อง 3)")
        # gate / channel references must exist in chart
        warns = []
        for x, y in re.findall(r'(?:ช่อง|channel)\s*(\d{1,2})\s*[-–]\s*(\d{1,2})', t, re.I):
            if tuple(sorted((int(x), int(y)))) not in channels: warns.append(f"อ้างช่อง {x}-{y} ที่ไม่ defined ในชาร์ท (ตรวจว่าเป็นช่องของคนอื่น/ตัวอย่างหรือเปล่า)")
        for g in re.findall(r'(?:ประตู|gate)\s*(\d{1,2})(?![\d\-–])', t, re.I):
            if int(g) not in all_gates: warns.append(f"อ้าง gate {g} ที่ไม่มีในชาร์ท (ตรวจว่าเป็น gate คู่ของคนอื่นหรือเปล่า)")
        status = 'OK ' if not probs else 'FAIL'
        if warns: print(f"WARN {os.path.basename(f)}: " + '; '.join(sorted(set(warns))))
        if probs: bad += 1
        print(f"{status} {os.path.basename(f)}  ไทย={n}  ##={h2}" + (("\n     - " + "\n     - ".join(sorted(set(probs)))) if probs else ''))
    print(f"\n{len(files)-bad}/{len(files)} ผ่าน"); sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
