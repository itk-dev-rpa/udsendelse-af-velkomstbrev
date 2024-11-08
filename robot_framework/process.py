"""This module contains the main process of the robot."""
import hashlib
import os
from datetime import datetime, timedelta

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection, QueueStatus
from python_serviceplatformen.authentication import KombitAccess
from python_serviceplatformen import digital_post
from mailmerge import MailMerge

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

    completed_queue = orchestrator_connection.get_queue_elements(config.QUEUE_NAME, status=QueueStatus.DONE)
    sent_letters = [queue_element.reference for queue_element in completed_queue]

    # Get data from SQL
    from_date = (datetime.now() - timedelta(days=60)).strftime("%m-%d-%Y")
    query = sql_data.sql_query(from_date)
    data = sql_data.read_data(query)
    data_dict = sql_data.sql_to_dict(data)

    kombit_access = KombitAccess(cvr=config.CVR, cert_path="test/Certificate.pem", test=True)
    data_dict = {
        "2611740000": "poul"
    }

    # Generate and send letters to people
    # with MailMerge(config.TEMPLATE, keep_fields="all") as document:
    for cpr, name in data_dict.items():
        # Make sure we didn't send this letter already
        encrypted_id = encrypt_data(cpr, name)
        if encrypted_id in sent_letters:
            print("hej")
            # continue

        # Send the letter and save a reference for later
        queue_element = orchestrator_connection.create_queue_element(config.QUEUE_NAME, encrypted_id)
        # filename = write_document(name, cpr, document)
        filename = config.PDF_WELCOME
        m = digital_post_composer.compose_message("Welcome to Aarhus", config.CVR, cpr, filename)
        digital_post.send_message("Digital Post", m, kombit_access)
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE)


def write_document(name: str, cpr: str, document: MailMerge) -> str:
    filename = f'{config.SAVE_FOLDER}/{cpr}.docx'
    document.merge(Fornavn=name,
                   CPR=cpr)
    document.write(filename)
    return filename


def encrypt_data(data: str, salt: str) -> str:
    """Take some data and encrypt it with some salt.

    Args:
        data: Data to encrypt.
        salt: Related token to salt the data with.
    """
    salted_data = data + salt
    hash_obj = hashlib.sha256(salted_data.encode())
    return hash_obj.hexdigest()


if __name__ == "__main__":
    conn_string = os.getenv("OpenOrchestratorConnString")
    crypto_key = os.getenv("OpenOrchestratorKey")
    oc = OrchestratorConnection("Udsendelse af velkomstbrev", conn_string, crypto_key, "")
    process(oc)
