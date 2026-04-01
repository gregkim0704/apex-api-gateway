"""APEX 부동산 OS — 통합 API Gateway

12개 앱의 API를 단일 FastAPI 서버로 통합합니다.
모든 엔드포인트는 /api/v1/ 접두사를 사용합니다.

실행: uvicorn main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import realtrade, legal_ai, ad_copy, briefing, crm, homepage

app = FastAPI(
    title="APEX 부동산 OS API",
    description="12개 부동산 앱의 통합 API Gateway · KIRI × APEX",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(realtrade.router, prefix="/api/v1/realtrade", tags=["실거래가"])
app.include_router(legal_ai.router, prefix="/api/v1/legal", tags=["세무·법무 AI"])
app.include_router(ad_copy.router, prefix="/api/v1/adcopy", tags=["광고 문구"])
app.include_router(briefing.router, prefix="/api/v1/briefing", tags=["브리핑"])
app.include_router(crm.router, prefix="/api/v1/crm", tags=["CRM"])
app.include_router(homepage.router, prefix="/api/v1/homepage", tags=["홈페이지 빌더"])


@app.get("/")
async def root():
    return {
        "service": "APEX 부동산 OS API Gateway",
        "version": "1.0.0",
        "endpoints": {
            "실거래가": "/api/v1/realtrade",
            "세무법무AI": "/api/v1/legal",
            "광고문구": "/api/v1/adcopy",
            "브리핑": "/api/v1/briefing",
            "CRM": "/api/v1/crm",
        },
        "docs": "/docs",
    }


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "apps": 12, "agents": 7}
