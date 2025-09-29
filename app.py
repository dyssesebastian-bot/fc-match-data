# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS  # Vigtigt for at tillade requests fra Simply.com
import pytesseract
from PIL import Image
import io
import re

app = Flask(__name__)
CORS(app) # Tillader requests fra alle domæner. Kan begrænses senere.

# Funktion til at parse teksten. Denne skal du selv finjustere!
def parse_stats(text):
    stats = {}
    
    # Prøv at finde "Boldbesiddelse 55 % 45 %"
    try:
        match = re.search(r"Boldbesiddelse\s*(\d+)\s*%\s*(\d+)\s*%", text, re.IGNORECASE)
        if match:
            stats['hjemme_boldbesiddelse'] = int(match.group(1))
            stats['ude_boldbesiddelse'] = int(match.group(2))
    except Exception as e:
        print(f"Fejl ved parsing af boldbesiddelse: {e}")

    # Prøv at finde scoren, f.eks. "2 - 1"
    # Denne er svær, da tallene kan stå alene. Kig efter mønstre.
    # Denne regex er kun et gæt og skal sikkert justeres!
    try:
        match = re.search(r"(\d+)\s*-\s*(\d+)", text)
        if match:
            # Her antager vi, at det første match for "X - Y" er scoren.
            stats['hjemme_mål'] = int(match.group(1))
            stats['ude_mål'] = int(match.group(2))
    except Exception as e:
        print(f"Fejl ved parsing af mål: {e}")

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
        return jsonify({"error": str(e)}), 500

# En simpel "velkomst"-side så du kan se, at serveren kører
@app.route('/')
def hello():
    return "FC26 Stats API er online!"

if __name__ == '__main__':
    app.run(debug=True)
