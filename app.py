# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import re
import traceback # Importer traceback for detaljeret fejl-logging

app = Flask(__name__)
CORS(app)

# parse_stats funktionen (uændret)
def parse_stats(text):
    # ... din parsing-logik her ...
    stats = {}
    try:
        match = re.search(r"Boldbesiddelse\s*(\d+)\s*%\s*(\d+)\s*%", text, re.IGNORECASE)
        if match:
            stats['hjemme_boldbesiddelse'] = int(match.group(1))
            stats['ude_boldbesiddelse'] = int(match.group(2))
    except Exception:
        pass # Ignorer parsing fejl for nu
    return stats


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'screenshot' not in request.files:
        return jsonify({"error": "Ingen fil vedhæftet"}), 400

    file = request.files['screenshot']
    if not file:
        return jsonify({"error": "Ingen fil valgt"}), 400

    try:
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image, lang='dan')
        parsed_data = parse_stats(text)
        
        return jsonify({
            "success": True,
            "parsed_stats": parsed_data,
            "raw_text": text
        })
    except Exception as e:
        # **NYT: Print den fulde fejl-traceback til Render's logs**
        print("En fejl opstod under billedbehandling:")
        print(traceback.format_exc())
        
        # Returner en generel fejl til brugeren
        return jsonify({"error": "Der skete en intern fejl på serveren ved behandling af billedet."}), 500

@app.route('/')
def hello():
    return "FC26 Stats API er online!"

# if __name__ ... delen kan fjernes, da gunicorn starter app'en
