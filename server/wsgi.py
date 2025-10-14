import os
from flask import Flask, request, jsonify
import waitress
import service
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


@app.route("/account/prompt", methods=["POST"])
def prompt_for_account_action():
    try:
        return service.prompted_account_action(request)

    except Exception as e:
        return (jsonify({"error": f"Error processing request: {str(e)}"}), 500)


@app.route("/account/action", methods=["POST"])
def directly_called_account_action():
    try:
        return service.directly_called_account_action(request)

    except Exception as e:
        return (jsonify({"error": f"Error processing request: {str(e)}"}), 500)


# In prod the app variable above gets picked up by the containers waitress instance
if __name__ == "__main__" and os.getenv("GEMINI_BANKING_ENVIRONMENT") != "prod":
    waitress.serve(app, host="0.0.0.0", port=8080)
