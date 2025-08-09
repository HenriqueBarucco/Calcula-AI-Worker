from helpers.logger import logger

import requests

from config.env import API_URL

def send_patch(session_id: str, price_id: str, name: str, value: float) -> None:
    headers = {"session": session_id, "Content-Type": "application/json"}
    body = {"priceId": price_id, "name": name, "value": value}
    logger.info(f"Sending PATCH: {body}")
    r = requests.patch(f"{API_URL}/v1/sessions/prices", headers=headers, json=body)
    r.raise_for_status()
    logger.info(f"PATCH OK: {r.text}")


def delete_price(session_id: str, price_id: str) -> None:
    headers = {"session": session_id}
    url = f"{API_URL}/v1/sessions/prices/{price_id}"
    logger.info(f"Sending DELETE: {url}")
    r = requests.delete(url, headers=headers)
    r.raise_for_status()
    logger.info(f"DELETE OK: {r.text}")