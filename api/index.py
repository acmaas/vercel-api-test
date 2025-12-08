from flask import Flask, jsonify, request
import os
from supabase import create_client, Client, PostgrestAPIError

SUPABASE_URL: str = os.environ.get("SUPABASE_URL")
SUPABASE_KEY: str = os.environ.get("SUPABASE_KEY")

supabase: Client = None
db_error_message: str = ""

if not SUPABASE_URL or not SUPABASE_KEY:
    db_error_message = "FATAL: Supabase environment variables are missing."
else:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        db_error_message = f"Client Initialization Failed: {e}"
        supabase = None

app = Flask(__name__)


def check_db_connection() -> dict:
    """
    Performs a non-destructive query to check if the database is reachable.
    """
    if not supabase:
        return {
            "is_connected": False,
            "details": db_error_message
        }

    try:
        # We attempt to call a system function (now) that doesn't need a table.
        # This proves the client can reach the database server.

        # This table is guaranteed to exist and is usually readable by the anon key.
        response = (
            supabase.table('health_check')
            .select('status')
            .limit(1)
            .execute()
        )

        # If .execute() completes, the connection is good.
        data_status = f"Data retrieved: {response.data[0]['status']}" if response.data else "Table is reachable but empty."

        return {
            "is_connected": True,
            "details": f"Connection successful to custom table. {data_status}"
        }

    except PostgrestAPIError as e:
        # If we get a PostgREST error (e.g., 401 Unauthorized), the connection is bad.
        # This proves the key/URL are invalid or lack basic system read permissions.
        return {
            "is_connected": False,
            "details": f"PostgREST Error: Key/Permissions invalid: {e.message}"
        }

    except Exception as e:
        # Catches network errors or other fundamental connection issues
        return {
            "is_connected": False,
            "details": f"Network or General Connection Error: {e.__class__.__name__}: {e}"
        }

@app.route('/', methods=['GET'])
def home():
    """
    The main API endpoint.
    Returns a success message and a status code.
    """
    connection_status = check_db_connection()

    status_code = 200
    if not connection_status["is_connected"]:
        # If the DB connection fails, we report an internal server error (500)
        status_code = 500

    return jsonify({
        "status": "API Running",
        "database_connection": connection_status,
        "message": "Use /api/user/<id> for the dynamic endpoint."
    }), status_code


# --- Dynamic Endpoint using Query Parameters ---
@app.route('/api/lookup', methods=['GET'])
def lookup_multiple_params():
    """
    Handles requests like: /api/lookup?id=123&product=ABC
    The parameters are accessed via request.args
    """

    # Use request.args.get() to safely retrieve parameters.
    # The second argument is a default value if the parameter is missing.
    id_code = request.args.get('id', 'N/A')
    product_code = request.args.get('product', 'N/A')

    # --- Server-Side Logic ---

    if id_code != 'N/A' and product_code != 'N/A':
        message = (f"Successfully processed request for ID: {id_code} "
                   f"and Product: {product_code}.")
        http_status = 200
    else:
        message = "Missing required parameters (id and/or product)."
        http_status = 400

    response_data = {
        "status": "processed",
        "requested_id": id_code,
        "requested_product": product_code,
        "detail": message
    }

    # Return the JSON response and the appropriate HTTP status code
    return jsonify(response_data), http_status

if __name__ == '__main__':
    app.run(debug=True)