"""LangGraph 기반 에이전트 오케스트레이션 그래프

7개 에이전트를 순차/병렬로 실행하는 StateGraph.
시나리오에 정의된 에이전트 순서대로 체이닝합니다.
"""
import logging
import time
import uuid
from typing import Any
from agents.nodes import AGENT_NODES
from agents.scenarios import SCENARIOS

logger = logging.getLogger(__name__)

# 워크플로우 실행 결과 저장소 (인메모리)
workflow_store: dict[str, dict] = {}


async def execute_workflow(scenario_id: str, inputs: dict) -> dict:
    """시나리오 기반 워크플로우 실행

    Args:
        scenario_id: 시나리오 ID (예: "customer_inquiry")
        inputs: 사용자 입력값

    Returns:
        워크플로우 실행 결과 (단계별 로그 + 최종 결과)
    """
    # 시나리오 찾기
    scenario = next((s for s in SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        return {"error": f"시나리오 '{scenario_id}'를 찾을 수 없습니다."}

    workflow_id = str(uuid.uuid4())[:8]
    agents = scenario["agents"]
    total = len(agents)

    logger.info(f"🎯 워크플로우 시작: {scenario['name']} (ID: {workflow_id})")
    logger.info(f"   에이전트 체인: {' → '.join(agents)}")

    # 상태 초기화
    state = {
        "workflow_id": workflow_id,
        "scenario": scenario_id,
        "inputs": inputs,
        "results": {},
        "steps": [],
        "status": "running",
    }

    workflow_store[workflow_id] = state

    # 에이전트 순차 실행
    for idx, agent_name in enumerate(agents, 1):
        step = {
            "step": idx,
            "agent": agent_name,
            "status": "running",
            "started_at": time.time(),
        }
        state["steps"].append(step)

        node_fn = AGENT_NODES.get(agent_name)
        if not node_fn:
            step["status"] = "skipped"
            step["error"] = f"에이전트 '{agent_name}' 노드를 찾을 수 없습니다."
            logger.warning(f"  ⚠️ Step {idx}/{total}: {agent_name} — 스킵")
            continue

        try:
            logger.info(f"  ▶ Step {idx}/{total}: {agent_name} 실행 중...")
            result = await node_fn(state)

            # 상태 업데이트
            if "results" in result:
                state["results"] = result["results"]

            step["status"] = "completed"
            step["completed_at"] = time.time()
            step["duration"] = round(step["completed_at"] - step["started_at"], 2)
            step["result"] = state["results"].get(agent_name, {}).get("data", {})

            logger.info(f"  ✅ Step {idx}/{total}: {agent_name} 완료 ({step['duration']}초)")

        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
            step["completed_at"] = time.time()
            step["duration"] = round(step["completed_at"] - step["started_at"], 2)
            logger.error(f"  ❌ Step {idx}/{total}: {agent_name} 실패 — {e}")

    # 워크플로우 완료
    state["status"] = "completed"
    state["completed_at"] = time.time()

    # 최종 요약 생성
    completed = sum(1 for s in state["steps"] if s["status"] == "completed")
    failed = sum(1 for s in state["steps"] if s["status"] == "failed")

    state["summary"] = {
        "scenario": scenario["name"],
        "total_agents": total,
        "completed": completed,
        "failed": failed,
        "steps": [
            {
                "step": s["step"],
                "agent": s["agent"],
                "status": s["status"],
                "duration": s.get("duration", 0),
                "result": s.get("result", s.get("error", "")),
            }
            for s in state["steps"]
        ],
    }

    logger.info(f"🎯 워크플로우 완료: {completed}/{total} 성공")

    return state
