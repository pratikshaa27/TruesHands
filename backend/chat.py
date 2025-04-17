from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Configure Gemini API Key
genai.configure(api_key="AIzaSyB9AGVgkWIlGo9BS0n5cq9co4AdqiPeBbY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Chatbot context
context = """
You are a chatbot that answers questions only related to the following features of a donation platform:

1. User Registration and Authentication
   - Institutes, donors, and suppliers register separately.
   - Institutes need verification for legitimacy.

2. Institute Dashboard
   - Raise requirements (e.g., 10 kg rice, 5 liters of milk).
   - Track donations (pending, fulfilled, etc.).
   - Log usage of received items.
   - Provide feedback on received supplies.

3. Donor Dashboard
   - Browse requests from institutes.
   - Donate fixed amounts or specific items.
   - Track donations and delivery status.
   - View donation history and feedback.

4. Supplier Dashboard
   - Receive and confirm orders from institutes.
   - Ship items and update delivery status.
   - Track payments from the platform.

5. Admin Dashboard
   - Monitor transactions and oversee donations.
   - Detect anomalies in usage and prevent misuse.
   - Manage suppliers to ensure fair distribution.
   - Resolve disputes between users.

Respond only with information relevant to these features.
"""

@app.route("/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    prompt = data.get("message", "")

    if not prompt:
        return jsonify({"error": "No message provided"}), 400

    # Generate response from Gemini AI
    response = model.generate_content([context, prompt])
    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(debug=True)
