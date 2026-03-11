import json
import logging
from pathlib import Path

from config import BASE_DIR, OUTPUT_DIR

# =====================================================
# PATHS
# =====================================================

INPUT_DIR = OUTPUT_DIR / "flattened"
OUTPUT_DIR = OUTPUT_DIR / "normalized"
OBJECTS_DIR = BASE_DIR / "output" / "objects"
LOG_DIR = BASE_DIR / "output" / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# LOGGER
# =====================================================

log_file = LOG_DIR / "normalize_rules.log"

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
# LOAD UID MAP
# =====================================================

def load_uid_map():

    logger.info("Carregando objetos para criação do UID map")

    uid_map = {}

    for file in OBJECTS_DIR.glob("*.json"):

        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning(f"Erro ao carregar {file}: {e}")
            continue

        if isinstance(data, list):

            for obj in data:

                uid = obj.get("uid")
                name = obj.get("name")

                if uid and name:
                    uid_map[uid] = name

    logger.info(f"UID MAP carregado: {len(uid_map)} objetos")

    return uid_map


# =====================================================
# SAFE LIST
# =====================================================

def safe_list(value):

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [value]


# =====================================================
# UID RESOLVE
# =====================================================

def resolve_list(values, uid_map):

    resolved = []

    for v in safe_list(values):

        if isinstance(v, dict):
            v = v.get("uid") or v.get("name")

        resolved.append(uid_map.get(v, v))

    return resolved


# =====================================================
# NORMALIZE ACTION
# =====================================================

def normalize_action(action):

    if isinstance(action, dict):
        action = action.get("name")

    if not action:
        return "drop"

    action = action.lower()

    mapping = {
        "accept": "accept",
        "allow": "accept",
        "drop": "drop",
        "reject": "reject"
    }

    return mapping.get(action, action)


# =====================================================
# NORMALIZE RULE
# =====================================================

def normalize_rule(rule, uid_map):

    sources = resolve_list(rule.get("source"), uid_map)
    destinations = resolve_list(rule.get("destination"), uid_map)

    services = resolve_list(rule.get("service"), uid_map)
    applications = resolve_list(rule.get("applications"), uid_map)

    if applications:
        services.extend(applications)

    normalized = {

        "name": rule.get("name"),
        "uid": rule.get("uid"),

        "source": sources,
        "destination": destinations,
        "service": services,

        "action": normalize_action(rule.get("action")),
        "enabled": rule.get("enabled", True),

        "rule_number": rule.get("rule-number")
        or rule.get("rule_number"),

        "section": rule.get("section")

    }

    return normalized


# =====================================================
# RULE VALIDATION
# =====================================================

def valid_rule(rule):

    if not rule["enabled"]:
        return False

    if not rule["source"]:
        return False

    if not rule["destination"]:
        return False

    if not rule["service"]:
        return False

    return True


# =====================================================
# PROCESS POLICY FILE
# =====================================================

def process_policy_file(file_path, uid_map):

    logger.info(f"Processando policy: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    rules = data if isinstance(data, list) else data.get("rulebase", [])

    normalized_rules = []

    for rule in rules:

        normalized = normalize_rule(rule, uid_map)

        if valid_rule(normalized):
            normalized_rules.append(normalized)

    relative = file_path.relative_to(INPUT_DIR)
    output_file = OUTPUT_DIR / relative

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(normalized_rules, f, indent=2)

    logger.info(
        f"Rules normalizadas: {len(normalized_rules)} | arquivo: {output_file}"
    )


# =====================================================
# WALK POLICIES
# =====================================================

def walk_policies(uid_map):

    logger.info("Iniciando normalização das policies")

    for package_dir in INPUT_DIR.iterdir():

        if not package_dir.is_dir():
            continue

        logger.info(f"Processando package: {package_dir.name}")

        for file in package_dir.glob("*.json"):
            process_policy_file(file, uid_map)


# =====================================================
# MAIN
# =====================================================

def main():

    logger.info("========== NORMALIZAÇÃO DE RULES ==========")

    uid_map = load_uid_map()

    walk_policies(uid_map)

    logger.info("========== NORMALIZAÇÃO FINALIZADA ==========")


# =====================================================

if __name__ == "__main__":
    main()