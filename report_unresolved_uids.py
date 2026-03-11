import json
import os
import re
from utils.logger import setup_logger


logger = setup_logger("report_unresolved_uids")


UID_REGEX = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def is_uid(value):

    if not isinstance(value, str):
        return False

    return UID_REGEX.match(value)


def scan_file(file_path, unresolved):

    with open(file_path, "r", encoding="utf-8") as f:

        data = json.load(f)

    for rule in data:

        for field in ["source", "destination", "service"]:

            value = rule.get(field)

            if is_uid(value):

                unresolved.add(value)


def main():

    logger.info("Iniciando scan de UIDs não resolvidos")

    base_path = "output/resolved"

    unresolved = set()

    for root, dirs, files in os.walk(base_path):

        for file in files:

            if not file.endswith(".json"):
                continue

            file_path = os.path.join(root, file)

            logger.info(f"Analisando {file_path}")

            scan_file(file_path, unresolved)

    output_file = "output/reports/unresolved_uids.json"

    os.makedirs("output/reports", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:

        json.dump(sorted(list(unresolved)), f, indent=2)

    logger.info(f"Total de UIDs não resolvidos: {len(unresolved)}")

    logger.info(f"Relatório salvo em {output_file}")


if __name__ == "__main__":
    main()