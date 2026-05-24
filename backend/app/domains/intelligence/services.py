"""
Intelligence Services - AI coordination and orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_

from .models import (
    InferenceStatus,
    ModelProvider,
    PromptType,
    InferenceRequest,
    PromptTemplate,
    ModelSelection,
    GenerationPipeline,
    PipelineExecution,
    AICoordinationLog,
    ProviderHealth,
)

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    """Generation request for AI coordination"""
    prompt: str
    model: str
    provider: ModelProvider
    prompt_type: PromptType = PromptType.CHAT
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResponse:
    """Generation response"""
    content: str
    model: str
    provider: str
    tokens_used: int
    latency_ms: float
    finish_reason: str = "stop"


class InferenceCoordinator:
    """
    Inference coordinator for AI model routing and execution.
    Handles provider failover, load balancing, and inference optimization.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._providers: Dict[str, Dict[str, Any]] = {}
        self._model_configs: Dict[str, Dict[str, Any]] = {}
        self._health_status: Dict[str, ProviderHealth] = {}
        self._running = False
    
    async def initialize(self) -> None:
        """Initialize the inference coordinator"""
        await self._load_provider_health()
        self._running = True
        logger.info("InferenceCoordinator initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the coordinator"""
        self._running = False
        logger.info("InferenceCoordinator shutdown")
    
    async def _load_provider_health(self) -> None:
        """Load provider health status from database"""
        result = await self.db.execute(select(ProviderHealth))
        for health in result.scalars().all():
            self._health_status[health.provider] = health
    
    # ==================== Provider Management ====================
    
    async def register_provider(
        self,
        provider: ModelProvider,
        config: Dict[str, Any],
    ) -> None:
        """Register an AI provider"""
        self._providers[provider.value] = {
            "config": config,
            "api_key": config.get("api_key"),
            "base_url": config.get("base_url"),
            "models": config.get("models", []),
        }
        
        # Create health record
        health = ProviderHealth(
            provider=provider.value,
            status="healthy",
            is_available=True,
            last_check=datetime.utcnow(),
        )
        
        self.db.add(health)
        await self.db.commit()
        
        self._health_status[provider.value] = health
    
    async def get_provider_health(
        self,
        provider: str,
    ) -> Optional[ProviderHealth]:
        """Get provider health status"""
        return self._health_status.get(provider)
    
    async def update_provider_health(
        self,
        provider: str,
        status: str,
        is_available: bool,
        metrics: Optional[Dict[str, float]] = None,
    ) -> ProviderHealth:
        """Update provider health status"""
        health = self._health_status.get(provider)
        
        if not health:
            health = ProviderHealth(
                provider=provider,
                last_check=datetime.utcnow(),
            )
            self.db.add(health)
        
        health.status = status
        health.is_available = is_available
        health.last_check = datetime.utcnow()
        
        if metrics:
            if "avg_latency_ms" in metrics:
                health.avg_latency_ms = metrics["avg_latency_ms"]
            if "success_rate" in metrics:
                health.success_rate = metrics["success_rate"]
            if "requests_per_minute" in metrics:
                health.requests_per_minute = metrics["requests_per_minute"]
        
        self.db.add(health)
        await self.db.commit()
        await self.db.refresh(health)
        
        self._health_status[provider] = health
        
        return health
    
    async def get_available_providers(
        self,
        required_capabilities: Optional[List[str]] = None,
    ) -> List[str]:
        """Get available providers"""
        available = []
        
        for provider, health in self._health_status.items():
            if health.is_available and health.status == "healthy":
                if required_capabilities:
                    # Check if provider supports required capabilities
                    # Placeholder - would check model capabilities
                    available.append(provider)
                else:
                    available.append(provider)
        
        return available
    
    # ==================== Inference Execution ====================
    
    async def execute_inference(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Execute inference request"""
        # Log the request
        await self._log_coordination(
            event_type="inference_request",
            source="coordinator",
            data={
                "model": request.model,
                "provider": request.provider.value,
                "prompt_type": request.prompt_type.value,
            },
        )
        
        # Update health
        await self.update_provider_health(
            request.provider.value,
            status="healthy",
            is_available=True,
        )
        
        # Placeholder - actual implementation would call the provider
        # For now, return simulated response
        return GenerationResponse(
            content=f"Simulated response for: {request.prompt[:50]}...",
            model=request.model,
            provider=request.provider.value,
            tokens_used=100,
            latency_ms=150.0,
        )
    
    async def create_inference_request(
        self,
        request: GenerationRequest,
        correlation_id: Optional[str] = None,
        session_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
    ) -> InferenceRequest:
        """Create and track inference request"""
        inference_req = InferenceRequest(
            request_id=str(uuid4()),
            prompt_type=request.prompt_type.value,
            model=request.model,
            provider=request.provider.value,
            prompt=request.prompt,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            status=InferenceStatus.PENDING.value,
            correlation_id=correlation_id,
            session_id=session_id,
            owner_id=owner_id,
        )
        
        self.db.add(inference_req)
        await self.db.commit()
        await self.db.refresh(inference_req)
        
        return inference_req
    
    # ==================== Model Selection ====================
    
    async def select_model(
        self,
        request_type: str,
        requirements: Dict[str, Any],
    ) -> tuple[str, str]:
        """
        Select optimal model for request.
        Returns (model, provider).
        """
        # Get available providers
        available = await self.get_available_providers()
        
        if not available:
            raise ValueError("No available providers")
        
        # Simple selection based on requirements
        # In production, this would use more sophisticated logic
        model = requirements.get("model", "gpt-4")
        provider = requirements.get("provider", "openai")
        
        # Record selection
        selection = ModelSelection(
            selection_id=str(uuid4()),
            request_type=request_type,
            selected_model=model,
            selected_provider=provider,
            requirements=requirements,
            selection_reason="Based on requirements",
            selected_at=datetime.utcnow(),
        )
        
        self.db.add(selection)
        await self.db.commit()
        
        return model, provider
    
    # ==================== Logging ====================
    
    async def _log_coordination(
        self,
        event_type: str,
        source: str,
        data: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        severity: str = "info",
    ) -> AICoordinationLog:
        """Log AI coordination event"""
        log = AICoordinationLog(
            log_id=str(uuid4()),
            event_type=event_type,
            event_category="ai_coordination",
            source=source,
            source_type="coordinator",
            data=data,
            correlation_id=correlation_id,
            timestamp=datetime.utcnow(),
            severity=severity,
        )
        
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        
        return log


class PromptOrchestrator:
    """
    Prompt orchestration for reusable AI interactions.
    Manages prompt templates, lifecycle, and optimization.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._templates: Dict[str, PromptTemplate] = {}
    
    async def initialize(self) -> None:
        """Initialize the prompt orchestrator"""
        await self._load_templates()
        logger.info("PromptOrchestrator initialized")
    
    async def _load_templates(self) -> None:
        """Load prompt templates from database"""
        result = await self.db.execute(select(PromptTemplate))
        for template in result.scalars().all():
            self._templates[template.name] = template
    
    async def create_template(
        self,
        name: str,
        user_template: str,
        template_type: str = "completion",
        system_template: Optional[str] = None,
        variables: Optional[List[str]] = None,
        recommended_model: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> PromptTemplate:
        """Create a prompt template"""
        # Identify required variables
        import re
        required = re.findall(r'\{(\w+)\}', user_template)
        
        template = PromptTemplate(
            name=name,
            template_type=template_type,
            user_template=user_template,
            system_template=system_template,
            variables=variables or [],
            required_variables=required,
            recommended_model=recommended_model,
            owner_id=owner_id,
        )
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        self._templates[name] = template
        
        return template
    
    async def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name"""
        return self._templates.get(name)
    
    async def render_template(
        self,
        name: str,
        variables: Dict[str, Any],
    ) -> tuple[str, Optional[str]]:
        """Render prompt template with variables"""
        template = self._templates.get(name)
        
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        # Check required variables
        missing = [v for v in (template.required_variables or []) if v not in variables]
        if missing:
            raise ValueError(f"Missing required variables: {missing}")
        
        # Render user template
        user_prompt = template.user_template
        for key, value in variables.items():
            user_prompt = user_prompt.replace(f"{{{key}}}", str(value))
        
        # Render system template
        system_prompt = None
        if template.system_template:
            system_prompt = template.system_template
            for key, value in variables.items():
                system_prompt = system_prompt.replace(f"{{{key}}}", str(value))
        
        # Update usage
        template.usage_count += 1
        self.db.add(template)
        await self.db.commit()
        
        return user_prompt, system_prompt
    
    async def update_template_stats(
        self,
        name: str,
        success: bool,
        latency_ms: float,
    ) -> PromptTemplate:
        """Update template usage statistics"""
        template = self._templates.get(name)
        
        if not template:
            raise ValueError(f"Template not found: {name}")
        
        # Update success rate
        if template.success_rate is None:
            template.success_rate = 1.0 if success else 0.0
        else:
            # Exponential moving average
            template.success_rate = template.success_rate * 0.9 + (1.0 if success else 0.0) * 0.1
        
        # Update avg latency
        if template.avg_latency_ms is None:
            template.avg_latency_ms = latency_ms
        else:
            template.avg_latency_ms = template.avg_latency_ms * 0.9 + latency_ms * 0.1
        
        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)
        
        return template


class GenerationPipelineOrchestrator:
    """
    Generation pipeline orchestrator for multi-step AI workflows.
    Manages pipeline execution and step coordination.
    """
    
    def __init__(self, db: AsyncSession, inference_coordinator: InferenceCoordinator):
        self.db = db
        self.inference_coordinator = inference_coordinator
        self._pipelines: Dict[str, GenerationPipeline] = {}
    
    async def initialize(self) -> None:
        """Initialize the pipeline orchestrator"""
        await self._load_pipelines()
        logger.info("GenerationPipelineOrchestrator initialized")
    
    async def _load_pipelines(self) -> None:
        """Load pipelines from database"""
        result = await self.db.execute(select(GenerationPipeline))
        for pipeline in result.scalars().all():
            self._pipelines[pipeline.name] = pipeline
    
    async def create_pipeline(
        self,
        name: str,
        pipeline_type: str,
        steps: List[Dict[str, Any]],
        description: Optional[str] = None,
        owner_id: Optional[UUID] = None,
    ) -> GenerationPipeline:
        """Create a generation pipeline"""
        pipeline = GenerationPipeline(
            name=name,
            description=description,
            pipeline_type=pipeline_type,
            steps=steps,
            owner_id=owner_id,
        )
        
        self.db.add(pipeline)
        await self.db.commit()
        await self.db.refresh(pipeline)
        
        self._pipelines[name] = pipeline
        
        return pipeline
    
    async def execute_pipeline(
        self,
        pipeline_name: str,
        input_data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> PipelineExecution:
        """Execute a generation pipeline"""
        pipeline = self._pipelines.get(pipeline_name)
        
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
        
        execution = PipelineExecution(
            pipeline_id=pipeline.id,
            execution_id=str(uuid4()),
            input_data=input_data,
            status=InferenceStatus.PENDING.value,
            total_steps=len(pipeline.steps or []),
            correlation_id=correlation_id,
        )
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        # Execute steps
        step_results = []
        current_data = input_data
        execution.started_at = datetime.utcnow()
        execution.status = InferenceStatus.RUNNING.value
        self.db.add(execution)
        await self.db.commit()
        
        try:
            for i, step in enumerate(pipeline.steps or []):
                step_type = step.get("type")
                step_config = step.get("config", {})
                
                # Execute step
                result = await self._execute_pipeline_step(
                    step_type, step_config, current_data
                )
                
                step_results.append(result)
                current_data.update(result.get("output", {}))
                execution.completed_steps = i + 1
                
                self.db.add(execution)
                await self.db.commit()
            
            # Success
            execution.status = InferenceStatus.COMPLETED.value
            execution.output_data = current_data
            execution.step_results = step_results
            execution.completed_at = datetime.utcnow()
            execution.total_duration_ms = (
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            
        except Exception as e:
            logger.error(f"Pipeline execution error: {e}")
            execution.status = InferenceStatus.FAILED.value
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
        
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)
        
        return execution
    
    async def _execute_pipeline_step(
        self,
        step_type: str,
        config: Dict[str, Any],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a single pipeline step"""
        if step_type == "generate":
            # AI generation step
            request = GenerationRequest(
                prompt=config.get("prompt", "").format(**data),
                model=config.get("model", "gpt-4"),
                provider=ModelProvider(config.get("provider", "openai")),
                prompt_type=PromptType(config.get("prompt_type", "completion")),
                system_prompt=config.get("system_prompt"),
            )
            
            response = await self.inference_coordinator.execute_inference(request)
            
            return {
                "step_type": step_type,
                "output": {"generated": response.content},
            }
        
        elif step_type == "transform":
            # Data transformation step
            return {
                "step_type": step_type,
                "output": {"transformed": data},
            }
        
        elif step_type == "condition":
            # Conditional step
            return {
                "step_type": step_type,
                "output": {"condition_met": True},
            }
        
        return {"step_type": step_type, "output": {}}