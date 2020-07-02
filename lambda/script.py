import json
import os
from typing import Dict, List, Optional

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore


def get_env_var(env) -> Optional[str]:
    return os.environ.get(env)


def get_scope(scope: Optional[str]) -> List[str]:
    client = boto3.client("ssm")
    return [client.get_parameter(Name=scope, WithDecryption=True)["Parameter"]["Value"]]


def get_subject_email(subject: Optional[str]) -> str:
    client = boto3.client("ssm")
    return client.get_parameter(Name=subject, WithDecryption=True)["Parameter"]["Value"]


def get_credentials_file(credentials: Optional[str]) -> str:
    client = boto3.client("ssm")
    content = client.get_parameter(Name=credentials, WithDecryption=True)["Parameter"][
        "Value"
    ]

    with open("/tmp/credentials.json", "w") as outfile:
        outfile.write(content)
    return "/tmp/credentials.json"


def create_admin_client(
    service_account_file: str, scope: List[str], subject: str, pageToken: str = None
):
    client = boto3.client("ssm")
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scope, subject=subject,
    )
    # https://googleapis.github.io/google-api-python-client/docs/epy/googleapiclient.discovery-pysrc.html#build
    client = googleapiclient.discovery.build(
        "admin", "directory_v1", credentials=credentials, cache_discovery=False
    )

    return client


def create_groups_client(
    service_account_file: str, scope: List[str], subject: str, pageToken: str = None
):
    client = boto3.client("ssm")
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scope, subject=subject,
    )

    client = googleapiclient.discovery.build(
        "groupssettings", "v1", credentials=credentials, cache_discovery=False
    )

    return client


def build_group_dict() -> Dict[str, str]:
    response = create_admin_client(
        get_credentials_file(get_env_var("CREDENTIALS")),
        get_scope(get_env_var("ADMIN_SCOPE")),
        get_subject_email(get_env_var("SUBJECT")),
    )
    group_ids = {}
    hasNextPageToken = True
    nextPageToken = None

    while hasNextPageToken:

        groups = (
            response.groups()
            .list(
                pageToken=nextPageToken,
                domain="digital.cabinet-office.gov.uk",
                maxResults=200,
            )
            .execute()
        )
        hasNextPageToken = False
        if "nextPageToken" in groups:
            nextPageToken = groups["nextPageToken"]
            hasNextPageToken = True

        if groups:
            if "nextPageToken" in groups:
                for g in groups["groups"]:
                    group_names = g["name"]
                    group_id = g["email"]
                    group_ids[group_names] = group_id
    return group_ids


def get_group_info(group_ids: Dict[str, str]) -> List[Dict[str, str]]:
    response = create_groups_client(
        get_credentials_file(get_env_var("CREDENTIALS")),
        get_scope(get_env_var("GROUPS_SCOPE")),
        get_subject_email(get_env_var("SUBJECT")),
    )

    return [
        response.groups().get(groupUniqueId=value).execute()
        for key, value in group_ids.items()
    ]


def print_group_info() -> None:
    for group in get_group_info(build_group_dict()):
        print(json.dumps(group))


def main(event, context):
    print_group_info()
