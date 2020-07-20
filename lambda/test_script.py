from unittest.mock import Mock, patch
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
