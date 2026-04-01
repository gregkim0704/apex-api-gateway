"""App #7 — 브리핑 PPT 생성기 API 라우터"""
import os
import json
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")


class BriefingRequest(BaseModel):
    address: str = "서울시 강남구 역삼동"
    complex_name: str = "래미안역삼"


@router.post("/analyze")
async def analyze_briefing(req: BriefingRequest):
    """AI 브리핑 자료 생성 (단지개요/시세/환경/투자포인트/리스크)"""
    prompt = f"""아파트 단지 정보:
- 주소: {req.address}
- 단지명: {req.complex_name}

투자 브리핑 자료를 구조화하세요. 반드시 JSON으로 응답:
{{"overview":"단지개요 2-3문장","priceAnalysis":"시세분석 3-4문장","environment":"주변환경 3-4문장","investmentPoints":"투자포인트 3-4문장","risks":"리스크요인 2-3문장"}}"""

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-20250514", "max_tokens": 2000,
                "system": "부동산 브리핑 전문가. 아파트 단지 투자 분석 자료를 구조화. 한국어, JSON 응답.",
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
