import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.agent.state import AgentWorkflowState
from backend.app.agent.nodes import (
    discover_jobs_node,
    deduplicate_and_persist_jobs_node,
    match_jobs_node,
    tailor_resumes_node,
    check_policy_and_route_node,
    submit_applications_node
)
from backend.app.db.session import SyncSessionLocal
from backend.app.models.application import AgentRun, AgentRunEvent

def route_after_policy(state: AgentWorkflowState):
    """Conditional router based on automation policy and queued applications."""
    if state.get("auto_submit_apps") and len(state["auto_submit_apps"]) > 0:
        return "submit_applications"
    return END

def build_agent_graph():
    """Builds and compiles the production LangGraph state machine."""
    builder = StateGraph(AgentWorkflowState)

    # Add Nodes
    builder.add_node("discover_jobs", discover_jobs_node)
    builder.add_node("deduplicate_and_persist", deduplicate_and_persist_jobs_node)
    builder.add_node("match_jobs", match_jobs_node)
    builder.add_node("tailor_resumes", tailor_resumes_node)
    builder.add_node("check_policy_and_route", check_policy_and_route_node)
    builder.add_node("submit_applications", submit_applications_node)

    # Add Edges
    builder.add_edge(START, "discover_jobs")
    builder.add_edge("discover_jobs", "deduplicate_and_persist")
    builder.add_edge("deduplicate_and_persist", "match_jobs")
    builder.add_edge("match_jobs", "tailor_resumes")
    builder.add_edge("tailor_resumes", "check_policy_and_route")

    # Conditional Routing
    builder.add_conditional_edges(
        "check_policy_and_route",
        route_after_policy,
        {
            "submit_applications": "submit_applications",
            END: END
        }
    )
    builder.add_edge("submit_applications", END)

    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)

agent_graph = build_agent_graph()

def execute_pipeline(user_id: int = 1, trigger_type: str = "manual") -> Dict[str, Any]:
    """Runs the complete end-to-end agent workflow and records execution audit metrics."""
    run_uuid = f"run_{uuid.uuid4().hex[:12]}"
    session = SyncSessionLocal()
    
    # Create DB run record
    run_record = AgentRun(
        run_uuid=run_uuid,
        trigger_type=trigger_type,
        status="running",
        started_at=datetime.utcnow()
    )
    session.add(run_record)
    session.commit()
    session.refresh(run_record)

    initial_state: AgentWorkflowState = {
        "run_id": run_uuid,
        "user_id": user_id,
        "automation_mode": "automatic",
        "min_match_score": 75,
        "raw_discovered": [],
        "deduplicated_jobs": [],
        "eligible_jobs": [],
        "evaluated_jobs": [],
        "tailored_resumes": [],
        "pending_approval_apps": [],
        "auto_submit_apps": [],
        "submitted_apps": [],
        "failed_apps": [],
        "logs": [f"Pipeline initialized (trigger: {trigger_type})"],
        "errors": [],
        "current_stage": "started",
        "status": "running"
    }

    try:
        config = {"configurable": {"thread_id": run_uuid}}
        final_state = agent_graph.invoke(initial_state, config=config)
        
        # Update run metrics in DB
        run_record.status = "completed"
        run_record.completed_at = datetime.utcnow()
        run_record.jobs_discovered = len(final_state.get("raw_discovered", []))
        run_record.jobs_matched = len(final_state.get("evaluated_jobs", []))
        run_record.resumes_tailored = len(final_state.get("tailored_resumes", []))
        run_record.applications_submitted = len(final_state.get("submitted_apps", []))
        
        # Log events
        for log in final_state.get("logs", []):
            event = AgentRunEvent(
                run_id=run_record.id,
                stage="workflow",
                level="info",
                message=log
            )
            session.add(event)
        session.commit()
        return final_state
    except Exception as e:
        session.rollback()
        run_record.status = "failed"
        run_record.completed_at = datetime.utcnow()
        run_record.error_summary = str(e)
        session.commit()
        print(f"Agent pipeline execution error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("Executing full LangGraph pipeline test...")
    result = execute_pipeline(user_id=1, trigger_type="manual_test")
    print("\n--- Pipeline Execution Summary ---")
    print(f"Jobs Discovered: {len(result.get('raw_discovered', []))}")
    print(f"Jobs Deduplicated: {len(result.get('deduplicated_jobs', []))}")
    print(f"Jobs Evaluated: {len(result.get('evaluated_jobs', []))}")
    print(f"Resumes Tailored: {len(result.get('tailored_resumes', []))}")
    print(f"Applications Submitted: {len(result.get('submitted_apps', []))}")
    for log in result.get("logs", []):
        print(f"  • {log}")
