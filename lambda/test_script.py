from unittest.mock import Mock, patch
import filecmp

from script import *

@patch('script.ssm_client.get_parameter')
def test_get_scope(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": "test_scope_value"}}
    expected = ["test_scope_value"]
    actual = get_scope("test_scope")
    assert expected == actual

@patch('script.ssm_client.get_parameter')
def test_get_subject_email(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": "test_subject_email"}}
    expected = "test_subject_email"
    actual = get_subject_email("test_email_param")
    assert expected == actual

@patch('script.ssm_client.get_parameter')
def test_get_credentials_file(mock_get_ssm):
    mock_get_ssm.return_value = {"Parameter": {"Value": '{"test_creds": true}'}}
    expected_credentials_file = "./test_assetts/expected_credentials_file.json"
    actual_credentials_file = get_credentials_file("test_credentials_param", "./test_assetts/actual_credentials_file.json")

    assert filecmp.cmp(actual_credentials_file, expected_credentials_file)

    #clear test file
    open(actual_credentials_file, 'w').close()