import json
import os
from pprint import pprint
from typing import Optional

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore

client = boto3.client("ssm")


def get_ssm_env_var() -> Optional[str]:
    return os.environ.get("CREDENTIALS")


def get_subject_env_var() -> Optional[str]:
    return os.environ.get("SUBJECT")


def get_subject_email(SUBJECT: Optional[str]) -> str:
    return client.get_parameter(Name=SUBJECT, WithDecryption=True)["Parameter"]["Value"]


def get_credentials_file(CREDENTIALS: Optional[str]) -> str:
    content = client.get_parameter(Name=CREDENTIALS, WithDecryption=True)["Parameter"][
        "Value"
    ]

    with open("credentials.json", "w") as outfile:
        outfile.write(content)
    return "credentials.json"


SCOPES = ["https://www.googleapis.com/auth/admin.directory.group.readonly"]

SERVICE_ACCOUNT_FILE = get_credentials_file(get_ssm_env_var())
SUBJECT = get_subject_email(get_subject_env_var())

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=SUBJECT,
)

client = googleapiclient.discovery.build(
    "admin", "directory_v1", credentials=credentials
)

response = (
    client.groups()
    .list(domain="digital.cabinet-office.gov.uk", maxResults=200)
    .execute()
)

pprint(response)
# for r in response:
#     page_token = r["nextPageToken"]
