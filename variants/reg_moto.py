# moto-a~e 템플릿을 mintcl 사이트에 등록한다. 사진 설치 후 실행.
#   python C:/web-project/SP/variants/reg_moto.py
# 하는 일: 썸네일(기본형 1280×960) · 섹션 캡처 · og.jpg · samples.ts 10건 · designCode 프리픽스 · 업종 라벨 ·
#          헤더 내비 · 시작하기 섹션 · TEMPLATE_SECTIONS · sitemap 재생성. 이미 등록돼 있으면 그 단계는 건너뛴다.
import os, re, io, subprocess, sys, asyncio
from PIL import Image
from playwright.async_api import async_playwright

ROOT = r'C:\web-project\mintcl-netlify-spa'
T = os.path.join(ROOT, 'public', 'templates')
TH = os.path.join(ROOT, 'public', 'thumbs')
IND, PFX = 'moto', 'MOT'
LABEL = '전기 이륜차 · 바이크'
LETTERS = 'abcde'
DESIGNS = {
    'a': ('스플릿 라이트', '밝은 배경에 제품 누끼를 크게 세운 스플릿 히어로, 알약 버튼과 둥근 카드, 지그재그 제품 배치로 전기 스쿠터 판매 · 정비 매장의 상담 문의를 만드는 5페이지 템플릿입니다.',
          ['제품 누끼 스플릿 히어로', '제품 · 서비스 지그재그', '상품형 제품 상세 페이지', 'A/S 절차 · 협력점 지도']),
    'b': ('에디토리얼 다크', '전체 다크 네이비에 풀블리드 히어로와 섹션 번호, 하이라인 구분으로 프리미엄 브랜드 무드를 만드는 전기 스쿠터 판매 · 정비 매장 5페이지 템플릿입니다.',
          ['풀블리드 다크 히어로', '섹션 번호 · 하이라인 구성', '스티키 제품 스택', '다크 협력점 지도']),
    'c': ('벤토 그리드', '연회색 바탕에 흰 카드 벤토 그리드 히어로와 떠 있는 알약 헤더, 카드형 섹션으로 정보를 정리하는 전기 스쿠터 판매 · 정비 매장 5페이지 템플릿입니다.',
          ['벤토 그리드 히어로', '플로팅 알약 헤더', '카드형 제품 · 서비스', '카드형 A/S · 협력점']),
    'd': ('쇼룸', '블랙 쇼룸 무드에 정면 누끼 대형 히어로와 좌우 스펙 열, 풀와이드 이미지 패널과 괘선 격자로 제품을 크게 보여주는 전기 스쿠터 판매 · 정비 매장 5페이지 템플릿입니다.',
          ['정면 누끼 쇼룸 히어로', '풀와이드 제품 패널', '괘선 격자 특징 소개', '세로 카드 이용 사례']),
    'e': ('매거진', '크림 바탕 매거진 레이아웃, 좌측 고정 제목과 우측 스크롤 콘텐츠 2단, 섹션 인덱스와 얇은 괘선으로 읽는 흐름을 만드는 전기 스쿠터 판매 · 정비 매장 5페이지 템플릿입니다.',
          ['좌측 고정 제목 2단 구성', '섹션 인덱스 · 괘선', '스펙 표 히어로', '와이드 제품 목록']),
}
IDEAL = '전기 스쿠터 · 이륜차 판매점, 정비 · 배터리 케어 매장, 리스 렌탈 업체'


def rd(p): return open(p, encoding='utf-8').read()
def wr(p, s): open(p, 'w', encoding='utf-8').write(s)


# ---------- 1. 캡처 ----------
async def capture():
    os.makedirs(os.path.join(TH, 'sections'), exist_ok=True)
    sections = {}
    async with async_playwright() as p:
        b = await p.chromium.launch(channel='chrome')
        for L in LETTERS:
            # 썸네일: 기본형 1280×960
            ctx = await b.new_context(viewport={'width': 1280, 'height': 960}, device_scale_factor=1)
            pg = await ctx.new_page()
            await pg.goto('file:///' + os.path.join(T, f'{IND}-{L}-basic', 'index.html').replace(os.sep, '/'))
            await pg.wait_for_timeout(1200)
            png = await pg.screenshot()
            Image.open(io.BytesIO(png)).convert('RGB').save(os.path.join(TH, f'{IND}-{L}.jpg'), quality=82)
            await ctx.close()
            # 섹션 캡처 + og: 랜딩형 1440
            ctx = await b.new_context(viewport={'width': 1440, 'height': 900}, device_scale_factor=1)
            pg = await ctx.new_page()
            await pg.goto('file:///' + os.path.join(T, f'{IND}-{L}', 'index.html').replace(os.sep, '/'))
            await pg.wait_for_timeout(800)
            await pg.add_style_tag(content='.rv{opacity:1!important;transform:none!important;transition:none!important}')
            await pg.wait_for_timeout(300)
            if L == 'a':
                og = await pg.screenshot(clip={'x': 0, 'y': 0, 'width': 1440, 'height': 756})
                Image.open(io.BytesIO(og)).convert('RGB').resize((1200, 630), Image.LANCZOS).save(os.path.join(T, f'{IND}-a', 'og.jpg'), quality=85)
            secs = await pg.query_selector_all('section')
            shots = []
            for el in secs:
                h2 = await el.query_selector('h2')
                if not h2 or len(shots) >= 5:
                    continue
                title = re.sub(r'\s+', ' ', (await h2.inner_text()).replace('\n', ' ')).strip()
                if not title or len(title) > 40:
                    continue
                await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(200)
                png = await el.screenshot()
                im = Image.open(io.BytesIO(png)).convert('RGB')
                if im.width > 1280:
                    im = im.resize((1280, int(im.height * 1280 / im.width)), Image.LANCZOS)
                n = len(shots) + 1
                im.save(os.path.join(TH, 'sections', f'{IND}-{L}-{n}.jpg'), quality=80)
                shots.append((f'/thumbs/sections/{IND}-{L}-{n}.jpg', title))
            sections[f'{IND}-{L}'] = shots
            await ctx.close()
        await b.close()
    return sections


# ---------- 2. 코드 등록 ----------
def sample_entries():
    out = []
    for i, L in enumerate(LETTERS, 1):
        name, purpose, feats = DESIGNS[L]
        U = L.upper(); f = ', '.join(f'"{x}"' for x in feats)
        out.append(f'''  {{
    slug: "{IND}-{L}-template",
    industry: "{LABEL} 홈페이지",
    title: "{LABEL} 홈페이지 (랜딩형 템플릿 · 디자인 {U})",
    type: ["landing-template", "small-business"],
    tag: "랜딩형 템플릿 · {LABEL}",
    purpose:
      "{purpose}",
    features: [{f}],
    idealFor: "{IDEAL}",
    image: "/thumbs/{IND}-{L}.jpg",
    liveUrl: "/templates/{IND}-{L}/",
    industryKey: "{IND}",
    designCode: "{PFX}L-100{i}",
  }},
  {{
    slug: "{IND}-{L}-basic-template",
    industry: "{LABEL} 홈페이지",
    title: "{LABEL} 홈페이지 (기본형 템플릿 · 디자인 {U})",
    type: ["basic-template", "small-business"],
    tag: "기본형 템플릿 · {LABEL}",
    purpose:
      "{purpose} 스크롤 등장 애니메이션을 뺀 기본형입니다.",
    features: [{f}],
    idealFor: "{IDEAL}",
    image: "/thumbs/{IND}-{L}.jpg",
    liveUrl: "/templates/{IND}-{L}-basic/",
    industryKey: "{IND}",
    designCode: "{PFX}B-100{i}",
  }},
''')
    return ''.join(out)


def register(sections):
    # samples.ts
    p = os.path.join(ROOT, 'src', 'lib', 'samples.ts'); s = rd(p)
    if f'slug: "{IND}-a-template"' not in s:
        s = s.replace('export const SAMPLES: Sample[] = [\n', 'export const SAMPLES: Sample[] = [\n' + sample_entries(), 1)
    if f'  {IND}: "' not in s:
        s = s.replace('  travel: "여행·트레킹",\n', f'  travel: "여행·트레킹",\n  {IND}: "{LABEL.replace(" · ", "·")}",\n', 1)
    wr(p, s)
    # designCode.ts
    p = os.path.join(ROOT, 'src', 'lib', 'designCode.ts'); s = rd(p)
    if f'  {IND}: "{PFX}"' not in s:
        s = s.replace('  travel: "TRV",\n', f'  travel: "TRV",\n  {IND}: "{PFX}",\n', 1)
    wr(p, s)
    # navData.ts
    p = os.path.join(ROOT, 'src', 'components', 'site', 'navData.ts'); s = rd(p)
    if f'industry={IND}' not in s:
        s = s.replace('Mountain, type LucideIcon } from "lucide-react";', 'Mountain, Bike, type LucideIcon } from "lucide-react";', 1)
        s = s.replace('    href: "/templates?industry=travel",\n  },\n', f'    href: "/templates?industry=travel",\n  }},\n  {{\n    icon: Bike,\n    title: "{LABEL} 맞춤형",\n    desc: "제품 상세 · 구매 상담 · 협력점 지도",\n    href: "/templates?industry={IND}",\n  }},\n', 1)
    wr(p, s)
    # StartOptionsSection.tsx
    p = os.path.join(ROOT, 'src', 'components', 'sections', 'StartOptionsSection.tsx'); s = rd(p)
    if f'key: "{IND}"' not in s:
        s = s.replace('  Mountain,\n  type LucideIcon,\n', '  Mountain,\n  Bike,\n  type LucideIcon,\n', 1)
        line = (f'  {{ key: "{IND}", name: "{LABEL}", icon: Bike, img: "/thumbs/{IND}-a.jpg", href: "/templates?industry={IND}", title: "{LABEL} 홈페이지", '
                f'note: "제품 상세와 구매 · 리스 상담, A/S 절차와 협력점 지도로 문의를 만드는 구성입니다.", points: ["제품 상세 · 사양", "구매 · 리스 상담", "A/S 절차", "협력점 지도"] }},\n')
        m = re.search(r'  \{ key: "travel",[^\n]*\n', s)
        s = s[:m.end()] + line + s[m.end():]
    wr(p, s)
    # templateSections.ts
    p = os.path.join(ROOT, 'src', 'lib', 'templateSections.ts'); s = rd(p)
    for key, shots in sections.items():
        block = f'  "{key}": [\n' + ''.join(f'    {{ img: "{img}", title: "{t}" }},\n' for img, t in shots) + '  ],\n'
        if f'  "{key}": [' in s:
            s = re.sub(r'  "%s": \[\n(?:.*?\n)*?  \],\n' % re.escape(key), block, s, count=1)
        else:
            s = s[:s.rstrip().rfind('};')] + block + '};\n'
    wr(p, s)


if __name__ == '__main__':
    print('캡처 중…')
    sections = asyncio.run(capture())
    for k, v in sections.items():
        print(' ', k, len(v), '컷')
    register(sections)
    print('코드 등록 완료')
    subprocess.run(['node', 'scripts/generate-sitemap.mjs'], cwd=ROOT)
    r = subprocess.run(['npx', 'tsc', '--noEmit', '-p', 'tsconfig.app.json'], cwd=ROOT, shell=True, capture_output=True, text=True)
    print('tsc:', 'OK' if r.returncode == 0 else r.stdout[-2000:] + r.stderr[-2000:])
