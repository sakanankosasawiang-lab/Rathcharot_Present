import os
import re
import json
import urllib.parse

workspace = r'c:\Apps\Rathcharot_Present'

def natural_sort_key(filename):
    """Sort numbered ceremony photos (1)..(116) before S__... camera files naturally."""
    parts = [int(p) if p.isdigit() else p.lower() for p in re.split(r'(\d+)', filename)]
    priority = 0 if not filename.startswith('S__') else 1
    return (priority, parts)

categories = [
    {
        'id': 'profile',
        'folder': 'โปรไฟล์ช่างภาพ',
        'title': 'โปรไฟล์ช่างภาพ (ทีมช่างภาพบันทึกประวัติศาสตร์ชาติ)',
        'badge': 'PROFESSIONALISM & EXPERT TEAM',
        'subtitle': 'ช่างภาพบันทึกภาพประวัติศาสตร์ และพิธีงานสำคัญของสำนักราชวัง โดยสังกัดจาก สมาคมถ่ายภาพแห่งประเทศไทยในพระบรมราชูปถัมภ์',
        'numeral': '06',
        'headline': 'โปรไฟล์ช่างภาพ — ช่างภาพบันทึกภาพประวัติศาสตร์ & พิธีสำคัญสำนักราชวัง',
        'why_us': [
            'สังกัดสมาคมถ่ายภาพแห่งประเทศไทย ในพระบรมราชูปถัมภ์: ทีมช่างภาพบันทึกภาพประวัติศาสตร์และพระราชพิธีสำคัญของสำนักพระราชวัง',
            'รู้กาลเทศะและไหวพริบระดับ Professional: รู้ชัดว่าควรทำอะไร ไม่ควรทำอะไรในแต่ละช่วงพิธี และแก้ไขปัญหาเฉพาะหน้าได้อย่างราบรื่น',
            'มาตรฐานสุภาพ สำรวม สมเกียรติ 100%: แต่งกายสูทสากลสีดำ กิริยานอบน้อม พร้อมอุปกรณ์สำรอง Dual-Slot มั่นใจทุกลำดับพิธี'
        ]
    },
    {
        'id': 'streaming',
        'folder': 'streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว',
        'title': 'บริการเช่าจอทีวีขนาด 65 นิ้ว & Live Stream',
        'badge': 'SPECIAL HIGHLIGHT : LIVE STREAM & DISPLAY',
        'subtitle': 'ถ่ายทอดสดพิธีการ จากศาลาหลักเพื่อให้ผู้มาร่วมงานได้เห็นพิธีการสำคัญต่างๆ ด้วยอุปกรณ์มาตรฐาน คมชัด เสถียร จาก Hollyland และ DJI พร้อมทีมงานเทคนิคดูแลตลอดงาน',
        'numeral': '★',
        'headline': 'บริการเช่าจอทีวีขนาด 65 นิ้ว & Live Stream',
        'why_us': [
            'จอ 65 นิ้ว High-Definition: ชมพิธีสวดและฌาปนกิจรอบศาลาแบบ Real-Time',
            'สัญญาณมาตรฐาน Hollyland & DJI: ภาพและเสียงคมชัด เสถียร ไม่สะดุด',
            'ทีม Switcher/OB ดูแลตลอดงาน: พร้อมบันทึกและตัดต่อไฟล์ 4K / Full HD'
        ]
    },
    {
        'id': 'royal',
        'folder': 'พิธีหลวง',
        'title': 'การถ่ายภาพงานพิธีหลวง และเครื่องเกียรติยศพระราชทาน',
        'badge': 'MAIN PILLAR 1 : ROYAL CEREMONY',
        'subtitle': '“เกียรติยศสูงสุดแห่งชีวิต” ในพิธีพระราชทานน้ำหลวงอาบศพ พระราชทานโกศศพ พระราชทานเพลิงศพ และการเวียนเมรุ',
        'numeral': '02',
        'headline': 'การถ่ายภาพงานพิธีหลวง และเครื่องเกียรติยศ',
        'why_us': [
            'เกียรติยศสูงสุดแห่งชีวิต: บันทึกพิธีน้ำหลวงอาบศพ โกศ และพระราชทานเพลิงศพอย่างครบถ้วน',
            'ผ่านงานพระราชพิธีสำคัญระดับประเทศ: เข้าใจระเบียบขั้นตอน ริ้วขบวน และลำดับพิธีหลวง',
            'มาตรฐานละเอียด สำรวม สมเกียรติ: ส่งต่อภาพบันทึกประวัติศาสตร์และเกียรติยศของวงศ์ตระกูล'
        ]
    },
    {
        'id': 'chinese',
        'folder': 'ธรรมเนียมจีน และพิธีกรรม',
        'title': 'การถ่ายภาพพิธีกงเต็ก และธรรมเนียมจีนโบราณ',
        'badge': 'MAIN PILLAR 2 : CHINESE CEREMONY & KONG TEK',
        'subtitle': 'พิธีกงเต็ก คือพิธีอุทิศส่วนบุญส่วนกุศลและส่งดวงวิญญาณสู่สุคติในแบบมงคลตามประเพณีจีน ทุกขั้นตอนเต็มไปด้วยความหมาย ความศรัทธา และสายสัมพันธ์ของครอบครัว',
        'numeral': '03',
        'headline': 'การถ่ายภาพพิธีกงเต็ก และธรรมเนียมจีน',
        'why_us': [
            'สื่อถึงความกตัญญูและมงคล: บันทึกพิธีอุทิศบุญกุศลและส่งดวงวิญญาณตามโบราณประเพณีจีน',
            'แม่นยำทุกลำดับพิธีต่อเนื่อง: ข้ามสะพานโอฆสงสาร จุดไฟนำทาง และไหว้ตามลำดับอาวุโส',
            'ครบเครื่องกระดาษและสายสัมพันธ์ครอบครัว: เก็บรายละเอียดบ้านกงเต็กและความรักของลูกหลานทุกรุ่น'
        ]
    },
    {
        'id': 'chanting',
        'folder': 'บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน',
        'badge': 'MAIN PILLAR 03 : CREMATION DAY ATMOSPHERE & CANDID',
        'title': 'ภาพบรรยากาศวันฌาปนกิจ',
        'subtitle': 'การบันทึกภาพบรรยากาศและแคนดิดในวันฌาปนกิจ (Cremation Day Atmosphere & Candid Moments) ถ่ายทอด "สายสัมพันธ์ ความรัก และอารมณ์ความรู้สึก" ในช่วงเวลาสำคัญที่สุดของพิธีการ',
        'numeral': '04',
        'headline': 'ภาพบรรยากาศวันฌาปนกิจ (Atmosphere & Candid Moments)',
        'why_us': [
            'เก็บบรรยากาศแคนดิดและสายใยครอบครัว: ถ่ายทอดแววตา ความอบอุ่น การสวมกอด ให้กำลังใจ และการแสดงความอาลัยของครอบครัว ญาติมิตร และแขกคนสำคัญ',
            'บันทึกครบทุกขั้นตอนพิธีการหน้าเมรุ: เคลื่อนขบวนเวียนรอบเมรุ 3 รอบ, พิธีทอดผ้าบังสุกุล, การอ่านประวัติไว้อาลัย, การวางดอกไม้จันทน์ และพิธีประชุมเพลิง',
            'รู้กาลเทศะ ทราบมุมยืน และประสานงานราบรื่น: ช่างภาพแต่งกายสูทสากลสีดำสุภาพ สำรวม ทราบจุดยืนที่ไม่บังสายตาแขก และทำงานร่วมกับเจ้าหน้าที่ฌาปนสถานอย่างมืออาชีพ'
        ]
    },
    {
        'id': 'cremation',
        'folder': 'เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย',
        'badge': 'MAIN PILLAR 3.2 : CREMATION DAY & FAREWELL',
        'title': 'พิธีฌาปนกิจ และบันทึกความทรงจำวันสุดท้าย',
        'subtitle': 'งานศพคือพิธีสำคัญครั้งสุดท้ายในชีวิต ภาพถ่ายและวิดีโอคุณภาพสูงจะช่วยสืบสานเรื่องราว ความทรงจำ และคุณงามความดีของผู้จากไป',
        'numeral': '05',
        'headline': 'พิธีฌาปนกิจ และความทรงจำวันสุดท้าย',
        'why_us': [
            'บันทึกครบทุกวาระสำคัญ: เคลื่อนขบวนศพ เวียนรอบเมรุ ทอดผ้าบังสุกุล และวางดอกไม้จันทน์',
            'ภาพนิ่ง & วิดีโอ 4K / Full HD: คมชัด สมเกียรติ ตัดต่ออย่างประณีตเก็บไว้เป็นมรดกครอบครัว',
            'รู้จุดยืนและประสานงานราบรื่น: ชำนาญพื้นที่ฌาปนสถาน ดูแลอย่างให้เกียรติในทุกขั้นตอน'
        ]
    },
    {
        'id': 'floating',
        'folder': 'ลอยอังคาร',
        'badge': 'MAIN PILLAR 3.3 : ASHES SCATTERING CEREMONY',
        'title': 'พิธีเก็บอัฐิและลอยอังคาร และบริการเรือลอยอังคาร',
        'subtitle': 'การดูแลบันทึกภาพต่อเนื่องจนถึงพิธีการขั้นสุดท้ายอย่างสงบ บริสุทธิ์ สว่าง และร่มเย็น ท่ามกลางธรรมชาติ',
        'numeral': '06',
        'headline': 'พิธีเก็บอัฐิและลอยอังคาร และบริการเรือลอยอังคาร',
        'why_us': [
            'ดูแลต่อเนื่องจนถึงแม่น้ำและทะเล: บันทึกพิธีไหว้แม่ย่านาง เจ้าแม่คงคา และขั้นตอนบนเรือครบถ้วน',
            'มุมมองสงบ สว่าง และร่มเย็น: ถ่ายทอดช่วงเวลาโปรยดอกไม้ การอธิษฐาน และสายใยครอบครัว',
            'คล่องตัว มั่นคงบนเรือและคลื่นลม: จัดมุมกล้องปลอดภัย เก็บภาพคมชัดทุกจังหวะสำคัญ'
        ]
    },
    {
        'id': 'coffin',
        'folder': 'coffin',
        'title': 'ราชรถหีบศพมาตรฐาน & แพ็กเกจหีบศพราชรถ',
        'badge': 'RATHCHAROT COFFIN & CASKET',
        'subtitle': 'แบบหีบศพมาตรฐานและหีบศพทรงเกียรติกว่า 28 รุ่น จากแบรนด์ราชรถ พร้อมบริการครบวงจร 24 ชม.',
        'numeral': '07',
        'headline': 'ราชรถหีบศพ (28 รุ่นมาตรฐาน & ทรงเกียรติ)',
        'why_us': [
            'ครบครันกว่า 28 รุ่นมาตรฐานและทรงเกียรติ: ตั้งแต่หีบเทพพนม หีบหลุยส์ หีบคริสต์ จนถึงหีบจำปาไม้สักทองเกรดพรีเมียม',
            'วัสดุประณีต พร้อมสเปกขนาดชัดเจน: ระบุรายละเอียดเนื้อไม้ ผ้าบุ และขนาดครบถ้วนทุกรุ่นในภาพเดียว',
            'เชื่อมต่อบริการครบวงจร 24 ชม.: จัดดอกไม้หน้าศพ เคลื่อนย้ายร่างทั่วประเทศ และจัดงานศพแบบครบวงจร โดยทีมราชรถ'
        ]
    },
    {
        'id': 'promotion',
        'folder': 'Promotion',
        'title': 'โปรโมชั่นแพ็กเกจจัดงานศพครบวงจร ราชรถ',
        'badge': 'SPECIAL PROMOTION PACKAGES',
        'subtitle': 'แพ็กเกจจัดงานศพครบวงจร หีบศพ ดอกไม้หน้าหีบ รถรับร่าง พิธีกรรม พร้อมฟรีช่างภาพ 1 คืน',
        'numeral': '08',
        'headline': 'โปรโมชั่นแพ็กเกจจัดงานศพราชรถ (RVIP1, RJ1, RW1–RW6)',
        'why_us': [
            'ครบวงจรในแพ็กเกจเดียว: หีบศพมาตรฐาน/พรีเมียม ดอกไม้หน้าหีบ Luxury รถรับร่าง ชุดรดน้ำศพ และอุปกรณ์พิธีครบครัน',
            'ฟรี! บริการช่างภาพงานศพ 1 คืน: ทุกแพ็กเกจโปรโมชั่นแถมฟรีช่างภาพมืออาชีพบันทึกภาพบรรยากาศพิธี 1 คืน',
            'รายละเอียดชัดเจน ไม่บวกเพิ่มแอบแฝง: แสดงรายการอุปกรณ์ของแถมและราคาสุทธิชัดเจนในภาพเดียว คลิกขยายดูรายละเอียดได้ทันที'
        ]
    }
]

total_images = 0
for cat in categories:
    folder_path = os.path.join(workspace, cat['folder'])
    all_files = sorted(
        [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))],
        key=natural_sort_key
    )
    
    # Filter special logo & QR files from royal ceremony gallery
    if cat['id'] == 'royal':
        all_files = [f for f in all_files if f not in ['S__246022147.jpg', 'S__246022150_0.png', 'S__246022151_0.png']]
    elif cat['id'] == 'coffin':
        all_files = [f for f in all_files if f not in ['1794279723605.jpg']]
    
    # URL encoded relative paths for web safety
    encoded_images = []
    for f in all_files:
        rel_path = f"{cat['folder']}/{f}"
        encoded_path = f"{urllib.parse.quote(cat['folder'])}/{urllib.parse.quote(f)}"
        encoded_images.append({
            'filename': f,
            'rel_path': rel_path,
            'encoded_path': encoded_path
        })
    cat['images'] = encoded_images
    total_images += len(encoded_images)
    print(f"Loaded {cat['title']}: {len(encoded_images)} images")

print(f"Total curated gallery images: {total_images}")

# Also add brand logos and QR
branding = {
    'logo_rathcharot': f"{urllib.parse.quote('พิธีหลวง')}/S__246022151_0.png",
    'logo_funeral_photo': f"{urllib.parse.quote('พิธีหลวง')}/S__246022150_0.png",
    'qr_funeral_photo': f"{urllib.parse.quote('พิธีหลวง')}/S__246022147.jpg",
    'website_photo': 'https://www.ช่างภาพงานศพ.com',
    'website_rathcharot': 'https://www.rathcharot.com',
    'line_id': 'Rathcharot',
    'phone': '085-999-2396',
    'tiktok': 'Rathcharot',
    'ig': 'Rathcharot'
}

js_content = f"// Generated Catalog Data for Rathcharot & ChangPhapNganSop\nconst CATALOG_BRANDING = {json.dumps(branding, ensure_ascii=False, indent=2)};\n\nconst CATALOG_CATEGORIES = {json.dumps(categories, ensure_ascii=False, indent=2)};\n"

with open(os.path.join(workspace, 'catalog_data.js'), 'w', encoding='utf-8') as out_f:
    out_f.write(js_content)

print("Saved catalog_data.js successfully!")
