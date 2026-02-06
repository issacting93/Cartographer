"""
Context Engine: API Router

Exposes the Task-First Interaction Model via REST endpoints.
Implements the three interaction patterns from the CUI 2026 paper:
- Pattern 1: Pin to Task (/event/pin)
- Pattern 2: Task Shelf (/task/*)
- Pattern 3: Context Lens (/query/context)
"""

from fastapi import APIRouter, HTTPException
import logging

from .models import (
    CreateTaskRequest,
    CreateTaskResponse,
    TaskListResponse,
    SwitchTaskRequest,
    SwitchTaskResponse,
    PinEventRequest,
    PinEventResponse,
    ContextQueryRequest,
    ContextQueryResponse,
    ConstraintNode,
    TaskObject
)
from .task_manager import task_manager

logger = logging.getLogger(__name__)

router = APIRouter()


# --- Task Management (Pattern 2: Task Shelf) ---

@router.post("/task/create", response_model=CreateTaskResponse)
async def create_task(request: CreateTaskRequest):
    """
    Create a new Task Object.
    
    This is the "Materialization" step in the Task Lifetime.
    The task becomes the active context for subsequent interactions.
    """
    try:
        task = task_manager.create_task(
            user_id=request.user_id,
            name=request.name,
            description=request.description,
            initial_nodes=request.initial_nodes
        )
        return CreateTaskResponse(task_id=task.id, ok=True)
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/task/list", response_model=TaskListResponse)
async def list_tasks(user_id: str):
    """
    List all tasks for a user.
    
    Returns tasks sorted by last updated, with the active task ID.
    This powers the "Task Shelf" UI component.
    """
    tasks = task_manager.list_tasks(user_id)
    active_task = task_manager.get_active_task(user_id)
    
    return TaskListResponse(
        tasks=tasks,
        active_task_id=active_task.id if active_task else None
    )


@router.post("/task/switch", response_model=SwitchTaskResponse)
async def switch_task(request: SwitchTaskRequest):
    """
    Switch to a different task.
    
    This is the "Resumption" step in the Task Lifetime.
    Updates last_resumed_at timestamp for interruption tracking.
    """
    success = task_manager.set_active_task(request.user_id, request.task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_manager.get_task(request.user_id, request.task_id)
    return SwitchTaskResponse(ok=True, task=task)


@router.get("/task/{task_id}")
async def get_task(user_id: str, task_id: str):
    """Get a specific task by ID."""
    task = task_manager.get_task(user_id, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.post("/task/{task_id}/suspend")
async def suspend_task(user_id: str, task_id: str):
    """
    Suspend a task.
    
    Lifecycle: Execution → Suspension
    Increments interruption_count for evaluation metrics.
    """
    success = task_manager.suspend_task(user_id, task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"ok": True}


@router.post("/task/{task_id}/complete")
async def complete_task(user_id: str, task_id: str):
    """
    Mark a task as completed.
    
    Lifecycle: Execution → Completion
    """
    success = task_manager.complete_task(user_id, task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"ok": True}


# --- Pattern 1: Pin to Task ---

@router.post("/event/pin", response_model=PinEventResponse)
async def pin_event(request: PinEventRequest):
    """
    Pin text to a Task as a Constraint Node.
    
    This implements Pattern 1 from the paper: "Keyword as Context"
    Converts free-form text into a persistent, typed constraint.
    """
    node = ConstraintNode(
        type=request.type,
        label=request.text,
        source=request.source,
        pinned=True,
        active=True
    )
    
    result = task_manager.add_node(
        user_id=request.user_id,
        task_id=request.task_id,
        node=node
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return PinEventResponse(node_id=node.id, ok=True)


# --- Pattern 3: Context Lens ---

@router.post("/query/context", response_model=ContextQueryResponse)
async def query_context(request: ContextQueryRequest):
    """
    Query with explicit context scope.
    
    This implements Pattern 3: "Context Lens"
    Only nodes in the `scope` list are included in the augmented prompt.
    If scope is empty, all active nodes are included.
    """
    task = task_manager.get_task(request.user_id, request.task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Determine which nodes are in scope
    if request.scope:
        # Explicit scope: only include specified nodes
        active_nodes = [n for n in task.nodes if n.id in request.scope]
    else:
        # Default scope: all active nodes
        active_nodes = task.get_active_nodes()
    
    # Build augmented prompt
    context_lines = []
    for node in active_nodes:
        prefix = f"[{node.type}]"
        context_lines.append(f"{prefix} {node.label}")
    
    context_block = "\n".join(context_lines)
    
    augmented_prompt = f"""ACTIVE CONTEXT:
{context_block}

USER REQUEST:
{request.prompt}

Please respond while respecting all constraints and context above."""
    
    # Generate suggested scripts (basic version)
    scripts = []
    if active_nodes:
        # Example script suggestions based on context
        goal_nodes = [n for n in active_nodes if n.type == "Goal"]
        if goal_nodes:
            scripts.append(f"Help me with: {goal_nodes[0].label}")
        
        constraint_nodes = [n for n in active_nodes if n.type == "Constraint"]
        if constraint_nodes:
            scripts.append(f"Remember: {constraint_nodes[0].label}")
    
    return ContextQueryResponse(
        augmented_prompt=augmented_prompt,
        active_nodes=active_nodes,
        scripts=scripts
    )


# --- Node Operations ---

@router.post("/task/{task_id}/node/toggle")
async def toggle_node(user_id: str, task_id: str, node_id: str, active: bool):
    """Toggle whether a node is in scope."""
    success = task_manager.toggle_node_active(user_id, task_id, node_id, active)
    
    if not success:
        raise HTTPException(status_code=404, detail="Task or node not found")
    
    return {"ok": True, "active": active}


# --- Metrics (for Evaluation) ---

@router.get("/task/{task_id}/metrics")
async def get_task_metrics(user_id: str, task_id: str):
    """
    Get evaluation metrics for a task.
    
    Returns:
    - restatement_count: Number of times constraints were re-stated
    - constraint_violations: Number of times LLM violated constraints
    - interruption_count: Number of task suspensions
    - conversation_turns: Total turns in the task
    """
    task = task_manager.get_task(user_id, task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.id,
        "task_name": task.name,
        "status": task.status,
        "metrics": task.metrics.model_dump()
    }
