"""
Context Engine: Task Manager

Handles CRUD operations for Task Objects.
Implements the Task Lifetime: Conception → Materialization → Execution → Suspension → Resumption → Completion
"""

import os
import json
from typing import Optional, List
from datetime import datetime
from pathlib import Path
import logging

from .models import (
    TaskObject, 
    ConstraintNode, 
    TaskMetadata,
    RestatementEvent,
    ConstraintViolationEvent
)

logger = logging.getLogger(__name__)


class TaskManager:
    """
    Manages persistent Task Objects for users.
    
    Storage structure:
    /data/users/{user_id}/tasks/{task_id}.json
    /data/users/{user_id}/active_task.txt  (stores current task ID)
    /data/users/{user_id}/logs/restatements.jsonl
    """
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            # Default to backend/data/users
            base = Path(__file__).parent.parent.parent / "data" / "users"
        else:
            base = Path(data_dir)
        
        self.data_dir = base
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"TaskManager initialized with data_dir: {self.data_dir}")
    
    def _user_dir(self, user_id: str) -> Path:
        """Get or create user's data directory."""
        user_dir = self.data_dir / user_id
        user_dir.mkdir(parents=True, exist_ok=True)
        (user_dir / "tasks").mkdir(exist_ok=True)
        (user_dir / "logs").mkdir(exist_ok=True)
        return user_dir
    
    def _task_path(self, user_id: str, task_id: str) -> Path:
        """Get path to a specific task file."""
        return self._user_dir(user_id) / "tasks" / f"{task_id}.json"
    
    def _active_task_path(self, user_id: str) -> Path:
        """Get path to active task pointer."""
        return self._user_dir(user_id) / "active_task.txt"
    
    # --- CRUD Operations ---
    
    def create_task(
        self, 
        user_id: str, 
        name: str, 
        description: str = None,
        initial_nodes: List[ConstraintNode] = None
    ) -> TaskObject:
        """
        Create a new Task Object.
        Lifecycle: Conception → Materialization
        """
        task = TaskObject(
            user_id=user_id,
            name=name,
            description=description,
            nodes=initial_nodes or [],
            status="active"
        )
        
        # Save to disk
        self._save_task(task)
        
        # Set as active task
        self.set_active_task(user_id, task.id)
        
        logger.info(f"Created task {task.id} for user {user_id}: '{name}'")
        return task
    
    def get_task(self, user_id: str, task_id: str) -> Optional[TaskObject]:
        """Load a task from disk."""
        path = self._task_path(user_id, task_id)
        if not path.exists():
            return None
        
        with open(path, "r") as f:
            data = json.load(f)
        
        return TaskObject(**data)
    
    def list_tasks(self, user_id: str) -> List[TaskObject]:
        """List all tasks for a user."""
        tasks_dir = self._user_dir(user_id) / "tasks"
        tasks = []
        
        for task_file in tasks_dir.glob("*.json"):
            with open(task_file, "r") as f:
                data = json.load(f)
            tasks.append(TaskObject(**data))
        
        # Sort by updated_at descending
        tasks.sort(key=lambda t: t.updated_at, reverse=True)
        return tasks
    
    def get_active_task(self, user_id: str) -> Optional[TaskObject]:
        """Get the currently active task for a user."""
        active_path = self._active_task_path(user_id)
        if not active_path.exists():
            return None
        
        task_id = active_path.read_text().strip()
        return self.get_task(user_id, task_id)
    
    def set_active_task(self, user_id: str, task_id: str) -> bool:
        """Set a task as the active task."""
        task = self.get_task(user_id, task_id)
        if task is None:
            return False
        
        active_path = self._active_task_path(user_id)
        active_path.write_text(task_id)
        
        # Update task metrics
        task.metrics.last_resumed_at = datetime.utcnow()
        task.updated_at = datetime.utcnow()
        self._save_task(task)
        
        logger.info(f"Switched user {user_id} to task {task_id}")
        return True
    
    def update_task(self, task: TaskObject) -> TaskObject:
        """Update a task (saves to disk)."""
        task.updated_at = datetime.utcnow()
        self._save_task(task)
        return task
    
    def _save_task(self, task: TaskObject):
        """Persist task to disk."""
        path = self._task_path(task.user_id, task.id)
        with open(path, "w") as f:
            json.dump(task.model_dump(mode="json"), f, indent=2, default=str)
    
    # --- Lifecycle Operations ---
    
    def suspend_task(self, user_id: str, task_id: str) -> bool:
        """
        Suspend a task.
        Lifecycle: Execution → Suspension
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return False
        
        task.status = "suspended"
        task.metrics.interruption_count += 1
        self.update_task(task)
        
        logger.info(f"Suspended task {task_id}")
        return True
    
    def complete_task(self, user_id: str, task_id: str) -> bool:
        """
        Mark a task as completed.
        Lifecycle: Execution → Completion
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return False
        
        task.status = "completed"
        self.update_task(task)
        
        logger.info(f"Completed task {task_id}")
        return True
    
    def archive_task(self, user_id: str, task_id: str) -> bool:
        """
        Archive a task.
        Lifecycle: Completion → Archive
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return False
        
        task.status = "archived"
        self.update_task(task)
        
        logger.info(f"Archived task {task_id}")
        return True
    
    # --- Node Operations (Pattern 1: Pin to Task) ---
    
    def add_node(
        self, 
        user_id: str, 
        task_id: str, 
        node: ConstraintNode
    ) -> Optional[ConstraintNode]:
        """
        Add a Constraint Node to a Task.
        Implements Pattern 1: Pin to Task
        """
        task = self.get_task(user_id, task_id)
        if task is None:
            return None
        
        task.nodes.append(node)
        self.update_task(task)
        
        logger.info(f"Added node {node.id} to task {task_id}: '{node.label}'")
        return node
    
    def toggle_node_active(
        self, 
        user_id: str, 
        task_id: str, 
        node_id: str,
        active: bool
    ) -> bool:
        """Toggle whether a node is in scope."""
        task = self.get_task(user_id, task_id)
        if task is None:
            return False
        
        for node in task.nodes:
            if node.id == node_id:
                node.active = active
                self.update_task(task)
                return True
        
        return False
    
    # --- Logging (for Evaluation) ---
    
    def log_restatement(self, event: RestatementEvent):
        """Log a restatement event for CUI evaluation."""
        task = self.get_task_by_id(event.task_id)
        if task:
            # Update task metrics
            task.metrics.restatement_count += 1
            self._save_task(task)
        
        # Append to log file
        # Extract user_id from task_id or store it differently
        # For now, we write to a global log
        log_path = self.data_dir / "restatements.jsonl"
        with open(log_path, "a") as f:
            f.write(event.model_dump_json() + "\n")
    
    def log_violation(self, event: ConstraintViolationEvent):
        """Log a constraint violation event."""
        log_path = self.data_dir / "violations.jsonl"
        with open(log_path, "a") as f:
            f.write(event.model_dump_json() + "\n")
    
    def get_task_by_id(self, task_id: str) -> Optional[TaskObject]:
        """Find a task by ID across all users (for logging)."""
        for user_dir in self.data_dir.iterdir():
            if user_dir.is_dir():
                task = self.get_task(user_dir.name, task_id)
                if task:
                    return task
        return None


# Singleton instance
task_manager = TaskManager()
