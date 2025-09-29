"""
Enhanced AI Provider System for FZX-Terminal Building Agent
Supports OpenRouter, Gemini, and other providers with real-time model detection
"""

import os
import asyncio
import json
import aiohttp
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta

class AIProvider(Enum):
    """Supported AI providers."""
    OPENROUTER = "openrouter"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"

@dataclass
class AIModel:
    """AI model information."""
    id: str
    name: str
    provider: AIProvider
    context_length: int
    max_tokens: int
    cost_per_1k_tokens: float
    description: str
    capabilities: List[str]
    last_updated: str
    
    def __post_init__(self):
        if isinstance(self.capabilities, str):
            self.capabilities = [self.capabilities]

@dataclass
class AIProviderConfig:
    """Configuration for AI provider."""
    provider: AIProvider
    api_key: str
    base_url: str
    model_id: str
    max_tokens: int = 4000
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    enable_streaming: bool = True
    enable_context_integration: bool = True

class EnhancedAIProvider:
    """Enhanced AI provider with OpenRouter support and real-time model checking."""
    
    def __init__(self):
        self.config_dir = Path.cwd() / ".terminal_data" / "ai_config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.models_cache_file = self.config_dir / "models_cache.json"
        self.config_file = self.config_dir / "provider_config.json"
        
        self.config: Optional[AIProviderConfig] = None
        self.available_models: Dict[str, AIModel] = {}
        self.last_model_check: Optional[datetime] = None
        
        # Provider configurations
        self.provider_configs = {
            AIProvider.OPENROUTER: {
                "base_url": "https://openrouter.ai/api/v1",
                "models_endpoint": "https://openrouter.ai/api/v1/models",
                "chat_endpoint": "/chat/completions",
                "headers_template": {
                    "Authorization": "Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/FZX-Terminal",
                    "X-Title": "FZX-Terminal Building Agent"
                }
            },
            AIProvider.GEMINI: {
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "models_endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
                "chat_endpoint": "/models/{model}:generateContent",
                "headers_template": {
                    "Content-Type": "application/json"
                }
            }
        }
        
        self.load_config()
        
    def load_config(self) -> None:
        """Load AI provider configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.config = AIProviderConfig(**data)
        except Exception:
            self.config = None
    
    def save_config(self) -> None:
        """Save AI provider configuration."""
        try:
            if self.config:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.config), f, indent=2, default=str)
        except Exception:
            pass
    
    def load_models_cache(self) -> None:
        """Load cached models."""
        try:
            if self.models_cache_file.exists():
                with open(self.models_cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                self.available_models = {}
                for model_id, model_data in data.get('models', {}).items():
                    model_data['provider'] = AIProvider(model_data['provider'])
                    self.available_models[model_id] = AIModel(**model_data)
                    
                self.last_model_check = datetime.fromisoformat(data.get('last_check', datetime.now().isoformat()))
        except Exception:
            self.available_models = {}
            self.last_model_check = None
    
    def save_models_cache(self) -> None:
        """Save models cache."""
        try:
            data = {
                'models': {model_id: asdict(model) for model_id, model in self.available_models.items()},
                'last_check': self.last_model_check.isoformat() if self.last_model_check else datetime.now().isoformat()
            }
            
            with open(self.models_cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass
    
    async def fetch_openrouter_models(self) -> List[AIModel]:
        """Fetch latest models from OpenRouter with comprehensive model data."""
        models = []
        try:
            async with aiohttp.ClientSession() as session:
                # Use OpenRouter's public models endpoint
                async with session.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={
                        "User-Agent": "FZX-Terminal-BuildingAgent/1.0",
                        "Accept": "application/json"
                    },
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"🔍 Found {len(data.get('data', []))} models from OpenRouter")
                        
                        for model_data in data.get('data', []):
                            try:
                                # Extract pricing information
                                pricing = model_data.get('pricing', {})
                                prompt_cost = float(pricing.get('prompt', '0'))
                                completion_cost = float(pricing.get('completion', '0'))
                                
                                # Calculate average cost per 1k tokens
                                avg_cost = (prompt_cost + completion_cost) / 2
                                
                                # Extract context length
                                context_length = model_data.get('context_length', 4096)
                                if isinstance(context_length, str):
                                    # Handle string values like "128k"
                                    if 'k' in context_length.lower():
                                        context_length = int(float(context_length.lower().replace('k', '')) * 1000)
                                    elif 'm' in context_length.lower():
                                        context_length = int(float(context_length.lower().replace('m', '')) * 1000000)
                                    else:
                                        context_length = int(context_length)
                                
                                # Determine capabilities
                                capabilities = ['chat', 'completion']
                                if 'vision' in model_data.get('id', '').lower() or 'gpt-4' in model_data.get('id', '').lower():
                                    capabilities.append('vision')
                                if 'code' in model_data.get('id', '').lower() or 'codellama' in model_data.get('id', '').lower():
                                    capabilities.append('code')
                                
                                # Create model with enhanced information
                                model = AIModel(
                                    id=model_data['id'],
                                    name=model_data.get('name', model_data['id']),
                                    provider=AIProvider.OPENROUTER,
                                    context_length=context_length,
                                    max_tokens=model_data.get('top_provider', {}).get('max_completion_tokens', 
                                                            min(4000, context_length // 4)),
                                    cost_per_1k_tokens=avg_cost,
                                    description=model_data.get('description', ''),
                                    capabilities=capabilities,
                                    last_updated=datetime.now().isoformat()
                                )
                                models.append(model)
                                
                            except (ValueError, KeyError, TypeError) as e:
                                # Skip malformed model data
                                continue
                                
                    else:
                        print(f"⚠️ OpenRouter API returned status {response.status}")
                        
        except asyncio.TimeoutError:
            print("⚠️ OpenRouter API request timed out")
        except Exception as e:
            print(f"⚠️ Error fetching OpenRouter models: {e}")
        
        # Sort models by cost (free first, then by price)
        models.sort(key=lambda m: (m.cost_per_1k_tokens, m.name))
        
        print(f"✅ Successfully fetched {len(models)} OpenRouter models")
        
        # Show some stats
        free_models = [m for m in models if m.cost_per_1k_tokens == 0]
        paid_models = [m for m in models if m.cost_per_1k_tokens > 0]
        
        print(f"   📦 Free models: {len(free_models)}")
        print(f"   💰 Paid models: {len(paid_models)}")
        
        if free_models:
            print(f"   🎯 Popular free models: {', '.join([m.name for m in free_models[:5]])}")
        
        return models
    
    async def fetch_gemini_models(self) -> List[AIModel]:
        """Fetch latest Gemini models."""
        models = []
        
        # Known Gemini models (since API doesn't provide list endpoint)
        known_models = [
            {
                'id': 'gemini-2.0-flash-exp',
                'name': 'Gemini 2.0 Flash (Experimental)',
                'context_length': 1000000,
                'max_tokens': 8192,
                'description': 'Latest experimental Gemini model with enhanced capabilities'
            },
            {
                'id': 'gemini-1.5-pro-latest',
                'name': 'Gemini 1.5 Pro (Latest)',
                'context_length': 2000000,
                'max_tokens': 8192,
                'description': 'Most capable Gemini model for complex tasks'
            },
            {
                'id': 'gemini-1.5-flash-latest',
                'name': 'Gemini 1.5 Flash (Latest)',
                'context_length': 1000000,
                'max_tokens': 8192,
                'description': 'Fast and efficient Gemini model'
            },
            {
                'id': 'gemini-1.5-flash-8b-latest',
                'name': 'Gemini 1.5 Flash 8B (Latest)',
                'context_length': 1000000,
                'max_tokens': 8192,
                'description': 'Lightweight and fast Gemini model'
            }
        ]
        
        for model_data in known_models:
            model = AIModel(
                id=model_data['id'],
                name=model_data['name'],
                provider=AIProvider.GEMINI,
                context_length=model_data['context_length'],
                max_tokens=model_data['max_tokens'],
                cost_per_1k_tokens=0.0,  # Free tier available
                description=model_data['description'],
                capabilities=['chat', 'completion', 'vision'],
                last_updated=datetime.now().isoformat()
            )
            models.append(model)
        
        return models
    
    async def update_models_cache(self, force: bool = False) -> bool:
        """Update models cache from providers."""
        try:
            # Check if we need to update (daily check)
            if not force and self.last_model_check:
                if datetime.now() - self.last_model_check < timedelta(hours=24):
                    self.load_models_cache()
                    return True
            
            print("🔄 Fetching latest AI models...")
            
            # Fetch models from all providers
            all_models = []
            
            # OpenRouter models
            try:
                openrouter_models = await self.fetch_openrouter_models()
                all_models.extend(openrouter_models)
                print(f"✅ Found {len(openrouter_models)} OpenRouter models")
            except Exception as e:
                print(f"⚠️ OpenRouter fetch failed: {e}")
            
            # Gemini models
            try:
                gemini_models = await self.fetch_gemini_models()
                all_models.extend(gemini_models)
                print(f"✅ Found {len(gemini_models)} Gemini models")
            except Exception as e:
                print(f"⚠️ Gemini fetch failed: {e}")
            
            # Update cache
            self.available_models = {model.id: model for model in all_models}
            self.last_model_check = datetime.now()
            self.save_models_cache()
            
            print(f"✅ Updated model cache with {len(self.available_models)} total models")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update models cache: {e}")
            return False
    
    def get_available_models(self, provider: Optional[AIProvider] = None) -> List[AIModel]:
        """Get available models, optionally filtered by provider."""
        if not self.available_models:
            self.load_models_cache()
        
        models = list(self.available_models.values())
        
        if provider:
            models = [model for model in models if model.provider == provider]
        
        # Sort by provider, then by name
        models.sort(key=lambda m: (m.provider.value, m.name))
        
        return models
    
    def get_model_by_id(self, model_id: str) -> Optional[AIModel]:
        """Get model by ID."""
        if not self.available_models:
            self.load_models_cache()
        
        return self.available_models.get(model_id)
    
    def configure_provider(self, provider: AIProvider, api_key: str, model_id: str, **kwargs) -> bool:
        """Configure AI provider."""
        try:
            base_url = self.provider_configs.get(provider, {}).get("base_url", "")
            
            self.config = AIProviderConfig(
                provider=provider,
                api_key=api_key,
                base_url=base_url,
                model_id=model_id,
                max_tokens=kwargs.get('max_tokens', 4000),
                temperature=kwargs.get('temperature', 0.7),
                top_p=kwargs.get('top_p', 1.0),
                frequency_penalty=kwargs.get('frequency_penalty', 0.0),
                presence_penalty=kwargs.get('presence_penalty', 0.0),
                enable_streaming=kwargs.get('enable_streaming', True),
                enable_context_integration=kwargs.get('enable_context_integration', True)
            )
            
            self.save_config()
            return True
            
        except Exception:
            return False
    
    async def validate_api_key(self, provider: AIProvider, api_key: str, model_id: str) -> Tuple[bool, str]:
        """Validate API key with a test request."""
        try:
            if provider == AIProvider.OPENROUTER:
                return await self._validate_openrouter_key(api_key, model_id)
            elif provider == AIProvider.GEMINI:
                return await self._validate_gemini_key(api_key, model_id)
            else:
                return False, f"Provider {provider.value} validation not implemented"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    async def _validate_openrouter_key(self, api_key: str, model_id: str) -> Tuple[bool, str]:
        """Validate OpenRouter API key."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://github.com/FZX-Terminal",
                    "X-Title": "FZX-Terminal Building Agent",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model_id,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
                
                async with session.post(
                    f"{self.provider_configs[AIProvider.OPENROUTER]['base_url']}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True, "API key is valid"
                    elif response.status == 401:
                        return False, "Invalid API key"
                    elif response.status == 402:
                        return False, "Insufficient credits"
                    else:
                        text = await response.text()
                        return False, f"API error: {response.status} - {text[:100]}"
                        
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    async def _validate_gemini_key(self, api_key: str, model_id: str) -> Tuple[bool, str]:
        """Validate Gemini API key."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent"
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "contents": [{"parts": [{"text": "Hello"}]}],
                    "generationConfig": {"maxOutputTokens": 10}
                }
                
                async with session.post(
                    f"{url}?key={api_key}",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True, "API key is valid"
                    elif response.status == 400:
                        return False, "Invalid API key or model"
                    elif response.status == 403:
                        return False, "API key does not have access to this model"
                    else:
                        text = await response.text()
                        return False, f"API error: {response.status} - {text[:100]}"
                        
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    async def generate_text(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using configured provider."""
        if not self.config:
            return {
                "success": False,
                "error": "AI provider not configured",
                "content": "",
                "model": "",
                "usage": {}
            }
        
        try:
            if self.config.provider == AIProvider.OPENROUTER:
                return await self._generate_openrouter(prompt, context)
            elif self.config.provider == AIProvider.GEMINI:
                return await self._generate_gemini(prompt, context)
            else:
                return {
                    "success": False,
                    "error": f"Provider {self.config.provider.value} not implemented",
                    "content": "",
                    "model": self.config.model_id,
                    "usage": {}
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Generation error: {str(e)}",
                "content": "",
                "model": self.config.model_id,
                "usage": {}
            }
    
    async def _generate_openrouter(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using OpenRouter."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "HTTP-Referer": "https://github.com/FZX-Terminal",
                    "X-Title": "FZX-Terminal Building Agent",
                    "Content-Type": "application/json"
                }
                
                messages = [{"role": "user", "content": prompt}]
                
                # Add context if provided
                if context and self.config.enable_context_integration:
                    context_prompt = self._build_context_prompt(context)
                    if context_prompt:
                        messages.insert(0, {"role": "system", "content": context_prompt})
                
                payload = {
                    "model": self.config.model_id,
                    "messages": messages,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "top_p": self.config.top_p,
                    "frequency_penalty": self.config.frequency_penalty,
                    "presence_penalty": self.config.presence_penalty,
                    "stream": False  # For simplicity, disable streaming for now
                }
                
                async with session.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            "success": True,
                            "content": data["choices"][0]["message"]["content"],
                            "model": data.get("model", self.config.model_id),
                            "usage": data.get("usage", {}),
                            "response_time": 0.0,  # Could track this
                            "error": None
                        }
                    else:
                        text = await response.text()
                        return {
                            "success": False,
                            "error": f"API error: {response.status} - {text}",
                            "content": "",
                            "model": self.config.model_id,
                            "usage": {}
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"OpenRouter generation error: {str(e)}",
                "content": "",
                "model": self.config.model_id,
                "usage": {}
            }
    
    async def _generate_gemini(self, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate text using Gemini."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config.model_id}:generateContent"
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                # Build content with context
                text_content = prompt
                if context and self.config.enable_context_integration:
                    context_prompt = self._build_context_prompt(context)
                    if context_prompt:
                        text_content = f"{context_prompt}\n\n{prompt}"
                
                payload = {
                    "contents": [{"parts": [{"text": text_content}]}],
                    "generationConfig": {
                        "maxOutputTokens": self.config.max_tokens,
                        "temperature": self.config.temperature,
                        "topP": self.config.top_p
                    }
                }
                
                async with session.post(
                    f"{url}?key={self.config.api_key}",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        content = ""
                        if "candidates" in data and data["candidates"]:
                            candidate = data["candidates"][0]
                            if "content" in candidate and "parts" in candidate["content"]:
                                content = candidate["content"]["parts"][0].get("text", "")
                        
                        return {
                            "success": True,
                            "content": content,
                            "model": self.config.model_id,
                            "usage": data.get("usageMetadata", {}),
                            "response_time": 0.0,
                            "error": None
                        }
                    else:
                        text = await response.text()
                        return {
                            "success": False,
                            "error": f"API error: {response.status} - {text}",
                            "content": "",
                            "model": self.config.model_id,
                            "usage": {}
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Gemini generation error: {str(e)}",
                "content": "",
                "model": self.config.model_id,
                "usage": {}
            }
    
    def _build_context_prompt(self, context: Dict[str, Any]) -> str:
        """Build context prompt from provided context."""
        if not context:
            return ""
        
        context_parts = []
        
        if "project_type" in context:
            context_parts.append(f"Project Type: {context['project_type']}")
        
        if "framework" in context:
            context_parts.append(f"Framework: {context['framework']}")
        
        if "description" in context:
            context_parts.append(f"Description: {context['description']}")
        
        if "features" in context:
            context_parts.append(f"Required Features: {', '.join(context['features'])}")
        
        if "current_files" in context:
            context_parts.append(f"Current Files: {', '.join(context['current_files'][:10])}")
        
        if context_parts:
            return f"Context:\n{chr(10).join(context_parts)}\n"
        
        return ""
    
    def is_configured(self) -> bool:
        """Check if provider is configured."""
        return self.config is not None
    
    def get_current_model(self) -> Optional[AIModel]:
        """Get currently configured model."""
        if not self.config:
            return None
        
        return self.get_model_by_id(self.config.model_id)
    
    async def interactive_model_selection(self, provider: Optional[AIProvider] = None) -> Optional[AIModel]:
        """Enhanced interactive model selection with categorization and filtering."""
        models = self.get_available_models(provider)
        
        if not models:
            print("❌ No models available. Please update models cache first.")
            return None
        
        # Categorize models
        free_models = [m for m in models if m.cost_per_1k_tokens == 0]
        low_cost_models = [m for m in models if 0 < m.cost_per_1k_tokens <= 0.001]
        mid_cost_models = [m for m in models if 0.001 < m.cost_per_1k_tokens <= 0.01]
        premium_models = [m for m in models if m.cost_per_1k_tokens > 0.01]
        
        categories = {
            '🆓 Free Models': free_models,
            '💰 Low Cost Models (≤$0.001/1k)': low_cost_models,
            '💸 Mid Cost Models ($0.001-$0.01/1k)': mid_cost_models,
            '💎 Premium Models (>$0.01/1k)': premium_models
        }
        
        while True:
            print("\n" + "="*80)
            print(f"🤖 AI MODEL SELECTION ({len(models)} total models available)")
            print("="*80)
            
            # Show categories
            for i, (category_name, category_models) in enumerate(categories.items(), 1):
                if category_models:
                    print(f"{i}. {category_name} ({len(category_models)} models)")
            
            print("\nOptions:")
            print("📝 Type 's <search_term>' to search models (e.g., 's gpt' or 's vision')")
            print("🔄 Type 'r' to refresh models from providers")
            print("❌ Type 'q' to quit")
            
            choice = input("\nSelect category (1-4), search, refresh, or quit: ").strip().lower()
            
            if choice == 'q':
                return None
            elif choice == 'r':
                print("🔄 Refreshing models...")
                await self.update_models_cache(force=True)
                models = self.get_available_models(provider)
                continue
            elif choice.startswith('s '):
                search_term = choice[2:].strip()
                filtered_models = [
                    m for m in models 
                    if search_term.lower() in m.name.lower() or 
                       search_term.lower() in m.id.lower() or
                       search_term.lower() in m.description.lower()
                ]
                if filtered_models:
                    selected = await self._display_and_select_models(filtered_models, f"Search: '{search_term}'")
                    if selected:
                        return selected
                else:
                    print(f"❌ No models found matching '{search_term}'")
                    input("Press Enter to continue...")
                continue
            
            try:
                category_index = int(choice) - 1
                category_items = list(categories.items())
                
                if 0 <= category_index < len(category_items):
                    category_name, category_models = category_items[category_index]
                    if category_models:
                        selected = await self._display_and_select_models(category_models, category_name)
                        if selected:
                            return selected
                    else:
                        print(f"❌ No models available in {category_name}")
                        input("Press Enter to continue...")
                else:
                    print(f"❌ Please enter a number between 1 and {len(category_items)}")
                    input("Press Enter to continue...")
            except ValueError:
                print("❌ Please enter a valid option")
                input("Press Enter to continue...")
    
    async def _display_and_select_models(self, models: List[AIModel], category_title: str) -> Optional[AIModel]:
        """Display models in a category and allow selection."""
        models_per_page = 20
        current_page = 0
        total_pages = (len(models) + models_per_page - 1) // models_per_page
        
        while True:
            start_idx = current_page * models_per_page
            end_idx = min(start_idx + models_per_page, len(models))
            page_models = models[start_idx:end_idx]
            
            print("\n" + "="*80)
            print(f"📋 {category_title}")
            if total_pages > 1:
                print(f"📄 Page {current_page + 1} of {total_pages} (showing {start_idx + 1}-{end_idx} of {len(models)})")
            print("="*80)
            
            # Display models
            for i, model in enumerate(page_models, 1):
                cost_info = f"${model.cost_per_1k_tokens:.6f}/1k" if model.cost_per_1k_tokens > 0 else "FREE"
                context_info = f"{model.context_length:,}" if model.context_length > 0 else "Unknown"
                
                print(f"{i:2d}. {model.name}")
                print(f"    🆔 ID: {model.id}")
                print(f"    📏 Context: {context_info} tokens | 💰 Cost: {cost_info}")
                
                # Show capabilities
                if model.capabilities:
                    caps = ', '.join(model.capabilities)
                    print(f"    🔧 Capabilities: {caps}")
                
                # Show description (truncated)
                if model.description:
                    desc = model.description[:60] + "..." if len(model.description) > 60 else model.description
                    print(f"    📖 {desc}")
                print()
            
            # Navigation options
            options = []
            if total_pages > 1:
                if current_page > 0:
                    options.append("'p' for previous page")
                if current_page < total_pages - 1:
                    options.append("'n' for next page")
            options.extend(["'b' to go back", "'q' to quit"])
            
            print(f"Select model (1-{len(page_models)}), {', '.join(options)}: ", end="")
            choice = input().strip().lower()
            
            if choice == 'q':
                return None
            elif choice == 'b':
                return None
            elif choice == 'p' and current_page > 0:
                current_page -= 1
                continue
            elif choice == 'n' and current_page < total_pages - 1:
                current_page += 1
                continue
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(page_models):
                    selected_model = page_models[index]
                    print(f"\n✅ Selected: {selected_model.name}")
                    print(f"🆔 Model ID: {selected_model.id}")
                    print(f"💰 Cost: ${selected_model.cost_per_1k_tokens:.6f}/1k tokens")
                    print(f"📏 Context Length: {selected_model.context_length:,} tokens")
                    return selected_model
                else:
                    print(f"❌ Please enter a number between 1 and {len(page_models)}")
                    input("Press Enter to continue...")
            except ValueError:
                print("❌ Please enter a valid option")
                input("Press Enter to continue...")

# Factory function
def get_enhanced_ai_provider() -> EnhancedAIProvider:
    """Get enhanced AI provider instance."""
    return EnhancedAIProvider()

if __name__ == "__main__":
    # Test the enhanced AI provider
    async def test_provider():
        provider = EnhancedAIProvider()
        
        # Update models cache
        await provider.update_models_cache(force=True)
        
        # Show available models
        models = provider.get_available_models()
        print(f"\nFound {len(models)} total models:")
        
        for model in models[:10]:  # Show first 10
            print(f"  {model.provider.value}: {model.name} ({model.id})")
            print(f"    Context: {model.context_length:,} tokens")
            print(f"    Cost: ${model.cost_per_1k_tokens:.4f}/1k tokens")
            print()
    
    asyncio.run(test_provider())