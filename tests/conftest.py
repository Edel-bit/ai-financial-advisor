import sys
from pathlib import Path

# Let tests import modules from src/ the same way the app does
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
