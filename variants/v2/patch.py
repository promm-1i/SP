# v2 서브페이지 패치: 다크 헤더, 회사소개 카드 문구색 정리
def patch(name, s):
    s = s.replace('<header class="hdr">', '<header class="hdr dark">')
    s = s.replace('<meta name="theme-color" content="#01101C">', '<meta name="theme-color" content="#050B12">')
    if name == 'about.html':
        s = s.replace('<p class="eyebrow rv" style="color:#fff">About Us</p>', '<p class="eyebrow rv">About Us</p>')
    return s
