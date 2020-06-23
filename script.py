import os

# from pprint import pprint
from typing import Optional

import boto3  # type: ignore
import googleapiclient.discovery
from google.oauth2 import service_account  # type: ignore

client = boto3.client("ssm")


def get_ssm_env_var() -> Optional[str]:
    return os.environ.get("SSM_PARAMETER")


def get_credentials_file(SSM_PARAMETER: Optional[str]) -> str:
    content = client.get_parameter(Name=SSM_PARAMETER, WithDecryption=True)[
        "Parameter"
    ]["Value"]

    with open("credentials.json", "w") as outfile:
        outfile.write(content)
    return "credentials.json"


SCOPES = ["https://www.googleapis.com/auth/admin.directory.group.readonly"]

SERVICE_ACCOUNT_FILE = get_credentials_file(get_ssm_env_var())

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)


