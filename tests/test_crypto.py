import pytest

from sofoste_medical_center.crypto import (
    PacketError,
    decrypt_record,
    encrypt_record,
    generate_transfer_key,
)


def test_encrypted_packet_round_trip_and_has_no_plaintext():
    record = {"first_name": "Ada", "allergies": "Penicillin"}
    key = generate_transfer_key()
    packet = encrypt_record(record, key)
    assert packet.startswith("SMC2.")
    assert "Ada" not in packet
    assert key.replace("-", "") not in packet
    assert decrypt_record(packet, key) == record


@pytest.mark.parametrize("change", ["wrong-key", "tampered"])
def test_authentication_rejects_wrong_or_modified_data(change):
    key = generate_transfer_key()
    packet = encrypt_record({"first_name": "Ada"}, key)
    if change == "wrong-key":
        key = generate_transfer_key()
    else:
        packet = packet[:-1] + ("A" if packet[-1] != "A" else "B")
    with pytest.raises(PacketError):
        decrypt_record(packet, key)
