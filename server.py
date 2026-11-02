#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom HTTP Server for Rathcharot Funeral Photography & Catalog Presentation
Provides static file serving and Admin REST API endpoints:
- Auth (user: admin, pass: admin1234)
- Direct routing for /admin and /admin/ to admin.html
- Catalog & Slide Visual management (updates index.html and catalog_data.js)
- Photo deletion (archives to .deleted_photos), edit, and upload
"""

import os
import sys
import json
import re
import shutil
import base64
import urllib.parse
try:
    from http.server import ThreadingHTTPServer as HTTPServerClass
except ImportError:
    from http.server import HTTPServer as HTTPServerClass
from http.server import SimpleHTTPRequestHandler

PORT = 8080
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DELETED_DIR = os.path.join(BASE_DIR, '.deleted_photos')
os.makedirs(DELETED_DIR, exist_ok=True)

AUTH_TOKEN = "rathcharot_admin_token_2026_secured"

def get_catalog_categories_from_file():
    cat_path = os.path.join(BASE_DIR, 'catalog_data.js')
    if not os.path.exists(cat_path):
        return []
    with open(cat_path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'const CATALOG_CATEGORIES\s*=\s*(\[[\s\S]*?\]);', content)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception as e:
            print("Error parsing CATALOG_CATEGORIES:", e)
    return []

def get_catalog_branding_from_file():
    cat_path = os.path.join(BASE_DIR, 'catalog_data.js')
    if not os.path.exists(cat_path):
        return {}
    with open(cat_path, 'r', encoding='utf-8') as f:
        content = f.read()
    m = re.search(r'const CATALOG_BRANDING\s*=\s*(\{[\s\S]*?\});', content)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception as e:
            print("Error parsing CATALOG_BRANDING:", e)
    return {}

def save_catalog_categories_to_file(categories, branding=None):
    cat_path = os.path.join(BASE_DIR, 'catalog_data.js')
    if branding is None:
        branding = get_catalog_branding_from_file()
    js_content = f"// Generated Catalog Data for Rathcharot & ChangPhapNganSop\nconst CATALOG_BRANDING = {json.dumps(branding, ensure_ascii=False, indent=2)};\n\nconst CATALOG_CATEGORIES = {json.dumps(categories, ensure_ascii=False, indent=2)};\n"
    with open(cat_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

def parse_slides_from_html():
    html_path = os.path.join(BASE_DIR, 'index.html')
    if not os.path.exists(html_path):
        return []
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    slide_matches = list(re.finditer(r'<section class="slide[^"]*" data-slide-index="(\d+)" data-category-id="([^"]+)">', html))
    slides_info = []

    for i, m in enumerate(slide_matches):
        slide_idx = int(m.group(1))
        cat_id = m.group(2)
        start_pos = m.start()
        end_pos = slide_matches[i+1].start() if i+1 < len(slide_matches) else html.find('</main>')
        slide_content = html[start_pos:end_pos]

        title_m = re.search(r'<h2 class="slide-title">([^<]+)</h2>', slide_content)
        title = title_m.group(1) if title_m else f"Slide {slide_idx}"

        hero_m = re.search(r'<img class="hero-img"\s+src="([^"]+)"\s+alt="([^"]*)"', slide_content)
        hero_src = hero_m.group(1) if hero_m else ""
        hero_alt = hero_m.group(2) if hero_m else ""

        thumb_matches = re.findall(r'<div class="slide-thumb-item[^"]*"\s+data-src="([^"]+)"', slide_content)

        slides_info.append({
            "slide_index": slide_idx,
            "category_id": cat_id,
            "title": title,
            "hero_src": hero_src,
            "hero_alt": hero_alt,
            "thumbs": thumb_matches
        })
    return slides_info

def update_slide_in_html(slide_idx, hero_src, hero_alt, thumbs, total_count=None):
    html_path = os.path.join(BASE_DIR, 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    pattern = rf'(<section class="slide[^"]*" data-slide-index="{slide_idx}"[^>]*>)([\s\S]*?)(</section>)'
    m = re.search(pattern, html)
    if not m:
        return False, f"Slide index {slide_idx} not found in index.html"

    prefix = m.group(1)
    slide_body = m.group(2)
    suffix = m.group(3)

    if hero_src:
        hero_pattern = r'(<img class="[^"]*hero-img[^"]*"\s+src=")[^"]*("\s+alt=")[^"]*(")'
        def hero_repl(match):
            alt_text = hero_alt if hero_alt is not None else "ภาพบรรยากาศพิธีการ"
            return f'{match.group(1)}{hero_src}{match.group(2)}{alt_text}{match.group(3)}'
        slide_body = re.sub(hero_pattern, hero_repl, slide_body, count=1)

    if thumbs is not None:
        strip_class = 'slide-thumb-strip slide-thumb-strip-portrait' if slide_idx == 7 else 'slide-thumb-strip'
        thumbs_html = f'<div class="{strip_class}">\n'
        for i, t in enumerate(thumbs):
            active_cls = ' active' if i == 0 else ''
            thumbs_html += f'                  <div class="slide-thumb-item{active_cls}" data-src="{t}"><img src="{t}"></div>\n'
        thumbs_html += '                </div>'
        
        strip_pattern = r'<div class="slide-thumb-strip[^"]*">[\s\S]*?</div>(?=\s*<div class="visual-actions-row">)'
        slide_body = re.sub(strip_pattern, thumbs_html, slide_body, count=1)

    if total_count is not None:
        count_pattern = r'(<span class="photo-count-pill">[^:]*:\s*)\d+(\s*ภาพ</span>)'
        slide_body = re.sub(count_pattern, rf'\g<1>{total_count}\g<2>', slide_body, count=1)

    new_html = html[:m.start()] + prefix + slide_body + suffix + html[m.end():]
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    return True, "Slide visual updated successfully"

def resync_all_folders():
    categories = get_catalog_categories_from_file()
    total_found = 0
    for cat in categories:
        folder_path = os.path.join(BASE_DIR, cat['folder'])
        if not os.path.exists(folder_path):
            continue
        all_files = sorted([f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])
        if cat['id'] == 'royal':
            all_files = [f for f in all_files if f not in ['S__246022147.jpg', 'S__246022150_0.png', 'S__246022151_0.png']]
        
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
        total_found += len(encoded_images)
    save_catalog_categories_to_file(categories)
    return total_found


class RathcharotServerHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS and disable aggressive caching for dev
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path

        # Direct route for /admin, /admin/, /admin.html
        if clean_path in ['/admin', '/admin/', '/admin/index.html']:
            admin_file = os.path.join(BASE_DIR, 'admin.html')
            if os.path.exists(admin_file):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                with open(admin_file, 'rb') as f:
                    content = f.read()
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return

        # API: get catalog data
        if clean_path == '/api/catalog-data':
            cats = get_catalog_categories_from_file()
            branding = get_catalog_branding_from_file()
            slides = parse_slides_from_html()
            resp = {
                'status': 'ok',
                'branding': branding,
                'categories': cats,
                'slides': slides
            }
            self.send_json(resp)
            return

        # API: list deleted photos
        if clean_path == '/api/deleted-photos':
            deleted_list = []
            if os.path.exists(DELETED_DIR):
                for sub in os.listdir(DELETED_DIR):
                    sub_path = os.path.join(DELETED_DIR, sub)
                    if os.path.isdir(sub_path):
                        for f in os.listdir(sub_path):
                            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                                deleted_list.append({
                                    'category_id': sub,
                                    'filename': f,
                                    'deleted_path': f".deleted_photos/{sub}/{f}"
                                })
            self.send_json({'status': 'ok', 'deleted_photos': deleted_list})
            return

        # Default static file handling
        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        clean_path = parsed.path

        # Read JSON body
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
        try:
            body = json.loads(post_data.decode('utf-8'))
        except Exception:
            body = {}

        # 1. API: Login
        if clean_path == '/api/login':
            user = body.get('username', '').strip()
            password = body.get('password', '').strip()
            if user == 'admin' and password == 'admin1234':
                self.send_json({
                    'status': 'ok',
                    'success': True,
                    'token': AUTH_TOKEN,
                    'message': 'เข้าสู่ระบบสำเร็จ'
                })
            else:
                self.send_json({
                    'status': 'error',
                    'success': False,
                    'message': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง (user: admin, password: admin1234)'
                }, code=401)
            return

        # 2. API: Save Slide Visual (Hero & Thumbnails)
        if clean_path == '/api/save-slide':
            slide_idx = body.get('slide_index')
            hero_src = body.get('hero_src')
            hero_alt = body.get('hero_alt', 'ภาพบรรยากาศพิธีการ')
            thumbs = body.get('thumbs', [])
            total_count = body.get('total_count')

            if slide_idx is None:
                self.send_json({'status': 'error', 'message': 'Missing slide_index'}, code=400)
                return

            success, msg = update_slide_in_html(slide_idx, hero_src, hero_alt, thumbs, total_count)
            if success:
                self.send_json({'status': 'ok', 'success': True, 'message': 'บันทึกภาพสไลด์เรียบร้อยแล้ว'})
            else:
                self.send_json({'status': 'error', 'success': False, 'message': msg}, code=500)
            return

        # 3. API: Delete Photo
        if clean_path == '/api/delete-photo':
            cat_id = body.get('category_id')
            filename = body.get('filename')
            if not cat_id or not filename:
                self.send_json({'status': 'error', 'message': 'Missing category_id or filename'}, code=400)
                return

            cats = get_catalog_categories_from_file()
            target_cat = next((c for c in cats if c['id'] == cat_id), None)
            if not target_cat:
                self.send_json({'status': 'error', 'message': 'Category not found'}, code=404)
                return

            # Find and remove image
            target_img = next((img for img in target_cat['images'] if img['filename'] == filename), None)
            if not target_img:
                self.send_json({'status': 'error', 'message': 'Photo not found in category'}, code=404)
                return

            target_cat['images'] = [img for img in target_cat['images'] if img['filename'] != filename]

            # Move physical file to .deleted_photos archive
            src_file = os.path.join(BASE_DIR, target_cat['folder'], filename)
            cat_del_dir = os.path.join(DELETED_DIR, cat_id)
            os.makedirs(cat_del_dir, exist_ok=True)
            dst_file = os.path.join(cat_del_dir, filename)

            if os.path.exists(src_file):
                try:
                    shutil.move(src_file, dst_file)
                except Exception as e:
                    print("Error moving file to .deleted_photos:", e)

            # Save updated categories
            save_catalog_categories_to_file(cats)

            # Check if this image was in any slide's hero or thumbs, replace if needed
            enc_target = target_img['encoded_path']
            slides = parse_slides_from_html()
            for s in slides:
                if s['category_id'] == cat_id:
                    new_hero = s['hero_src']
                    new_thumbs = list(s['thumbs'])
                    needs_update = False

                    # Check hero
                    if enc_target in s['hero_src'] or filename in s['hero_src']:
                        needs_update = True
                        if target_cat['images']:
                            new_hero = target_cat['images'][0]['encoded_path']
                        else:
                            new_hero = ""

                    # Check thumbs
                    if any(enc_target in t or filename in t for t in new_thumbs):
                        needs_update = True
                        new_thumbs = [t for t in new_thumbs if enc_target not in t and filename not in t]
                        while len(new_thumbs) < min(4, len(target_cat['images'])):
                            for candidate in target_cat['images']:
                                c_path = candidate['encoded_path']
                                if c_path not in new_thumbs:
                                    new_thumbs.append(c_path)
                                    if len(new_thumbs) >= min(4, len(target_cat['images'])):
                                        break

                    if needs_update:
                        update_slide_in_html(s['slide_index'], new_hero, s['hero_alt'], new_thumbs, len(target_cat['images']))

            self.send_json({
                'status': 'ok',
                'success': True,
                'message': f'ลบภาพ {filename} เรียบร้อยแล้ว (ย้ายไปเก็บที่ .deleted_photos)',
                'remaining_count': len(target_cat['images'])
            })
            return

        # 4. API: Upload Photo
        if clean_path == '/api/upload-photo':
            cat_id = body.get('category_id')
            filename = body.get('filename')
            data_base64 = body.get('data_base64')

            if not cat_id or not filename or not data_base64:
                self.send_json({'status': 'error', 'message': 'Missing fields'}, code=400)
                return

            cats = get_catalog_categories_from_file()
            target_cat = next((c for c in cats if c['id'] == cat_id), None)
            if not target_cat:
                self.send_json({'status': 'error', 'message': 'Category not found'}, code=404)
                return

            # Clean filename
            safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
            folder_path = os.path.join(BASE_DIR, target_cat['folder'])
            target_file_path = os.path.join(folder_path, safe_filename)

            # Strip data url prefix if present
            if ',' in data_base64:
                data_base64 = data_base64.split(',', 1)[1]

            try:
                file_bytes = base64.b64decode(data_base64)
                with open(target_file_path, 'wb') as f:
                    f.write(file_bytes)
            except Exception as e:
                self.send_json({'status': 'error', 'message': f'Failed to write file: {str(e)}'}, code=500)
                return

            # Re-sync category
            resync_all_folders()

            self.send_json({
                'status': 'ok',
                'success': True,
                'message': f'อัปโหลดภาพ {safe_filename} เข้าสู่หมวด {target_cat["title"]} สำเร็จ',
                'filename': safe_filename
            })
            return

        # 5. API: Restore Photo from .deleted_photos
        if clean_path == '/api/restore-photo':
            cat_id = body.get('category_id')
            filename = body.get('filename')
            if not cat_id or not filename:
                self.send_json({'status': 'error', 'message': 'Missing parameters'}, code=400)
                return

            cats = get_catalog_categories_from_file()
            target_cat = next((c for c in cats if c['id'] == cat_id), None)
            if not target_cat:
                self.send_json({'status': 'error', 'message': 'Category not found'}, code=404)
                return

            del_file = os.path.join(DELETED_DIR, cat_id, filename)
            restored_file = os.path.join(BASE_DIR, target_cat['folder'], filename)

            if os.path.exists(del_file):
                shutil.move(del_file, restored_file)
                resync_all_folders()
                self.send_json({
                    'status': 'ok',
                    'success': True,
                    'message': f'กู้คืนภาพ {filename} กลับสู่หมวด {target_cat["title"]} เรียบร้อยแล้ว'
                })
            else:
                self.send_json({'status': 'error', 'message': 'File not found in deleted archive'}, code=404)
            return

        # 6. API: Re-sync Folders
        if clean_path == '/api/resync':
            count = resync_all_folders()
            self.send_json({
                'status': 'ok',
                'success': True,
                'message': f'ซิงค์โฟลเดอร์สำเร็จ ตรวจพบภาพทั้งหมด {count} ภาพ'
            })
            return

        self.send_json({'status': 'error', 'message': 'Not Found'}, code=404)

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server():
    server_address = ('', PORT)
    httpd = HTTPServerClass(server_address, RathcharotServerHandler)
    httpd.daemon_threads = True
    print(f"==================================================")
    print(f" Rathcharot Web Server Running on port {PORT}")
    print(f" Main Presentation:  http://localhost:{PORT}")
    print(f" Admin Dashboard:    http://localhost:{PORT}/admin")
    print(f" Admin Credentials:  user: admin | pass: admin1234")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
