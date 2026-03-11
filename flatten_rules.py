import json
import logging
from pathlib import Path

from config import OUTPUT_DIR

# =====================================================
# PATHS
# =====================================================

RESOLVED_DIR = OUTPUT_DIR / "resolved"
FLATTEN_DIR = OUTPUT_DIR / "flattened"
LOG_DIR = OUTPUT_DIR / "logs"

FLATTEN_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOGGER
# =====================================================

log_file = LOG_DIR / "flatten_rules.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# =====================================================
# FLATTEN ENGINE
# =====================================================

def flatten_rule(rule, parent_section=None):

    flattened = []

    # Caso seja section
    if isinstance(rule, dict) and "rulebase" in rule:

        section_name = rule.get("name", parent_section)

        for sub_rule in rule["rulebase"]:
            flattened.extend(flatten_rule(sub_rule, section_name))

    else:

        rule_copy = rule.copy()

        if parent_section:
            rule_copy["section"] = parent_section

        flattened.append(rule_copy)

    return flattened


# =====================================================
# PROCESS POLICY
# =====================================================

def process_policy(file_path):

    logger.info(f"Processando {file_path}")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # -----------------------------
    # Detecta estrutura do JSON
    # -----------------------------

    if isinstance(data, list):

        # já é lista de rules
        rules = data

    elif isinstance(data, dict):

        rules = data.get("rulebase", [])

    else:

        logger.error(f"Formato JSON desconhecido: {file_path}")
        return []

    # -----------------------------

    flattened_rules = []

    for rule in rules:
        flattened_rules.extend(flatten_rule(rule))

    logger.info(f"Rules flatten: {len(flattened_rules)}")

    return flattened_rules


# =====================================================
# MAIN
# =====================================================

def main():

    logger.info("========== FLATTEN RULES ==========")

    for package_dir in RESOLVED_DIR.iterdir():

        if not package_dir.is_dir():
            continue

        output_package_dir = FLATTEN_DIR / package_dir.name
        output_package_dir.mkdir(parents=True, exist_ok=True)

        for policy_file in package_dir.glob("*.json"):

            flattened = process_policy(policy_file)

            output_file = output_package_dir / policy_file.name

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(flattened, f, indent=2)

            logger.info(f"Arquivo salvo: {output_file}")

    logger.info("========== FLATTEN FINALIZADO ==========")


# =====================================================

if __name__ == "__main__":
    main()