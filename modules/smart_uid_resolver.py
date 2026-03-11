import json
import os
import requests


class SmartUIDResolver:

    def __init__(self, uid_map, logger, mgmt_server=None, sid=None):
        self.uid_map = uid_map
        self.logger = logger
        self.mgmt_server = mgmt_server
        self.sid = sid
        self.cache = {}
        self.updatable_map = self._load_updatable_objects()

    def _load_updatable_objects(self):

        path = "data/updatable_objects.json"

        if not os.path.exists(path):
            return {}

        try:

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            return {o["uid"]: o["name"] for o in data}

        except Exception as e:

            self.logger.warning(f"Erro carregando updatable objects: {e}")

            return {}

    def resolve(self, uid):

        if uid in self.cache:
            return self.cache[uid]

        if uid in self.uid_map:
            name = self.uid_map[uid]
            self.cache[uid] = name
            return name

        if uid in self.updatable_map:
            name = self.updatable_map[uid]
            self.cache[uid] = name
            return name

        if self.mgmt_server and self.sid:
            name = self._resolve_via_api(uid)

            if name:
                self.cache[uid] = name
                return name

        return uid

    def _resolve_via_api(self, uid):

        try:

            url = f"https://{self.mgmt_server}/web_api/show-object"

            headers = {
                "Content-Type": "application/json",
                "X-chkp-sid": self.sid
            }

            payload = {
                "uid": uid
            }

            r = requests.post(url, json=payload, headers=headers, verify=False)

            if r.status_code == 200:

                data = r.json()

                name = data.get("name")

                if name:
                    self.logger.info(f"UID resolvido via API {uid} -> {name}")
                    return name

        except Exception as e:

            self.logger.error(f"Erro consultando API para UID {uid}: {e}")

        return None