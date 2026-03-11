import sys
import json
import requests
import urllib3
from pathlib import Path

# =====================================================
# AJUSTE DE PATH PARA IMPORTAR config.py
# =====================================================

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

# =====================================================
# IMPORTS DO PROJETO
# =====================================================

from config import (
    CHECKPOINT_SERVER,
    USERNAME,
    PASSWORD,
    LIMIT,
    VERIFY_SSL,
    OUTPUT_DIR
)

# =====================================================
# CONFIG
# =====================================================

urllib3.disable_warnings()

OUTPUT_FILE = OUTPUT_DIR / "updatable_objects.json"

# =====================================================
# LOGIN
# =====================================================

def login():

    print("Autenticando no SmartCenter")

    url = f"{CHECKPOINT_SERVER}/web_api/login"

    payload = {
        "user": USERNAME,
        "password": PASSWORD
    }

    r = requests.post(
        url,
        json=payload,
        verify=VERIFY_SSL
    )

    if r.status_code != 200:
        raise Exception(f"Erro login: {r.text}")

    sid = r.json()["sid"]

    return sid


# =====================================================
# EXPORT UPDATABLE OBJECTS
# =====================================================

def export_updatable_objects():

    sid = login()

    headers = {
        "Content-Type": "application/json",
        "X-chkp-sid": sid
    }

    url = f"{CHECKPOINT_SERVER}/web_api/show-updatable-objects"

    offset = 0
    all_objects = []

    while True:

        payload = {
            "limit": LIMIT,
            "offset": offset
        }

        r = requests.post(
            url,
            json=payload,
            headers=headers,
            verify=VERIFY_SSL
        )

        if r.status_code != 200:
            raise Exception(f"Erro API: {r.text}")

        data = r.json()

        objects = data.get("objects", [])

        all_objects.extend(objects)

        print(f"Objetos coletados: {len(all_objects)}")

        if len(objects) < LIMIT:
            break

        offset += LIMIT

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_objects, f, indent=4)

    print(f"\nExport finalizado: {len(all_objects)} objetos")
    print(f"Arquivo salvo em: {OUTPUT_FILE}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    export_updatable_objects()