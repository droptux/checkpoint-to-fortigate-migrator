import os
import json
import time
import logging

from core.checkpoint_client import CheckpointClient
from utils.logger import setup_logger
from config import OBJECTS_DIR
from config import POLICIES_DIR
from config import NORMALIZED_DIR
from config import FLATTEN_DIR



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("rules_extractor.txt"),
        logging.StreamHandler()
    ]
)

OUTPUT_POLICIES = POLICIES_DIR

def save_json(data, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logging.info(f"Arquivo salvo: {path}")


def extract_layer_rules(client, layer_name, package_name):

    logging.info(f"Extraindo rules da layer: {layer_name}")
    start_time = time.time()

    offset = 0
    limit = 500

    all_rules = []
    total_expected = None

    while True:

        payload = {
            "name": layer_name,
            "offset": offset,
            "limit": limit,
            "details-level": "full"
        }

        response = client.api_call("show-access-rulebase", payload)

        if total_expected is None:
            total_expected = response.get("total", 0)
            logging.info(f"Total esperado de rules: {total_expected}")

        rules = response.get("rulebase", [])

        count = len(rules)

        if count == 0:
            break

        all_rules.extend(rules)

        progress = (len(all_rules) / total_expected) * 100 if total_expected else 0

        logging.info(
            f"[{package_name}] offset {offset} | "
            f"extraídas {count} rules | "
            f"total coletado {len(all_rules)} | "
            f"{progress:.1f}%"
        )

        offset += limit

        if len(all_rules) >= total_expected:
            break

    elapsed = round(time.time() - start_time, 2)

    logging.info(
        f"Layer {layer_name} finalizada | "
        f"{len(all_rules)} rules extraídas | "
        f"tempo {elapsed}s"
    )

    return all_rules


def main():

    logging.info("INICIANDO EXTRAÇÃO RULEBASE")

    client = CheckpointClient()
    client.login()

    logging.info("Extraindo policy packages")

    packages = client.api_call("show-packages", {
        "limit": 500,
        "details-level": "full"
    })

    packages_list = packages.get("packages", [])

    logging.info(f"{len(packages_list)} packages encontrados")

    for package in packages_list:

        package_name = package["name"]

        logging.info(f"Processando package: {package_name}")

        layers = package.get("access-layers", [])

        for layer in layers:

            layer_name = layer["name"]

            rules = extract_layer_rules(client, layer_name, package_name)

            output_path = os.path.join(
                OUTPUT_POLICIES,
                package_name,
                f"{layer_name}.json"
            )

            save_json(rules, output_path)

    logging.info("EXTRAÇÃO RULEBASE FINALIZADA")

    client.logout()


if __name__ == "__main__":
    main()