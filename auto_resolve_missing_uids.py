import json
import os
import re

from utils.logger import setup_logger
from modules.smart_uid_resolver import SmartUIDResolver


logger = setup_logger("auto_resolve_missing_uids")


UID_REGEX = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def is_uid(value):

    if not isinstance(value, str):
        return False

    return UID_REGEX.match(value)


def load_objects():

    logger.info("Carregando objetos exportados")

    objects_path = "output/objects"

    uid_map = {}

    for root, dirs, files in os.walk(objects_path):

        for file in files:

            if not file.endswith(".json"):
                continue

            file_path = os.path.join(root, file)

            try:

                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            except Exception as e:

                logger.warning(f"Erro lendo {file_path}: {e}")
                continue

            objects = []

            # Caso 1 — lista direta
            if isinstance(data, list):
                objects = data

            # Caso 2 — dict com objects
            elif isinstance(data, dict):

                if "objects" in data:
                    objects = data["objects"]

                else:
                    objects = [data]

            # Caso 3 — ignorar
            else:
                logger.debug(f"Ignorando formato desconhecido: {file_path}")
                continue

            for obj in objects:

                if not isinstance(obj, dict):
                    continue

                uid = obj.get("uid")
                name = obj.get("name")

                if uid and name:
                    uid_map[uid] = name

    logger.info(f"Total de objetos carregados: {len(uid_map)}")

    return uid_map


def process_file(file_path, resolver):

    with open(file_path, "r", encoding="utf-8") as f:

        data = json.load(f)

    modified = False

    for rule in data:

        for field in ["source", "destination", "service"]:

            value = rule.get(field)

            if is_uid(value):

                resolved = resolver.resolve(value)

                if resolved != value:

                    rule[field] = resolved
                    modified = True

    if modified:

        with open(file_path, "w", encoding="utf-8") as f:

            json.dump(data, f, indent=2)


def main():

    logger.info("Iniciando auto resolução de UIDs")

    uid_map = load_objects()

    resolver = SmartUIDResolver(uid_map, logger)

    base_path = "output/resolved"

    for root, dirs, files in os.walk(base_path):

        for file in files:

            if not file.endswith(".json"):
                continue

            file_path = os.path.join(root, file)

            logger.info(f"Processando arquivo: {file_path}")

            process_file(file_path, resolver)

    logger.info("Auto resolução de UIDs finalizada")


if __name__ == "__main__":
    main()