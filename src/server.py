from datetime import datetime, timedelta
from flask import Flask, jsonify, send_file
import json
import logging
from txn_simulator import generate as transaction_generator

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

@app.route('/api/generate',methods=['GET'])
def generate():
    _, json_path = transaction_generator()
    return send_file(json_path,mimetype='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)