# SP 사이트를 기준으로 LE(럭스일렉트라) 디자인 시안 5종을 생성한다.
#   python C:/web-project/SP/make_variants.py          # v1~v5 전부
#   python C:/web-project/SP/make_variants.py 2 4      # 일부만
# 결과: C:/web-project/LE-v1 ~ LE-v5  (매번 새로 생성 — 시안 폴더를 직접 고치지 말고 variants/vN 을 고친 뒤 다시 돌린다)
#
# variants/vN/
#   theme.css   site.css 뒤에 링크되는 오버라이드 (토큰·헤더·섹션 배치)
#   home.html   메인 페이지 본문(히어로~CTA). LE index.html 의 <!-- HERO --> ~ <footer 사이에 끼워 넣는다 (SP 문구로 작성해도 LE 치환됨)
#   patch.py    서브페이지 HTML 치환 함수 patch(name, html) -> html  (선택)
import os, sys, shutil, importlib.util, subprocess, stat

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
LE = os.path.join(ROOT, 'LE')

# make_le.py 의 치환표 재사용
spec = importlib.util.spec_from_file_location('make_le', os.path.join(SRC, 'make_le.py'))
subprocess.run([sys.executable, os.path.join(SRC, 'make_le.py')], check=True, env=dict(os.environ, PYTHONIOENCODING='utf-8'))
REPL = []
for line in open(os.path.join(SRC, 'make_le.py'), encoding='utf-8').read().split('REPL = [')[1].split(']')[0].splitlines():
    line = line.strip().rstrip(',')
    if line.startswith('('):
        a, b = eval(line)
        REPL.append((a, b))

def le(s):
    for a, b in REPL:
        s = s.replace(a, b)
    return s

want = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5]
for n in want:
    vdir = os.path.join(SRC, 'variants', f'v{n}')
    if not os.path.isfile(os.path.join(vdir, 'theme.css')):
        print(f'v{n}: theme.css 없음, 건너뜀'); continue
    dst = os.path.join(ROOT, f'LE-v{n}')
    if os.path.exists(dst):
        shutil.rmtree(dst, onerror=lambda f, p, e: (os.chmod(p, stat.S_IWRITE), f(p)))
    shutil.copytree(LE, dst, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    shutil.copy(os.path.join(vdir, 'theme.css'), os.path.join(dst, 'assets', 'theme.css'))

    patch = None
    pp = os.path.join(vdir, 'patch.py')
    if os.path.isfile(pp):
        sp = importlib.util.spec_from_file_location(f'patch_v{n}', pp); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); patch = m.patch

    home = os.path.join(vdir, 'home.html')
    for name in os.listdir(dst):
        if not name.endswith('.html'):
            continue
        p = os.path.join(dst, name)
        s = open(p, encoding='utf-8').read()
        if name == 'index.html' and os.path.isfile(home):
            body = le(open(home, encoding='utf-8').read())
            a = s.index('<!-- HERO -->'); b = s.index('<footer class="foot">')
            s = s[:a] + body.strip() + chr(10)*2 + s[b:]
        s = s.replace('<link rel="stylesheet" href="./assets/site.css">', '<link rel="stylesheet" href="./assets/site.css">\n<link rel="stylesheet" href="./assets/theme.css">')
        s = s.replace('<meta name="theme-color" content="#01101C">', '<meta name="theme-color" content="#01101C"><meta name="le-variant" content="v%d">' % n)
        if patch:
            s = patch(name, s)
        open(p, 'w', encoding='utf-8').write(s)
    print(f'v{n} → {dst}')
