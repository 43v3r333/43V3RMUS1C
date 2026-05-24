"""
AI Worker Tasks - AI inference and generation tasks
"""
import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from celery import Task
from celery.utils.log import get_task_logger

from .celery_app import celery_app
from ..core.config import settings
from ..domains.ai_runtime import (
    AIOrchestrator,
    get_ai_orchestrator,
    OpenAIAdapter,
    AnthropicAdapter,
    GenerationRequest,
    GenerationConfig,
    ChatMessage,
    ChatRequest,
    PromptTemplate,
)

logger = get_task_logger(__name__)


class AITask(Task):
    """Base task for AI processing"""
    _orchestrator: Optional[AIOrchestrator] = None
    
    @property
    def orchestrator(self) -> AIOrchestrator:
        if self._orchestrator is None:
            self._orchestrator = get_ai_orchestrator()
        return self._orchestrator


@celery_app.task(bind=True, base=AITask, name="ai.generate")
async def ai_generate(
    self,
    prompt: str,
    model: str = "gpt-4",
    provider: Optional[str] = None,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate text using AI model.
    """
    logger.info(f"AI generation request: model={model}, provider={provider}")
    
    try:
        # Get or initialize orchestrator
        orchestrator = get_ai_orchestrator()
        
        # Initialize providers if needed
        if not orchestrator._configured:
            await orchestrator.initialize(
                openai_key=settings.openai_api_key or None,
                anthropic_key=settings.anthropic_api_key or None,
            )
        
        # Execute generation
        config = GenerationConfig(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        response = await orchestrator.generate(
            prompt=prompt,
            model=model,
            provider=provider,
            system_prompt=system_prompt,
            config=config,
        )
        
        return {
            "success": True,
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
            "tokens_used": response.tokens_used,
            "finish_reason": response.finish_reason,
            "metadata": response.metadata,
        }
        
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=AITask, name="ai.chat")
async def ai_chat(
    self,
    messages: List[Dict[str, str]],
    model: str = "gpt-4",
    provider: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> Dict[str, Any]:
    """
    Generate chat completion.
    """
    logger.info(f"AI chat request: model={model}")
    
    try:
        orchestrator = get_ai_orchestrator()
        
        if not orchestrator._configured:
            await orchestrator.initialize(
                openai_key=settings.openai_api_key or None,
                anthropic_key=settings.anthropic_api_key or None,
            )
        
        response = await orchestrator.chat(
            messages=messages,
            model=model,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        return {
            "success": True,
            "content": response.content,
            "model": response.model,
            "provider": response.provider,
            "tokens_used": response.tokens_used,
            "finish_reason": response.finish_reason,
        }
        
    except Exception as e:
        logger.error(f"AI chat error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=AITask, name="ai.generate_media_script")
async def generate_media_script(
    self,
    media_type: str,
    duration: float,
    style: str,
    parameters: Optional[Dict] = None,
) -> Dict[str, Any]:
    """
    Generate media script/description for AI processing.
    """
    logger.info(f"Generating media script: type={media_type}, duration={duration}s")
    
    try:
        orchestrator = get_ai_orchestrator()
        
        if not orchestrator._configured:
            await orchestrator.initialize(
                openai_key=settings.openai_api_key or None,
            )
        
        prompt = f"""Generate a detailed script for a {media_type} piece with the following specifications:
- Duration: {duration} seconds
- Style: {style}
- Additional parameters: {parameters or {}}

Include:
1. Scene descriptions
2. Key moments and transitions
3. Audio cues and music style
4. Visual composition notes
5. Pacing and rhythm guidance
"""
        
        response = await orchestrator.generate(
            prompt=prompt,
            model="gpt-4",
            system_prompt="You are an expert media producer and creative director. Generate detailed, actionable scripts for media production.",
        )
        
        return {
            "success": True,
            "script": response.content,
            "media_type": media_type,
            "duration": duration,
            "style": style,
        }
        
    except Exception as e:
        logger.error(f"Media script generation error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=AITask, name="ai.analyze_content")
async def analyze_content(
    self,
    content: str,
    analysis_type: str = "general",
) -> Dict[str, Any]:
    """
    Analyze content and extract insights.
    """
    logger.info(f"Analyzing content: type={analysis_type}")
    
    try:
        orchestrator = get_ai_orchestrator()
        
        if not orchestrator._configured:
            await orchestrator.initialize(
                openai_key=settings.openai_api_key or None,
            )
        
        analysis_prompts = {
            "structure": "Analyze the structure and organization of this content.",
            "emotion": "Analyze the emotional tone and impact of this content.",
            "keywords": "Extract key themes, topics, and keywords from this content.",
            "quality": "Assess the quality, clarity, and effectiveness of this content.",
        }
        
        prompt = f"{analysis_prompts.get(analysis_type, analysis_prompts['general'])}\n\nContent:\n{content[:5000]}"
        
        response = await orchestrator.generate(
            prompt=prompt,
            model="gpt-4",
            system_prompt="You are an expert content analyst.",
        )
        
        return {
            "success": True,
            "analysis": response.content,
            "analysis_type": analysis_type,
        }
        
    except Exception as e:
        logger.error(f"Content analysis error: {e}")
        return {
            "success": False,
            "error": str(e),
        }


@celery_app.task(bind=True, base=AITask, name="ai.batch_generate")
async def batch_generate(
    self,
    prompts: List[str],
    model: str = "gpt-3.5-turbo",
    provider: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate multiple responses in batch.
    """
    logger.info(f"Batch generation: {len(prompts)} prompts")
    
    results = []
    errors = []
    
    for i, prompt in enumerate(prompts):
        try:
            response = await ai_generate.delay(
                prompt=prompt,
                model=model,
                provider=provider,
            )
            results.append(response.get())
        except Exception as e:
            errors.append({"index": i, "error": str(e)})
    
    return {
        "success": len(errors) == 0,
        "total": len(prompts),
        "completed": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors,
    }


@celery_app.task(bind=True, base=AITask, name="ai.health_check")
async def ai_health_check(self) -> Dict[str, Any]:
    """
    Health check for AI worker.
    """
    orchestrator = get_ai_orchestrator()
    
    return {
        "status": "healthy",
        "worker_type": "ai",
        "providers": list(orchestrator._adapters.keys()) if orchestrator._configured else [],
    }