from pathlib import Path

# =====================================================
# BASE PATHS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"

OBJECTS_DIR = OUTPUT_DIR / "objects"
POLICIES_DIR = OUTPUT_DIR / "policies"
NORMALIZED_DIR = OUTPUT_DIR / "normalized"
FLATTEN_DIR = OUTPUT_DIR / "flattened"

LOG_DIR = OUTPUT_DIR / "logs"

# cria diretórios automaticamente
for directory in [
    OUTPUT_DIR,
    OBJECTS_DIR,
    POLICIES_DIR,
    NORMALIZED_DIR,
    FLATTEN_DIR,
    LOG_DIR
]:
    directory.mkdir(parents=True, exist_ok=True)

# =====================================================
# CHECKPOINT API
# =====================================================

CHECKPOINT_SERVER = "https://10.193.12.32"
USERNAME = "userAqui"
PASSWORD = "SENHAAQUI"

# =====================================================
# API CONFIG
# =====================================================

LIMIT = 500
VERIFY_SSL = False