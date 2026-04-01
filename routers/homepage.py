"""App #11 — AI 홈페이지 빌더 API 라우터"""
import os
import json
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")


class HomepageRequest(BaseModel):
    agencyName: str = ""
    ownerName: str = ""
    phone: str = ""
    address: str = ""
    description: str = ""
    listings: list = []
    template: str = ""


@router.post("/generate")
async def generate_homepage(req: HomepageRequest):
    """AI 홈페이지 콘텐츠 생성"""
    prompt = f"""중개사 정보:
- 중개사명: {req.agencyName}
- 대표: {req.ownerName}
- 전화: {req.phone}
- 주소: {req.address}
- 소개: {req.description}
- 매물 수: {len(req.listings)}개
- 템플릿: {req.template}

위 정보로 부동산 중개사 홈페이지 콘텐츠를 생성하세요.
반드시 JSON으로 응답: {{"heroTitle":"메인 카피","heroSubtitle":"서브 카피","aboutText":"소개글 3-4문장","seoTitle":"SEO 제목","seoDescription":"SEO 설명","ctaText":"CTA 버튼 텍스트"}}"""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514", "max_tokens": 1500,
                "system": "부동산 중개사 홈페이지 전문 웹 디자이너. 신뢰감을 주는 한국어 콘텐츠 생성.",
                "messages": [{"role": "user", "content": prompt}],
            },
        )
    data = resp.json()
    text = data.get("content", [{}])[0].get("text", "{}")

    try:
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        result = json.loads(match.group()) if match else {"raw": text}
    except Exception:
        result = {"raw": text}

    return result
