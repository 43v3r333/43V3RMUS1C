"""
Provider and Model Registry - AI provider and model management
"""
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum

from .adapters import AIModelAdapter, AdapterCapability


class ModelCapability(str, Enum):
    """Model capabilities"""
    TEXT = "text"
    CODE = "code"
    IMAGES = "images"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"
    FUNCTION_CALLING = "function_calling"
    LONG_CONTEXT = "long_context"
    FAST = "fast"
    REASONING = "reasoning"


@dataclass
class ModelInfo:
    """Information about a model"""
    model_id: str
    provider: str
    display_name: str
    description: str
    capabilities: Set[ModelCapability] = field(default_factory=set)
    context_window: int = 0
    max_output_tokens: int = 0
    supported_features: List[str] = field(default_factory=list)
    pricing: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderInfo:
    """Information about a provider"""
    name: str
    display_name: str
    description: str
    website: Optional[str] = None
    status: str = "active"
    rate_limits: Optional[Dict[str, int]] = None
    capabilities: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProviderRegistry:
    """
    Registry for AI providers.
    Manages provider configurations and availability.
    """
    
    def __init__(self):
        self._providers: Dict[str, AIModelAdapter] = {}
        self._provider_info: Dict[str, ProviderInfo] = {}
    
    def register(self, name: str, adapter: AIModelAdapter) -> None:
        """Register a provider"""
        self._providers[name] = adapter
        self._provider_info[name] = ProviderInfo(
            name=name,
            display_name=name.capitalize(),
            description=f"{name} provider",
            capabilities=set(str(c) for c in adapter.capabilities),
        )
    
    def unregister(self, name: str) -> None:
        """Unregister a provider"""
        if name in self._providers:
            del self._providers[name]
        if name in self._provider_info:
            del self._provider_info[name]
    
    def get(self, name: str) -> Optional[AIModelAdapter]:
        """Get provider by name"""
        return self._providers.get(name)
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self._providers.keys())
    
    def get_info(self, name: str) -> Optional[ProviderInfo]:
        """Get provider information"""
        return self._provider_info.get(name)
    
    def list_provider_infos(self) -> List[ProviderInfo]:
        """List all provider information"""
        return list(self._provider_info.values())
    
    def is_available(self, name: str) -> bool:
        """Check if provider is available"""
        adapter = self._providers.get(name)
        return adapter is not None and adapter._configured
    
    def get_capabilities(self, name: str) -> Set[AdapterCapability]:
        """Get provider capabilities"""
        adapter = self._providers.get(name)
        return adapter.capabilities if adapter else set()


class ModelRegistry:
    """
    Registry for AI models.
    Manages model configurations and capabilities.
    """
    
    def __init__(self):
        self._models: Dict[str, ModelInfo] = {}
        self._provider_models: Dict[str, List[str]] = {}
        self._default_models: Dict[str, str] = {}
        self._model_aliases: Dict[str, str] = {}
        
        self._register_builtin_models()
    
    def _register_builtin_models(self) -> None:
        """Register built-in model definitions"""
        # OpenAI models
        self.register_model(ModelInfo(
            model_id="gpt-4",
            provider="openai",
            display_name="GPT-4",
            description="Most capable GPT model for complex tasks",
            capabilities={ModelCapability.TEXT, ModelCapability.REASONING},
            context_window=128000,
            max_output_tokens=8192,
            supported_features=["json_mode", "function_calling"],
            pricing={"input": 0.03, "output": 0.06},
        ))
        
        self.register_model(ModelInfo(
            model_id="gpt-4-turbo",
            provider="openai",
            display_name="GPT-4 Turbo",
            description="Faster GPT-4 with 128K context",
            capabilities={ModelCapability.TEXT, ModelCapability.REASONING, ModelCapability.FAST},
            context_window=128000,
            max_output_tokens=4096,
            supported_features=["json_mode", "function_calling"],
            pricing={"input": 0.01, "output": 0.03},
        ))
        
        self.register_model(ModelInfo(
            model_id="gpt-3.5-turbo",
            provider="openai",
            display_name="GPT-3.5 Turbo",
            description="Fast and efficient chat model",
            capabilities={ModelCapability.TEXT, ModelCapability.FAST},
            context_window=16385,
            max_output_tokens=4096,
            supported_features=["json_mode", "function_calling"],
            pricing={"input": 0.0005, "output": 0.0015},
        ))
        
        # Anthropic models
        self.register_model(ModelInfo(
            model_id="claude-3-opus-20240229",
            provider="anthropic",
            display_name="Claude 3 Opus",
            description="Most capable Claude model",
            capabilities={ModelCapability.TEXT, ModelCapability.REASONING, ModelCapability.LONG_CONTEXT},
            context_window=200000,
            max_output_tokens=4096,
            supported_features=["vision", "thinking"],
            pricing={"input": 0.015, "output": 0.075},
        ))
        
        self.register_model(ModelInfo(
            model_id="claude-3-sonnet-20240229",
            provider="anthropic",
            display_name="Claude 3 Sonnet",
            description="Balanced performance and speed",
            capabilities={ModelCapability.TEXT, ModelCapability.REASONING, ModelCapability.FAST},
            context_window=200000,
            max_output_tokens=4096,
            supported_features=["vision", "thinking"],
            pricing={"input": 0.003, "output": 0.015},
        ))
        
        self.register_model(ModelInfo(
            model_id="claude-3-haiku-20240307",
            provider="anthropic",
            display_name="Claude 3 Haiku",
            description="Fast and affordable",
            capabilities={ModelCapability.TEXT, ModelCapability.FAST},
            context_window=200000,
            max_output_tokens=4096,
            supported_features=["vision"],
            pricing={"input": 0.00025, "output": 0.00125},
        ))
        
        # Local default
        self.register_model(ModelInfo(
            model_id="llama2",
            provider="local",
            display_name="Llama 2",
            description="Open source language model",
            capabilities={ModelCapability.TEXT},
            context_window=4096,
            max_output_tokens=2048,
        ))
    
    def register_model(self, model_info: ModelInfo) -> None:
        """Register a model"""
        self._models[model_info.model_id] = model_info
        
        # Track by provider
        if model_info.provider not in self._provider_models:
            self._provider_models[model_info.provider] = []
        self._provider_models[model_info.provider].append(model_info.model_id)
    
    def unregister_model(self, model_id: str) -> None:
        """Unregister a model"""
        if model_id in self._models:
            model = self._models[model_id]
            if model.provider in self._provider_models:
                self._provider_models[model.provider].remove(model_id)
            del self._models[model_id]
    
    def get(self, model_id: str) -> Optional[ModelInfo]:
        """Get model by ID"""
        # Check aliases
        if model_id in self._model_aliases:
            model_id = self._model_aliases[model_id]
        return self._models.get(model_id)
    
    def get_provider(self, model_id: str) -> Optional[str]:
        """Get provider for a model"""
        model = self.get(model_id)
        return model.provider if model else None
    
    def list_models(
        self,
        provider: Optional[str] = None,
        capability: Optional[ModelCapability] = None,
    ) -> List[ModelInfo]:
        """List models with optional filtering"""
        models = list(self._models.values())
        
        if provider:
            models = [m for m in models if m.provider == provider]
        
        if capability:
            models = [m for m in models if capability in m.capabilities]
        
        return models
    
    def list_models_by_provider(self, provider: str) -> List[str]:
        """List model IDs for a provider"""
        return self._provider_models.get(provider, [])
    
    def set_default_model(self, provider: str, model_id: str) -> None:
        """Set default model for provider"""
        if model_id in self._models:
            self._default_models[provider] = model_id
    
    def get_default_model(self, provider: str) -> Optional[str]:
        """Get default model for provider"""
        return self._default_models.get(provider)
    
    def add_alias(self, alias: str, model_id: str) -> None:
        """Add model alias"""
        self._model_aliases[alias] = model_id
    
    def remove_alias(self, alias: str) -> None:
        """Remove model alias"""
        if alias in self._model_aliases:
            del self._model_aliases[alias]
    
    def get_info(self, model_id: str) -> Optional[ModelInfo]:
        """Get model information"""
        return self.get(model_id)
    
    def search_models(
        self,
        query: str,
        limit: int = 10,
    ) -> List[ModelInfo]:
        """Search models by name or description"""
        query_lower = query.lower()
        results = []
        
        for model in self._models.values():
            if query_lower in model.model_id.lower():
                results.append(model)
            elif query_lower in model.display_name.lower():
                results.append(model)
            elif query_lower in model.description.lower():
                results.append(model)
        
        return results[:limit]
    
    def get_recommended_model(
        self,
        requirements: Dict[str, Any],
    ) -> Optional[ModelInfo]:
        """Get recommended model based on requirements"""
        max_context = requirements.get("max_context", float("inf"))
        need_reasoning = requirements.get("reasoning", False)
        need_fast = requirements.get("fast", False)
        budget = requirements.get("budget", float("inf"))
        
        candidates = self._models.values()
        
        # Filter by context
        candidates = [m for m in candidates if m.context_window >= max_context]
        
        # Filter by capabilities
        if need_reasoning:
            candidates = [m for m in candidates if ModelCapability.REASONING in m.capabilities]
        
        if need_fast:
            candidates = [m for m in candidates if ModelCapability.FAST in m.capabilities]
        
        # Sort by price if budget is set
        if budget < float("inf"):
            candidates = [
                m for m in candidates
                if m.pricing and m.pricing.get("input", float("inf")) <= budget
            ]
        
        return candidates[0] if candidates else None