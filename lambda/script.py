import json
import os
from typing import Dict, List

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

ssm_client = boto3.client("ssm")


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
    scope: str,
    subject: str,
    pageToken: str = None,
):
    """
    Returns a given client built from a google api and api version passed in .
    """
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=[scope], subject=subject,
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
        scope,
        get_subject_email(os.environ["SUBJECT"]),
    )
    group_ids = {}
    nextPageToken = None

    while True:
        try:
            groups = (
                google_client.groups()
                .list(
                    pageToken=nextPageToken,
                    domain=os.environ["DOMAIN"],
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

        except HttpError as e:
            print(f"Http error getting group ids: {e}")

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
        scope,
        get_subject_email(os.environ["SUBJECT"]),
    )

    group_list = []
    for _, group_id in group_ids.items():
        try:
            group_list.append(
                google_client.groups().get(groupUniqueId=group_id).execute()
            )
        except HttpError as e:
            print(f"Http error for group {group_id}: {e}")
            if "exceeded" in f"{e}".lower():
                print("Rate limit exceeded, stopping loop over groups...")
                break

    return group_list


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
    groups_scope = "https://www.googleapis.com/auth/apps.groups.settings"
    admin_scope = "https://www.googleapis.com/auth/admin.directory.group.readonly"

    print_group_info(
        "groupssettings", "v1", groups_scope, "admin", "directory_v1", admin_scope
    )
