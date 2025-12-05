# This file is placed inside the 'api/' directory.
# Vercel automatically recognizes files in this path as Serverless Functions.

from flask import Flask, jsonify

# Flask is used as a simple Web Server Gateway Interface (WSGI) application
# which Vercel can easily deploy as a Python function.
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    """
    The main API endpoint.
    Returns a success message and a status code.
    """
    response_data = {
        "status": "success",
        "message": "Vercel API is running successfully. Ready for the coding test!",
        "developer": "MAAS Alexander Christian"
    }
    # Track.run will connect to the base URL and check the response.
    return jsonify(response_data)

# Optional: You can define other endpoints here as required by the test.
@app.route('/calculate', methods=['POST'])
def calculate():
    # Example logic for the test:
    # data = request.get_json()
    # result = data.get('input') * 2
    # return jsonify({"result": result})
    return jsonify({"error": "This is a placeholder for your main test logic."})

if __name__ == '__main__':
    # This block is only for local testing, Vercel ignores it during deployment.
    app.run(debug=True)