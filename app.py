import os
from flask import Flask, render_template, request
from rag import get_health_recommendation
import sqlite3
import json


app = Flask(__name__)
app.jinja_env.filters['from_json'] = json.loads

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    age = request.form.get("age")
    goal = request.form.get("goal")
    activity = request.form.get("activity")
    query = request.form.get("query")

    try:
        result = get_health_recommendation(query, age, goal, activity)
    except Exception as e:
        result = f"⚠️ Error: {str(e)}"

    return render_template("result.html", result=result)

@app.route("/history")
def history():
    conn = sqlite3.connect("healthibite.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, timestamp, query, severity, response
        FROM history
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return render_template("history.html", rows=rows)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # IMPORTANT
    app.run(host="0.0.0.0", port=port)
