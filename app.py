from flask import Flask, render_template, request
from rag import get_health_recommendation

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)