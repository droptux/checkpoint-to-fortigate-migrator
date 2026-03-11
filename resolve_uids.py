import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import OUTPUT_DIR
from utils.logger import setup_logger


logger = setup_logger("resolve_uids.log")

NORMALIZED_DIR = OUTPUT_DIR / "normalized"
OBJECTS_DIR = OUTPUT_DIR / "objects"
RESOLVED_DIR = OUTPUT_DIR / "resolved"

RESOLVED_DIR.mkdir(parents=True, exist_ok=True)


SYSTEM_UID_MAP = {

    "6c488338-8eec-4103-ad21-cd461ac2c472": "accept",
    "6c488338-8eec-4103-ad21-cd461ac2c473": "drop",

    "97aeb369-9aea-11d5-bd16-0090272ccb30": "any",
    "00000000-0000-0000-0000-000000000000": "any"

}


def load_objects():

    logger.info("Carregando objetos...")

    objects_index = {}

    for file in OBJECTS_DIR.glob("*.json"):

        with open(file, "r", encoding="utf-8") as f:

            data = json.load(f)

            if not isinstance(data, list):
                continue

            for obj in data:

                if not isinstance(obj, dict):
                    continue

                uid = obj.get("uid")

                if not uid:
                    continue

                objects_index[uid] = obj

    logger.info(f"Objetos indexados: {len(objects_index)}")

    return objects_index


def resolve_value(value, objects):

    if value in SYSTEM_UID_MAP:
        return SYSTEM_UID_MAP[value]

    if value in objects:

        obj = objects[value]

        name = obj.get("name")

        if name:
            return name

    return value


def resolve_list(values, objects):

    resolved = []

    for v in values:

        resolved.append(resolve_value(v, objects))

    return resolved


def resolve_action(value, objects):

    if value in SYSTEM_UID_MAP:
        return SYSTEM_UID_MAP[value]

    if value in objects:

        name = objects[value].get("name", "").lower()

        if name in ["accept", "allow"]:
            return "accept"

        if name in ["drop", "deny", "reject"]:
            return "drop"

    return value


def process_file(file_path, objects):

    logger.info(f"Processando {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:

        rules = json.load(f)

    resolved = []

    for rule in rules:

        rule["source"] = resolve_list(rule.get("source", []), objects)

        rule["destination"] = resolve_list(rule.get("destination", []), objects)

        rule["service"] = resolve_list(rule.get("service", []), objects)

        rule["action"] = resolve_action(rule.get("action"), objects)

        resolved.append(rule)

    output_path = RESOLVED_DIR / file_path.name

    with open(output_path, "w", encoding="utf-8") as f:

        json.dump(resolved, f, indent=2)

    logger.info(f"Rules resolvidas: {len(resolved)}")


def main():

    logger.info("========== RESOLVE UIDS ==========")

    objects = load_objects()

    for file in NORMALIZED_DIR.glob("*.json"):

        process_file(file, objects)

    logger.info("========== FINALIZADO ==========")


if __name__ == "__main__":
    main()