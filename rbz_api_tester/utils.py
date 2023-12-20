import json
import socket
import requests


def read_json(file_path: str):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON decoding error: {e}")


def alias_from_api(api_str: str) -> str:
    apis = read_json("./api-map.json")
    for api in apis:
        if api["API"] == api_str:
            return api["alias"]
    raise Exception(f"mapping does not contain api: {api_str}")


def api_from_alias(alias_str: str) -> str:
    apis = read_json("./rbz_api_tester/api-map.json")
    for api in apis["api-to-alias"]:
        if api["alias"] == alias_str:
            return api["API"]
    raise Exception(f"mapping does not contain alias: {alias_str}")


def template_from_alias(alias_str: str) -> str:
    apis = read_json("./rbz_api_tester/api-map.json")
    for api in apis["api-to-alias"]:
        if api["alias"] == alias_str:
            return api["template"]
    raise Exception(f"mapping does not contain alias: {alias_str}")


def defaults_from_alias(alias_str: str) -> str:
    apis = read_json("./rbz_api_tester/api-map.json")
    for api in apis["api-to-alias"]:
        if api["alias"] == alias_str:
            return api["defaults"]
    raise Exception(f"mapping does not contain alias: {alias_str}")


def template_from_api(api_str: str) -> str:
    apis = read_json("./rbz_api_tester/api-map.json")
    for api in apis["api-to-alias"]:
        if api["API"] == api_str:
            return api["template"]
    raise Exception(f"mapping does not contain api: {api_str}")


def defaults_from_api(api_str: str) -> str:
    apis = read_json("./rbz_api_tester/api-map.json")
    for api in apis["api-to-alias"]:
        if api["API"] == api_str:
            return api["defaults"]
    raise Exception(f"mapping does not contain api: {api_str}")


def available_api(clean: bool) -> []:
    res = []
    apis = read_json("./rbz_api_tester/api-map.json")
    for api in apis["api-to-alias"]:
        if bool(api["clean"]) == clean:
            res.append(api["API"])
    return res


def get_my_ip() -> str:
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def get_my_external_ip() -> str:
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json()["ip"]
    except:
        return get_my_ip()
