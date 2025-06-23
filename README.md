# Udsendelse af Velkomstbrev til internationale tilflyttere

This RPA extract a list of people who moved to the city of Aarhus within the last months and send them a letter of welcome through Digital Post.

## Quick start

Deploy on Open Orchestrator.

## Process

- Get list of people who moved to the city within the last month from SQL
- Check if how many days have passed since their last move within the city
- Either send a letter or save encrypted ID in Orchestrator Queue

## Known errors

- Serviceplatformen may do a timeout when checking if a person is registered with Digital Post, but the robot will catch it next time.

## Requirements

Minimum python version 3.10

## Linting and Github Actions

This template is also setup with flake8 and pylint linting in Github Actions.
This workflow will trigger whenever you push your code to Github.
The workflow is defined under `.github/workflows/Linting.yml`.

