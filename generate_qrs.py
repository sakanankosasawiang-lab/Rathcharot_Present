import qrcode
import qrcode.image.svg

# 1. Rathcharot website
factory = qrcode.image.svg.SvgPathImage
img_rathcharot = qrcode.make('https://www.rathcharot.com', image_factory=factory, box_size=10, border=2)
img_rathcharot.save('qr_rathcharot.svg')

# 2. LINE consultation
img_line = qrcode.make('https://line.me/ti/p/~Rathcharot', image_factory=factory, box_size=10, border=2)
img_line.save('qr_line.svg')

# 3. Chang Phap Ngan Sop website (clean SVG fallback)
img_photo = qrcode.make('https://www.ช่างภาพงานศพ.com', image_factory=factory, box_size=10, border=2)
img_photo.save('qr_changphapngansop.svg')

print("Generated QR code SVGs successfully!")
