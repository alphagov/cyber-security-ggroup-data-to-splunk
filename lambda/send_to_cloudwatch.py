from datetime import datetime
from functools import lru_cache

import boto3  # type: ignore


def debug(text):
    print(text)


def process_groups_data(groups_data):
    """
    Send the group data one at a time to cloud watch. This will create a
    new event for each group in Splunk.
    """
    group_name = "/gds/google-group-data"
    stream_name = f"{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}-google-group-data"
    debug("create log stream")
    token = create_log_stream(group_name, stream_name)

    for group in groups_data:
        logs_client().put_log_events(
            logGroupName=group_name,
            logStreamName=stream_name,
            logEvents=group,
            sequenceToken=token,
        )


@lru_cache(maxsize=None)
def logs_client():
    return boto3.client("logs")


def create_log_stream(group_name, stream_name):

    try:
        logs_client().create_log_stream(
            logGroupName=group_name, logStreamName=stream_name
        )
    except logs_client().exceptions.ResourceAlreadyExistsException:
        pass

    response = logs_client().describe_log_streams(
        logGroupName=group_name, logStreamNamePrefix=stream_name,
    )

    if "uploadSequenceToken" in response["logStreams"][0]:
        token = response["logStreams"][0]["uploadSequenceToken"]
    else:
        token = "0"

    return token
