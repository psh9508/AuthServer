import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.services.exceptions.source_control_exception import (
    InvalidSourceControlEncryptionKeyError,
    SourceControlEncryptionKeyNotConfiguredError,
)


class ScmPemCipher:
    @classmethod
    def encrypt(cls, pem: str) -> str:
        key = cls._get_key()
        nonce = os.urandom(12)
        cipher = AESGCM(key)
        encrypted = cipher.encrypt(nonce, pem.encode("utf-8"), None)
        return base64.b64encode(nonce + encrypted).decode("utf-8")

    @classmethod
    def decrypt(cls, encrypted_pem: str) -> str:
        key = cls._get_key()

        try:
            payload = base64.b64decode(encrypted_pem)
        except Exception as exc:
            raise InvalidSourceControlEncryptionKeyError() from exc

        nonce = payload[:12]
        cipher_text = payload[12:]
        cipher = AESGCM(key)
        decrypted = cipher.decrypt(nonce, cipher_text, None)
        return decrypted.decode("utf-8")

    @classmethod
    def _get_key(cls) -> bytes:
        encryption_key = os.getenv("SCM_PEM_ENCRYPTION_KEY")
        if not encryption_key:
            raise SourceControlEncryptionKeyNotConfiguredError()

        try:
            key = base64.b64decode(encryption_key)
        except Exception as exc:
            raise InvalidSourceControlEncryptionKeyError() from exc

        if len(key) not in (16, 24, 32):
            raise InvalidSourceControlEncryptionKeyError()

        return key
