"""This module contains the main process of the robot."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from python_serviceplatformen.authentication import KombitAccess
from python_serviceplatformen import digital_post

from robot_framework.custom import mail_merge, sql_data, keyvault, digital_post_composer
from robot_framework import config


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    # Get tokens
    vault_auth = orchestrator_connection.get_credential(config.KEYVAULT_CREDENTIALS)
    vault_uri = orchestrator_connection.get_constant(config.KEYVAULT_URI).value
    certificate = keyvault.get_certificate(vault_username=vault_auth.username, vault_password=vault_auth.password, vault_uri=vault_uri, vault_path=config.KEYVAULT_PATH)
    kombit_access = KombitAccess(cvr=config.CVR, cert_path=certificate)

    # Get data from SQL
    query = sql_data.sql_query("2006-10-02")
    data = sql_data.read_data(query)
    data_dict = sql_data.sql_to_dict(data)

    # Save files from data
    files = mail_merge.data_to_template(data_dict)

    # Send files to people
    for cpr, filename in files.items():
        # Send a letter to cpr through the thing
        m = digital_post_composer.compose_message("Welcome to Aarhus", config.CVR, cpr, filename)
        digital_post.send_message("Digital Post", m, kombit_access)
