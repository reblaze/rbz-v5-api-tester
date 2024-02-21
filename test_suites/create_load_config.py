import requests
import json
import argparse

parser = argparse.ArgumentParser(description='Create config for load tests')
parser.add_argument('-p', '--planet_name', type=str, help='Planet name', required=True)
parser.add_argument('-k', '--api_key', type=str, help='API key', required=True)
args = parser.parse_args()

PLANET = args.planet_name
HOST = f'https://{args.planet_name}.dev.app.reblaze.io'
APIKEY = args.api_key


def make_request(method, endpoint, entity_id, data=None):
    headers = {'Authorization': f'Basic {APIKEY}'}
    if method == 'GET':
        response = requests.get(f'{HOST}/api/v4/conf/prod/{endpoint}/{entity_id}', headers=headers)
    elif method == 'PUT':
        headers['Content-Type'] = 'application/json'
        response = requests.put(f'{HOST}/api/v4/conf/prod/{endpoint}/{entity_id}', headers=headers,
                                data=json.dumps(data))
    elif method == 'DELETE':
        response = requests.delete(f'{HOST}/api/v4/conf/prod/{endpoint}/{entity_id}', headers=headers)
    elif method == 'POST':
        headers['Content-Type'] = 'application/json'
        response = requests.post(f'{HOST}/api/v4/conf/prod/{endpoint}/{entity_id}', headers=headers,
                                 data=json.dumps(data))
    else:
        print(f'Unsupported HTTP method: {method}')
        exit(1)
    return response

def publish_config():
    headers = {'Authorization': f'Basic {APIKEY}'}
    headers['Content-Type'] = 'application/json'
    data = []
    publish_data = {'name': 'prod', 'url': f'gs://rbz-{PLANET}-config/prod/'}
    data.append(publish_data)
    response = requests.put(f'{HOST}/api/v4/tools/publish/prod', headers=headers, data=json.dumps(data))
    return response

# Create 20 acl profiles
for i in range(1, 19):
    acl_data = {'id': f'acl{i}', 'name': f'acl{i}', 'description': f'New ACL Profile Description and Remarks',
                'action': f'action-acl-block', 'tags': [], 'allow': ['allow-tag'], 'allow_bot': ['allow-bot-tag'],
                'deny_bot': ['deny-bot-tag'], 'passthrough': ['passthrough-tag'], 'force_deny': ['force-deny-tag'],
                'deny': ['deny-tag']}
    response = make_request('POST', 'acl-profiles', acl_data['id'], acl_data)
    if response.status_code != 201:
        exit(1)

# Create 100 server groups
for i in range(1, 101):
    # Create backend
    be_data = {'id': f'backend{i}', 'name': f'backend{i}', 'http11': True, 'transport_mode': 'default',
               'sticky': 'none', 'sticky_cookie_name': '', 'least_conn': False,
               'back_hosts': [{'backup': False, 'down': False, 'fail_timeout': 10, 'host': f'test{i}.evgeniytestzone.dev.rbzdns.com',
                               'http_port': 80, 'https_port': 443, 'max_fails': 0, 'monitor_state': '0', 'weight': 1,
                               'id': f'host{i}'}]}
    response = make_request('POST', 'backend-services', f'backend{i}', be_data)
    if response.status_code != 201:
        exit(1)
    # Create path mapping with 20 paths, including default and deny-bot
    sp_map = [{'id': '__default_entry__', 'match': '/', 'name': 'default', 'acl_profile': '__acldefault__',
               'content_filter_profile': '__defaultcontentfilter__', 'backend_id': f'backend{i}', 'acl_active': True,
               'content_filter_active': True,
               'limit_ids': ['rl-asn-path-ddos', 'rl-session-host-ddos', 'rl-session-path-ddos'],
               'cloud_functions': ['redirectHTTPToHTTPS', 'rewriteURLSegment']},
              {'id': 'deny_bot', 'match': '/deny-bot', 'name': 'deny_bot', 'acl_profile': '__acldenybot__',
               'content_filter_profile': '__defaultcontentfilter__', 'backend_id': f'backend{i}', 'acl_active': True,
               'content_filter_active': True,
               'limit_ids': ['rl-asn-path-ddos', 'rl-session-host-ddos', 'rl-session-path-ddos'],
               'cloud_functions': ['redirectHTTPToHTTPS', 'rewriteURLSegment']}]
    for j in range(1, 19):
        map_data = {'id': f'test{j}', 'name': f'test{j}', 'match': f'/test{j}/[a-z]+/yyyyy', 'acl_profile': f'acl{j}',
                    'content_filter_profile': '__defaultcontentfilter__', 'backend_id': f'backend{i}',
                    'acl_active': True,
                    'content_filter_active': True,
                    'limit_ids': ['rl-asn-path-ddos', 'rl-session-host-ddos', 'rl-session-path-ddos'],
                    'cloud_functions': ['redirectHTTPToHTTPS', 'rewriteURLSegment']}
        sp_map.append(map_data)
    # Create security policy
    sp_data = {'id': f'test_sp{i}', 'name': f'test_sp{i}', 'match': f'__default__', 'tags': [],
               'session': [{'attrs': 'ip'}],
               'map': sp_map}
    response = make_request('POST', 'security-policies', f'test_sp{i}', sp_data)
    if response.status_code != 201:
        exit(1)
    # Create server group
    sg_data = {'name': f'test{i}.site', 'id': f'test{i}_site', 'mobile_sdk': '', 'description': '',
               'proxy_template': '__default__', 'routing_profile': '__default__', 'security_policy': f'test_sp{i}',
               'server_names': [f'test{i}.site'], 'ssl_certificate': 'placeholder',
               'challenge_cookie_domain': '$host'}
    response = make_request('POST', 'server-groups', f'test{i}_site', sg_data)
    if response.status_code != 201:
        exit(1)
response = publish_config()
if response.status_code != 200:
    exit(1)

