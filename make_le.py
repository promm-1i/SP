# SP 사이트를 LE(럭스일렉트라) 사이트로 복제한다. 구조·디자인은 동일, 회사 정보·로고·이메일만 교체.
#   python C:/web-project/SP/make_le.py
# 결과: C:/web-project/LE/  (매번 SP 기준으로 새로 생성한다 — LE 를 직접 고치지 말고 SP 를 고친 뒤 다시 돌린다)
import os, shutil, re, stat

SRC = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(SRC), 'LE')
BRAND = os.path.join(SRC, 'le-brand')   # LE 전용 이미지(파일명이 SP 와 같은 것은 복사 후 덮어쓴다)

REPL = [
    ('주식회사 에스피모빌리티', '주식회사 럭스일렉트라'),
    ('㈜에스피모빌리티', '㈜럭스일렉트라'),
    ('에스피모빌리티', '럭스일렉트라'),
    ('SP MOBILITY', 'LUX ELECTRA'),
    ('SP Mobility', 'Lux Electra'),
    ('대표 안성섭', '대표 김진하 · 박영춘 (공동대표)'),
    ('<dd>안성섭</dd>', '<dd>김진하 · 박영춘 (공동대표)</dd>'),
    ('716-86-03649', '494-86-03981'),
    ('2024년 8월', '2025년 12월'),
    ('봉신로230번길 42, 2층', '봉신로230번길 42, 1층'),
    ('info.spmobility@gmail.com', 'bestion41@luxelectra.co.kr'),
    # 사업 분야는 각 사 등록증 종목 기준 (LE: 모터사이클 제조 · 축전지 제조 · 기타 운송장비 임대)
    ('전기오토바이 · 전기충전기 · 전기배터리 · 소프트웨어 개발', '전기오토바이 제조 · 축전지 제조 · 운송장비 임대'),
    ('logo-sp-white.png', 'logo-le-white.png'),
    ('logo-sp.png', 'logo-le.png'),
    ('spmobility.netlify.app', 'luxelectra.netlify.app'),   # og:image 절대경로
]

# LE 는 깃 저장소(promm-1i/LE)라 .git 은 남기고 내용물만 비운다 — 통째로 지우면 원격 연결이 날아간다
def rm(path):
    shutil.rmtree(path, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))


if os.path.exists(DST):
    for name in os.listdir(DST):
        if name == '.git':
            continue
        p = os.path.join(DST, name)
        rm(p) if os.path.isdir(p) else os.remove(p)
else:
    os.makedirs(DST)
shutil.copytree(SRC, DST, dirs_exist_ok=True, ignore=shutil.ignore_patterns(
    'make_le.py', 'make_variants.py', 'variants', 'le-brand', '__pycache__', '.git', '.impeccable'))

# 문자열 교체 — html 외에 dealers.js(본사 카드)·css/js 머리말에도 사명이 들어 있다
for root, dirs, files in os.walk(DST):
    for name in files:
        if not name.endswith(('.html', '.js', '.css')):
            continue
        p = os.path.join(root, name)
        s = open(p, encoding='utf-8').read()
        o = s
        for a, b in REPL:
            s = s.replace(a, b)
        if s != o:
            open(p, 'w', encoding='utf-8', newline='\n').write(s)

# LE 전용 이미지 덮어쓰기 (로고 2종 + 파비콘 4종 + favicon.svg + og.jpg)
img = os.path.join(DST, 'assets', 'img')
for name in sorted(os.listdir(BRAND)):
    shutil.copy2(os.path.join(BRAND, name), os.path.join(img, name))
# SP 로고 파일은 LE 사이트에 필요 없다
for name in ('logo-sp.png', 'logo-sp-white.png'):
    p = os.path.join(img, name)
    if os.path.exists(p):
        os.remove(p)

# 푸터 대형 워터마크: "LUX ELECTRA" 가 "SP MOBILITY" 보다 7.5% 넓다.
# 폭에 맞춰 줄어드는 식은 SP 쪽에 있고, 여기서는 나눗수·상한만 LE 글자폭으로 바꾼다.
css = os.path.join(DST, 'assets', 'site.css')
s = open(css, encoding='utf-8').read()
for a, b in (('font-size:min(calc((100vw - 80px)/6.1),223px)', 'font-size:min(calc((100vw - 80px)/6.55),204px)'),
             ('font-size:min(96px,calc((100vw - 80px)/6.1))', 'font-size:min(89px,calc((100vw - 80px)/6.55))'),
             ('.foot .gmark{font-size:calc((100vw - 80px)/6.1)}', '.foot .gmark{font-size:calc((100vw - 80px)/6.55)}')):
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(css, 'w', encoding='utf-8', newline='\n').write(s)

print('LE 생성 완료:', DST)
