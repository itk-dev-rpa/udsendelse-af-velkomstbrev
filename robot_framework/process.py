"""This module contains the main process of the robot."""
import hashlib
import os
from datetime import datetime, timedelta

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection, QueueStatus
from python_serviceplatformen.authentication import KombitAccess
from python_serviceplatformen import digital_post

from robot_framework.custom import sql_data, keyvault, digital_post_composer
from robot_framework import config


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    # Get tokens
    vault_auth = orchestrator_connection.get_credential(config.KEYVAULT_CREDENTIALS)
    vault_uri = orchestrator_connection.get_constant(config.KEYVAULT_URI).value
    certificate = keyvault.get_certificate(vault_username=vault_auth.username, vault_password=vault_auth.password, vault_uri=vault_uri, vault_path=config.KEYVAULT_PATH)
    kombit_access = KombitAccess(cvr=config.CVR, cert_path=certificate)

    # Get list of sent letters
    completed_queue = orchestrator_connection.get_queue_elements(config.QUEUE_NAME, status=QueueStatus.DONE)
    sent_letters = [queue_element.reference for queue_element in completed_queue]

    # Get recipients from SQL
    from_date = (datetime.now() - timedelta(days=config.MAX_DAYS_SINCE_LAST_MOVE)).strftime("%m-%d-%Y")
    query = sql_data.sql_query(from_date)
    data = sql_data.read_data(query)
    data_dict = sql_data.sql_to_dict(data)

    # Generate and send letters to recipients
    for cpr, name in data_dict.items():
        # Make sure we didn't send this letter already
        encrypted_id = encrypt_data(cpr, name)
        if encrypted_id in sent_letters:
            continue

        # Send the letter and save a reference for later
        queue_element = orchestrator_connection.create_queue_element(config.QUEUE_NAME, encrypted_id)
        m = digital_post_composer.compose_message("Welcome to Aarhus", config.CVR, cpr, config.PDF_WELCOME)
        digital_post.send_message("Digital Post", m, kombit_access)
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE)


def encrypt_data(data: str, salt: str) -> str:
    """Encrypt data with salt.

    Args:
        data: Data to encrypt.
        salt: Related token to salt the data with.

    Returns:
        Encrypted data as string.
    """
    salted_data = data + salt
    hash_obj = hashlib.sha256(salted_data.encode())
    return hash_obj.hexdigest()


if __name__ == "__main__":
    conn_string = os.getenv("OpenOrchestratorConnString")
    crypto_key = os.getenv("OpenOrchestratorKey")
    oc = OrchestratorConnection("Udsendelse af velkomstbrev", conn_string, crypto_key, "")
    process(oc)
