from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

suppliers = {}  # Dictionary to track supplier fraud activity
MAX_FRAUD_COUNT = 3  # Threshold for banning a supplier

GEMINI_API_KEY = "AIzaSyB9AGVgkWIlGo9BS0n5cq9co4AdqiPeBbY"
GEMINI_API_URL = "https://generativeai.googleapis.com/v1/models/gemini-pro:generateText"

def detect_fraud(supplier_id, received_goods, actual_price, expected_goods, expected_price):
    """Detects fraud based on received and expected values using Gemini API."""
    prompt = f"""
    Supplier ID: {supplier_id}
    Expected Goods: {expected_goods}
    Received Goods: {received_goods}
    Expected Price: {expected_price}
    Actual Price Charged: {actual_price}

    Determine if fraud occurred based on these values. If the supplier delivered fewer goods or charged more, respond with 'FRAUD'. Otherwise, respond with 'NO FRAUD'.
    """

    response = requests.post(GEMINI_API_URL, json={"prompt": prompt}, headers={"Authorization": f"Bearer {GEMINI_API_KEY}"})
    result = response.json()

    return "FRAUD" in result.get("text", "").upper()

@app.route('/report_fraud', methods=['POST'])
def report_fraud():
    data = request.json
    supplier_id = data["supplier_id"]
    received_goods = data["received_goods"]
    actual_price = data["actual_price"]
    expected_goods = data["expected_goods"]
    expected_price = data["expected_price"]

    fraud_detected = detect_fraud(supplier_id, received_goods, actual_price, expected_goods, expected_price)

    if fraud_detected:
        if supplier_id in suppliers:
            suppliers[supplier_id] += 1
        else:
            suppliers[supplier_id] = 1

        if suppliers[supplier_id] >= MAX_FRAUD_COUNT:
            return jsonify({"message": "Supplier BANNED due to continuous fraud.", "status": "banned"})
        else:
            return jsonify({"message": "Fraud detected!", "status": "fraud"})
    return jsonify({"message": "No fraud detected.", "status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)
