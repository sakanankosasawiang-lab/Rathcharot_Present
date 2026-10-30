import os
import docx
from docx.shared import Mm, Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from PIL import Image

def create_catalog():
    doc = docx.Document()

    # 1. Page Setup: A4 Portrait, 12mm margins for maximum catalog canvas
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(12)
        section.bottom_margin = Mm(12)
        section.left_margin = Mm(12)
        section.right_margin = Mm(12)
        section.header_distance = Mm(0)
        section.footer_distance = Mm(0)

    # 2. Dark Background Setup (Obsidian Black: #0C0C0E)
    background = parse_xml(f'<w:background {nsdecls("w")} w:color="0C0C0E"/>')
    doc.element.insert(0, background)
    doc.settings.element.append(parse_xml(f'<w:displayBackgroundShape {nsdecls("w")}/>'))

    # Helper styling functions
    def set_cell_background(cell, fill_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
        # top/bottom/left/right in dxa (1 pt = 20 dxa)
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        cell._tc.get_or_add_tcPr().append(tcMar)

    def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        edges = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
        for edge, border in edges.items():
            if border:
                val = border.get('val', 'single')
                sz = border.get('sz', 4) # 4 = 0.5pt, 8 = 1pt, 12 = 1.5pt
                col = border.get('color', 'C5A059')
                b_xml = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{col}"/>')
                borders.append(b_xml)
            else:
                b_xml = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="none"/>')
                borders.append(b_xml)
        tcPr.append(borders)

    def format_run(run, font_name='Prompt', size_pt=10, bold=False, italic=False, color_rgb=(255, 255, 255)):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = RGBColor(*color_rgb)
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
        rPr.append(rFonts)

    def add_page_frame(doc):
        # Outer table wrapping the full page like an ornate gold picture frame
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Mm(186)
        set_cell_background(cell, "0F0E0D")
        set_cell_margins(cell, top=140, bottom=140, left=160, right=160)
        set_cell_borders(cell,
            top={'sz': 12, 'color': 'C5A059'},
            bottom={'sz': 12, 'color': 'C5A059'},
            left={'sz': 12, 'color': 'C5A059'},
            right={'sz': 12, 'color': 'C5A059'}
        )
        return cell

    # Define color constants
    C_GOLD = (212, 175, 55)
    C_GOLD_LIGHT = (244, 228, 166)
    C_GOLD_BORDER = (197, 160, 89)
    C_WHITE = (255, 255, 255)
    C_MUTED = (163, 157, 146)
    C_SEC = (226, 221, 213)

    print('Building Page 1: Cover Page...')
    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    p1_cell = add_page_frame(doc)

    # Top Logos
    p_logo = p1_cell.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(12)
    p_logo.paragraph_format.space_after = Pt(14)
    if os.path.exists('พิธีหลวง/S__246022151_0.png'):
        p_logo.add_run().add_picture('พิธีหลวง/S__246022151_0.png', width=Mm(28))
    r_div = p_logo.add_run('   |   ')
    format_run(r_div, size_pt=20, color_rgb=C_GOLD_BORDER)
    if os.path.exists('พิธีหลวง/S__246022150_0.png'):
        p_logo.add_run().add_picture('พิธีหลวง/S__246022150_0.png', width=Mm(28))

    # Main Title
    p_title = p1_cell.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(4)
    p_title.paragraph_format.space_after = Pt(6)
    r_t = p_title.add_run('ราชรถ & ช่างภาพงานศพ.com')
    format_run(r_t, size_pt=26, bold=True, color_rgb=C_GOLD)

    # Subtitle
    p_sub = p1_cell.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(12)
    r_s = p_sub.add_run('แคตตาล็อกการให้บริการช่างภาพภาพนิ่ง วิดีโอซีนีม่า และ Live Streaming ถ่ายทอดสดงานพิธีศพครบวงจร')
    format_run(r_s, size_pt=13, bold=True, color_rgb=C_GOLD_LIGHT)

    # Tagline
    p_tag = p1_cell.add_paragraph()
    p_tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tag.paragraph_format.space_before = Pt(0)
    p_tag.paragraph_format.space_after = Pt(18)
    r_tag = p_tag.add_run('ดูแลด้วยมาตรฐานระดับมืออาชีพ สำรวม รู้กาลเทศะ และแม่นยำทุกลำดับพิธีการตลอด 24 ชั่วโมง ทั่วประเทศ')
    format_run(r_tag, size_pt=10.5, color_rgb=C_SEC)

    # 3 Selling Pillars Highlight Cards in Cover
    t_pillars = p1_cell.add_table(rows=1, cols=3)
    t_pillars.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_pillars.autofit = False
    pillars_data = [
        ('1. การถ่ายภาพพิธีหลวง', 'แม่นยำระเบียบสำนักพระราชวัง ทรงเกียรติยศสูงสุดแก่ผู้วายชนม์และวงศ์ตระกูล'),
        ('2. การถ่ายภาพพิธีจีน', 'รู้จริงเรื่องพิธีกงเต็ก เดินข้ามสะพาน ไม่พลาดช็อตสำคัญ บันทึกสายใยกตัญญู'),
        ('★ Live Streaming 65-75"', 'ถ่ายทอดสดคมชัดสูง จอใหญ่รอบศาลา พร้อมทีมงานวิศวกรดูแลฟรีตลอดงาน')
    ]
    for i, (p_head, p_desc) in enumerate(pillars_data):
        c = t_pillars.cell(0, i)
        c.width = Mm(58)
        set_cell_background(c, "171614")
        set_cell_margins(c, top=80, bottom=80, left=80, right=80)
        set_cell_borders(c,
            top={'sz': 6, 'color': 'C5A059'},
            bottom={'sz': 6, 'color': 'C5A059'},
            left={'sz': 6, 'color': 'C5A059'},
            right={'sz': 6, 'color': 'C5A059'}
        )
        p1 = c.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_after = Pt(4)
        r1 = p1.add_run(p_head)
        format_run(r1, size_pt=10.5, bold=True, color_rgb=C_GOLD)

        p2 = c.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(2)
        r2 = p2.add_run(p_desc)
        format_run(r2, size_pt=8.5, color_rgb=C_SEC)

    # Featured Hero Image for Cover
    p_cov_img = p1_cell.add_paragraph()
    p_cov_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_img.paragraph_format.space_before = Pt(16)
    p_cov_img.paragraph_format.space_after = Pt(6)
    cov_img_path = 'พิธีหลวง/S__246022154_0.jpg'
    if os.path.exists(cov_img_path):
        p_cov_img.add_run().add_picture(cov_img_path, width=Mm(170), height=Mm(85))

    p_cov_cap = p1_cell.add_paragraph()
    p_cov_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_cap.paragraph_format.space_after = Pt(14)
    r_cc = p_cov_cap.add_run('บันทึกทุกความทรงจำอันทรงคุณค่า ด้วยศาสตร์และศิลป์แห่งการถ่ายทอดภาพงานพิธีศพอย่างสมเกียรติ')
    format_run(r_cc, size_pt=9, italic=True, color_rgb=C_MUTED)

    # Cover Footer with 3 QR Codes
    t_qrs = p1_cell.add_table(rows=1, cols=3)
    t_qrs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_qrs.autofit = False
    qr_data = [
        ('qr_changphapngansop.png', 'ผลงานช่างภาพ', 'www.ช่างภาพงานศพ.com'),
        ('qr_rathcharot.png', 'เว็บไซต์ทางการ', 'www.ราชรถ.com'),
        ('qr_line.png', 'ติดต่อสอบถาม 24 ชม.', 'LINE : Rathcharot')
    ]
    for i, (qr_img, qr_t, qr_sub) in enumerate(qr_data):
        qc = t_qrs.cell(0, i)
        qc.width = Mm(58)
        set_cell_background(qc, "121110")
        set_cell_margins(qc, top=40, bottom=40, left=40, right=40)
        set_cell_borders(qc,
            top={'sz': 4, 'color': '8A6014'},
            bottom={'sz': 4, 'color': '8A6014'},
            left={'sz': 4, 'color': '8A6014'},
            right={'sz': 4, 'color': '8A6014'}
        )
        qp = qc.paragraphs[0]
        qp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp.paragraph_format.space_after = Pt(2)
        if os.path.exists(qr_img):
            qp.add_run().add_picture(qr_img, width=Mm(20), height=Mm(20))
        
        qp_text = qc.add_paragraph()
        qp_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp_text.paragraph_format.space_after = Pt(0)
        r_qt = qp_text.add_run(qr_t + '\n')
        format_run(r_qt, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)
        r_qs = qp_text.add_run(qr_sub)
        format_run(r_qs, size_pt=7.5, color_rgb=C_WHITE)

    # Category Page Generator Function
    def add_category_page(badge_text, title_text, subtitle_text, hook_title, hook_bullets, accent_box, hero_img, hero_cap, sub_imgs, page_num_str):
        doc.add_page_break()
        c = add_page_frame(doc)

        # 1. Header Banner
        p_badge = c.paragraphs[0]
        p_badge.paragraph_format.space_before = Pt(4)
        p_badge.paragraph_format.space_after = Pt(2)
        r_b = p_badge.add_run(f'  ◆ {badge_text}  ')
        format_run(r_b, size_pt=8.5, bold=True, color_rgb=C_GOLD_LIGHT)

        p_t = c.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(title_text)
        format_run(r_t, size_pt=18, bold=True, color_rgb=C_GOLD)

        p_s = c.add_paragraph()
        p_s.paragraph_format.space_before = Pt(0)
        p_s.paragraph_format.space_after = Pt(8)
        r_s = p_s.add_run(subtitle_text)
        format_run(r_s, size_pt=9.5, color_rgb=C_MUTED)

        # 2. Selling Points Box (Compact Table with Gold Left Bar)
        t_hook = c.add_table(rows=1, cols=1)
        t_hook.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_hook.autofit = False
        c_hook = t_hook.cell(0, 0)
        c_hook.width = Mm(176)
        set_cell_background(c_hook, "161513")
        set_cell_margins(c_hook, top=60, bottom=60, left=100, right=100)
        set_cell_borders(c_hook,
            left={'sz': 16, 'color': 'D4AF37'}, # Thick Gold Left Bar
            top={'sz': 4, 'color': '3D3522'},
            bottom={'sz': 4, 'color': '3D3522'},
            right={'sz': 4, 'color': '3D3522'}
        )

        p_h = c_hook.paragraphs[0]
        p_h.paragraph_format.space_before = Pt(0)
        p_h.paragraph_format.space_after = Pt(4)
        r_h = p_h.add_run(hook_title)
        format_run(r_h, size_pt=9.5, bold=True, color_rgb=C_GOLD_LIGHT)

        for b_title, b_desc in hook_bullets:
            p_b = c_hook.add_paragraph()
            p_b.paragraph_format.space_before = Pt(0)
            p_b.paragraph_format.space_after = Pt(2)
            r_dot = p_b.add_run('• ')
            format_run(r_dot, size_pt=9, bold=True, color_rgb=C_GOLD)
            r_bt = p_b.add_run(b_title + ' : ')
            format_run(r_bt, size_pt=9, bold=True, color_rgb=C_WHITE)
            r_bd = p_b.add_run(b_desc)
            format_run(r_bd, size_pt=9, color_rgb=C_SEC)

        if accent_box:
            acc_t, acc_d = accent_box
            p_acc = c_hook.add_paragraph()
            p_acc.paragraph_format.space_before = Pt(3)
            p_acc.paragraph_format.space_after = Pt(0)
            r_at = p_acc.add_run('★ ' + acc_t + ' — ')
            format_run(r_at, size_pt=8.5, bold=True, color_rgb=C_GOLD_LIGHT)
            r_ad = p_acc.add_run(acc_d)
            format_run(r_ad, size_pt=8.5, italic=True, color_rgb=C_MUTED)

        # 3. Magazine Catalog Layout: Hero Image (Large)
        p_hero = c.add_paragraph()
        p_hero.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hero.paragraph_format.space_before = Pt(8)
        p_hero.paragraph_format.space_after = Pt(2)
        if os.path.exists(hero_img):
            p_hero.add_run().add_picture(hero_img, width=Mm(176), height=Mm(74))

        # Hero Image Caption
        p_hcap = c.add_paragraph()
        p_hcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hcap.paragraph_format.space_before = Pt(0)
        p_hcap.paragraph_format.space_after = Pt(8)
        r_hc1 = p_hcap.add_run('【 ภาพหลัก 】 ')
        format_run(r_hc1, size_pt=8.5, bold=True, color_rgb=C_GOLD)
        r_hc2 = p_hcap.add_run(hero_cap)
        format_run(r_hc2, size_pt=8.5, color_rgb=C_SEC)

        # 4. Magazine Catalog Layout: 3 Sub-images in 3-column row
        t_sub = c.add_table(rows=1, cols=len(sub_imgs))
        t_sub.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_sub.autofit = False
        col_w = Mm(176 / len(sub_imgs))

        for j, (s_path, s_title, s_desc) in enumerate(sub_imgs):
            sc = t_sub.cell(0, j)
            sc.width = col_w
            set_cell_background(sc, "131211")
            set_cell_margins(sc, top=40, bottom=40, left=40, right=40)
            set_cell_borders(sc,
                top={'sz': 4, 'color': '8A6014'},
                bottom={'sz': 4, 'color': '8A6014'},
                left={'sz': 4, 'color': '8A6014'},
                right={'sz': 4, 'color': '8A6014'}
            )
            sp = sc.paragraphs[0]
            sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sp.paragraph_format.space_after = Pt(3)
            if os.path.exists(s_path):
                sp.add_run().add_picture(s_path, width=Mm(54), height=Mm(38))
            
            sp_cap = sc.add_paragraph()
            sp_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sp_cap.paragraph_format.space_after = Pt(0)
            r_st = sp_cap.add_run(f'ภาพที่ {j+2}: {s_title}\n')
            format_run(r_st, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)
            r_sd = sp_cap.add_run(s_desc)
            format_run(r_sd, size_pt=7.5, color_rgb=C_SEC)

        # 5. Footer Bar of Page
        p_ft = c.add_paragraph()
        p_ft.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ft.paragraph_format.space_before = Pt(8)
        p_ft.paragraph_format.space_after = Pt(0)
        r_fl = p_ft.add_run('ราชรถ & ช่างภาพงานศพ.com  •  โทร 085-999-2396  •  LINE : Rathcharot')
        format_run(r_fl, size_pt=8, color_rgb=C_MUTED)
        r_fr = p_ft.add_run(f'                                         แคตตาล็อกหน้า {page_num_str}')
        format_run(r_fr, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)

    # =========================================================================
    # PAGE 2: LIVE STREAMING & จอ 65-75 นิ้ว
    # =========================================================================
    print('Building Page 2: Live Streaming...')
    add_category_page(
        badge_text="SPECIAL HIGHLIGHT : LIVE STREAMING",
        title_text="บริการ Live Streaming ถ่ายทอดสด & จอ 65 - 75 นิ้ว",
        subtitle_text="ระบบถ่ายทอดสดระดับมืออาชีพ พร้อมติดตั้งจอขนาดใหญ่รอบศาลา และทีมงานดูแลฟรีตลอดงาน",
        hook_title="ทำไมต้องใช้บริการ Live Streaming กับเรา :",
        hook_bullets=[
            ("ฟรี! ทีมงานมืออาชีพดูแลตลอดงาน", "มีวิศวกร Switcher/OB ควบคุมการตัดสลับกล้องและสัญญาณให้ฟรีตลอดพิธี"),
            ("ติดตั้งจอคมชัดขนาดใหญ่ 65 - 75 นิ้ว", "แขกที่นั่งด้านนอกศาลามองเห็นพิธีการด้านในได้อย่างชัดเจนทุกมุมมอง"),
            ("ถ่ายทอดสดออนไลน์สัญญาณเสถียร", "รองรับญาติมิตรทั่วโลกให้ร่วมไว้อาลัยแบบ Real-Time คมชัดสูง"),
            ("บันทึกวิดีโอ Full HD / 4K ส่งมอบ", "ได้รับไฟล์วิดีโอบันทึกพิธีการฉบับสมบูรณ์สำหรับเก็บไว้เป็นเกียรติประวัติ")
        ],
        accent_box=("ระบบถ่ายทอดสดระดับมืออาชีพ", "ใช้อุปกรณ์ระดับสตูดิโอ พร้อมระบบสัญญาณอินเทอร์เน็ตสำรองหลายโครงข่าย มั่นใจได้ว่าภาพนิ่ง ไหลลื่น ไม่สะดุด"),
        hero_img="streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว/S__246046734_0.jpg",
        hero_cap="การติดตั้งจอถ่ายทอดสด 75 นิ้ว คมชัดรอบศาลา ช่วยให้ผู้ร่วมงานจำนวนมากมองเห็นพิธีการได้อย่างทั่วถึง",
        sub_imgs=[
            ("streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว/S__246046735_0.jpg",
             "มุมมองแขกนอกศาลา", "แขกด้านนอกมองเห็นพิธีการด้านในผ่านจอคมชัดระดับ Full HD"),
            ("streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว/S__246046736_0.jpg",
             "ระบบคอนโทรลเลอร์ OB", "โต๊ะควบคุม Switcher พร้อมวิศวกรดูแลสัญญาณให้ฟรีตลอดงาน"),
            ("streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว/S__246030381.jpg",
             "กล้องระดับสตูดิโอ", "การจัดมุมกล้องรอบทิศทาง เก็บครบทุกช่วงเวลาสำคัญในพิธี")
        ],
        page_num_str="02 / 09"
    )

    # =========================================================================
    # PAGE 3: MAIN PILLAR 1 - การถ่ายภาพงานพิธีหลวง
    # =========================================================================
    print('Building Page 3: Royal Ceremony...')
    add_category_page(
        badge_text="MAIN PILLAR 01 : ROYAL CEREMONY",
        title_text="การถ่ายภาพงานพิธีหลวง และเครื่องเกียรติยศ",
        subtitle_text="พระราชทานน้ำหลวงอาบศพ / พระราชทานเพลิงศพ / หีบเพลิงพระราชทาน / เครื่องเกียรติยศ",
        hook_title="ทำไมต้องใช้ช่างภาพมืออาชีพแบบเรา :",
        hook_bullets=[
            ("แม่นยำทุกลำดับพิธีการ", "เข้าใจขั้นตอนพิธีการของสำนักพระราชวังอย่างถูกต้อง ทั้งการรับน้ำหลวง หีบเพลิง และริ้วขบวน"),
            ("รู้มุมกล้องและกาลเทศะสูงสุด", "ทราบตำแหน่งยืนที่เหมาะสม ไม่เดินตัดหน้าขบวน ไม่บังสายตาประธาน และไม่ล้ำเขตพิธี"),
            ("บันทึกความสง่างามสมเกียรติยศ", "ถ่ายทอดภาพโกศ ลองใน หีบทองลายสลัก พวงมาลาพระราชทาน และริ้วขบวนได้อย่างวิจิตรงดงาม")
        ],
        accent_box=("มาตรฐานเกียรติยศสูงสุด", "ทีมงานแต่งกายชุดสูทสากลสีดำสุภาพ มีบัตรสื่อมวลชนพระราชพิธี และปฏิบัติงานด้วยความสำรวมสูงสุด"),
        hero_img="พิธีหลวง/S__246022154_0.jpg",
        hero_cap="พิธีพระราชทานน้ำหลวงอาบศพและขบวนอัญเชิญเครื่องเกียรติยศพระราชทานอย่างสมพระเกียรติ",
        sub_imgs=[
            ("พิธีหลวง/S__246022155_0.jpg", "เพลิงพระราชทาน", "การประกอบพิธีพระราชทานเพลิงศพและขบวนเชิญกล่องเพลิง"),
            ("พิธีหลวง/S__246022156_0.jpg", "พวงมาลาพระราชทาน", "บันทึกภาพพวงมาลาพระราชทานและเครื่องประกอบเกียรติยศ"),
            ("พิธีหลวง/S__246022158_0.jpg", "บรรยากาศทรงเกียรติ", "ถ่ายทอดความสง่างามและความภาคภูมิใจสูงสุดของวงศ์ตระกูล")
        ],
        page_num_str="03 / 09"
    )

    # =========================================================================
    # PAGE 4: MAIN PILLAR 2 - การถ่ายภาพพิธีจีน และธรรมเนียมปฏิบัติ
    # =========================================================================
    print('Building Page 4: Chinese Ceremony & Kong Tek...')
    add_category_page(
        badge_text="MAIN PILLAR 02 : CHINESE CEREMONY & KONG TEK",
        title_text="การถ่ายภาพพิธีจีน และธรรมเนียมปฏิบัติ",
        subtitle_text="พิธีกงเต็ก / ข้ามสะพานโอฆสงสาร / พิธีเคลื่อนย้าย / พิธีฝัง-เผา / สวดส่งวิญญาณ",
        hook_title="ทำไมต้องใช้ช่างภาพมืออาชีพแบบเรา :",
        hook_bullets=[
            ("รู้จริงเรื่องธรรมเนียมจีน", "เข้าใจลำดับพิธีกงเต็ก การเดินข้ามสะพานโอฆสงสาร การจุดไฟนำทาง และการไหว้ตามลำดับอาวุโส"),
            ("ไม่พลาดช็อตสำคัญเสี้ยววินาที", "พิธีกรรมจีนมีความรวดเร็วและต่อเนื่อง ช่างภาพผู้เชี่ยวชาญจะดักตำแหน่งล่วงหน้าได้ทันที"),
            ("เก็บครบทั้งความขลังและสายใย", "ถ่ายทอดรายละเอียดวิจิตรของเครื่องกระดาษ หีบไม้สักทอง และความกตัญญูของลูกหลาน")
        ],
        accent_box=("ความต่อเนื่องของพิธีกรรม", "ดูแลบันทึกภาพตลอดพิธีสวดกงเต็กจนถึงการส่งดวงวิญญาณและพิธีเผากระดาษเงินกระดาษทองอย่างสมบูรณ์แบบ"),
        hero_img="ธรรมเนียมจีน และพิธีกรรม/S__246030361.jpg",
        hero_cap="พิธีสวดกงเต็กและการนำทางดวงวิญญาณตามประเพณีจีนโบราณ บันทึกสายใยความผูกพันของลูกหลาน",
        sub_imgs=[
            ("ธรรมเนียมจีน และพิธีกรรม/S__246022288_0.jpg", "ข้ามสะพานโอฆสงสาร", "พิธีเดินข้ามสะพานส่งดวงวิญญาณสู่สุคติภูมิอย่างถูกต้อง"),
            ("ธรรมเนียมจีน และพิธีกรรม/S__246022295_0.jpg", "เครื่องกระดาษวิจิตร", "ถ่ายทอดรายละเอียดบ้านกงเต็ก รถ และสิ่งของเครื่องใช้บรรพบุรุษ"),
            ("ธรรมเนียมจีน และพิธีกรรม/S__246030353_0.jpg", "พิธีเผากระดาษทอง", "การเผาส่งมอบเครื่องกงเต็กเพื่อความสุขสมบูรณ์ในสัมปรายภพ")
        ],
        page_num_str="04 / 09"
    )

    # =========================================================================
    # PAGE 5: MAIN PILLAR 3.1 - การถ่ายภาพพิธีสวดพระอภิธรรม
    # =========================================================================
    print('Building Page 5: Evening Chanting Ceremony...')
    add_category_page(
        badge_text="MAIN PILLAR 03 : EVENING CHANTING CEREMONY",
        title_text="การถ่ายภาพพิธีสวดพระอภิธรรม",
        subtitle_text="บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน ทั้งความสงบ อบอุ่น และสมเกียรติ",
        hook_title="ทำไมต้องใช้ช่างภาพมืออาชีพแบบเรา :",
        hook_bullets=[
            ("เก็บครบทุกมิติแห่งความอาลัย", "บันทึกภาพครอบครัว ญาติสนิท มิตรสหาย และบุคคลสำคัญที่มาร่วมแสดงความเสียใจ"),
            ("แสงสีนุ่มนวล คลาสสิก สมเกียรติ", "ปรับแต่งโทนภาพอย่างประณีต ดึงอารมณ์ความสงบ สำรวม และคงคุณค่าเหนือกาลเวลา"),
            ("ไม่รบกวนสมาธิในพิธีสวด", "ใช้ชัตเตอร์เงียบ (Silent Shutter) จัดแสงและจังหวะก้าวเดินอย่างสุภาพ ไม่รบกวนพระสงฆ์และแขก")
        ],
        accent_box=("ความทรงจำอันทรงคุณค่า", "ส่งมอบภาพถ่ายที่เป็นตัวแทนแห่งความรัก ความเคารพ และการระลึกถึงจากทุกคนที่รักผู้วายชนม์"),
        hero_img="บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน/S__246022190_0.jpg",
        hero_cap="บรรยากาศพิธีสวดพระอภิธรรมและความสงบงดงามสมเกียรติ ท่ามกลางญาติมิตรและบุคคลสำคัญ",
        sub_imgs=[
            ("บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน/S__246022191_0.jpg", "การฟังสวดพระอภิธรรม", "ภาพประธานในพิธีและผู้ร่วมงานร่วมฟังสวดพระอภิธรรม"),
            ("บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน/S__246022192_0.jpg", "ดอกไม้หน้าหีบศพ", "ความงดงามของการจัดวางดอกไม้และภาพถ่ายผู้วายชนม์"),
            ("บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน/S__246022193_0.jpg", "ถวายจตุปัจจัยไทยธรรม", "พิธีถวายไทยธรรมแด่พระสงฆ์เพื่ออุทิศส่วนกุศลอย่างสมบูรณ์")
        ],
        page_num_str="05 / 09"
    )

    # =========================================================================
    # PAGE 6: MAIN PILLAR 3.2 - ความทรงจำวันสุดท้าย (วันฌาปนกิจ)
    # =========================================================================
    print('Building Page 6: Cremation Day...')
    add_category_page(
        badge_text="MAIN PILLAR 03 : CREMATION DAY",
        title_text="เก็บทุกความทรงจำในวันสุดท้าย (วันฌาปนกิจ)",
        subtitle_text="พิธีเคลื่อนร่าง / เวียนเมรุ 3 รอบ / ทอดผ้าบังสุกุล / พิธีวางดอกไม้จันทน์ / ประชุมเพลิง",
        hook_title="ทำไมต้องใช้ช่างภาพมืออาชีพแบบเรา :",
        hook_bullets=[
            ("บันทึกทุกความทรงจำที่ไม่อาจย้อนกลับ", "วันฌาปนกิจมีพิธีการกระชับและอารมณ์ความรู้สึกเข้มข้น ช่างภาพมืออาชีพจะเก็บได้ครบทุกช็อตสำคัญ"),
            ("ลำดับภาพเป็นเรื่องราว (Storytelling)", "ถ่ายทอดริ้วขบวนเวียนเมรุ การแสดงความอาลัย และจังหวะสุดท้ายของการส่งร่างอย่างละเมียดละไม"),
            ("มุมมองครบครันทั้งมุมกว้างและโคลสอัพ", "เก็บทั้งภาพรวมความยิ่งใหญ่ของงาน และภาพหยดน้ำตาแห่งความรักและความกตัญญู")
        ],
        accent_box=("ช่วงเวลาสำคัญที่สุดของครอบครัว", "ให้เจ้าภาพได้บอกลาบุคคลอันเป็นที่รักอย่างเต็มหัวใจ โดยมีทีมงานมืออาชีพบันทึกประวัติศาสตร์ครอบครัวแทนท่าน"),
        hero_img="เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย/S__246022253_0.jpg",
        hero_cap="ริ้วขบวนเวียนรอบเมรุ 3 รอบ อัญเชิญร่างผู้วายชนม์สู่จิตกาธานด้วยความเคารพสูงสุด",
        sub_imgs=[
            ("เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย/S__246022254_0.jpg", "ทอดผ้าไตรบังสุกุล", "พิธีทอดผ้าบังสุกุลโดยประธานในพิธีและแขกผู้มีเกียรติ"),
            ("เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย/S__246022255_0.jpg", "วางดอกไม้จันทน์", "การแสดงความระลึกถึงและกราบลาเป็นครั้งสุดท้าย"),
            ("เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย/S__246022256_0.jpg", "ภาพประวัติศาสตร์ครอบครัว", "บันทึกสายใยความรักและความผูกพันของวงศ์ตระกูล")
        ],
        page_num_str="06 / 09"
    )

    # =========================================================================
    # PAGE 7: MAIN PILLAR 3.3 - พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติ
    # =========================================================================
    print('Building Page 7: Ashes Scattering Ceremony...')
    add_category_page(
        badge_text="MAIN PILLAR 03 : ASHES SCATTERING CEREMONY",
        title_text="พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติ",
        subtitle_text="พิธีเก็บอัฐิ / อัญเชิญลงเรือ / บูชาแม่ย่านาง / โปรยดอกไม้และส่งดวงวิญญาณสู่สายน้ำอันสงบ",
        hook_title="ทำไมต้องใช้ช่างภาพมืออาชีพแบบเรา :",
        hook_bullets=[
            ("บันทึกความบริสุทธิ์แห่งการส่งสู่สัมปรายภพ", "ถ่ายทอดภาพสายน้ำ แสงแดด และสายลม เป็นสัญลักษณ์แห่งการปล่อยวางและความสุขสงบนิรันดร์"),
            ("ชำนาญการถ่ายภาพบนเรือและผืนน้ำ", "เข้าใจการทรงตัว ทิศทางแสงแดด และการเคลื่อนไหวของเรือ ได้ภาพคมชัด ไม่เบลอ ไม่เอียง"),
            ("บันทึกทุกขั้นตอนการประกอบพิธีทางน้ำ", "เก็บครบทั้งพิธีไหว้แม่ย่านางเรือ การโปรยเหรียญ การลอยกระทง และการโปรยดอกไม้ส่งอัฐิ")
        ],
        accent_box=("ความสุขสงบสู่สุคติภูมิ", "ภาพถ่ายพิธีลอยอังคารจะช่วยปลอบประโลมจิตใจครอบครัวว่า ผู้วายชนม์ได้เดินทางสู่ภพภูมิที่สงบและร่มเย็นแล้ว"),
        hero_img="ลอยอังคาร/S__246022308_0.jpg",
        hero_cap="พิธีลอยอังคารกลางสายน้ำอันสงบ โปรยกลีบดอกไม้มงคลส่งดวงวิญญาณสู่สุคติภูมิ",
        sub_imgs=[
            ("ลอยอังคาร/S__246022309_0.jpg", "อัญเชิญอัฐิลงเรือ", "ครอบครัวอัญเชิญลุ้งอัฐิลงเรือสู่จุดประกอบพิธีกลางสายน้ำ"),
            ("ลอยอังคาร/S__246022310_0.jpg", "พิธีขอขมาแม่ย่านาง", "การประกอบพิธีกล่าวคำขอขมาและบูชาสิ่งศักดิ์สิทธิ์ประจำสายน้ำ"),
            ("ลอยอังคาร/S__246022311_0.jpg", "ลอยกระทงส่งวิญญาณ", "การส่งกระทงดอกไม้อำลาและส่งคำอธิษฐานสู่สรวงสวรรค์")
        ],
        page_num_str="07 / 09"
    )

    # =========================================================================
    # PAGE 8: มาตรฐานทีมช่างภาพ & จรรยาบรรณวิชาชีพ
    # =========================================================================
    print('Building Page 8: Professional Team & Ethics...')
    add_category_page(
        badge_text="PROFESSIONAL TEAM & ETHICS",
        title_text="มาตรฐานทีมช่างภาพ & จรรยาบรรณวิชาชีพ",
        subtitle_text="เบื้องหลังความไว้วางใจจากครอบครัวชั้นนำและองค์กรระดับประเทศตลอด 24 ชั่วโมง",
        hook_title="ทำไมต้องไว้วางใจทีมช่างภาพเรา :",
        hook_bullets=[
            ("แต่งกายชุดสูทสากลสีดำ สำรวม 100%", "สุภาพ เรียบร้อย อบรมมารยาทการไหว้และการประสานงานกับเจ้าหน้าที่พิธีการทุกฝ่าย"),
            ("อุปกรณ์เกรด Professional Dual-Slot", "ใช้กล้องระดับโปร บันทึกไฟล์สำรองคู่ขนาน ป้องกันเหตุสุดวิสัย มั่นใจได้ 100%"),
            ("ส่งมอบไฟล์ภาพรวดเร็ว แสงสีนุ่มนวล", "คุมโทนสีให้สมเกียรติ คลาสสิก คงคุณค่าแห่งความทรงจำไปตลอดกาล"),
            ("มีประสบการณ์เฉพาะทางงานศพทุกรูปแบบ", "เข้าใจความต้องการของเจ้าภาพ ไม่รบกวนเวลาอันมีค่า และพร้อมสแตนด์บายตลอด 24 ชม.")
        ],
        accent_box=("ความสบายใจสูงสุดของเจ้าภาพ", "ไม่ต้องกังวลเรื่องการแต่งกาย มารยาท หรือจังหวะการบันทึกภาพ ให้ครอบครัวได้ต้อนรับแขกอย่างเต็มที่"),
        hero_img="โปรไฟล์ช่างภาพ/S__246030375_0.jpg",
        hero_cap="ทีมงานช่างภาพมืออาชีพในชุดสูทสากลสีดำสุภาพ ปฏิบัติงานด้วยความสำรวมสูงสุดในทุกขั้นตอน",
        sub_imgs=[
            ("โปรไฟล์ช่างภาพ/S__246030374_0.jpg", "รู้มุมกล้องกาลเทศะ", "ทราบตำแหน่งยืนที่เหมาะสม ไม่บังสายตาประธานในพิธี"),
            ("โปรไฟล์ช่างภาพ/S__246030377_0.jpg", "อุปกรณ์โปร Dual-Slot", "กล้องและเลนส์ระดับสตูดิโอ มีระบบสำรองข้อมูลคู่ขนาน"),
            ("โปรไฟล์ช่างภาพ/S__246046733_0.jpg", "แต่งแสงสีสมเกียรติ", "การปรับแต่งแสงสีให้คงความคลาสสิก สมเกียรติยศ")
        ],
        page_num_str="08 / 09"
    )

    # =========================================================================
    # PAGE 9: CLOSING & CONTACT HUB (Exact Match to Flyer)
    # =========================================================================
    print('Building Page 9: Closing & Contact Hub...')
    doc.add_page_break()
    p9_cell = add_page_frame(doc)

    # Logo ราชรถ
    p9_logo = p9_cell.paragraphs[0]
    p9_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_logo.paragraph_format.space_before = Pt(8)
    p9_logo.paragraph_format.space_after = Pt(2)
    if os.path.exists('พิธีหลวง/S__246022151_0.png'):
        p9_logo.add_run().add_picture('พิธีหลวง/S__246022151_0.png', width=Mm(36))

    p9_title = p9_cell.add_paragraph()
    p9_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_title.paragraph_format.space_before = Pt(0)
    p9_title.paragraph_format.space_after = Pt(6)
    r_pt = p9_title.add_run('ราชรถ')
    format_run(r_pt, size_pt=26, bold=True, color_rgb=C_GOLD)

    # Divider line
    p9_div = p9_cell.add_paragraph()
    p9_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_div.paragraph_format.space_before = Pt(0)
    p9_div.paragraph_format.space_after = Pt(10)
    r_div2 = p9_div.add_run('──────────  ◇  ──────────')
    format_run(r_div2, size_pt=10, color_rgb=C_GOLD_BORDER)

    # Services List (Exact Text from Flyer)
    services_items = [
        "บริการในงานศพทั่วประเทศ 24 ชั่วโมง",
        "หีบศพมาตรฐาน",
        "เคลื่อนย้ายศพทั่วประเทศ",
        "ออแกไนซ์งานศพครบวงจร",
        "ให้บริการครบทุกขั้นตอน ทั้งไทย-จีน โดยทีมงานมืออาชีพ",
        "ดูแลตั้งแต่เคลื่อนย้ายร่าง ถึงลอยอังคาร",
        "จัดดอกไม้หน้าหีบศพ / วันฌาปนกิจ",
        "แพคเกจหีบศพพร้อมดอกไม้ครบวงจร พร้อมอุปกรณ์",
        "บริการช่างภาพภาพนิ่ง วิดีโอซีนีม่า และ Live Streaming ถ่ายทอดสด"
    ]
    t_svc = p9_cell.add_table(rows=1, cols=1)
    t_svc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_svc.autofit = False
    c_svc = t_svc.cell(0, 0)
    c_svc.width = Mm(160)
    set_cell_background(c_svc, "141312")
    set_cell_margins(c_svc, top=80, bottom=80, left=100, right=100)
    set_cell_borders(c_svc,
        top={'sz': 6, 'color': 'C5A059'},
        bottom={'sz': 6, 'color': 'C5A059'},
        left={'sz': 6, 'color': 'C5A059'},
        right={'sz': 6, 'color': 'C5A059'}
    )
    for k, s_item in enumerate(services_items):
        sp = c_svc.paragraphs[0] if k == 0 else c_svc.add_paragraph()
        sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sp.paragraph_format.space_before = Pt(1)
        sp.paragraph_format.space_after = Pt(2)
        r_si = sp.add_run(s_item)
        if k == 0 or k == len(services_items) - 1:
            format_run(r_si, size_pt=11, bold=True, color_rgb=C_GOLD_LIGHT)
        else:
            format_run(r_si, size_pt=10, color_rgb=C_WHITE)

    # 3 QR Codes Hub
    p9_qr_title = p9_cell.add_paragraph()
    p9_qr_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_qr_title.paragraph_format.space_before = Pt(12)
    p9_qr_title.paragraph_format.space_after = Pt(6)
    r_qt_main = p9_qr_title.add_run('สแกน QR Code เพื่อชมผลงาน เยี่ยมชมเว็บไซต์ หรือติดต่อสอบถาม')
    format_run(r_qt_main, size_pt=10, bold=True, color_rgb=C_GOLD_LIGHT)

    t9_qrs = p9_cell.add_table(rows=1, cols=3)
    t9_qrs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t9_qrs.autofit = False
    for i, (qr_img, qr_t, qr_sub) in enumerate(qr_data):
        qc = t9_qrs.cell(0, i)
        qc.width = Mm(58)
        set_cell_background(qc, "161513")
        set_cell_margins(qc, top=60, bottom=60, left=40, right=40)
        set_cell_borders(qc,
            top={'sz': 6, 'color': 'C5A059'},
            bottom={'sz': 6, 'color': 'C5A059'},
            left={'sz': 6, 'color': 'C5A059'},
            right={'sz': 6, 'color': 'C5A059'}
        )
        qp = qc.paragraphs[0]
        qp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp.paragraph_format.space_after = Pt(4)
        if os.path.exists(qr_img):
            qp.add_run().add_picture(qr_img, width=Mm(28), height=Mm(28))
        
        qp_text = qc.add_paragraph()
        qp_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp_text.paragraph_format.space_after = Pt(0)
        r_qt = qp_text.add_run(qr_t + '\n')
        format_run(r_qt, size_pt=9.5, bold=True, color_rgb=C_GOLD)
        r_qs = qp_text.add_run(qr_sub)
        format_run(r_qs, size_pt=8.5, color_rgb=C_WHITE)

    # Contact Details
    p9_cont = p9_cell.add_paragraph()
    p9_cont.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_cont.paragraph_format.space_before = Pt(14)
    p9_cont.paragraph_format.space_after = Pt(2)
    r_call = p9_cont.add_run('📞 โทร: 085-999-2396 (ตลอด 24 ชั่วโมง)   |   💬 LINE : Rathcharot\n')
    format_run(r_call, size_pt=11, bold=True, color_rgb=C_GOLD_LIGHT)
    r_soc = p9_cont.add_run('🎵 Tiktok: Rathcharot   •   📷 IG: Rathcharot   •   🌐 www.rathcharot.com   •   www.ช่างภาพงานศพ.com')
    format_run(r_soc, size_pt=9, color_rgb=C_SEC)

    # Save Document
    output_filename = "Rathcharot_Funeral_Catalog_A4.docx"
    doc.save(output_filename)
    print(f"Catalog created successfully: {output_filename}")

if __name__ == "__main__":
    create_catalog()
