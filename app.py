from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/generate-pin', methods=['GET'])
def generate_pin():
    pin = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return jsonify({'pin': pin})

if __name__ == '__main__':
    app.run(debug=True)
