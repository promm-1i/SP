# SP 사이트를 LE(럭스일렉트라) 사이트로 복제한다. 구조·디자인은 동일, 회사 정보·로고·이메일만 교체.
#   python C:/web-project/SP/make_le.py
# 결과: C:/web-project/LE/  (매번 SP 기준으로 새로 생성한다 — LE 를 직접 고치지 말고 SP 를 고친 뒤 다시 돌린다)
import os, shutil, re, stat

SRC = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(SRC), 'LE')

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
    ('logo-sp-white.png', 'logo-le.png'),
    ('logo-sp.png', 'logo-le.png'),
]

if os.path.exists(DST):
    shutil.rmtree(DST, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns('make_le.py', 'make_variants.py', 'variants', '__pycache__', '.git', '.impeccable'))

for name in os.listdir(DST):
    if not name.endswith('.html'):
        continue
    p = os.path.join(DST, name)
    s = open(p, encoding='utf-8').read()
    for a, b in REPL:
        s = s.replace(a, b)
    open(p, 'w', encoding='utf-8').write(s)

# LE 엠블럼은 정사각형이라 헤더·푸터 로고 높이만 살짝 키운다
css = os.path.join(DST, 'assets', 'site.css')
s = open(css, encoding='utf-8').read()
s = s.replace('.hdr .logo img{height:44px;width:auto}', '.hdr .logo img{height:52px;width:auto}')
s = s.replace('.foot .flogo img{height:40px;width:auto}', '.foot .flogo img{height:56px;width:auto}')
open(css, 'w', encoding='utf-8').write(s)

print('LE 생성 완료:', DST)
