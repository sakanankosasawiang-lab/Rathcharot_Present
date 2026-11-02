import os
import io
import json
import docx
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from PIL import Image

def generate_full_catalog():
    print("Starting generation of Full Comprehensive Word Catalog (A4)...")
    doc = docx.Document()

    # 1. Page Setup: A4 Portrait, 11mm margins for maximum printable canvas
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(11)
        section.bottom_margin = Mm(11)
        section.left_margin = Mm(11)
        section.right_margin = Mm(11)
        section.header_distance = Mm(0)
        section.footer_distance = Mm(0)

    # 2. Dark Background Setup (Obsidian Black: #0C0C0E)
    background = parse_xml(f'<w:background {nsdecls("w")} w:color="0C0C0E"/>')
    doc.element.insert(0, background)
    doc.settings.element.append(parse_xml(f'<w:displayBackgroundShape {nsdecls("w")}/>'))

    # Colors
    C_GOLD = (212, 175, 55)
    C_GOLD_LIGHT = (244, 228, 166)
    C_GOLD_BORDER = (197, 160, 89)
    C_WHITE = (255, 255, 255)
    C_MUTED = (163, 157, 146)
    C_SEC = (226, 221, 213)

    # Helper functions
    def set_cell_background(cell, fill_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        cell._tc.get_or_add_tcPr().append(tcMar)

    def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
        tcPr = cell._tc.get_or_add_tcPr()
        borders = parse_xml(f'<w:tcBorders {nsdecls("w")}/>')
        edges = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
        for edge, border in edges.items():
            if border:
                val = border.get('val', 'single')
                sz = border.get('sz', 4)
                col = border.get('color', 'C5A059')
                b_xml = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="{val}" w:sz="{sz}" w:space="0" w:color="{col}"/>')
                borders.append(b_xml)
            else:
                b_xml = parse_xml(f'<w:{edge} {nsdecls("w")} w:val="none"/>')
                borders.append(b_xml)
        tcPr.append(borders)

    def format_run(run, font_name='Prompt', size_pt=9.5, bold=False, italic=False, color_rgb=(255, 255, 255)):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = RGBColor(*color_rgb)
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_name}" w:hAnsi="{font_name}" w:cs="{font_name}"/>')
        rPr.append(rFonts)

    def get_optimized_image_stream(img_path, max_dim=1400, quality=84):
        if not os.path.exists(img_path):
            return None, 1.0
        try:
            with Image.open(img_path) as im:
                w, h = im.size
                aspect = w / h if h > 0 else 1.0
                if img_path.lower().endswith('.png'):
                    buf = io.BytesIO()
                    im.save(buf, format='PNG')
                    buf.seek(0)
                    return buf, aspect
                else:
                    ratio = min(max_dim / w, max_dim / h) if max(w, h) > max_dim else 1.0
                    new_w, new_h = max(1, int(w * ratio)), max(1, int(h * ratio))
                    im_res = im.resize((new_w, new_h), Image.Resampling.LANCZOS) if ratio < 1.0 else im
                    if im_res.mode != 'RGB':
                        im_res = im_res.convert('RGB')
                    buf = io.BytesIO()
                    im_res.save(buf, format='JPEG', quality=quality, optimize=True)
                    buf.seek(0)
                    return buf, aspect
        except Exception as e:
            print(f'Error optimizing image {img_path}: {e}')
            return None, 1.0

    def add_picture_with_optional_link(paragraph, img_source, link_target=None, width=None, height=None):
        if link_target:
            part = paragraph.part
            normalized_link = link_target.replace('\\', '/')
            r_id = part.relate_to(normalized_link, docx.opc.constants.RELATIONSHIP_TYPE.HYPERLINK, is_external=True)
            hyperlink = parse_xml(f'<w:hyperlink {nsdecls("w")} {nsdecls("r")} r:id="{r_id}" w:history="1"/>')
            run = paragraph.add_run()
            if width and height:
                run.add_picture(img_source, width=width, height=height)
            elif width:
                run.add_picture(img_source, width=width)
            elif height:
                run.add_picture(img_source, height=height)
            else:
                run.add_picture(img_source)
            hyperlink.append(run._r)
            paragraph._p.append(hyperlink)
            return run
        else:
            run = paragraph.add_run()
            if width and height:
                run.add_picture(img_source, width=width, height=height)
            elif width:
                run.add_picture(img_source, width=width)
            elif height:
                run.add_picture(img_source, height=height)
            else:
                run.add_picture(img_source)
            return run

    def add_page_frame(doc, border_color='C5A059', border_sz=12):
        table = doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.cell(0, 0)
        cell.width = Mm(188)
        set_cell_background(cell, "0F0E0D")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        set_cell_borders(cell,
            top={'sz': border_sz, 'color': border_color},
            bottom={'sz': border_sz, 'color': border_color},
            left={'sz': border_sz, 'color': border_color},
            right={'sz': border_sz, 'color': border_color}
        )
        return cell

    # Load images manifest
    with open('images_manifest.json', encoding='utf-8-sig') as f:
        manifest = json.load(f)

    current_page_num = 1

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    print("Building Page 1: Cover Page...")
    p1_cell = add_page_frame(doc)

    p_logo = p1_cell.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(8)
    p_logo.paragraph_format.space_after = Pt(10)
    if os.path.exists('พิธีหลวง/S__246022151_0.png'):
        add_picture_with_optional_link(p_logo, 'พิธีหลวง/S__246022151_0.png', link_target='https://www.ราชรถ.com', width=Mm(28))
    r_div = p_logo.add_run('   |   ')
    format_run(r_div, size_pt=20, color_rgb=C_GOLD_BORDER)
    if os.path.exists('พิธีหลวง/S__246022150_0.png'):
        add_picture_with_optional_link(p_logo, 'พิธีหลวง/S__246022150_0.png', link_target='https://www.ช่างภาพงานศพ.com', width=Mm(28))

    p_title = p1_cell.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_t = p_title.add_run('ราชรถ & ช่างภาพงานศพ.com')
    format_run(r_t, size_pt=25, bold=True, color_rgb=C_GOLD)

    p_sub = p1_cell.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(8)
    r_sub = p_sub.add_run('บริการถ่ายภาพงานพิธี • ถ่ายวิดีโองานพิธี • บริการจอทีวี 65" & Live Streaming ถ่ายทอดสด 24 ชม.')
    format_run(r_sub, size_pt=10.5, color_rgb=C_GOLD_LIGHT)

    # Core Philosophy Box
    t_phil = p1_cell.add_table(rows=1, cols=1)
    t_phil.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_phil.autofit = False
    c_phil = t_phil.cell(0, 0)
    c_phil.width = Mm(176)
    set_cell_background(c_phil, "181510")
    set_cell_margins(c_phil, top=50, bottom=50, left=80, right=80)
    set_cell_borders(c_phil,
        top={'sz': 4, 'color': '8A6014'},
        bottom={'sz': 4, 'color': '8A6014'},
        left={'sz': 6, 'color': 'D4AF37'},
        right={'sz': 4, 'color': '8A6014'}
    )
    p_ph = c_phil.paragraphs[0]
    p_ph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ph.paragraph_format.space_before = Pt(2)
    p_ph.paragraph_format.space_after = Pt(2)
    r_ph1 = p_ph.add_run('“ บันทึกเกียรติยศและประวัติศาสตร์ของครอบครัว ”\n')
    format_run(r_ph1, size_pt=10.5, bold=True, color_rgb=C_GOLD)
    r_ph2 = p_ph.add_run('งานศพคือพิธีสำคัญครั้งสุดท้ายในชีวิต ภาพถ่ายและวิดีโอคุณภาพสูงจะช่วยสืบสานเรื่องราว ความทรงจำ และคุณงามความดีของผู้จากไป\nโดยทีมช่างภาพบันทึกประวัติศาสตร์ชาติ ผู้ผ่านงานพิธีหลวงและพระราชพิธีสำคัญ ด้วยมาตรฐานละเอียด สำรวม และสมเกียรติสูงสุด')
    format_run(r_ph2, size_pt=8.5, color_rgb=C_SEC)

    # 3 Core Service Pillars (ตามข้อความของคุณอมเรศ)
    t_pil = p1_cell.add_table(rows=1, cols=3)
    t_pil.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_pil.autofit = False
    pillars = [
        ("บริการถ่ายภาพงานพิธี", "ช่างภาพมืออาชีพประสบการณ์สูง เก็บบรรยากาศภายในงานอย่างสมเกียรติ จัดองค์ประกอบภาพอย่างสวยงาม"),
        ("บริการถ่ายวิดีโองานพิธี", "บันทึกไฟล์ที่มีคุณภาพสูง คมชัด 4K / Full HD ตัดต่ออย่างประณีตโดยทีมงานมืออาชีพ"),
        ("บริการจอทีวี 65\" & ถ่ายทอดสด", "ระบบสัญญาณระดับมืออาชีพ คมชัด เสถียร จาก Hollyland และ DJI พร้อมทีมงานเทคนิคดูแลตลอดงาน")
    ]
    for i, (p_head, p_desc) in enumerate(pillars):
        c = t_pil.cell(0, i)
        c.width = Mm(58)
        set_cell_background(c, "131211")
        set_cell_margins(c, top=40, bottom=40, left=40, right=40)
        set_cell_borders(c,
            top={'sz': 4, 'color': '8A6014'},
            bottom={'sz': 4, 'color': '8A6014'},
            left={'sz': 4, 'color': '8A6014'},
            right={'sz': 4, 'color': '8A6014'}
        )
        p1 = c.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(p_head)
        format_run(r1, size_pt=9.5, bold=True, color_rgb=C_GOLD)

        p2 = c.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(2)
        r2 = p2.add_run(p_desc)
        format_run(r2, size_pt=7.5, color_rgb=C_SEC)

    # Cover Hero Image (Clickable)
    p_cov_img = p1_cell.add_paragraph()
    p_cov_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_img.paragraph_format.space_before = Pt(10)
    p_cov_img.paragraph_format.space_after = Pt(2)
    cov_img_path = 'พิธีหลวง/S__246022154_0.jpg'
    if os.path.exists(cov_img_path):
        cov_s, _ = get_optimized_image_stream(cov_img_path, max_dim=1600, quality=86)
        if cov_s:
            add_picture_with_optional_link(p_cov_img, cov_s, link_target=cov_img_path, width=Mm(174), height=Mm(80))

    p_cov_cap = p1_cell.add_paragraph()
    p_cov_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_cap.paragraph_format.space_after = Pt(8)
    r_cc = p_cov_cap.add_run('บันทึกทุกความทรงจำอันทรงคุณค่า ด้วยศาสตร์และศิลป์แห่งการถ่ายทอดภาพงานพิธีศพอย่างสมเกียรติ (คลิกที่ภาพเพื่อเปิดดูภาพต้นฉบับ)')
    format_run(r_cc, size_pt=8, italic=True, color_rgb=C_MUTED)

    # 3 QR Codes
    t_qrs = p1_cell.add_table(rows=1, cols=3)
    t_qrs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_qrs.autofit = False
    qr_data = [
        ('qr_changphapngansop.png', 'ผลงานช่างภาพ', 'www.ช่างภาพงานศพ.com', 'https://www.ช่างภาพงานศพ.com'),
        ('qr_rathcharot.png', 'เว็บไซต์ทางการ', 'www.ราชรถ.com', 'https://www.rathcharot.com'),
        ('qr_line.png', 'ติดต่อสอบถาม 24 ชม.', 'LINE : Rathcharot', 'https://line.me/ti/p/~Rathcharot')
    ]
    for i, (qr_img, qr_t, qr_sub, qr_url) in enumerate(qr_data):
        qc = t_qrs.cell(0, i)
        qc.width = Mm(58)
        set_cell_background(qc, "121110")
        set_cell_margins(qc, top=35, bottom=35, left=35, right=35)
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
            add_picture_with_optional_link(qp, qr_img, link_target=qr_url, width=Mm(18), height=Mm(18))
        
        qp_text = qc.add_paragraph()
        qp_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp_text.paragraph_format.space_after = Pt(0)
        r_qt = qp_text.add_run(qr_t + '\n')
        format_run(r_qt, size_pt=7.5, bold=True, color_rgb=C_GOLD_LIGHT)
        r_qs = qp_text.add_run(qr_sub)
        format_run(r_qs, size_pt=7, color_rgb=C_WHITE)

    # Helper function for adding the Main Showcase Page of a category
    def add_category_showcase_page(badge_text, title_text, subtitle_text, hook_title, hook_bullets, accent_box, hero_img, hero_cap, sub_imgs, folder_total_count):
        nonlocal current_page_num
        current_page_num += 1
        doc.add_page_break()
        c = add_page_frame(doc, border_color='C5A059', border_sz=8)

        # Header Badge
        p_badge = c.paragraphs[0]
        p_badge.paragraph_format.space_before = Pt(4)
        p_badge.paragraph_format.space_after = Pt(2)
        r_b = p_badge.add_run(f'●  {badge_text}  ●')
        format_run(r_b, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)

        # Title
        p_t = c.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(2)
        r_tit = p_t.add_run(title_text)
        format_run(r_tit, size_pt=18, bold=True, color_rgb=C_GOLD)

        # Subtitle
        p_subt = c.add_paragraph()
        p_subt.paragraph_format.space_before = Pt(0)
        p_subt.paragraph_format.space_after = Pt(6)
        r_st = p_subt.add_run(subtitle_text)
        format_run(r_st, size_pt=8.5, color_rgb=C_SEC)

        # Selling Hook Section
        p_hk = c.add_paragraph()
        p_hk.paragraph_format.space_before = Pt(0)
        p_hk.paragraph_format.space_after = Pt(2)
        r_hkt = p_hk.add_run(hook_title)
        format_run(r_hkt, size_pt=9.5, bold=True, color_rgb=C_GOLD_LIGHT)

        for b_title, b_desc in hook_bullets:
            p_bl = c.add_paragraph()
            p_bl.paragraph_format.left_indent = Mm(4)
            p_bl.paragraph_format.space_before = Pt(1)
            p_bl.paragraph_format.space_after = Pt(1)
            r_bt = p_bl.add_run('◆ ' + b_title + ' : ')
            format_run(r_bt, size_pt=8.2, bold=True, color_rgb=C_WHITE)
            r_bd = p_bl.add_run(b_desc)
            format_run(r_bd, size_pt=8.2, color_rgb=C_SEC)

        # Accent Box
        if accent_box:
            acc_t, acc_d = accent_box
            p_acc = c.add_paragraph()
            p_acc.paragraph_format.space_before = Pt(3)
            p_acc.paragraph_format.space_after = Pt(0)
            r_at = p_acc.add_run('★ ' + acc_t + ' — ')
            format_run(r_at, size_pt=8.2, bold=True, color_rgb=C_GOLD_LIGHT)
            r_ad = p_acc.add_run(acc_d)
            format_run(r_ad, size_pt=8, italic=True, color_rgb=C_MUTED)

        # Hero Image (Featured Large & Clickable)
        p_hero = c.add_paragraph()
        p_hero.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hero.paragraph_format.space_before = Pt(6)
        p_hero.paragraph_format.space_after = Pt(2)
        if os.path.exists(hero_img):
            h_s, _ = get_optimized_image_stream(hero_img, max_dim=1600, quality=86)
            if h_s:
                add_picture_with_optional_link(p_hero, h_s, link_target=hero_img, width=Mm(176), height=Mm(72))

        p_hcap = c.add_paragraph()
        p_hcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hcap.paragraph_format.space_before = Pt(0)
        p_hcap.paragraph_format.space_after = Pt(6)
        r_hc1 = p_hcap.add_run('【 ภาพหลักประจำหมวด 】 ')
        format_run(r_hc1, size_pt=8, bold=True, color_rgb=C_GOLD)
        r_hc2 = p_hcap.add_run(hero_cap + ' (คลิกดูภาพใหญ่)')
        format_run(r_hc2, size_pt=8, color_rgb=C_SEC)

        # 3 Sub-images row (Clickable)
        t_sub = c.add_table(rows=1, cols=len(sub_imgs))
        t_sub.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_sub.autofit = False
        col_w = Mm(176 / len(sub_imgs))

        for j, (s_path, s_title, s_desc) in enumerate(sub_imgs):
            sc = t_sub.cell(0, j)
            sc.width = col_w
            set_cell_background(sc, "131211")
            set_cell_margins(sc, top=30, bottom=30, left=30, right=30)
            set_cell_borders(sc,
                top={'sz': 4, 'color': '8A6014'},
                bottom={'sz': 4, 'color': '8A6014'},
                left={'sz': 4, 'color': '8A6014'},
                right={'sz': 4, 'color': '8A6014'}
            )
            sp = sc.paragraphs[0]
            sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sp.paragraph_format.space_after = Pt(2)
            if os.path.exists(s_path):
                sub_s, _ = get_optimized_image_stream(s_path, max_dim=900, quality=84)
                if sub_s:
                    add_picture_with_optional_link(sp, sub_s, link_target=s_path, width=Mm(54), height=Mm(38))
            
            sp_cap = sc.add_paragraph()
            sp_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            sp_cap.paragraph_format.space_after = Pt(0)
            r_st = sp_cap.add_run(f'ภาพที่ {j+2}: {s_title}\n')
            format_run(r_st, size_pt=7.5, bold=True, color_rgb=C_GOLD_LIGHT)
            r_sd = sp_cap.add_run(s_desc)
            format_run(r_sd, size_pt=7, color_rgb=C_SEC)

        # Footer
        p_ft = c.add_paragraph()
        p_ft.paragraph_format.space_before = Pt(6)
        p_ft.paragraph_format.space_after = Pt(0)
        r_fl = p_ft.add_run(f'หมวดนี้มีผลงานจริงทั้งหมด {folder_total_count} ภาพ (ชมภาพต่อเนื่องในหน้าถัดไป)  •  โทร 085-999-2396')
        format_run(r_fl, size_pt=7.5, color_rgb=C_MUTED)
        r_fr = p_ft.add_run(f'  [หน้า {current_page_num}]')
        format_run(r_fr, size_pt=7.5, bold=True, color_rgb=C_GOLD_LIGHT)

    # Helper function for adding continuation gallery pages
    def add_continuation_gallery_pages(cat_name, remaining_images_with_captions, category_title, badge_text):
        nonlocal current_page_num
        chunk_size = 4
        chunks = [remaining_images_with_captions[i:i + chunk_size] for i in range(0, len(remaining_images_with_captions), chunk_size)]

        for chunk_idx, img_chunk in enumerate(chunks):
            current_page_num += 1
            doc.add_page_break()
            c = add_page_frame(doc, border_color='8A6014', border_sz=6)

            # Mini header
            p_top = c.paragraphs[0]
            p_top.paragraph_format.space_before = Pt(2)
            p_top.paragraph_format.space_after = Pt(1)
            r_tb = p_top.add_run(f'●  {badge_text}  •  แกลเลอรีภาพผลงานจริง (ตอนที่ {chunk_idx + 1} จาก {len(chunks)})  ●')
            format_run(r_tb, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)

            p_tt = c.add_paragraph()
            p_tt.paragraph_format.space_before = Pt(0)
            p_tt.paragraph_format.space_after = Pt(2)
            r_tit = p_tt.add_run(f'{category_title} (คลังภาพผลงานต่อเนื่อง)')
            format_run(r_tit, size_pt=13, bold=True, color_rgb=C_GOLD)

            p_hint = c.add_paragraph()
            p_hint.paragraph_format.space_before = Pt(0)
            p_hint.paragraph_format.space_after = Pt(4)
            r_hint = p_hint.add_run('※ คลิกที่รูปภาพใดก็ได้ เพื่อเปิดชมไฟล์ภาพต้นฉบับขนาดใหญ่ คมชัดระดับ High-Resolution')
            format_run(r_hint, size_pt=7.5, italic=True, color_rgb=C_MUTED)

            # 2x2 Grid Table
            t_grid = c.add_table(rows=2, cols=2)
            t_grid.alignment = WD_TABLE_ALIGNMENT.CENTER
            t_grid.autofit = False

            for idx, img_info in enumerate(img_chunk):
                row_idx = idx // 2
                col_idx = idx % 2
                cell = t_grid.cell(row_idx, col_idx)
                cell.width = Mm(88)

                set_cell_background(cell, "121110")
                set_cell_margins(cell, top=30, bottom=30, left=30, right=30)
                set_cell_borders(cell,
                    top={'sz': 4, 'color': 'C5A059'},
                    bottom={'sz': 4, 'color': 'C5A059'},
                    left={'sz': 4, 'color': 'C5A059'},
                    right={'sz': 4, 'color': 'C5A059'}
                )

                img_path, img_caption = img_info
                full_img_path = os.path.join(cat_name, img_path) if not os.path.isabs(img_path) and not os.path.exists(img_path) else img_path

                cp = cell.paragraphs[0]
                cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                cp.paragraph_format.space_after = Pt(2)

                if os.path.exists(full_img_path):
                    try:
                        s_img, aspect = get_optimized_image_stream(full_img_path, max_dim=1400, quality=84)
                        if s_img:
                            if aspect >= 1.0:
                                add_picture_with_optional_link(cp, s_img, link_target=full_img_path, width=Mm(81), height=Mm(round(81 / aspect, 2)))
                            else:
                                add_picture_with_optional_link(cp, s_img, link_target=full_img_path, height=Mm(66), width=Mm(round(66 * aspect, 2)))
                        else:
                            cp.add_run(f'[ภาพ: {img_path}]')
                    except Exception as e:
                        cp.add_run(f'[ภาพ: {img_path}]')

                # Caption
                p_c = cell.add_paragraph()
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_before = Pt(2)
                p_c.paragraph_format.space_after = Pt(0)
                r_ct = p_c.add_run('【 ภาพผลงานจริง 】 ')
                format_run(r_ct, size_pt=7.5, bold=True, color_rgb=C_GOLD_LIGHT)
                r_cd = p_c.add_run(img_caption)
                format_run(r_cd, size_pt=7.2, color_rgb=C_SEC)
                r_ck = p_c.add_run(' (คลิกดูภาพใหญ่)')
                format_run(r_ck, size_pt=6.5, italic=True, color_rgb=C_MUTED)

            # If chunk has only 1, 2, or 3 images, style remaining empty cells
            if len(img_chunk) < 4:
                for empty_idx in range(len(img_chunk), 4):
                    r_i = empty_idx // 2
                    c_i = empty_idx % 2
                    empty_cell = t_grid.cell(r_i, c_i)
                    empty_cell.width = Mm(88)
                    set_cell_background(empty_cell, "0F0E0D")
                    set_cell_margins(empty_cell, top=30, bottom=30, left=30, right=30)
                    set_cell_borders(empty_cell,
                        top={'sz': 2, 'color': '554018'},
                        bottom={'sz': 2, 'color': '554018'},
                        left={'sz': 2, 'color': '554018'},
                        right={'sz': 2, 'color': '554018'}
                    )
                    ep = empty_cell.paragraphs[0]
                    ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    ep_run = ep.add_run('ราชรถ & ช่างภาพงานศพ.com\nพร้อมให้บริการทั่วประเทศ 24 ชั่วโมง\nโทร 085-999-2396')
                    format_run(ep_run, size_pt=8, italic=True, color_rgb=C_MUTED)

            # Continuation Footer
            p_cft = c.add_paragraph()
            p_cft.paragraph_format.space_before = Pt(6)
            p_cft.paragraph_format.space_after = Pt(0)
            r_cfl = p_cft.add_run('ราชรถ & ช่างภาพงานศพ.com  •  www.ช่างภาพงานศพ.com  •  โทร 085-999-2396')
            format_run(r_cfl, size_pt=7.5, color_rgb=C_MUTED)
            r_cfr = p_cft.add_run(f'  [หน้า {current_page_num}]')
            format_run(r_cfr, size_pt=7.5, bold=True, color_rgb=C_GOLD_LIGHT)

    # =========================================================================
    # CATEGORY 1: บริการจอทีวี 65" & ถ่ายทอดสด (Live Stream & Display)
    # =========================================================================
    cat1_name = "streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว"
    cat1_files = manifest[cat1_name]
    print(f"Building Category 1: Live Stream & Display ({len(cat1_files)} images)...")

    c1_showcase_keys = ['S__246046734_0.jpg', 'S__246046735_0.jpg', 'S__246046736_0.jpg', 'S__246030381.jpg']
    add_category_showcase_page(
        badge_text="SPECIAL HIGHLIGHT : LIVE STREAM & DISPLAY",
        title_text="บริการจอทีวี 65\" & ถ่ายทอดสด (Live Stream & Display)",
        subtitle_text="ถ่ายทอดสดระบบสัญญาณระดับมืออาชีพด้วยอุปกรณ์มาตรฐาน คมชัด เสถียร จาก Hollyland และ DJI พร้อมทีมงานเทคนิคดูแลตลอดงาน",
        hook_title="ทำไมต้องเลือกบริการจอทีวี 65\" & ถ่ายทอดสดกับเรา :",
        hook_bullets=[
            ("จอ 65 นิ้ว ภาพคมชัด High-Definition", "เพื่อชม VDO พิธีการอย่างชัดเจนในพิธีสวดพระอภิธรรมหรืองานฌาปนกิจแบบ Real-Time รอบศาลา"),
            ("ระบบสัญญาณระดับมืออาชีพ คมชัด เสถียร", "ใช้อุปกรณ์มาตรฐานระดับสากลจาก Hollyland และ DJI ภาพลื่นไหล คมชัด ไม่สะดุด"),
            ("พร้อมอุปกรณ์และทีมงานเทคนิคดูแลตลอดงาน", "มีทีมงานเทคนิคและ Switcher/OB ควบคุมตัดสลับกล้องและดูแลระบบสัญญาณให้ฟรีตลอดพิธี"),
            ("บันทึกไฟล์วิดีโอคุณภาพสูง ส่งมอบครบถ้วน", "บันทึกเทปพิธีการแบบ Full HD / 4K สำหรับเก็บไว้เป็นเกียรติประวัติแห่งความทรงจำ")
        ],
        accent_box=("อุปกรณ์มาตรฐานระดับโลก", "ระบบสัญญาณถ่ายทอดสด คมชัด เสถียร จาก Hollyland และ DJI เพื่อให้ญาติมิตรทั่วโลกได้ร่วมพิธีแบบ Real-Time อย่างสมเกียรติ"),
        hero_img=os.path.join(cat1_name, 'S__246046734_0.jpg'),
        hero_cap="การติดตั้งจอถ่ายทอดสด 65-75 นิ้ว คมชัดรอบศาลา ช่วยให้ผู้ร่วมงานจำนวนมากมองเห็นพิธีการได้อย่างทั่วถึง",
        sub_imgs=[
            (os.path.join(cat1_name, 'S__246046735_0.jpg'), "มุมมองแขกนอกศาลา", "แขกด้านนอกมองเห็นพิธีการด้านในผ่านจอคมชัดระดับ Full HD"),
            (os.path.join(cat1_name, 'S__246046736_0.jpg'), "ระบบคอนโทรลเลอร์ OB", "โต๊ะควบคุม Switcher พร้อมวิศวกรดูแลสัญญาณให้ฟรีตลอดงาน"),
            (os.path.join(cat1_name, 'S__246030381.jpg'), "กล้องระดับสตูดิโอ", "การจัดมุมกล้องรอบทิศทาง เก็บครบทุกช่วงเวลาสำคัญในพิธี")
        ],
        folder_total_count=len(cat1_files)
    )

    c1_remaining = [
        (f, "บริการจอทีวี 65 นิ้ว ภาพคมชัด High-Definition & ถ่ายทอดสดสัญญาณเสถียรจาก Hollyland และ DJI โดยทีมงานเทคนิคดูแลตลอดงาน")
        for f in cat1_files if f not in c1_showcase_keys
    ]
    add_continuation_gallery_pages(cat1_name, c1_remaining, "บริการจอทีวี 65\" & ถ่ายทอดสด (Live Stream & Display)", "LIVE STREAM & DISPLAY")

    # =========================================================================
    # CATEGORY 2: การถ่ายภาพงานพิธีหลวง (Royal Ceremony)
    # =========================================================================
    cat2_name = "พิธีหลวง"
    cat2_files = manifest[cat2_name]
    print(f"Building Category 2: Royal Ceremony ({len(cat2_files)} images)...")

    c2_showcase_keys = ['S__246022154_0.jpg', 'S__246022155_0.jpg', 'S__246022156_0.jpg', 'S__246022158_0.jpg']
    add_category_showcase_page(
        badge_text="MAIN PILLAR 01 : ROYAL CEREMONY",
        title_text="การถ่ายภาพงานพิธีหลวง และเครื่องเกียรติยศพระราชทาน",
        subtitle_text="ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ ผู้ผ่านงานพิธีหลวงและพระราชพิธีสำคัญ ด้วยมาตรฐานละเอียด สำรวม และสมเกียรติสูงสุด",
        hook_title="“เกียรติยศสูงสุดแห่งชีวิต” และประวัติศาสตร์ของครอบครัว :",
        hook_bullets=[
            ("การบันทึกทางประวัติศาสตร์สูงสุด", "ในพิธีพระราชทานน้ำหลวงอาบศพ พระราชทานโกศศพ พระราชทานเพลิงศพ และการเวียนเมรุ คือ 'เกียรติยศสูงสุดแห่งชีวิต'"),
            ("ได้รับพระมหากรุณาธิคุณโปรดเกล้าฯ", "พระราชทานแก่ผู้วายชนม์และวงศ์ตระกูล เพื่อเป็นบันทึกเกียรติยศและประวัติศาสตร์อันทรงคุณค่าสืบไป"),
            ("ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ", "ผู้ผ่านงานพิธีหลวงและพระราชพิธีสำคัญ ด้วยมาตรฐานละเอียด สำรวม และถูกต้องตามระเบียบแบบแผน"),
            ("บันทึกเกียรติยศและประวัติศาสตร์ของครอบครัว", "งานศพคือพิธีสำคัญครั้งสุดท้ายในชีวิต ภาพถ่ายและวิดีโอคุณภาพสูงจะช่วยสืบสานเรื่องราวและคุณงามความดี")
        ],
        accent_box=("เกียรติยศสูงสุดแห่งชีวิต", "การบันทึกภาพพิธีพระราชทานน้ำหลวงอาบศพ พระราชทานโกศศพ พระราชทานเพลิงศพ และการเวียนเมรุ คือการบันทึกประวัติศาสตร์อันทรงเกียรติสูงสุดของวงศ์ตระกูล"),
        hero_img=os.path.join(cat2_name, 'S__246022154_0.jpg'),
        hero_cap="ริ้วขบวนพระราชทานเกียรติยศและหีบเพลิงพระราชทาน บันทึกอย่างถูกต้องตามระเบียบแบบแผนราชสำนัก",
        sub_imgs=[
            (os.path.join(cat2_name, 'S__246022155_0.jpg'), "หีบเพลิงพระราชทาน", "การรับพระราชทานหีบเพลิงและเครื่องขมาอย่างสมพระเกียรติ"),
            (os.path.join(cat2_name, 'S__246022156_0.jpg'), "ริ้วขบวนเวียนเมรุ", "ความสง่างามและความพร้อมเพรียงของขบวนเกียรติยศ"),
            (os.path.join(cat2_name, 'S__246022158_0.jpg'), "พระราชทานเพลิงศพ", "พิธีการสำคัญสูงสุดแห่งชีวิตของผู้วายชนม์และวงศ์ตระกูล")
        ],
        folder_total_count=len(cat2_files)
    )

    c2_remaining_captions = [
        "การบันทึกทางประวัติศาสตร์สูงสุดในพิธีพระราชทานน้ำหลวงอาบศพ พระราชทานโกศศพ และพระราชทานเพลิงศพ",
        "เกียรติยศสูงสุดแห่งชีวิต ที่ได้รับพระมหากรุณาธิคุณโปรดเกล้าฯ พระราชทานแก่ผู้วายชนม์และวงศ์ตระกูล",
        "ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ ผู้ผ่านงานพิธีหลวงและพระราชพิธีสำคัญอย่างสมเกียรติ",
        "บันทึกเกียรติยศและประวัติศาสตร์ของครอบครัว เพื่อสืบสานคุณงามความดีของผู้จากไปชั่วนิรันดร์",
        "พิธีอัญเชิญเครื่องเกียรติยศพระราชทานและหีบเพลิงพระราชทานอย่างถูกต้องตามโบราณราชประเพณี",
        "ความพร้อมเพรียงของริ้วขบวนอิสริยยศและการเวียนรอบเมรุอย่างสง่างาม",
        "ประธานในพิธีประกอบพิธีพระราชทานเพลิงศพด้วยความสำรวมและสมเกียรติยศสูงสุด",
        "ภาพประวัติศาสตร์อันทรงคุณค่าที่ส่งต่อความภาคภูมิใจสู่ลูกหลานและวงศ์ตระกูลสืบไป",
        "ความประณีตวิจิตรของเครื่องราชอิสริยาภรณ์ โกศพระราชทาน และเหรียญตราเกียรติยศ",
        "ช่างภาพมืออาชีพในชุดสูทสากลสีดำ ปฏิบัติหน้าที่ด้วยความสำรวมและรู้กาลเทศะสูงสุด"
    ]
    c2_remaining = [
        (f, c2_remaining_captions[idx % len(c2_remaining_captions)])
        for idx, f in enumerate(cat2_files) if f not in c2_showcase_keys
    ]
    add_continuation_gallery_pages(cat2_name, c2_remaining, "การถ่ายภาพงานพิธีหลวง และเครื่องเกียรติยศ", "ROYAL CEREMONY")

    # =========================================================================
    # CATEGORY 3: พิธีกงเต็ก และธรรมเนียมจีน (Chinese Ceremony & Kong Tek)
    # =========================================================================
    cat3_name = "ธรรมเนียมจีน และพิธีกรรม"
    cat3_files = manifest[cat3_name]
    print(f"Building Category 3: Chinese Ceremony & Kong Tek ({len(cat3_files)} images)...")

    c3_showcase_keys = ['S__246030361.jpg', 'S__246022288_0.jpg', 'S__246022295_0.jpg', 'S__246030353.jpg']
    add_category_showcase_page(
        badge_text="MAIN PILLAR 02 : CHINESE CEREMONY & KONG TEK",
        title_text="การถ่ายภาพพิธีกงเต็ก และธรรมเนียมปฏิบัติประเพณีจีน",
        subtitle_text="พิธีกงเต็ก คือพิธีอุทิศส่วนบุญส่วนกุศลและส่งดวงวิญญาณสู่สุคติในแบบมงคลตามประเพณีจีน ทุกขั้นตอนเต็มไปด้วยความหมาย ความศรัทธา และสายสัมพันธ์ของครอบครัว",
        hook_title="ทำไมต้องใช้ช่างภาพผู้เชี่ยวชาญพิธีกงเต็กแบบเรา :",
        hook_bullets=[
            ("เปี่ยมด้วยความหมาย ความศรัทธา และสายสัมพันธ์", "พิธีกงเต็กคือการอุทิศบุญกุศลและส่งดวงวิญญาณสู่สุคติในแบบมงคล ทุกขั้นตอนสะท้อนความกตัญญูของลูกหลาน"),
            ("เข้าใจขั้นตอนและลำดับพิธีจีนอย่างลึกซึ้ง", "เข้าใจพิธีสวดกงเต็ก การเดินข้ามสะพานโอฆสงสาร การจุดไฟนำทาง และการไหว้ตามลำดับอาวุโส"),
            ("ไม่พลาดช็อตสำคัญที่มีความต่อเนื่องรวดเร็ว", "พิธีกรรมจีนมีความรวดเร็วและต่อเนื่อง ช่างภาพผู้เชี่ยวชาญจะดักตำแหน่งล่วงหน้าได้อย่างแม่นยำ"),
            ("เก็บครบทั้งความวิจิตรและสายสัมพันธ์ครอบครัว", "ถ่ายทอดรายละเอียดวิจิตรของเครื่องกระดาษ บ้านกงเต็ก หีบไม้ และความกตัญญูของลูกหลานทุกรุ่น")
        ],
        accent_box=("ส่งดวงวิญญาณสู่สุคติ", "พิธีกงเต็กทุกขั้นตอนเต็มไปด้วยความหมาย ความศรัทธา และสายสัมพันธ์ของครอบครัว บันทึกทุกช่วงเวลาแห่งการส่งดวงวิญญาณสู่สุคติภูมิอย่างสมบูรณ์แบบ"),
        hero_img=os.path.join(cat3_name, 'S__246030361.jpg'),
        hero_cap="พิธีสวดกงเต็กและการนำทางดวงวิญญาณตามประเพณีจีนโบราณ บันทึกสายใยความผูกพันของลูกหลาน",
        sub_imgs=[
            (os.path.join(cat3_name, 'S__246022288_0.jpg'), "ข้ามสะพานโอฆสงสาร", "พิธีเดินข้ามสะพานส่งดวงวิญญาณสู่สุคติภูมิอย่างถูกต้อง"),
            (os.path.join(cat3_name, 'S__246022295_0.jpg'), "เครื่องกระดาษวิจิตร", "ถ่ายทอดรายละเอียดบ้านกงเต็ก รถ และสิ่งของเครื่องใช้บรรพบุรุษ"),
            (os.path.join(cat3_name, 'S__246030353_0.jpg'), "พิธีเผากระดาษทอง", "การเผาส่งมอบเครื่องกงเต็กเพื่อความสุขสมบูรณ์ในสัมปรายภพ")
        ],
        folder_total_count=len(cat3_files)
    )

    c3_remaining_captions = [
        "พิธีกงเต็ก คือพิธีอุทิศส่วนบุญส่วนกุศลและส่งดวงวิญญาณสู่สุคติในแบบมงคลตามประเพณีจีน",
        "ทุกขั้นตอนเต็มไปด้วยความหมาย ความศรัทธา และสายสัมพันธ์อันลึกซึ้งของครอบครัว",
        "ลูกหลานร่วมพิธีเดินข้ามสะพานโอฆสงสารแสดงความกตัญญูกตเวทิตา",
        "ความประณีตของบ้านกงเต็ก รถยนต์ และสิ่งของเครื่องใช้ส่งมอบบรรพบุรุษ",
        "การประกอบพิธีของพระสงฆ์จีนนิกายและซินแสตามโบราณประเพณีอย่างเคร่งครัด",
        "พิธีเคารพศพตามลำดับชั้นอาวุโสของลูก หลาน เหลน",
        "พิธีเผากระดาษเงินกระดาษทองและเครื่องกงเต็กสู่สัมปรายภพ",
        "บันทึกสายใยความรัก ความอบอุ่น และความผูกพันอันแน่นแฟ้นของครอบครัวตระกูลจีน",
        "การนำขบวนเคลื่อนย้ายร่างสู่พิธีการขั้นต่อไปอย่างราบรื่นและถูกต้องตามประเพณี"
    ]
    c3_remaining = [
        (f, c3_remaining_captions[idx % len(c3_remaining_captions)])
        for idx, f in enumerate(cat3_files) if f not in c3_showcase_keys
    ]
    add_continuation_gallery_pages(cat3_name, c3_remaining, "การถ่ายภาพพิธีจีน และพิธีกงเต็ก", "CHINESE CEREMONY & KONG TEK")

    # =========================================================================
    # CATEGORY 4: พิธีสวดพระอภิธรรม & บรรยากาศ (Atmosphere & Candid Moments)
    # =========================================================================
    cat4_name = "บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน"
    cat4_files = manifest[cat4_name]
    print(f"Building Category 4: Atmosphere & Evening Chanting ({len(cat4_files)} images)...")

    c4_showcase_keys = ['S__246022190_0.jpg', 'S__246022191_0.jpg', 'S__246022192_0.jpg', 'S__246022193_0.jpg']
    add_category_showcase_page(
        badge_text="MAIN PILLAR 03 : ATMOSPHERE & EVENING CHANTING",
        title_text="การถ่ายภาพพิธีสวดพระอภิธรรม และภาพบรรยากาศงานพิธี",
        subtitle_text="ภาพบรรยากาศในงานศพ (Atmosphere & Candid Moments) ไม่ใช่แค่การถ่ายภาพคนมาร่วมงาน แต่คือการบันทึก 'สายสัมพันธ์ ความรัก และอารมณ์ความรู้สึก' ของการจากไปชั่วนิรันดร์",
        hook_title="ทำไมภาพบรรยากาศและแคนดิดถึงมีความหมายสูงสุด :",
        hook_bullets=[
            ("บันทึกสายสัมพันธ์ ความรัก และอารมณ์ความรู้สึก", "ไม่ใช่แค่การถ่ายภาพคนมาร่วมงาน แต่คือการบันทึกสายใย แววตา การให้กำลังใจ และความรักอันบริสุทธิ์"),
            ("สืบสานเรื่องราวและคุณงามความดีของผู้จากไป", "งานศพคือพิธีสำคัญครั้งสุดท้ายในชีวิต ภาพถ่ายและวิดีโอคุณภาพสูงจะช่วยสืบสานความทรงจำตลอดกาล"),
            ("บริการถ่ายภาพงานพิธีโดยมืออาชีพประสบการณ์สูง", "เก็บบรรยากาศภายในงานอย่างสมเกียรติ จัดองค์ประกอบภาพอย่างสวยงาม แสงสีนุ่มนวล คลาสสิก"),
            ("ปฏิบัติงานด้วยความสุภาพ สำรวม ไม่รบกวนพิธี", "ใช้ชัตเตอร์เงียบ (Silent Shutter) จัดแสงและจังหวะก้าวเดินอย่างสุภาพ ไม่รบกวนพระสงฆ์และแขกผู้ใหญ่")
        ],
        accent_box=("บันทึกสายสัมพันธ์และความรู้สึก", "ภาพบรรยากาศในงานศพคือการบันทึก 'สายสัมพันธ์ ความรัก และอารมณ์ความรู้สึก' ของการจากไปชั่วนิรันดร์ เพื่อให้ความทรงจำอันงดงามคงอยู่ตลอดไป"),
        hero_img=os.path.join(cat4_name, 'S__246022190_0.jpg'),
        hero_cap="บรรยากาศพิธีสวดพระอภิธรรมและความสงบงดงามสมเกียรติ ท่ามกลางญาติมิตรและบุคคลสำคัญ",
        sub_imgs=[
            (os.path.join(cat4_name, 'S__246022191_0.jpg'), "การฟังสวดพระอภิธรรม", "ภาพประธานในพิธีและผู้ร่วมงานร่วมฟังสวดพระอภิธรรมอย่างสำรวม"),
            (os.path.join(cat4_name, 'S__246022192_0.jpg'), "ดอกไม้หน้าหีบศพ", "ความงดงามของการจัดวางดอกไม้และภาพถ่ายผู้วายชนม์"),
            (os.path.join(cat4_name, 'S__246022193_0.jpg'), "ถวายจตุปัจจัยไทยธรรม", "พิธีถวายไทยธรรมแด่พระสงฆ์เพื่ออุทิศส่วนกุศลอย่างสมบูรณ์")
        ],
        folder_total_count=len(cat4_files)
    )

    c4_remaining_captions = [
        "ภาพบรรยากาศในงานศพ (Atmosphere & Candid Moments) บันทึกสายสัมพันธ์ ความรัก และอารมณ์ความรู้สึก",
        "งานศพคือพิธีสำคัญครั้งสุดท้ายในชีวิต ภาพถ่ายและวิดีโอคุณภาพสูงช่วยสืบสานความทรงจำชั่วนิรันดร์",
        "ช่างภาพมืออาชีพประสบการณ์สูง เก็บบรรยากาศภายในงานอย่างสมเกียรติ จัดองค์ประกอบสวยงาม",
        "บรรยากาศความสงบ สำรวม ในช่วงพิธีสวดพระอภิธรรมประจำค่ำคืน",
        "พระสงฆ์เจริญพระพุทธมนต์และแสดงพระธรรมเทศนา",
        "ประธานในพิธีจุดธูปเทียนบูชาพระรัตนตรัยและเคารพผู้วายชนม์",
        "บันทึกภาพบุคคลสำคัญ ญาติสนิท มิตรสหายที่มาร่วมแสดงความอาลัย",
        "การจัดตกแต่งดอกไม้สดหน้าหีบศพอย่างวิจิตรตระการตา",
        "พิธีทอดผ้าบังสุกุลและถวายจตุปัจจัยไทยธรรมแด่พระสงฆ์",
        "ภาพหมู่ครอบครัวเจ้าภาพร่วมกับผู้มีเกียรติที่มาร่วมแสดงความอาลัย",
        "รายละเอียดความประณีตของหีบศพและภาพถ่ายที่ระลึกผู้วายชนม์",
        "ภาพความอบอุ่นและการให้กำลังใจแก่ครอบครัวเจ้าภาพในวาระสำคัญ"
    ]
    c4_remaining = [
        (f, c4_remaining_captions[idx % len(c4_remaining_captions)])
        for idx, f in enumerate(cat4_files) if f not in c4_showcase_keys
    ]
    add_continuation_gallery_pages(cat4_name, c4_remaining, "การถ่ายภาพพิธีสวดพระอภิธรรม และภาพบรรยากาศ", "ATMOSPHERE & CHANTING")

    # =========================================================================
    # CATEGORY 5: วันฌาปนกิจ / บันทึกความทรงจำวันสุดท้าย (Cremation Day)
    # =========================================================================
    cat5_name = "เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย"
    cat5_files = manifest[cat5_name]
    print(f"Building Category 5: Cremation Day & Final Farewell ({len(cat5_files)} images)...")

    c5_showcase_keys = ['S__246022245_0.jpg', 'S__246022246_0.jpg', 'S__246022247_0.jpg', 'S__246022248_0.jpg']
    add_category_showcase_page(
        badge_text="MAIN PILLAR 04 : CREMATION DAY & FAREWELL",
        title_text="พิธีฌาปนกิจ และบันทึกความทรงจำวันสุดท้าย",
        subtitle_text="งานศพคือพิธีสำคัญครั้งสุดท้ายในชีวิต ภาพถ่ายและวิดีโอคุณภาพสูงจะช่วยสืบสานเรื่องราว ความทรงจำ และคุณงามความดีของผู้จากไป",
        hook_title="บันทึกประวัติศาสตร์ครั้งสำคัญที่สุดของครอบครัว :",
        hook_bullets=[
            ("พิธีการอันทรงเกียรติและสมบูรณ์แบบ", "บันทึกขบวนเคลื่อนศพ การเวียนรอบเมรุ พิธีทอดผ้าบังสุกุล และการขึ้นวางดอกไม้จันทน์"),
            ("บริการถ่ายภาพและวิดีโอคุณภาพสูง", "บันทึกไฟล์คุณภาพสูงระดับ 4K / Full HD ตัดต่อโดยมืออาชีพเพื่อส่งมอบเป็นเกียรติประวัติ"),
            ("จัดองค์ประกอบภาพอย่างสวยงามและสมเกียรติ", "คุมโทนสีสุภาพ สง่างาม ถ่ายทอดความอาลัย ความเคารพ และความรักสูงสุด"),
            ("ทีมงานมีประสบการณ์เฉพาะทางงานศพ", "ทราบจุดยืนและกาลเทศะในทุกบริเวณฌาปนสถาน ประสานงานกับเจ้าหน้าที่อย่างราบรื่น")
        ],
        accent_box=("มรดกแห่งความทรงจำ", "สืบสานเรื่องราวและคุณงามความดีของผู้วายชนม์ ส่งต่อเป็นประวัติศาสตร์อันทรงคุณค่าแก่วงศ์ตระกูล"),
        hero_img=os.path.join(cat5_name, 'S__246022245_0.jpg'),
        hero_cap="การเคลื่อนขบวนศพเวียนรอบเมรุ 3 รอบเพื่อรำลึกถึงพระอนิจจังอย่างสมเกียรติยศ",
        sub_imgs=[
            (os.path.join(cat5_name, 'S__246022246_0.jpg'), "พิธีทอดผ้าบังสุกุล", "ประธานในพิธีและบุคคลสำคัญทอดผ้าบังสุกุลหน้าเมรุ"),
            (os.path.join(cat5_name, 'S__246022247_0.jpg'), "วางดอกไม้จันทน์", "ช่วงเวลาแห่งการกราบลาครั้งสุดท้ายด้วยความอาลัยยิ่ง"),
            (os.path.join(cat5_name, 'S__246022248_0.jpg'), "พิธีประชุมเพลิง", "ส่งดวงวิญญาณอันเป็นที่รักสู่สุคติภูมิชั่วนิรันดร์")
        ],
        folder_total_count=len(cat5_files)
    )

    c5_remaining_captions = [
        "บันทึกเกียรติยศและประวัติศาสตร์ของครอบครัวในพิธีสำคัญครั้งสุดท้ายในชีวิต",
        "ถ่ายทอดสายสัมพันธ์ ความรัก และคุณงามความดีของผู้จากไปเพื่อเป็นมรดกความทรงจำ",
        "การจัดริ้วขบวนเชิญหีบศพเวียนรอบเมรุด้วยความเคารพและสมเกียรติ",
        "ภาพประธานในพิธีและบุคคลสำคัญร่วมทอดผ้ามหาบังสุกุล",
        "ช่วงเวลาแห่งการวางดอกไม้จันทน์กราบลาผู้วายชนม์ด้วยความเคารพรักอย่างสุดซึ้ง",
        "การบันทึกภาพมุมกว้างแสดงเกียรติยศและความพร้อมเพรียงของผู้ร่วมงาน",
        "ภาพแคนดิดความรัก ความอบอุ่น และการปลอบประโลมครอบครัวเจ้าภาพ",
        "พิธีการบนเมรุที่จัดวางองค์ประกอบอย่างสวยงาม ทรงคุณค่าเหนือกาลเวลา"
    ]
    c5_remaining = [
        (f, c5_remaining_captions[idx % len(c5_remaining_captions)])
        for idx, f in enumerate(cat5_files) if f not in c5_showcase_keys
    ]
    add_continuation_gallery_pages(cat5_name, c5_remaining, "พิธีฌาปนกิจ และความทรงจำวันสุดท้าย", "CREMATION & FAREWELL")

    # =========================================================================
    # CATEGORY 6: พิธีลอยอังคาร (Ashes Scattering Ceremony)
    # =========================================================================
    cat6_name = "ลอยอังคาร"
    cat6_files = manifest[cat6_name]
    print(f"Building Category 6: Ashes Scattering ({len(cat6_files)} images)...")

    c6_showcase_keys = ['S__246022307_0.jpg', 'S__246022308_0.jpg', 'S__246022309_0.jpg', 'S__246022310_0.jpg']
    add_category_showcase_page(
        badge_text="MAIN PILLAR 05 : ASHES SCATTERING CEREMONY",
        title_text="พิธีลอยอังคาร และการส่งดวงวิญญาณสู่สุคติภูมิ",
        subtitle_text="การดูแลบันทึกภาพต่อเนื่องจนถึงพิธีการขั้นสุดท้ายอย่างสงบ บริสุทธิ์ สว่าง และร่มเย็น ท่ามกลางธรรมชาติ",
        hook_title="ความต่อเนื่องและการดูแลอย่างครบวงจร :",
        hook_bullets=[
            ("ดูแลต่อเนื่องจนถึงแม่น้ำและทะเล", "บันทึกพิธีการบนเรือลอยอังคาร พิธีไหว้แม่ย่านางและเจ้าแม่คงคาอย่างถูกต้องครบถ้วน"),
            ("ภาพมุมมองสงบ สว่าง และร่มเย็น", "ถ่ายทอดความหมายแห่งการปล่อยวาง การโปรยดอกไม้ และการส่งดวงวิญญาณสู่ความสงบ"),
            ("เก็บบันทึกความอบอุ่นของครอบครัวอย่างใกล้ชิด", "ถ่ายทอดความรัก การอธิษฐาน และสายใยผูกพันในวาระสุดท้ายอย่างนุ่มนวล"),
            ("ช่างภาพมีความชำนาญบนเรือและคลื่นลม", "ทรงตัวและจัดมุมกล้องได้มั่นคง ปลอดภัย พร้อมบันทึกภาพคมชัดทุกช่วงเวลา")
        ],
        accent_box=("ส่งสู่สุคติภูมิอันร่มเย็น", "บันทึกพิธีการขั้นสุดท้ายอันงดงาม เพื่อให้ครอบครัวได้ระลึกถึงด้วยความสงบใจและเปี่ยมด้วยความหวัง"),
        hero_img=os.path.join(cat6_name, 'S__246022307_0.jpg'),
        hero_cap="การประกอบพิธีลอยอังคารกลางสายน้ำอันสงบ อัญเชิญอังคารลงสู่กระแสน้ำอย่างบริสุทธิ์",
        sub_imgs=[
            (os.path.join(cat6_name, 'S__246022308_0.jpg'), "ไหว้แม่ย่านางเรือ", "พิธีขอขมาและบูชาแม่ย่านางเรือตามประเพณี"),
            (os.path.join(cat6_name, 'S__246022309_0.jpg'), "โปรยกลีบดอกไม้", "การโปรยกลีบกุหลาบและดอกไม้มงคลส่งดวงวิญญาณ"),
            (os.path.join(cat6_name, 'S__246022310_0.jpg'), "สู่ความสงบชั่วนิรันดร์", "บันทึกความทรงจำสุดท้ายที่งดงามและเปี่ยมด้วยความหวัง")
        ],
        folder_total_count=len(cat6_files)
    )

    c6_remaining_captions = [
        "พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติภูมิอันสงบ ร่มเย็น และบริสุทธิ์",
        "ครอบครัวร่วมอธิษฐานจิตและโปรยกลีบดอกไม้มงคลลงสู่กระแสน้ำ",
        "การดูแลบันทึกภาพอย่างใกล้ชิดและปลอดภัยตลอดพิธีการบนเรือ",
        "บันทึกสายสัมพันธ์และความรักอันอบอุ่นของคนในครอบครัวเป็นครั้งสุดท้าย",
        "ภาพความสงบ สว่าง และความร่มเย็นแห่งการปล่อยวางสู่ธรรมชาติ"
    ]
    c6_remaining = [
        (f, c6_remaining_captions[idx % len(c6_remaining_captions)])
        for idx, f in enumerate(cat6_files) if f not in c6_showcase_keys
    ]
    add_continuation_gallery_pages(cat6_name, c6_remaining, "พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติ", "ASHES SCATTERING")

    # =========================================================================
    # CATEGORY 7: ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ (Photographer Team & Profiles)
    # ใช้รูปภาพจากโฟลเดอร์ Photographer ทั้ง 18 ภาพ!
    # =========================================================================
    cat7_name = "Photographer"
    cat7_files = manifest[cat7_name]
    print(f"Building Category 7: Professional Team & Profiles ({len(cat7_files)} images)...")

    # 4 Showcase images: Hero equipment/display + 3 Sub-images (Camera gear, switcher, suit portrait)
    c7_showcase_keys = ['S__246399003_0.jpg', 'S__246399004_0.jpg', 'S__246399005_0.jpg', 'S__246399007_0.jpg']
    add_category_showcase_page(
        badge_text="PROFESSIONAL PHOTOGRAPHER TEAM & PROFILES",
        title_text="ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ & ทีมงานมืออาชีพ",
        subtitle_text="ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ ผู้ผ่านงานพิธีหลวงและพระราชพิธีสำคัญ ด้วยมาตรฐานละเอียด สำรวม และสมเกียรติสูงสุด",
        hook_title="มาตรฐานทีมช่างภาพมืออาชีพ ราชรถ & ช่างภาพงานศพ.com :",
        hook_bullets=[
            ("ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ", "ผู้ผ่านงานพิธีหลวง พระราชพิธีสำคัญ และงานบุคคลสำคัญระดับประเทศ ด้วยความเชี่ยวชาญสูงสุด"),
            ("บริการถ่ายภาพงานพิธี", "ช่างภาพมืออาชีพประสบการณ์สูง เก็บบรรยากาศภายในงานอย่างสมเกียรติ จัดองค์ประกอบภาพอย่างสวยงาม"),
            ("บริการถ่ายวิดีโองานพิธี", "บันทึกไฟล์ที่มีคุณภาพสูง คมชัด 4K / Full HD ตัดต่ออย่างประณีตโดยทีมงานมืออาชีพ"),
            ("บริการจอทีวี 65\" & ถ่ายทอดสด (Live Stream & Display)", "ระบบสัญญาณระดับมืออาชีพ คมชัด เสถียร จาก Hollyland และ DJI พร้อมทีมงานเทคนิคดูแลตลอดงาน")
        ],
        accent_box=("มาตรฐานและจรรยาบรรณวิชาชีพ", "ทีมช่างภาพทุกคนสวมชุดสูทสากลสีดำ กิริยาสำรวม สุภาพ นอบน้อม รู้กาลเทศะสูงสุด พร้อมอุปกรณ์สำรองข้อมูล Dual-Slot ปลอดภัย 100%"),
        hero_img=os.path.join(cat7_name, 'S__246399003_0.jpg'),
        hero_cap="ระบบจอทีวี 65-75 นิ้ว & Live Streaming ถ่ายทอดสดสัญญาณมาตรฐานจาก Hollyland และ DJI พร้อมทีมงานเทคนิคดูแลตลอดงาน",
        sub_imgs=[
            (os.path.join(cat7_name, 'S__246399004_0.jpg'), "อุปกรณ์มาตรฐานระดับโลก", "กล้อง เลนส์ และระบบสัญญาณเสถียรจาก Hollyland และ DJI"),
            (os.path.join(cat7_name, 'S__246399005_0.jpg'), "ระบบ Switcher / OB", "โต๊ะควบคุมสัญญาณตัดสลับกล้อง พร้อมทีมงานเทคนิคดูแลฟรีตลอดงาน"),
            (os.path.join(cat7_name, 'S__246399007_0.jpg'), "ชุดสูทสากลสีดำสุภาพ", "ช่างภาพมืออาชีพในชุดสูทสากลสีดำ ปฏิบัติหน้าที่ด้วยความสำรวม")
        ],
        folder_total_count=len(cat7_files)
    )

    # Captions for all remaining 14 images in Photographer folder
    photo_captions_map = {
        'S__3252234_0.jpg': "ทีมช่างภาพมืออาชีพ ราชรถ & ช่างภาพงานศพ.com",
        'S__3252235_0.jpg': "ทีมช่างภาพมืออาชีพ ผู้ผ่านงานพิธีสำคัญระดับประเทศ",
        'S__3252236_0.jpg': "ช่างภาพมากประสบการณ์ ชำนาญลำดับขั้นตอนพิธีการ",
        'S__3252237_0.jpg': "ช่างภาพมืออาชีพ บันทึกภาพด้วยความสำรวมและสมเกียรติ",
        'S__3252238_0.jpg': "ทีมงานช่างภาพประจำจุดสำคัญ เก็บครบทุกมิติแห่งความอาลัย",
        'S__3252239_0.jpg': "ช่างภาพมืออาชีพ ผู้ผ่านงานพิธีหลวงและพระราชทานเพลิงศพ",
        'S__3252240_0.jpg': "ทีมช่างภาพสายพิธีกรรม ชำนาญพิธีจีนและกงเต็กโบราณ",
        'S__3252241_0.jpg': "ช่างภาพมืออาชีพ ดูแลภาพนิ่งและวิดีโอคุณภาพสูง",
        'S__3252242_0.jpg': "ทีมงานผู้เชี่ยวชาญการจัดองค์ประกอบภาพและแสงสีสมเกียรติ",
        'S__3252243_0.jpg': "ทีมช่างภาพมืออาชีพ พร้อมสแตนด์บายดูแลงานตลอด 24 ชั่วโมง",
        'S__246399006_0.jpg': "ระบบส่งสัญญาณไร้สายมาตรฐานสากล คมชัด เสถียร ไม่สะดุดตลอดพิธีการ",
        'S__246399020.jpg': "การบันทึกวิดีโอคุณภาพสูงด้วยอุปกรณ์กันสั่นระดับสตูดิโอ",
        'F264F5C7-D51A-42F1-ACA3-2B9EBD5D7F95.jpg': "ทีมงานช่างภาพประสบการณ์สูงพร้อมดูแลความทรงจำของครอบครัว",
        'S__914374661.jpg': "บันทึกเกียรติยศและประวัติศาสตร์ของครอบครัวด้วยความทุ่มเทและสมเกียรติ"
    }

    c7_remaining = [
        (f, photo_captions_map.get(f, "ทีมช่างภาพมืออาชีพ ราชรถ & ช่างภาพงานศพ.com พร้อมสแตนด์บายดูแลงานพิธีตลอด 24 ชั่วโมง"))
        for f in cat7_files if f not in c7_showcase_keys
    ]
    if c7_remaining:
        add_continuation_gallery_pages(cat7_name, c7_remaining, "ทำเนียบทีมช่างภาพมืออาชีพ & อุปกรณ์ระดับสากล", "PHOTOGRAPHER PROFILES")

    # =========================================================================
    # CLOSING & CONTACT HUB PAGE
    # =========================================================================
    print("Building Final Page: Closing & Contact Hub...")
    current_page_num += 1
    doc.add_page_break()
    p9_cell = add_page_frame(doc, border_color='C5A059', border_sz=12)

    p9_logo = p9_cell.paragraphs[0]
    p9_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_logo.paragraph_format.space_before = Pt(8)
    p9_logo.paragraph_format.space_after = Pt(2)
    if os.path.exists('พิธีหลวง/S__246022151_0.png'):
        add_picture_with_optional_link(p9_logo, 'พิธีหลวง/S__246022151_0.png', link_target='https://www.ราชรถ.com', width=Mm(36))

    p9_title = p9_cell.add_paragraph()
    p9_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_title.paragraph_format.space_before = Pt(0)
    p9_title.paragraph_format.space_after = Pt(4)
    r_pt = p9_title.add_run('ราชรถ & ช่างภาพงานศพ.com')
    format_run(r_pt, size_pt=24, bold=True, color_rgb=C_GOLD)

    p9_div = p9_cell.add_paragraph()
    p9_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_div.paragraph_format.space_before = Pt(0)
    p9_div.paragraph_format.space_after = Pt(6)
    r_div2 = p9_div.add_run('──────────  ◇  ──────────')
    format_run(r_div2, size_pt=10, color_rgb=C_GOLD_BORDER)

    services_items = [
        "บริการในงานศพทั่วประเทศ 24 ชั่วโมง",
        "บริการถ่ายภาพงานพิธี (ภาพนิ่ง) : ช่างภาพมืออาชีพประสบการณ์สูง เก็บบรรยากาศอย่างสมเกียรติ",
        "บริการถ่ายวิดีโองานพิธี (VDO Cinema) : บันทึกไฟล์คุณภาพสูง ตัดต่อโดยมืออาชีพ",
        "บริการจอทีวี 65\" & ถ่ายทอดสด (Live Stream & Display) : สัญญาณเสถียรจาก Hollyland และ DJI",
        "หีบศพมาตรฐาน และแพคเกจหีบศพพร้อมดอกไม้ครบวงจร",
        "เคลื่อนย้ายศพทั่วประเทศ และออแกไนซ์งานศพครบวงจร",
        "ให้บริการครบทุกขั้นตอน ทั้งไทย-จีน โดยทีมงานมืออาชีพ ดูแลตั้งแต่เคลื่อนย้ายร่าง ถึงลอยอังคาร"
    ]
    t_svc = p9_cell.add_table(rows=1, cols=1)
    t_svc.alignment = WD_TABLE_ALIGNMENT.CENTER
    t_svc.autofit = False
    c_svc = t_svc.cell(0, 0)
    c_svc.width = Mm(160)
    set_cell_background(c_svc, "141312")
    set_cell_margins(c_svc, top=50, bottom=50, left=80, right=80)
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
        if k == 0 or "บริการ" in s_item:
            format_run(r_si, size_pt=9.5, bold=True, color_rgb=C_GOLD_LIGHT)
        else:
            format_run(r_si, size_pt=8.5, color_rgb=C_WHITE)

    # 3 QR Codes Hub
    p9_qr_title = p9_cell.add_paragraph()
    p9_qr_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_qr_title.paragraph_format.space_before = Pt(8)
    p9_qr_title.paragraph_format.space_after = Pt(4)
    r_qt_main = p9_qr_title.add_run('สแกน QR Code เพื่อชมผลงาน เยี่ยมชมเว็บไซต์ หรือติดต่อสอบถาม 24 ชม.')
    format_run(r_qt_main, size_pt=9, bold=True, color_rgb=C_GOLD_LIGHT)

    t9_qrs = p9_cell.add_table(rows=1, cols=3)
    t9_qrs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t9_qrs.autofit = False
    for i, (qr_img, qr_t, qr_sub, qr_url) in enumerate(qr_data):
        qc = t9_qrs.cell(0, i)
        qc.width = Mm(58)
        set_cell_background(qc, "161513")
        set_cell_margins(qc, top=40, bottom=40, left=40, right=40)
        set_cell_borders(qc,
            top={'sz': 6, 'color': 'C5A059'},
            bottom={'sz': 6, 'color': 'C5A059'},
            left={'sz': 6, 'color': 'C5A059'},
            right={'sz': 6, 'color': 'C5A059'}
        )
        qp = qc.paragraphs[0]
        qp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp.paragraph_format.space_after = Pt(2)
        if os.path.exists(qr_img):
            add_picture_with_optional_link(qp, qr_img, link_target=qr_url, width=Mm(24), height=Mm(24))
        
        qp_text = qc.add_paragraph()
        qp_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp_text.paragraph_format.space_after = Pt(0)
        r_qt = qp_text.add_run(qr_t + '\n')
        format_run(r_qt, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)
        r_qs = qp_text.add_run(qr_sub)
        format_run(r_qs, size_pt=7.5, color_rgb=C_WHITE)

    # Contacts Footer
    p9_foot = p9_cell.add_paragraph()
    p9_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_foot.paragraph_format.space_before = Pt(8)
    p9_foot.paragraph_format.space_after = Pt(2)
    r_c1 = p9_foot.add_run('โทร 085-999-2396  |  LINE : Rathcharot  |  Tiktok : Rathcharot  |  IG : Rathcharot\n')
    format_run(r_c1, size_pt=8.5, bold=True, color_rgb=C_GOLD_LIGHT)
    r_c2 = p9_foot.add_run('www.ช่างภาพงานศพ.com   •   www.ราชรถ.com')
    format_run(r_c2, size_pt=8.5, color_rgb=C_SEC)

    # Save document
    output_filename = "Rathcharot_Funeral_Catalog_A4.docx"
    doc.save(output_filename)
    print(f"Full Comprehensive Catalog generated successfully: {output_filename}")
    print(f"Total Pages Generated: {current_page_num}")

if __name__ == "__main__":
    generate_full_catalog()
