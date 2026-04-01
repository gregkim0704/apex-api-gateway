"""프리셋 시나리오 4개 정의"""

SCENARIOS = [
    {
        "id": "customer_inquiry",
        "name": "고객 문의 접수",
        "icon": "🏠",
        "description": "새 고객 등록 → 관심매물 세금 분석 → 브리핑 자료 생성",
        "agents": ["crm", "legal", "briefing"],
        "color": "#3b82f6",
        "inputs": [
            {"key": "customerName", "label": "고객명", "placeholder": "예: 김철수"},
            {"key": "phone", "label": "연락처", "placeholder": "예: 010-1234-5678"},
            {"key": "interest", "label": "관심 매물", "placeholder": "예: 역삼동 래미안 84㎡"},
        ],
    },
    {
        "id": "ranking_management",
        "name": "매물 순위 관리",
        "icon": "📊",
        "description": "매물 순위 확인 → 하락 감지 → 광고 문구 자동 생성",
        "agents": ["sentinel", "growth"],
        "color": "#f59e0b",
        "inputs": [
            {"key": "region", "label": "지역", "placeholder": "예: 강남구"},
            {"key": "complexName", "label": "단지명", "placeholder": "예: 래미안역삼"},
        ],
    },
    {
        "id": "auction_analysis",
        "name": "경매 물건 분석",
        "icon": "🔨",
        "description": "시세 조회 → 세금 분석 → 투자 브리핑 자동 생성",
        "agents": ["finance", "legal", "briefing"],
        "color": "#ef4444",
        "inputs": [
            {"key": "address", "label": "물건 주소", "placeholder": "예: 서울 마포구 상암동"},
            {"key": "appraisalValue", "label": "감정가 (만원)", "placeholder": "예: 52000"},
        ],
    },
    {
        "id": "online_marketing",
        "name": "온라인 마케팅",
        "icon": "🌐",
        "description": "매물 정보 → 광고카피 5종 + 홈페이지 콘텐츠 자동 생성",
        "agents": ["growth"],
        "color": "#10b981",
        "inputs": [
            {"key": "propertyType", "label": "매물 유형", "placeholder": "예: 아파트"},
            {"key": "area", "label": "면적 (평)", "placeholder": "예: 25"},
            {"key": "price", "label": "가격", "placeholder": "예: 18억"},
            {"key": "features", "label": "특징", "placeholder": "예: 역세권, 학군, 남향"},
        ],
    },
]
