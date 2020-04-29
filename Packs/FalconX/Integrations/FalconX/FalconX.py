from typing import Dict, Callable, Tuple, Any

import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *

import json
import requests

# Disable insecure warnings
requests.packages.urllib3.disable_warnings()
access_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6InB1YmxpYzphNDdiNTc2MS0zYzk3LTQwMmItOTgzNi0wNmNhODI0NTViOTMiLCJ0eXAiOiJKV1QifQ.eyJhdWQiOlsiMTU3YjMyZjRmNWE5NDQ1Yjg1ODRiODM3ZWY4MDQ0NzciXSwiY2xpZW50X2lkIjoiMTU3YjMyZjRmNWE5NDQ1Yjg1ODRiODM3ZWY4MDQ0NzciLCJleHAiOjE1ODgxNzEwNzAsImlhdCI6MTU4ODE2OTI3MCwiaXNzIjoiaHR0cHM6Ly9hcGkuY3Jvd2RzdHJpa2UuY29tLyIsImp0aSI6ImU5NWYyMTZmLTJhYzMtNGViYi04YjNiLTg2ZDdkODU2MDdhOCIsIm5iZiI6MTU4ODE2OTI3MCwic3ViIjoiMTU3YjMyZjRmNWE5NDQ1Yjg1ODRiODM3ZWY4MDQ0NzcifQ.O9heF_Cii5lk53jF9UJ--I9DP1yG1NjtTp6sz16ff6mCJt3dm3wLKQaFvpj46lhApIqmqupnts2Bnm8Vt7abwppzOA5umTmFKPuFJXrKg8wJmGUF2CEV597qLj4ytq3Iw-VuohVZnv2YMSfwjDBdwzT7cJhMzvJbGFwNg4BPw5e6oJbj--0gCE_2RDaeYivGGgYDcC9njaN12WXRNuZUvKFyjnjKHHsHwtbEPqN4r09bxiKqQ2Fbcj2FuDwtpEDdWPbIe3MKrYo0cuhjJWiEIgUO9haobcQH13gD3RXo9PUOr1m_zSw3DpTJe1MooLizIsjljjyJt3evdY4qEXhEt9b9nY8zBTeSQfhwtNxL-HDrZjpk8DP5OVzGhjvmT1Ok_z0V0XWjMWnb58rB45gNWEolSfKtkwjtlO2bneCe1vKrshJmXW7z1aK7VVNEDCtwRZ_Otn44jTYYUHNm4paBogTNyFfmmPNjO0bIkfTFRqT0hSUZRWeaYcYPEsj1HaW7BpmlPI-MTmDi77MW28OAKZFMYlLWQqQcy4jiwzQEHCDNZC9JHPszTsVF_XkouK3salEHW_bdceAdYZjq4k02tz3A-T-t10bDmC2NLGPmqNvAgdwykK3ao1Ecn6aANlrtoylRaYt9_M0JEOyi1is1h-BGR5Pt71ZU8I5vqS0DV4E"


class Client(BaseClient):
    """
      Client to use in the FalconX integration. Overrides BaseClient
      """

    def __init__(self, server_url: str, username: str, password: str):
        self._base_url = server_url
        self._username = username
        self._password = password
        #self.token = self._generate_token()
        self.token = access_token

    def http_request(self, method, url_suffix, data, headers=None, params=None, response_type: str = 'json'):
        """
        Generic request to FalconX
        """
        full_url = urljoin(self._base_url, url_suffix)

        try:
            result = requests.request(
                method,
                full_url,
                verify=False,
                params=params,
                data=data,
                headers=headers,
            )
            if not result.ok:
                demisto.log(result.text)
                raise ValueError(f'Error in API call to FalconX {result.status_code}. Reason: {result.text}')

            if response_type != 'json':
                return result.text
            return result.json()

        except Exception as exception:
            raise Exception(str(exception))

    def _generate_token(self) -> str:
        """Generate an Access token

        Returns:
            valid token
        """

        body = {
            'client_id': self._username,
            'client_secret': self._password
        }

        BYTE_CREDS = f'{self._username}:{self._password}'.encode('utf-8')

        HEADERS = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Basic {base64.b64encode(BYTE_CREDS).decode()}'
        }

        headers = {
            'Authorization': HEADERS['Authorization']
        }
        token_res = self.http_request('POST', '/oauth2/token', data=body, headers=headers)
        # print(token_res.text)
        return token_res.get('access_token')


def test_module(client, args):
    """
    If a client was made then an accesses token was successfully reached,
    therefor the username and password are valid and a connection was made
    """
    demisto.log("OK!!!!")
    return 'ok'


# is failing
def upload_file(client, args):

    file = args.get('file', "")
    file_name = args.get('file_name', "")
    comment = args.get('comment', "")
    is_confidential = args.get('is_confidential')

    if not file or not file_name:
        raise ValueError('Please add a valid file and file name.')

    url_suffix = f"/samples/entities/samples/v2?file_name={file_name}&is_confidential={is_confidential}&comment={comment}"

    headers = {
        'Authorization': 'Bearer '+access_token,
        'Content-Type': 'application/octet-stream',
    }

    data = open(file, 'rb').read()

    response = client.http_request("POST", url_suffix, data=data, headers=headers)
    # demisto.log(response.text)
    return response


def send_uploaded_file_to_sendbox_analysis(client, args):
    sha256 = args.get('sha256', "")
    environment_id = args.get('environment_id', "")
    action_script = args.get('action_script', "")
    command_line = args.get('command_line', "")
    document_password = args.get('document_password')
    enable_tor = args.get('enable_tor') # default is false
    submit_name = args.get('submit_name', "")
    system_date = args.get('system_date', "")
    system_time = args.get('system_time', "")

    url_suffix = "/falconx/entities/submissions/v1"
    body = {
        "sandbox": [
            {
                "sha256": sha256,
                "environment_id": environment_id,
                "action_script": action_script,
                "command_line": command_line,
                "document_password": document_password,
                "enable_tor": enable_tor,
                "submit_name": submit_name,
                "system_date": system_date,
                "system_time": system_time
            }
        ]
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
    }
    response = client.http_request("POST", url_suffix, data=body, headers=headers)
    # demisto.log(response.text)
    return response


def send_url_to_sandbox_analysis(client, args):
    url_suffix = "/falconx/entities/submissions/v1"
    url = args.get('url', "")
    environment_id = args.get('environment_id', "")
    action_script = args.get('action_script', "")
    command_line = args.get('command_line', "")
    document_password = args.get('document_password')
    enable_tor = args.get('enable_tor')  # default is false
    submit_name = args.get('submit_name', "")
    system_date = args.get('system_date', "")
    system_time = args.get('system_time', "")

    body = {
        "sandbox": [
            {
                "url": url,
                "environment_id": environment_id,
                "action_script": action_script,
                "command_line": command_line,
                "document_password": document_password,
                "enable_tor": enable_tor,
                "submit_name": submit_name,
                "system_date": system_date,
                "system_time": system_time
            }
        ]
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json',
    }
    response = client.http_request("POST", url_suffix, data=body, headers=headers)
    # demisto.log(response.text)
    return response


def get_full_report(client, args):
    ids = args.get("ids", "")
    url_suffix = f"/falconx/entities/reports/v1?ids={id}"
    params = {
        "ids": ids
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def get_report_summary(client, args):
    ids = args.get("ids", "")
    url_suffix = f"/falconx/entities/report-summaries/v1?ids={id}"
    params = {
        "ids": ids
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def get_analysis_status(client, args):
    ids = args.get("ids", "")
    url_suffix = f"/falconx/entities/submissions/v1?ids={ids}"

    params = {
        "ids": ids
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def download_ioc(client, args):
    id = args.get("id", "")
    accept_encoding = args.get("accept_encoding", "")
    url_suffix = f"/falconx/entities/artifacts/v1?id={id}" \
                 f"&name=&Accept-Encoding={accept_encoding}"

    params = {
        "id": id,
        "Accept-Encoding": accept_encoding,
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def check_quota_status(client, args):
    ids = args.get("ids", "")
    url_suffix = f"/falconx/entities/submissions/v1?ids={ids}"

    params = {
        "ids": ids
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def find_sandbox_reports(client, args):
    filter = args.get("filter", "")
    offset = args.get("offset", "")
    limit = args.get("limit", "")
    sort = args.get("sort", "")
    url_suffix = f"/falconx/queries/reports/v1?filter={filter}&offset={offset}&limit{limit}=&sort={sort}"

    params = {
        "filter": filter,
        "offset": offset,
        "limit": limit,
        "sort": sort,
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def find_submission_id(client, args):
    filter = args.get("filter", "")
    offset = args.get("offset", "")
    limit = args.get("limit", "")
    sort = args.get("sort", "")
    url_suffix = f"/falconx/queries/submissions/v1?filter={filter}&offset={offset}&limit{limit}=&sort={sort}"

    params = {
        "filter": filter,
        "offset": offset,
        "limit": limit,
        "sort": sort,
    }
    headers = {
        'Authorization': 'Bearer ' + access_token,
    }

    response = client.http_request("GET", url_suffix, headers=headers, data=None, params=params)
    # demisto.log(response.text)
    return response


def main():
    # print("start")
    url = "https://api.crowdstrike.com/" # CONST?
    params = demisto.params()
    username = params.get('credentials').get('identifier')
    password = params.get('credentials').get('password')
    try:
        command = demisto.command()
        LOG(f'Command being called in FalconX Sandbox is: {command}')
        client = Client(server_url=url, username=username, password=password)
        commands: Dict[str, Callable[[Client, Dict[str, str]], Tuple[str, Dict[Any, Any], Dict[Any, Any]]]] = {
            'test-module': test_module,
            'cs-fx-upload-file': upload_file,
            'cs-fx-detonate-uploaded-file': send_uploaded_file_to_sendbox_analysis,
            'cs-fx-detonate-url': send_url_to_sandbox_analysis,
            'cs-fx-get-full-report': get_full_report,
            'cs-fx-get-report-summary': get_report_summary,
            'cs-fx-get-analysis-status': get_analysis_status,
            'cs-fx-download-ioc': download_ioc,
            'cs-fx-check-quota': check_quota_status,
            'cs-fx-find-reports': find_sandbox_reports,
            'cs-fx-find-submission-id': find_submission_id
        }
        if command in commands:
            return_outputs(*commands[command](client, demisto.args()))
        else:
            raise NotImplementedError(f'{command} is not an existing FalconX command')
    except Exception as err:
        return_error(str(err))


if __name__ in ['__main__', 'builtin', 'builtins']:
    main()