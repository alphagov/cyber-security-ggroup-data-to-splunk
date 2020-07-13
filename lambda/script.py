import json
import os
from typing import Dict, List, Optional

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore

client = boto3.client("ssm")


def get_scope(scope: Optional[str]) -> List[str]:
    """
    Returns the scope from AWS SSM.
    """
    return [client.get_parameter(Name=scope, WithDecryption=True)["Parameter"]["Value"]]


def get_subject_email(subject: Optional[str]) -> str:
    """
    Returns the subject email from AWS SSM.
    """
    return client.get_parameter(Name=subject, WithDecryption=True)["Parameter"]["Value"]


def get_credentials_file(credentials: Optional[str]) -> str:
    """
    Gets the credentials file from AWS SSM and writes it to the local file
    /tmp/credentials.json Returns the file location for the credentials file.
    """
    content = client.get_parameter(Name=credentials, WithDecryption=True)["Parameter"][
        "Value"
    ]

    with open("/tmp/credentials.json", "w") as outfile:
        outfile.write(content)
    return "/tmp/credentials.json"


def create_response(
    api: str,
    api_version: str,
    service_account_file: str,
    scope: List[str],
    subject: str,
    pageToken: str = None,
):
    """
    Returns a given client built from a google api and api version passed in .
    """
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scope, subject=subject,
    )

    client = googleapiclient.discovery.build(
        api, api_version, credentials=credentials, cache_discovery=False
    )

    return client


def build_group_dict(api: str, api_version: str, scope: str) -> Dict[str, str]:
    """
    Returns a dictionary of google groups names and their ID.
    """
    response = create_response(
        api,
        api_version,
        get_credentials_file(os.environ.get("CREDENTIALS")),
        get_scope(os.environ.get(scope)),
        get_subject_email(os.environ.get("SUBJECT")),
    )
    group_ids = {}
    nextPageToken = None

    while True:
        groups = (
            response.groups()
            .list(
                pageToken=nextPageToken,
                domain="digital.cabinet-office.gov.uk",
                maxResults=200,
            )
            .execute()
        )
        if groups:
            for g in groups["groups"]:
                group_names = g["name"]
                group_id = g["email"]
                group_ids[group_names] = group_id

            if "nextPageToken" not in groups:
                break

    return group_ids


def get_group_info(
    api: str, api_version: str, scope: str, group_ids: Dict[str, str]
) -> List[Dict[str, str]]:
    """
    Returns a List of dicts containing each groups metadata.
    """
    response = create_response(
        api,
        api_version,
        get_credentials_file(os.environ.get("CREDENTIALS")),
        get_scope(os.environ.get(scope)),
        get_subject_email(os.environ.get("SUBJECT")),
    )

    return [
        response.groups().get(groupUniqueId=group_id).execute()
        for _, group_id in group_ids.items()
    ]


def print_group_info(
    group_api_name: str,
    group_api_version: str,
    group_scope: str,
    admin_api_name: str,
    admin_api_version: str,
    admin_scope: str,
) -> None:
    """
    Prints each group's information so that it can be picked up by Cloudwatch Logs
    """
    for group in get_group_info(
        group_api_name,
        group_api_version,
        group_scope,
        build_group_dict(admin_api_name, admin_api_version, admin_scope),
    ):
        print(json.dumps(group))


def main(event, context):
    print_group_info(
        "groupssettings", "v1", "GROUPS_SCOPE", "admin", "directory_v1", "ADMIN_SCOPE"
    )
