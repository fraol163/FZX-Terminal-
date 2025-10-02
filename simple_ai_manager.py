"""
Simple AI Manager for FZX-Terminal
Supports both OpenRouter and Gemini providers with chat functionality only
"""

import os
import json
import time
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class AIProvider(Enum):
    """Supported AI providers."""
    GEMINI = "gemini"
    OPENROUTER = "openrouter"

class AIModelType(Enum):
    """Available models."""
    # Gemini models
    GEMINI_1_5_PRO_LATEST = "gemini-1.5-pro-latest"
    GEMINI_1_5_FLASH_LATEST = "gemini-1.5-flash-latest"
    GEMINI_1_5_FLASH_8B = "gemini-1.5-flash-8b"
    GEMINI_2_0_FLASH_EXP = "gemini-2.0-flash-exp"
    
    # OpenRouter models (popular free ones)
    OPENROUTER_NEXUS = "nexusflow/nexus-raven-v2-13b"
    OPENROUTER_MISTRAL = "mistralai/mistral-7b-instruct"
    OPENROUTER_ZEPHYR = "huggingfaceh4/zephyr-7b-beta"
    OPENROUTER_OPENCHAT = "openchat/openchat-3.5"

@dataclass
class AIConfig:
    """AI service configuration."""
    api_key: str
    provider: AIProvider
    model: str
    max_tokens: int = 4000
    temperature: float = 0.7
    timeout: int = 30
    context_window: int = 32000
    enable_context_integration: bool = True

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

class SimpleAIManager:
    """Simple AI manager with chat functionality for both providers."""
    
    def __init__(self):
        self.project_root = Path(os.getcwd())
        self.config_file = self.project_root / ".terminal_data" / "ai_config.json"
        self.config: Optional[AIConfig] = None
        
        # Ensure config directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self) -> None:
        """Load AI configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Convert string values back to enums
                config_data['provider'] = AIProvider(config_data['provider'])
                
                # Filter out parameters not supported by this AIConfig class
                supported_params = {'api_key', 'provider', 'model', 'max_tokens', 'temperature', 
                                  'timeout', 'context_window', 'enable_context_integration'}
                filtered_config_data = {k: v for k, v in config_data.items() if k in supported_params}
                
                self.config = AIConfig(**filtered_config_data)
                
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
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_dict, f, indent=2)
            except Exception as e:
                print(f"Error saving AI config: {e}")
    
    def configure(self, 
                 api_key: str,
                 provider: str,
                 model: str,
                 max_tokens: int = 4000,
                 temperature: float = 0.7) -> bool:
        """Configure AI service."""
        try:
            provider_enum = AIProvider(provider)
            
            self.config = AIConfig(
                api_key=api_key,
                provider=provider_enum,
                model=model,
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
    
    async def validate_api_key(self, api_key: str, provider: str, model: str) -> tuple[bool, str]:
        """Validate API key by making a test request."""
        if not api_key.strip():
            return False, "API key cannot be empty"
        
        try:
            provider_enum = AIProvider(provider)
            
            # Create temporary config for validation
            temp_config = AIConfig(
                api_key=api_key,
                provider=provider_enum,
                model=model,
                max_tokens=100,
                temperature=0.1,
                timeout=10
            )
            
            # Test with a simple message
            messages = [{"role": "user", "content": "Hello"}]
            response = await self._make_request(messages, temp_config)
            
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
    
    async def chat(self, message: str, use_context: bool = True) -> AIResponse:
        """Send chat message to AI service."""
        if not self.is_configured():
            return AIResponse(
                content="",
                model="",
                usage={},
                timestamp=time.time(),
                response_time=0,
                success=False,
                error="AI service not configured. Use 'ai config setup' to set up."
            )
        
        try:
            # Prepare messages
            messages = [{"role": "user", "content": message}]
            
            # Get response
            response = await self._make_request(messages)
            
            return response
                
        except Exception as e:
            return AIResponse(
                content="",
                model=self.config.model,
                usage={},
                timestamp=time.time(),
                response_time=0,
                success=False,
                error=f"Service error: {str(e)}"
            )
    
    async def _make_request(self, messages: List[Dict[str, str]], 
                           config: Optional[AIConfig] = None) -> AIResponse:
        """Make API request to the configured provider."""
        config = config or self.config
        start_time = time.time()
        
        try:
            if config.provider == AIProvider.GEMINI:
                return await self._make_gemini_request(messages, config)
            elif config.provider == AIProvider.OPENROUTER:
                return await self._make_openrouter_request(messages, config)
            else:
                raise Exception(f"Unsupported provider: {config.provider}")
                
        except Exception as e:
            response_time = time.time() - start_time
            return AIResponse(
                content="",
                model=config.model,
                usage={},
                timestamp=time.time(),
                response_time=response_time,
                success=False,
                error=str(e)
            )
    
    async def _make_gemini_request(self, messages: List[Dict[str, str]], 
                                 config: AIConfig) -> AIResponse:
        """Make request to Google Gemini API."""
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.model}:generateContent"
            headers = {"Content-Type": "application/json"}
            params = {"key": config.api_key}
            
            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                role = "user" if msg.get("role") == "user" else "model"
                content = msg.get("content", "")
                
                contents.append({
                    "role": role,
                    "parts": [{"text": content}]
                })
            
            data = {
                "contents": contents,
                "generationConfig": {
                    "maxOutputTokens": config.max_tokens,
                    "temperature": config.temperature,
                    "topP": 0.8,
                    "topK": 40
                }
            }
            
            async with session.post(url, json=data, headers=headers, params=params,
                                  timeout=aiohttp.ClientTimeout(total=config.timeout)) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Extract response content
                    candidates = response_data.get("candidates", [])
                    if not candidates:
                        raise Exception("No response candidates returned")
                    
                    content = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    usage = response_data.get("usageMetadata", {})
                    response_time = time.time() - start_time
                    
                    return AIResponse(
                        content=content,
                        model=config.model,
                        usage=usage,
                        timestamp=time.time(),
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"Gemini API error: {response.status} - {error_text}")
    
    async def _make_openrouter_request(self, messages: List[Dict[str, str]], 
                                     config: AIConfig) -> AIResponse:
        """Make request to OpenRouter API."""
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            url = "https://openrouter.ai/api/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "HTTP-Referer": "https://github.com/FZX-Terminal",
                "X-Title": "FZX-Terminal",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": config.model,
                "messages": messages,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature
            }
            
            async with session.post(url, json=data, headers=headers,
                                  timeout=aiohttp.ClientTimeout(total=config.timeout)) as response:
                if response.status == 200:
                    response_data = await response.json()
                    
                    # Extract response content
                    choices = response_data.get("choices", [])
                    if not choices:
                        raise Exception("No response choices returned")
                    
                    content = choices[0].get("message", {}).get("content", "")
                    usage = response_data.get("usage", {})
                    response_time = time.time() - start_time
                    
                    return AIResponse(
                        content=content,
                        model=config.model,
                        usage=usage,
                        timestamp=time.time(),
                        response_time=response_time,
                        success=True
                    )
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error: {response.status} - {error_text}")

# Global AI manager instance
_ai_manager_instance: Optional[SimpleAIManager] = None

def get_simple_ai_manager() -> SimpleAIManager:
    """Get global simple AI manager instance."""
    global _ai_manager_instance
    if _ai_manager_instance is None:
        _ai_manager_instance = SimpleAIManager()
    return _ai_manager_instance

if __name__ == "__main__":
    # Simple test
    async def test():
        manager = get_simple_ai_manager()
        if manager.is_configured():
            response = await manager.chat("Hello, how are you?")
            print(f"Response: {response.content}")
            print(f"Success: {response.success}")
        else:
            print("AI service not configured")
    
    # Run test
    asyncio.run(test())