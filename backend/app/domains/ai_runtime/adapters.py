"""
AI Model Adapters - Provider-agnostic AI abstraction layer
"""
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Set, Type, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AdapterCapability(str, Enum):
    """Capabilities of AI adapters"""
    TEXT_GENERATION = "text_generation"
    CHAT_COMPLETION = "chat_completion"
    IMAGE_GENERATION = "image_generation"
    IMAGE_ANALYSIS = "image_analysis"
    AUDIO_GENERATION = "audio_generation"
    EMBEDDINGS = "embeddings"
    FINE_TUNING = "fine_tuning"


@dataclass
class GenerationConfig:
    """Configuration for generation"""
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    seed: Optional[int] = None
    response_format: Optional[Dict[str, Any]] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[str] = None


@dataclass
class GenerationRequest:
    """Request for AI generation"""
    prompt: str
    system_prompt: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    config: Optional[GenerationConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GenerationResponse:
    """Response from AI generation"""
    content: str
    model: str
    provider: str
    tokens_used: int
    input_tokens: int = 0
    output_tokens: int = 0
    finish_reason: str = "stop"
    metadata: Dict[str, Any] = field(default_factory=dict)
    latencies: Dict[str, float] = field(default_factory=dict)


@dataclass
class ChatMessage:
    """Chat message"""
    role: str  # "system", "user", "assistant"
    content: str
    name: Optional[str] = None


@dataclass
class ChatRequest:
    """Chat completion request"""
    messages: List[ChatMessage]
    model: str
    temperature: float = 0.7
    max_tokens: int = 4096
    top_p: float = 1.0
    stop: Optional[List[str]] = None
    stream: bool = False


class AIModelAdapter(ABC):
    """
    Abstract base class for AI model adapters.
    Provides provider-agnostic interface for AI operations.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.organization = organization
        self._capabilities: Set[AdapterCapability] = set()
        self._models: List[str] = []
        self._configured = False
    
    @property
    @abstractmethod
    def provider(self) -> str:
        """Return the provider name"""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model"""
        pass
    
    @property
    def capabilities(self) -> Set[AdapterCapability]:
        """Return adapter capabilities"""
        return self._capabilities
    
    @property
    def models(self) -> List[str]:
        """Return available models"""
        return self._models
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the adapter"""
        pass
    
    @abstractmethod
    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate text from prompt"""
        pass
    
    @abstractmethod
    async def chat(
        self,
        request: ChatRequest,
    ) -> GenerationResponse:
        """Generate chat completion"""
        pass
    
    async def generate_stream(
        self,
        request: GenerationRequest,
        callback: Optional[Callable[[str], None]] = None,
    ) -> GenerationResponse:
        """Generate text with streaming"""
        # Default implementation - override for streaming
        response = await self.generate(request)
        if callback:
            callback(response.content)
        return response
    
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text (estimate)"""
        # Rough estimate: 4 chars per token
        return len(text) // 4
    
    def validate_config(self, config: GenerationConfig) -> bool:
        """Validate generation config"""
        if config.temperature < 0 or config.temperature > 2:
            return False
        if config.max_tokens < 1:
            return False
        return True


class OpenAIAdapter(AIModelAdapter):
    """OpenAI API adapter"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
    ):
        super().__init__(api_key, base_url, organization)
        self._capabilities = {
            AdapterCapability.TEXT_GENERATION,
            AdapterCapability.CHAT_COMPLETION,
            AdapterCapability.EMBEDDINGS,
        }
        self._models = [
            "gpt-4-turbo",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "text-embedding-3-small",
            "text-embedding-ada-002",
        ]
        self._client = None
    
    @property
    def provider(self) -> str:
        return "openai"
    
    @property
    def default_model(self) -> str:
        return "gpt-4"
    
    async def initialize(self) -> None:
        """Initialize OpenAI client"""
        try:
            import openai
            self._client = openai.AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization,
            )
            self._configured = True
            logger.info("OpenAI adapter initialized")
        except ImportError:
            logger.warning("OpenAI client not installed")
    
    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate text using OpenAI"""
        if not self._configured:
            raise RuntimeError("OpenAI adapter not initialized")
        
        config = request.config or GenerationConfig(model=self.default_model)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self._client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": request.system_prompt or ""},
                    {"role": "user", "content": request.prompt},
                ],
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                frequency_penalty=config.frequency_penalty,
                presence_penalty=config.presence_penalty,
                stop=config.stop,
            )
            
            end_time = asyncio.get_event_loop().time()
            
            choice = response.choices[0]
            return GenerationResponse(
                content=choice.message.content or "",
                model=config.model,
                provider=self.provider,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                finish_reason=choice.finish_reason or "stop",
                metadata=response.model_dump(),
                latencies={"total": end_time - start_time},
            )
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def chat(
        self,
        request: ChatRequest,
    ) -> GenerationResponse:
        """Generate chat completion using OpenAI"""
        if not self._configured:
            raise RuntimeError("OpenAI adapter not initialized")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self._client.chat.completions.create(
                model=request.model,
                messages=[{"role": m.role, "content": m.content, "name": m.name} for m in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
                stop=request.stop,
                stream=request.stream,
            )
            
            end_time = asyncio.get_event_loop().time()
            
            if request.stream:
                # Handle streaming
                content = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                return GenerationResponse(
                    content=content,
                    model=request.model,
                    provider=self.provider,
                    tokens_used=0,
                    finish_reason="stop",
                    latencies={"total": end_time - start_time},
                )
            else:
                choice = response.choices[0]
                return GenerationResponse(
                    content=choice.message.content or "",
                    model=request.model,
                    provider=self.provider,
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    input_tokens=response.usage.prompt_tokens if response.usage else 0,
                    output_tokens=response.usage.completion_tokens if response.usage else 0,
                    finish_reason=choice.finish_reason or "stop",
                    metadata=response.model_dump(),
                    latencies={"total": end_time - start_time},
                )
                
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise


class AnthropicAdapter(AIModelAdapter):
    """Anthropic API adapter"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        super().__init__(api_key, base_url)
        self._capabilities = {
            AdapterCapability.TEXT_GENERATION,
            AdapterCapability.CHAT_COMPLETION,
        }
        self._models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2",
            "claude-instant-1.2",
        ]
        self._client = None
    
    @property
    def provider(self) -> str:
        return "anthropic"
    
    @property
    def default_model(self) -> str:
        return "claude-3-sonnet-20240229"
    
    async def initialize(self) -> None:
        """Initialize Anthropic client"""
        try:
            import anthropic
            self._client = anthropic.AsyncAnthropic(
                api_key=self.api_key,
            )
            self._configured = True
            logger.info("Anthropic adapter initialized")
        except ImportError:
            logger.warning("Anthropic client not installed")
    
    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate text using Anthropic"""
        if not self._configured:
            raise RuntimeError("Anthropic adapter not initialized")
        
        config = request.config or GenerationConfig(model=self.default_model)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self._client.messages.create(
                model=config.model,
                system=request.system_prompt,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                messages=[{"role": "user", "content": request.prompt}],
            )
            
            end_time = asyncio.get_event_loop().time()
            
            return GenerationResponse(
                content=response.content[0].text,
                model=config.model,
                provider=self.provider,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                finish_reason="stop" if response.stop_reason == "end_turn" else response.stop_reason,
                metadata={"id": response.id},
                latencies={"total": end_time - start_time},
            )
            
        except Exception as e:
            logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def chat(
        self,
        request: ChatRequest,
    ) -> GenerationResponse:
        """Generate chat completion using Anthropic"""
        if not self._configured:
            raise RuntimeError("Anthropic adapter not initialized")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            # Convert messages to Anthropic format
            anthropic_messages = []
            system_message = None
            
            for msg in request.messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": "user" if msg.role == "user" else "assistant",
                        "content": msg.content,
                    })
            
            response = await self._client.messages.create(
                model=request.model,
                system=system_message,
                messages=anthropic_messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )
            
            end_time = asyncio.get_event_loop().time()
            
            return GenerationResponse(
                content=response.content[0].text,
                model=request.model,
                provider=self.provider,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                finish_reason="stop" if response.stop_reason == "end_turn" else response.stop_reason,
                metadata={"id": response.id},
                latencies={"total": end_time - start_time},
            )
            
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise


class LocalAdapter(AIModelAdapter):
    """Local/model server adapter"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
    ):
        super().__init__(api_key, base_url)
        self._capabilities = {
            AdapterCapability.TEXT_GENERATION,
            AdapterCapability.CHAT_COMPLETION,
            AdapterCapability.EMBEDDINGS,
        }
        self._models = []
        self._client = None
    
    @property
    def provider(self) -> str:
        return "local"
    
    @property
    def default_model(self) -> str:
        return "llama2"
    
    async def initialize(self) -> None:
        """Initialize local client"""
        import httpx
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            timeout=300.0,
        )
        
        # Try to get available models
        try:
            response = await self._client.get("/v1/models")
            if response.status_code == 200:
                data = response.json()
                self._models = [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.warning(f"Could not fetch local models: {e}")
            self._models = ["llama2", "mistral"]
        
        self._configured = True
        logger.info(f"Local adapter initialized with models: {self._models}")
    
    async def generate(
        self,
        request: GenerationRequest,
    ) -> GenerationResponse:
        """Generate text using local server"""
        if not self._configured:
            raise RuntimeError("Local adapter not initialized")
        
        config = request.config or GenerationConfig(model=self.default_model)
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self._client.post(
                "/v1/completions",
                json={
                    "model": config.model,
                    "prompt": f"{request.system_prompt}\n\n{request.prompt}" if request.system_prompt else request.prompt,
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                    "stop": config.stop,
                },
            )
            
            end_time = asyncio.get_event_loop().time()
            
            if response.status_code == 200:
                data = response.json()
                return GenerationResponse(
                    content=data["choices"][0]["text"],
                    model=config.model,
                    provider=self.provider,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    finish_reason=data["choices"][0].get("finish_reason", "stop"),
                    latencies={"total": end_time - start_time},
                )
            else:
                raise Exception(f"Local generation failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Local generation error: {e}")
            raise
    
    async def chat(
        self,
        request: ChatRequest,
    ) -> GenerationResponse:
        """Generate chat completion using local server"""
        if not self._configured:
            raise RuntimeError("Local adapter not initialized")
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            response = await self._client.post(
                "/v1/chat/completions",
                json={
                    "model": request.model,
                    "messages": [
                        {"role": m.role, "content": m.content} for m in request.messages
                    ],
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stop": request.stop,
                },
            )
            
            end_time = asyncio.get_event_loop().time()
            
            if response.status_code == 200:
                data = response.json()
                return GenerationResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=request.model,
                    provider=self.provider,
                    tokens_used=data.get("usage", {}).get("total_tokens", 0),
                    finish_reason=data["choices"][0].get("finish_reason", "stop"),
                    latencies={"total": end_time - start_time},
                )
            else:
                raise Exception(f"Local chat failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Local chat error: {e}")
            raise