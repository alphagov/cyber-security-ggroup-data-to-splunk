# cyber-security-ggroup-data-to-splunk
This repo holds the infrastrcutre for a Lambda which exports Google groups metadata to Splunk.
TODO:which index will the data come through?
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

## How to deploy

 TODO