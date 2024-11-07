"""Module for getting a certificate from hvac client"""
from hvac import Client


def get_certificate(vault_username: str, vault_password: str, vault_uri: str, vault_path: str) -> str:
    # Access Keyvault
    vault_client = Client(vault_uri)
    token = vault_client.auth.approle.login(role_id=vault_username, secret_id=vault_password)
    vault_client.token = token['auth']['client_token']

    # Get certificate
    read_response = vault_client.secrets.kv.v2.read_secret_version(mount_point='rpa', path=vault_path, raise_on_deleted_version=True)
    certificate = read_response['data']['data']['cert']

    # Because KombitAccess requires a file, we save and delete the certificate after we use it
    certificate_path = "certificate.pem"
    with open(certificate_path, 'w', encoding='utf-8') as cert_file:
        cert_file.write(certificate)
    return certificate_path
