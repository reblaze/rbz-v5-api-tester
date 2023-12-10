import json
from rbz_api_tester.Param import TestSuite
from rbz_api_tester.Param import Test
from rbz_api_tester.Param import Steps
from rbz_api_tester.Param import Param
from rbz_api_tester.Param import Payload
from rbz_api_tester.Param import Expected
from haralyzer import HarParser
from typing import List


def translate_api(url):
    for key in translator.keys():
        if str(url).startswith(key):
            return translator[key]
    return ""


planet_url = "https://rbzdevtester.dev.app.reblaze.io"
har_parser = HarParser.from_file(
    "c:/Users/Mor/Downloads/rbzdevtester.dev.app.reblaze.io.har"
)
translator = {
    "/conf/api/v3/configs/prod/d/aclprofiles": "aclprofile",
    "/conf/api/v3/configs/prod/d/actions": "action",
    "/reblaze/api/v3/reblaze/configs/prod/d/backends": "backend",
    "/reblaze/api/v3/reblaze/configs/prod/d/cloud-functions": "cloudfunction",
    "/conf/api/v3/configs/prod/d/contentfilterprofiles": "contentfilterprofile",
    "/conf/api/v3/configs/prod/d/contentfilterrules": "contentfilterrule",
    "/reblaze/api/v3/reblaze/configs/prod/d/dynamic-rules": "dynamicrule",
    "/conf/api/v3/configs/prod/d/flowcontrol": "flowcontrol",
    "/conf/api/v3/configs/prod/d/globalfilters": "globalfilter",
    "/reblaze/api/v3/reblaze/configs/prod/d/proxy-templates": "proxytemplate",
    "/conf/api/v3/configs/prod/d/ratelimits": "ratelimit",
    "/reblaze/api/v3/reblaze/configs/prod/d/routing-profiles": "routingprofile",
    "/conf/api/v3/configs/prod/d/securitypolicies": "securitypolicy",
    "/reblaze/api/v3/reblaze/configs/prod/d/sites": "servergroup",
}

mime_types = [
    "text/plain",
    "text/html",
    "text/json",
    "text/xml",
    "application/octet-stream",
    "application/pdf",
    "application/zip",
    "application/msword",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/json",
    "application/xml",
    "application/xhtml+xml",
]

types_with_no_quotes = (int, bool, float)

# Parse the HAR data
har_data = har_parser.har_data

test_suite = TestSuite("Add your test suite name here", False, list())
test = Test("Add your test name here", False, list())
step_num = 1
# Print details of each entry
for entry in har_data["entries"]:
    request = entry["request"]
    response = entry["response"]

    mime_type = str(entry["response"]["content"]["mimeType"])

    if mime_type not in mime_types:
        continue

    url = request["url"]
    method = request["method"]
    status = response["status"]

    response_type = None
    results = None
    response_text = None

    if response["content"]["mimeType"] == "application/json":
        response_type = "json"
        response_json = json.loads(response["content"]["text"])
        results = list()
        if type(response_json) is list:
            for item in response_json:
                for key, value in item.items():
                    val = None
                    if isinstance(value, types_with_no_quotes):
                        val = value
                    else:
                        val = str(value)
                    param = Param(Key=key, Value=val)
                    results.append(param)
        else:
            for key, value in response_json.items():
                val = None
                if isinstance(value, types_with_no_quotes):
                    val = value
                else:
                    val = str(value)
                param = Param(Key=key, Value=val)
                results.append(param)

    else:
        response_text = response["content"]["text"]
        response_type = "text"

    if method == "POST" or method == "PUT":
        payload = json.loads(request["postData"]["text"])
        params = list()
        for key, value in payload.items():
            val = None
            if type(value) is str:
                val = '"' + value + '"'
            elif isinstance(value, types_with_no_quotes):
                val = value
            else:
                val = str(value)
            param = Param(Key=key, Value=val)
            params.append(param)

        if results is None:
            step = Steps(
                Name="Add your step name here",
                Skip=False,
                GenerateID=False,
                Step=step_num,
                Method=method,
                API=str(url).replace(planet_url, ""),
                Payload=Payload(
                    Defaults=f"{translate_api(str(url).replace(planet_url, ''))}.defaults",
                    Template=f"{translate_api(str(url).replace(planet_url, ''))}.template",
                    Params=params,
                ),
                Expected=Expected(
                    Code=int(response["status"]),
                    Type=response_type,
                    Results=None,
                    Text=response_text,
                ),
            )
        else:
            step = Steps(
                Name="Add your step name here",
                Skip=False,
                GenerateID=False,
                Step=step_num,
                Method=method,
                API=str(url).replace(planet_url, ""),
                Payload=Payload(
                    Defaults=f"{translate_api(str(url).replace(planet_url, ''))}.defaults",
                    Template=f"{translate_api(str(url).replace(planet_url, ''))}.template",
                    Params=params,
                ),
                Expected=Expected(
                    Code=int(response["status"]),
                    Type=response_type,
                    Results=results,
                    Text=None,
                ),
            )

    else:
        if results is None:
            step = Steps(
                Name="Add your step name here",
                Skip=False,
                GenerateID=False,
                Step=step_num,
                Method=method,
                API=str(url).replace(planet_url, ""),
                Payload=None,
                Expected=Expected(
                    Code=int(response["status"]),
                    Type=response_type,
                    Results=None,
                    Text=response_text,
                ),
            )
        else:
            step = Steps(
                Name="Add your step name here",
                Skip=False,
                GenerateID=False,
                Step=step_num,
                Method=method,
                API=str(url).replace(planet_url, ""),
                Payload=None,
                Expected=Expected(
                    Code=int(response["status"]),
                    Type=response_type,
                    Results=results,
                    Text=None,
                ),
            )

    test.Steps.append(step)

test_suite.Tests.append(test)
with open("my_suite.json", "w") as output_file:
    content = json.dumps(test_suite.to_dict())
    output_file.write(content)
    output_file.close()
