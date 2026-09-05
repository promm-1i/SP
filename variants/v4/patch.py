# v4 서브페이지 패치: 다크 헤더 (메인은 히어로 위에 투명 헤더)
def patch(name, s):
    s = s.replace('<meta name="theme-color" content="#01101C">', '<meta name="theme-color" content="#0A0C10">')
    if name == 'index.html':
        s = s.replace('<header class="hdr">', '<header class="hdr dark home">')
    else:
        s = s.replace('<header class="hdr">', '<header class="hdr dark">')
    return s
