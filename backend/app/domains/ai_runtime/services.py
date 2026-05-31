"""
AI Runtime Engine - AI orchestration and agent management
"""
import logging
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID
from datetime import datetime
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .models import (
    TaskStatus,
    TaskPriority,
    ModelProvider,
    AIContext,
    AIResponse,
    AITask,
)

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    """Model configuration"""
    model: str
    provider: ModelProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096


class AIRuntimeEngine:
    """
    AI Runtime Engine for AI task orchestration.
    Manages AI tasks, model routing, context management,
    and response handling.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._model_configs: Dict[str, ModelConfig] = {}
        self._default_config = ModelConfig(
            model="gpt-4",
            provider=ModelProvider.OPENAI,
            temperature=0.7,
            max_tokens=4096,
        )
        self._register_default_models()
    
    def _register_default_models(self):
        """Register default model configurations"""
        self._model_configs["gpt-4"] = ModelConfig(
            model="gpt-4",
            provider=ModelProvider.OPENAI,
        )
        self._model_configs["gpt-3.5-turbo"] = ModelConfig(
            model="gpt-3.5-turbo",
            provider=ModelProvider.OPENAI,
        )
        self._model_configs["claude-3-opus"] = ModelConfig(
            model="claude-3-opus-20240229",
            provider=ModelProvider.ANTHROPIC,
        )
        self._model_configs["claude-3-sonnet"] = ModelConfig(
            model="claude-3-sonnet-20240229",
            provider=ModelProvider.ANTHROPIC,
        )
    
    def register_model(self, name: str, config: ModelConfig):
        """Register a model configuration"""
        self._model_configs[name] = config
    
    def get_model_config(self, model_name: str) -> ModelConfig:
        """Get model configuration"""
        return self._model_configs.get(model_name, self._default_config)
    
    # ==================== Task Operations ====================
    
    async def create_task(
        self,
        name: str,
        task_type: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[AIContext] = None,
        model: str = "gpt-4",
        priority: TaskPriority = TaskPriority.NORMAL,
        owner_id: Optional[UUID] = None,
        project_id: Optional[UUID] = None,
    ) -> AITask:
        """Create a new AI task"""
        task = AITask(
            name=name,
            task_type=task_type,
            prompt=prompt,
            system_prompt=system_prompt,
            context=context.__dict__ if context else None,
            model=model,
            provider=ModelProvider.OPENAI.value,
            priority=priority.value,
            status=TaskStatus.PENDING.value,
            owner_id=owner_id,
            project_id=project_id,
            queued_at=datetime.utcnow(),
        )
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def get_task(self, task_id: UUID) -> Optional[AITask]:
        """Get task by ID"""
        result = await self.db.execute(
            select(AITask).where(AITask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def update_task_status(
        self,
        task: AITask,
        status: TaskStatus,
        **kwargs,
    ) -> AITask:
        """Update task status"""
        task.status = status.value
        
        if status == TaskStatus.RUNNING:
            task.started_at = datetime.utcnow()
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED):
            task.completed_at = datetime.utcnow()
        
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    async def cancel_task(self, task: AITask) -> AITask:
        """Cancel a task"""
        return await self.update_task_status(task, TaskStatus.CANCELLED)
    
    async def retry_task(self, task: AITask) -> AITask:
        """Retry a failed task"""
        if task.retry_count >= task.max_retries:
            raise ValueError("Max retries exceeded")
        
        task.retry_count += 1
        task.status = TaskStatus.QUEUED.value
        task.error_message = None
        task.queued_at = datetime.utcnow()
        
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        
        return task
    
    # ==================== Execution ====================
    
    async def execute_task(
        self,
        task: AITask,
        llm_callable: Optional[Callable] = None,
    ) -> AIResponse:
        """Execute an AI task"""
        try:
            # Update status
            await self.update_task_status(task, TaskStatus.RUNNING)
            
            # Build context
            context_dict = task.context or {}
            system_prompt = task.system_prompt or ""
            
            # Prepare prompt
            full_prompt = f"{system_prompt}\n\n{task.prompt}" if system_prompt else task.prompt
            
            # Get model config
            model_config = self.get_model_config(task.model)
            
            # Execute with LLM (placeholder - actual implementation would call the LLM API)
            if llm_callable:
                response = await llm_callable(
                    prompt=full_prompt,
                    model=task.model,
                    temperature=model_config.temperature,
                    max_tokens=model_config.max_tokens,
                )
            else:
                # Simulated response for development
                response = AIResponse(
                    content=f"Simulated response for: {task.name}",
                    model=task.model,
                    tokens_used=100,
                    finish_reason="stop",
                )
            
            # Update task with response
            task.response = response.content
            task.tokens_used = response.tokens_used
            task.response_metadata = response.metadata
            
            await self.update_task_status(task, TaskStatus.COMPLETED)
            
            return response
            
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            task.error_message = str(e)
            await self.update_task_status(task, TaskStatus.FAILED)
            raise
    
    async def execute_batch(
        self,
        tasks: List[AITask],
        llm_callable: Optional[Callable] = None,
    ) -> List[AIResponse]:
        """Execute multiple tasks"""
        responses = []
        
        for task in tasks:
            try:
                response = await self.execute_task(task, llm_callable)
                responses.append(response)
            except Exception as e:
                logger.error(f"Batch task error: {e}")
                responses.append(AIResponse(
                    content="",
                    model=task.model,
                    tokens_used=0,
                    finish_reason="error",
                    metadata={"error": str(e)},
                ))
        
        return responses
    
    # ==================== Task Queue ====================
    
    async def get_queued_tasks(
        self,
        limit: int = 100,
    ) -> List[AITask]:
        """Get queued tasks by priority"""
        result = await self.db.execute(
            select(AITask)
            .where(AITask.status == TaskStatus.QUEUED.value)
            .order_by(
                # Order by priority (critical first)
                AITask.priority.desc(),
                # Then by queued time
                AITask.queued_at
            )
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_tasks_by_status(
        self,
        status: TaskStatus,
        limit: int = 100,
    ) -> List[AITask]:
        """Get tasks by status"""
        result = await self.db.execute(
            select(AITask)
            .where(AITask.status == status.value)
            .order_by(AITask.queued_at)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    # ==================== Statistics ====================
    
    async def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        stats = {}
        
        for status in TaskStatus:
            result = await self.db.execute(
                select(AITask).where(AITask.status == status.value)
            )
            stats[status.value] = len(list(result.scalars().all()))
        
        total_tokens = await self.db.execute(
            select(AITask.tokens_used).where(
                AITask.status == TaskStatus.COMPLETED.value
            )
        )
        total = sum(t for t in total_tokens.scalars().all() if t)
        
        return {
            "by_status": stats,
            "total_tokens_used": total,
        }