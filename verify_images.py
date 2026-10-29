import re
import os
import urllib.parse

html = open('index.html', encoding='utf-8').read()
matches = re.findall(r'(?:src|data-src)="([^"]+)"', html)
missing = []
tested = set()
for m in matches:
    if m.startswith('http') or m.startswith('data:') or m.startswith('#') or m == '':
        continue
    decoded = urllib.parse.unquote(m)
    if decoded in tested:
        continue
    tested.add(decoded)
    if not os.path.exists(decoded):
        missing.append((m, decoded))

print(f"Total local image paths tested: {len(tested)}")
if missing:
    print("MISSING FILES:")
    for orig, dec in missing:
        print(f"  {orig} -> {dec}")
else:
    print("SUCCESS: 100% of all image paths exist and resolved perfectly!")
