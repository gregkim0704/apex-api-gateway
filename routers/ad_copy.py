"""App #8 — 매물 광고 문구 생성기 API 라우터"""
import os
import json
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")


class AdCopyRequest(BaseModel):
    property_type: str = "아파트"  # 아파트/오피스텔/빌라
    area: float = 84  # 평
    floor: int = 12
    price: str = "18억"
    features: list[str] = []  # 역세권, 학군, 조망 등
    description: str = ""


@router.post("/generate")
async def generate_ad_copy(req: AdCopyRequest):
    """AI 매물 광고 문구 5종 생성"""
    prompt = f"""매물 정보:
- 유형: {req.property_type}
- 면적: {req.area}평
- 층수: {req.floor}층
- 가격: {req.price}
- 특징: {', '.join(req.features) if req.features else '없음'}
- 추가설명: {req.description or '없음'}

위 매물에 대해 5가지 스타일의 광고 문구를 생성하세요.
반드시 JSON 배열로 응답: [{{"style":"간결형","text":"..."}},{{"style":"감성형","text":"..."}},{{"style":"정보형","text":"..."}},{{"style":"비교형","text":"..."}},{{"style":"긴급형","text":"..."}}]"""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514", "max_tokens": 1500,
                "system": "부동산 매물 광고 카피라이터. 네이버 부동산/직방에 바로 등록 가능한 실용적 문구 생성. 한국어, 이모지 적절히 사용.",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
    data = resp.json()
    text = data.get("content", [{}])[0].get("text", "[]")

    try:
        import re
        match = re.search(r'\[.*\]', text, re.DOTALL)
        copies = json.loads(match.group()) if match else []
    except Exception:
        copies = [{"style": "기본", "text": text}]

    return {"copies": copies}
