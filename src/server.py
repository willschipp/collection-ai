from datetime import datetime, timedelta
from flask import Flask, request, send_file, jsonify
import json
import logging
from txn_simulator import generate as transaction_generator
from repayment_calclator import get_repayment_plan_json
import uuid

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

@app.route('/api/generate',methods=['GET'])
def generate():
    _, json_path = transaction_generator()
    return send_file(json_path,mimetype='application/json')

@app.route('/api/repayments',methods=['POST'])
def get_repayment():
    upload_id = str(uuid.uuid4())
    months = request.args.get('months')
    data = request.get_json()
    file_path = f'./upload/transactions_{upload_id}.json'
    logger.info(f"months {months}")

    with open(file_path,'w') as out_file:
        json.dump(data,out_file,indent=4)
    # now execute
    repayment_amount = round(get_repayment_plan_json(file_path,months),2)
    return jsonify({'repaymentAmount':repayment_amount}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=False)