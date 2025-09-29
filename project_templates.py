"""
Project Templates System for FZX-Terminal Building Agent
Provides pre-configured templates for various project types and frameworks
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum

@dataclass
class TemplateConfig:
    """Configuration for template generation."""
    name: str
    build_type: str
    framework: Optional[str] = None
    language: str = "javascript"
    features: List[str] = None
    
    def __post_init__(self):
        if self.features is None:
            self.features = []

class ProjectTemplates:
    """Template system for project generation."""
    
    def __init__(self):
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates_dir.mkdir(exist_ok=True)
        
        # Initialize default templates
        self._ensure_default_templates()
    
    def _ensure_default_templates(self) -> None:
        """Ensure default templates exist."""
        default_templates = {
            "react-web": self._get_react_template(),
            "express-api": self._get_express_template(),
            "python-cli": self._get_python_cli_template(),
            "nextjs-fullstack": self._get_nextjs_template()
        }
        
        for template_name, template_data in default_templates.items():
            template_file = self.templates_dir / f"{template_name}.json"
            if not template_file.exists():
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2)
    
    def _get_react_template(self) -> Dict[str, Any]:
        """Get React web application template."""
        return {
            "name": "React Web Application",
            "description": "Modern React application with Vite build tool",
            "build_type": "web",
            "framework": "react",
            "language": "javascript",
            "files": {
                "package.json": {
                    "name": "{{project_name}}",
                    "private": True,
                    "version": "0.0.0",
                    "type": "module",
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build",
                        "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0",
                        "preview": "vite preview"
                    },
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    },
                    "devDependencies": {
                        "@types/react": "^18.2.15",
                        "@types/react-dom": "^18.2.7",
                        "@vitejs/plugin-react": "^4.0.3",
                        "eslint": "^8.45.0",
                        "eslint-plugin-react": "^7.32.2",
                        "eslint-plugin-react-hooks": "^4.6.0",
                        "eslint-plugin-react-refresh": "^0.4.3",
                        "vite": "^4.4.5"
                    }
                },
                "index.html": """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{project_name}}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",
                "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",
                "src/App.jsx": """import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vitejs.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>{{project_name}}</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App""",
                "src/App.css": """#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.react:hover {
  filter: drop-shadow(0 0 2em #61dafbaa);
}

@keyframes logo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: no-preference) {
  a:nth-of-type(2) .logo {
    animation: logo-spin infinite 20s linear;
  }
}

.card {
  padding: 2em;
}

.read-the-docs {
  color: #888;
}""",
                "src/index.css": """:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  -webkit-text-size-adjust: 100%;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}
a:hover {
  color: #535bf2;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

h1 {
  font-size: 3.2em;
  line-height: 1.1;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: #1a1a1a;
  color: white;
  cursor: pointer;
  transition: border-color 0.25s;
}
button:hover {
  border-color: #646cff;
}
button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}

@media (prefers-color-scheme: light) {
  :root {
    color: #213547;
    background-color: #ffffff;
  }
  a:hover {
    color: #747bff;
  }
  button {
    background-color: #f9f9f9;
    color: #213547;
  }
}""",
                "vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
})""",
                "README.md": """# {{project_name}}

A modern React application built with Vite.

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Features

- ⚡ Fast development with Vite
- ⚛️ React 18
- 🎨 Modern CSS
- 🔧 ESLint configuration
- 📦 Production-ready build

## Project Structure

```
src/
├── App.jsx          # Main App component
├── App.css          # App styles
├── main.jsx         # Entry point
└── index.css        # Global styles
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

---

Built with ❤️ using FZX-Terminal Building Agent
""",
                ".gitignore": """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?"""
            },
            "directories": ["src", "public", "src/assets"],
            "commands": [
                {"name": "install", "command": "npm install"},
                {"name": "dev", "command": "npm run dev"},
                {"name": "build", "command": "npm run build"}
            ]
        }
    
    def _get_express_template(self) -> Dict[str, Any]:
        """Get Express.js API template."""
        return {
            "name": "Express.js API Server",
            "description": "RESTful API server with Express.js and modern middleware",
            "build_type": "api",
            "framework": "express",
            "language": "javascript",
            "files": {
                "package.json": {
                    "name": "{{project_name}}",
                    "version": "1.0.0",
                    "description": "Express.js API server",
                    "main": "server.js",
                    "scripts": {
                        "start": "node server.js",
                        "dev": "nodemon server.js",
                        "test": "jest",
                        "lint": "eslint ."
                    },
                    "dependencies": {
                        "express": "^4.18.2",
                        "cors": "^2.8.5",
                        "helmet": "^7.0.0",
                        "morgan": "^1.10.0",
                        "dotenv": "^16.3.1"
                    },
                    "devDependencies": {
                        "nodemon": "^3.0.1",
                        "jest": "^29.6.2",
                        "eslint": "^8.45.0"
                    }
                },
                "server.js": """const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Routes
app.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to {{project_name}} API',
    version: '1.0.0',
    status: 'running'
  });
});

app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    timestamp: new Date().toISOString()
  });
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Something went wrong!' });
});

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

app.listen(PORT, () => {
  console.log(`🚀 {{project_name}} API server running on port ${PORT}`);
});

module.exports = app;""",
                ".env.example": """PORT=3000
NODE_ENV=development
API_KEY=your_api_key_here
DATABASE_URL=your_database_url_here""",
                "README.md": """# {{project_name}}

Express.js API server with modern middleware and best practices.

## Getting Started

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev

# Start production server
npm start
```

## API Endpoints

- `GET /` - API information
- `GET /api/health` - Health check

## Features

- 🚀 Express.js framework
- 🛡️ Security with Helmet
- 🌐 CORS enabled
- 📝 Request logging with Morgan
- 🔧 Environment variables
- 🧪 Jest testing setup

## Scripts

- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests
- `npm run lint` - Run ESLint

---

Built with ❤️ using FZX-Terminal Building Agent
""",
                ".gitignore": """node_modules/
.env
.DS_Store
logs
*.log
npm-debug.log*
dist/
coverage/"""
            },
            "directories": ["routes", "middleware", "models", "tests"],
            "commands": [
                {"name": "install", "command": "npm install"},
                {"name": "dev", "command": "npm run dev"},
                {"name": "start", "command": "npm start"}
            ]
        }
    
    def _get_python_cli_template(self) -> Dict[str, Any]:
        """Get Python CLI template."""
        return {
            "name": "Python CLI Tool",
            "description": "Modern Python CLI application with Click framework",
            "build_type": "cli",
            "framework": "click",
            "language": "python",
            "files": {
                "pyproject.toml": """[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{{project_name}}"
version = "0.1.0"
description = "A modern Python CLI tool"
authors = [{name = "Your Name", email = "your.email@example.com"}]
readme = "README.md"
requires-python = ">=3.8"
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]
dependencies = [
    "click>=8.0.0",
    "rich>=13.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=22.0.0",
    "flake8>=5.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
{{project_name}} = "{{project_name}}.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["{{project_name}}*"]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true""",
                "{{project_name}}/__init__.py": """\"\"\"{{project_name}} - A modern Python CLI tool.\"\"\"

__version__ = "0.1.0"
""",
                "{{project_name}}/cli.py": """\"\"\"Main CLI interface for {{project_name}}.\"\"\"

import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.version_option()
def main():
    \"\"\"{{project_name}} - A modern Python CLI tool.\"\"\"
    pass

@main.command()
@click.option('--name', default='World', help='Name to greet.')
@click.option('--count', default=1, help='Number of greetings.')
def hello(name, count):
    \"\"\"Simple program that greets NAME for a total of COUNT times.\"\"\"
    for i in range(count):
        console.print(f"Hello {name}!", style="bold green")

@main.command()
def status():
    \"\"\"Show application status.\"\"\"
    table = Table(title="{{project_name}} Status")
    
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    table.add_row("Status", "✅ Running")
    table.add_row("Version", "0.1.0")
    table.add_row("Python", "🐍 Ready")
    
    console.print(table)

if __name__ == '__main__':
    main()
""",
                "tests/__init__.py": "",
                "tests/test_cli.py": """\"\"\"Tests for CLI functionality.\"\"\"

import pytest
from click.testing import CliRunner
from {{project_name}}.cli import main

def test_hello_command():
    \"\"\"Test hello command.\"\"\"
    runner = CliRunner()
    result = runner.invoke(main, ['hello'])
    assert result.exit_code == 0
    assert 'Hello World!' in result.output

def test_hello_with_name():
    \"\"\"Test hello command with custom name.\"\"\"
    runner = CliRunner()
    result = runner.invoke(main, ['hello', '--name', 'Python'])
    assert result.exit_code == 0
    assert 'Hello Python!' in result.output

def test_status_command():
    \"\"\"Test status command.\"\"\"
    runner = CliRunner()
    result = runner.invoke(main, ['status'])
    assert result.exit_code == 0
    assert 'Status' in result.output
""",
                "README.md": """# {{project_name}}

A modern Python CLI tool built with Click and Rich.

## Installation

```bash
# Install in development mode
pip install -e .

# Or install from PyPI (when published)
pip install {{project_name}}
```

## Usage

```bash
# Show help
{{project_name}} --help

# Greet someone
{{project_name}} hello --name "Developer"

# Show status
{{project_name}} status
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint code
flake8 .

# Type checking
mypy .
```

## Features

- 🖱️ Modern CLI with Click
- 🎨 Beautiful output with Rich
- 🧪 Comprehensive test suite
- 🔧 Development tools included
- 📦 Ready for PyPI distribution

---

Built with ❤️ using FZX-Terminal Building Agent
""",
                ".gitignore": """__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

.pytest_cache/
.mypy_cache/
.coverage
htmlcov/
.tox/
"""
            },
            "directories": ["{{project_name}}", "tests"],
            "commands": [
                {"name": "install", "command": "pip install -e ."},
                {"name": "test", "command": "pytest"},
                {"name": "run", "command": "{{project_name}} --help"}
            ]
        }
    
    def _get_nextjs_template(self) -> Dict[str, Any]:
        """Get Next.js full-stack template."""
        return {
            "name": "Next.js Full-Stack Application",
            "description": "Modern full-stack web application with Next.js 14",
            "build_type": "fullstack",
            "framework": "nextjs",
            "language": "javascript",
            "files": {
                "package.json": {
                    "name": "{{project_name}}",
                    "version": "0.1.0",
                    "private": True,
                    "scripts": {
                        "dev": "next dev",
                        "build": "next build",
                        "start": "next start",
                        "lint": "next lint"
                    },
                    "dependencies": {
                        "next": "14.0.0",
                        "react": "^18",
                        "react-dom": "^18"
                    },
                    "devDependencies": {
                        "eslint": "^8",
                        "eslint-config-next": "14.0.0"
                    }
                },
                "next.config.js": """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig
""",
                "app/layout.js": """import './globals.css'

export const metadata = {
  title: '{{project_name}}',
  description: 'Built with Next.js and FZX-Terminal',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
""",
                "app/page.js": """export default function Home() {
  return (
    <main>
      <div className="container">
        <h1>Welcome to {{project_name}}</h1>
        <p>A modern Next.js application built with FZX-Terminal Building Agent.</p>
        
        <div className="features">
          <div className="feature">
            <h3>⚡ Fast</h3>
            <p>Built with Next.js 14 and React 18</p>
          </div>
          <div className="feature">
            <h3>🎨 Modern</h3>
            <p>Clean and responsive design</p>
          </div>
          <div className="feature">
            <h3>🚀 Ready</h3>
            <p>Production-ready configuration</p>
          </div>
        </div>
      </div>
    </main>
  )
}
""",
                "app/globals.css": """* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

html,
body {
  max-width: 100vw;
  overflow-x: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto',
    'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans',
    'Helvetica Neue', sans-serif;
}

body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  min-height: 100vh;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  background: linear-gradient(45deg, #fff, #f0f0f0);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 3rem;
}

.feature {
  background: rgba(255, 255, 255, 0.1);
  padding: 2rem;
  border-radius: 1rem;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.feature h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  h1 {
    font-size: 2rem;
  }
  
  .container {
    padding: 1rem;
  }
}
""",
                "README.md": """# {{project_name}}

A modern Next.js full-stack application with cutting-edge features.

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Features

- ⚡ Next.js 14 with App Router
- ⚛️ React 18 with modern features
- 🎨 Beautiful gradient design
- 📱 Fully responsive
- 🚀 Production-ready
- 🔧 ESLint configuration

## Project Structure

```
app/
├── layout.js       # Root layout
├── page.js         # Home page
└── globals.css     # Global styles
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

---

Built with ❤️ using FZX-Terminal Building Agent
""",
                ".gitignore": """# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# next.js
/.next/
/out/

# production
/build

# misc
.DS_Store
*.pem

# debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# local env files
.env*.local

# vercel
.vercel

# typescript
*.tsbuildinfo
next-env.d.ts"""
            },
            "directories": ["app", "public"],
            "commands": [
                {"name": "install", "command": "npm install"},
                {"name": "dev", "command": "npm run dev"},
                {"name": "build", "command": "npm run build"}
            ]
        }
    
    def generate_project(self, config: TemplateConfig, output_path: Path) -> List[str]:
        """Generate project from template configuration."""
        files_created = []
        
        # Find appropriate template
        template_key = self._get_template_key(config)
        template_file = self.templates_dir / f"{template_key}.json"
        
        if not template_file.exists():
            # Fallback to basic template
            return self._generate_basic_project(config, output_path)
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
            
            # Create directories
            if 'directories' in template_data:
                for dir_name in template_data['directories']:
                    dir_path = output_path / self._replace_placeholders(dir_name, config)
                    dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create files
            if 'files' in template_data:
                for file_path, content in template_data['files'].items():
                    full_path = output_path / self._replace_placeholders(file_path, config)
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if isinstance(content, dict):
                        # JSON content
                        content_str = json.dumps(content, indent=2)
                    else:
                        # String content
                        content_str = str(content)
                    
                    # Replace placeholders in content
                    final_content = self._replace_placeholders(content_str, config)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(final_content)
                    
                    files_created.append(str(full_path.relative_to(output_path)))
            
            return files_created
            
        except Exception as e:
            print(f"Error generating from template: {e}")
            return self._generate_basic_project(config, output_path)
    
    def _get_template_key(self, config: TemplateConfig) -> str:
        """Get template key based on configuration."""
        if config.framework:
            return f"{config.framework}-{config.build_type}"
        else:
            return f"basic-{config.build_type}"
    
    def _replace_placeholders(self, text: str, config: TemplateConfig) -> str:
        """Replace template placeholders with actual values."""
        replacements = {
            '{{project_name}}': config.name,
            '{{build_type}}': config.build_type,
            '{{framework}}': config.framework or 'default',
            '{{language}}': config.language
        }
        
        result = text
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def _generate_basic_project(self, config: TemplateConfig, output_path: Path) -> List[str]:
        """Generate basic project structure as fallback."""
        files_created = []
        
        # Create README
        readme_content = f"# {config.name}\n\nA {config.build_type} project built with FZX-Terminal Building Agent.\n"
        readme_path = output_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        files_created.append("README.md")
        
        # Create .gitignore
        gitignore_content = "node_modules/\n.env\n.DS_Store\n*.log\n"
        gitignore_path = output_path / ".gitignore"
        with open(gitignore_path, 'w', encoding='utf-8') as f:
            f.write(gitignore_content)
        files_created.append(".gitignore")
        
        return files_created
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates."""
        templates = []
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                
                templates.append({
                    "key": template_file.stem,
                    "name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", ""),
                    "build_type": template_data.get("build_type", "unknown"),
                    "framework": template_data.get("framework", "default"),
                    "language": template_data.get("language", "unknown")
                })
            except Exception:
                continue
        
        return templates
    
    def create_custom_template(self, name: str, template_data: Dict[str, Any]) -> bool:
        """Create a custom template."""
        try:
            template_file = self.templates_dir / f"{name}.json"
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2)
            return True
        except Exception:
            return False