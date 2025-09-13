"""
Project Context Inference System for AI Terminal Workflow
Intelligent project fingerprinting and context detection

Addresses user struggles:
- AI not understanding project context automatically
- Manual context setup for each new project
- Missing project-specific optimizations
- Lack of intelligent project type detection
"""

import os
import sys
import json
import time
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from collections import defaultdict, Counter
from dataclasses import dataclass, asdict
from enum import Enum

class ProjectType(Enum):
    """Detected project types."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    NODE = "node"
    DJANGO = "django"
    FLASK = "flask"
    FASTAPI = "fastapi"
    NEXTJS = "nextjs"
    NUXTJS = "nuxtjs"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    CSHARP = "csharp"
    CPP = "cpp"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    TERRAFORM = "terraform"
    ANSIBLE = "ansible"
    MACHINE_LEARNING = "ml"
    DATA_SCIENCE = "data_science"
    WEB_SCRAPING = "web_scraping"
    API = "api"
    CLI = "cli"
    LIBRARY = "library"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    MIXED = "mixed"
    UNKNOWN = "unknown"

class ConfidenceLevel(Enum):
    """Confidence levels for project detection."""
    VERY_HIGH = 0.9
    HIGH = 0.7
    MEDIUM = 0.5
    LOW = 0.3
    VERY_LOW = 0.1

@dataclass
class ProjectFingerprint:
    """Project fingerprint with detected characteristics."""
    project_type: ProjectType
    confidence: float
    evidence: List[str]
    technologies: List[str]
    frameworks: List[str]
    languages: List[str]
    build_tools: List[str]
    package_managers: List[str]
    testing_frameworks: List[str]
    deployment_targets: List[str]
    development_patterns: List[str]
    project_structure: Dict[str, Any]
    dependencies: Dict[str, List[str]]
    metadata: Dict[str, Any]
    
    def __post_init__(self):
        for field in ['evidence', 'technologies', 'frameworks', 'languages', 
                     'build_tools', 'package_managers', 'testing_frameworks',
                     'deployment_targets', 'development_patterns']:
            if getattr(self, field) is None:
                setattr(self, field, [])
        
        if self.dependencies is None:
            self.dependencies = {}
        if self.metadata is None:
            self.metadata = {}
        if self.project_structure is None:
            self.project_structure = {}

class ProjectDetector:
    """Detects project types and characteristics."""
    
    def __init__(self):
        self.detection_rules = {
            ProjectType.PYTHON: {
                'files': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock'],
                'extensions': ['.py'],
                'directories': ['__pycache__', '.pytest_cache', 'venv', 'env'],
                'patterns': [r'import\s+\w+', r'from\s+\w+\s+import', r'def\s+\w+\(', r'class\s+\w+'],
                'confidence_boost': 0.8
            },
            ProjectType.JAVASCRIPT: {
                'files': ['package.json', 'package-lock.json', 'yarn.lock'],
                'extensions': ['.js', '.mjs'],
                'directories': ['node_modules', 'dist', 'build'],
                'patterns': [r'require\(', r'import\s+.*from', r'export\s+', r'function\s+\w+'],
                'confidence_boost': 0.8
            },
            ProjectType.TYPESCRIPT: {
                'files': ['tsconfig.json', 'tslint.json', 'package.json'],
                'extensions': ['.ts', '.tsx'],
                'directories': ['node_modules', 'dist', 'build'],
                'patterns': [r'interface\s+\w+', r'type\s+\w+\s*=', r'import\s+.*from'],
                'confidence_boost': 0.9
            },
            ProjectType.REACT: {
                'files': ['package.json'],
                'extensions': ['.jsx', '.tsx'],
                'directories': ['src', 'public', 'build'],
                'patterns': [r'import\s+React', r'from\s+["\']react["\']', r'jsx', r'useState', r'useEffect'],
                'dependencies': ['react', 'react-dom'],
                'confidence_boost': 0.9
            },
            ProjectType.VUE: {
                'files': ['vue.config.js', 'package.json'],
                'extensions': ['.vue'],
                'directories': ['src', 'dist'],
                'patterns': [r'<template>', r'<script>', r'<style>', r'Vue\.'],
                'dependencies': ['vue'],
                'confidence_boost': 0.9
            },
            ProjectType.DJANGO: {
                'files': ['manage.py', 'settings.py', 'requirements.txt'],
                'directories': ['migrations', 'static', 'templates'],
                'patterns': [r'from\s+django', r'import\s+django', r'INSTALLED_APPS', r'urlpatterns'],
                'dependencies': ['django'],
                'confidence_boost': 0.9
            },
            ProjectType.FLASK: {
                'files': ['app.py', 'wsgi.py', 'requirements.txt'],
                'patterns': [r'from\s+flask', r'import\s+Flask', r'@app\.route', r'Flask\(__name__\)'],
                'dependencies': ['flask'],
                'confidence_boost': 0.9
            },
            ProjectType.FASTAPI: {
                'files': ['main.py', 'requirements.txt'],
                'patterns': [r'from\s+fastapi', r'import\s+FastAPI', r'@app\.(get|post|put|delete)', r'FastAPI\(\)'],
                'dependencies': ['fastapi', 'uvicorn'],
                'confidence_boost': 0.9
            },
            ProjectType.NEXTJS: {
                'files': ['next.config.js', 'package.json'],
                'directories': ['pages', '.next'],
                'patterns': [r'import\s+.*from\s+["\']next', r'getStaticProps', r'getServerSideProps'],
                'dependencies': ['next'],
                'confidence_boost': 0.9
            },
            ProjectType.RUST: {
                'files': ['Cargo.toml', 'Cargo.lock'],
                'extensions': ['.rs'],
                'directories': ['target', 'src'],
                'patterns': [r'fn\s+\w+', r'struct\s+\w+', r'impl\s+', r'use\s+'],
                'confidence_boost': 0.9
            },
            ProjectType.GO: {
                'files': ['go.mod', 'go.sum'],
                'extensions': ['.go'],
                'patterns': [r'package\s+\w+', r'import\s+', r'func\s+\w+', r'type\s+\w+'],
                'confidence_boost': 0.9
            },
            ProjectType.DOCKER: {
                'files': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore'],
                'patterns': [r'FROM\s+', r'RUN\s+', r'COPY\s+', r'EXPOSE\s+'],
                'confidence_boost': 0.8
            },
            ProjectType.MACHINE_LEARNING: {
                'files': ['requirements.txt', 'environment.yml'],
                'extensions': ['.ipynb'],
                'directories': ['data', 'models', 'notebooks'],
                'patterns': [r'import\s+(numpy|pandas|sklearn|tensorflow|torch|keras)', 
                           r'from\s+(sklearn|tensorflow|torch|keras)', r'plt\.', r'np\.'],
                'dependencies': ['numpy', 'pandas', 'scikit-learn', 'tensorflow', 'torch', 'keras'],
                'confidence_boost': 0.8
            }
        }
        
        self.framework_indicators = {
            'testing': {
                'pytest': [r'import\s+pytest', r'def\s+test_', r'@pytest\.'],
                'unittest': [r'import\s+unittest', r'class\s+.*Test', r'def\s+test_'],
                'jest': [r'describe\(', r'it\(', r'test\(', r'expect\('],
                'mocha': [r'describe\(', r'it\('],
                'jasmine': [r'describe\(', r'it\(', r'expect\('],
            },
            'build_tools': {
                'webpack': ['webpack.config.js', 'webpack.config.ts'],
                'vite': ['vite.config.js', 'vite.config.ts'],
                'rollup': ['rollup.config.js'],
                'parcel': ['.parcelrc'],
                'gulp': ['gulpfile.js'],
                'grunt': ['Gruntfile.js'],
                'make': ['Makefile'],
                'cmake': ['CMakeLists.txt']
            },
            'deployment': {
                'kubernetes': ['deployment.yaml', 'service.yaml', 'ingress.yaml', 'kustomization.yaml'],
                'terraform': ['.tf', 'terraform.tfvars'],
                'ansible': ['playbook.yml', 'inventory'],
                'heroku': ['Procfile'],
                'vercel': ['vercel.json'],
                'netlify': ['netlify.toml', '_redirects']
            }
        }
    
    def detect_project_type(self, project_path: str) -> ProjectFingerprint:
        """Detect project type and characteristics."""
        project_path = Path(project_path)
        
        type_scores = defaultdict(float)
        evidence = defaultdict(list)
        
        file_structure = self._scan_project_structure(project_path)
        
        for project_type, rules in self.detection_rules.items():
            score = 0.0
            type_evidence = []
            
            for file_name in rules.get('files', []):
                if file_name in file_structure['files']:
                    score += 0.3
                    type_evidence.append(f"Found {file_name}")
            
            for ext in rules.get('extensions', []):
                ext_count = file_structure['extensions'].get(ext, 0)
                if ext_count > 0:
                    score += min(0.2 * ext_count / 10, 0.4)
                    type_evidence.append(f"Found {ext_count} {ext} files")
            
            for dir_name in rules.get('directories', []):
                if dir_name in file_structure['directories']:
                    score += 0.1
                    type_evidence.append(f"Found {dir_name} directory")
            
            dependencies_score = self._check_dependencies(project_path, rules.get('dependencies', []))
            score += dependencies_score
            if dependencies_score > 0:
                type_evidence.append(f"Found matching dependencies")
            
            patterns_score = self._check_code_patterns(project_path, rules.get('patterns', []))
            score += patterns_score
            if patterns_score > 0:
                type_evidence.append(f"Found matching code patterns")
            
            if score > 0:
                score *= rules.get('confidence_boost', 1.0)
            
            type_scores[project_type] = score
            evidence[project_type] = type_evidence
        
        if not type_scores:
            primary_type = ProjectType.UNKNOWN
            confidence = 0.0
            primary_evidence = ["No clear project indicators found"]
        else:
            primary_type = max(type_scores.keys(), key=lambda x: type_scores[x])
            confidence = min(type_scores[primary_type], 1.0)
            primary_evidence = evidence[primary_type]
        
        technologies = self._detect_technologies(project_path, file_structure)
        frameworks = self._detect_frameworks(project_path, file_structure)
        languages = self._detect_languages(file_structure)
        build_tools = self._detect_build_tools(project_path)
        package_managers = self._detect_package_managers(project_path)
        testing_frameworks = self._detect_testing_frameworks(project_path)
        deployment_targets = self._detect_deployment_targets(project_path)
        development_patterns = self._detect_development_patterns(project_path, file_structure)
        
        fingerprint = ProjectFingerprint(
            project_type=primary_type,
            confidence=confidence,
            evidence=primary_evidence,
            technologies=technologies,
            frameworks=frameworks,
            languages=languages,
            build_tools=build_tools,
            package_managers=package_managers,
            testing_frameworks=testing_frameworks,
            deployment_targets=deployment_targets,
            development_patterns=development_patterns,
            project_structure=file_structure,
            dependencies=self._extract_dependencies(project_path),
            metadata={
                'detection_time': datetime.now().isoformat(),
                'project_path': str(project_path),
                'all_type_scores': dict(type_scores)
            }
        )
        
        return fingerprint
    
    def _scan_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Scan project structure and collect file information."""
        structure = {
            'files': set(),
            'directories': set(),
            'extensions': Counter(),
            'file_count': 0,
            'directory_count': 0,
            'total_size': 0
        }
        
        try:
            for item in project_path.rglob('*'):
                if any(part.startswith('.') for part in item.parts[len(project_path.parts):]):
                    continue
                if any(ignore in str(item) for ignore in ['node_modules', '__pycache__', '.git', 'venv', 'env']):
                    continue
                
                if item.is_file():
                    structure['files'].add(item.name)
                    structure['extensions'][item.suffix.lower()] += 1
                    structure['file_count'] += 1
                    try:
                        structure['total_size'] += item.stat().st_size
                    except (OSError, PermissionError):
                        pass
                elif item.is_dir():
                    structure['directories'].add(item.name)
                    structure['directory_count'] += 1
        
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not scan project structure: {e}")
        
        return structure
    
    def _check_dependencies(self, project_path: Path, target_dependencies: List[str]) -> float:
        """Check for specific dependencies in package files."""
        if not target_dependencies:
            return 0.0
        
        score = 0.0
        
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                all_deps = {}
                all_deps.update(package_data.get('dependencies', {}))
                all_deps.update(package_data.get('devDependencies', {}))
                
                for dep in target_dependencies:
                    if dep in all_deps:
                        score += 0.2
            except (json.JSONDecodeError, OSError):
                pass
        
        requirements_txt = project_path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    requirements = f.read().lower()
                    
                for dep in target_dependencies:
                    if dep.lower() in requirements:
                        score += 0.2
            except OSError:
                pass
        
        pyproject_toml = project_path / 'pyproject.toml'
        if pyproject_toml.exists():
            try:
                with open(pyproject_toml, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                for dep in target_dependencies:
                    if dep.lower() in content:
                        score += 0.2
            except OSError:
                pass
        
        return min(score, 0.6)
    
    def _check_code_patterns(self, project_path: Path, patterns: List[str]) -> float:
        """Check for code patterns in project files."""
        if not patterns:
            return 0.0
        
        score = 0.0
        files_checked = 0
        max_files_to_check = 20
        
        try:
            for file_path in project_path.rglob('*'):
                if files_checked >= max_files_to_check:
                    break
                
                if not file_path.is_file():
                    continue
                
                if file_path.suffix.lower() not in ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.rs', '.go', '.java', '.cs', '.cpp', '.c', '.h']:
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern in patterns:
                        if re.search(pattern, content, re.MULTILINE):
                            score += 0.05
                    
                    files_checked += 1
                    
                except (OSError, UnicodeDecodeError):
                    continue
        
        except (OSError, PermissionError):
            pass
        
        return min(score, 0.4)
    
    def _detect_technologies(self, project_path: Path, file_structure: Dict[str, Any]) -> List[str]:
        """Detect technologies used in the project."""
        technologies = set()
        
        ext_tech_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'React',
            '.tsx': 'React/TypeScript',
            '.vue': 'Vue.js',
            '.rs': 'Rust',
            '.go': 'Go',
            '.java': 'Java',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SASS/SCSS',
            '.less': 'LESS',
            '.sql': 'SQL',
            '.sh': 'Shell Script',
            '.ps1': 'PowerShell',
            '.yaml': 'YAML',
            '.yml': 'YAML',
            '.json': 'JSON',
            '.xml': 'XML',
            '.md': 'Markdown'
        }
        
        for ext, count in file_structure['extensions'].items():
            if ext in ext_tech_map and count > 0:
                technologies.add(ext_tech_map[ext])
        
        file_tech_map = {
            'Dockerfile': 'Docker',
            'docker-compose.yml': 'Docker Compose',
            'Vagrantfile': 'Vagrant',
            'Makefile': 'Make',
            'CMakeLists.txt': 'CMake',
            'build.gradle': 'Gradle',
            'pom.xml': 'Maven',
            'Cargo.toml': 'Cargo',
            'go.mod': 'Go Modules',
            'package.json': 'npm/Node.js',
            'composer.json': 'Composer',
            'Gemfile': 'Bundler',
            'requirements.txt': 'pip',
            'Pipfile': 'Pipenv',
            'poetry.lock': 'Poetry'
        }
        
        for file_name in file_structure['files']:
            if file_name in file_tech_map:
                technologies.add(file_tech_map[file_name])
        
        return sorted(list(technologies))
    
    def _detect_frameworks(self, project_path: Path, file_structure: Dict[str, Any]) -> List[str]:
        """Detect frameworks used in the project."""
        frameworks = set()
        
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                all_deps = {}
                all_deps.update(package_data.get('dependencies', {}))
                all_deps.update(package_data.get('devDependencies', {}))
                
                framework_map = {
                    'react': 'React',
                    'vue': 'Vue.js',
                    'angular': 'Angular',
                    'svelte': 'Svelte',
                    'next': 'Next.js',
                    'nuxt': 'Nuxt.js',
                    'gatsby': 'Gatsby',
                    'express': 'Express.js',
                    'koa': 'Koa.js',
                    'fastify': 'Fastify',
                    'nestjs': 'NestJS',
                    'electron': 'Electron',
                    'react-native': 'React Native'
                }
                
                for dep_name in all_deps:
                    for framework_key, framework_name in framework_map.items():
                        if framework_key in dep_name.lower():
                            frameworks.add(framework_name)
            
            except (json.JSONDecodeError, OSError):
                pass
        
        requirements_files = ['requirements.txt', 'pyproject.toml', 'Pipfile']
        for req_file in requirements_files:
            req_path = project_path / req_file
            if req_path.exists():
                try:
                    with open(req_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                    python_frameworks = {
                        'django': 'Django',
                        'flask': 'Flask',
                        'fastapi': 'FastAPI',
                        'tornado': 'Tornado',
                        'pyramid': 'Pyramid',
                        'bottle': 'Bottle',
                        'cherrypy': 'CherryPy',
                        'streamlit': 'Streamlit',
                        'dash': 'Dash',
                        'tensorflow': 'TensorFlow',
                        'pytorch': 'PyTorch',
                        'keras': 'Keras',
                        'scikit-learn': 'Scikit-learn',
                        'pandas': 'Pandas',
                        'numpy': 'NumPy'
                    }
                    
                    for framework_key, framework_name in python_frameworks.items():
                        if framework_key in content:
                            frameworks.add(framework_name)
                
                except OSError:
                    pass
        
        return sorted(list(frameworks))
    
    def _detect_languages(self, file_structure: Dict[str, Any]) -> List[str]:
        """Detect programming languages used in the project."""
        languages = set()
        
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.jsx': 'JavaScript',
            '.tsx': 'TypeScript',
            '.rs': 'Rust',
            '.go': 'Go',
            '.java': 'Java',
            '.cs': 'C#',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.dart': 'Dart',
            '.scala': 'Scala',
            '.clj': 'Clojure',
            '.hs': 'Haskell',
            '.elm': 'Elm',
            '.r': 'R',
            '.m': 'MATLAB',
            '.pl': 'Perl',
            '.lua': 'Lua',
            '.sh': 'Shell',
            '.ps1': 'PowerShell'
        }
        
        for ext, count in file_structure['extensions'].items():
            if ext in language_map and count > 0:
                languages.add(language_map[ext])
        
        return sorted(list(languages))
    
    def _detect_build_tools(self, project_path: Path) -> List[str]:
        """Detect build tools used in the project."""
        build_tools = set()
        
        for tool_name, file_patterns in self.framework_indicators['build_tools'].items():
            for pattern in file_patterns:
                if (project_path / pattern).exists():
                    build_tools.add(tool_name)
                    break
        
        return sorted(list(build_tools))
    
    def _detect_package_managers(self, project_path: Path) -> List[str]:
        """Detect package managers used in the project."""
        package_managers = set()
        
        manager_files = {
            'npm': ['package.json', 'package-lock.json'],
            'yarn': ['yarn.lock'],
            'pnpm': ['pnpm-lock.yaml'],
            'pip': ['requirements.txt'],
            'pipenv': ['Pipfile', 'Pipfile.lock'],
            'poetry': ['pyproject.toml', 'poetry.lock'],
            'conda': ['environment.yml', 'environment.yaml'],
            'cargo': ['Cargo.toml', 'Cargo.lock'],
            'go mod': ['go.mod', 'go.sum'],
            'maven': ['pom.xml'],
            'gradle': ['build.gradle', 'build.gradle.kts'],
            'composer': ['composer.json', 'composer.lock'],
            'bundler': ['Gemfile', 'Gemfile.lock']
        }
        
        for manager, files in manager_files.items():
            if any((project_path / file).exists() for file in files):
                package_managers.add(manager)
        
        return sorted(list(package_managers))
    
    def _detect_testing_frameworks(self, project_path: Path) -> List[str]:
        """Detect testing frameworks used in the project."""
        testing_frameworks = set()
        
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                all_deps = {}
                all_deps.update(package_data.get('dependencies', {}))
                all_deps.update(package_data.get('devDependencies', {}))
                
                js_test_frameworks = {
                    'jest': 'Jest',
                    'mocha': 'Mocha',
                    'jasmine': 'Jasmine',
                    'karma': 'Karma',
                    'cypress': 'Cypress',
                    'playwright': 'Playwright',
                    'puppeteer': 'Puppeteer',
                    'selenium': 'Selenium',
                    'webdriver': 'WebDriver'
                }
                
                for dep_name in all_deps:
                    for framework_key, framework_name in js_test_frameworks.items():
                        if framework_key in dep_name.lower():
                            testing_frameworks.add(framework_name)
            
            except (json.JSONDecodeError, OSError):
                pass
        
        python_test_files = {
            'pytest': ['pytest.ini', 'pyproject.toml', 'setup.cfg'],
            'unittest': [],
            'nose': ['nose.cfg'],
            'tox': ['tox.ini']
        }
        
        for framework, files in python_test_files.items():
            if any((project_path / file).exists() for file in files):
                testing_frameworks.add(framework)
        
        return sorted(list(testing_frameworks))
    
    def _detect_deployment_targets(self, project_path: Path) -> List[str]:
        """Detect deployment targets and platforms."""
        deployment_targets = set()
        
        for target_name, file_patterns in self.framework_indicators['deployment'].items():
            for pattern in file_patterns:
                if (project_path / pattern).exists():
                    deployment_targets.add(target_name)
                    break
        
        cloud_files = {
            'AWS': ['.aws', 'serverless.yml', 'sam.yaml', 'cloudformation.yaml'],
            'Google Cloud': ['app.yaml', 'cloudbuild.yaml', '.gcloudignore'],
            'Azure': ['azure-pipelines.yml', '.azure'],
            'Heroku': ['Procfile', 'app.json'],
            'Vercel': ['vercel.json', 'now.json'],
            'Netlify': ['netlify.toml', '_redirects', '_headers'],
            'GitHub Pages': ['.github/workflows/pages.yml'],
            'Docker': ['Dockerfile', 'docker-compose.yml']
        }
        
        for platform, files in cloud_files.items():
            if any((project_path / file).exists() for file in files):
                deployment_targets.add(platform)
        
        return sorted(list(deployment_targets))
    
    def _detect_development_patterns(self, project_path: Path, file_structure: Dict[str, Any]) -> List[str]:
        """Detect development patterns and architectures."""
        patterns = set()
        
        directories = file_structure['directories']
        
        if {'models', 'views', 'controllers'}.issubset(directories):
            patterns.add('MVC Architecture')
        
        if any(d in directories for d in ['services', 'microservices', 'api']):
            patterns.add('Microservices')
        
        if 'packages' in directories or len([d for d in directories if 'package' in d.lower()]) > 1:
            patterns.add('Monorepo')
        
        if {'domain', 'infrastructure', 'application'}.issubset(directories):
            patterns.add('Clean Architecture')
        
        if {'adapters', 'ports'}.issubset(directories):
            patterns.add('Hexagonal Architecture')
        
        test_dirs = [d for d in directories if 'test' in d.lower()]
        if len(test_dirs) > 0 and file_structure['file_count'] > 0:
            patterns.add('Test-Driven Development')
        
        if 'docs' in directories or 'documentation' in directories:
            patterns.add('Documentation-Driven Development')
        
        if any(f in file_structure['files'] for f in ['.gitignore', '.gitattributes']):
            patterns.add('Version Control')
        
        if any(f in file_structure['files'] for f in ['README.md', 'README.rst', 'README.txt']):
            patterns.add('Open Source')
        
        ci_files = ['.github', '.gitlab-ci.yml', '.travis.yml', 'jenkins', 'azure-pipelines.yml']
        if any((project_path / f).exists() for f in ci_files):
            patterns.add('Continuous Integration')
        
        return sorted(list(patterns))
    
    def _extract_dependencies(self, project_path: Path) -> Dict[str, List[str]]:
        """Extract project dependencies from various package files."""
        dependencies = {}
        
        # JavaScript/Node.js dependencies
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    
                dependencies['production'] = list(package_data.get('dependencies', {}).keys())
                dependencies['development'] = list(package_data.get('devDependencies', {}).keys())
                dependencies['peer'] = list(package_data.get('peerDependencies', {}).keys())
            
            except (json.JSONDecodeError, OSError):
                pass
        
        # Python dependencies
        requirements_txt = project_path / 'requirements.txt'
        if requirements_txt.exists():
            try:
                with open(requirements_txt, 'r', encoding='utf-8') as f:
                    requirements = []
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifiers)
                            package_name = re.split(r'[>=<!=]', line)[0].strip()
                            requirements.append(package_name)
                    dependencies['python'] = requirements
            
            except OSError:
                pass
        
        # Poetry dependencies
        pyproject_toml = project_path / 'pyproject.toml'
        if pyproject_toml.exists():
            try:
                with open(pyproject_toml, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple extraction - could be improved with TOML parser
                    poetry_deps = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
                    if poetry_deps:
                        dependencies['poetry'] = poetry_deps
            
            except OSError:
                pass
        
        # Rust dependencies
        cargo_toml = project_path / 'Cargo.toml'
        if cargo_toml.exists():
            try:
                with open(cargo_toml, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Simple extraction - could be improved with TOML parser
                    cargo_deps = re.findall(r'^(\w+)\s*=', content, re.MULTILINE)
                    if cargo_deps:
                        dependencies['cargo'] = cargo_deps
            
            except OSError:
                pass
        
        # Go dependencies
        go_mod = project_path / 'go.mod'
        if go_mod.exists():
            try:
                with open(go_mod, 'r', encoding='utf-8') as f:
                    content = f.read()
                    go_deps = re.findall(r'require\s+([^\s]+)', content)
                    if go_deps:
                        dependencies['go'] = go_deps
            
            except OSError:
                pass
        
        return dependencies


class ProjectInferenceEngine:
    """Main project inference engine."""
    
    def __init__(self):
        self.detector = ProjectDetector()
        self.cache = {}
        self.cache_file = Path('.project_context.json')
        
        self._load_cache()
    
    def analyze_project(self, project_path: str = None, force_refresh: bool = False) -> ProjectFingerprint:
        """Analyze project and return comprehensive fingerprint."""
        if project_path is None:
            project_path = os.getcwd()
        
        project_path = Path(project_path).resolve()
        cache_key = str(project_path)
        
        if not force_refresh and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if self._is_cache_valid(cached_result):
                print("📋 Using cached project analysis")
                return ProjectFingerprint(**cached_result['fingerprint'])
        
        print(f"🔍 Analyzing project: {project_path.name}")
        fingerprint = self.detector.detect_project_type(str(project_path))
        
        self.cache[cache_key] = {
            'fingerprint': asdict(fingerprint),
            'timestamp': time.time(),
            'project_path': str(project_path)
        }
        
        self._save_cache()
        
        return fingerprint
    
    def get_project_recommendations(self, fingerprint: ProjectFingerprint) -> Dict[str, List[str]]:
        """Get recommendations based on project analysis."""
        recommendations = {
            'setup_suggestions': [],
            'tool_recommendations': [],
            'best_practices': [],
            'optimization_tips': [],
            'security_suggestions': []
        }
        
        # Setup suggestions based on project type
        if fingerprint.project_type == ProjectType.PYTHON:
            if 'venv' not in fingerprint.development_patterns:
                recommendations['setup_suggestions'].append("Set up virtual environment (python -m venv venv)")
            if not fingerprint.package_managers:
                recommendations['setup_suggestions'].append("Consider using pip, pipenv, or poetry for dependency management")
            if 'pytest' not in fingerprint.testing_frameworks:
                recommendations['tool_recommendations'].append("Add pytest for testing")
        
        elif fingerprint.project_type == ProjectType.JAVASCRIPT:
            if 'npm' not in fingerprint.package_managers and 'yarn' not in fingerprint.package_managers:
                recommendations['setup_suggestions'].append("Initialize package.json (npm init)")
            if not fingerprint.testing_frameworks:
                recommendations['tool_recommendations'].append("Add Jest or Mocha for testing")
        
        elif fingerprint.project_type == ProjectType.REACT:
            if 'TypeScript' not in fingerprint.languages:
                recommendations['tool_recommendations'].append("Consider migrating to TypeScript")
            if 'eslint' not in [tool.lower() for tool in fingerprint.build_tools]:
                recommendations['tool_recommendations'].append("Add ESLint for code quality")
        
        # General recommendations
        if 'Version Control' not in fingerprint.development_patterns:
            recommendations['setup_suggestions'].append("Initialize Git repository (git init)")
        
        if 'Documentation-Driven Development' not in fingerprint.development_patterns:
            recommendations['best_practices'].append("Add README.md with project documentation")
        
        if not fingerprint.testing_frameworks:
            recommendations['best_practices'].append("Implement automated testing")
        
        if 'Continuous Integration' not in fingerprint.development_patterns:
            recommendations['optimization_tips'].append("Set up CI/CD pipeline")
        
        # Security suggestions
        if fingerprint.project_type in [ProjectType.JAVASCRIPT, ProjectType.TYPESCRIPT, ProjectType.REACT]:
            recommendations['security_suggestions'].append("Run npm audit to check for vulnerabilities")
        
        if fingerprint.project_type == ProjectType.PYTHON:
            recommendations['security_suggestions'].append("Use safety to check for known security vulnerabilities")
        
        if 'Docker' not in fingerprint.technologies:
            recommendations['optimization_tips'].append("Consider containerizing with Docker")
        
        return recommendations
    
    def generate_project_summary(self, fingerprint: ProjectFingerprint) -> str:
        """Generate a human-readable project summary."""
        summary_parts = []
        
        # Project type and confidence
        confidence_desc = "high" if fingerprint.confidence > 0.7 else "medium" if fingerprint.confidence > 0.4 else "low"
        summary_parts.append(f"Detected as {fingerprint.project_type.value} project with {confidence_desc} confidence ({fingerprint.confidence:.1%})")
        
        # Languages
        if fingerprint.languages:
            lang_str = ", ".join(fingerprint.languages[:3])
            if len(fingerprint.languages) > 3:
                lang_str += f" and {len(fingerprint.languages) - 3} more"
            summary_parts.append(f"Primary languages: {lang_str}")
        
        # Frameworks
        if fingerprint.frameworks:
            framework_str = ", ".join(fingerprint.frameworks[:3])
            if len(fingerprint.frameworks) > 3:
                framework_str += f" and {len(fingerprint.frameworks) - 3} more"
            summary_parts.append(f"Frameworks: {framework_str}")
        
        # Build tools and package managers
        tools = fingerprint.build_tools + fingerprint.package_managers
        if tools:
            tools_str = ", ".join(tools[:3])
            if len(tools) > 3:
                tools_str += f" and {len(tools) - 3} more"
            summary_parts.append(f"Tools: {tools_str}")
        
        # Development patterns
        if fingerprint.development_patterns:
            patterns_str = ", ".join(fingerprint.development_patterns[:2])
            if len(fingerprint.development_patterns) > 2:
                patterns_str += f" and {len(fingerprint.development_patterns) - 2} more"
            summary_parts.append(f"Patterns: {patterns_str}")
        
        return ". ".join(summary_parts) + "."
    
    def _is_cache_valid(self, cached_data: Dict[str, Any], max_age_hours: int = 24) -> bool:
        """Check if cached data is still valid."""
        cache_age = time.time() - cached_data.get('timestamp', 0)
        return cache_age < (max_age_hours * 3600)
    
    def _load_cache(self) -> None:
        """Load cache from disk."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
        except (json.JSONDecodeError, OSError):
            self.cache = {}
    
    def _save_cache(self) -> None:
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except OSError as e:
            print(f"Warning: Could not save project cache: {e}")


# Global inference engine instance
_inference_engine_instance = None


def get_project_inference_engine() -> ProjectInferenceEngine:
    """Get or create the global project inference engine instance."""
    global _inference_engine_instance
    if _inference_engine_instance is None:
        _inference_engine_instance = ProjectInferenceEngine()
    return _inference_engine_instance


def analyze_current_project(force_refresh: bool = False) -> ProjectFingerprint:
    """Analyze the current project directory."""
    engine = get_project_inference_engine()
    return engine.analyze_project(force_refresh=force_refresh)


def get_project_recommendations_for_current() -> Dict[str, List[str]]:
    """Get recommendations for the current project."""
    engine = get_project_inference_engine()
    fingerprint = engine.analyze_project()
    return engine.get_project_recommendations(fingerprint)


if __name__ == "__main__":
    print("🔍 Testing Project Inference Engine...")
    
    engine = get_project_inference_engine()
    fingerprint = engine.analyze_project()
    
    print(f"\n📊 Project Analysis Results:")
    print(f"  Type: {fingerprint.project_type.value}")
    print(f"  Confidence: {fingerprint.confidence:.1%}")
    print(f"  Languages: {', '.join(fingerprint.languages) if fingerprint.languages else 'None detected'}")
    print(f"  Frameworks: {', '.join(fingerprint.frameworks) if fingerprint.frameworks else 'None detected'}")
    print(f"  Technologies: {', '.join(fingerprint.technologies) if fingerprint.technologies else 'None detected'}")
    
    if fingerprint.evidence:
        print(f"\n🔍 Evidence:")
        for evidence in fingerprint.evidence[:5]:
            print(f"    • {evidence}")
    
    summary = engine.generate_project_summary(fingerprint)
    print(f"\n📋 Summary: {summary}")
    
    recommendations = engine.get_project_recommendations(fingerprint)
    print(f"\n💡 Recommendations:")
    for category, suggestions in recommendations.items():
        if suggestions:
            print(f"  {category.replace('_', ' ').title()}:")
            for suggestion in suggestions[:3]:
                print(f"    • {suggestion}")
    
    print("\n✅ Project Inference Engine test completed!")
