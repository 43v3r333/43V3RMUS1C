"""
Workflow and job repository
"""
from typing import Optional, List
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.workflow import RenderJob, Workflow, AutomationJob, AIPrompt
from .base import BaseRepository


class RenderJobRepository(BaseRepository[RenderJob]):
    """Render job repository"""
    
    def __init__(self, db: Session):
        super().__init__(RenderJob, db)
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[RenderJob]:
        """Get jobs by status"""
        return self.db.query(RenderJob).filter(
            RenderJob.status == status,
            RenderJob.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_type(self, job_type: str, skip: int = 0, limit: int = 20) -> List[RenderJob]:
        """Get jobs by type"""
        return self.db.query(RenderJob).filter(
            RenderJob.job_type == job_type,
            RenderJob.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_project(self, project_id: UUID, skip: int = 0, limit: int = 20) -> List[RenderJob]:
        """Get jobs by project"""
        return self.db.query(RenderJob).filter(
            RenderJob.project_id == project_id,
            RenderJob.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_pending(self, limit: int = 20) -> List[RenderJob]:
        """Get pending jobs for processing"""
        return self.db.query(RenderJob).filter(
            RenderJob.status.in_(["pending", "queued"]),
            RenderJob.deleted_at.is_(None)
        ).order_by(RenderJob.priority.desc(), RenderJob.created_at).limit(limit).all()
    
    def get_by_worker(self, worker_id: str, skip: int = 0, limit: int = 20) -> List[RenderJob]:
        """Get jobs by worker"""
        return self.db.query(RenderJob).filter(
            RenderJob.worker_id == worker_id,
            RenderJob.status == "processing",
            RenderJob.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class WorkflowRepository(BaseRepository[Workflow]):
    """Workflow repository"""
    
    def __init__(self, db: Session):
        super().__init__(Workflow, db)
    
    def get_by_type(self, workflow_type: str, skip: int = 0, limit: int = 20) -> List[Workflow]:
        """Get workflows by type"""
        return self.db.query(Workflow).filter(
            Workflow.workflow_type == workflow_type,
            Workflow.is_active == True,
            Workflow.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_public(self, skip: int = 0, limit: int = 20) -> List[Workflow]:
        """Get public workflows"""
        return self.db.query(Workflow).filter(
            Workflow.is_public == True,
            Workflow.is_active == True,
            Workflow.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_creator(self, created_by_id: UUID, skip: int = 0, limit: int = 20) -> List[Workflow]:
        """Get workflows by creator"""
        return self.db.query(Workflow).filter(
            Workflow.created_by_id == created_by_id,
            Workflow.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()


class AutomationJobRepository(BaseRepository[AutomationJob]):
    """Automation job repository"""
    
    def __init__(self, db: Session):
        super().__init__(AutomationJob, db)
    
    def get_by_status(self, status: str, skip: int = 0, limit: int = 20) -> List[AutomationJob]:
        """Get jobs by status"""
        return self.db.query(AutomationJob).filter(
            AutomationJob.status == status,
            AutomationJob.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_workflow(self, workflow_id: UUID, skip: int = 0, limit: int = 20) -> List[AutomationJob]:
        """Get jobs by workflow"""
        return self.db.query(AutomationJob).filter(
            AutomationJob.workflow_id == workflow_id,
            AutomationJob.deleted_at.is_(None)
        ).order_by(AutomationJob.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_recent(self, limit: int = 20) -> List[AutomationJob]:
        """Get recent jobs"""
        return self.db.query(AutomationJob).filter(
            AutomationJob.deleted_at.is_(None)
        ).order_by(AutomationJob.created_at.desc()).limit(limit).all()


class AIPromptRepository(BaseRepository[AIPrompt]):
    """AI Prompt repository"""
    
    def __init__(self, db: Session):
        super().__init__(AIPrompt, db)
    
    def get_by_type(self, prompt_type: str, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Get prompts by type"""
        return self.db.query(AIPrompt).filter(
            AIPrompt.prompt_type == prompt_type,
            AIPrompt.is_active == True,
            AIPrompt.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_public(self, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Get public prompts"""
        return self.db.query(AIPrompt).filter(
            AIPrompt.is_public == True,
            AIPrompt.is_active == True,
            AIPrompt.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_category(self, category: str, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Get prompts by category"""
        return self.db.query(AIPrompt).filter(
            AIPrompt.category == category,
            AIPrompt.is_active == True,
            AIPrompt.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def get_by_creator(self, created_by_id: UUID, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Get prompts by creator"""
        return self.db.query(AIPrompt).filter(
            AIPrompt.created_by_id == created_by_id,
            AIPrompt.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[AIPrompt]:
        """Search prompts by name"""
        return self.db.query(AIPrompt).filter(
            AIPrompt.name.ilike(f"%{query}%"),
            AIPrompt.is_active == True,
            AIPrompt.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def increment_use_count(self, prompt_id: UUID) -> None:
        """Increment prompt use count"""
        self.db.query(AIPrompt).filter(AIPrompt.id == prompt_id).update(
            {AIPrompt.use_count: AIPrompt.use_count + 1}
        )
        self.db.commit()