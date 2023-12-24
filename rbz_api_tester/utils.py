import json
import socket
import requests
import uuid

from rbz_api_tester.CommonParameters import CommonParameters


def generate_uuid():
    dt = int((uuid.uuid1().time * 10000) & 0xFFFFFFFFFFFF)
    return "api_tester_" + str(uuid.UUID(f"{dt:032x}")).split("-")[4]


def read_json(file_path: str):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decoding error: {e}")


def get_my_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def get_my_external_ip() -> str:
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return get_my_ip()
