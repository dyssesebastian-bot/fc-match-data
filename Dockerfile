# Start med et officielt Python-image
FROM python:3.9-slim

# Sæt en arbejdsm mappe
WORKDIR /app

# Opdater systemet og installer Tesseract og den danske sprogpakke
# -y bekræfter automatisk installationen
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-dan \
    && rm -rf /var/lib/apt/lists/*

# Kopier filen med Python-pakker
COPY requirements.txt .

# Installer Python-pakkerne
RUN pip install --no-cache-dir -r requirements.txt

# Kopier resten af din app-kode ind i containeren
COPY . .

# Fortæl Docker hvilken kommando der skal køres, når containeren starter
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
