"""This module contains the main process of the robot."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from robot_framework.custom import mail_merge, sql_data


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    # Get data from SQL
    query = sql_data.sql_query("2006-10-02")
    data = sql_data.read_data(query)
    data_dict = sql_data.sql_to_dict(data)

    # Save files from data
    files = mail_merge.data_to_template(data_dict)

    # Send files to people
    for cpr, filename in files.items():
        # Send a letter to cpr through the thing
        print("sending a letter")
