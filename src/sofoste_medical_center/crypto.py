"""Authenticated encryption for a self-contained QR transfer packet.

The QR contains salt + nonce + ciphertext. The transfer key is deliberately
kept outside the QR, so scanning the code alone cannot reveal patient data.
"""

from __future__ import annotations

import base64
import json
import secrets
import zlib
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

PACKET_PREFIX = "SMC2."
ASSOCIATED_DATA = b"sofoste-medical-center:v2"
MAX_PACKET_LENGTH = 7000


class PacketError(ValueError):
    """Raised when a packet or transfer key cannot be authenticated."""


def generate_transfer_key() -> str:
    """Return an 80-bit, human-readable key grouped for dictation."""
    raw = base64.b32encode(secrets.token_bytes(10)).decode("ascii").rstrip("=")
    return "-".join(raw[index : index + 4] for index in range(0, len(raw), 4))


def normalize_transfer_key(value: str) -> str:
    normalized = "".join(character for character in value.upper() if character.isalnum())
    if len(normalized) != 16 or any(character not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567" for character in normalized):
        raise PacketError("invalid transfer key")
    return normalized


def _derive_key(transfer_key: str, salt: bytes) -> bytes:
    return Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(
        normalize_transfer_key(transfer_key).encode("ascii")
    )


def encrypt_record(record: dict[str, Any], transfer_key: str) -> str:
    """Compress and encrypt a JSON record with AES-256-GCM."""
    plaintext = json.dumps(record, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = zlib.compress(plaintext, level=9)
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(_derive_key(transfer_key, salt)).encrypt(
        nonce, compressed, ASSOCIATED_DATA
    )
    payload = base64.urlsafe_b64encode(salt + nonce + ciphertext).decode("ascii").rstrip("=")
    return PACKET_PREFIX + payload


def decrypt_record(packet: str, transfer_key: str) -> dict[str, Any]:
    """Authenticate and decode a packet; expose one neutral error on failure."""
    try:
        if not packet.startswith(PACKET_PREFIX) or len(packet) > MAX_PACKET_LENGTH:
            raise PacketError("invalid packet")
        encoded = packet[len(PACKET_PREFIX) :]
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if len(payload) < 45:
            raise PacketError("invalid packet")
        salt, nonce, ciphertext = payload[:16], payload[16:28], payload[28:]
        compressed = AESGCM(_derive_key(transfer_key, salt)).decrypt(
            nonce, ciphertext, ASSOCIATED_DATA
        )
        inflater = zlib.decompressobj()
        plaintext = inflater.decompress(compressed, 16_385)
        if len(plaintext) > 16_384 or inflater.unconsumed_tail or not inflater.eof:
            raise PacketError("packet is too large")
        decoded = json.loads(plaintext)
        if not isinstance(decoded, dict):
            raise PacketError("invalid packet")
        return decoded
    except (InvalidTag, PacketError, ValueError, TypeError, json.JSONDecodeError, zlib.error) as exc:
        raise PacketError("packet or transfer key is invalid") from exc
