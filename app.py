import os
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError, OperationFailure
from dotenv import load_dotenv

# Load environment variables from .env (ignored in production if not present)
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# ── Database connection ──────────────────────────────────────────────────────
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError(
        "MONGO_URI is not set. "
        "Create a .env file based on .env.example and add your Atlas connection string."
    )

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Verify the connection is reachable before the first request
    client.admin.command("ping")
    print("✓ Connected to MongoDB successfully.")
except (ConnectionFailure, ConfigurationError, OperationFailure) as e:
    raise RuntimeError(
        "Could not connect to MongoDB. "
        "Check that MONGO_URI is correct, your password is right, "
        "and your IP is whitelisted in Atlas Network Access."
    ) from e

# Select database and collection (names unchanged)
db = client["beginner_db"]
todos = db["todos"]


# ── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    # Retrieve all documents from the todos collection
    all_todos = list(todos.find())
    return render_template("index.html", todos=all_todos)


@app.route("/add", methods=["POST"])
def add():
    # Read the submitted form field named 'task'
    task = request.form.get("task")
    # Only insert if the task is not empty
    if task:
        todos.insert_one({"task": task})
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
