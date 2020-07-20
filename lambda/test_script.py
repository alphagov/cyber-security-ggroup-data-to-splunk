from unittest.mock import Mock, patch
import filecmp

from script import *


@patch("script.ssm_client.get_parameter")
def test_get_scope(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": "test_scope_value"}}
    expected = ["test_scope_value"]
    actual = get_scope("test_scope")
    assert expected == actual


@patch("script.ssm_client.get_parameter")
def test_get_subject_email(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": "test_subject_email"}}
    expected = "test_subject_email"
    actual = get_subject_email("test_email_param")
    assert expected == actual


@patch("script.ssm_client.get_parameter")
def test_get_credentials_file(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": '{"test_creds": true}'}}
    expected_credentials_file = "./test_assetts/expected_credentials_file.json"
    actual_credentials_file = get_credentials_file(
        "test_credentials_param", "./test_assetts/actual_credentials_file.json"
    )
    assert actual_credentials_file == "./test_assetts/actual_credentials_file.json"
    assert filecmp.cmp(actual_credentials_file, expected_credentials_file)

    # clear test file
    open(actual_credentials_file, "w").close()


@patch("script.get_subject_email")
@patch("script.get_scope")
@patch("script.get_credentials_file")
@patch("script.create_google_client")
def test_build_group_dict(
    mock_create_google_client,
    mock_get_credentials_file,
    mock_get_scope,
    mock_get_subject_email,
):
    class GoogleClientMockClass:
        def groups():
            class GoogleClientList:
                def list(pageToken, domain, maxResults):
                    class GoogleClientExecute:
                        def execute():
                            first_set = {
                                "groups": [
                                    {
                                        "name": "group1",
                                        "email": "group1@email.com",
                                        "members": 0,
                                    },
                                    {
                                        "name": "group2",
                                        "email": "group2@email.com",
                                        "members": 3,
                                    },
                                ], 
                                "nextPageToken": "first_next_page_token"
                            }
                            second_set =  {
                                "groups": [
                                    {
                                        "name": "group3",
                                        "email": "group3@email.com",
                                        "members": 0,
                                    },
                                    {
                                        "name": "group4",
                                        "email": "group4@email.com",
                                        "members": 3,
                                    },
                                ],
                                "nextPageToken": "last_next_page_token"
                            }
                            last_set = {
                                "groups": [
                                    {
                                        "name": "group5",
                                        "email": "group5@email.com",
                                        "members": 0,
                                    }
                                ]
                            }
                            if pageToken=="last_next_page_token":
                                return last_set
                            elif pageToken=="first_next_page_token":
                                return second_set
                            else:
                                return first_set
                    
                    return GoogleClientExecute

            return GoogleClientList

    mock_create_google_client.return_value = GoogleClientMockClass
    mock_get_credentials_file.return_value = (
        "./test_assetts/expected_credentials_file.json"
    )
    mock_get_scope.return_value = {"Parameter": {"Value": "test_scope_value"}}
    mock_get_subject_email.return_value = {"Parameter": {"Value": "test_subject_email"}}

    os.environ["CREDENTIALS"] = "credentials_param"
    os.environ["SUBJECT"] = "subject_email_param"
    os.environ["test_groups_scope"] = "test_groups_scope"

    actual = build_group_dict("http://api.com", "v3", "test_groups_scope")
    assert actual == {"group1": "group1@email.com", "group2": "group2@email.com", "group3": "group3@email.com", "group4": "group4@email.com", "group5": "group5@email.com"}
