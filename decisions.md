# decisions.md — LifeWay HD report (ถอดจากแชต 2026-11-04 → 05)
วันที่ | จุดแยก | ทางเลือก | ที่เลือก | เพราะ (คำพูดผู้ใช้) | อะไรจะทำให้เปลี่ยนใจ
2026-11-04 | แหล่งคำนวณชาร์ท | free API / RoxyAPI / คำนวณเอง | คำนวณเองด้วย Swiss Ephemeris | API ถูกบล็อกจาก sandbox; ต่อมาเทียบกับ bodygraph.com ตรง 13/13 ดาว | ถ้า sandbox เรียก API ได้ หรือต้องการ Chiron/Lilith/Variables → ใช้ API
2026-11-05 | ภาษาเขียน | อังกฤษแล้วแปล / ไทยตรง | ไทยตรงจาก JSON + brief | "อย่าเขียนอังกฤษแล้วแปล" คุณภาพดีกว่า ไม่เสียเวลา 2 เท่า | ไม่มี
2026-11-05 | วิธีเขียน 14 บท | เขียนทีเดียว / ทีละบท subagent ขนาน 4 ตัว | subagent 4 ตัว บทละ ~1,400 คำ + brief ชุดเดียว | ผู้ใช้อนุมัติ "โอเคคุณภาพ" จากบทตัวอย่าง Type | ถ้าเสียงไม่สม่ำเสมอ → ลด agent เหลือ 2 หรือใส่ตัวอย่างบทอนุมัติให้ทุก agent
2026-11-05 | ตัวจัดหน้า | ReportLab (skill book-layout-gemini) / docx→LibreOffice / Chrome print | docx→LibreOffice ฟอนต์ Sarabun | ReportLab วางวรรณยุกต์ไทยผิด; LibreOffice shape ถูก และผู้ใช้แก้ใน Word ได้ | ถ้าต้องการ header/footer แบบนิตยสาร → Chrome headless + CSS
2026-11-05 | รูปประกอบ | Gemini (skill เดิม) / Canva MCP / SVG วาดเอง | SVG วาดเอง 15 รูป | Gemini ถูกบล็อกจาก sandbox; Canva ได้แต่ thumbnail 200px | รันบนเครื่องผู้ใช้ที่เรียก Gemini ได้
2026-11-05 | ความยาวเล่ม | 30-40 หน้า / 64 หน้า | 64 หน้า | ผู้ใช้ขอ "30-40 หน้าขึ้นไป" และไม่ท้วง | ถ้าลูกค้าบ่นว่ายาว → ลดคำต่อบท
2026-11-05 | ชาร์ท | วาดเอง v1 / วาดเอง v2 classic / GitHub AGPL / bodygraph.com API | bodygraph.com API + ดีไซน์ "lifeway" | ผู้ใช้: "ชาร์ทมันไม่ค่อยสวย" (v1) "ยังไม่สวย" (v2) → ซื้อแพ็ก bodygraph.com | AGPL ของ GitHub ใช้ได้เฉพาะ POC
2026-11-05 | เครื่องยนต์เขียนตอน automate | Claude API ผ่าน n8n / Claude subscription (scheduled task + skill) | Claude subscription + skill | "ไม่ค่อยอยากใช้ claude api" "เปิด claude desktop ตลอดเวลาได้" | ยอดขาย > ~20 เล่ม/วัน → ย้ายส่วนเขียนไป API (n8n workflow เตรียมไว้แล้ว)
2026-11-05 | ชื่อโปรเจกต์ | — | LifeWay | ผู้ใช้ตั้ง | —
