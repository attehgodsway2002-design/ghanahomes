#!/usr/bin/env python
"""
Run this script to start both the Django development server and the Django-Q cluster
in separate terminals. The script sets up proper virtualenv activation and paths.

Usage:
    python start_dev.py

This will:
1. Start Django development server on http://localhost:8000
2. Start Django-Q cluster for processing background tasks
"""

import os
import subprocess
import sys
from time import sleep
from pathlib import Path

# Get project root directory
PROJECT_ROOT = str(Path(__file__).parent.absolute())
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")

def run_command(cmd, **kwargs):
    env = os.environ.copy()
    # Clear problematic variables that cause "Could not find platform independent libraries" warning
    env.pop('PYTHONHOME', None)
    env.pop('PYTHONPATH', None)
    # Set required Django variables
    env['DJANGO_SETTINGS_MODULE'] = 'ghanahomes.settings'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )

def main():
    # Start Django dev server
    print("Starting Django development server...")
    server_proc = run_command([VENV_PYTHON, "manage.py", "runserver"])
    
    # Start Django-Q cluster
    print("Starting Django-Q cluster...")
    sleep(2)  # Give the dev server a moment to start
    cluster_proc = run_command([VENV_PYTHON, "manage.py", "qcluster"])
    
    print("\nServers started!")
    print("Django server: http://localhost:8000")
    print("Press Ctrl+C in the server windows to stop them")
    
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("Stopping servers...")
    finally:
        server_proc.terminate()
        cluster_proc.terminate()
        print("Servers stopped")

if __name__ == "__main__":
    main()