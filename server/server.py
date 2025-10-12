from flask import Flask, request, jsonify
import service

app = Flask(__name__)


@app.route("/account/prompt", methods=["POST"])
def prompt_for_account_action():
    try:
        data: dict = request.get_json()

        return (jsonify(data), 200)

    except Exception as e:
        return (jsonify({"error": f"Error processing request: {str(e)}"}), 500)


@app.route("/account/action")
def directly_called_account_action():
    try:
        return service.directly_called_account_action(request)

    except Exception as e:
        return (jsonify({"error": f"Error processing request: {str(e)}"}), 500)


def serialize_response(response: str) -> dict:
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=False)
