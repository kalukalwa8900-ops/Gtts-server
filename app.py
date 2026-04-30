import os
import uuid
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from gtts import gTTS

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "TTS API is running"

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(force=True, silent=True) or {}

    text = data.get("text", "").strip()
    lang = data.get("lang", "en").strip() or "en"

    if not text:
        return jsonify({"error": "text is required and cannot be empty"}), 400

    filename = f"/tmp/{uuid.uuid4().hex}.mp3"

    try:
        tts_obj = gTTS(text=text, lang=lang)
        tts_obj.save(filename)
    except Exception as e:
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    return send_file(
        filename,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="speech.mp3"
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
