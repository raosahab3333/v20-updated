
from flask import Flask, render_template
from strategy import run_strategy

app = Flask(__name__)

@app.route("/")
def index():
    df = run_strategy()
    stocks = df.to_dict(orient="records") if not df.empty else []
    return render_template("index.html", stocks=stocks)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
