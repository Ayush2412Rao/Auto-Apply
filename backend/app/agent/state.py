from typing import TypedDict, List, Dict, Any, Optional

class AgentWorkflowState(TypedDict):
    run_id: str
    user_id: int
    automation_mode: str
    min_match_score: int
    
    raw_discovered: List[Dict[str, Any]]
    deduplicated_jobs: List[Dict[str, Any]]
    eligible_jobs: List[Dict[str, Any]]
    evaluated_jobs: List[Dict[str, Any]]
    tailored_resumes: List[Dict[str, Any]]
    
    pending_approval_apps: List[Dict[str, Any]]
    auto_submit_apps: List[Dict[str, Any]]
    submitted_apps: List[Dict[str, Any]]
    failed_apps: List[Dict[str, Any]]
    
    logs: List[str]
    errors: List[str]
    current_stage: str
    status: str
