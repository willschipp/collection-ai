from datetime import datetime, timedelta
from flask import Flask, jsonify
import json
import logging
from txn_simulator import generate_cc_transactions

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

@app.route('/api/generate',methods=['GET'])
def generate():
    today_str = (datetime.now() - timedelta(days=270)).strftime('%Y-%m-%-d')
    df = generate_cc_transactions(today_str)
    json_str = df.to_json(orient='records')
    json_obj = json.loads(json_str)
    return jsonify(json_obj)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)