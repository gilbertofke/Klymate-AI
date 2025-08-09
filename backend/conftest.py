"""
Pytest configuration for Klymate AI Backend

This file ensures proper Python path setup for all test environments.
"""

import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
project_root = backend_dir.parent

# Add paths for imports
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(project_root))

# Ensure backend utils can be imported
if str(backend_dir) not in sys.path:
    sys.path.append(str(backend_dir))

print(f"Python path configured for tests:")
print(f"  Backend dir: {backend_dir}")
print(f"  Project root: {project_root}")