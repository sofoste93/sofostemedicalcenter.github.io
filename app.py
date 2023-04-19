from encryption import generate_key, encrypt_data
from encryption import decrypt_data
from qr_code_generator import generate_qr_code
from flask import Flask, jsonify, json, request, send_file, render_template

import random

app = Flask(__name__)


@app.route('/')
def language_selection():
    return render_template("language_selection.html")


@app.route('/enter-pin')
def enter_pin():
    return render_template("enter_pin.html")


@app.route('/form-page-1')
def form_page_1():
    return render_template("form_page_1.html")


@app.route('/form-page-2')
def form_page_2():
    return render_template("form_page_2.html")


@app.route('/form-page-3')
def form_page_3():
    return render_template("form_page_3.html")


@app.route('/summary')
def summary():
    return render_template("summary.html")


@app.route('/generate-pin', methods=['GET'])
def generate_pin():
    pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return jsonify({'pin': pin})


def validate_medical_data(data):
    required_fields = ['sex', 'last_name', 'first_name', 'date_of_birth', 'place_of_birth', 'age', 'recent_illnesses',
                       'allergies', 'heart_ailments', 'asthma', 'diabetes', 'medications', 'dietary_supplements',
                       'treatments']

    for field in required_fields:
        if field not in data:
            return False
    return True


@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.get_json()

    if not validate_medical_data(data):
        return jsonify({'error': 'Invalid data'}), 400

    # Encrypt data and save to the device
    key = generate_key()
    encrypted_data = encrypt_data(json.dumps(data), key)

    with open('medical_data.enc', 'wb') as f:
        f.write(encrypted_data)

    return jsonify({'success': True, 'encryption_key': key.decode('utf-8')})


@app.route('/generate-qr-code/<key>', methods=['GET'])
def generate_qr_code_route(key):
    with open('medical_data.enc', 'rb') as f:
        encrypted_data = f.read()

    decrypted_data = decrypt_data(encrypted_data, key.encode('utf-8'))
    generate_qr_code(decrypted_data, key)

    return send_file('qr_code.png', mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)
