# v1 서브페이지 패치
def patch(name, s):
    if name == 'about.html':
        s = s.replace('<p class="eyebrow rv" style="color:#fff">About Us</p>', '<p class="eyebrow rv">About Us</p>')
        # 소개 히어로: 텍스트를 div 로 감싸고 우측에 제품 누끼
        s = s.replace('<div class="in">\n    <div class="crumb"><a href="./index.html">Home</a><span>/</span><span>About</span></div>',
                      '<div class="in">\n  <div>\n    <div class="crumb"><a href="./index.html">Home</a><span>/</span><span>About</span></div>', 1)
        s = s.replace('창출합니다.</p>\n  </div>\n</section>',
                      '창출합니다.</p>\n  </div>\n  <div class="art rv" style="--d:.15s"><img src="./assets/img/product-quarter.webp" alt="캄페온"></div>\n  </div>\n</section>', 1)
    return s
