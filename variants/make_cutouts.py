# moto-a 사진에서 히어로 누끼 2장을 뽑는다 (rembg isnet-general-use).
#   angle-frontR.jpg → cut-quarter.png (1224×1118 안에 맞춤)
#   angle-front.jpg  → cut-front.png   (850×1195 안에 맞춤)
#   python C:/web-project/SP/variants/make_cutouts.py
import os
from PIL import Image
from rembg import remove, new_session

IMG = r'C:\web-project\mintcl-netlify-spa\public\templates\moto-a\assets\img'
JOBS = [('angle-frontR.jpg', 'cut-quarter.png', (1224, 1118)), ('angle-front.jpg', 'cut-front.png', (850, 1195))]
sess = new_session('isnet-general-use')
for src, dst, box in JOBS:
    im = Image.open(os.path.join(IMG, src)).convert('RGB')
    out = remove(im, session=sess).convert('RGBA')
    bbox = out.getbbox()
    if bbox:
        out = out.crop(bbox)
    out.thumbnail(box, Image.LANCZOS)
    canvas = Image.new('RGBA', box, (0, 0, 0, 0))
    canvas.paste(out, ((box[0] - out.width) // 2, box[1] - out.height), out)  # 바닥 정렬
    canvas.save(os.path.join(IMG, dst))
    print(dst, canvas.size)
