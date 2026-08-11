# Udsendelse af Velkomstbrev til internationale tilflyttere

This RPA extract a list of people who moved to the city of Aarhus within the last months and send them a letter of welcome through Digital Post.

## Quick start

Deploy on Open Orchestrator.

## Process

- Get list of people from SQL who arrived in the city from outside Denmark, and have been here long
  enough for their letter to be due. Later moves within the city don't affect this.
- Skip anyone who already has a letter registered in the Orchestrator Queue, or who isn't registered
  for Digital Post.
- Send the letter and save the encrypted ID in the Orchestrator Queue so it isn't sent again.

Queue elements only exist to avoid sending a letter twice, and can be deleted once they are older
than `MAX_DAYS_SINCE_ARRIVAL`, since the query will never return that person again.

## Known errors

- Serviceplatformen may do a timeout when checking if a person is registered with Digital Post, but the robot will catch it next time.

## Requirements

Minimum python version 3.10

## Linting and Github Actions

This template is also setup with flake8 and pylint linting in Github Actions.
This workflow will trigger whenever you push your code to Github.
The workflow is defined under `.github/workflows/Linting.yml`.
