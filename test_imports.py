#!/usr/bin/env python3
"""
Test script to verify all modules can be imported successfully.
This helps identify any missing dependencies or import errors.
"""

import sys
import traceback
from pathlib import Path

def test_import(module_name, description=""):
    """Test importing a module and report results."""
    try:
        __import__(module_name)
        print(f"✅ {module_name:<25} - {description}")
        return True
    except ImportError as e:
        print(f"❌ {module_name:<25} - Import Error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  {module_name:<25} - Other Error: {e}")
        return False

def main():
    """Test all module imports."""
    print("🧪 Testing FZX-Terminal Module Imports")
    print("=" * 60)
    
    modules_to_test = [
        ("chat_manager", "Chat transcript management with JSONL storage"),
        ("context_manager", "Intelligent memory optimization and context preservation"),
        ("terminal_persistence", "Command correlation and output tracking"),
        ("session_bridge", "Session continuity and context compression"),
        ("project_inference", "Intelligent project fingerprinting and detection"),
        ("file_manager", "File integrity checking and backup management"),
        ("high_performance_file_system", "Unified state management system"),
        ("startup_hook", "Entry point for automatic integration"),
        ("auto_startup", "Session continuity and context preservation"),
        ("progress_tracker", "Task and milestone tracking system"),
        ("file_structure_mapper", "Directory structure analysis and mapping"),
        ("launch", "Quick launcher script"),
    ]
    
    successful_imports = 0
    total_modules = len(modules_to_test)
    
    for module_name, description in modules_to_test:
        if test_import(module_name, description):
            successful_imports += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Import Test Results: {successful_imports}/{total_modules} modules imported successfully")
    
    if successful_imports == total_modules:
        print("🎉 All modules imported successfully! The project is ready to run.")
        
        # Test the main terminal interface import
        print("\n🔍 Testing main terminal interface...")
        try:
            import terminal_interface
            print("✅ terminal_interface - Main interface module loaded")
            
            # Try to create an instance (but don't run it)
            try:
                interface = terminal_interface.RobustTerminalInterface()
                print("✅ RobustTerminalInterface instance created successfully")
                print("🚀 FZX-Terminal is ready for use!")
                return 0
            except Exception as e:
                print(f"⚠️  RobustTerminalInterface instantiation failed: {e}")
                print("   This may be due to missing dependencies or configuration issues.")
                return 1
                
        except ImportError as e:
            print(f"❌ terminal_interface - Import Error: {e}")
            return 1
        except Exception as e:
            print(f"⚠️  terminal_interface - Other Error: {e}")
            traceback.print_exc()
            return 1
    else:
        print("❌ Some modules failed to import. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())