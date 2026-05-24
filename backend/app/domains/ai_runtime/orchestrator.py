"""
AI Orchestrator - Unified AI generation orchestration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field

from .adapters import (
    AIModelAdapter,
    OpenAIAdapter,
    AnthropicAdapter,
    LocalAdapter,
    GenerationRequest,
    GenerationResponse,
    ChatRequest,
    GenerationConfig,
    AdapterCapability,
)
from .registry import ProviderRegistry, ModelRegistry

logger = logging.getLogger(__name__)


@dataclass
class GenerationPipeline:
    """Pipeline for AI generation steps"""
    name: str
    steps: List[Dict[str, Any]]
    config: Optional[Dict[str, Any]] = None


@dataclass
class PromptTemplate:
    """Template for prompts"""
    name: str
    system_template: str
    user_template: str
    variables: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIOrchestrator:
    """
    Unified AI orchestration layer.
    Provides consistent interface for AI operations across providers.
    """
    
    def __init__(self):
        self._registry = ProviderRegistry()
        self._model_registry = ModelRegistry()
        self._adapters: Dict[str, AIModelAdapter] = {}
        self._prompt_templates: Dict[str, PromptTemplate] = {}
        self._pipelines: Dict[str, GenerationPipeline] = {}
        self._configured = False
    
    async def initialize(
        self,
        openai_key: Optional[str] = None,
        anthropic_key: Optional[str] = None,
        local_url: Optional[str] = None,
    ) -> None:
        """Initialize AI orchestrator with providers"""
        # Initialize adapters
        if openai_key:
            openai_adapter = OpenAIAdapter(api_key=openai_key)
            await openai_adapter.initialize()
            self._adapters["openai"] = openai_adapter
            self._registry.register("openai", openai_adapter)
        
        if anthropic_key:
            anthropic_adapter = AnthropicAdapter(api_key=anthropic_key)
            await anthropic_adapter.initialize()
            self._adapters["anthropic"] = anthropic_adapter
            self._registry.register("anthropic", anthropic_adapter)
        
        if local_url:
            local_adapter = LocalAdapter(base_url=local_url)
            await local_adapter.initialize()
            self._adapters["local"] = local_adapter
            self._registry.register("local", local_adapter)
        
        # Register models
        for provider, adapter in self._adapters.items():
            for model in adapter.models:
                self._model_registry.register(
                    model_id=model,
                    provider=provider,
                    capabilities=list(adapter.capabilities),
                )
        
        self._configured = True
        logger.info(f"AI Orchestrator initialized with providers: {list(self._adapters.keys())}")
    
    def get_adapter(self, provider: str) -> Optional[AIModelAdapter]:
        """Get adapter by provider"""
        return self._adapters.get(provider)
    
    def get_provider_for_model(self, model: str) -> Optional[str]:
        """Get provider for a model"""
        return self._model_registry.get_provider(model)
    
    async def generate(
        self,
        prompt: str,
        model: str,
        provider: Optional[str] = None,
        system_prompt: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
        **kwargs,
    ) -> GenerationResponse:
        """Generate text with automatic provider selection"""
        provider = provider or self.get_provider_for_model(model)
        
        if not provider:
            raise ValueError(f"No provider found for model: {model}")
        
        adapter = self.get_adapter(provider)
        if not adapter:
            raise ValueError(f"Adapter not found for provider: {provider}")
        
        request = GenerationRequest(
            prompt=prompt,
            system_prompt=system_prompt,
            config=config,
        )
        
        return await adapter.generate(request)
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str,
        provider: Optional[str] = None,
        **kwargs,
    ) -> GenerationResponse:
        """Generate chat completion"""
        from .adapters import ChatMessage
        
        provider = provider or self.get_provider_for_model(model)
        
        if not provider:
            raise ValueError(f"No provider found for model: {model}")
        
        adapter = self.get_adapter(provider)
        if not adapter:
            raise ValueError(f"Adapter not found for provider: {provider}")
        
        chat_messages = [
            ChatMessage(role=m["role"], content=m["content"])
            for m in messages
        ]
        
        request = ChatRequest(
            messages=chat_messages,
            model=model,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 4096),
        )
        
        return await adapter.chat(request)
    
    # ==================== Prompt Templates ====================
    
    def register_prompt_template(
        self,
        template: PromptTemplate,
    ) -> None:
        """Register a prompt template"""
        self._prompt_templates[template.name] = template
    
    def get_prompt_template(self, name: str) -> Optional[PromptTemplate]:
        """Get prompt template by name"""
        return self._prompt_templates.get(name)
    
    def render_prompt(
        self,
        template_name: str,
        variables: Dict[str, Any],
    ) -> tuple[str, str]:
        """Render a prompt template with variables"""
        template = self._prompt_templates.get(template_name)
        if not template:
            raise ValueError(f"Template not found: {template_name}")
        
        # Check required variables
        missing = [v for v in template.variables if v not in variables]
        if missing:
            raise ValueError(f"Missing template variables: {missing}")
        
        system_prompt = template.system_template
        user_prompt = template.user_template
        
        # Replace variables
        for key, value in variables.items():
            system_prompt = system_prompt.replace(f"{{{key}}}", str(value))
            user_prompt = user_prompt.replace(f"{{{key}}}", str(value))
        
        return system_prompt, user_prompt
    
    # ==================== Generation Pipelines ====================
    
    def register_pipeline(
        self,
        pipeline: GenerationPipeline,
    ) -> None:
        """Register a generation pipeline"""
        self._pipelines[pipeline.name] = pipeline
    
    async def execute_pipeline(
        self,
        pipeline_name: str,
        initial_input: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute a generation pipeline"""
        pipeline = self._pipelines.get(pipeline_name)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_name}")
        
        context = context or {}
        step_results = {}
        
        for step in pipeline.steps:
            step_type = step.get("type")
            step_config = step.get("config", {})
            
            if step_type == "generate":
                model = step_config.get("model")
                provider = step_config.get("provider")
                
                prompt = self._render_step_prompt(step_config, context, step_results)
                system_prompt = step_config.get("system_prompt", "")
                
                response = await self.generate(
                    prompt=prompt,
                    model=model,
                    provider=provider,
                    system_prompt=system_prompt,
                )
                
                step_results[step.get("name", step_type)] = response.content
                
            elif step_type == "transform":
                transform_type = step_config.get("transform_type")
                
                if transform_type == "extract":
                    pattern = step_config.get("pattern")
                    source = step_config.get("source")
                    
                    import re
                    input_text = step_results.get(source, "")
                    matches = re.findall(pattern, input_text)
                    step_results[step.get("name", step_type)] = matches
                
                elif transform_type == "join":
                    sources = step_config.get("sources", [])
                    separator = step_config.get("separator", "\n")
                    step_results[step.get("name", step_type)] = separator.join(
                        str(step_results.get(s, "")) for s in sources
                    )
            
            elif step_type == "condition":
                condition = step_config.get("condition")
                if_result = step_config.get("if")
                else_result = step_config.get("else")
                
                # Simple condition evaluation
                if self._evaluate_condition(condition, step_results):
                    step_results[step.get("name", step_type)] = if_result
                else:
                    step_results[step.get("name", step_type)] = else_result
        
        return step_results
    
    def _render_step_prompt(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any],
        results: Dict[str, Any],
    ) -> str:
        """Render prompt for a step"""
        prompt_template = config.get("prompt")
        
        # Replace context variables
        for key, value in context.items():
            prompt_template = prompt_template.replace(f"{{{key}}}", str(value))
        
        # Replace result references
        for key, value in results.items():
            prompt_template = prompt_template.replace(f"{{result.{key}}}", str(value))
        
        return prompt_template
    
    def _evaluate_condition(
        self,
        condition: Dict[str, Any],
        results: Dict[str, Any],
    ) -> bool:
        """Evaluate a condition"""
        operator = condition.get("operator")
        left = condition.get("left")
        right = condition.get("right")
        
        # Resolve left value
        if isinstance(left, str) and left.startswith("result."):
            left = results.get(left.replace("result.", ""), "")
        
        # Resolve right value
        if isinstance(right, str) and right.startswith("result."):
            right = results.get(right.replace("result.", ""), "")
        
        if operator == "equals":
            return left == right
        elif operator == "contains":
            return right in str(left)
        elif operator == "greater_than":
            return float(left) > float(right)
        elif operator == "less_than":
            return float(left) < float(right)
        
        return False
    
    # ==================== Health & Stats ====================
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        return {
            "status": "healthy" if self._configured else "not_initialized",
            "providers": list(self._adapters.keys()),
            "models": len(self._model_registry.list_models()),
            "templates": len(self._prompt_templates),
            "pipelines": len(self._pipelines),
        }
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        stats = {}
        for provider, adapter in self._adapters.items():
            stats[provider] = {
                "configured": True,
                "models": adapter.models,
                "capabilities": list(adapter.capabilities),
            }
        return stats


# Global orchestrator instance
_orchestrator: Optional[AIOrchestrator] = None


def get_ai_orchestrator() -> AIOrchestrator:
    """Get or create global AI orchestrator"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator