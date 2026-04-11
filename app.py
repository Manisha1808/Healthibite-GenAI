import os
from flask import Flask, render_template, request
import sqlite3
import json

# Safe RAG import
try:
    from rag import get_health_recommendation
except Exception as e:
    print("RAG import failed:", e)
    get_health_recommendation = None

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

    if get_health_recommendation is None:
        result = "⚠️ AI system failed to load."
    else:
        try:
            result = get_health_recommendation(query, age, goal, activity)
        except Exception as e:
            print("Error in /result route:", e)
            result = "⚠️ Something went wrong. Please try again."

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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)