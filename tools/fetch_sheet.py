"""inbox/<폴더> 사진을 작은 번호 붙은 모아보기(12장/장)로 만든다 → 토큰 절약.
사용: python3 tools/fetch_sheet.py inbox/<폴더> <출력폴더>"""
import sys, glob, os
from PIL import Image, ImageDraw, ImageOps, ImageFont
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
fs = sorted([f for f in glob.glob(os.path.join(src, "*")) if f.lower().endswith((".jpg",".jpeg",".png"))])
W, H, C = 300, 400, 4
for s in range(0, len(fs), 12):
    sheet = Image.new("RGB", (W*C, H*3), "white")
    for k, f in enumerate(fs[s:s+12]):
        im = ImageOps.exif_transpose(Image.open(f)); im.thumbnail((W, H))
        x, y = (k % C)*W, (k//C)*H
        sheet.paste(im, (x, y)); d = ImageDraw.Draw(sheet)
        d.rectangle([x, y, x+48, y+30], fill="black")
        d.text((x+6, y+3), os.path.basename(f)[:2], fill="yellow", font=ImageFont.load_default(24))
    p = os.path.join(out, f"sheet{s//12+1}.jpg"); sheet.save(p, quality=80); print(p)
