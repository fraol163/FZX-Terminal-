"""
Universal Building Agent for FZX-Terminal
Intelligent project scaffolding, code generation, and build automation
"""

import os
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Safe imports with fallbacks
try:
    from ai_service import get_ai_manager
except ImportError:
    get_ai_manager = None

try:
    from project_templates import ProjectTemplates, TemplateConfig
except ImportError:
    ProjectTemplates = None
    TemplateConfig = None

class BuildType(Enum):
    """Supported build types."""
    WEB = "web"
    API = "api"
    DESKTOP = "desktop"
    MOBILE = "mobile"
    CLI = "cli"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    FULLSTACK = "fullstack"

class Framework(Enum):
    """Popular frameworks for each build type."""
    # Web
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXTJS = "nextjs"
    NUXT = "nuxt"
    
    # API
    EXPRESS = "express"
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"
    NESTJS = "nestjs"
    GO_GIN = "gin"
    
    # Desktop
    ELECTRON = "electron"
    TAURI = "tauri"
    FLUTTER_DESKTOP = "flutter-desktop"
    
    # Mobile
    REACT_NATIVE = "react-native"
    FLUTTER = "flutter"
    EXPO = "expo"

@dataclass
class BuildConfig:
    """Configuration for a build operation."""
    name: str
    build_type: BuildType
    framework: Optional[Framework] = None
    language: str = "javascript"
    features: List[str] = None
    template: str = "default"
    output_dir: str = None
    ai_enhanced: bool = True
    
    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.output_dir is None:
            self.output_dir = self.name

class BuildingAgent:
    """Universal building agent with AI integration."""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.templates_dir = Path(__file__).parent / "templates"
        
        # AI integration
        self.ai_manager = None
        if get_ai_manager:
            try:
                self.ai_manager = get_ai_manager()
            except Exception:
                pass
        
        # Template system
        self.project_templates = None
        if ProjectTemplates:
            self.project_templates = ProjectTemplates()
        
        # Build history
        self.build_history = []
        self.build_log_file = self.workspace_path / ".terminal_data" / "build_history.json"
        self._load_build_history()
    
    def _load_build_history(self) -> None:
        """Load previous build history."""
        try:
            if self.build_log_file.exists():
                with open(self.build_log_file, 'r', encoding='utf-8') as f:
                    self.build_history = json.load(f)
        except Exception:
            self.build_history = []
    
    def _save_build_history(self) -> None:
        """Save build history."""
        try:
            self.build_log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.build_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.build_history, f, indent=2, default=str)
        except Exception:
            pass
    
    def _log_build(self, config: BuildConfig, status: str, details: Dict[str, Any] = None) -> None:
        """Log build operation."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "config": asdict(config),
            "status": status,
            "details": details or {}
        }
        self.build_history.append(log_entry)
        self._save_build_history()
    
    def detect_project_type(self, path: Path = None) -> Tuple[BuildType, Framework, Dict[str, Any]]:
        """Intelligently detect project type and framework."""
        target_path = path or self.workspace_path
        
        # Check for common files and directories
        files = list(target_path.glob("*")) if target_path.exists() else []
        file_names = [f.name for f in files if f.is_file()]
        dir_names = [d.name for d in files if d.is_dir()]
        
        detection_info = {
            "files": file_names,
            "directories": dir_names,
            "confidence": 0.0,
            "indicators": []
        }
        
        # Web frameworks
        if "package.json" in file_names:
            detection_info["confidence"] = 0.8
            detection_info["indicators"].append("package.json found")
            
            if "next.config.js" in file_names or "next.config.ts" in file_names:
                return BuildType.WEB, Framework.NEXTJS, detection_info
            elif "nuxt.config.js" in file_names or "nuxt.config.ts" in file_names:
                return BuildType.WEB, Framework.NUXT, detection_info
            elif "angular.json" in file_names:
                return BuildType.WEB, Framework.ANGULAR, detection_info
            elif "svelte.config.js" in file_names:
                return BuildType.WEB, Framework.SVELTE, detection_info
            elif "vue.config.js" in file_names or "vite.config.js" in file_names:
                return BuildType.WEB, Framework.VUE, detection_info
            else:
                return BuildType.WEB, Framework.REACT, detection_info
        
        # Python frameworks
        if "requirements.txt" in file_names or "pyproject.toml" in file_names:
            detection_info["confidence"] = 0.7
            detection_info["indicators"].append("Python project files found")
            
            if "manage.py" in file_names:
                return BuildType.WEB, Framework.DJANGO, detection_info
            elif "app.py" in file_names or "main.py" in file_names:
                if any("flask" in f.lower() for f in file_names):
                    return BuildType.API, Framework.FLASK, detection_info
                elif any("fastapi" in f.lower() for f in file_names):
                    return BuildType.API, Framework.FASTAPI, detection_info
        
        # Go projects
        if "go.mod" in file_names:
            detection_info["confidence"] = 0.7
            detection_info["indicators"].append("Go module found")
            return BuildType.API, Framework.GO_GIN, detection_info
        
        # Mobile projects
        if "pubspec.yaml" in file_names:
            detection_info["confidence"] = 0.8
            detection_info["indicators"].append("Flutter project")
            return BuildType.MOBILE, Framework.FLUTTER, detection_info
        
        # Desktop projects
        if "tauri.conf.json" in file_names:
            detection_info["confidence"] = 0.9
            detection_info["indicators"].append("Tauri configuration found")
            return BuildType.DESKTOP, Framework.TAURI, detection_info
        
        # Default to web project
        return BuildType.WEB, Framework.REACT, detection_info
    
    def create_project(self, config: BuildConfig) -> Dict[str, Any]:
        """Create a project (synchronous wrapper for build_project)."""
        import asyncio
        return asyncio.run(self.build_project(config))
    
    async def build_project(self, config: BuildConfig) -> Dict[str, Any]:
        """Main build orchestration method."""
        result = {
            "success": False,
            "message": "",
            "details": {},
            "files_created": [],
            "next_steps": []
        }
        
        try:
            # Validate configuration
            if not self._validate_config(config):
                result["message"] = "Invalid configuration"
                return result
            
            # Create output directory
            output_path = self.workspace_path / config.output_dir
            if output_path.exists():
                result["message"] = f"Directory '{config.output_dir}' already exists"
                return result
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Log build start
            self._log_build(config, "started")
            
            # Generate project structure
            if self.project_templates:
                files_created = await self._generate_from_template(config, output_path)
            else:
                files_created = await self._generate_basic_structure(config, output_path)
            
            # AI-enhanced generation
            if config.ai_enhanced and self.ai_manager:
                await self._ai_enhance_project(config, output_path)
            
            # Set up development environment
            await self._setup_development_environment(config, output_path)
            
            result.update({
                "success": True,
                "message": f"Successfully created {config.build_type.value} project '{config.name}'",
                "files_created": files_created,
                "next_steps": self._generate_next_steps(config)
            })
            
            self._log_build(config, "completed", result)
            
        except Exception as e:
            result["message"] = f"Build failed: {str(e)}"
            self._log_build(config, "failed", {"error": str(e)})
        
        return result
    
    def _validate_config(self, config: BuildConfig) -> bool:
        """Validate build configuration."""
        if not config.name or not config.name.replace("-", "").replace("_", "").isalnum():
            return False
        
        if config.build_type not in BuildType:
            return False
        
        return True
    
    async def _generate_from_template(self, config: BuildConfig, output_path: Path) -> List[str]:
        """Generate project from template."""
        files_created = []
        
        # Use template system if available
        if self.project_templates:
            template_config = TemplateConfig(
                name=config.name,
                build_type=config.build_type,
                framework=config.framework,
                features=config.features
            )
            files_created = self.project_templates.generate_project(template_config, output_path)
        
        return files_created
    
    async def _generate_basic_structure(self, config: BuildConfig, output_path: Path) -> List[str]:
        """Generate basic project structure without templates."""
        files_created = []
        
        # Create basic files based on build type
        if config.build_type == BuildType.WEB:
            files_created = self._create_web_project(config, output_path)
        elif config.build_type == BuildType.API:
            files_created = self._create_api_project(config, output_path)
        elif config.build_type == BuildType.CLI:
            files_created = self._create_cli_project(config, output_path)
        
        return files_created
    
    def _create_web_project(self, config: BuildConfig, output_path: Path) -> List[str]:
        """Create basic web project structure with AI-generated content."""
        files = [
            "package.json",
            "index.html",
            "src/main.js",
            "src/App.js",
            "src/components/Header.js",
            "public/favicon.ico",
            "README.md",
            ".gitignore"
        ]
        
        # Create directories first
        for file_path in files:
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate content for key files using AI if available
        if self.ai_manager and self.ai_manager.is_configured():
            self._generate_web_project_content_with_ai(config, output_path, files)
        else:
            # Fallback to basic file creation
            for file_path in files:
                full_path = output_path / file_path
                full_path.touch()
        
        return files
    
    def _create_api_project(self, config: BuildConfig, output_path: Path) -> List[str]:
        """Create basic API project structure with AI-generated content."""
        files = [
            "package.json",
            "server.js",
            "routes/index.js",
            "models/user.js",
            "middleware/auth.js",
            "config/database.js",
            "tests/api.test.js",
            "README.md",
            ".env.example",
            ".gitignore"
        ]
        
        # Create directories first
        for file_path in files:
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate content for key files using AI if available
        if self.ai_manager and self.ai_manager.is_configured():
            self._generate_api_project_content_with_ai(config, output_path, files)
        else:
            # Fallback to basic file creation
            for file_path in files:
                full_path = output_path / file_path
                full_path.touch()
        
        return files
    
    def _create_cli_project(self, config: BuildConfig, output_path: Path) -> List[str]:
        """Create basic CLI project structure with AI-generated content."""
        files = [
            "package.json",
            "bin/cli.js",
            "lib/index.js",
            "lib/commands/help.js",
            "tests/cli.test.js",
            "README.md",
            ".gitignore"
        ]
        
        # Create directories first
        for file_path in files:
            full_path = output_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate content for key files using AI if available
        if self.ai_manager and self.ai_manager.is_configured():
            self._generate_cli_project_content_with_ai(config, output_path, files)
        else:
            # Fallback to basic file creation
            for file_path in files:
                full_path = output_path / file_path
                full_path.touch()
        
        return files
    
    def _generate_api_project_content_with_ai(self, config: BuildConfig, output_path: Path, files: List[str]) -> None:
        """Generate API project content using AI."""
        try:
            # Create a prompt for generating project content
            framework_name = config.framework.value if config.framework else "Node.js with Express"
            prompt = f"""
            Generate complete, functional code for a {config.build_type.value} project named '{config.name}' using {framework_name}.
            
            Project Requirements:
            - Project Name: {config.name}
            - Framework: {framework_name}
            - Features: {', '.join(config.features) if config.features else 'Standard API features'}
            
            Please provide complete, runnable code for the following files:
            
            1. package.json - With appropriate dependencies
            2. server.js - Main server entry point
            3. routes/index.js - Basic routes
            4. models/user.js - User model example
            5. middleware/auth.js - Authentication middleware
            6. config/database.js - Database configuration
            7. tests/api.test.js - Basic API tests
            8. README.md - Project documentation
            9. .env.example - Environment variables example
            10. .gitignore - Standard git ignore patterns
            
            Format your response as a JSON object with file paths as keys and file contents as values.
            Example format: {{"package.json": "...content...", "server.js": "...content..."}}
            
            Make sure the code is modern, follows best practices, and is fully functional.
            """
            
            import asyncio
            async def generate_content():
                response = await self.ai_manager.chat(prompt, use_context=False)
                return response
            
            # Run the async function
            try:
                response = asyncio.run(generate_content())
                if response.success:
                    # Parse AI response to extract file contents
                    import json
                    import re
                    
                    # Try to extract JSON from response
                    content = response.content
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if json_match:
                        try:
                            file_contents = json.loads(json_match.group())
                            
                            # Create files with AI-generated content
                            for file_path, file_content in file_contents.items():
                                full_path = output_path / file_path
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                with open(full_path, 'w', encoding='utf-8') as f:
                                    f.write(file_content)
                            
                            # Create any remaining files that weren't in the AI response
                            for file_path in files:
                                full_path = output_path / file_path
                                if not full_path.exists():
                                    full_path.parent.mkdir(parents=True, exist_ok=True)
                                    full_path.touch()
                        except json.JSONDecodeError:
                            # Fallback to empty files if JSON parsing fails
                            print(f"⚠️ AI response parsing failed, creating empty files")
                            for file_path in files:
                                full_path = output_path / file_path
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                full_path.touch()
                    else:
                        # Fallback to empty files if no JSON found
                        print(f"⚠️ No JSON found in AI response, creating empty files")
                        for file_path in files:
                            full_path = output_path / file_path
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            full_path.touch()
                else:
                    # Fallback to empty files if AI fails
                    print(f"⚠️ AI generation failed: {response.error}, creating empty files")
                    for file_path in files:
                        full_path = output_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
            except Exception:
                # Fallback to empty files if AI fails
                for file_path in files:
                        full_path = output_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
        except Exception:
            # Final fallback to empty files
            for file_path in files:
                full_path = output_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch()
    
    def _generate_cli_project_content_with_ai(self, config: BuildConfig, output_path: Path, files: List[str]) -> None:
        """Generate CLI project content using AI."""
        try:
            # Create a prompt for generating project content
            prompt = f"""
            Generate complete, functional code for a {config.build_type.value} project named '{config.name}'.
            
            Project Requirements:
            - Project Name: {config.name}
            - Features: {', '.join(config.features) if config.features else 'Standard CLI features'}
            
            Please provide complete, runnable code for the following files:
            
            1. package.json - With appropriate dependencies
            2. bin/cli.js - Main CLI entry point
            3. lib/index.js - Main library code
            4. lib/commands/help.js - Help command
            5. tests/cli.test.js - Basic CLI tests
            6. README.md - Project documentation
            7. .gitignore - Standard git ignore patterns
            
            Format your response as a JSON object with file paths as keys and file contents as values.
            Example format: {{"package.json": "...content...", "bin/cli.js": "...content..."}}
            
            Make sure the code is modern, follows best practices, and is fully functional.
            """
            
            import asyncio
            async def generate_content():
                response = await self.ai_manager.chat(prompt, use_context=False)
                return response
            
            # Run the async function
            try:
                response = asyncio.run(generate_content())
                if response.success:
                    # Parse AI response to extract file contents
                    import json
                    import re
                    
                    # Try to extract JSON from response
                    content = response.content
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if json_match:
                        try:
                            file_contents = json.loads(json_match.group())
                            
                            # Create files with AI-generated content
                            for file_path, file_content in file_contents.items():
                                full_path = output_path / file_path
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                with open(full_path, 'w', encoding='utf-8') as f:
                                    f.write(file_content)
                            
                            # Create any remaining files that weren't in the AI response
                            for file_path in files:
                                full_path = output_path / file_path
                                if not full_path.exists():
                                    full_path.parent.mkdir(parents=True, exist_ok=True)
                                    full_path.touch()
                        except json.JSONDecodeError:
                            # Fallback to empty files if JSON parsing fails
                            for file_path in files:
                                full_path = output_path / file_path
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                full_path.touch()
                    else:
                        # Fallback to empty files if no JSON found
                        for file_path in files:
                            full_path = output_path / file_path
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            full_path.touch()
                else:
                    # Fallback to empty files if AI fails
                    for file_path in files:
                        full_path = output_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
            except Exception:
                # Fallback to empty files if AI fails
                for file_path in files:
                        full_path = output_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
        except Exception:
            # Final fallback to empty files
            for file_path in files:
                full_path = output_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch()
    
    async def _ai_enhance_project(self, config: BuildConfig, output_path: Path) -> None:
        """Use AI to enhance generated project."""
        if not self.ai_manager:
            return
        
        try:
            # Generate AI-enhanced code snippets
            prompt = f"Generate enhanced code for a {config.build_type.value} project named '{config.name}' using {config.framework.value if config.framework else 'default'} framework."
            # AI enhancement logic would go here
            pass
        except Exception:
            # AI enhancement is optional
            pass
    
    def _generate_web_project_content_with_ai(self, config: BuildConfig, output_path: Path, files: List[str]) -> None:
        """Generate web project content using AI."""
        print(f"🚀 _generate_web_project_content_with_ai called with {len(files)} files")
        try:
            # Create a prompt for generating project content
            framework_name = config.framework.value if config.framework else "modern web technologies"
            prompt = f"""
            Generate complete, functional code for a {config.build_type.value} project named '{config.name}' using {framework_name}.
            
            Project Requirements:
            - Project Name: {config.name}
            - Framework: {framework_name}
            - Features: {', '.join(config.features) if config.features else 'Standard features'}
            
            Please provide complete, runnable code for the following files:
            
            1. package.json - With appropriate dependencies
            2. index.html - Basic HTML structure
            3. src/main.js - Main JavaScript entry point
            4. src/App.js - Main application component
            5. src/components/Header.js - Header component
            6. README.md - Project documentation
            7. .gitignore - Standard git ignore patterns
            
            Format your response as a JSON object with file paths as keys and file contents as values.
            Example format: {{"package.json": "...content...", "index.html": "...content..."}}
            
            Make sure the code is modern, follows best practices, and is fully functional.
            """
            
            import asyncio
            async def generate_content():
                response = await self.ai_manager.chat(prompt, use_context=False)
                return response
            
            # Run the async function
            try:
                response = asyncio.run(generate_content())
                print(f"🤖 AI response received, success: {response.success}")
                if response.success:
                    # Parse AI response to extract file contents
                    import json
                    import re
                    
                    # Try to extract JSON from response
                    content = response.content
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    
                    if json_match:
                        try:
                            file_contents = json.loads(json_match.group())
                            print(f"✅ Parsed AI response with {len(file_contents)} files")
                            
                            # Create files with AI-generated content
                            for file_path, file_content in file_contents.items():
                                full_path = output_path / file_path
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                with open(full_path, 'w', encoding='utf-8') as f:
                                    f.write(file_content)
                                print(f"   📄 Created {file_path} ({len(file_content)} chars)")
                            
                            # Create any remaining files that weren't in the AI response
                            for file_path in files:
                                full_path = output_path / file_path
                                if not full_path.exists():
                                    full_path.parent.mkdir(parents=True, exist_ok=True)
                                    full_path.touch()
                                    print(f"   📄 Created empty {file_path}")
                        except json.JSONDecodeError:
                            # Fallback to empty files if JSON parsing fails
                            print(f"⚠️ AI response parsing failed, creating empty files")
                            for file_path in files:
                                full_path = output_path / file_path
                                full_path.parent.mkdir(parents=True, exist_ok=True)
                                full_path.touch()
                    else:
                        # Fallback to empty files if no JSON found
                        print(f"⚠️ No JSON found in AI response, creating empty files")
                        for file_path in files:
                            full_path = output_path / file_path
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            full_path.touch()
                else:
                    # Fallback to empty files if AI fails
                    print(f"⚠️ AI generation failed: {response.error}, creating empty files")
                    for file_path in files:
                        full_path = output_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
            except Exception as e:
                # Fallback to empty files if AI fails
                print(f"⚠️ AI generation exception: {e}, creating empty files")
                for file_path in files:
                        full_path = output_path / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.touch()
        except Exception as e:
            # Final fallback to empty files
            print(f"⚠️ AI generation failed with exception: {e}, creating empty files")
            for file_path in files:
                full_path = output_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch()
    
    async def _setup_development_environment(self, config: BuildConfig, output_path: Path) -> None:
        """Set up development environment."""
        try:
            if config.build_type in [BuildType.WEB, BuildType.API] and config.language == "javascript":
                # Initialize npm project
                subprocess.run(["npm", "init", "-y"], cwd=output_path, check=False)
        except Exception:
            # Environment setup is optional
            pass
    
    def _generate_next_steps(self, config: BuildConfig) -> List[str]:
        """Generate recommended next steps."""
        steps = [
            f"Navigate to project: cd {config.output_dir}",
            "Install dependencies",
            "Start development server",
            "Begin coding your application"
        ]
        
        if config.build_type == BuildType.WEB:
            steps.extend([
                "Configure build tools",
                "Set up testing framework",
                "Deploy to hosting platform"
            ])
        elif config.build_type == BuildType.API:
            steps.extend([
                "Configure database connection",
                "Set up authentication",
                "Create API documentation"
            ])
        
        return steps
    
    def get_build_suggestions(self, context: str = "") -> List[Dict[str, Any]]:
        """Get intelligent build suggestions based on context."""
        suggestions = []
        
        # Detect current project and suggest enhancements
        current_type, current_framework, detection_info = self.detect_project_type()
        
        if detection_info["confidence"] > 0.5:
            suggestions.append({
                "type": "enhancement",
                "title": f"Enhance current {current_type.value} project",
                "description": f"Add features to your {current_framework.value} project",
                "command": f"build enhance {current_type.value}"
            })
        
        # Common project suggestions
        common_builds = [
            (BuildType.WEB, Framework.REACT, "Modern React web application"),
            (BuildType.API, Framework.EXPRESS, "Node.js REST API server"),
            (BuildType.CLI, None, "Command-line tool"),
            (BuildType.FULLSTACK, Framework.NEXTJS, "Full-stack Next.js application")
        ]
        
        for build_type, framework, description in common_builds:
            suggestions.append({
                "type": "create",
                "title": f"Create {build_type.value} project",
                "description": description,
                "command": f"build {build_type.value} my-{build_type.value}-app{' --framework ' + framework.value if framework else ''}"
            })
        
        return suggestions
    
    def get_build_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent build history."""
        return self.build_history[-limit:] if self.build_history else []

# Factory function for easy import
def get_building_agent(workspace_path: str = None) -> BuildingAgent:
    """Get building agent instance."""
    return BuildingAgent(workspace_path)

# CLI interface for testing
if __name__ == "__main__":
    agent = BuildingAgent()
    
    # Test project detection
    build_type, framework, info = agent.detect_project_type()
    print(f"Detected: {build_type.value} project with {framework.value} framework")
    print(f"Confidence: {info['confidence']:.1%}")
    
    # Show suggestions
    suggestions = agent.get_build_suggestions()
    print(f"\nBuild suggestions:")
    for i, suggestion in enumerate(suggestions[:5], 1):
        print(f"{i}. {suggestion['title']} - {suggestion['description']}")
