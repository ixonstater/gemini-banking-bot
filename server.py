from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/prompt", methods=["POST"])
def prompt():
    try:
        data: dict = request.get_json()
        if not data or not validate_prompt(data):
            return (jsonify({"error": "Unable to read request body."}), 400)

        return (jsonify(data), 200)

    except Exception as e:
        return (jsonify({"error": f"Error processing request: {str(e)}"}), 500)


def validate_prompt(data: dict) -> bool:
    if not "prompt" in data:
        return False

    return True


def serialize_response(response: str) -> dict:
    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=False)
