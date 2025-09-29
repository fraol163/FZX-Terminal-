"""
Advanced Building Agent for FZX-Terminal
Full-featured AI-powered project generator with natural language processing,
terminal monitoring, bug detection, and perfect design generation
"""

import os
import sys
import json
import asyncio
import subprocess
import psutil
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum

# Import our enhanced AI provider
try:
    from enhanced_ai_provider import get_enhanced_ai_provider, AIProvider, AIModel
    from building_agent import BuildingAgent, BuildConfig, BuildType, Framework
    from project_templates import ProjectTemplates, TemplateConfig
except ImportError as e:
    print(f"Warning: Could not import enhanced components: {e}")
    get_enhanced_ai_provider = None

class ProjectComplexity(Enum):
    """Project complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

class DesignStyle(Enum):
    """Design style preferences."""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    CREATIVE = "creative"
    CORPORATE = "corporate"
    STARTUP = "startup"

@dataclass
class UserRequirements:
    """User requirements from natural language description."""
    project_name: str
    description: str
    build_type: BuildType
    framework: Optional[Framework] = None
    complexity: ProjectComplexity = ProjectComplexity.MODERATE
    design_style: DesignStyle = DesignStyle.MODERN
    features: List[str] = None
    target_audience: str = ""
    color_scheme: str = ""
    additional_requirements: str = ""
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

@dataclass
class GenerationResult:
    """Result of code generation."""
    success: bool
    message: str
    files_created: List[str]
    errors: List[str] = None
    warnings: List[str] = None
    performance_metrics: Dict[str, Any] = None
    design_recommendations: List[str] = None
    next_steps: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.design_recommendations is None:
            self.design_recommendations = []
        if self.next_steps is None:
            self.next_steps = []

class TerminalMonitor:
    """Monitor terminal status, processes, and system health."""
    
    def __init__(self):
        self.monitoring_active = False
        self.process_history = []
        self.error_log = []
        self.performance_data = []
    
    def start_monitoring(self) -> None:
        """Start terminal monitoring."""
        self.monitoring_active = True
        print("🔍 Terminal monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop terminal monitoring."""
        self.monitoring_active = False
        print("⏹️ Terminal monitoring stopped")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
                "active_processes": len(psutil.pids()),
                "python_processes": len([p for p in psutil.process_iter(['name']) if 'python' in p.info['name'].lower()]),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}
    
    def check_for_errors(self, output: str) -> List[str]:
        """Analyze output for errors and issues."""
        errors = []
        
        error_patterns = [
            ("SyntaxError", "Python syntax error detected"),
            ("ImportError", "Module import failure"),
            ("ModuleNotFoundError", "Missing module dependency"),
            ("TypeError", "Type mismatch error"),
            ("ValueError", "Invalid value error"),
            ("FileNotFoundError", "File or directory not found"),
            ("PermissionError", "Insufficient permissions"),
            ("ConnectionError", "Network connection issue"),
            ("TimeoutError", "Operation timeout"),
            ("npm ERR!", "NPM package error"),
            ("ERROR", "General error detected"),
            ("FAILED", "Operation failure"),
            ("Exception", "Exception occurred")
        ]
        
        for pattern, description in error_patterns:
            if pattern.lower() in output.lower():
                errors.append(f"{description}: Found '{pattern}' in output")
        
        return errors
    
    def analyze_performance(self, start_time: float, end_time: float, memory_before: float, memory_after: float) -> Dict[str, Any]:
        """Analyze performance metrics."""
        return {
            "execution_time": end_time - start_time,
            "memory_delta": memory_after - memory_before,
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "timestamp": datetime.now().isoformat()
        }

class CodeAnalyzer:
    """Analyze generated code for bugs, issues, and improvements."""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for issues."""
        if not file_path.exists():
            return {"error": "File not found"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "file_path": str(file_path),
                "line_count": len(content.splitlines()),
                "char_count": len(content),
                "issues": [],
                "suggestions": [],
                "quality_score": 0.0
            }
            
            # Basic analysis
            analysis.update(self._analyze_content(content, file_path.suffix))
            
            return analysis
            
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_content(self, content: str, file_extension: str) -> Dict[str, Any]:
        """Analyze file content based on type."""
        issues = []
        suggestions = []
        quality_score = 100.0
        
        if file_extension == '.py':
            return self._analyze_python(content)
        elif file_extension in ['.js', '.jsx', '.ts', '.tsx']:
            return self._analyze_javascript(content)
        elif file_extension in ['.html', '.htm']:
            return self._analyze_html(content)
        elif file_extension == '.css':
            return self._analyze_css(content)
        elif file_extension == '.json':
            return self._analyze_json(content)
        
        return {"issues": issues, "suggestions": suggestions, "quality_score": quality_score}
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """Analyze Python code."""
        issues = []
        suggestions = []
        quality_score = 100.0
        
        lines = content.splitlines()
        
        # Check for common Python issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Long lines
            if len(line) > 100:
                issues.append(f"Line {i}: Line too long ({len(line)} chars)")
                quality_score -= 2
            
            # Missing docstrings for functions/classes
            if line_stripped.startswith(('def ', 'class ')) and i < len(lines) - 1:
                next_line = lines[i].strip() if i < len(lines) else ""
                if not next_line.startswith('"""') and not next_line.startswith("'''"):
                    suggestions.append(f"Line {i}: Consider adding docstring")
                    quality_score -= 1
            
            # Unused imports (basic check)
            if line_stripped.startswith('import ') or line_stripped.startswith('from '):
                module_name = line_stripped.split()[1].split('.')[0]
                if module_name not in content[lines[i-1:]:]:
                    suggestions.append(f"Line {i}: Possibly unused import '{module_name}'")
                    quality_score -= 1
            
            # TODO comments
            if 'TODO' in line_stripped.upper():
                suggestions.append(f"Line {i}: TODO comment found")
        
        # Check for try-except blocks
        if 'try:' in content and content.count('try:') > content.count('except'):
            issues.append("Try blocks without corresponding except blocks")
            quality_score -= 5
        
        return {"issues": issues, "suggestions": suggestions, "quality_score": max(0, quality_score)}
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code."""
        issues = []
        suggestions = []
        quality_score = 100.0
        
        lines = content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Missing semicolons
            if line_stripped and not line_stripped.endswith((';', '{', '}', ')', ',')):
                if any(keyword in line_stripped for keyword in ['var ', 'let ', 'const ', 'return ']):
                    suggestions.append(f"Line {i}: Consider adding semicolon")
                    quality_score -= 0.5
            
            # Console.log statements
            if 'console.log' in line_stripped:
                suggestions.append(f"Line {i}: Console.log found - consider removing for production")
                quality_score -= 1
            
            # Long lines
            if len(line) > 120:
                issues.append(f"Line {i}: Line too long ({len(line)} chars)")
                quality_score -= 2
        
        # Check for modern JS features
        if 'var ' in content:
            suggestions.append("Consider using 'let' or 'const' instead of 'var'")
            quality_score -= 2
        
        return {"issues": issues, "suggestions": suggestions, "quality_score": max(0, quality_score)}
    
    def _analyze_html(self, content: str) -> Dict[str, Any]:
        """Analyze HTML code."""
        issues = []
        suggestions = []
        quality_score = 100.0
        
        # Basic HTML validation
        if '<html' not in content.lower():
            issues.append("Missing <html> tag")
            quality_score -= 10
        
        if '<head' not in content.lower():
            issues.append("Missing <head> section")
            quality_score -= 10
        
        if '<title' not in content.lower():
            suggestions.append("Consider adding <title> tag")
            quality_score -= 5
        
        # Accessibility checks
        if '<img' in content and 'alt=' not in content:
            issues.append("Image tags missing alt attributes")
            quality_score -= 15
        
        return {"issues": issues, "suggestions": suggestions, "quality_score": max(0, quality_score)}
    
    def _analyze_css(self, content: str) -> Dict[str, Any]:
        """Analyze CSS code."""
        issues = []
        suggestions = []
        quality_score = 100.0
        
        # Check for vendor prefixes
        prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
        for prefix in prefixes:
            if prefix in content:
                suggestions.append(f"Consider using autoprefixer instead of manual {prefix} prefixes")
                break
        
        # Check for !important usage
        important_count = content.count('!important')
        if important_count > 0:
            suggestions.append(f"Found {important_count} !important declarations - consider refactoring")
            quality_score -= important_count * 2
        
        return {"issues": issues, "suggestions": suggestions, "quality_score": max(0, quality_score)}
    
    def _analyze_json(self, content: str) -> Dict[str, Any]:
        """Analyze JSON files."""
        issues = []
        suggestions = []
        quality_score = 100.0
        
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            issues.append(f"JSON syntax error: {e}")
            quality_score = 0
        
        return {"issues": issues, "suggestions": suggestions, "quality_score": quality_score}

class AdvancedBuildingAgent:
    """Advanced building agent with comprehensive AI integration and monitoring."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.data_dir = self.workspace_path / ".terminal_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.ai_provider = get_enhanced_ai_provider() if get_enhanced_ai_provider else None
        self.base_agent = BuildingAgent(str(self.workspace_path))
        self.monitor = TerminalMonitor()
        self.code_analyzer = CodeAnalyzer()
        
        # Generation history
        self.generation_history = []
        self.history_file = self.data_dir / "generation_history.json"
        self._load_history()
    
    def _load_history(self) -> None:
        """Load generation history."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.generation_history = data.get('generations', [])
        except Exception:
            self.generation_history = []
    
    def _save_history(self) -> None:
        """Save generation history."""
        try:
            data = {
                'generations': self.generation_history,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception:
            pass
    
    async def setup_ai_provider(self, provider: str, api_key: str, interactive: bool = True) -> bool:
        """Set up AI provider with real-time model selection."""
        if not self.ai_provider:
            print("❌ Enhanced AI provider not available")
            return False
        
        try:
            # Convert provider string to enum
            provider_enum = AIProvider(provider.lower())
            
            print(f"🔄 Setting up {provider_enum.value} provider...")
            
            # Update models cache
            print("📡 Fetching latest models...")
            await self.ai_provider.update_models_cache(force=True)
            
            # Get available models for this provider
            available_models = self.ai_provider.get_available_models(provider_enum)
            
            if not available_models:
                print(f"❌ No models found for {provider_enum.value}")
                return False
            
            print(f"✅ Found {len(available_models)} models for {provider_enum.value}")
            
            # Interactive model selection
            if interactive:
                selected_model = await self.ai_provider.interactive_model_selection(provider_enum)
                if not selected_model:
                    return False
            else:
                # Use first available model
                selected_model = available_models[0]
            
            print(f"🧪 Validating API key with {selected_model.name}...")
            
            # Validate API key
            is_valid, message = await self.ai_provider.validate_api_key(
                provider_enum, api_key, selected_model.id
            )
            
            if not is_valid:
                print(f"❌ API key validation failed: {message}")
                return False
            
            print(f"✅ API key validated: {message}")
            
            # Configure provider
            success = self.ai_provider.configure_provider(
                provider=provider_enum,
                api_key=api_key,
                model_id=selected_model.id,
                max_tokens=4000,
                temperature=0.7
            )
            
            if success:
                print(f"🎉 Successfully configured {provider_enum.value} with {selected_model.name}")
                return True
            else:
                print("❌ Failed to configure provider")
                return False
                
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def _interactive_model_selection(self, models: List[AIModel]) -> Optional[AIModel]:
        """Interactive model selection."""
        print(f"\n📋 Available Models:")
        print("-" * 80)
        
        for i, model in enumerate(models[:20], 1):  # Show top 20 models
            cost_info = f"${model.cost_per_1k_tokens:.4f}/1k" if model.cost_per_1k_tokens > 0 else "Free"
            context_info = f"{model.context_length:,}" if model.context_length > 0 else "Unknown"
            
            print(f"{i:2d}. {model.name}")
            print(f"    ID: {model.id}")
            print(f"    Context: {context_info} tokens | Cost: {cost_info}")
            if model.description:
                desc = model.description[:80] + "..." if len(model.description) > 80 else model.description
                print(f"    Description: {desc}")
            print()
        
        while True:
            try:
                choice = input(f"Select model (1-{min(len(models), 20)}) or 'q' to quit: ").strip()
                
                if choice.lower() == 'q':
                    return None
                
                index = int(choice) - 1
                if 0 <= index < min(len(models), 20):
                    selected_model = models[index]
                    print(f"✅ Selected: {selected_model.name}")
                    return selected_model
                else:
                    print(f"❌ Please enter a number between 1 and {min(len(models), 20)}")
                    
            except ValueError:
                print("❌ Please enter a valid number")
    
    async def generate_from_description(self, description: str, project_name: str = None) -> GenerationResult:
        """Generate project from natural language description."""
        print(f"🧠 Analyzing description: '{description[:100]}...'")
        
        # Start monitoring
        self.monitor.start_monitoring()
        start_time = time.time()
        memory_before = psutil.virtual_memory().percent
        
        try:
            # Parse requirements from description
            requirements = await self._parse_requirements(description, project_name)
            
            print(f"📋 Parsed requirements:")
            print(f"   Project: {requirements.project_name}")
            print(f"   Type: {requirements.build_type.value}")
            print(f"   Framework: {requirements.framework.value if requirements.framework else 'Auto-detect'}")
            print(f"   Complexity: {requirements.complexity.value}")
            print(f"   Style: {requirements.design_style.value}")
            print(f"   Features: {', '.join(requirements.features[:5])}")
            
            # Generate project
            result = await self._generate_project(requirements)
            
            # Analyze generated code
            if result.success and result.files_created:
                print(f"🔍 Analyzing generated code...")
                await self._analyze_generated_code(result)
            
            # Performance analysis
            end_time = time.time()
            memory_after = psutil.virtual_memory().percent
            
            result.performance_metrics = self.monitor.analyze_performance(
                start_time, end_time, memory_before, memory_after
            )
            
            # Add to history
            history_entry = {
                "timestamp": datetime.now().isoformat(),
                "description": description,
                "requirements": asdict(requirements),
                "result": asdict(result),
                "performance": result.performance_metrics
            }
            
            self.generation_history.append(history_entry)
            self._save_history()
            
            return result
            
        except Exception as e:
            return GenerationResult(
                success=False,
                message=f"Generation failed: {str(e)}",
                files_created=[],
                errors=[str(e)]
            )
        finally:
            self.monitor.stop_monitoring()
    
    async def _parse_requirements(self, description: str, project_name: str = None) -> UserRequirements:
        """Parse natural language description into structured requirements."""
        
        # Use AI to parse if available
        if self.ai_provider and self.ai_provider.is_configured():
            return await self._ai_parse_requirements(description, project_name)
        
        # Fallback to rule-based parsing
        return self._rule_based_parse(description, project_name)
    
    async def _ai_parse_requirements(self, description: str, project_name: str = None) -> UserRequirements:
        """Use AI to parse requirements from description."""
        
        parsing_prompt = f"""
        Analyze this project description and extract structured requirements:
        
        Description: "{description}"
        Project Name: {project_name or "Auto-generate"}
        
        Please extract and format as JSON:
        {{
            "project_name": "extracted or generated name",
            "build_type": "web|api|desktop|mobile|cli|library",
            "framework": "react|vue|angular|express|fastapi|django|electron|flutter|null",
            "complexity": "simple|moderate|complex|enterprise",
            "design_style": "modern|classic|minimal|creative|corporate|startup",
            "features": ["feature1", "feature2"],
            "target_audience": "description of target users",
            "color_scheme": "preferred colors or theme",
            "additional_requirements": "any special requirements"
        }}
        
        Focus on understanding the user's intent and extracting actionable requirements.
        """
        
        try:
            response = await self.ai_provider.generate_text(
                parsing_prompt,
                context={
                    "task": "requirement_parsing",
                    "description": description
                }
            )
            
            if response["success"]:
                # Try to extract JSON from response
                content = response["content"]
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    parsed_data = json.loads(json_str)
                    
                    return UserRequirements(
                        project_name=parsed_data.get('project_name', project_name or 'my-project'),
                        description=description,
                        build_type=BuildType(parsed_data.get('build_type', 'web')),
                        framework=Framework(parsed_data['framework']) if parsed_data.get('framework') and parsed_data['framework'] != 'null' else None,
                        complexity=ProjectComplexity(parsed_data.get('complexity', 'moderate')),
                        design_style=DesignStyle(parsed_data.get('design_style', 'modern')),
                        features=parsed_data.get('features', []),
                        target_audience=parsed_data.get('target_audience', ''),
                        color_scheme=parsed_data.get('color_scheme', ''),
                        additional_requirements=parsed_data.get('additional_requirements', '')
                    )
            
        except Exception as e:
            print(f"⚠️ AI parsing failed: {e}, falling back to rule-based parsing")
        
        # Fallback to rule-based parsing
        return self._rule_based_parse(description, project_name)
    
    def _rule_based_parse(self, description: str, project_name: str = None) -> UserRequirements:
        """Rule-based parsing as fallback."""
        desc_lower = description.lower()
        
        # Determine build type
        build_type = BuildType.WEB  # default
        if any(word in desc_lower for word in ['api', 'server', 'backend', 'rest']):
            build_type = BuildType.API
        elif any(word in desc_lower for word in ['desktop', 'electron', 'tauri']):
            build_type = BuildType.DESKTOP
        elif any(word in desc_lower for word in ['mobile', 'app', 'android', 'ios', 'flutter']):
            build_type = BuildType.MOBILE
        elif any(word in desc_lower for word in ['cli', 'command', 'terminal', 'tool']):
            build_type = BuildType.CLI
        elif any(word in desc_lower for word in ['library', 'package', 'module']):
            build_type = BuildType.LIBRARY
        
        # Determine framework
        framework = None
        if 'react' in desc_lower:
            framework = Framework.REACT
        elif 'vue' in desc_lower:
            framework = Framework.VUE
        elif 'angular' in desc_lower:
            framework = Framework.ANGULAR
        elif 'express' in desc_lower:
            framework = Framework.EXPRESS
        elif 'fastapi' in desc_lower:
            framework = Framework.FASTAPI
        elif 'django' in desc_lower:
            framework = Framework.DJANGO
        elif 'electron' in desc_lower:
            framework = Framework.ELECTRON
        elif 'flutter' in desc_lower:
            framework = Framework.FLUTTER
        
        # Determine complexity
        complexity = ProjectComplexity.MODERATE
        if any(word in desc_lower for word in ['simple', 'basic', 'minimal']):
            complexity = ProjectComplexity.SIMPLE
        elif any(word in desc_lower for word in ['complex', 'advanced', 'sophisticated']):
            complexity = ProjectComplexity.COMPLEX
        elif any(word in desc_lower for word in ['enterprise', 'large', 'scalable']):
            complexity = ProjectComplexity.ENTERPRISE
        
        # Extract features
        features = []
        feature_keywords = {
            'authentication': ['auth', 'login', 'signin', 'signup', 'register'],
            'database': ['database', 'db', 'storage', 'data'],
            'payment': ['payment', 'billing', 'stripe', 'paypal'],
            'realtime': ['realtime', 'websocket', 'live', 'chat'],
            'responsive': ['responsive', 'mobile-first', 'adaptive'],
            'testing': ['test', 'testing', 'unit test', 'integration'],
            'deployment': ['deploy', 'deployment', 'docker', 'cloud'],
            'api': ['api', 'rest', 'graphql', 'endpoint']
        }
        
        for feature, keywords in feature_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                features.append(feature)
        
        return UserRequirements(
            project_name=project_name or 'my-project',
            description=description,
            build_type=build_type,
            framework=framework,
            complexity=complexity,
            design_style=DesignStyle.MODERN,
            features=features,
            target_audience="",
            color_scheme="",
            additional_requirements=""
        )
    
    async def _generate_project(self, requirements: UserRequirements) -> GenerationResult:
        """Generate project based on requirements."""
        try:
            # Create build config
            config = BuildConfig(
                name=requirements.project_name,
                build_type=requirements.build_type,
                framework=requirements.framework,
                features=requirements.features
            )
            
            print(f"🔨 Generating {requirements.build_type.value} project...")
            
            # Use base agent for basic generation
            base_result = await self.base_agent.build_project(config)
            
            if not base_result['success']:
                return GenerationResult(
                    success=False,
                    message=base_result['message'],
                    files_created=[]
                )
            
            result = GenerationResult(
                success=True,
                message=base_result['message'],
                files_created=base_result['files_created'],
                next_steps=base_result['next_steps']
            )
            
            # AI enhancement if available
            if self.ai_provider and self.ai_provider.is_configured():
                await self._ai_enhance_project(requirements, result)
            
            return result
            
        except Exception as e:
            return GenerationResult(
                success=False,
                message=f"Generation failed: {str(e)}",
                files_created=[],
                errors=[str(e)]
            )
    
    async def _ai_enhance_project(self, requirements: UserRequirements, result: GenerationResult) -> None:
        """Use AI to enhance generated project."""
        try:
            enhancement_prompt = f"""
            Enhance this {requirements.build_type.value} project based on requirements:
            
            Project: {requirements.project_name}
            Description: {requirements.description}
            Complexity: {requirements.complexity.value}
            Design Style: {requirements.design_style.value}
            Features: {', '.join(requirements.features)}
            Target Audience: {requirements.target_audience}
            
            Provide specific code improvements, additional features, and design recommendations.
            Focus on modern best practices, performance, and user experience.
            """
            
            response = await self.ai_provider.generate_text(
                enhancement_prompt,
                context={
                    "project_type": requirements.build_type.value,
                    "framework": requirements.framework.value if requirements.framework else None,
                    "features": requirements.features,
                    "files_created": result.files_created[:10]  # First 10 files
                }
            )
            
            if response["success"]:
                # Parse AI recommendations
                content = response["content"]
                
                # Extract recommendations (basic parsing)
                if "recommendations:" in content.lower():
                    recommendations_text = content.split("recommendations:", 1)[1].strip()
                    result.design_recommendations.extend([
                        line.strip("- ").strip() for line in recommendations_text.split("\n")
                        if line.strip() and not line.strip().startswith("#")
                    ][:10])  # Limit to 10 recommendations
                
        except Exception as e:
            result.warnings.append(f"AI enhancement failed: {str(e)}")
    
    async def _analyze_generated_code(self, result: GenerationResult) -> None:
        """Analyze generated code for issues and improvements."""
        try:
            total_issues = 0
            total_suggestions = 0
            quality_scores = []
            
            for file_path_str in result.files_created[:20]:  # Analyze first 20 files
                file_path = self.workspace_path / result.files_created[0].split('/')[0] / file_path_str
                
                if file_path.exists():
                    analysis = self.code_analyzer.analyze_file(file_path)
                    
                    if "issues" in analysis:
                        total_issues += len(analysis["issues"])
                        result.errors.extend(analysis["issues"])
                    
                    if "suggestions" in analysis:
                        total_suggestions += len(analysis["suggestions"])
                        result.warnings.extend(analysis["suggestions"])
                    
                    if "quality_score" in analysis:
                        quality_scores.append(analysis["quality_score"])
            
            # Calculate overall quality
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                result.performance_metrics["code_quality_score"] = avg_quality
                result.performance_metrics["total_issues"] = total_issues
                result.performance_metrics["total_suggestions"] = total_suggestions
                
                if avg_quality >= 90:
                    result.design_recommendations.append("✅ Excellent code quality detected")
                elif avg_quality >= 70:
                    result.design_recommendations.append("✨ Good code quality with minor improvements possible")
                else:
                    result.design_recommendations.append("⚠️ Code quality needs improvement - consider refactoring")
                    
        except Exception as e:
            result.warnings.append(f"Code analysis failed: {str(e)}")
    
    def get_terminal_status(self) -> Dict[str, Any]:
        """Get comprehensive terminal status."""
        status = {
            "system": self.monitor.get_system_status(),
            "ai_provider": {
                "configured": self.ai_provider.is_configured() if self.ai_provider else False,
                "provider": self.ai_provider.config.provider.value if self.ai_provider and self.ai_provider.is_configured() else None,
                "model": self.ai_provider.config.model_id if self.ai_provider and self.ai_provider.is_configured() else None
            },
            "generation_history": {
                "total_generations": len(self.generation_history),
                "successful_generations": len([g for g in self.generation_history if g.get('result', {}).get('success', False)]),
                "last_generation": self.generation_history[-1]['timestamp'] if self.generation_history else None
            },
            "workspace": {
                "path": str(self.workspace_path),
                "exists": self.workspace_path.exists(),
                "data_dir_exists": self.data_dir.exists()
            }
        }
        
        return status
    
    def get_generation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent generation history."""
        return self.generation_history[-limit:] if self.generation_history else []
    
    async def check_for_updates(self) -> Dict[str, Any]:
        """Check for AI model updates and system health."""
        results = {
            "models_updated": False,
            "new_models_count": 0,
            "system_healthy": True,
            "recommendations": []
        }
        
        try:
            if self.ai_provider:
                print("🔄 Checking for model updates...")
                old_count = len(self.ai_provider.get_available_models())
                
                updated = await self.ai_provider.update_models_cache(force=True)
                
                if updated:
                    new_count = len(self.ai_provider.get_available_models())
                    results["models_updated"] = True
                    results["new_models_count"] = new_count - old_count
                    
                    if results["new_models_count"] > 0:
                        results["recommendations"].append(f"Found {results['new_models_count']} new AI models")
            
            # System health check
            system_status = self.monitor.get_system_status()
            
            if "error" in system_status:
                results["system_healthy"] = False
                results["recommendations"].append("System monitoring error detected")
            else:
                if system_status.get("cpu_percent", 0) > 80:
                    results["recommendations"].append("High CPU usage detected")
                if system_status.get("memory_percent", 0) > 80:
                    results["recommendations"].append("High memory usage detected")
                    
        except Exception as e:
            results["system_healthy"] = False
            results["recommendations"].append(f"Update check failed: {str(e)}")
        
        return results

# Factory function
def get_advanced_building_agent(workspace_path: str = None) -> AdvancedBuildingAgent:
    """Get advanced building agent instance."""
    return AdvancedBuildingAgent(workspace_path)

if __name__ == "__main__":
    # Test the advanced building agent
    async def test_agent():
        agent = AdvancedBuildingAgent()
        
        # Test description parsing
        description = "Create a modern React web app for a todo list with authentication and dark mode"
        
        print(f"Testing description: {description}")
        
        # Parse requirements
        requirements = await agent._parse_requirements(description, "todo-app")
        
        print(f"\nParsed requirements:")
        print(f"  Name: {requirements.project_name}")
        print(f"  Type: {requirements.build_type.value}")
        print(f"  Framework: {requirements.framework.value if requirements.framework else 'None'}")
        print(f"  Features: {requirements.features}")
        
        # Get terminal status
        status = agent.get_terminal_status()
        print(f"\nTerminal Status:")
        print(f"  System CPU: {status['system'].get('cpu_percent', 'N/A')}%")
        print(f"  AI Configured: {status['ai_provider']['configured']}")
        print(f"  Total Generations: {status['generation_history']['total_generations']}")
    
    asyncio.run(test_agent())