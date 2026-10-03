from __future__ import annotations

import base64
import hmac
import io
import re
import secrets
from typing import Any

import qrcode
from flask import Flask, abort, redirect, render_template, request, session, url_for

from .crypto import PacketError, decrypt_record, encrypt_record, generate_transfer_key
from .i18n import LANGUAGES, translations
from .limiter import AttemptLimiter
from .validation import FIELDS, ValidationError, validate_record

SAFE_HOST = re.compile(r"^[A-Za-z0-9.:[\]-]+$")


def _qr_data_uri(content: str) -> str:
    # Level L leaves enough room for every validated record while the AES-GCM
    # authentication tag still detects any changed or partially read packet.
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=7, border=3)
    qr.add_data(content)
    qr.make(fit=True)
    image = qr.make_image(fill_color="#103f32", back_color="white")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return "data:image/png;base64," + base64.b64encode(output.getvalue()).decode("ascii")


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=secrets.token_hex(32),
        MAX_CONTENT_LENGTH=32 * 1024,
        MAX_FORM_MEMORY_SIZE=32 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Strict",
    )
    if test_config:
        app.config.update(test_config)
    limiter = AttemptLimiter()

    def language() -> str:
        selected = request.args.get("lang") or session.get("language", "fr")
        return selected if selected in LANGUAGES else "fr"

    @app.context_processor
    def inject_globals() -> dict[str, Any]:
        lang = language()
        token = session.setdefault("csrf_token", secrets.token_urlsafe(24))
        return {"t": translations(lang), "lang": lang, "languages": LANGUAGES, "csrf_token": token}

    @app.before_request
    def protect_posts() -> None:
        if request.method == "POST":
            expected = session.get("csrf_token", "")
            supplied = request.form.get("csrf_token", "")
            if not expected or not hmac.compare_digest(expected, supplied):
                abort(400)

    @app.after_request
    def secure_response(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; img-src 'self' data:; style-src 'self'; "
            "script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; "
            "form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store, max-age=0"
        return response

    @app.get("/")
    def home():
        lang = language()
        if request.args.get("lang") in LANGUAGES:
            session["language"] = lang
        return render_template("home.html")

    @app.route("/intake", methods=["GET", "POST"])
    def intake():
        error = None
        if request.method == "POST":
            try:
                record = validate_record(request.form)
                key = generate_transfer_key()
                packet = encrypt_record(record, key)
                host = request.host if SAFE_HOST.fullmatch(request.host) else "127.0.0.1:8765"
                scan_url = f"{request.scheme}://{host}{url_for('receive')}#packet={packet}"
                return render_template(
                    "share.html", key=key, packet=packet, qr_uri=_qr_data_uri(scan_url)
                )
            except ValidationError:
                error = translations(language())["form_error"]
        return render_template("intake.html", fields=FIELDS, error=error)

    @app.route("/receive", methods=["GET", "POST"])
    def receive():
        error = None
        record = None
        identity = request.remote_addr or "local"
        if request.method == "POST":
            if not limiter.allowed(identity):
                error = translations(language())["limited"]
            else:
                try:
                    record = decrypt_record(request.form.get("packet", ""), request.form.get("key", ""))
                    limiter.clear(identity)
                except PacketError:
                    limiter.failed(identity)
                    error = translations(language())["invalid"]
        return render_template("receive.html", error=error, record=record, fields=FIELDS)

    @app.get("/health")
    def health():
        return {"status": "ok", "version": "2.0.0"}

    @app.get("/lang/<selected>")
    def set_language(selected: str):
        if selected in LANGUAGES:
            session["language"] = selected
        return redirect(request.referrer or url_for("home"))

    return app
