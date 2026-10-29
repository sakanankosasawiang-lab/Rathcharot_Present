import os
import json
import urllib.parse

workspace = r'c:\Apps\Rathcharot_Present'

categories = [
    {
        'id': 'profile',
        'folder': 'โปรไฟล์ช่างภาพ',
        'title': 'ทีมช่างภาพมืออาชีพ ราชรถ & ช่างภาพงานศพ',
        'badge': 'PROFESSIONAL TEAM',
        'subtitle': 'ช่างภาพและทีมงานมืออาชีพ ได้รับการอบรมระเบียบปฏิบัติและกาลเทศะสูงสุด',
        'numeral': '01',
        'headline': 'มาตรฐานทีมช่างภาพมืออาชีพ',
        'why_us': [
            'ทีมช่างภาพแต่งกายชุดสูทสุภาพ เรียบร้อย สำรวม รู้กาลเทศะทุกลำดับพิธีการ',
            'มีประสบการณ์ตรงในงานพระราชทานเพลิงศพ งานพิธีหลวง และงานบุคคลสำคัญระดับประเทศ',
            'อุปกรณ์กล้องคู่เกรดโปรเฟสชั่นแนล (Dual Full-Frame) บันทึกไฟล์คู่สำรองข้อมูลทันที ไม่มีคำว่าภาพหาย',
            'ใช้เลนส์เกรดสูงและเทเลโฟโต้ เก็บภาพคมชัดในที่แสงน้อย โดยไม่เดินตัดหน้าหรือรบกวนแขกผู้ใหญ่'
        ]
    },
    {
        'id': 'streaming',
        'folder': 'streaming สด โดยทีมงานมืออาชีพ พร้อมอุปกรณ์ที่มีคุณภาพไฮเล็บโซลูชั่น ด้วยขนาดจอ 65 -75 นิ้ว',
        'title': 'Live Streaming ถ่ายทอดสด & จอ TV/LED 65-75 นิ้ว',
        'badge': 'SPECIAL HIGHLIGHT',
        'subtitle': 'ถ่ายทอดสดงานพิธีด้วยระบบ High-Definition พร้อมทีมงานดูแลฟรีตลอดงาน',
        'numeral': '★',
        'headline': 'บริการ Live Streaming & จอถ่ายทอดสดรอบศาลา',
        'why_us': [
            'ฟรี! ทีมงานมืออาชีพดูแลระบบตลอดงาน มี Switcher/OB ควบคุมตัดสลับกล้อง เจ้าภาพไม่ต้องกังวล',
            'ติดตั้งจอคมชัดขนาดใหญ่ 65 - 75 นิ้ว รอบศาลา แขกที่นั่งด้านนอกเห็นพิธีการชัดเจนทุกมุมมอง',
            'ถ่ายทอดสดออนไลน์สัญญาณเสถียร รองรับญาติและแขกคนสำคัญทั่วโลกที่อยู่ต่างประเทศ/ต่างจังหวัด',
            'บันทึกไฟล์วิดีโอ Full HD / 4K ส่งมอบให้ครอบครัวเก็บไว้เป็นความทรงจำอันทรงคุณค่า'
        ]
    },
    {
        'id': 'royal',
        'folder': 'พิธีหลวง',
        'title': 'การถ่ายภาพงานพิธีหลวง (พระราชทานเพลิงศพ / น้ำหลวงอาบศพ)',
        'badge': 'MAIN PILLAR 1',
        'subtitle': 'พิธีพระราชทานเกียรติยศสูงสุดแห่งผู้วายชนม์และวงศ์ตระกูล',
        'numeral': '02',
        'headline': '1. การถ่ายภาพงานพิธีหลวง',
        'why_us': [
            'แม่นยำทุกลำดับพิธีการ เข้าใจขั้นตอนการรับน้ำหลวง หีบเพลิงพระราชทาน และริ้วขบวนอิสริยยศ',
            'รู้ตำแหน่งยืนและมุมกล้องที่ถูกต้อง ไม่บังสายตาประธาน ไม่ล้ำเส้นเขตพิธีเจ้าหน้าที่สำนักพระราชวัง',
            'บันทึกความสง่างามสมเกียรติยศ ทั้งโกศ ลองใน หีบทองลายสลัก พวงมาลาพระราชทาน และริ้วขบวน'
        ]
    },
    {
        'id': 'chinese',
        'folder': 'ธรรมเนียมจีน และพิธีกรรม',
        'badge': 'MAIN PILLAR 2',
        'title': 'การถ่ายภาพพิธีจีน และธรรมเนียมปฏิบัติ (กงเต็ก)',
        'subtitle': 'ธรรมเนียมจีน พิธีกงเต็ก พิธีเคลื่อนย้าย และการส่งดวงวิญญาณ',
        'numeral': '03',
        'headline': '2. การถ่ายภาพพิธีจีน และธรรมเนียมปฏิบัติ',
        'why_us': [
            'รู้จริงเรื่องธรรมเนียมจีน เข้าใจลำดับพิธีกงเต็ก พิธีข้ามสะพานโอฆสงสาร การจุดไฟ และการไหว้ตามลำดับอาวุโส',
            'ไม่พลาดช็อตสำคัญที่มีเพียงเสี้ยววินาที เพราะพิธีกรรมจีนรวดเร็ว ช่างภาพต้องอ่านเกมล่วงหน้าได้ทันที',
            'เก็บครบทั้งความขลังและสายใยความกตัญญู บันทึกรายละเอียดเครื่องกระดาษ หีบไม้สัก และความผูกพันของลูกหลาน'
        ]
    },
    {
        'id': 'chanting',
        'folder': 'บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน',
        'badge': 'MAIN PILLAR 3.1',
        'title': 'พิธีสวดพระอภิธรรม และบรรยากาศในศาลา',
        'subtitle': 'บันทึกทุกบรรยากาศ ให้ครบทุกองค์ประกอบของการจัดงาน',
        'numeral': '04',
        'headline': '3. การถ่ายภาพพิธีสวดอภิธรรม',
        'why_us': [
            'เก็บครบทุกองค์ประกอบ พวงหรีดจากบุคคลสำคัญ ดอกไม้หน้าหีบ ป้ายงาน และของชำร่วย',
            'บันทึกภาพแขกผู้มีเกียรติทุกท่านที่มาร่วมไว้อาลัยอย่างครบถ้วน เพื่อใช้จัดทำหนังสืออนุสรณ์หรือส่งขอบคุณ',
            'ทำงานเงียบ สำรวม แสงแฟลชและมุมกล้องนุ่มนวล ไม่รบกวนสมาธิระหว่างการฟังสวดพระอภิธรรม'
        ]
    },
    {
        'id': 'cremation',
        'folder': 'เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย',
        'badge': 'MAIN PILLAR 3.2',
        'title': 'ความทรงจำวันสุดท้าย (วันฌาปนกิจ / พระราชทานเพลิง)',
        'subtitle': 'เก็บทุกอย่างเพื่อความทรงจำวันสุดท้าย',
        'numeral': '05',
        'headline': 'ความทรงจำวันสุดท้าย (วันฌาปนกิจ)',
        'why_us': [
            'ถ่ายทอดอารมณ์ด้วยความเคารพ (Candid & Emotion) เก็บภาพความรัก รอยยิ้ม และการกราบลาครั้งสุดท้ายอย่างนุ่มนวล',
            'บันทึกพิธีเคลื่อนขบวนเวียนเมรุ พิธีทอดผ้าไตรบังสุกุล และการวางดอกไม้จันทน์อย่างสมบูรณ์แบบ',
            'ช่างภาพประจำจุดสำคัญทุกทิศทาง เก็บภาพรวมและภาพโคลสอัปได้ครบทุกอารมณ์ความรู้สึก'
        ]
    },
    {
        'id': 'floating',
        'folder': 'ลอยอังคาร',
        'badge': 'MAIN PILLAR 3.3',
        'title': 'พิธีลอยอังคารส่งดวงวิญญาณสู่สุคติ',
        'subtitle': 'บริการดูแลต่อเนื่องจนเสร็จสิ้นพิธีการทั้งหมด',
        'numeral': '06',
        'headline': 'พิธีลอยอังคารส่งดวงวิญญาณ',
        'why_us': [
            'บริการต่อเนื่องจนถึงแม่น้ำและทะเล บันทึกพิธีการบนเรือลอยอังคารอย่างใกล้ชิดและปลอดภัย',
            'ถ่ายทอดความสงบ อบอุ่น และการส่งดวงวิญญาณอันเป็นที่รักสู่สุคติภพอย่างงดงาม',
            'ส่งมอบไฟล์ภาพและวิดีโอคุณภาพสูงครบเซ็ต สะดวก รวดเร็ว พร้อมใช้งาน'
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
