import base64
import os

from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from infrastructure.logging.LoggerImplements import LoggerImplements

log_impl = LoggerImplements("DecryptLogger")


def decrypt(secret_name: str) -> str:
    """Decrypts an encrypted text using AES or Azure Key Vault"""
    plaintext = ""
    try:
        log_impl.log_information("Starting decryption process", "decrypt")

        # Check if we are using Azure Key Vault for decryption
        if os.getenv("SiKeyVault") == "true":
            # Get Azure credentials from environment variables
            key_name = os.getenv("keyName")
            client_id = os.getenv("ClientId")
            client_secret = os.getenv("ClientSecret")
            tenant_id = os.getenv("TuAzureTenantID")

            log_impl.log_information(
                f"Connecting to Azure Key Vault: https://{key_name}.vault.azure.net/", "decrypt", f"Using Key Vault: {key_name}"
            )

            # Authenticate with Azure using client credentials
            client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)
            secret_client = SecretClient(vault_url=f"https://{key_name}.vault.azure.net/", credential=client_credential)

            # Retrieve the secret from the Key Vault
            log_impl.log_information(f"Fetching secret: {secret_name}", "decrypt", f"Secret name: {secret_name}")
            secret = secret_client.get_secret(secret_name)
            plaintext = secret.value  # Assign the value of the secret to the plaintext variable

        else:
            # If not using Azure Key Vault, decrypt using AES encryption
            if not secret_name:
                return ""

            log_impl.log_information("Using AES decryption.", "decrypt", "AES decryption triggered")

            # Decode the AES key and initialization vector (IV) from base64
            key = base64.b64decode(os.getenv("AES_KEY"))
            iv = base64.b64decode(os.getenv("AES_IV"))

            log_impl.log_information(f"AES Key (Base64 decoded): {key}", "decrypt", "AES Key decoded")
            log_impl.log_information(f"AES IV (Base64 decoded): {iv}", "decrypt", "AES IV decoded")

            # Decode the ciphertext (secret_name) from base64
            cipher_text = base64.b64decode(secret_name)

            # Set up the AES decryption cipher in CBC mode
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            # Decrypt the data and finalize the decryption process
            decrypted_data = decryptor.update(cipher_text) + decryptor.finalize()

            # Remove padding (PKCS7)
            unpadder = padding.PKCS7(128).unpadder()
            unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

            plaintext = unpadded_data.decode("utf-8")

        return plaintext

    except Exception as e:
        log_impl.log_error(f"Error during decryption: {e}", "decrypt", f"Error: {e}")
        raise Exception("Error retrieving the secret")
