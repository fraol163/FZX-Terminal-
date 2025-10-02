"""
AI Service Module for FZX-Terminal
Google Gemini API integration with codebase understanding capabilities
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Optional imports for full functionality
try:
    import asyncio
    import aiohttp
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False
    print("Warning: aiohttp not available. AI service will run in limited mode.")
    print("Install with: pip install aiohttp")

try:
    from context_manager import get_context_manager
    from chat_manager import get_chat_manager
    from terminal_persistence import get_terminal_engine
except ImportError as e:
    print(f"Warning: Could not import workflow components: {e}")


class AIProvider(Enum):
    """Supported AI providers."""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"


class AIModelType(Enum):
    """Available Gemini models (latest versions only)."""
    GEMINI_1_5_PRO_LATEST = "gemini-1.5-pro-latest"
    GEMINI_1_5_FLASH_LATEST = "gemini-1.5-flash-latest"
    GEMINI_1_5_FLASH_8B = "gemini-1.5-flash-8b"
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"
    
    @classmethod
    def has_value(cls, value):
        """Check if a value exists in the enum."""
        return value in [item.value for item in cls]


@dataclass
class AIConfig:
    """AI service configuration."""
    api_key: str
    provider: AIProvider = AIProvider.GEMINI
    model: AIModelType = AIModelType.GEMINI_1_5_FLASH_LATEST
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0
    context_window: int = 32000
    enable_context_integration: bool = True
    enable_streaming: bool = True


@dataclass
class AIResponse:
    """AI response wrapper."""
    content: str
    model: str
    usage: Dict[str, Any]
    timestamp: float
    response_time: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class OpenRouterService:
    """OpenRouter API service implementation."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = "https://openrouter.ai/api/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        self.context_manager = None
        self.chat_manager = None
        
        # Initialize context integration if enabled
        if self.config.enable_context_integration:
            try:
                self.context_manager = get_context_manager()
                self.chat_manager = get_chat_manager()
            except Exception as e:
                print(f"Warning: Context integration disabled: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not ASYNC_AVAILABLE:
            raise RuntimeError("aiohttp not available. Please install: pip install aiohttp")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_model_endpoint(self) -> str:
        """Get the API endpoint for chat completions."""
        return f"{self.base_url}/chat/completions"
    
    def _prepare_request_data(self, messages: List[Dict[str, str]], 
                            system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Prepare request data for OpenRouter API."""
        # Convert messages to OpenRouter format
        openrouter_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            openrouter_messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # Convert messages
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            openrouter_messages.append({
                "role": role,
                "content": content
            })
        
        return {
            "model": self.config.model.value,
            "messages": openrouter_messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "top_p": 0.8
        }
    
    async def _make_api_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://fzx-terminal.com",
            "X-Title": "FZX Terminal"
        }
        
        for attempt in range(self.config.retry_count):
            try:
                async with self.session.post(
                    url, 
                    json=data, 
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit
                        if attempt < self.config.retry_count - 1:
                            await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                            continue
                    
                    error_text = await response.text()
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                    
            except asyncio.TimeoutError:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    continue
                raise Exception("API request timed out")
            except Exception as e:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    continue
                raise e
        
        raise Exception("Max retry attempts exceeded")
    
    async def chat_completion(self, 
                            messages: List[Dict[str, str]], 
                            system_prompt: Optional[str] = None,
                            model: Optional[str] = None) -> AIResponse:
        """Generate chat completion using OpenRouter API."""
        start_time = time.time()
        model = model or self.config.model.value
        
        try:
            # Prepare request
            url = self._get_model_endpoint()
            data = self._prepare_request_data(messages, system_prompt)
            
            # Make API call
            response_data = await self._make_api_request(url, data)
            
            # Extract response content
            choices = response_data.get("choices", [])
            if not choices:
                raise Exception("No response choices returned")
            
            content = choices[0].get("message", {}).get("content", "")
            
            # Extract usage information
            usage = response_data.get("usage", {})
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=content,
                model=model,
                usage=usage,
                timestamp=time.time(),
                response_time=response_time,
                success=True,
                metadata={
                    "finish_reason": choices[0].get("finish_reason", ""),
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return AIResponse(
                content="",
                model=model,
                usage={},
                timestamp=time.time(),
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    def build_codebase_aware_prompt(self, user_message: str) -> str:
        """Build codebase-aware prompt using existing context manager."""
        if not self.context_manager:
            return user_message
        
        try:
            # Get relevant context from context manager
            context_data = self.context_manager.build_prompt(
                max_tokens=self.config.context_window // 2,
                reserved_reply_tokens=self.config.max_tokens,
                system_header="You are an AI assistant integrated into FZX-Terminal, helping with development tasks."
            )
            
            if context_data.get("prompt_text"):
                return f"{context_data['prompt_text']}\n\nUser: {user_message}"
            
        except Exception as e:
            print(f"Warning: Could not build codebase-aware prompt: {e}")
        
        return user_message


class GeminiService:
    """Google Gemini API service implementation."""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.base_url = "https://generativelanguage.googleapis.com/v1/models"
        self.session: Optional[aiohttp.ClientSession] = None
        self.context_manager = None
        self.chat_manager = None
        
        # Initialize context integration if enabled
        if self.config.enable_context_integration:
            try:
                self.context_manager = get_context_manager()
                self.chat_manager = get_chat_manager()
            except Exception as e:
                print(f"Warning: Context integration disabled: {e}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        if not ASYNC_AVAILABLE:
            raise RuntimeError("aiohttp not available. Please install: pip install aiohttp")
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    def _get_model_endpoint(self, model: AIModelType) -> str:
        """Get the API endpoint for a specific model."""
        return f"{self.base_url}/{model.value}:generateContent"
    
    def _prepare_request_data(self, messages: List[Dict[str, str]], 
                            system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Prepare request data for Gemini API."""
        contents = []
        
        # Add system prompt if provided
        if system_prompt:
            contents.append({
                "role": "user",
                "parts": [{"text": f"System: {system_prompt}"}]
            })
        
        # Convert messages to Gemini format
        for msg in messages:
            role = "user" if msg.get("role") == "user" else "model"
            content = msg.get("content", "")
            
            contents.append({
                "role": role,
                "parts": [{"text": content}]
            })
        
        return {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": self.config.max_tokens,
                "temperature": self.config.temperature,
                "topP": 0.8,
                "topK": 40
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
    
    async def _make_api_request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with retry logic."""
        headers = {
            "Content-Type": "application/json"
        }
        
        params = {
            "key": self.config.api_key
        }
        
        for attempt in range(self.config.retry_count):
            try:
                async with self.session.post(
                    url, 
                    json=data, 
                    headers=headers,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limit
                        if attempt < self.config.retry_count - 1:
                            await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                            continue
                    
                    error_text = await response.text()
                    raise Exception(f"API request failed: {response.status} - {error_text}")
                    
            except asyncio.TimeoutError:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    continue
                raise Exception("API request timed out")
            except Exception as e:
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay)
                    continue
                raise e
        
        raise Exception("Max retry attempts exceeded")
    
    async def chat_completion(self, 
                            messages: List[Dict[str, str]], 
                            system_prompt: Optional[str] = None,
                            model: Optional[AIModelType] = None) -> AIResponse:
        """Generate chat completion using Gemini API."""
        start_time = time.time()
        model = model or self.config.model
        
        try:
            # Prepare request
            url = self._get_model_endpoint(model)
            data = self._prepare_request_data(messages, system_prompt)
            
            # Make API call
            response_data = await self._make_api_request(url, data)
            
            # Extract response content
            candidates = response_data.get("candidates", [])
            if not candidates:
                raise Exception("No response candidates returned")
            
            content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            
            # Extract usage information
            usage = response_data.get("usageMetadata", {})
            
            response_time = time.time() - start_time
            
            return AIResponse(
                content=content,
                model=model.value,
                usage=usage,
                timestamp=time.time(),
                response_time=response_time,
                success=True,
                metadata={
                    "finish_reason": candidates[0].get("finishReason", ""),
                    "safety_ratings": candidates[0].get("safetyRatings", [])
                }
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return AIResponse(
                content="",
                model=model.value,
                usage={},
                timestamp=time.time(),
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    def build_codebase_aware_prompt(self, user_message: str) -> str:
        """Build codebase-aware prompt using existing context manager."""
        if not self.context_manager:
            return user_message
        
        try:
            # Get relevant context from context manager
            context_data = self.context_manager.build_prompt(
                max_tokens=self.config.context_window // 2,
                reserved_reply_tokens=self.config.max_tokens,
                system_header="You are an AI assistant integrated into FZX-Terminal, helping with development tasks."
            )
            
            if context_data.get("prompt_text"):
                return f"{context_data['prompt_text']}\n\nUser: {user_message}"
            
        except Exception as e:
            print(f"Warning: Could not build codebase-aware prompt: {e}")
        
        return user_message


class AIServiceManager:
    """Main AI service manager."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.config_file = self.project_root / ".terminal_data" / "ai_config.json"
        self.config: Optional[AIConfig] = None
        self.service: Optional[Union[GeminiService, OpenRouterService]] = None
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    async def fetch_openrouter_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetch available models from OpenRouter API in real-time."""
        if not ASYNC_AVAILABLE:
            raise RuntimeError("aiohttp not available. Please install: pip install aiohttp")
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Content-Type": "application/json",
                }
                
                async with session.get("https://openrouter.ai/api/v1/models", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("data", [])
                        
                        # Categorize models by pricing
                        free_models = []
                        paid_models = []
                        
                        for model in models:
                            # Check if model has pricing information
                            pricing = model.get("pricing", {})
                            try:
                                prompt_cost = float(pricing.get("prompt", "0")) if pricing.get("prompt") else 0
                                completion_cost = float(pricing.get("completion", "0")) if pricing.get("completion") else 0
                                if prompt_cost > 0 or completion_cost > 0:
                                    paid_models.append(model)
                                else:
                                    free_models.append(model)
                            except (ValueError, TypeError):
                                # If we can't parse the pricing, consider it free
                                free_models.append(model)
                        
                        # Sort models by name for better presentation
                        try:
                            free_models.sort(key=lambda x: x.get("id", ""))
                            paid_models.sort(key=lambda x: x.get("id", ""))
                        except Exception:
                            # If sorting fails, continue without sorting
                            pass
                        all_models = free_models + paid_models  # All models with free first
                        
                        # Return categorized models
                        return {
                            "all": all_models,
                            "free": free_models,
                            "paid": paid_models
                        }
                    else:
                        error_text = await response.text()
                        raise Exception(f"Failed to fetch models: {response.status} - {error_text}")
        except Exception as e:
            print(f"Warning: Could not fetch OpenRouter models: {e}")
            return {"all": [], "free": [], "paid": []}
    
    def load_config(self) -> None:
        """Load AI configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Convert string values back to enums
                config_data['provider'] = AIProvider(config_data['provider'])
                config_data['model'] = AIModelType(config_data['model'])
                
                self.config = AIConfig(**config_data)
                
            except Exception as e:
                print(f"Warning: Could not load AI config: {e}")
                self.config = None
        else:
            self.config = None
    
    def save_config(self) -> None:
        """Save AI configuration to file."""
        if self.config:
            try:
                # Convert enums to strings for JSON serialization
                config_dict = asdict(self.config)
                config_dict['provider'] = self.config.provider.value
                config_dict['model'] = self.config.model.value
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2)
            except Exception as e:
                print(f"Error saving AI config: {e}")
    
    def configure(self, 
                 api_key: str,
                 model: str = "gemini-1.5-flash-latest",
                 max_tokens: int = 4000,
                 temperature: float = 0.7,
                 provider: AIProvider = AIProvider.GEMINI) -> bool:
        """Configure AI service."""
        try:
            # For OpenRouter, we allow any model string since it supports many models
            if provider == AIProvider.OPENROUTER:
                # Create a temporary enum-like object for OpenRouter models
                class OpenRouterModel:
                    def __init__(self, value):
                        self.value = value
                
                model_obj = OpenRouterModel(model)
            else:
                # For Gemini, validate against predefined models
                model_obj = AIModelType(model)
            
            self.config = AIConfig(
                api_key=api_key,
                provider=provider,
                model=model_obj,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            self.save_config()
            return True
            
        except (ValueError, Exception) as e:
            print(f"Configuration error: {e}")
            return False
    
    def is_configured(self) -> bool:
        """Check if AI service is properly configured."""
        return self.config is not None and bool(self.config.api_key)
    
    async def validate_api_key(self, api_key: str, model: str = "gemini-1.5-flash", provider: AIProvider = AIProvider.GEMINI) -> tuple[bool, str]:
        """Validate API key by making a test request."""
        if not ASYNC_AVAILABLE:
            return False, "aiohttp not available. Please install: pip install aiohttp"
        
        if not api_key.strip():
            return False, "API key cannot be empty"
        
        # Create temporary config for validation
        # For OpenRouter, we allow any model string
        if provider == AIProvider.OPENROUTER:
            # Create a temporary enum-like object for OpenRouter models
            class OpenRouterModel:
                def __init__(self, value):
                    self.value = value
            
            model_obj = OpenRouterModel(model)
        else:
            # For Gemini, validate against predefined models
            model_obj = AIModelType(model)
        
        temp_config = AIConfig(
            api_key=api_key,
            model=model_obj,
            max_tokens=100,
            temperature=0.1,
            timeout=10
        )
        
        try:
            # Create appropriate service instance based on provider
            if provider == AIProvider.OPENROUTER:
                service = OpenRouterService(temp_config)
            else:  # Default to Gemini
                service = GeminiService(temp_config)
            
            async with service as service_instance:
                messages = [{"role": "user", "content": "Hello"}]
                response = await service_instance.chat_completion(messages)
                
                if response.success:
                    return True, "API key is valid"
                else:
                    # Parse common error messages
                    error_msg = response.error or "Unknown error"
                    if "API_KEY_INVALID" in error_msg or "401" in error_msg:
                        return False, "Invalid API key"
                    elif "403" in error_msg:
                        return False, "API key access denied - check permissions"
                    elif "429" in error_msg:
                        return False, "Rate limit exceeded - API key may be valid but quota exceeded"
                    else:
                        return False, f"API validation failed: {error_msg}"
                        
        except Exception as e:
            error_str = str(e)
            if "API_KEY_INVALID" in error_str or "401" in error_str:
                return False, "Invalid API key"
            elif "403" in error_str:
                return False, "API key access denied"
            elif "timeout" in error_str.lower():
                return False, "Connection timeout - please check your internet connection"
            else:
                return False, f"Validation error: {error_str}"
    
    async def chat(self, 
                  message: str, 
                  use_context: bool = True,
                  model: Optional[str] = None) -> AIResponse:
        """Send chat message to AI service."""
        if not ASYNC_AVAILABLE:
            return AIResponse(
                content="",
                model="",
                usage={},
                timestamp=time.time(),
                response_time=0,
                success=False,
                error="aiohttp not available. Please install: pip install aiohttp"
            )
        
        if not self.is_configured():
            return AIResponse(
                content="",
                model="",
                usage={},
                timestamp=time.time(),
                response_time=0,
                success=False,
                error="AI service not configured. Use 'ai config' to set up."
            )
        
        try:
            # Create appropriate service instance based on provider
            if self.config.provider == AIProvider.OPENROUTER:
                service = OpenRouterService(self.config)
            else:  # Default to Gemini
                service = GeminiService(self.config)
            
            async with service as service_instance:
                # Build codebase-aware prompt if requested
                if use_context:
                    enhanced_message = service_instance.build_codebase_aware_prompt(message)
                else:
                    enhanced_message = message
                
                # Prepare messages
                messages = [{"role": "user", "content": enhanced_message}]
                
                # Set model if specified
                # Handle both enum and string model values
                config_model_value = self.config.model.value if hasattr(self.config.model, 'value') else self.config.model
                model_value = model or config_model_value
                
                # Get response
                response = await service_instance.chat_completion(messages, model=model_value)
                
                # Log to chat manager if available
                if service_instance.chat_manager and response.success:
                    service_instance.chat_manager.add_message("user", message)
                    service_instance.chat_manager.add_message("assistant", response.content)
                
                return response
                
        except Exception as e:
            return AIResponse(
                content="",
                model=self.config.model.value,
                usage={},
                timestamp=time.time(),
                response_time=0,
                success=False,
                error=f"Service error: {str(e)}"
            )


# Global AI service manager instance
_ai_manager_instance: Optional[AIServiceManager] = None


def get_ai_manager() -> AIServiceManager:
    """Get global AI service manager instance."""
    global _ai_manager_instance
    if _ai_manager_instance is None:
        _ai_manager_instance = AIServiceManager()
    return _ai_manager_instance


if __name__ == "__main__":
    # Simple test
    async def test():
        manager = get_ai_manager()
        if manager.is_configured():
            response = await manager.chat("Hello, how are you?")
            print(f"Response: {response.content}")
            print(f"Success: {response.success}")
        else:
            print("AI service not configured")
    
    # Run test
    asyncio.run(test())