import json
import os
import time
from typing import Any, Dict, List, Optional, Tuple

import boto3  # type: ignore
import googleapiclient.discovery  # type: ignore
from google.oauth2 import service_account  # type: ignore
from googleapiclient.errors import HttpError  # type: ignore

ssm_client = boto3.client("ssm")
lambda_client = boto3.client("lambda")


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


def build_group_dict(
    api: str, api_version: str, scope: str, nextPageToken: Optional[str],
) -> Tuple[Dict[str, str], Optional[str]]:
    """
    Returns two objects:
    - a dictionary of google groups names and their ID
    - a payload for an invocation of this lambda (either None or a JSON encoded string)
    """
    google_client = create_google_client(
        api,
        api_version,
        get_credentials_file(os.environ["CREDENTIALS"]),
        scope,
        get_subject_email(os.environ["SUBJECT"]),
    )
    group_ids = {}
    lambda_payload = None

    try:
        groups = (
            google_client.groups()
            .list(pageToken=nextPageToken, domain=os.environ["DOMAIN"], maxResults=200,)
            .execute()
        )
        if groups:
            for g in groups["groups"]:
                group_names = g["name"]
                group_id = g["email"]
                group_ids[group_names] = group_id

            if "nextPageToken" in groups:
                lambda_payload = json.dumps({"nextPageToken": groups["nextPageToken"]})

    except HttpError as e:
        print(f"Http error getting group ids: {e}")

    return group_ids, lambda_payload


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
                google_client.groups()
                .get(groupUniqueId=group_id)
                .execute(num_retries=8)  # This is supposed to be an exponential retry
            )
        except HttpError as e:
            print(f"Http error for group {group_id}: {e}")
            if "exceeded" in f"{e}".lower():
                if "Queries per day" in f"{e}":
                    print("Queries per day limit exceeded")
                    break
                if "Queries per minute" in f"{e}":
                    print("Queries per minute limit exceeded")
                    # time.sleep(61)

    return group_list


def print_group_info(
    group_api_name: str,
    group_api_version: str,
    group_scope: str,
    admin_api_name: str,
    admin_api_version: str,
    admin_scope: str,
    nextPageToken: Optional[str],
) -> Optional[str]:
    """
    Prints each group's information so that it can be picked up by Cloudwatch Logs, and
    returns the lambda_payload for future invocations of the lambda
    """
    group_ids, lambda_payload = build_group_dict(
        admin_api_name, admin_api_version, admin_scope, nextPageToken,
    )
    group_list = get_group_info(
        group_api_name, group_api_version, group_scope, group_ids
    )
    for group in group_list:
        print(json.dumps(group))

    return lambda_payload


def main(event: Dict, context: Any):
    groups_scope = "https://www.googleapis.com/auth/apps.groups.settings"
    admin_scope = "https://www.googleapis.com/auth/admin.directory.group.readonly"
    nextPageToken = event.get("nextPageToken", None)
    lambda_function_name: str = context.function_name

    lambda_payload = print_group_info(
        "groupssettings",
        "v1",
        groups_scope,
        "admin",
        "directory_v1",
        admin_scope,
        nextPageToken,
    )

    lambda_client.invoke(
        FunctionName=lambda_function_name,
        InvocationType="Event",
        Payload=lambda_payload,
    )
