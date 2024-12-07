
import os
import subprocess
from flask import Flask, request, render_template_string, redirect, url_for
from dotenv import set_key, load_dotenv


app = Flask(__name__)

# Path to the .env file
ENV_PATH = ".env"

# Load existing .env file
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

# HTML template for the form
FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Paycor Credentials</title>
</head>
<body>
    <h1>Enter Your Paycor Credentials</h1>
    <form method="POST" action="{{ url_for('save_credentials') }}">
        <label for="username">Username:</label><br>
        <input type="text" id="username" name="username" required><br><br>
        <label for="password">Password:</label><br>
        <input type="password" id="password" name="password" required><br><br>
        <button type="submit">Save</button>
    </form>
    <form method="POST" action="{{ url_for('run_paycorbot') }}">
        <button type="submit">Run Paycorbot</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    """Displays the credentials form."""
    return render_template_string(FORM_TEMPLATE)

@app.route("/save", methods=["POST"])
def save_credentials():
    """Saves the credentials securely to the .env file."""
    username = request.form.get("username")
    password = request.form.get("password")

    if not username or not password:
        return "Error: Username and Password are required!", 400

    # Save credentials to the .env file
    set_key(ENV_PATH, "PAYCOR_USERNAME", username)
    set_key(ENV_PATH, "PAYCOR_PASSWORD", password)

    return redirect(url_for("index"))

@app.route("/run", methods=["POST"])
def run_paycorbot():
    """Runs the Paycorbot script."""
    try:
        result = subprocess.run(
            ["poetry", "run", "python", "-m", "paycorbot"],
            check=True,
            capture_output=True,
            text=True
        )
        return f"<pre>{result.stdout}</pre>"
    except subprocess.CalledProcessError as e:
        return f"<pre>Error: {e.stderr}</pre>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
