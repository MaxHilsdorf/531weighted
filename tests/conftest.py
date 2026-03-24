from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_SRC = Path(__file__).resolve().parent.parent / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))
