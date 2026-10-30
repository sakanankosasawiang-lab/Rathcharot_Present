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

    # Global page counter tracking
    total_pages_estimate = 38
    current_page_num = 1

    # =========================================================================
    # PAGE 1: COVER PAGE
    # =========================================================================
    print("Building Page 1: Cover Page...")
    p1_cell = add_page_frame(doc)

    p_logo = p1_cell.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(10)
    p_logo.paragraph_format.space_after = Pt(12)
    if os.path.exists('พิธีหลวง/S__246022151_0.png'):
        p_logo.add_run().add_picture('พิธีหลวง/S__246022151_0.png', width=Mm(28))
    r_div = p_logo.add_run('   |   ')
    format_run(r_div, size_pt=20, color_rgb=C_GOLD_BORDER)
    if os.path.exists('พิธีหลวง/S__246022150_0.png'):
        p_logo.add_run().add_picture('พิธีหลวง/S__246022150_0.png', width=Mm(28))

    p_title = p1_cell.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_t = p_title.add_run('ราชรถ & ช่างภาพงานศพ.com')
    format_run(r_t, size_pt=25, bold=True, color_rgb=C_GOLD)

    p_sub = p1_cell.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(10)
    r_s = p_sub.add_run('แคตตาล็อกรวมผลงานช่างภาพภาพนิ่ง วิดีโอซีนีม่า และ Live Streaming ถ่ายทอดสดงานพิธีศพครบวงจร')
    format_run(r_s, size_pt=12, bold=True, color_rgb=C_GOLD_LIGHT)

    p_tag = p1_cell.add_paragraph()
    p_tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tag.paragraph_format.space_before = Pt(0)
    p_tag.paragraph_format.space_after = Pt(14)
    r_tag = p_tag.add_run('ดูแลด้วยมาตรฐานระดับมืออาชีพ สำรวม รู้กาลเทศะ และแม่นยำทุกลำดับพิธีการตลอด 24 ชั่วโมง ทั่วประเทศ')
    format_run(r_tag, size_pt=10, color_rgb=C_SEC)

    # 3 Highlights Cards in Cover
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
        set_cell_margins(c, top=60, bottom=60, left=60, right=60)
        set_cell_borders(c,
            top={'sz': 6, 'color': 'C5A059'},
            bottom={'sz': 6, 'color': 'C5A059'},
            left={'sz': 6, 'color': 'C5A059'},
            right={'sz': 6, 'color': 'C5A059'}
        )
        p1 = c.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_after = Pt(3)
        r1 = p1.add_run(p_head)
        format_run(r1, size_pt=10, bold=True, color_rgb=C_GOLD)

        p2 = c.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(2)
        r2 = p2.add_run(p_desc)
        format_run(r2, size_pt=8, color_rgb=C_SEC)

    # Cover Hero Image
    p_cov_img = p1_cell.add_paragraph()
    p_cov_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_img.paragraph_format.space_before = Pt(14)
    p_cov_img.paragraph_format.space_after = Pt(4)
    if os.path.exists('พิธีหลวง/S__246022154_0.jpg'):
        cov_s, _ = get_optimized_image_stream('พิธีหลวง/S__246022154_0.jpg', max_dim=1600, quality=86)
        if cov_s:
            p_cov_img.add_run().add_picture(cov_s, width=Mm(174), height=Mm(84))

    p_cov_cap = p1_cell.add_paragraph()
    p_cov_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cov_cap.paragraph_format.space_after = Pt(12)
    r_cc = p_cov_cap.add_run('บันทึกทุกความทรงจำอันทรงคุณค่า ด้วยศาสตร์และศิลป์แห่งการถ่ายทอดภาพงานพิธีศพอย่างสมเกียรติ')
    format_run(r_cc, size_pt=8.5, italic=True, color_rgb=C_MUTED)

    # 3 QR Codes
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
            qp.add_run().add_picture(qr_img, width=Mm(18), height=Mm(18))
        
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
        c = add_page_frame(doc, border_color='C5A059', border_sz=12)

        # Header Badge
        p_badge = c.paragraphs[0]
        p_badge.paragraph_format.space_before = Pt(2)
        p_badge.paragraph_format.space_after = Pt(2)
        r_b = p_badge.add_run(f'  ◆ {badge_text}  ')
        format_run(r_b, size_pt=8.5, bold=True, color_rgb=C_GOLD_LIGHT)

        p_t = c.add_paragraph()
        p_t.paragraph_format.space_before = Pt(0)
        p_t.paragraph_format.space_after = Pt(2)
        r_t = p_t.add_run(title_text)
        format_run(r_t, size_pt=17, bold=True, color_rgb=C_GOLD)

        p_s = c.add_paragraph()
        p_s.paragraph_format.space_before = Pt(0)
        p_s.paragraph_format.space_after = Pt(6)
        r_s = p_s.add_run(subtitle_text)
        format_run(r_s, size_pt=9, color_rgb=C_MUTED)

        # Selling Points Box
        t_hook = c.add_table(rows=1, cols=1)
        t_hook.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_hook.autofit = False
        c_hook = t_hook.cell(0, 0)
        c_hook.width = Mm(176)
        set_cell_background(c_hook, "161513")
        set_cell_margins(c_hook, top=50, bottom=50, left=80, right=80)
        set_cell_borders(c_hook,
            left={'sz': 16, 'color': 'D4AF37'},
            top={'sz': 4, 'color': '3D3522'},
            bottom={'sz': 4, 'color': '3D3522'},
            right={'sz': 4, 'color': '3D3522'}
        )

        p_h = c_hook.paragraphs[0]
        p_h.paragraph_format.space_before = Pt(0)
        p_h.paragraph_format.space_after = Pt(3)
        r_h = p_h.add_run(hook_title)
        format_run(r_h, size_pt=9, bold=True, color_rgb=C_GOLD_LIGHT)

        for b_title, b_desc in hook_bullets:
            p_b = c_hook.add_paragraph()
            p_b.paragraph_format.space_before = Pt(0)
            p_b.paragraph_format.space_after = Pt(1.5)
            r_dot = p_b.add_run('• ')
            format_run(r_dot, size_pt=8.5, bold=True, color_rgb=C_GOLD)
            r_bt = p_b.add_run(b_title + ' : ')
            format_run(r_bt, size_pt=8.5, bold=True, color_rgb=C_WHITE)
            r_bd = p_b.add_run(b_desc)
            format_run(r_bd, size_pt=8.5, color_rgb=C_SEC)

        if accent_box:
            acc_t, acc_d = accent_box
            p_acc = c_hook.add_paragraph()
            p_acc.paragraph_format.space_before = Pt(3)
            p_acc.paragraph_format.space_after = Pt(0)
            r_at = p_acc.add_run('★ ' + acc_t + ' — ')
            format_run(r_at, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)
            r_ad = p_acc.add_run(acc_d)
            format_run(r_ad, size_pt=8, italic=True, color_rgb=C_MUTED)

        # Hero Image (Featured Large)
        p_hero = c.add_paragraph()
        p_hero.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hero.paragraph_format.space_before = Pt(6)
        p_hero.paragraph_format.space_after = Pt(2)
        if os.path.exists(hero_img):
            h_s, _ = get_optimized_image_stream(hero_img, max_dim=1600, quality=86)
            if h_s:
                p_hero.add_run().add_picture(h_s, width=Mm(176), height=Mm(72))

        p_hcap = c.add_paragraph()
        p_hcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hcap.paragraph_format.space_before = Pt(0)
        p_hcap.paragraph_format.space_after = Pt(6)
        r_hc1 = p_hcap.add_run('【 ภาพหลักประจำหมวด 】 ')
        format_run(r_hc1, size_pt=8, bold=True, color_rgb=C_GOLD)
        r_hc2 = p_hcap.add_run(hero_cap)
        format_run(r_hc2, size_pt=8, color_rgb=C_SEC)

        # 3 Sub-images row
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
                    sp.add_run().add_picture(sub_s, width=Mm(54), height=Mm(38))
            
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

    # Function to add Continuation Gallery Pages for all remaining images
    def add_continuation_gallery_pages(cat_name, remaining_images, cat_display_title, cat_badge_text):
        nonlocal current_page_num
        if not remaining_images:
            return

        # Chunk images by 4 to 6 per page. 4 images per page (2 rows x 2 cols) gives large, beautiful cards with crystal clear captions!
        # If there are many images, 6 per page (3 rows x 2 cols) or 4 per page. Let's do 4 per page for maximum luxury presentation impact!
        chunk_size = 4
        chunks = [remaining_images[i:i + chunk_size] for i in range(0, len(remaining_images), chunk_size)]
        total_chunks = len(chunks)

        for chunk_idx, img_chunk in enumerate(chunks):
            current_page_num += 1
            doc.add_page_break()
            c = add_page_frame(doc, border_color='8A6014', border_sz=8)

            # Top Header of Continuation Page
            p_hdr = c.paragraphs[0]
            p_hdr.paragraph_format.space_before = Pt(2)
            p_hdr.paragraph_format.space_after = Pt(2)
            r_bd = p_hdr.add_run(f'  ◆ {cat_badge_text} : คลังภาพผลงานต่อเนื่อง (ชุดที่ {chunk_idx + 1}/{total_chunks})  ')
            format_run(r_bd, size_pt=8, bold=True, color_rgb=C_GOLD_LIGHT)

            p_ht = c.add_paragraph()
            p_ht.paragraph_format.space_before = Pt(0)
            p_ht.paragraph_format.space_after = Pt(6)
            r_ht = p_ht.add_run(f'{cat_display_title} — บันทึกภาพผลงานจริง')
            format_run(r_ht, size_pt=13, bold=True, color_rgb=C_GOLD)

            # 2-column Grid for the 4 images in this chunk
            # 2 rows x 2 cols table
            t_grid = c.add_table(rows=2, cols=2)
            t_grid.alignment = WD_TABLE_ALIGNMENT.CENTER
            t_grid.autofit = False

            for idx_in_chunk, img_info in enumerate(img_chunk):
                row_idx = idx_in_chunk // 2
                col_idx = idx_in_chunk % 2
                cell = t_grid.cell(row_idx, col_idx)
                cell.width = Mm(87)

                set_cell_background(cell, "141312")
                set_cell_margins(cell, top=40, bottom=40, left=50, right=50)
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
                                cp.add_run().add_picture(s_img, width=Mm(81), height=Mm(round(81 / aspect, 2)))
                            else:
                                cp.add_run().add_picture(s_img, height=Mm(66), width=Mm(round(66 * aspect, 2)))
                        else:
                            cp.add_run(f'[ภาพ: {img_path}]')
                    except Exception as e:
                        cp.add_run(f'[ภาพ: {img_path}]')

                # Caption
                p_c = cell.add_paragraph()
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_c.paragraph_format.space_before = Pt(2)
                p_c.paragraph_format.space_after = Pt(0)
                r_ct = p_c.add_run(f'【 ภาพผลงานจริง 】\n')
                format_run(r_ct, size_pt=7.5, bold=True, color_rgb=C_GOLD_LIGHT)
                r_cd = p_c.add_run(img_caption)
                format_run(r_cd, size_pt=7.2, color_rgb=C_SEC)

            # If chunk has only 1, 2, or 3 images, style remaining empty cells
            if len(img_chunk) < 4:
                for empty_idx in range(len(img_chunk), 4):
                    r_i = empty_idx // 2
                    c_i = empty_idx % 2
                    e_cell = t_grid.cell(r_i, c_i)
                    e_cell.width = Mm(87)
                    set_cell_background(e_cell, "0F0E0D")
                    set_cell_borders(e_cell) # No border

            # Footer
            p_ft = c.add_paragraph()
            p_ft.paragraph_format.space_before = Pt(6)
            p_ft.paragraph_format.space_after = Pt(0)
            r_fl = p_ft.add_run('ราชรถ & ช่างภาพงานศพ.com  •  บริการถ่ายทอดสดและช่างภาพมืออาชีพ 24 ชม.  •  โทร 085-999-2396')
            format_run(r_fl, size_pt=7.5, color_rgb=C_MUTED)

    # =========================================================================
    # CATEGORY 1: LIVE STREAMING & จอ 65-75 นิ้ว
    # =========================================================================
    cat1_name = "streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว"
    cat1_files = manifest[cat1_name]
    print(f"Building Category 1: Live Streaming ({len(cat1_files)} images)...")

    # Showcase page
    c1_showcase_keys = ['S__246046734_0.jpg', 'S__246046735_0.jpg', 'S__246046736_0.jpg', 'S__246030381.jpg']
    add_category_showcase_page(
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
        hero_img=os.path.join(cat1_name, 'S__246046734_0.jpg'),
        hero_cap="การติดตั้งจอถ่ายทอดสด 75 นิ้ว คมชัดรอบศาลา ช่วยให้ผู้ร่วมงานจำนวนมากมองเห็นพิธีการได้อย่างทั่วถึง",
        sub_imgs=[
            (os.path.join(cat1_name, 'S__246046735_0.jpg'), "มุมมองแขกนอกศาลา", "แขกด้านนอกมองเห็นพิธีการด้านในผ่านจอคมชัดระดับ Full HD"),
            (os.path.join(cat1_name, 'S__246046736_0.jpg'), "ระบบคอนโทรลเลอร์ OB", "โต๊ะควบคุม Switcher พร้อมวิศวกรดูแลสัญญาณให้ฟรีตลอดงาน"),
            (os.path.join(cat1_name, 'S__246030381.jpg'), "กล้องระดับสตูดิโอ", "การจัดมุมกล้องรอบทิศทาง เก็บครบทุกช่วงเวลาสำคัญในพิธี")
        ],
        folder_total_count=len(cat1_files)
    )

    # Remaining images for Category 1
    c1_remaining = [
        (f, "การติดตั้งจอคมชัดสูงรอบศาลา พร้อมจัดระเบียบสายสัญญาณอย่างปลอดภัย เรียบร้อย สมเกียรติยศ")
        for f in cat1_files if f not in c1_showcase_keys
    ]
    add_continuation_gallery_pages(cat1_name, c1_remaining, "บริการ Live Streaming & จอ 65-75 นิ้ว", "LIVE STREAMING")

    # =========================================================================
    # CATEGORY 2: การถ่ายภาพงานพิธีหลวง (Royal Ceremony)
    # =========================================================================
    cat2_name = "พิธีหลวง"
    cat2_files = manifest[cat2_name]
    print(f"Building Category 2: Royal Ceremony ({len(cat2_files)} images)...")

    c2_showcase_keys = ['S__246022154_0.jpg', 'S__246022155_0.jpg', 'S__246022156_0.jpg', 'S__246022158_0.jpg']
    add_category_showcase_page(
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
        hero_img=os.path.join(cat2_name, 'S__246022154_0.jpg'),
        hero_cap="พิธีพระราชทานน้ำหลวงอาบศพและขบวนอัญเชิญเครื่องเกียรติยศพระราชทานอย่างสมพระเกียรติ",
        sub_imgs=[
            (os.path.join(cat2_name, 'S__246022155_0.jpg'), "เพลิงพระราชทาน", "การประกอบพิธีพระราชทานเพลิงศพและขบวนเชิญกล่องเพลิง"),
            (os.path.join(cat2_name, 'S__246022156_0.jpg'), "พวงมาลาพระราชทาน", "บันทึกภาพพวงมาลาพระราชทานและเครื่องประกอบเกียรติยศ"),
            (os.path.join(cat2_name, 'S__246022158_0.jpg'), "บรรยากาศทรงเกียรติ", "ถ่ายทอดความสง่างามและความภาคภูมิใจสูงสุดของวงศ์ตระกูล")
        ],
        folder_total_count=len(cat2_files)
    )

    c2_remaining_captions = [
        "พิธีอัญเชิญเครื่องเกียรติยศพระราชทานเข้าสู่มณฑลพิธีอย่างสง่างาม",
        "การประกอบพิธีพระราชทานน้ำหลวงอาบศพและประธานในพิธี",
        "โกศแปดเหลี่ยมและเครื่องประกอบเกียรติยศพระราชทาน",
        "พวงมาลาพระราชทานจากพระบรมวงศานุวงศ์จัดวางอย่างประณีต",
        "ริ้วขบวนเชิญกล่องเพลิงพระราชทานขึ้นสู่จิตกาธาน",
        "พิธีทอดผ้าไตรพระราชทานแด่พระสงฆ์ทรงสมณศักดิ์",
        "เจ้าหน้าที่สำนักพระราชวังและทีมช่างภาพปฏิบัติหน้าที่ด้วยความสำรวมสูงสุด",
        "บันทึกเกียรติประวัติอันสูงสุดของผู้วายชนม์และวงศ์ตระกูล",
        "บรรยากาศความอาลัยและความทรงเกียรติของแขกผู้มีเกียรติระดับประเทศ",
        "ภาพรายละเอียดหีบทองลายสลักและเครื่องราชอิสริยาภรณ์"
    ]
    c2_remaining = []
    r_idx = 0
    for f in cat2_files:
        # Ignore logos/QR files in this folder
        if f in ['S__246022151_0.png', 'S__246022150_0.png', 'S__246022147.jpg']:
            continue
        if f not in c2_showcase_keys:
            cap = c2_remaining_captions[r_idx % len(c2_remaining_captions)]
            c2_remaining.append((f, cap))
            r_idx += 1

    add_continuation_gallery_pages(cat2_name, c2_remaining, "การถ่ายภาพงานพิธีหลวง และเครื่องเกียรติยศ", "ROYAL CEREMONY")

    # =========================================================================
    # CATEGORY 3: พิธีจีน และธรรมเนียมปฏิบัติ (Chinese Ceremony & Kong Tek)
    # =========================================================================
    cat3_name = "ธรรมเนียมจีน และพิธีกรรม"
    cat3_files = manifest[cat3_name]
    print(f"Building Category 3: Chinese Ceremony ({len(cat3_files)} images)...")

    c3_showcase_keys = ['S__246030361.jpg', 'S__246022288_0.jpg', 'S__246022295_0.jpg', 'S__246030353_0.jpg']
    add_category_showcase_page(
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
        "พิธีสวดพระพุทธมนต์จีนและพิธีสวดเปิดทางสวรรค์แก่ดวงวิญญาณ",
        "ลูกหลานร่วมพิธีเดินข้ามสะพานโอฆสงสารแสดงความกตัญญูกตเวทิตา",
        "ความประณีตของบ้านกงเต็ก รถยนต์ และสิ่งของเครื่องใช้ส่งมอบบรรพบุรุษ",
        "การประกอบพิธีของพระสงฆ์จีนนิกายและซินแสตามโบราณประเพณี",
        "พิธีเคารพศพตามลำดับชั้นอาวุโสของลูก หลาน เหลน",
        "พิธีเผากระดาษเงินกระดาษทองและเครื่องกงเต็กสู่สัมปรายภพ",
        "บันทึกสายใยความรักและความผูกพันอันแน่นแฟ้นของครอบครัวตระกูลจีน",
        "การนำขบวนเคลื่อนย้ายร่างสู่พิธีการขั้นต่อไปอย่างเคร่งครัด"
    ]
    c3_remaining = [
        (f, c3_remaining_captions[idx % len(c3_remaining_captions)])
        for idx, f in enumerate(cat3_files) if f not in c3_showcase_keys
    ]
    add_continuation_gallery_pages(cat3_name, c3_remaining, "การถ่ายภาพพิธีจีน และธรรมเนียมปฏิบัติ", "CHINESE CEREMONY")

    # =========================================================================
    # CATEGORY 4: พิธีสวดพระอภิธรรม (Evening Chanting)
    # =========================================================================
    cat4_name = "บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน"
    cat4_files = manifest[cat4_name]
    print(f"Building Category 4: Evening Chanting ({len(cat4_files)} images)...")

    c4_showcase_keys = ['S__246022190_0.jpg', 'S__246022191_0.jpg', 'S__246022192_0.jpg', 'S__246022193_0.jpg']
    add_category_showcase_page(
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
        hero_img=os.path.join(cat4_name, 'S__246022190_0.jpg'),
        hero_cap="บรรยากาศพิธีสวดพระอภิธรรมและความสงบงดงามสมเกียรติ ท่ามกลางญาติมิตรและบุคคลสำคัญ",
        sub_imgs=[
            (os.path.join(cat4_name, 'S__246022191_0.jpg'), "การฟังสวดพระอภิธรรม", "ภาพประธานในพิธีและผู้ร่วมงานร่วมฟังสวดพระอภิธรรม"),
            (os.path.join(cat4_name, 'S__246022192_0.jpg'), "ดอกไม้หน้าหีบศพ", "ความงดงามของการจัดวางดอกไม้และภาพถ่ายผู้วายชนม์"),
            (os.path.join(cat4_name, 'S__246022193_0.jpg'), "ถวายจตุปัจจัยไทยธรรม", "พิธีถวายไทยธรรมแด่พระสงฆ์เพื่ออุทิศส่วนกุศลอย่างสมบูรณ์")
        ],
        folder_total_count=len(cat4_files)
    )

    c4_remaining_captions = [
        "บรรยากาศความสงบ สำรวม ในช่วงพิธีสวดพระอภิธรรมประจำค่ำคืน",
        "พระสงฆ์เจริญพระพุทธมนต์และแสดงพระธรรมเทศนา",
        "ประธานในพิธีจุดธูปเทียนบูชาพระรัตนตรัยและเคารพผู้วายชนม์",
        "บันทึกภาพบุคคลสำคัญ ญาติสนิท มิตรสหายที่มาร่วมไว้อาลัย",
        "การจัดตกแต่งดอกไม้สดหน้าหีบศพอย่างวิจิตรตระการตา",
        "พิธีทอดผ้าบังสุกุลและถวายจตุปัจจัยไทยธรรมแด่พระสงฆ์",
        "ภาพหมู่ครอบครัวเจ้าภาพร่วมกับผู้มีเกียรติที่มาร่วมแสดงความอาลัย",
        "รายละเอียดความประณีตของหีบศพและภาพถ่ายที่ระลึกผู้วายชนม์",
        "ภาพความอบอุ่นและการให้กำลังใจแก่ครอบครัวเจ้าภาพ"
    ]
    c4_remaining = [
        (f, c4_remaining_captions[idx % len(c4_remaining_captions)])
        for idx, f in enumerate(cat4_files) if f not in c4_showcase_keys
    ]
    add_continuation_gallery_pages(cat4_name, c4_remaining, "การถ่ายภาพพิธีสวดพระอภิธรรม", "EVENING CHANTING")

    # =========================================================================
    # CATEGORY 5: วันสุดท้าย (วันฌาปนกิจ - Cremation Day)
    # =========================================================================
    cat5_name = "เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย"
    cat5_files = manifest[cat5_name]
    print(f"Building Category 5: Cremation Day ({len(cat5_files)} images)...")

    c5_showcase_keys = ['S__246022253_0.jpg', 'S__246022254_0.jpg', 'S__246022255_0.jpg', 'S__246022256_0.jpg']
    add_category_showcase_page(
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
        hero_img=os.path.join(cat5_name, 'S__246022253_0.jpg'),
        hero_cap="ริ้วขบวนเวียนรอบเมรุ 3 รอบ อัญเชิญร่างผู้วายชนม์สู่จิตกาธานด้วยความเคารพสูงสุด",
        sub_imgs=[
            (os.path.join(cat5_name, 'S__246022254_0.jpg'), "ทอดผ้าไตรบังสุกุล", "พิธีทอดผ้าบังสุกุลโดยประธานในพิธีและแขกผู้มีเกียรติ"),
            (os.path.join(cat5_name, 'S__246022255_0.jpg'), "วางดอกไม้จันทน์", "การแสดงความระลึกถึงและกราบลาเป็นครั้งสุดท้าย"),
            (os.path.join(cat5_name, 'S__246022256_0.jpg'), "ภาพประวัติศาสตร์ครอบครัว", "บันทึกสายใยความรักและความผูกพันของวงศ์ตระกูล")
        ],
        folder_total_count=len(cat5_files)
    )

    c5_remaining_captions = [
        "ริ้วขบวนอัญเชิญหีบศพเวียนรอบเมรุ 3 รอบตามโบราณประเพณี",
        "การเชิญหีบศพขึ้นสู่จิตกาธานและจัดเตรียมพิธีประชุมเพลิง",
        "พิธีทอดผ้าบังสุกุลโดยประธานในพิธีและแขกผู้ใหญ่",
        "การอ่านประวัติและคำไว้อาลัยแด่ผู้วายชนม์",
        "แขกผู้มีเกียรติร่วมทอดผ้าและวางดอกไม้จันทน์อำลาเป็นครั้งสุดท้าย",
        "พิธีประชุมเพลิงส่งดวงวิญญาณสู่สุคติภูมิ",
        "ภาพประวัติศาสตร์ความผูกพันและสายใยรักอันอบอุ่นของครอบครัว",
        "บันทึกความทรงจำวันสุดท้ายอย่างประณีตและเปี่ยมด้วยคุณค่าเหนือกาลเวลา"
    ]
    c5_remaining = [
        (f, c5_remaining_captions[idx % len(c5_remaining_captions)])
        for idx, f in enumerate(cat5_files) if f not in c5_showcase_keys
    ]
    add_continuation_gallery_pages(cat5_name, c5_remaining, "เก็บทุกความทรงจำในวันสุดท้าย (วันฌาปนกิจ)", "CREMATION DAY")

    # =========================================================================
    # CATEGORY 6: พิธีลอยอังคาร (Ashes Scattering)
    # =========================================================================
    cat6_name = "ลอยอังคาร"
    cat6_files = manifest[cat6_name]
    print(f"Building Category 6: Ashes Scattering ({len(cat6_files)} images)...")

    c6_showcase_keys = ['S__246022308_0.jpg', 'S__246022309_0.jpg', 'S__246022310_0.jpg', 'S__246022311_0.jpg']
    add_category_showcase_page(
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
        hero_img=os.path.join(cat6_name, 'S__246022308_0.jpg'),
        hero_cap="พิธีลอยอังคารกลางสายน้ำอันสงบ โปรยกลีบดอกไม้มงคลส่งดวงวิญญาณสู่สุคติภูมิ",
        sub_imgs=[
            (os.path.join(cat6_name, 'S__246022309_0.jpg'), "อัญเชิญอัฐิลงเรือ", "ครอบครัวอัญเชิญลุ้งอัฐิลงเรือสู่จุดประกอบพิธีกลางสายน้ำ"),
            (os.path.join(cat6_name, 'S__246022310_0.jpg'), "พิธีขอขมาแม่ย่านาง", "การประกอบพิธีกล่าวคำขอขมาและบูชาสิ่งศักดิ์สิทธิ์ประจำสายน้ำ"),
            (os.path.join(cat6_name, 'S__246022311_0.jpg'), "ลอยกระทงส่งวิญญาณ", "การส่งกระทงดอกไม้อำลาและส่งคำอธิษฐานสู่สรวงสวรรค์")
        ],
        folder_total_count=len(cat6_files)
    )

    c6_remaining_captions = [
        "ครอบครัวอัญเชิญลุ้งอัฐิมุ่งหน้าสู่ปากอ่าวหรือจุดประกอบพิธีทางน้ำ",
        "พิธีไหว้บูชาสิ่งศักดิ์สิทธิ์และแม่ย่านางเรือเพื่อความราบรื่น",
        "การโปรยกลีบดอกไม้ 7 สีและเหรียญมงคลส่งดวงวิญญาณ",
        "ลุ้งอัฐิและกระทงดอกไม้ลอยล่องกลางสายน้ำอันกว้างใหญ่",
        "ครอบครัวร่วมสวดแผ่เมตตาและกล่าวคำอำลาเป็นครั้งสุดท้าย",
        "ภาพความสงบ สว่าง และความร่มเย็นแห่งการปล่อยวางสู่ธรรมชาติ"
    ]
    c6_remaining = [
        (f, c6_remaining_captions[idx % len(c6_remaining_captions)])
        for idx, f in enumerate(cat6_files) if f not in c6_showcase_keys
    ]
    add_continuation_gallery_pages(cat6_name, c6_remaining, "พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติ", "ASHES SCATTERING")

    # =========================================================================
    # CATEGORY 7: โปรไฟล์ทีมช่างภาพ (Professional Team & Ethics)
    # =========================================================================
    cat7_name = "โปรไฟล์ช่างภาพ"
    cat7_files = manifest[cat7_name]
    print(f"Building Category 7: Team & Ethics ({len(cat7_files)} images)...")

    c7_showcase_keys = ['S__246030375_0.jpg', 'S__246030374_0.jpg', 'S__246030377_0.jpg', 'S__246046733_0.jpg']
    add_category_showcase_page(
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
        hero_img=os.path.join(cat7_name, 'S__246030375_0.jpg'),
        hero_cap="ทีมงานช่างภาพมืออาชีพในชุดสูทสากลสีดำสุภาพ ปฏิบัติงานด้วยความสำรวมสูงสุดในทุกขั้นตอน",
        sub_imgs=[
            (os.path.join(cat7_name, 'S__246030374_0.jpg'), "รู้มุมกล้องกาลเทศะ", "ทราบตำแหน่งยืนที่เหมาะสม ไม่บังสายตาประธานในพิธี"),
            (os.path.join(cat7_name, 'S__246030377_0.jpg'), "อุปกรณ์โปร Dual-Slot", "กล้องและเลนส์ระดับสตูดิโอ มีระบบสำรองข้อมูลคู่ขนาน"),
            (os.path.join(cat7_name, 'S__246046733_0.jpg'), "แต่งแสงสีสมเกียรติ", "การปรับแต่งแสงสีให้คงความคลาสสิก สมเกียรติยศ")
        ],
        folder_total_count=len(cat7_files)
    )

    c7_remaining = [
        (f, "ทีมงานช่างภาพมืออาชีพพร้อมสแตนด์บายดูแลบันทึกภาพและสัญญาณถ่ายทอดสดตลอด 24 ชั่วโมง")
        for f in cat7_files if f not in c7_showcase_keys
    ]
    if c7_remaining:
        add_continuation_gallery_pages(cat7_name, c7_remaining, "มาตรฐานทีมช่างภาพ & อุปกรณ์ระดับโปร", "PROFESSIONAL TEAM")

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
        p9_logo.add_run().add_picture('พิธีหลวง/S__246022151_0.png', width=Mm(36))

    p9_title = p9_cell.add_paragraph()
    p9_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_title.paragraph_format.space_before = Pt(0)
    p9_title.paragraph_format.space_after = Pt(6)
    r_pt = p9_title.add_run('ราชรถ')
    format_run(r_pt, size_pt=26, bold=True, color_rgb=C_GOLD)

    p9_div = p9_cell.add_paragraph()
    p9_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_div.paragraph_format.space_before = Pt(0)
    p9_div.paragraph_format.space_after = Pt(8)
    r_div2 = p9_div.add_run('──────────  ◇  ──────────')
    format_run(r_div2, size_pt=10, color_rgb=C_GOLD_BORDER)

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
    set_cell_margins(c_svc, top=60, bottom=60, left=80, right=80)
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
            format_run(r_si, size_pt=10.5, bold=True, color_rgb=C_GOLD_LIGHT)
        else:
            format_run(r_si, size_pt=9.5, color_rgb=C_WHITE)

    # 3 QR Codes Hub
    p9_qr_title = p9_cell.add_paragraph()
    p9_qr_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_qr_title.paragraph_format.space_before = Pt(10)
    p9_qr_title.paragraph_format.space_after = Pt(4)
    r_qt_main = p9_qr_title.add_run('สแกน QR Code เพื่อชมผลงาน เยี่ยมชมเว็บไซต์ หรือติดต่อสอบถาม')
    format_run(r_qt_main, size_pt=9.5, bold=True, color_rgb=C_GOLD_LIGHT)

    t9_qrs = p9_cell.add_table(rows=1, cols=3)
    t9_qrs.alignment = WD_TABLE_ALIGNMENT.CENTER
    t9_qrs.autofit = False
    for i, (qr_img, qr_t, qr_sub) in enumerate(qr_data):
        qc = t9_qrs.cell(0, i)
        qc.width = Mm(58)
        set_cell_background(qc, "161513")
        set_cell_margins(qc, top=50, bottom=50, left=40, right=40)
        set_cell_borders(qc,
            top={'sz': 6, 'color': 'C5A059'},
            bottom={'sz': 6, 'color': 'C5A059'},
            left={'sz': 6, 'color': 'C5A059'},
            right={'sz': 6, 'color': 'C5A059'}
        )
        qp = qc.paragraphs[0]
        qp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp.paragraph_format.space_after = Pt(3)
        if os.path.exists(qr_img):
            qp.add_run().add_picture(qr_img, width=Mm(26), height=Mm(26))
        
        qp_text = qc.add_paragraph()
        qp_text.alignment = WD_ALIGN_PARAGRAPH.CENTER
        qp_text.paragraph_format.space_after = Pt(0)
        r_qt = qp_text.add_run(qr_t + '\n')
        format_run(r_qt, size_pt=9, bold=True, color_rgb=C_GOLD)
        r_qs = qp_text.add_run(qr_sub)
        format_run(r_qs, size_pt=8, color_rgb=C_WHITE)

    p9_cont = p9_cell.add_paragraph()
    p9_cont.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9_cont.paragraph_format.space_before = Pt(12)
    p9_cont.paragraph_format.space_after = Pt(2)
    r_call = p9_cont.add_run('📞 โทร: 085-999-2396 (ตลอด 24 ชั่วโมง)   |   💬 LINE : Rathcharot\n')
    format_run(r_call, size_pt=10.5, bold=True, color_rgb=C_GOLD_LIGHT)
    r_soc = p9_cont.add_run('🎵 Tiktok: Rathcharot   •   📷 IG: Rathcharot   •   🌐 www.rathcharot.com   •   www.ช่างภาพงานศพ.com')
    format_run(r_soc, size_pt=8.5, color_rgb=C_SEC)

    # Save to Rathcharot_Funeral_Catalog_A4.docx
    output_filename = "Rathcharot_Funeral_Catalog_A4.docx"
    doc.save(output_filename)
    print(f"Full Comprehensive Catalog generated successfully: {output_filename}")
    print(f"Total Pages Generated: {current_page_num}")

if __name__ == "__main__":
    generate_full_catalog()
