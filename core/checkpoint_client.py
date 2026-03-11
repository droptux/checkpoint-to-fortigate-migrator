import requests
import logging
import urllib3
from config import CHECKPOINT_SERVER, USERNAME, PASSWORD, VERIFY_SSL
urllib3.disable_warnings()

logger = logging.getLogger(__name__)


class CheckpointClient:

    def __init__(self):

        self.base_url = f"{CHECKPOINT_SERVER}/web_api"
        self.session = requests.Session()
        self.session.verify = VERIFY_SSL
        self.sid = None

    def login(self):

        logger.info("[API] Realizando login")

        payload = {
            "user": USERNAME,
            "password": PASSWORD
        }

        response = self.session.post(
            f"{self.base_url}/login",
            json=payload
        )

        response.raise_for_status()

        data = response.json()

        self.sid = data["sid"]

        self.session.headers.update({
            "X-chkp-sid": self.sid
        })

        logger.info("[API] Login realizado com sucesso")

    def api_call(self, command, payload=None):

        if payload is None:
            payload = {}

        url = f"{self.base_url}/{command}"

        response = self.session.post(url, json=payload)

        response.raise_for_status()

        return response.json()

    def logout(self):

        logger.info("[API] Encerrando sessão")

        try:

            self.session.post(f"{self.base_url}/logout")

            logger.info("[API] Logout realizado com sucesso")

        except Exception as e:

            logger.warning(f"[API] Falha no logout: {e}")