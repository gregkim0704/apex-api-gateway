"""에이전트 오케스트레이션 API 라우터

LangGraph 기반 7-Agent 자율 운영 시스템의 API 엔드포인트.
시나리오 선택 → 에이전트 체이닝 실행 → 결과 반환.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any

from agents.scenarios import SCENARIOS
from agents.graph import execute_workflow, workflow_store

router = APIRouter()


class ExecuteRequest(BaseModel):
    scenario_id: str
    inputs: dict[str, Any] = {}


@router.get("/scenarios")
async def list_scenarios():
    """실행 가능한 시나리오 목록"""
    return {"scenarios": SCENARIOS}


@router.post("/execute")
async def run_workflow(req: ExecuteRequest):
    """워크플로우 실행 — 시나리오 기반 에이전트 체이닝"""
    result = await execute_workflow(req.scenario_id, req.inputs)
    return result


@router.get("/status/{workflow_id}")
async def get_status(workflow_id: str):
    """워크플로우 실행 상태 조회"""
    state = workflow_store.get(workflow_id)
    if not state:
        return {"error": "워크플로우를 찾을 수 없습니다."}
    return state
