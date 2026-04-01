"""App #6 — 세무·법무 AI 비서 API 라우터"""
import os
import httpx
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SYSTEM_PROMPT = """당신은 APEX 부동산 세무·법무 AI 비서입니다. 한국 부동산 관련 세금(양도소득세, 취득세, 재산세, 종합부동산세)과 법률(주택임대차보호법, 공인중개사법) 전문가입니다.
- 항상 한국어로 답변합니다.
- 구체적인 세율, 계산법, 판례를 포함합니다.
- 2024년 기준 최신 세법을 적용합니다.
- 복잡한 사안은 세무사/변호사 상담을 권합니다."""


from typing import Any, List

class ChatRequest(BaseModel):
    message: str
    history: List[Any] = []


class TaxCalcRequest(BaseModel):
    sale_price: int  # 만원
    buy_price: int   # 만원
    holding_years: int
    is_multi_home: bool = False


@router.post("/chat")
async def chat(req: ChatRequest):
    """AI 세무·법무 상담"""
    messages = []
    for h in req.history[-10:]:
        role = "assistant" if h.get("role") == "bot" else "user"
        messages.append({"role": role, "content": h.get("text", "")})
    messages.append({"role": "user", "content": req.message})

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 1024, "system": SYSTEM_PROMPT, "messages": messages},
        )
    data = resp.json()
    text = data.get("content", [{}])[0].get("text", "응답 생성 실패")
    return {"text": text}


@router.post("/calc/transfer-tax")
async def calc_transfer_tax(req: TaxCalcRequest):
    """양도소득세 계산"""
    gain = (req.sale_price - req.buy_price) * 10000
    if gain <= 0:
        return {"gain": 0, "tax": 0, "rate": 0}

    deduction = 0
    if not req.is_multi_home and req.holding_years >= 3:
        rate = min(req.holding_years * 2, 30)
        deduction = int(gain * rate / 100)

    taxable = gain - deduction - 2500000
    if taxable <= 0:
        return {"gain": gain, "tax": 0, "rate": 0, "deduction": deduction}

    brackets = [
        (14000000, 6, 0), (50000000, 15, 1260000), (88000000, 24, 5760000),
        (150000000, 35, 15440000), (300000000, 38, 19940000),
        (500000000, 40, 25940000), (1000000000, 42, 35940000), (float('inf'), 45, 65940000),
    ]
    tax = 0
    rate = 0
    for limit, r, ded in brackets:
        if taxable <= limit:
            tax = int(taxable * r / 100 - ded)
            rate = r
            break

    return {"gain": gain, "tax": max(0, tax), "rate": rate, "deduction": deduction}
