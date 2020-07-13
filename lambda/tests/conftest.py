# VCR debugging
import json
import logging
from urllib.parse import urlparse, urlunparse

import vcr

logging.basicConfig()
vcr_log = logging.getLogger("vcr")
vcr_log.setLevel(logging.DEBUG)


def scrub_response(response):
    """Helper to scub secrets from a vcr request body"""
    try:
        data = json.loads(response["body"]["string"])
        response["body"]["string"] = json.dumps(
            scrub_json(data), separators=(",", ":")
        ).encode()
    except Exception:
        pass

    cl = ["Content-Length", "content-length"]
    for i in cl:
        if i in response["headers"]:
            response["headers"][i] = [str(len(response["body"]["string"]))]

    return response


# TODO: CLEAN ME
def scrub_request(request):
    """Helper to scub secrets from a vcr request body"""

    try:
        data = json.loads(request.body)
    except Exception:
        data = None

    if data:
        request.body = json.dumps(scrub_json(data), separators=(",", ":")).encode()

    url = urlparse(request.uri)

    if "nessus" in url.netloc:
        url = url._replace(netloc="localhost")
        request.uri = urlunparse(url)

    return request


# credentials = """
# {\"type\": \"service_account\",
#     \"project_id\": \"cyber-security-get-groups\",
#     \"private_key_id\": \"d067fe85d79bfbeb37517d8e0e0e8b9ac9bc254f\",
#     \"private_key\": \"-----BEGIN PRIVATE KEY----- -----END PRIVATE KEY-----\n\",
#     \"client_email\": \"some-email@cyber-security-get-groups.iam.gserviceaccount.com\",
#     \"client_id\": \"108642412837943356287\",
#     \"auth_uri\": \"https://accounts.google.com/o/oauth2/auth\",
#     \"token_uri\": \"https://oauth2.googleapis.com/token\",
#     \"auth_provider_x509_cert_url\": \"https://www.googleapis.com/oauth2/v1/certs\",
#     }
# """


def scrub_json(data):
    """Helper to remove secret values from JSON"""
    parameters = [
        ("/google_data_to_splunk/groups_scope", "https://www.test.groups.scope"),
        ("/google_data_to_splunk/subject_email", "subject_email@subjectemail.com"),
        # ("/google_data_to_splunk/credentials", credentials),
    ]
    if "Parameter" in data:
        data["Parameter"][
            "ARN"
        ] = "arn:aws:ssm:us-east-1:000000000000:parameter/test_param/"
        data["Parameter"]["LastModifiedDate"] = 0

        for parameter in parameters:
            if data["Parameter"]["Name"] == parameter[0]:
                data["Parameter"]["Value"] = (
                    parameter[1] if len(parameter) > 1 else parameter[0]
                )

    secrets = [
        ("groups_scope", "https://www.test.groups.scope"),
    ]

    for secret in secrets:
        if secret[0] in data:
            data[secret[0]] = secret[1]

    return data


# Standardise vcr config
vcr.default_vcr = vcr.VCR(
    record_mode="once",
    match_on=["uri", "method", "body"],
    cassette_library_dir="tests/fixtures/cassettes",
    path_transformer=vcr.VCR.ensure_suffix(".yaml"),
    filter_headers=[
        "Authorization",
        "X-Amz-Security-Token",
        "X-Amz-Date",
        "X-Amz-Target",
        "X-ApiKeys",
        "X-API-Token",
        "X-Cookie",
    ],
    decode_compressed_response=True,
    before_record_response=scrub_response,
    before_record_request=scrub_request,
)
vcr.use_cassette = vcr.default_vcr.use_cassette
