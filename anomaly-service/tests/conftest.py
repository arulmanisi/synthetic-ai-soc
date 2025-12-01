import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
MITRE_DIR = ROOT_DIR.parent / "mitre"
if str(MITRE_DIR) not in sys.path:
    sys.path.insert(0, str(MITRE_DIR))

# Ensure Python sees repo root for nested imports
REPO_ROOT = ROOT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
