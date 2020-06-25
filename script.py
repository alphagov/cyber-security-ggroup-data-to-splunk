import os
from pprint import pprint
from typing import List, Optional

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore


def get_env_var(env) -> Optional[str]:
    return os.environ.get(env)


def get_scope(SCOPE: Optional[str]) -> List[str]:
    client = boto3.client("ssm")
    return [client.get_parameter(Name=SCOPE, WithDecryption=True)["Parameter"]["Value"]]


def get_subject_email(SUBJECT: Optional[str]) -> str:
    client = boto3.client("ssm")
    return client.get_parameter(Name=SUBJECT, WithDecryption=True)["Parameter"]["Value"]


def get_credentials_file(CREDENTIALS: Optional[str]) -> str:
    client = boto3.client("ssm")
    content = client.get_parameter(Name=CREDENTIALS, WithDecryption=True)["Parameter"][
        "Value"
    ]

    with open("credentials.json", "w") as outfile:
        outfile.write(content)
    return "credentials.json"


def get_groups(SERVICE_ACCOUNT_FILE: str, scope: List[str], subject: str) -> str:
    client = boto3.client("ssm")
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope, subject=subject,
    )

    client = googleapiclient.discovery.build(
        "admin", "directory_v1", credentials=credentials
    )

    response = (
        client.groups()
        .list(domain="digital.cabinet-office.gov.uk", maxResults=10)
        .execute()
    )

    return response


def build_group_dict():
    response = get_groups(
        get_credentials_file(get_env_var("CREDENTIALS")),
        get_scope(get_env_var("SCOPES")),
        get_subject_email(get_env_var("SUBJECT")),
    )

    group_ids = {}

    for r in response["groups"]:
        group_names = r["name"]
        group_id = r["id"]
        group_ids[group_names] = group_id
    return group_ids


pprint(build_group_dict())
