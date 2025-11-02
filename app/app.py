from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return "<h1>Sample App Running</h1><p>Visit /health for status.</p>"

@app.route("/health")
def health():
    return jsonify(status="ok"), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)