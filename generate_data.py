import os
import json
import urllib.parse

workspace = r'c:\Apps\Rathcharot_Present'

categories = [
    {
        'id': 'profile',
        'folder': 'Photographer',
        'title': 'ทำไมต้องจ้างช่างภาพระดับ Professional?',
        'badge': 'PROFESSIONALISM & EXPERT TEAM',
        'subtitle': 'ประสบการณ์งานพิธีหลวงและงานสำคัญ พร้อมการแก้ปัญหาเฉพาะหน้าและการวางตัวที่เหมาะสมที่สุด',
        'numeral': '06',
        'headline': 'ทำไมต้องจ้างช่างภาพระดับ Professional?',
        'why_us': [
            'Professionalism มูลค่าสูงสุดของช่างภาพ: ช่างภาพประสบการณ์สูงมีไหวพริบในการแก้ไขปัญหาเฉพาะหน้าและรับมือทุกสถานการณ์ระหว่างการทำงานได้อย่างราบรื่น',
            'รู้กาลเทศะในงานศพและงานพิธีใหญ่: รู้ว่าควรทำอะไร ไม่ควรทำอะไรในแต่ละช่วงเวลา และวางตัวอย่างไรให้เหมาะสม สมเกียรติเจ้าภาพและแขกผู้ใหญ่',
            'มาตรฐานบันทึกประวัติศาสตร์ชาติ 100%: ทีมงานแต่งกายสูทสากลสีดำ กิริยาสำรวม นอบน้อม พร้อมอุปกรณ์ Dual-Slot สำรองข้อมูลคู่ขนาน'
        ]
    },
    {
        'id': 'streaming',
        'folder': 'streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว',
        'title': 'บริการจอทีวี 65" & ถ่ายทอดสด (Live Stream & Display)',
        'badge': 'SPECIAL HIGHLIGHT : LIVE STREAM & DISPLAY',
        'subtitle': 'ถ่ายทอดสดระบบสัญญาณระดับมืออาชีพด้วยอุปกรณ์มาตรฐาน คมชัด เสถียร จาก Hollyland และ DJI พร้อมอุปกรณ์เเละทีมงานเทคนิคดูแลตลอดงาน',
        'numeral': '★',
        'headline': 'บริการจอทีวี 65" & ถ่ายทอดสด (Live Stream & Display)',
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
        'badge': 'MAIN PILLAR 3.1 : ATMOSPHERE & EVENING CHANTING',
        'title': 'การถ่ายภาพพิธีสวดพระอภิธรรม และภาพบรรยากาศงานพิธี',
        'subtitle': 'ภาพบรรยากาศในงานศพ (Atmosphere & Candid Moments) ไม่ใช่แค่การถ่ายภาพคนมาร่วมงาน แต่คือการบันทึก "สายสัมพันธ์ ความรัก และอารมณ์ความรู้สึก" ของการจากไปชั่วนิรันดร์',
        'numeral': '04',
        'headline': 'พิธีสวดพระอภิธรรม & ภาพบรรยากาศ (Atmosphere & Candid)',
        'why_us': [
            'บันทึกอารมณ์และความผูกพัน: ภาพแคนดิด แววตา และการให้กำลังใจของครอบครัวและญาติมิตร',
            'จัดองค์ประกอบสง่างาม สมเกียรติ: โทนสีสุภาพ คลาสสิก เพื่อสืบสานคุณงามความดีของผู้จากไป',
            'สุภาพ สำรวม ใช้ Silent Shutter: ปฏิบัติงานอย่างเงียบสงบ ไม่รบกวนบรรยากาศการฟังสวด'
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
        'title': 'พิธีลอยอังคาร และการส่งดวงวิญญาณสู่สุคติภูมิ',
        'subtitle': 'การดูแลบันทึกภาพต่อเนื่องจนถึงพิธีการขั้นสุดท้ายอย่างสงบ บริสุทธิ์ สว่าง และร่มเย็น ท่ามกลางธรรมชาติ',
        'numeral': '06',
        'headline': 'พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติ',
        'why_us': [
            'ดูแลต่อเนื่องจนถึงแม่น้ำและทะเล: บันทึกพิธีไหว้แม่ย่านาง เจ้าแม่คงคา และขั้นตอนบนเรือครบถ้วน',
            'มุมมองสงบ สว่าง และร่มเย็น: ถ่ายทอดช่วงเวลาโปรยดอกไม้ การอธิษฐาน และสายใยครอบครัว',
            'คล่องตัว มั่นคงบนเรือและคลื่นลม: จัดมุมกล้องปลอดภัย เก็บภาพคมชัดทุกจังหวะสำคัญ'
        ]
    },
    {
        'id': 'coffin',
        'folder': 'coffin',
        'title': 'แคตตาล็อกหีบศพมาตรฐาน & แพ็กเกจหีบศพราชรถ',
        'badge': 'RATHCHAROT COFFIN & CASKET CATALOG',
        'subtitle': 'แบบหีบศพมาตรฐานและหีบศพทรงเกียรติกว่า 28 รุ่น จากแบรนด์ราชรถ พร้อมบริการครบวงจร 24 ชม.',
        'numeral': '07',
        'headline': 'แคตตาล็อกหีบศพราชรถ (28 รุ่นมาตรฐาน & ทรงเกียรติ)',
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
    all_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
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
