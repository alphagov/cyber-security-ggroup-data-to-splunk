import os
from pprint import pprint
from typing import List, Optional

import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore

import boto3  # type: ignore
from send_to_cloudwatch import process_groups_data


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

    with open("/tmp/credentials.json", "w") as outfile:
        outfile.write(content)
    return "/tmp/credentials.json"


def create_admin_client(
    SERVICE_ACCOUNT_FILE: str, scope: List[str], subject: str, pageToken: str = None
) -> str:
    client = boto3.client("ssm")
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope, subject=subject,
    )

    client = googleapiclient.discovery.build(
        "admin", "directory_v1", credentials=credentials, cache_discovery=False
    )

    return client


def create_groups_client(
    SERVICE_ACCOUNT_FILE: str, scope: List[str], subject: str, pageToken: str = None
) -> str:
    client = boto3.client("ssm")
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope, subject=subject,
    )

    client = googleapiclient.discovery.build(
        "groupssettings", "v1", credentials=credentials, cache_discovery=False
    )

    return client


def build_group_dict():
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
                    hasNextPageToken = False
    return group_ids


def get_group_info(group_ids):
    response = create_groups_client(
        get_credentials_file(get_env_var("CREDENTIALS")),
        get_scope(get_env_var("GROUPS_SCOPE")),
        get_subject_email(get_env_var("SUBJECT")),
    )
    group_settings = {}

    for key, value in group_ids.items():
        group_key = key
        group_value = response.groups().get(groupUniqueId=value).execute()
        group_settings[group_key] = group_value
        return group_settings


def main(event, context):
    print(get_group_info(build_group_dict()))