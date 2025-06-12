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

    # Get recipients from SQL
    from_date = (datetime.now() - timedelta(days=config.MAX_DAYS_SINCE_LAST_MOVE)).strftime(config.DB_DATE_FORMAT)
    query = sql_data.sql_query(from_date)
    data = sql_data.read_data(query)

    # Generate and send letters to recipients
    for cpr, name, move_date, prev_kom_kode in data:
        encrypted_id = encrypt_data(cpr, name)

        queue_element = orchestrator_connection.get_queue_elements(config.QUEUE_NAME, encrypted_id)
        queue_element = queue_element[0] if queue_element else None

        if not queue_element:
            # Skip moves from within the city, but only if first move
            if prev_kom_kode == config.LOCAL_KOM_KODE:
                continue
            # Create a new queue element with the current date
            queue_element = orchestrator_connection.create_queue_element(config.QUEUE_NAME, encrypted_id, data=move_date.strftime(config.DB_DATE_FORMAT))
            orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.IN_PROGRESS)

        elif queue_element.status == QueueStatus.DONE or not digital_post.is_registered(cpr, 'digitalpost', kombit_access):
            # Don't send letter twice or if recipient doesn't have Digital Post
            continue

        queue_date = datetime.strptime(queue_element.data, config.DB_DATE_FORMAT)
        if queue_element.status == QueueStatus.IN_PROGRESS and (datetime.today() - queue_date).days >= config.MIN_DAYS_SINCE_LAST_MOVE:
            # Send the letter
            m = digital_post_composer.compose_message("Welcome to Aarhus", config.CVR, cpr, name, config.PDF_WELCOME)
            # digital_post.send_message("Digital Post", m, kombit_access)
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
