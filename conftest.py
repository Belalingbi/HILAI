import sys
from pathlib import Path

# Assure que le répertoire racine du projet est dans sys.path pour les tests
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
