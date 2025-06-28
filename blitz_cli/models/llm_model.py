import os
from typing import Optional, Dict, Any, Union, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator, model_validator
import warnings 
from dotenv import load_dotenv

    # Example of using with LangChain
from langchain_core.messages import SystemMessage,HumanMessage,AIMessage
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cerebras import ChatCerebras
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_sambanova import ChatSambaNovaCloud
from langchain_anthropic import ChatAnthropic
from langchain_cohere import ChatCohere
from langchain_ai21 import ChatAI21
from langchain_together.llms import Together 
from langchain_deepinfra import ChatDeepInfra
from langchain_ollama import ChatOllama
from langchain_huggingface import ChatHuggingFace

from config.settings import AgentSettings

load_dotenv()

warnings.filterwarnings('ignore')
# Initialize settings
settings = AgentSettings()


class Provider(str, Enum):
    """Enumeration of supported LLM providers"""
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    MISTRAL = "mistral"
    CEREBRAS = "cerebras"
    NVIDIA = "nvidia"
    SAMBANOVA = "sambanova"
    COHERE = "cohere"
    AI21 = "ai21"
    TOGETHER = "together"
    DEEPINFRA = "deepinfra"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    NOVITA = "novita"
    OPENROUTER = "openrouter"


class SamplingParameters(BaseModel):
    """Sampling parameters for LLM generation"""
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Temperature for sampling")
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(default=None, ge=1, description="Top-k sampling parameter")
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=1000000, description="Maximum tokens to generate")
    stop: Optional[Union[str, List[str]]] = Field(default=None, description="Stop sequences")
    stream: Optional[bool] = Field(default=False, description="Whether to stream the response")
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0, description="Presence penalty")
    repeat_penalty: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Repeat penalty")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError('Temperature must be between 0.0 and 2.0')
        return v
    
    @field_validator('top_p')
    @classmethod
    def validate_top_p(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Top-p must be between 0.0 and 1.0')
        return v
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v):
        if v is not None and (v < 1 or v > 1000000):
            raise ValueError('Max tokens must be between 1 and 1,000,000')
        return v
    
    @field_validator('frequency_penalty', 'presence_penalty')
    @classmethod
    def validate_penalties(cls, v):
        if v is not None and (v < -2.0 or v > 2.0):
            raise ValueError('Penalty must be between -2.0 and 2.0')
        return v
    
    @field_validator('repeat_penalty')
    @classmethod
    def validate_repeat_penalty(cls, v):
        if v is not None and (v < 0.0 or v > 2.0):
            raise ValueError('Repeat penalty must be between 0.0 and 2.0')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class ModelConfig(BaseModel):
    """Configuration for a specific LLM model"""
    provider: Provider = Field(description="LLM provider")
    model_name: str = Field(description="Model name/identifier")
    api_key: Optional[str] = Field(default=None, description="API key for the provider")
    base_url: Optional[str] = Field(default=None, description="Custom base URL for API")
    sampling_params: Optional[SamplingParameters] = Field(default=None, description="Sampling parameters")
    
    @field_validator('model_name')
    @classmethod
    def validate_model_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Model name cannot be empty')
        return v.strip()
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v):
        if v is not None and not v.strip():
            raise ValueError('API key cannot be empty if provided')
        return v.strip() if v else None
    
    @field_validator('base_url')
    @classmethod
    def validate_base_url(cls, v):
        """Validate base URL format"""
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError('Base URL must start with http:// or https://')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()


class ModelRegistry(BaseModel):
    """Registry of available models with Pydantic validation"""
    models: Dict[str, ModelConfig] = Field(default_factory=dict, description="Registered models")
    
    def add_model(self, name: str, config: ModelConfig):
        """Add a model to the registry"""
        self.models[name] = config
    
    def remove_model(self, name: str):
        """Remove a model from the registry"""
        if name in self.models:
            del self.models[name]
    
    def get_model(self, name: str) -> Optional[ModelConfig]:
        """Get a model configuration by name"""
        return self.models.get(name)
    
    def get_provider_models(self, provider: Provider) -> Dict[str, ModelConfig]:
        """Get all models for a specific provider"""
        return {
            name: config for name, config in self.models.items()
            if config.provider == provider
        }
    
    def list_models(self) -> Dict[str, ModelConfig]:
        """List all registered models"""
        return self.models.copy()


class LLMModelManager(BaseModel):
    """
    Comprehensive LLM model manager using Pydantic for validation and configuration
    """
    registry: ModelRegistry = Field(default_factory=ModelRegistry, description="Model registry")
    models: Dict[str, Any] = Field(default_factory=dict, description="Cached model instances")
    default_sampling_params: SamplingParameters = Field(
        default_factory=lambda: SamplingParameters(),
        description="Default sampling parameters"
    )
    settings: AgentSettings = Field(default_factory=AgentSettings, description="Agent settings")
    
    model_config = {
        "arbitrary_types_allowed": True,
        "validate_assignment": True
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        self._initialize_default_models()
    
    def _initialize_default_models(self):
        """Initialize the registry with default models from settings"""
        # Get model configurations from settings
        model_config = self.settings.model_config_dict
        default_model = model_config.get("default_model", "groq")
        
        # Create default models based on settings
        default_models = {
            # OpenAI Models
            "gpt-4": ModelConfig(
                provider=Provider.OPENAI,
                model_name="gpt-4",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            "gpt-4-turbo": ModelConfig(
                provider=Provider.OPENAI,
                model_name="gpt-4-turbo-preview",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            "gpt-3.5-turbo": ModelConfig(
                provider=Provider.OPENAI,
                model_name="gpt-3.5-turbo",
                api_key=os.getenv("OPENAI_API_KEY")
            ),
            
            # Google Models (from settings)
            "gemini-pro": ModelConfig(
                provider=Provider.GOOGLE,
                model_name="gemini-pro",
                api_key=self.settings.google_api_key or os.getenv("GOOGLE_API_KEY"),
                sampling_params=SamplingParameters(
                    max_tokens=model_config.get("gemini", {}).get("max_tokens", 100000)
                )
            ),
            "gemini-2.0-flash": ModelConfig(
                provider=Provider.GOOGLE,
                model_name="gemini-2.0-flash-exp",
                api_key=self.settings.google_api_key or os.getenv("GOOGLE_API_KEY"),
                sampling_params=SamplingParameters(
                    max_tokens=model_config.get("gemini", {}).get("max_tokens", 100000)
                )
            ),
            
            # Anthropic Models
            "claude-3-opus": ModelConfig(
                provider=Provider.ANTHROPIC,
                model_name="claude-3-opus-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ),
            "claude-3-sonnet": ModelConfig(
                provider=Provider.ANTHROPIC,
                model_name="claude-3-sonnet-20240229",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ),
            "claude-3-haiku": ModelConfig(
                provider=Provider.ANTHROPIC,
                model_name="claude-3-haiku-20240307",
                api_key=os.getenv("ANTHROPIC_API_KEY")
            ),
            
            # Groq Models (from settings)
            "llama-3.1-8b": ModelConfig(
                provider=Provider.GROQ,
                model_name="llama3-8b-8192",
                api_key=self.settings.groq_api_key or os.getenv("GROQ_API_KEY"),
                sampling_params=SamplingParameters(
                    temperature=model_config.get("groq", {}).get("temperature", 0.2),
                    max_tokens=model_config.get("groq", {}).get("max_tokens", 100000)
                )
            ),
            "llama-3.1-70b": ModelConfig(
                provider=Provider.GROQ,
                model_name="llama3-70b-8192",
                api_key=self.settings.groq_api_key or os.getenv("GROQ_API_KEY"),
                sampling_params=SamplingParameters(
                    temperature=model_config.get("groq", {}).get("temperature", 0.2),
                    max_tokens=model_config.get("groq", {}).get("max_tokens", 100000)
                )
            ),
            "mixtral-8x7b": ModelConfig(
                provider=Provider.GROQ,
                model_name="mixtral-8x7b-32768",
                api_key=self.settings.groq_api_key or os.getenv("GROQ_API_KEY"),
                sampling_params=SamplingParameters(
                    temperature=model_config.get("groq", {}).get("temperature", 0.2),
                    max_tokens=model_config.get("groq", {}).get("max_tokens", 100000)
                )
            ),
            "gemma2-9b": ModelConfig(
                provider=Provider.GROQ,
                model_name="gemma2-9b-it",
                api_key=self.settings.groq_api_key or os.getenv("GROQ_API_KEY"),
                sampling_params=SamplingParameters(
                    temperature=model_config.get("groq", {}).get("temperature", 0.2),
                    max_tokens=model_config.get("groq", {}).get("max_tokens", 100000)
                )
            ),
            # Add the default model from settings
            "qwen-qwq-32b": ModelConfig(
                provider=Provider.GROQ,
                model_name=model_config.get("groq", {}).get("model", "qwen-qwq-32b"),
                api_key=self.settings.groq_api_key or os.getenv("GROQ_API_KEY"),
                sampling_params=SamplingParameters(
                    temperature=model_config.get("groq", {}).get("temperature", 0.2),
                    max_tokens=model_config.get("groq", {}).get("max_tokens", 100000)
                )
            ),
            
            # Mistral Models
            "mistral-large": ModelConfig(
                provider=Provider.MISTRAL,
                model_name="mistral-large-latest",
                api_key=os.getenv("MISTRAL_API_KEY")
            ),
            "mistral-medium": ModelConfig(
                provider=Provider.MISTRAL,
                model_name="mistral-medium-latest",
                api_key=os.getenv("MISTRAL_API_KEY")
            ),
            "mistral-small": ModelConfig(
                provider=Provider.MISTRAL,
                model_name="mistral-small-latest",
                api_key=os.getenv("MISTRAL_API_KEY")
            ),
            
            # Cerebras Models
            "cerebras-llama-2-7b": ModelConfig(
                provider=Provider.CEREBRAS,
                model_name="cerebras-llama-2-7b-chat",
                api_key=os.getenv("CEREBRAS_API_KEY")
            ),
            
            # NVIDIA Models
            "nvidia-llama-2-70b": ModelConfig(
                provider=Provider.NVIDIA,
                model_name="meta/llama2-70b",
                api_key=os.getenv("NVIDIA_API_KEY")
            ),
            
            # Together AI Models
            "together-llama-2-70b": ModelConfig(
                provider=Provider.TOGETHER,
                model_name="meta-llama/Llama-2-70b-chat-hf",
                api_key=os.getenv("TOGETHER_API_KEY")
            ),
            
            # DeepInfra Models
            "deepinfra-llama-2-70b": ModelConfig(
                provider=Provider.DEEPINFRA,
                model_name="meta-llama/Llama-2-70b-chat-hf",
                api_key=os.getenv("DEEPINFRA_API_KEY")
            ),
            
            # Novita AI Models
            "qwen2.5-7b": ModelConfig(
                provider=Provider.NOVITA,
                model_name="qwen/qwen2.5-7b-instruct",
                api_key=os.getenv("NOVITA_API_KEY"),
                base_url="https://api.novita.ai/v3/openai"
            ),
            "qwen2.5-14b": ModelConfig(
                provider=Provider.NOVITA,
                model_name="qwen/qwen2.5-14b-instruct",
                api_key=os.getenv("NOVITA_API_KEY"),
                base_url="https://api.novita.ai/v3/openai"
            ),
            "qwen2.5-32b": ModelConfig(
                provider=Provider.NOVITA,
                model_name="qwen/qwen2.5-32b-instruct",
                api_key=os.getenv("NOVITA_API_KEY"),
                base_url="https://api.novita.ai/v3/openai"
            ),
            
            # OpenRouter Models
            "openrouter-gpt-4": ModelConfig(
                provider=Provider.OPENROUTER,
                model_name="openai/gpt-4",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            ),
            "openrouter-claude-3": ModelConfig(
                provider=Provider.OPENROUTER,
                model_name="anthropic/claude-3-opus",
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            ),
        }
        
        for name, config in default_models.items():
            self.registry.add_model(name, config)
    
    def get_default_model(self) -> Any:
        """Get the default model from settings"""
        default_model = self.settings.model_config_dict.get("default_model", "groq")
        if default_model == "groq":
            return self.create_model("qwen-qwq-32b")
        elif default_model == "gemini":
            return self.create_model("gemini-2.0-flash")
        else:
            return self.create_model(default_model)
    
    def get_model_with_settings(self, model_name: Optional[str] = None) -> Any:
        """Get a model using settings configuration"""
        if model_name is None:
            return self.get_default_model()
        
        # Check if model exists in registry
        if model_name in self.registry.models:
            return self.create_model(model_name)
        
        # Try to create with default provider
        default_provider = self.settings.model_config_dict.get("default_model", "groq")
        if default_provider == "groq":
            return self.create_model(model_name, provider=Provider.GROQ)
        elif default_provider == "gemini":
            return self.create_model(model_name, provider=Provider.GOOGLE)
        else:
            return self.create_model(model_name)
    
    def create_model(
        self,
        model_name: str,
        provider: Optional[Provider] = None,
        sampling_params: Optional[SamplingParameters] = None,
        custom_config: Optional[ModelConfig] = None
    ) -> Any:
        """
        Create an LLM model instance with the specified configuration.
        
        Args:
            model_name: Name of the model to create
            provider: Provider to use (optional if model is in registry)
            sampling_params: Sampling parameters for the model
            custom_config: Custom model configuration
            
        Returns:
            LangChain chat model instance
        """
        # Use custom config if provided
        if custom_config:
            config = custom_config
        elif model_name in self.registry.models:
            config = self.registry.models[model_name]
        else:
            if not provider:
                raise ValueError(f"Model '{model_name}' not found in registry and no provider specified")
            config = ModelConfig(
                provider=provider,
                model_name=model_name,
                api_key=os.getenv(f"{provider.upper()}_API_KEY")
            )
        
        # Merge sampling parameters
        if sampling_params:
            final_sampling_params = sampling_params
        elif config.sampling_params:
            final_sampling_params = config.sampling_params
        else:
            final_sampling_params = self.default_sampling_params
        
        # Create model based on provider
        model = self._create_provider_model(config, final_sampling_params)
        
        # Cache the model
        cache_key = f"{config.provider.value}:{model_name}"
        self.models[cache_key] = model
        
        return model
    
    def _create_provider_model(self, config: ModelConfig, sampling_params: SamplingParameters) -> Any:
        """Create a model instance for the specified provider"""
        
        # Common parameters
        common_params = {
            "temperature": sampling_params.temperature,
            "max_tokens": sampling_params.max_tokens,
            "stream": sampling_params.stream,
        }
        
        # Add provider-specific parameters
        if sampling_params.top_p is not None:
            common_params["top_p"] = sampling_params.top_p
        if sampling_params.top_k is not None:
            common_params["top_k"] = sampling_params.top_k
        if sampling_params.frequency_penalty is not None:
            common_params["frequency_penalty"] = sampling_params.frequency_penalty
        if sampling_params.presence_penalty is not None:
            common_params["presence_penalty"] = sampling_params.presence_penalty
        if sampling_params.stop is not None:
            common_params["stop"] = sampling_params.stop
        if sampling_params.repeat_penalty is not None:
            common_params["repeat_penalty"] = sampling_params.repeat_penalty
        
        # Filter out None values
        common_params = {k: v for k, v in common_params.items() if v is not None}
        
        try:
            if config.provider == Provider.OPENAI:
                return ChatOpenAI(
                    model=config.model_name,
                    openai_api_key=config.api_key,
                    openai_api_base=config.base_url,
                    **common_params
                )
            
            elif config.provider == Provider.GOOGLE:
                return ChatGoogleGenerativeAI(
                    model=config.model_name,
                    google_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.ANTHROPIC:
                return ChatAnthropic(
                    model=config.model_name,
                    anthropic_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.GROQ:
                return ChatGroq(
                    model=config.model_name,
                    groq_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.MISTRAL:
                return ChatMistralAI(
                    model=config.model_name,
                    mistral_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.CEREBRAS:
                return ChatCerebras(
                    model=config.model_name,
                    cerebras_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.NVIDIA:
                return ChatNVIDIA(
                    model=config.model_name,
                    nvidia_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.SAMBANOVA:
                return ChatSambaNovaCloud(
                    model=config.model_name,
                    sambanova_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.COHERE:
                return ChatCohere(
                    model=config.model_name,
                    cohere_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.AI21:
                return ChatAI21(
                    model=config.model_name,
                    ai21_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.TOGETHER:
                # Ensure max_tokens is set for Together models
                together_params = common_params.copy()
                if "max_tokens" not in together_params or together_params["max_tokens"] is None:
                    together_params["max_tokens"] = 2000  # Default value
                
                return Together(
                    model=config.model_name,
                    together_api_key=config.api_key,
                    **together_params
                )
            
            elif config.provider == Provider.DEEPINFRA:
                return ChatDeepInfra(
                    model=config.model_name,
                    deepinfra_api_key=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.OLLAMA:
                return ChatOllama(
                    model=config.model_name,
                    base_url=config.base_url,
                    **common_params
                )
            
            elif config.provider == Provider.HUGGINGFACE:
                return ChatHuggingFace(
                    model_name=config.model_name,
                    huggingfacehub_api_token=config.api_key,
                    **common_params
                )
            
            elif config.provider == Provider.NOVITA:
                return ChatOpenAI(
                    model=config.model_name,
                    openai_api_key=config.api_key,
                    openai_api_base=config.base_url,
                    **common_params
                )
            
            elif config.provider == Provider.OPENROUTER:
                return ChatOpenAI(
                    model=config.model_name,
                    openai_api_key=config.api_key,
                    openai_api_base=config.base_url,
                    **common_params
                )
            
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
                
        except Exception as e:
            raise ValueError(f"Failed to create model for provider {config.provider}: {str(e)}")
    
    def get_model(self, model_name: str) -> Any:
        """Get a cached model instance"""
        for cache_key, model in self.models.items():
            if model_name in cache_key:
                return model
        return None
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models with their configurations"""
        return {
            name: {
                "provider": config.provider.value,
                "model_name": config.model_name,
                "sampling_params": config.sampling_params.dict() if config.sampling_params else None,
                "has_api_key": bool(config.api_key)
            }
            for name, config in self.registry.models.items()
        }
    
    def add_custom_model(self, name: str, config: ModelConfig):
        """Add a custom model to the registry"""
        self.registry.add_model(name, config)
    
    def remove_model(self, name: str):
        """Remove a model from the registry"""
        self.registry.remove_model(name)
    
    def get_provider_models(self, provider: Provider) -> Dict[str, ModelConfig]:
        """Get all models for a specific provider"""
        return self.registry.get_provider_models(provider)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manager to dictionary for serialization"""
        return {
            "registry": self.registry.model_dump(),
            "default_sampling_params": self.default_sampling_params.model_dump(),
            "cached_models_count": len(self.models)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMModelManager':
        """Create manager from dictionary"""
        return cls(**data)

    def get_system_prompt(self) -> str:
        """Get the system prompt from settings"""
        return self.settings.SYSTEM_PROMPT
    
    def create_model_with_system_prompt(self, model_name: Optional[str] = None) -> Any:
        """Create a model with the system prompt from settings"""
        model = self.get_model_with_settings(model_name)
        # Note: The system prompt would be used when creating the chat chain
        # This is just a helper method to get both model and system prompt
        return model, self.get_system_prompt()

    def validate_model_config(self, model_name: str) -> bool:
        """Validate if a model configuration is complete"""
        if model_name not in self.registry.models:
            return False
        
        config = self.registry.models[model_name]
        return bool(config.api_key)

    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific model"""
        if model_name not in self.registry.models:
            raise ValueError(f"Model '{model_name}' not found in registry")
        
        config = self.registry.models[model_name]
        return {
            "name": model_name,
            "provider": config.provider.value,
            "model_name": config.model_name,
            "base_url": config.base_url,
            "sampling_params": config.sampling_params.model_dump() if config.sampling_params else None,
            "has_api_key": bool(config.api_key),
            "is_valid": self.validate_model_config(model_name)
        }


# Convenience functions for quick model creation
def create_openai_model(
    model_name: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatOpenAI:
    """Quick function to create an OpenAI model"""
    manager = LLMModelManager()
    sampling_params = SamplingParameters(
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return manager.create_model(model_name, sampling_params=sampling_params)


def create_groq_model(
    model_name: str = "llama3-8b-8192",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatGroq:
    """Quick function to create a Groq model"""
    manager = LLMModelManager()
    sampling_params = SamplingParameters(
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return manager.create_model(model_name, sampling_params=sampling_params)


def create_google_model(
    model_name: str = "gemini-2.0-flash",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    **kwargs
) -> ChatGoogleGenerativeAI:
    """Quick function to create a Google model"""
    manager = LLMModelManager()
    sampling_params = SamplingParameters(
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
    return manager.create_model(model_name, sampling_params=sampling_params)


# Example usage and integration with AgentSettings
if __name__ == "__main__":
    # Initialize the model manager with settings
    manager = LLMModelManager()
    
    # Get the default model from settings
    default_model = manager.get_default_model()
    print(f"Default model: {default_model}")
    
    # Get system prompt from settings
    system_prompt = manager.get_system_prompt()
    print(f"System prompt length: {len(system_prompt)} characters")
    
    # List all available models with their configurations
    available_models = manager.list_available_models()
    print(f"Available models: {len(available_models)}")
    
    # Get detailed info about a specific model
    try:
        model_info = manager.get_model_info("qwen-qwq-32b")
        print(f"Model info: {model_info}")
    except ValueError as e:
        print(f"Error: {e}")
    
    # Create a model with custom sampling parameters
    custom_params = SamplingParameters(
        temperature=0.7,
        max_tokens=2000,
        top_p=0.9,
        frequency_penalty=0.1
    )
    
    # Add a custom model
    custom_config = ModelConfig(
        provider=Provider.GROQ,
        model_name="llama3-8b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        sampling_params=custom_params
    )
    manager.add_custom_model("custom-llama", custom_config)
    
    # Create the custom model
    custom_model = manager.create_model("custom-llama")
    print(f"Custom model created: {custom_model}")
    
    
    # Create messages
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Hello! Can you help me with coding?")
    ]
    
    # Use the model (if API key is available)
    try:
        response = default_model.invoke(messages)
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Error using model: {e}")
        print("Make sure to set the appropriate API key in your environment variables")
    
    # Save and load configurations
    config_data = manager.model_dump()
    print(f"Configuration saved: {len(config_data)} fields")
    
    # Create a new manager from saved configuration
    new_manager = LLMModelManager.model_validate(config_data)
    print(f"New manager created with {len(new_manager.registry.models)} models")