#!/usr/bin/env python3
"""
Development startup script for pyNMR
This script handles virtual environment activation and starts the GUI
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Define virtual environment paths based on OS
    if platform.system() == "Windows":
        venv_python = project_root / ".venv" / "Scripts" / "python.exe"
        venv_activate = project_root / ".venv" / "Scripts" / "activate.bat"
    else:
        venv_python = project_root / ".venv" / "bin" / "python"
        venv_activate = project_root / ".venv" / "bin" / "activate"
    
    # Check if virtual environment exists
    if not venv_python.exists():
        print("❌ Virtual environment not found!")
        print(f"Expected at: {venv_python}")
        print("\nTo set up the development environment:")
        print("1. python -m venv .venv")
        print("2. pip install -e .")
        print("3. pip install PyQt5 scipy numpy dill")
        sys.exit(1)
    
    # Change to project directory
    os.chdir(project_root)
    
    print("🚀 Starting pyNMR in development mode...")
    print(f"📁 Project root: {project_root}")
    print(f"🐍 Using Python: {venv_python}")
    
    # Start the application using the virtual environment Python
    try:
        result = subprocess.run([str(venv_python), "start_gui.py"], 
                              cwd=project_root,
                              check=False)
        
        if result.returncode != 0:
            print(f"\n❌ Application exited with error code: {result.returncode}")
            sys.exit(result.returncode)
        else:
            print("\n✅ Application closed successfully")
            
    except FileNotFoundError:
        print(f"❌ Could not find Python executable: {venv_python}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()