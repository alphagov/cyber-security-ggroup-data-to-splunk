# cyber-security-ggroup-data-to-splunk
This repo holds the infrastructure for a Lambda which exports Google groups metadata to Splunk.

## How to Find the Data
The Lambda sends the Google groups data to splunk, find it with the following search term:
`index="cyber_services_prod" sourcetype="aws:lambda:send_ggroup_data_to_splunk"`

## Prerequisites

Before working on this repo for the first time, you will need to run pipenv and create an environment for this repo:

```
pip install pipenv
cd cyber-security-ggroup-data-to-splunk/lambda
pipenv install --dev
pipenv shell

```

## Running tests

Tests are run from the root of the repository by running:
 
`make tests`

This command will run terraform format, terraform validate, flake8 and the unit tests.

## Contract Tests

Contract tests are run on the project's concourse pipeline to check that the Google API is working as we expect it to work. 
These are run at 10am every weekday, and will alert to #cyber-security-service-health in the event that they fail.

## How to deploy

Merges to master in this repo will trigger a deploy in [Concourse](https://cd.gds-reliability.engineering/teams/cybersecurity-tools/pipelines/ggroups-to-splunk)