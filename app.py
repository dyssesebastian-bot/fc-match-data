# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import io
import re
import traceback

# ======================= VIGTIG RETTELSE =======================
# Fortæl pytesseract præcis hvor Tesseract-programmet er installeret på Render's server.
# Dette løser 'TesseractNotFoundError'.
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
# ===============================================================

app = Flask(__name__)

# Opsæt CORS for at tillade anmodninger fra din hjemmeside.
# '*' tillader alle domæner - for bedre sikkerhed kan du erstatte det
# med dit specifikke domæne, f.eks. "http://sebastianviste.com"
CORS(app, resources={r"/upload": {"origins": "*"}})

def parse_stats(text):
    """
    Analyser den rå tekst fra OCR for at finde specifikke kampstatistikker.
    Denne funktion er den, du skal finjustere mest, efterhånden som du ser
    resultater fra forskellige screenshots.
    """
    stats = {}
    
    # Eksempel 1: Find "Boldbesiddelse 55 % 45 %"
    try:
        match = re.search(r"Boldbesiddelse\s*(\d+)\s*%\s*(\d+)\s*%", text, re.IGNORECASE)
        if match:
            stats['hjemme_boldbesiddelse'] = int(match.group(1))
            stats['ude_boldbesiddelse'] = int(match.group(2))
    except Exception as e:
        print(f"Kunne ikke parse boldbesiddelse: {e}")

    # Eksempel 2: Find "Skud på mål" - dette mønster skal justeres til dit screenshot
    # Antager et mønster som "Skud på mål 5(10) 3(7)"
    try:
        match = re.search(r"Skud på mål\s*(\d+)\s*\((\d+)\)\s*(\d+)\s*\((\d+)\)", text, re.IGNORECASE)
        if match:
            stats['hjemme_skud_på_mål'] = int(match.group(1))
            stats['hjemme_skud_total'] = int(match.group(2))
            stats['ude_skud_på_mål'] = int(match.group(3))
            stats['ude_skud_total'] = int(match.group(4))
    except Exception as e:
        print(f"Kunne ikke parse skud på mål: {e}")
        
    # Tilføj flere regex-regler her for andre statistikker (hjørnespark, frispark etc.)

    return stats


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint der modtager et billede, kører OCR, parser resultatet
    og returnerer de fundne data.
    """
    if 'screenshot' not in request.files:
        return jsonify({"error": "Ingen fil vedhæftet i 'screenshot' feltet"}), 400

    file = request.files['screenshot']
    if not file or file.filename == '':
        return jsonify({"error": "Ingen fil valgt"}), 400

    try:
        # Åbn billedet direkte fra upload-streamen
        image = Image.open(file.stream)
        
        # Kør Tesseract OCR på billedet med dansk sprogpakke
        text = pytesseract.image_to_string(image, lang='dan')
        
        # Parse den udtrukne tekst
        parsed_data = parse_stats(text)
        
        # Returner et succesfuldt svar med de fundne data
        return jsonify({
            "success": True,
            "parsed_stats": parsed_data,
            "raw_text": text  # Inkluderer rå tekst, super nyttigt til debugging!
        })

    except Exception as e:
        # Hvis noget går galt i 'try'-blokken, log den fulde fejl på serveren
        print("En fejl opstod under billedbehandling:")
        print(traceback.format_exc())
        
        # Returner en generel og brugervenlig fejl til frontend'en
        return jsonify({"error": "Der skete en intern fejl på serveren ved behandling af billedet."}), 500


@app.route('/')
def hello():
    """
    En simpel forside-route for at tjekke om serveren er online
    og til Render's health checks.
    """
    return "FC26 Stats API er online og klar til at modtage uploads!"


# Den følgende del (`if __name__ == '__main__':`) er ikke nødvendig,
# når man bruger Gunicorn på Render, men den skader ikke at have med.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
