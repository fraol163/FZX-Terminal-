#!/usr/bin/env python3
"""
Test script for the building agent with a mock AI manager
"""

import asyncio
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from building_agent import BuildingAgent, BuildConfig, BuildType, Framework

@dataclass
class MockAIResponse:
    """Mock AI response for testing."""
    content: str
    success: bool
    error: Optional[str] = None

class MockAIManager:
    """Mock AI manager for testing."""
    
    def is_configured(self):
        return True
    
    async def chat(self, prompt, use_context=False):
        """Return a mock JSON response with file contents."""
        # Simulate a JSON response with file contents
        mock_response = {
            "package.json": '{\n  "name": "test-web-project",\n  "version": "1.0.0",\n  "description": "A test web project",\n  "main": "index.js",\n  "scripts": {\n    "start": "react-scripts start",\n    "build": "react-scripts build"\n  },\n  "dependencies": {\n    "react": "^18.2.0",\n    "react-dom": "^18.2.0"\n  }\n}',
            "index.html": '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Test Web Project</title>\n</head>\n<body>\n    <div id="root"></div>\n    <script src="src/main.js"></script>\n</body>\n</html>',
            "src/main.js": 'import React from "react";\nimport ReactDOM from "react-dom/client";\nimport App from "./App";\n\nconst root = ReactDOM.createRoot(document.getElementById("root"));\nroot.render(<App />);',
            "src/App.js": 'import React from "react";\nimport Header from "./components/Header";\n\nfunction App() {\n  return (\n    <div className="App">\n      <Header />\n      <main>\n        <h1>Welcome to Test Web Project</h1>\n      </main>\n    </div>\n  );\n}\n\nexport default App;',
            "src/components/Header.js": 'import React from "react";\n\nfunction Header() {\n  return (\n    <header>\n      <h1>Test Web Project</h1>\n    </header>\n  );\n}\n\nexport default Header;',
            "README.md": "# Test Web Project\n\nA web project created with FZX-Terminal Building Agent.",
            ".gitignore": "node_modules/\n.env\n.DS_Store\n*.log"
        }
        
        # Return as JSON string
        import json
        response_content = json.dumps(mock_response, indent=2)
        
        return MockAIResponse(
            content=response_content,
            success=True
        )

async def test_building_agent_with_mock_ai():
    """Test the building agent with mock AI."""
    print("Testing Building Agent with Mock AI...")
    
    # Create building agent
    agent = BuildingAgent()
    
    # Replace AI manager with mock
    agent.ai_manager = MockAIManager()
    
    # Create a simple build config
    config = BuildConfig(
        name="mock-ai-project",
        build_type=BuildType.WEB,
        framework=Framework.REACT,
        features=["authentication", "responsive-design"]
    )
    
    print(f"Creating project: {config.name}")
    print(f"Type: {config.build_type.value}")
    print(f"Framework: {config.framework.value if config.framework else 'None'}")
    print(f"Features: {config.features}")
    
    # Build the project
    result = await agent.build_project(config)
    
    print(f"Build result: {result['success']}")
    print(f"Message: {result['message']}")
    if result['files_created']:
        print(f"Files created: {len(result['files_created'])}")
        for file_path in result['files_created'][:10]:  # Show first 10 files
            print(f"  - {file_path}")
    
    if result['next_steps']:
        print("Next steps:")
        for step in result['next_steps'][:3]:  # Show first 3 steps
            print(f"  - {step}")
    
    # Check if files were created with content
    print("\nChecking created files:")
    project_path = Path(config.output_dir)
    if project_path.exists():
        for file_path in project_path.rglob("*"):
            if file_path.is_file():
                print(f"  {file_path.relative_to(project_path)}: {file_path.stat().st_size} bytes")

if __name__ == "__main__":
    asyncio.run(test_building_agent_with_mock_ai())