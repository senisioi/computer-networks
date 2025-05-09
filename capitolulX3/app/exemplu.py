from flask import Flask, jsonify
from flask import request

app = Flask(__name__)

@app.route('/')
def hello():
    return ""


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=1)