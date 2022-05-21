import os
import json
import datetime

import requests


AUTH0_CLIENT_ID = os.environ.get("AUTH0_CLIENT_ID", "")
AUTH0_CLIENT_SECRET = os.environ.get("AUTH0_CLIENT_SECRET", "")
AUTH0_DOMAIN = os.environ.get("AUTH0_DOMAIN", "")
AUTH0_AUDIENCE = os.environ.get("AUTH0_AUDIENCE", "")


def get_token() -> str:
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": "sky.kip.dev",
        "grant_type": "client_credentials",
    }
    r = requests.post(f"https://{AUTH0_DOMAIN}/oauth/token", json=payload)
    return r.json()["access_token"]


def test_root():
    token = get_token()

    r = requests.get(
        "http://127.0.0.1:8000/", headers={"authorization": f"Bearer {token}"}
    )
    print(r.json())


if __name__ == "__main__":
    test_root()
