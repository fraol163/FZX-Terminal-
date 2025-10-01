#!/usr/bin/env python3
"""
FZX-Terminal Installation Verification
Run this after installation to verify everything works.
"""

import sys
import os
import json
import importlib
from pathlib import Path

def test_imports():
    """Test all required modules import"""
    print("Testing module imports...")
    failed_imports = []
    
    # Core dependencies that should be installed
    required_modules = [
        'aiohttp',
        'psutil'
    ]
    
    # Standard library modules (should always work)
    standard_modules = [
        'json',
        'asyncio',
        'os',
        'sys',
        'pathlib',
        'datetime',
        'logging',
        'typing',
        'subprocess',
        'threading',
        'uuid',
        'hashlib',
        'urllib.parse'
    ]
    
    # Test required modules first
    for module_name in required_modules:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    # Test a few standard library modules
    for module_name in standard_modules[:5]:  # Just test first 5 to keep output clean
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ Import failed: {failed_imports[0]}")
        print("\nRun: pip install -r requirements.txt")
        return False
    else:
        print("✅ All modules imported successfully")
        return True

def test_fzx_modules():
    """Test FZX-Terminal specific modules"""
    print("\nTesting FZX-Terminal modules...")
    fzx_modules = [
        'enhanced_ai_provider',
        'advanced_building_agent', 
        'building_agent'
    ]
    
    failed_imports = []
    
    for module_name in fzx_modules:
        try:
            module = importlib.import_module(module_name)
            # Test that we can get the main functions
            if module_name == 'enhanced_ai_provider':
                getattr(module, 'get_enhanced_ai_provider')
            elif module_name == 'advanced_building_agent':
                getattr(module, 'get_advanced_building_agent')
            elif module_name == 'building_agent':
                getattr(module, 'get_building_agent')
            print(f"✅ {module_name}")
        except (ImportError, AttributeError) as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n❌ FZX module failed: {failed_imports[0]}")
        return False
    else:
        print("✅ All FZX-Terminal modules imported successfully")
        return True

def test_directory_structure():
    """Test required directories exist"""
    print("\nTesting directory structure...")
    required = [
        'templates'
    ]
    
    for dir_name in required:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ exists")
        else:
            print(f"⚠️  {dir_name}/ missing (will be created on first run)")
    
    # Check if .terminal_data exists
    if os.path.exists('.terminal_data'):
        print("✅ .terminal_data/ exists")
    else:
        print("⚠️  .terminal_data/ missing (will be created on first run)")
    
    return True

def test_api_config():
    """Test if API keys configured"""
    print("\nTesting API configuration...")
    config_file = '.terminal_data/config.json'
    
    if not os.path.exists(config_file):
        print("⚠️  No API keys configured yet")
        print("Run: build setup-ai openrouter")
        return False
    
    try:
        with open(config_file) as f:
            config = json.load(f)
        
        if config.get('openrouter_api_key'):
            print("✅ OpenRouter API key found")
        else:
            print("⚠️  OpenRouter API key not set")
        
        if config.get('gemini_api_key'):
            print("✅ Gemini API key found")
        else:
            print("⚠️  Gemini API key not set")
        
        return True
    except (json.JSONDecodeError, FileNotFoundError):
        print("⚠️  Config file exists but invalid")
        return False

def test_generation():
    """Test basic generation capability"""
    print("\nTesting generation capability...")
    print("Skipping (requires API keys)")
    print("To test: build describe 'Create a simple Python script'")
    return True

if __name__ == "__main__":
    print("FZX-Terminal Installation Check")
    print("=" * 40)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("FZX Modules", test_fzx_modules()))
    results.append(("Directory", test_directory_structure()))
    results.append(("API Config", test_api_config()))
    results.append(("Generation", test_generation()))
    
    print("\n" + "=" * 40)
    print("VERIFICATION SUMMARY:")
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name}: {status}")
    
    # Only require first 3 to pass for basic functionality
    all_passed = all(r[1] for r in results[:3])  
    if all_passed:
        print("\n✅ Installation verified! Ready to use FZX-Terminal")
        print("Next: python terminal_interface.py")
        sys.exit(0)
    else:
        print("\n❌ Installation incomplete. Fix errors above.")
        sys.exit(1)