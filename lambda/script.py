import json
import os
from typing import Dict, List

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore

ssm_client = boto3.client("ssm", region="eu-west-2")


def get_scope(scope: str) -> List[str]:
    """
    Returns the scope from AWS SSM.
    """
    return [
        ssm_client.get_parameter(Name=scope, WithDecryption=True)["Parameter"]["Value"]
    ]


def get_subject_email(subject: str) -> str:
    """
    Returns the subject email from AWS SSM.
    """
    return ssm_client.get_parameter(Name=subject, WithDecryption=True)["Parameter"][
        "Value"
    ]


def get_credentials_file(
    credentials: str, cred_file_location: str = "/tmp/credentials.json"
) -> str:
    """
    Gets the credentials file from AWS SSM and writes it to the local file
    /tmp/credentials.json Returns the file location for the credentials file.
    """
    content = ssm_client.get_parameter(Name=credentials, WithDecryption=True)[
        "Parameter"
    ]["Value"]

    with open(cred_file_location, "w") as outfile:
        outfile.write(content)
    return cred_file_location


def create_google_client(
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

    google_client = googleapiclient.discovery.build(
        api, api_version, credentials=credentials, cache_discovery=False
    )

    return google_client


def build_group_dict(api: str, api_version: str, scope: str) -> Dict[str, str]:
    """
    Returns a dictionary of google groups names and their ID.
    """
    google_client = create_google_client(
        api,
        api_version,
        get_credentials_file(os.environ["CREDENTIALS"]),
        get_scope(os.environ[scope]),
        get_subject_email(os.environ["SUBJECT"]),
    )
    group_ids = {}
    nextPageToken = None

    while True:
        groups = (
            google_client.groups()
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
            else:
                nextPageToken = groups["nextPageToken"]

    return group_ids


def get_group_info(
    api: str, api_version: str, scope: str, group_ids: Dict[str, str]
) -> List[Dict[str, str]]:
    """
    Returns a List of dicts containing each groups metadata.
    """
    google_client = create_google_client(
        api,
        api_version,
        get_credentials_file(os.environ["CREDENTIALS"]),
        get_scope(os.environ[scope]),
        get_subject_email(os.environ["SUBJECT"]),
    )

    return [
        google_client.groups().get(groupUniqueId=group_id).execute()
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


def main(event: Dict, context: Dict):
    print_group_info(
        "groupssettings", "v1", "GROUPS_SCOPE", "admin", "directory_v1", "ADMIN_SCOPE"
    )
