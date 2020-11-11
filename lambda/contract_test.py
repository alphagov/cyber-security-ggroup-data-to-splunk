from script import (
    create_google_client,
    get_credentials_file,
    get_scope,
    get_subject_email,
)

admin_google_client = create_google_client(
    "admin",
    "directory_v1",
    get_credentials_file("/google_data_to_splunk/credentials"),
    get_scope("/google_data_to_splunk/admin_readonly_scope"),
    get_subject_email("/google_data_to_splunk/subject_email"),
)

groups_google_client = create_google_client(
    "groupssettings",
    "v1",
    get_credentials_file("/google_data_to_splunk/credentials"),
    get_scope("/google_data_to_splunk/groups_scope"),
    get_subject_email("/google_data_to_splunk/subject_email"),
)


def test_google_admin_api():
    """
    Tests that the google admin api returns something in the format we need
    (ie has name and email)
    """
    groups = (
        admin_google_client.groups()
        .list(pageToken=None, domain="digital.cabinet-office.gov.uk", maxResults=1)
        .execute()
    )
    assert groups["groups"][0]["name"] and groups["groups"][0]["email"]


def test_google_groups_api():
    """
    Tests that the group admin returns a non empty dictionary
    """
    group_id = (
        admin_google_client.groups()
        .list(pageToken=None, domain="digital.cabinet-office.gov.uk", maxResults=1)
        .execute()["groups"][0]["email"]
    )
    groups = groups_google_client.groups().get(groupUniqueId=group_id).execute()
    assert groups
    assert groups["email"]
