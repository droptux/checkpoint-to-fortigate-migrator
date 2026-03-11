import json
from pathlib import Path

from core.checkpoint_client import CheckpointClient
from utils.logger import setup_logger

from config import (
    OBJECTS_DIR,
    LIMIT
)

logger = setup_logger("objects_extraction.log")


# ==========================================================
# SAVE JSON
# ==========================================================

def save_json(filename, data):

    path = OBJECTS_DIR / filename

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    logger.info(f"[SAVE] {path}")


# ==========================================================
# SAFE PAGINATED EXTRACTION
# ==========================================================

def extract_paginated(client, api_command, key="objects"):

    logger.info(f"[START] {api_command}")

    offset = 0
    objects = []

    try:

        while True:

            payload = {
                "limit": LIMIT,
                "offset": offset,
                "details-level": "full"
            }

            data = client.api_call(api_command, payload)

            chunk = data.get(key, [])

            if not chunk:
                break

            objects.extend(chunk)

            logger.info(
                f"{api_command} | offset={offset} | extraídos={len(chunk)} | total={len(objects)}"
            )

            offset += LIMIT

    except Exception as e:

        logger.warning(f"[SKIP] {api_command} falhou: {e}")

        return []

    logger.info(f"[DONE] {api_command} total={len(objects)}")

    return objects


# ==========================================================
# SAFE NON-PAGINATED EXTRACTION
# ==========================================================

def extract_simple(client, api_command, key="objects"):

    logger.info(f"[START] {api_command}")

    try:

        data = client.api_call(
            api_command,
            {
                "details-level": "full"
            }
        )

        objects = data.get(key, [])

        logger.info(f"[DONE] {api_command} total={len(objects)}")

        return objects

    except Exception as e:

        logger.warning(f"[SKIP] {api_command} falhou: {e}")

        return []


# ==========================================================
# TIME OBJECTS (VERSÃO COMPATÍVEL)
# ==========================================================

def extract_time_objects(client):

    logger.info("[START] Extraindo objetos de tempo")

    data = extract_paginated(client, "show-time-groups")

    if data:
        save_json("time_objects.json", data)
        return

    data = extract_paginated(client, "show-time")

    if data:
        save_json("time_objects.json", data)
        return

    logger.warning("Nenhum objeto de tempo encontrado")


# ==========================================================
# BUILTIN OBJECTS (ANY / ANY SERVICE)
# ==========================================================

def inject_builtin_objects():

    logger.info("[INFO] Injetando objetos built-in")

    builtin = [

        {
            "name": "Any",
            "uid": "builtin-any",
            "type": "CpmiAnyObject"
        },
        {
            "name": "Any-IPv4",
            "uid": "builtin-any-ipv4",
            "type": "CpmiAnyObject"
        },
        {
            "name": "Any-IPv6",
            "uid": "builtin-any-ipv6",
            "type": "CpmiAnyObject"
        },
        {
            "name": "any",
            "uid": "builtin-any-service",
            "type": "service-any"
        }
    ]

    save_json("builtin_objects.json", builtin)


# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info("========== INICIANDO EXTRAÇÃO CHECKPOINT ==========")

    client = CheckpointClient()
    client.login()

    # ======================================================
    # PACKAGES
    # ======================================================

    packages = extract_simple(client, "show-packages", "packages")
    save_json("packages.json", packages)

    # ======================================================
    # ADDRESS OBJECTS
    # ======================================================

    save_json("hosts.json",
              extract_paginated(client, "show-hosts"))

    save_json("networks.json",
              extract_paginated(client, "show-networks"))

    save_json("ranges.json",
              extract_paginated(client, "show-address-ranges"))

    save_json("groups.json",
              extract_paginated(client, "show-groups"))

    save_json("dns_domains.json",
              extract_paginated(client, "show-dns-domains"))

    save_json("dynamic_objects.json",
              extract_simple(client, "show-dynamic-objects"))

    save_json("updatable_objects.json",
              extract_paginated(client, "show-updatable-objects"))

    # ======================================================
    # SERVICES
    # ======================================================

    save_json("services_tcp.json",
              extract_paginated(client, "show-services-tcp"))

    save_json("services_udp.json",
              extract_paginated(client, "show-services-udp"))

    save_json("services_icmp.json",
              extract_paginated(client, "show-services-icmp"))

    save_json("services_sctp.json",
              extract_paginated(client, "show-services-sctp"))

    save_json("services_other.json",
              extract_paginated(client, "show-services-other"))

    save_json("service_groups.json",
              extract_paginated(client, "show-service-groups"))

    # ======================================================
    # APPLICATION CONTROL
    # ======================================================

    save_json("application_sites.json",
              extract_paginated(client, "show-application-sites"))

    save_json("application_site_groups.json",
              extract_paginated(client, "show-application-site-groups"))

    # ======================================================
    # ACCESS OBJECTS
    # ======================================================

    save_json("access_roles.json",
              extract_paginated(client, "show-access-roles"))

    extract_time_objects(client)

    # ======================================================
    # VPN
    # ======================================================

    save_json("vpn_star_communities.json",
              extract_simple(client, "show-vpn-communities-star"))

    save_json("vpn_mesh_communities.json",
              extract_simple(client, "show-vpn-communities-mesh"))

    # ======================================================
    # BUILTIN OBJECTS
    # ======================================================

    inject_builtin_objects()

    client.logout()

    logger.info("========== EXTRAÇÃO FINALIZADA ==========")


if __name__ == "__main__":
    main()