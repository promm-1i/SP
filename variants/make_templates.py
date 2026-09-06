# SP 원본 + variants/v1~v5 를 중립 브랜드(볼트라이드 · 에어로 S1)로 바꿔
# mintcl 템플릿 `moto-a` ~ `moto-e` (랜딩형) + `moto-a-basic` ~ `moto-e-basic` (기본형) 을 생성한다.
#   python C:/web-project/SP/variants/make_templates.py            # 전부
#   python C:/web-project/SP/variants/make_templates.py 1 3        # v1→moto-a, v3→moto-c 만
# 사진은 moto-a/assets/img/ 한 곳에만 두고 나머지 9개 폴더는 ../moto-a/assets/img/ 상대경로로 참조한다.
# 사진이 아직 없으면 슬롯 크기의 플레이스홀더를 만들어 넣는다(이미 파일이 있으면 건드리지 않음).
import os, re, sys, shutil, stat, importlib.util

SP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAR = os.path.join(SP, 'variants')
OUT = r'C:\web-project\mintcl-netlify-spa\public\templates'
IND = 'moto'
LETTERS = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e'}
CONCEPT = {1: '스플릿 라이트', 2: '에디토리얼 다크', 3: '벤토 그리드', 4: '쇼룸', 5: '매거진'}

# ---------- 사진 슬롯 (새 파일명, 크기, 원본 파일명 매핑) ----------
SLOTS = {  # 새 파일 → (가로, 세로)
    'hero-side.jpg': (2880, 1800),
    'angle-front.jpg': (1200, 900), 'angle-frontR.jpg': (1200, 900), 'angle-side.jpg': (1200, 900),
    'angle-rear.jpg': (1200, 900), 'angle-rearL.jpg': (1200, 900), 'angle-left.jpg': (1200, 900),
    'angle-day-front.jpg': (1200, 900), 'angle-day-rear.jpg': (1200, 900),
    'detail-headlight.jpg': (1200, 900), 'detail-tail.jpg': (1200, 900), 'detail-motor.jpg': (1200, 900),
    'detail-brake.jpg': (1200, 900), 'detail-side.jpg': (1200, 900),
    'scene-showroom.jpg': (1600, 1000), 'scene-charging.jpg': (1600, 1000), 'scene-workshop.jpg': (1600, 1000),
    'scene-delivery.jpg': (1600, 1000), 'scene-rider-city.jpg': (1600, 1000), 'scene-town.jpg': (1600, 1000),
    'scene-support.jpg': (1600, 1000),
    'cut-quarter.png': (1224, 1118), 'cut-front.png': (850, 1195),
}
IMGMAP = {  # SP 원본 파일 → 새 파일
    'hero-bg.jpg': 'hero-side.jpg', 'big-01.jpg': 'hero-side.jpg',
    'work-01.jpg': 'angle-side.jpg', 'work-02.jpg': 'angle-left.jpg', 'work-03.jpg': 'angle-rearL.jpg',
    'card-01.jpg': 'detail-headlight.jpg', 'card-02.jpg': 'detail-side.jpg', 'card-03.jpg': 'detail-motor.jpg',
    'svc-01.jpg': 'scene-showroom.jpg', 'svc-02.jpg': 'scene-charging.jpg', 'svc-03.jpg': 'scene-workshop.jpg', 'svc-04.jpg': 'scene-delivery.jpg',
    'use-01.jpg': 'scene-rider-city.jpg', 'use-02.jpg': 'scene-delivery.jpg', 'use-03.jpg': 'scene-town.jpg', 'use-04.jpg': 'scene-support.jpg',
    'team-01.jpg': 'scene-showroom.jpg', 'team-02.jpg': 'scene-workshop.jpg', 'team-03.jpg': 'scene-support.jpg',
    'cta-bg.jpg': 'scene-rider-city.jpg', 'gal-03.jpg': 'angle-side.jpg',
    'product-quarter.webp': 'cut-quarter.png', 'hero-campeon.webp': 'cut-quarter.png', 'product-front.webp': 'cut-front.png',
    'logo-sp.png': 'logo.svg', 'logo-sp-white.png': 'logo-white.svg', 'logo-le.png': 'logo.svg',
}
GALLERY = [  # 제품 페이지 갤러리 (파일, 캡션)
    ('angle-front.jpg', '정면'), ('angle-frontR.jpg', '전측면'), ('angle-side.jpg', '측면'), ('angle-rear.jpg', '후면'),
    ('angle-rearL.jpg', '후측면'), ('angle-left.jpg', '좌측면'), ('angle-day-front.jpg', '주간 정면'), ('angle-day-rear.jpg', '주간 후면'),
    ('detail-headlight.jpg', '헤드라이트'), ('detail-tail.jpg', '테일램프'), ('detail-motor.jpg', '후륜 인휠 모터'), ('detail-brake.jpg', '디스크 브레이크'),
]

# ---------- 문구 중립화 (순서 중요: 긴 것 → 짧은 것) ----------
REPL = [
    # 메타 · 타이틀 (서브페이지)
    ('친환경 E-Mobility 기술 개발로 녹색 가치를 창조하는 Eco Value 기업, 주식회사 에스피모빌리티. 전기 이륜차 캄페온, OBC 충전, E.V Eco System.', '전기 스쿠터 판매와 정비, 배터리 케어를 한 곳에서 하는 라이더 전문 매장 볼트라이드. 회사 소개, 서비스 안내, 협력 파트너 문의.'),
    ('대한민국 배달 시장에 최적화된 전기 이륜차 캄페온. 7kW 모터, CATL 77.7V 160Ah 배터리, 환경부 인증 주행거리 198.2km, OBC 120분 충전. 제품 사양과 가격 안내.', '도심 배달과 출퇴근에 맞춘 전기 스쿠터 에어로 S1. 5kW 모터, 72V 50Ah 배터리, 1회 충전 최대 120km, 220V 4시간 충전. 제품 사양과 가격 안내.'),
    ('<title>캄페온 CAMPEON | 제품 안내 · 에스피모빌리티</title>', '<title>에어로 S1 | 제품 안내 · 볼트라이드</title>'),
    ('환경부 인증 기준 상온 198.2km, 저온 195.1km입니다.', '상온 기준 최대 120km, 저온 100km입니다.'),
    ('차량에 탑재된 On Board Charger가 외부 AC 전원을 DC로 바꿔 배터리를 직접 충전합니다.', '차량에 내장된 충전기로 가정용 콘센트에서 바로 충전합니다.'),
    ('소형B 유상운송종합보험 · ', '이륜차 보험 상담 · '),
    ('<span>198.2km</span>', '<span>120km</span>'), ('<span>107km/h</span>', '<span>80km/h</span>'), ('<span>7kW</span>', '<span>5kW</span>'),
    ('상온 198.2km / 저온 195.1km', '상온 120km / 저온 100km'), ('E.V ECO SYSTEM', 'OUR SERVICES'),
    ('alt="OBC"', 'alt="가정용 220V 충전"'), ('placeholder="아산시"', 'placeholder="성동구"'),
    # 메뉴 · 섹션 이름
    ('#eco">E.V Eco System</a>', '#eco">서비스 안내</a>'),
    # 회사 · 사업자
    ('주식회사 에스피모빌리티', '주식회사 볼트라이드'), ('㈜에스피모빌리티', '볼트라이드'), ('에스피모빌리티', '볼트라이드'),
    ('SP MOBILITY', 'VOLTRIDE'), ('SP Mobility', 'Voltride'),
    ('info.spmobility@gmail.com', 'hello@voltride.kr'), ('1661-5958', '1588-0000'),
    ('대표 안성섭', '대표 이준혁'), ('<dd>안성섭</dd>', '<dd>이준혁</dd>'), ('716-86-03649', '123-45-67890'), ('2024년 8월', '2021년 3월'),
    ('충청남도 아산시 둔포면 봉신로230번길 42, 2층', '서울특별시 성동구 성수이로 00, 1층'), ('충남 아산시 둔포면 봉신로230번길 42, 2층', '서울 성동구 성수이로 00, 1층'),
    ('전기오토바이 · 전기충전기 · 전기배터리 · 소프트웨어 개발', '전기 이륜차 판매 · 정비 · 배터리 케어 · 리스 렌탈'),
    # 회사소개 문단
    ('친환경 E-Mobility 기술로<br><span class="b">녹색 가치</span>를 만듭니다.', '전기 스쿠터,<br><span class="b">타는 것부터 관리까지.</span>'),
    ('볼트라이드는 친환경 E-Mobility 기술 개발을 통해 녹색 가치를 창조하는 Eco Value 기업입니다. 사람과 환경, 도시가 공생할 수 있는 지속가능한 기술을 개발하여 새로운 가치를 창출합니다.',
     '볼트라이드는 전기 스쿠터를 판매하고 정비하는 라이더 전문 매장입니다. 구매 상담부터 보조금 신청, 정기 점검과 배터리 케어까지 한 곳에서 처리합니다.'),
    ('Eco Value 기업,<br><span class="b">볼트라이드.</span>', '라이더 전문 매장,<br><span class="b">볼트라이드.</span>'),
    ('OBC 충전으로 120분 급속 충전이 가능하고, 1회 충전으로 200km 이상 달릴 수 있는 전기 이륜차 캄페온을 만듭니다.',
     '가정용 콘센트로 충전하고 1회 충전으로 120km를 달리는 전기 스쿠터 에어로 S1을 판매하고 정비합니다.'),
    ('대한민국 배달 시장을 기준으로 설계했습니다. 배터리 교환소에 의존하지 않는 직접충전 방식, 한국 지형에 맞춘 긴 주행거리와 등판 성능, 정비 편의성을 높인 설계로 라이더의 하루를 바꿉니다.',
     '배달 라이더와 출퇴근 이용자를 기준으로 골랐습니다. 배터리 교환소에 의존하지 않는 직접충전 방식, 도심에 맞는 주행거리와 등판 성능, 정비가 쉬운 구조로 라이더의 하루를 바꿉니다.'),
    ('전기 이륜차 제조에서 출발해 충전 스테이션, 배터리, 주행 데이터 솔루션까지 이어지는 E.V Eco System을 구축해 갑니다.',
     '판매에서 출발해 정비, 배터리 케어, 리스 렌탈까지 한 매장에서 이어지는 서비스를 만들어 갑니다.'),
    ('차량, 충전, 인프라를<br><span class="b">직접 만듭니다.</span>', '판매, 충전, 정비를<br><span class="b">한 곳에서.</span>'),
    ('제조사와 소비자가 직접 계약합니다. 중간 단계를 거치지 않아 품질을 보증하고 가격 부담을 낮춥니다.', '구매부터 정비, 배터리 케어까지 한 매장에서 이어집니다. 담당자가 처음부터 끝까지 안내합니다.'),
    ('7kW 모터, CATL 77.7V 160Ah 배터리. 배달 라이더의 니즈에 맞춘 소형 스펙의 경형 전기 이륜차.', '5kW 모터, 72V 50Ah 리튬이온 배터리. 도심 배달과 출퇴근에 맞춘 전기 스쿠터.'),
    ('외부 AC 전원을 DC로 변환해 배터리를 직접 충전하는 핵심 부품. 2시간 이내 충전, 교환소 미설치 지역 운행.', '차량에 내장된 충전기로 가정용 콘센트에서 바로 충전합니다. 약 4시간 완충, 배터리 교환소가 없는 지역에서도 운행합니다.'),
    ('전기차 완속 충전기와 같은 형태의 검증된 시스템. 낮은 설치비로 전국 단위 설치가 가능합니다.', '정기 점검과 배터리 진단, 소모품 교체를 매장에서 처리합니다. 예약하면 대기 없이 정비합니다.'),
    ('지속 가능한<br><span class="b">Eco Value Chain.</span>', '판매에서 정비까지,<br><span class="b">네 가지 서비스.</span>'),
    ('전기 이륜차에서 시작해 충전, 배터리 재생, 주행 데이터까지. 네 가지 사업이 하나의 순환 구조를 이룹니다.', '판매, 정비, 배터리 케어, 리스 렌탈. 네 가지 서비스가 한 매장에서 이어집니다.'),
    ('전기 이륜차 판매 및 서비스 협력 사업에 관심 있는 기업과 사업자를 모집합니다.', '전기 스쿠터 판매 · 정비 협력점에 관심 있는 기업과 사업자를 모집합니다.'),
    # 메인
    ('가정용 220V로 120분이면 완충. 배터리 교환소가 없어도 전국 어디서든 달리는 전기 이륜차, 캄페온.', '가정용 220V로 4시간이면 완충. 배터리 교환소가 없어도 어디서든 달리는 전기 스쿠터, 에어로 S1.'),
    ('가정용 220V로 120분 완충, 환경부 인증 주행거리 198.2km. 배터리 교환소 없이 전국 어디서나 달리는 전기 이륜차 캄페온. 신차 구매와 렌트·리스 상담.',
     '가정용 220V로 4시간 완충, 1회 충전 최대 120km. 배터리 교환소 없이 어디서나 달리는 전기 스쿠터 에어로 S1. 신차 구매와 렌트·리스, 정비까지.'),
    ('OBC 직접충전 전기 이륜차 캄페온. 충전은 어디서나, 주행은 더 멀리.', '가정용 콘센트로 충전하는 전기 스쿠터 에어로 S1. 충전은 어디서나, 주행은 더 멀리.'),
    ('15만 명 이상의 라이더가 소속된 배달대행 현장의 요구를 그대로 설계에 반영했습니다. 충전, 주행거리, 유지비. 세 가지를 한 번에 해결합니다.',
     '매장에서 만난 배달 라이더와 출퇴근 이용자의 요구를 기준으로 골랐습니다. 충전, 주행거리, 유지비. 세 가지를 한 번에 해결합니다.'),
    ('가정용 220V나 외부 AC 전원에 바로 연결해 충전합니다. 2시간 이내 완충, 배터리 교환소가 없는 지역에서도 운행할 수 있습니다.',
     '가정용 220V 콘센트에 바로 연결해 충전합니다. 약 4시간이면 완충, 배터리 교환소가 없는 지역에서도 운행할 수 있습니다.'),
    ('환경부 인증 상온 198.2km, 저온 195.1km. 하루 배달 동선을 한 번의 충전으로 소화합니다.', '1회 충전 최대 120km, 저온 100km. 하루 배달 동선을 한 번의 충전으로 소화합니다.'),
    ('월 충전비 약 30,000원 기준. 내연기관 대비 연료비를 크게 줄이고, 타이어 교체도 10분이면 끝납니다.', '월 충전비 약 15,000원 기준. 내연기관 대비 연료비를 크게 줄이고, 소모품 교체도 매장에서 바로 끝납니다.'),
    ('캄페온에서 충전 인프라까지,<br><span class="b">한 곳에서.</span>', '판매에서 정비까지,<br><span class="b">한 곳에서.</span>'),
    ('차량, 충전 시스템, 스테이션, 리스·렌탈까지 제조사가 직접 제공합니다.', '차량 판매, 가정용 충전, 정비와 배터리 케어, 리스·렌탈까지 한 매장에서 제공합니다.'),
    ('7kW 모터, CATL 77.7V 160Ah 배터리, 2인 승차. 대한민국 배달 시장에 맞춰 개발한 전기 이륜차.', '5kW 모터, 72V 50Ah 배터리, 2인 승차. 도심 배달과 출퇴근에 맞춘 전기 스쿠터.'),
    ('차량에 탑재된 On Board Charger가 외부 AC 전원을 DC로 바꿔 배터리를 직접 충전합니다. 교환소에 종속되지 않는 충전 방식입니다.', '차량에 내장된 충전기로 가정용 콘센트에서 바로 충전합니다. 배터리 교환소에 가지 않아도 됩니다.'),
    ('전기차 완속 충전기와 같은 형태의 검증된 충전 시스템. 낮은 설치비로 전국 어디든 설치할 수 있습니다.', '정기 점검과 배터리 진단, 소모품 교체까지 매장에서 바로 처리합니다. 예약하면 대기 없이 정비합니다.'),
    ('제조사와 직접 계약하는 리스·렌탈. 중간 유통 단계를 줄여 라이더의 월 부담을 낮춥니다.', '초기 비용 없이 월 이용료로 시작하는 리스·렌탈. 배달대행사와 법인은 대수별로 견적을 드립니다.'),
    ('OBC 직접충전 시스템', '가정용 220V 충전'), ('OBC 충전 시스템', '가정용 220V 충전'), ('전용 충전 스테이션', '정비 · 배터리 케어'),
    ('120분 완충', '4시간 완충'), ('전국 설치', '정비 예약'),
    ('한국 지형에 맞춘 7kW 모터. 언덕길과 골목길도 여유 있게 오릅니다.', '언덕이 많은 도심에 맞춘 5kW 모터. 언덕길과 골목길도 여유 있게 오릅니다.'),
    ('스마트키, 2ch ABS 기본. 소형B 유상운송종합보험으로 보험료 부담을 줄였습니다.', '스마트키, 2ch ABS 기본. 이륜차 보험 상담으로 보험료 부담도 줄입니다.'),
    ('월 충전비 약 3만 원', '월 충전비 약 1.5만 원'),
    ('7kW 모터, CATL 77.7V 160Ah 배터리, 환경부 인증 주행거리 198.2km.', '5kW 모터, 72V 50Ah 배터리, 1회 충전 최대 120km.'),
    ('전기 이륜차에서 시작하는<br><span class="b">Eco Value Chain.</span>', '구매 후에도<br><span class="b">매장이 함께합니다.</span>'),
    ('차량 제조에서 충전, 데이터, 배터리 재생까지 이어지는 순환 구조를 만들어 갑니다.', '구매 상담부터 정비, 배터리 케어, 보조금 신청까지 담당자가 이어서 안내합니다.'),
    ('<small>E-Mobility</small><h3>캄페온 전기 이륜차 제조</h3><p>리스 · 렌탈 뱅크와 신규 E.V 시장 개척.</p>', '<small>판매</small><h3>전기 스쿠터 판매</h3><p>신차 · 인증 중고 · 리스 렌탈 상담.</p>'),
    ('<small>Charging · OBC · Battery</small><h3>충전 인프라와 배터리</h3><p>충전 스테이션 · OBC 표준 · LMFP 배터리 · ESS</p>', '<small>정비 · 배터리</small><h3>정비 · 배터리 케어</h3><p>정기 점검 · 배터리 진단 · 소모품 교체</p>'),
    ('<small>Data · Solution</small><h3>주행 데이터 솔루션</h3><p>GPS 관제 · 안전운전 평가 · 탄소배출권 · 전용 보험</p>', '<small>라이더 지원</small><h3>라이더 지원</h3><p>보조금 신청 대행 · 보험 안내 · 안전 교육</p>'),
    ('전기 이륜차 보조금 안내는 준비 중입니다. 상담 시 지역별 지원 여부를 함께 안내해 드립니다.', '지자체별 전기 이륜차 보조금 신청을 매장에서 대행합니다. 상담 시 지역별 지원 여부를 함께 안내해 드립니다.'),
    ('가정용 220V 콘센트나 외부 AC 전원에 연결하면 차량 내 OBC가 직접 충전합니다. 완충까지 약 120분이 걸립니다.', '가정용 220V 콘센트에 연결하면 차량에 내장된 충전기가 직접 충전합니다. 완충까지 약 4시간이 걸립니다.'),
    ('친환경 E-Mobility 기술로 녹색 가치를 만드는 Eco Value 기업. 전기 이륜차 캄페온과 OBC 충전 솔루션.', '전기 스쿠터 판매와 정비, 배터리 케어를 한 곳에서. 라이더 전문 매장 볼트라이드.'),
    ('Electric Scooter · OBC Direct Charging', 'Electric Scooter · Plug-in Charging'),
    ('Campeon · Electric Scooter · OBC Direct Charging', 'Aero S1 · Electric Scooter · Plug-in Charging'),
    ('Issue 01 — Campeon', 'Issue 01 — Aero S1'),
    ('OBC 직접충전 전기 이륜차', '가정용 콘센트로 충전하는 전기 스쿠터'),
    ('<b>7kW</b><span>후륜 인휠 모터</span>', '<b>5kW</b><span>후륜 인휠 모터</span>'),
    ('<b>CATL 77.7V 160Ah</b><span>배터리 · 2인 승차</span>', '<b>72V 50Ah</b><span>리튬이온 · 2인 승차</span>'),
    ('<dd>7kW · CATL 77.7V 160Ah</dd>', '<dd>5kW · 72V 50Ah</dd>'),
    ('<dd>198.2 km</dd>', '<dd>120 km</dd>'), ('<dd>120 분</dd>', '<dd>4 시간</dd>'), ('<dd>107 km/h</dd>', '<dd>80 km/h</dd>'),
    ('주행거리 (환경부 인증)', '1회 충전 주행거리'),
    # 제품 페이지
    ('대한민국 배달 시장에 최적화된 OBC 직접충전 전기 이륜차. 소형B 유상운송종합보험 · 스마트키 · 2ch ABS 풀옵션.', '도심 배달과 출퇴근에 맞춘 가정용 충전 전기 스쿠터. 스마트키 · 2ch ABS 풀옵션, 보험과 보조금 상담까지.'),
    ('<span>환경부 인증 198.2km</span><span>최고속도 107km/h</span><span>OBC 120분 충전</span><span>2인 승차</span><span>7kW · CATL 77.7V 160Ah</span>',
     '<span>1회 충전 120km</span><span>최고속도 80km/h</span><span>220V 4시간 충전</span><span>2인 승차</span><span>5kW · 72V 50Ah</span>'),
    ('사전 상담 접수 중', '시승 · 상담 접수 중'),
    ('가격과 보조금은 출시 · 지자체 공고에 따라 확정됩니다. 지역별 전기 이륜차 보조금은 환경부 무공해차 통합누리집 기준으로 상담 시 안내해 드립니다.', '가격과 보조금은 지자체 공고에 따라 달라집니다. 지역별 전기 이륜차 보조금은 상담 시 안내해 드립니다.'),
    ('<b>198.2<small>km</small></b><h3>주행 가능 거리</h3><p>환경부 인증 상온 198.2km, 저온 195.1km.</p>', '<b>120<small>km</small></b><h3>주행 가능 거리</h3><p>상온 최대 120km, 저온 100km.</p>'),
    ('<b>120<small>분</small></b><h3>OBC 충전</h3><p>가정용 220V 또는 외부 AC 전원으로 직접 충전.</p>', '<b>4<small>시간</small></b><h3>220V 충전</h3><p>가정용 콘센트에서 직접 충전.</p>'),
    ('<b>30,000<small>원</small></b>', '<b>15,000<small>원</small></b>'),
    ('차량에 탑재된 OBC(On Board Charger)가 외부 AC 전원을 DC로 변환해 배터리를 직접 충전합니다. 배터리 교환소가 없는 지역에서도 운행할 수 있습니다.', '차량에 내장된 충전기가 가정용 콘센트 전원으로 배터리를 직접 충전합니다. 배터리 교환소가 없는 지역에서도 운행할 수 있습니다.'),
    ('<li><span>충전 전원</span><span>220V AC</span></li><li><span>완충 시간</span><span>약 120분</span></li><li><span>월 충전 비용</span><span>약 30,000원</span></li>', '<li><span>충전 전원</span><span>220V 가정용</span></li><li><span>완충 시간</span><span>약 4시간</span></li><li><span>월 충전 비용</span><span>약 15,000원</span></li>'),
    ('CATL 77.7V 160Ah 배터리와 7kW 모터. 환경부 인증 기준 상온 198.2km, 저온 195.1km를 달립니다. 한국 지형에 맞춘 강력한 등판 능력까지.', '72V 50Ah 배터리와 5kW 모터. 상온 기준 120km, 저온 100km를 달립니다. 언덕이 많은 도심에 맞춘 등판 능력까지.'),
    ('<li><span>주행거리 (환경부 인증)</span><span>198.2km</span></li><li><span>최고 속도</span><span>107km/h</span></li><li><span>모터</span><span>7kW</span></li>', '<li><span>1회 충전 주행거리</span><span>120km</span></li><li><span>최고 속도</span><span>80km/h</span></li><li><span>모터</span><span>5kW</span></li>'),
    ('10분이면 끝나는 타이어 교체, 소형B 유상운송종합보험 적용으로 낮아진 보험료. 스마트키와 2ch ABS 등 편의사양은 기본입니다.', '10분이면 끝나는 타이어 교체, 보험 상담까지 매장에서 함께. 스마트키와 2ch ABS 등 편의사양은 기본입니다.'),
    ('<li><span>보험 구분</span><span>소형B</span></li>', '<li><span>보험</span><span>매장 상담</span></li>'),
    ('환경부 인증 기준 수치입니다. 적재량 · 기온 · 주행 습관에 따라 달라질 수 있습니다.', '자체 측정 기준 수치입니다. 적재량 · 기온 · 주행 습관에 따라 달라질 수 있습니다.'),
    ('<div><dt>모델명</dt><dd>캄페온 (CAMPEON)</dd></div>', '<div><dt>모델명</dt><dd>에어로 S1 (AERO S1)</dd></div>'),
    ('<div><dt>모터</dt><dd>7kW</dd></div>', '<div><dt>모터</dt><dd>5kW 후륜 인휠</dd></div>'),
    ('<div><dt>배터리</dt><dd>77.7V 160Ah · CATL</dd></div>', '<div><dt>배터리</dt><dd>72V 50Ah 리튬이온</dd></div>'),
    ('<div><dt>주행거리 (환경부 인증)</dt><dd>상온 198.2km / 저온 195.1km</dd></div>', '<div><dt>1회 충전 주행거리</dt><dd>상온 120km / 저온 100km</dd></div>'),
    ('<div><dt>최고 속도</dt><dd>107km/h</dd></div>', '<div><dt>최고 속도</dt><dd>80km/h</dd></div>'),
    ('<div><dt>충전 방식</dt><dd>OBC 직접충전 · 220V</dd></div>', '<div><dt>충전 방식</dt><dd>가정용 220V 직접충전</dd></div>'),
    ('<div><dt>충전 시간</dt><dd>약 120분</dd></div>', '<div><dt>충전 시간</dt><dd>약 4시간</dd></div>'),
    ('<div><dt>공차 중량</dt><dd>200kg</dd></div>', '<div><dt>공차 중량</dt><dd>115kg</dd></div>'),
    ('<div><dt>보험 구분</dt><dd>소형B (100cc 이하 급)</dd></div>', '<div><dt>보험</dt><dd>이륜차 보험 · 매장 상담</dd></div>'),
    ('<div><dt>제동 · 안전</dt><dd>구동축전지 안전성 시험 기준 충족</dd></div>', '<div><dt>제동 · 안전</dt><dd>전 · 후륜 디스크 브레이크 · 2ch ABS</dd></div>'),
    ('가정용 220V 콘센트 또는 외부 AC 전원에 연결하면 차량 내 OBC가 직접 충전합니다.', '가정용 220V 콘센트에 연결하면 차량에 내장된 충전기가 직접 충전합니다.'),
    ('완충까지 약 120분. 별도 수전 공사가 필요 없습니다.', '완충까지 약 4시간. 별도 수전 공사가 필요 없습니다.'),
    ('전용 충전 스테이션 설치 지역에서는 스테이션 이용도 가능합니다.', '매장 방문 시 매장에서도 충전할 수 있습니다.'),
    ('보증 기간과 범위는 계약 시 안내해 드립니다.', '보증 기간과 범위는 구매 시 안내해 드립니다.'),
    # 잔여 수치 · 용어
    ('E.V Eco System', 'Our Services'),
    ('198.2<small>km</small>', '120<small>km</small>'), ('<b>120<small>분</small></b>', '<b>4<small>시간</small></b>'), ('107<small>km/h</small>', '80<small>km/h</small>'),
    ('환경부 인증 주행거리', '1회 충전 주행거리'), ('OBC 완충 시간', '220V 완충 시간'), ('OBC 직접충전', '콘센트 직접충전'), ('OBC Direct Charging', 'Plug-in Charging'),
    ('상황에 맞는 구매 방식으로 캄페온을 만나보세요.', '상황에 맞는 구매 방식으로 에어로 S1을 만나보세요.'),
    ('캄페온 CAMPEON<br>전기 이륜차', '에어로 S1<br>전기 스쿠터'), ('캄페온 CAMPEON', '에어로 S1'), ('CAMPEON 전기 이륜차', 'AERO S1 전기 스쿠터'),
    ('전기 이륜차 캄페온', '전기 스쿠터 에어로 S1'), ('캄페온 전기 이륜차', '에어로 S1 전기 스쿠터'),
    ('캄페온', '에어로 S1'), ('CAMPEON', 'AERO S1'), ('Campeon', 'Aero S1'),
    ('전기 이륜차', '전기 스쿠터'),
]
LEFTOVER = re.compile(r'캄페온|CAMPEON|Campeon|에스피|SP MOBILITY|SP Mobility|spmobility|OBC|198\.2|195\.1|CATL|77\.7|1661|봉신로|안성섭|716-86|환경부|Eco Value|E\.V |E-Mobility|소형B|On Board|15만|아산시|LMFP|탄소배출권')

DEALERS_JS = '''/* 협력점 데이터 — 여기에만 추가하면 고객지원 페이지의 목록과 지도에 함께 표시됩니다.
 *   region : 서울 | 인천 | 경기 | 강원 | 충청 | 전라 | 경상 | 제주   (지역 필터 버튼과 같은 값)
 *   type   : "hq" = 본점 · 직영 (빨간 핀)   |  "dealer" = 협력점 (파란 핀)
 *   lat/lng: 위도 · 경도. 네이버지도/구글지도에서 장소를 찍고 좌표를 복사해 넣으세요. */
/* 카카오맵을 쓰려면 developers.kakao.com 의 JavaScript 키를 넣으세요. 비워 두면 OpenStreetMap 지도로 표시됩니다. */
window.KAKAO_APP_KEY = "";

window.DEALERS = [
  { name: "볼트라이드 성수 본점", region: "서울", type: "hq", addr: "서울 성동구 성수이로 00, 1층", tel: "1588-0000", lat: 37.5445, lng: 127.0560 },
  { name: "볼트라이드 수원 정비센터", region: "경기", type: "dealer", addr: "경기 수원시 팔달구 매산로 00", tel: "031-000-0000", lat: 37.2660, lng: 127.0010 },
  { name: "부산 해운대 협력점", region: "경상", type: "dealer", addr: "부산 해운대구 해운대로 000", tel: "051-000-0000", lat: 35.1631, lng: 129.1636 },
  { name: "대전 유성 협력점", region: "충청", type: "dealer", addr: "대전 유성구 대학로 00", tel: "042-000-0000", lat: 36.3620, lng: 127.3560 }
];
'''

LOGO = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 250 56" width="250" height="56"><path d="M30 4 12 32h13l-3 20 20-28H29z" fill="#1470A8"/><text x="50" y="40" font-family="Arial Black,Arial,Helvetica,sans-serif" font-weight="900" font-size="30" letter-spacing="2" fill="{c}">VOLTRIDE</text></svg>'''
FAVICON = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="10" fill="#0B1B2B"/><path d="M36 10 18 36h12l-2 18 18-26H34z" fill="#1470A8"/></svg>'

ECARDS_OLD_START = '<div class="grid4">'
ECARDS_NEW = '''<div class="grid4">
    <div class="ecard rv"><span class="n">01</span><h3>판매</h3><ul><li>신차 · 인증 중고 판매</li><li>리스 · 렌탈 상담</li><li>시승 예약</li></ul></div>
    <div class="ecard rv" style="--d:.1s"><span class="n">02</span><h3>정비 · A/S</h3><ul><li>정기 점검 · 소모품 교체</li><li>배터리 진단</li><li>출장 · 픽업 정비</li></ul></div>
    <div class="ecard rv" style="--d:.2s"><span class="n">03</span><h3>충전 · 배터리</h3><ul><li>가정용 충전기 설치 안내</li><li>배터리 교체 · 재생</li><li>매장 충전</li></ul></div>
    <div class="ecard rv" style="--d:.3s"><span class="n">04</span><h3>라이더 지원</h3><ul><li>보조금 신청 대행</li><li>이륜차 보험 안내</li><li>안전 교육 · 관제 앱</li></ul></div>
  </div>'''

WM_CSS = '''
/* 템플릿: 워드마크 이미지 대신 텍스트 */
.wmtxt{display:inline-block;font-family:var(--mono);font-weight:600;letter-spacing:.2em;text-transform:uppercase;font-size:14px;line-height:1}
.buy .wm{height:auto;font-size:13px;color:var(--blue);margin-bottom:12px}
.hsplit .cue .wmtxt{font-size:12px}
.bento .bike .wm{filter:none;height:auto;font-size:13px;color:#fff}
.mhero .panel .wm{height:auto;font-size:13px;color:#fff}
'''
BASIC_CSS = '\n/* 기본형: 스크롤 등장 애니메이션 없이 처음부터 보이게 한다 */\n.rv{opacity:1!important;transform:none!important;filter:none!important;transition-property:none!important}\n'


def rmtree(p):
    if os.path.exists(p):
        shutil.rmtree(p, onerror=lambda f, x, e: (os.chmod(x, stat.S_IWRITE), f(x)))


def neutral(s):
    for a, b in REPL:
        s = s.replace(a, b)
    return s


def gallery_html():
    imgs, thumbs = [], []
    for i, (f, cap) in enumerate(GALLERY):
        on = ' class="on"' if i == 0 else ''
        imgs.append(f'          <img{on} src="./assets/img/{f}" alt="에어로 S1 {cap}" data-cap="{cap}">')
        oncls = ' class="on"' if i == 0 else ''
        thumbs.append(f'      <button{oncls} type="button" aria-label="{cap}"><img src="./assets/img/{f}" alt=""></button>')
    n = len(GALLERY)
    main = ('    <div class="gmain">\n' + '\n'.join(imgs) +
            '\n          <button class="gnav prev" type="button" data-g="-1" aria-label="이전 사진">←</button>\n'
            '          <button class="gnav next" type="button" data-g="1" aria-label="다음 사진">→</button>\n'
            f'          <div class="gcount"><span class="gcap">{GALLERY[0][1]}</span><span class="gnum">1 / {n}</span></div>\n        </div>\n'
            '    <div class="thumbs" role="tablist">\n' + '\n'.join(thumbs) + '\n    </div>')
    return main


def convert_html(name, s, letter, assets):
    """SP 페이지 HTML → 템플릿 HTML. assets: 이미지 경로 접두 ('./assets/img/' 또는 '../moto-a/assets/img/')"""
    L = letter.upper()
    # head: 파비콘·OG 정리
    s = re.sub(r'<link rel="icon"[^>]*>\n?', '', s)
    s = re.sub(r'<link rel="apple-touch-icon"[^>]*>\n?', '', s)
    s = s.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<link rel="icon" type="image/svg+xml" href="./favicon.svg">')
    s = s.replace('<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">\n<link rel="icon" type="image/svg+xml" href="./favicon.svg">')
    og = './og.jpg' if letter == 'a' else '../moto-a/og.jpg'
    s = s.replace('https://spmobility.netlify.app/assets/img/og.jpg', og)
    s = re.sub(r'<meta property="og:image:width"[^>]*><meta property="og:image:height"[^>]*>\n?', '', s)
    # 제목
    if name == 'index.html':
        s = re.sub(r'<title>.*?</title>', f'<title>볼트라이드 — 전기 이륜차 · 바이크 홈페이지 템플릿 (디자인 {L} · {CONCEPT[ord(letter)-96]})</title>', s, count=1)
        s = s.replace('<meta property="og:title" content="에스피모빌리티 | 전기 이륜차 캄페온">', f'<meta property="og:title" content="볼트라이드 — 전기 이륜차 · 바이크 홈페이지 템플릿 (디자인 {L})">')
    # 영상 슬롯 제거
    s = re.sub(r'\s*<video class="bg vid"[^>]*></video>', '', s)
    s = s.replace(' data-video="./assets/video/product-360.mp4"', '')
    # 제품 갤러리 재구성
    if name == 'product.html':
        a = s.index('    <div class="gmain"'); b = s.index('    </div>\n  </div>\n\n  <div class="buy')
        s = s[:a] + gallery_html() + '\n' + s[b + len('    </div>\n'):]
    # 회사소개 서비스 카드 재구성
    if name == 'about.html':
        a = s.index(ECARDS_OLD_START); b = s.index('</div>\n</section>', a)
        s = s[:a] + ECARDS_NEW + s[b + len('</div>'):]
    # 폼: Netlify 속성 제거 → 데모 동작(site.js 가 항상 접수 완료 상태로 전환)
    s = s.replace(' method="POST" data-netlify="true" netlify-honeypot="bot-field" action="/thanks.html"', ' action="#"')
    s = re.sub(r'<input type="hidden" name="form-name" value="[^"]*"><p class="sr"><label>Don’t fill this out: <input name="bot-field"></label></p>\n?', '', s)
    # 워드마크 이미지 → 텍스트
    s = re.sub(r'<img class="wm" src="\./assets/img/wordmark-campeon[^"]*" alt="Campeon">', '<span class="wm wmtxt">AERO S1</span>', s)
    s = re.sub(r'<img src="\./assets/img/wordmark-campeon[^"]*" alt="Campeon">', '<span class="wmtxt">AERO S1</span>', s)
    # 로고
    s = s.replace('<img src="./assets/img/logo-sp.png" alt="SP MOBILITY">', f'<img src="{assets}logo.svg" alt="VOLTRIDE">')
    s = s.replace('<img src="./assets/img/logo-sp-white.png" alt="SP MOBILITY" style="height:44px;width:auto">', f'<img src="{assets}logo-white.svg" alt="VOLTRIDE" style="height:44px;width:auto">')
    s = s.replace('<img src="./assets/img/logo-sp-white.png" alt="SP MOBILITY">', f'<img src="{assets}logo-white.svg" alt="VOLTRIDE">')
    if '<header class="hdr dark' in s:
        s = s.replace(f'aria-label="SP Mobility 홈"><img src="{assets}logo.svg"', f'aria-label="SP Mobility 홈"><img src="{assets}logo-white.svg"')
    # 문구
    s = neutral(s)
    # 이미지 경로
    def img(m):
        f = m.group(1)
        return assets + IMGMAP.get(f, f)
    s = re.sub(r'\./assets/img/([A-Za-z0-9_.-]+)', img, s)
    return s


def strip_anim_css(css):
    out, i = [], 0
    pat = re.compile(r'@(?:-webkit-)?keyframes\s+[\w-]+\s*\{')
    while True:
        m = pat.search(css, i)
        if not m:
            out.append(css[i:]); break
        out.append(css[i:m.start()])
        depth, j = 1, m.end()
        while j < len(css) and depth:
            depth += {'{': 1, '}': -1}.get(css[j], 0); j += 1
        i = j
    css = ''.join(out)
    css = re.sub(r'(?<![-\w])animation(?:-[\w-]+)?\s*:[^;}]*;', '', css)
    css = re.sub(r'(?<![-\w])animation(?:-[\w-]+)?\s*:[^;}]*(?=\})', '', css)
    return css


def basic_js(js):
    js = js.replace("    setInterval(function () { show(idx + 1); }, 5000);\n", '')
    js = re.sub(r"  // home hero: subtle mouse parallax.*?\n  }\n", '', js, flags=re.S)
    return js


def make_placeholders(imgdir):
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(imgdir, exist_ok=True)
    try:
        font = ImageFont.truetype('C:/Windows/Fonts/malgun.ttf', 28)
    except Exception:
        font = ImageFont.load_default()
    made = 0
    for f, (w, h) in SLOTS.items():
        p = os.path.join(imgdir, f)
        if os.path.exists(p):
            continue
        if f.endswith('.png'):
            im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((int(w * .08), int(h * .3), int(w * .92), int(h * .92)), radius=int(w * .06), fill=(11, 27, 43, 140))
            d.text((w // 2, int(h * .61)), f'제품 누끼 자리\n{f}', fill=(255, 255, 255, 200), font=font, anchor='mm', align='center')
        else:
            im = Image.new('RGB', (w, h), (11, 27, 43)); d = ImageDraw.Draw(im)
            for k in range(0, 40):
                r = int(min(w, h) * (1 - k / 40) * .7)
                c = (11 + k, 27 + k * 2, 43 + k * 3)
                d.ellipse((w // 2 - r, int(h * .55) - r // 2, w // 2 + r, int(h * .55) + r // 2), fill=c)
            d.text((w // 2, h // 2), f'사진 자리 · {f}\n{w}×{h}', fill=(180, 200, 220), font=font, anchor='mm', align='center')
        im.save(p); made += 1
    return made


def build(n):
    letter = LETTERS[n]; vdir = os.path.join(VAR, f'v{n}')
    land = os.path.join(OUT, f'{IND}-{letter}'); basic = land + '-basic'
    assets = './assets/img/' if letter == 'a' else '../moto-a/assets/img/'
    for d in (land, basic):
        rmtree(d); os.makedirs(os.path.join(d, 'assets'), exist_ok=True)
        open(os.path.join(d, 'favicon.svg'), 'w', encoding='utf-8').write(FAVICON)
    if letter == 'a':
        imgdir = os.path.join(land, 'assets', 'img')
        # 이미 설치된 사진이 있으면 보존: 기존 폴더에서 가져온다
        keep = os.path.join(OUT, '_moto_img_keep')
        if os.path.isdir(keep):
            shutil.copytree(keep, imgdir)
        else:
            os.makedirs(imgdir, exist_ok=True)
        open(os.path.join(imgdir, 'logo.svg'), 'w', encoding='utf-8').write(LOGO.format(c='#0B1B2B'))
        open(os.path.join(imgdir, 'logo-white.svg'), 'w', encoding='utf-8').write(LOGO.format(c='#ffffff'))
        made = make_placeholders(imgdir)
        if made:
            print(f'  플레이스홀더 {made}장 생성 (실제 사진으로 교체 필요)')
    # 패치 모듈
    patch = None
    pp = os.path.join(vdir, 'patch.py')
    if os.path.isfile(pp):
        sp = importlib.util.spec_from_file_location(f'patch_v{n}', pp); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); patch = m.patch
    home = open(os.path.join(vdir, 'home.html'), encoding='utf-8').read()
    theme = open(os.path.join(vdir, 'theme.css'), encoding='utf-8').read() + WM_CSS
    site_css = open(os.path.join(SP, 'assets', 'site.css'), encoding='utf-8').read()
    site_js = open(os.path.join(SP, 'assets', 'site.js'), encoding='utf-8').read()
    site_js = site_js.replace("if (location.protocol === 'file:') { ev.preventDefault();", "{ ev.preventDefault();")  # 폼은 항상 데모 접수 완료
    if letter != 'a':
        theme = theme.replace('./assets/img/', assets); site_css = site_css.replace('./assets/img/', assets)
    for d, is_basic in ((land, False), (basic, True)):
        css_t = theme; css_s = site_css; js = site_js
        if is_basic:
            css_t = strip_anim_css(css_t) + BASIC_CSS; css_s = strip_anim_css(css_s); js = basic_js(js)
            if letter == 'a':
                css_t = css_t.replace('./assets/img/', '../moto-a/assets/img/'); css_s = css_s.replace('./assets/img/', '../moto-a/assets/img/')
        open(os.path.join(d, 'assets', 'theme.css'), 'w', encoding='utf-8').write(css_t)
        open(os.path.join(d, 'assets', 'site.css'), 'w', encoding='utf-8').write(css_s)
        open(os.path.join(d, 'assets', 'site.js'), 'w', encoding='utf-8').write(js)
        open(os.path.join(d, 'assets', 'dealers.js'), 'w', encoding='utf-8').write(DEALERS_JS)
        a_assets = assets if not (is_basic and letter == 'a') else '../moto-a/assets/img/'
        for name in ('index.html', 'about.html', 'product.html', 'consult.html', 'support.html', 'thanks.html'):
            s = open(os.path.join(SP, name), encoding='utf-8').read()
            if name == 'index.html':
                a = s.index('<!-- HERO -->'); b = s.index('<footer class="foot">')
                s = s[:a] + home.strip() + chr(10) * 2 + s[b:]
            s = s.replace('<link rel="stylesheet" href="./assets/site.css">', '<link rel="stylesheet" href="./assets/site.css">\n<link rel="stylesheet" href="./assets/theme.css">')
            if patch:
                s = patch(name, s)
            s = convert_html(name, s, letter, a_assets)
            if is_basic:
                s = s.replace('홈페이지 템플릿 (디자인', '홈페이지 템플릿 (기본형 · 디자인')
            left = sorted(set(LEFTOVER.findall(s)))
            if left:
                print(f'  [잔여 문구] {os.path.basename(d)}/{name}: {left}')
            open(os.path.join(d, name), 'w', encoding='utf-8').write(s)
    print(f'v{n} → {land}  /  {basic}')


if __name__ == '__main__':
    want = [int(x) for x in sys.argv[1:]] or [1, 2, 3, 4, 5]
    for n in want:
        build(n)
