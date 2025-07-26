from flask import Blueprint, request, jsonify
from app import app

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chatbot', methods=['POST'])
def chatbot():
    try:
        data = request.get_json()
        prompt = data.get("message", "")

        if not prompt:
            return jsonify({"success": False, "error": "No message provided"}), 400

        # Generate response using the shared Gemini model
        response = app.gemini_model.generate_content([app.chatbot_context, prompt])
        
        return jsonify({
            "success": True,
            "response": response.text
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Chatbot service unavailable",
            "details": str(e)
        }), 500