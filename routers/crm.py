"""App #10 — 고객 CRM API 라우터"""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# In-memory store (실 서비스에서는 Supabase/PostgreSQL 사용)
customers_db = [
    {"id": 1, "name": "김철수", "phone": "010-1234-5678", "interest": "역삼동 래미안", "status": "임장예약", "notes": "전세 8억 이하 희망"},
    {"id": 2, "name": "이영희", "phone": "010-2345-6789", "interest": "삼성동 아이파크", "status": "계약준비", "notes": "매매 25억 예산"},
    {"id": 3, "name": "박민수", "phone": "010-3456-7890", "interest": "대치동 은마", "status": "상담완료", "notes": "투자 목적, 재건축 관심"},
]

next_id = 4


class CustomerCreate(BaseModel):
    name: str
    phone: str = ""
    interest: str = ""
    status: str = "신규문의"
    notes: str = ""


class CustomerUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    interest: str | None = None
    status: str | None = None
    notes: str | None = None


@router.get("/customers")
async def list_customers(status: str | None = None):
    """고객 목록 조회"""
    if status:
        filtered = [c for c in customers_db if c["status"] == status]
        return {"count": len(filtered), "data": filtered}
    return {"count": len(customers_db), "data": customers_db}


@router.get("/customers/{customer_id}")
async def get_customer(customer_id: int):
    """고객 상세 조회"""
    for c in customers_db:
        if c["id"] == customer_id:
            return c
    return {"error": "고객을 찾을 수 없습니다."}


@router.post("/customers")
async def create_customer(req: CustomerCreate):
    """고객 등록"""
    global next_id
    customer = {"id": next_id, **req.model_dump()}
    customers_db.append(customer)
    next_id += 1
    return {"message": "고객 등록 완료", "customer": customer}


@router.put("/customers/{customer_id}")
async def update_customer(customer_id: int, req: CustomerUpdate):
    """고객 정보 수정"""
    for c in customers_db:
        if c["id"] == customer_id:
            for key, value in req.model_dump(exclude_none=True).items():
                c[key] = value
            return {"message": "수정 완료", "customer": c}
    return {"error": "고객을 찾을 수 없습니다."}


@router.get("/pipeline")
async def pipeline():
    """파이프라인 현황"""
    statuses = ["신규문의", "상담완료", "임장예약", "임장완료", "계약준비", "계약완료"]
    result = {}
    for s in statuses:
        result[s] = [c for c in customers_db if c["status"] == s]
    return result
