"""
Quick Launcher for AI Terminal Workflow
Simple script to start the interactive terminal interface
"""

import sys
import os
from pathlib import Path

def main():
    """Launch the AI Terminal Workflow interface."""
    print("🚀 Starting AI Terminal Workflow...")
    
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        import terminal_interface
        interface = terminal_interface.TerminalInterface()
        interface.run()
        return 0
    except KeyboardInterrupt:
        print("\n⏹ Interrupted by user")
        return 0
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required files are present.")
        return 1
    except Exception as e:
        print(f"💥 Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())