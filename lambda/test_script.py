import filecmp
import io
import json
import os
import sys
from unittest.mock import patch

from script import (
    build_group_dict,
    get_credentials_file,
    get_group_info,
    get_subject_email,
    print_group_info,
)


@patch("script.ssm_client.get_parameter")
def test_get_subject_email(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": "test_subject_email"}}
    expected = "test_subject_email"
    actual = get_subject_email("test_email_param")
    assert actual == expected


@patch("script.ssm_client.get_parameter")
def test_get_credentials_file(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": '{"test_creds": true}'}}
    expected_credentials_file = "./lambda/test_assetts/expected_credentials_file.json"
    actual_credentials_file = get_credentials_file(
        "test_credentials_param", "./lambda/test_assetts/actual_credentials_file.json"
    )
    assert (
        actual_credentials_file == "./lambda/test_assetts/actual_credentials_file.json"
    )
    assert filecmp.cmp(actual_credentials_file, expected_credentials_file)

    # clear test file
    open(actual_credentials_file, "w").close()


@patch("script.get_subject_email")
@patch("script.get_credentials_file")
@patch("script.create_google_client")
def test_build_group_dict(
    mock_create_google_client, mock_get_credentials_file, mock_get_subject_email,
):
    class GoogleClientMockClass:
        def groups():
            class GoogleClientList:
                def list(pageToken, domain, maxResults):
                    class GoogleClientExecute:
                        def execute():
                            first_set = {
                                "groups": [
                                    {"name": "group1", "email": "group1@email.com"},
                                    {"name": "group2", "email": "group2@email.com"},
                                ],
                                "nextPageToken": "first_next_page_token",
                            }
                            second_set = {
                                "groups": [
                                    {"name": "group3", "email": "group3@email.com"},
                                    {"name": "group4", "email": "group4@email.com"},
                                ],
                                "nextPageToken": "last_next_page_token",
                            }
                            last_set = {
                                "groups": [
                                    {"name": "group5", "email": "group5@email.com"}
                                ]
                            }
                            if pageToken == "last_next_page_token":
                                return last_set
                            elif pageToken == "first_next_page_token":
                                return second_set
                            else:
                                return first_set

                    return GoogleClientExecute

            return GoogleClientList

    mock_create_google_client.return_value = GoogleClientMockClass
    mock_get_credentials_file.return_value = (
        "./lambda/test_assetts/expected_credentials_file.json"
    )
    mock_get_subject_email.return_value = {"Parameter": {"Value": "test_subject_email"}}

    os.environ["CREDENTIALS"] = "credentials_param"
    os.environ["SUBJECT"] = "subject_email_param"
    os.environ["DOMAIN"] = "digital.cabinet-office.gov.uk"

    actual = build_group_dict("http://api.com", "v3", "test_groups_scope")
    expected = {
        "group1": "group1@email.com",
        "group2": "group2@email.com",
        "group3": "group3@email.com",
        "group4": "group4@email.com",
        "group5": "group5@email.com",
    }

    assert actual == expected


@patch("script.get_subject_email")
@patch("script.get_credentials_file")
@patch("script.create_google_client")
def test_get_group_info(
    mock_create_google_client, mock_get_credentials_file, mock_get_subject_email,
):
    class GoogleClientMockClass:
        def groups():
            class GoogleClientGet:
                def get(groupUniqueId):
                    class GoogleClientExecute:
                        def execute():
                            groups = {
                                "group1@email.com": {
                                    "kind": "admin#directory#group",
                                    "id": "id1",
                                    "etag": "etag",
                                    "email": "group1@email.com",
                                    "name": "team1",
                                    "directMembersCount": "0",
                                    "description": "a description here",
                                    "adminCreated": False,
                                },
                                "group2@email.com": {
                                    "kind": "admin#directory#group",
                                    "id": "id2",
                                    "etag": "etag",
                                    "email": "group2@email.com",
                                    "name": "group2",
                                    "directMembersCount": "3",
                                    "description": "",
                                    "adminCreated": False,
                                },
                            }
                            return groups[groupUniqueId]

                    return GoogleClientExecute

            return GoogleClientGet

    mock_create_google_client.return_value = GoogleClientMockClass
    mock_get_credentials_file.return_value = (
        "./lambda/test_assetts/expected_credentials_file.json"
    )
    mock_get_subject_email.return_value = {"Parameter": {"Value": "test_subject_email"}}

    os.environ["CREDENTIALS"] = "credentials_param"
    os.environ["SUBJECT"] = "subject_email_param"
    os.environ["DOMAIN"] = "digital.cabinet-office.gov.uk"

    group_dict = {"group1": "group1@email.com", "group2": "group2@email.com"}

    actual = get_group_info("http:api.com", "v3", "test_groups_scope", group_dict)
    expected = [
        {
            "kind": "admin#directory#group",
            "id": "id1",
            "etag": "etag",
            "email": "group1@email.com",
            "name": "team1",
            "directMembersCount": "0",
            "description": "a description here",
            "adminCreated": False,
        },
        {
            "kind": "admin#directory#group",
            "id": "id2",
            "etag": "etag",
            "email": "group2@email.com",
            "name": "group2",
            "directMembersCount": "3",
            "description": "",
            "adminCreated": False,
        },
    ]
    assert expected == actual


@patch("script.get_group_info")
@patch("script.build_group_dict")
def test_print_group_info(mock_build_group_dict, mock_get_group_info):
    mock_build_group_dict.return_value = {
        "group1": "group1@email.com",
        "group2": "group2@email.com",
    }
    mock_get_group_info.return_value = [
        {
            "kind": "admin#directory#group",
            "id": "id1",
            "etag": "etag",
            "email": "group1@email.com",
            "name": "team1",
            "directMembersCount": "0",
            "description": "a description here",
            "adminCreated": False,
        },
        {
            "kind": "admin#directory#group",
            "id": "id2",
            "etag": "etag",
            "email": "group2@email.com",
            "name": "group2",
            "directMembersCount": "3",
            "description": "",
            "adminCreated": False,
        },
    ]

    capturedOutput = io.StringIO()
    sys.stdout = capturedOutput
    print_group_info(
        "http://api.com", "v3", "scope", "http://adminapi.com", "v3", "admin scope"
    )
    sys.stdout = sys.__stdout__
    actual = capturedOutput.getvalue()
    expected = (
        json.dumps(mock_get_group_info.return_value[0])
        + "\n"
        + json.dumps(mock_get_group_info.return_value[1])
        + "\n"
    )
    assert actual == expected
