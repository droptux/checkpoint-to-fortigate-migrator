import os
import sys
import json
import logging

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR, BASE_DIR
from utils.logger import setup_logger


logger = setup_logger("expand_groups.log")

INPUT_DIR = BASE_DIR / "output" / "normalized"
OUTPUT_EXPANDED = BASE_DIR / "output" / "expanded"
OBJECTS_DIR = BASE_DIR / "output" / "objects"

OUTPUT_EXPANDED.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------
# Carrega todos os objetos
# ---------------------------------------------------

def load_objects():

    logger.info("Carregando objetos...")

    objects = {}

    for file in OBJECTS_DIR.glob("*.json"):

        try:
            with open(file, encoding="utf-8") as f:
                data = json.load(f)

        except Exception as e:
            logger.warning(f"Erro ao carregar {file}: {e}")
            continue

        if isinstance(data, list):

            for obj in data:

                name = obj.get("name")

                if name:
                    objects[name] = obj

    logger.info(f"Objetos carregados: {len(objects)}")

    return objects


# ---------------------------------------------------
# Expansão recursiva
# ---------------------------------------------------

def expand_object(obj, objects, visited=None):

    if visited is None:
        visited = set()

    results = []

    # se já for string
    if isinstance(obj, str):

        # UID conhecido
        if obj in objects:

            real_obj = objects[obj]
            name = real_obj.get("name")

            if name:
                return [name]

            return [obj]

        # já é nome
        return [obj]

    # objeto dict
    uid = obj.get("uid")
    name = obj.get("name")
    obj_type = obj.get("type")

    if uid in visited:
        return []

    visited.add(uid)

    # se for host/network/service
    if obj_type not in ["group", "service-group"]:

        if name:
            return [name]

        return [uid]

    # se for grupo
    members = obj.get("members", [])

    for member in members:

        # member pode ser uid
        if isinstance(member, str):

            if member in objects:

                results.extend(
                    expand_object(objects[member], objects, visited)
                )

            else:
                results.append(member)

        # member pode ser dict
        elif isinstance(member, dict):

            results.extend(
                expand_object(member, objects, visited)
            )

    return results


# ---------------------------------------------------
# Expande lista
# ---------------------------------------------------

def expand_list(obj_list, objects):

    expanded = []

    for obj in obj_list:

        if isinstance(obj, dict):
            obj_name = obj.get("name")
        else:
            obj_name = obj

        if not obj_name:
            continue

        expanded.extend(
            expand_object(obj_name, objects)
        )

    return expanded


# ---------------------------------------------------
# Expande rule
# ---------------------------------------------------

def expand_rule(rule, objects):

    src_list = expand_list(rule.get("source", []), objects)
    dst_list = expand_list(rule.get("destination", []), objects)
    svc_list = expand_list(rule.get("service", []), objects)

    expanded_rules = []

    for src in src_list:
        for dst in dst_list:
            for svc in svc_list:

                new_rule = {
                    "name": rule.get("name"),
                    "rule_number": rule.get("rule_number"),
                    "source": src,
                    "destination": dst,
                    "service": svc,
                    "action": rule.get("action"),
                    "enabled": rule.get("enabled")
                }

                expanded_rules.append(new_rule)

    return expanded_rules


# ---------------------------------------------------
# Processa policy
# ---------------------------------------------------

def process_policy(file_path, objects):

    logger.info(f"Processando policy: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            rules = json.load(f)
    except Exception as e:
        logger.error(f"Erro lendo policy {file_path}: {e}")
        return

    expanded_rules = []

    for rule in rules:

        expanded = expand_rule(rule, objects)

        expanded_rules.extend(expanded)

    relative = file_path.relative_to(INPUT_DIR)

    output_file = OUTPUT_EXPANDED / relative

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(expanded_rules, f, indent=2)

    logger.info(
        f"Rules expandidas: {len(expanded_rules)} | arquivo: {output_file}"
    )


# ---------------------------------------------------
# Percorre policies
# ---------------------------------------------------

def walk_policies(objects):

    logger.info("Iniciando expansão de groups")

    for package_dir in INPUT_DIR.iterdir():

        if not package_dir.is_dir():
            continue

        logger.info(f"Processando package: {package_dir.name}")

        for file in package_dir.glob("*.json"):

            process_policy(file, objects)


# ---------------------------------------------------
# MAIN
# ---------------------------------------------------

def main():

    logger.info("========== EXPANSÃO DE GROUPS ==========")

    objects = load_objects()

    walk_policies(objects)

    logger.info("========== EXPANSÃO FINALIZADA ==========")


if __name__ == "__main__":
    main()