"""This module contains the main process of the robot."""

import hashlib

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection, QueueStatus
from python_serviceplatformen.authentication import KombitAccess
from python_serviceplatformen import digital_post
import itk_dev_event_log as event_log

from robot_framework.custom import sql_data, keyvault, digital_post_composer
from robot_framework import config


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")
    event_log.setup_logging(orchestrator_connection.get_constant(config.EVENT_LOG_CONN).value)

    # Get tokens
    vault_auth = orchestrator_connection.get_credential(config.KEYVAULT_CREDENTIALS)
    vault_uri = orchestrator_connection.get_constant(config.KEYVAULT_URI).value
    certificate = keyvault.get_certificate(vault_username=vault_auth.username, vault_password=vault_auth.password, vault_uri=vault_uri, vault_path=config.KEYVAULT_PATH)
    kombit_access = KombitAccess(cvr=config.CVR, cert_path=certificate)

    # Get everyone whose letter is due now from SQL. The query decides who is due,
    # so the queue is only used to keep track of who has already received a letter.
    data = sql_data.get_letter_receivers(config.MIN_DAYS_SINCE_ARRIVAL, config.MAX_DAYS_SINCE_ARRIVAL)
    orchestrator_connection.log_info(f"Number of people from query: {len(data)}")

    # Generate and send letters to recipients
    for cpr, name, arrival_date in data:
        encrypted_id = encrypt_data(cpr, name)
        queue_elements = orchestrator_connection.get_queue_elements(config.QUEUE_NAME, encrypted_id)

        # Don't send letter twice or if recipient doesn't have Digital Post
        if any(queue_element.status == QueueStatus.DONE for queue_element in queue_elements):
            orchestrator_connection.log_info("Skipping repeated person.")
            continue
        if not digital_post.is_registered(cpr, 'digitalpost', kombit_access):
            orchestrator_connection.log_info("Skipping not registered for Digital Post.")
            continue

        # Mark the letter as in progress before sending, so an unfinished attempt is retried on the next run
        queue_element = queue_elements[0] if queue_elements else orchestrator_connection.create_queue_element(config.QUEUE_NAME, encrypted_id, data=arrival_date.strftime(config.QUEUE_DATE_FORMAT))
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.IN_PROGRESS)

        m = digital_post_composer.compose_message("Welcome to Aarhus", config.CVR, cpr, name, config.PDF_WELCOME)
        digital_post.send_message("Digital Post", m, kombit_access)
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE)
        orchestrator_connection.log_info("Letter sent.")
        event_log.emit(orchestrator_connection.process_name, "Sent letter")


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


if __name__ == '__main__':
    import os
    import uuid
    conn_string = os.getenv("OpenOrchestratorConnString")
    crypto_key = os.getenv("OpenOrchestratorKey")
    oc = OrchestratorConnection("Velkomstbreve", conn_string, crypto_key, '', "trigger_id", uuid.uuid4())
    process(oc)
