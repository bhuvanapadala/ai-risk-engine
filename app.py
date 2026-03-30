from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Home route (UI page)
@app.route("/")
def home():
    return render_template("index.html")

# API route (we will connect AI later)
from engine import analyze_with_ai, extract_text_from_file

@app.route("/analyze", methods=["POST"])
def analyze():

    if 'file' in request.files:
        file = request.files['file']
        user_input = extract_text_from_file(file)
        category = "auto"

    else:
        data = request.json
        user_input = data.get("input")
        category = "auto"

    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = analyze_with_ai(user_input, category)

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)