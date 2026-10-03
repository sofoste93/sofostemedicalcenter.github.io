import re
import secrets
import string

from sofoste_medical_center import create_app
from sofoste_medical_center.crypto import encrypt_record, generate_transfer_key
from sofoste_medical_center.validation import FIELDS
from sofoste_medical_center.web import _qr_data_uri


def app():
    return create_app({"TESTING": True, "SECRET_KEY": "test-key"})


def csrf(client, path="/intake"):
    page = client.get(path)
    return re.search(rb'name="csrf_token" value="([^"]+)"', page.data).group(1).decode()


def test_security_headers_and_health():
    with app().test_client() as client:
        response = client.get("/health")
        assert response.json == {"status": "ok", "version": "2.0.0"}
        assert response.headers["X-Frame-Options"] == "DENY"
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]
        assert response.headers["Cache-Control"].startswith("no-store")


def test_intake_creates_qr_without_writing_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with app().test_client() as client:
        response = client.post("/intake", data={
            "csrf_token": csrf(client), "first_name": "Ada", "last_name": "Lovelace",
            "birth_date": "1915-12-10", "allergies": "None",
        })
        assert response.status_code == 200
        assert re.search(rb'id="transfer-key">[A-Z2-7-]+', response.data)
        assert b"data:image/png;base64," in response.data
        assert list(tmp_path.iterdir()) == []


def test_receive_rejects_missing_csrf_and_accepts_valid_packet():
    with app().test_client() as client:
        assert client.post("/receive", data={}).status_code == 400
        key = generate_transfer_key()
        packet = encrypt_record({"first_name": "Ada"}, key)
        response = client.post(
            "/receive",
            data={"csrf_token": csrf(client, "/receive"), "packet": packet, "key": key},
        )
        assert response.status_code == 200
        assert b"Ada" in response.data


def test_largest_valid_record_fits_in_qr_code():
    alphabet = string.ascii_letters + string.digits
    record = {
        field: "".join(secrets.choice(alphabet) for _ in range(maximum))
        for field, maximum in FIELDS.items()
    }
    record["birth_date"] = "2000-01-01"
    packet = encrypt_record(record, generate_transfer_key())
    assert _qr_data_uri("http://127.0.0.1:8765/receive#packet=" + packet).startswith(
        "data:image/png;base64,"
    )
