"""App #4 — 실거래가·건축물대장 API 라우터"""
import os
import httpx
from fastapi import APIRouter, Query

router = APIRouter()

API_KEY = os.getenv("DATA_GO_KR_API_KEY", "")
BASE_URL = "http://openapi.molit.go.kr"

REGION_CODES = {
    "강남구":"11680","서초구":"11650","송파구":"11710","마포구":"11440",
    "용산구":"11170","성동구":"11200","영등포구":"11560","강동구":"11740",
    "노원구":"11350","양천구":"11470",
}


def sqm_to_pyeong(sqm: float) -> float:
    return round(sqm / 3.305785, 1)


def format_price(man_won: int) -> str:
    if man_won >= 10000:
        eok = man_won // 10000
        r = man_won % 10000
        return f"{eok}억 {r:,}만원" if r else f"{eok}억"
    return f"{man_won:,}만원"


@router.get("/apt-trade")
async def apt_trade(region: str = Query(..., description="구 이름 (예: 강남구)"),
                    year_month: str = Query(..., description="YYYYMM (예: 202411)")):
    """아파트 매매 실거래가 조회"""
    code = REGION_CODES.get(region)
    if not code:
        return {"error": f"지원 지역: {', '.join(REGION_CODES.keys())}"}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{BASE_URL}/OpenAPI_ToolInstall498/service/rest/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev",
            params={"serviceKey": API_KEY, "LAWD_CD": code, "DEAL_YMD": year_month, "numOfRows": "50"},
        )
    if resp.status_code != 200:
        return {"error": f"API 호출 실패: {resp.status_code}"}

    items = resp.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
    if not isinstance(items, list):
        items = [items] if items else []

    results = []
    for item in items:
        price = int(item.get("거래금액", "0").replace(",", "").strip() or "0")
        area = float(item.get("전용면적", "0"))
        results.append({
            "아파트": item.get("아파트", ""),
            "법정동": item.get("법정동", ""),
            "거래금액": format_price(price),
            "전용면적": f"{area}㎡ ({sqm_to_pyeong(area)}평)",
            "층": item.get("층", ""),
            "거래일": f'{item.get("년","")}.{item.get("월","").zfill(2)}.{item.get("일","").strip().zfill(2)}',
            "건축년도": item.get("건축년도", ""),
        })
    return {"region": region, "period": year_month, "count": len(results), "data": results}


@router.get("/apt-rent")
async def apt_rent(region: str = Query(...), year_month: str = Query(...)):
    """아파트 전월세 실거래가 조회"""
    code = REGION_CODES.get(region)
    if not code:
        return {"error": f"지원 지역: {', '.join(REGION_CODES.keys())}"}

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{BASE_URL}/OpenAPI_ToolInstall498/service/rest/RTMSDataSvcAptRentDev/getRTMSDataSvcAptRentDev",
            params={"serviceKey": API_KEY, "LAWD_CD": code, "DEAL_YMD": year_month, "numOfRows": "50"},
        )
    if resp.status_code != 200:
        return {"error": f"API 호출 실패: {resp.status_code}"}

    items = resp.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
    if not isinstance(items, list):
        items = [items] if items else []

    results = []
    for item in items:
        deposit = int(item.get("보증금액", "0").replace(",", "").strip() or "0")
        monthly = int(item.get("월세금액", "0").replace(",", "").strip() or "0")
        results.append({
            "아파트": item.get("아파트", ""),
            "유형": "전세" if monthly == 0 else "월세",
            "보증금": format_price(deposit),
            "월세": f"{monthly}만원" if monthly > 0 else "-",
            "전용면적": f'{item.get("전용면적", "")}㎡',
            "층": item.get("층", ""),
        })
    return {"region": region, "period": year_month, "count": len(results), "data": results}


@router.get("/regions")
async def regions():
    """지원 지역 목록"""
    return {"regions": REGION_CODES}
