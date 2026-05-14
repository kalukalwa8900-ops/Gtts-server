import os
import uuid
from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
from gtts import gTTS

app = Flask(__name__)
CORS(app)


# ================================
# HOME
# ================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status":  "ok",
        "service": "gtts-server",
        "routes":  ["GET /", "GET /health", "POST /tts"]
    })


# ================================
# HEALTH — required by dubbing server
# ================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status":  "ok",
        "service": "gtts-server"
    })


# ================================
# TTS
# ================================

@app.route("/tts", methods=["POST"])
def tts():
    data = request.get_json(force=True, silent=True) or {}

    text = data.get("text", "").strip()
    lang = data.get("lang", "hi").strip() or "hi"

    if not text:
        return jsonify({"error": "text is required and cannot be empty"}), 400

    # Truncate to 4000 chars — very long text can freeze gTTS
    text = text[:4000]

    filename = f"/tmp/{uuid.uuid4().hex}.mp3"

    # Auto-delete temp file after response is sent
    @after_this_request
    def remove_file(response):
        try:
            os.remove(filename)
        except Exception:
            pass
        return response

    try:
        tts_obj = gTTS(
            text=text,
            lang=lang,
            slow=False
        )
        tts_obj.save(filename)
    except Exception as e:
        # Clean up if file was partially written
        try:
            os.remove(filename)
        except Exception:
            pass
        return jsonify({"error": f"TTS generation failed: {str(e)}"}), 500

    # Validate file was actually written and is not empty
    if not os.path.exists(filename) or os.path.getsize(filename) < 100:
        return jsonify({"error": "TTS generated empty audio file"}), 500

    return send_file(
        filename,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="speech.mp3"
    )


# ================================
# START (dev only — prod uses gunicorn)
# ================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
