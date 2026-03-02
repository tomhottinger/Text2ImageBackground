# ImgOverlay

Eine kleine Flask-Webapp, um Text mit konfigurierbarer Hintergrund-Box auf Bilder zu legen und als JPG herunterzuladen.

## Funktionen

- Bildquelle: Upload oder Auswahl aus vorhandenen `sample_images`
- Mehrzeiliger Text mit automatischem Zeilenumbruch
- Schriftart-Auswahl aus `volumes/fonts/*.ttf`
- Einstellbar: Schriftgröße, Textfarbe, Position, Textausrichtung, X/Y-Offset
- Hintergrund-Box: Farbe, Transparenz, Blur, Padding, Eckenradius, Box-Breite (%)
- Vorschau im Browser + Download als JPG
- Share/Preset-URL mit aktuellen Parametern
- Passwortgeschützter Upload neuer Sample-Bilder (`/upload_sample`)

## Tech Stack

- Backend: Python 3.11, Flask, Pillow
- WSGI/Prod-Server: Gunicorn
- Frontend: serverseitiges HTML (Jinja2), Vanilla JS, CSS
- Container: Docker + Docker Compose

## Installation

### Option A: Mit Docker Compose (empfohlen)

1. `.env` anlegen:
```bash
cp .env.example .env
```

2. Passwort setzen:
```env
UPLOAD_PASSWORD=dein_starkes_passwort
```

3. Starten:
```bash
docker compose up -d --build
```

4. App öffnen:
- lokal typischerweise unter `http://localhost:5000` (je nach Umgebung/Proxy)
- in dieser Compose-Datei ist Traefik-Integration konfiguriert

### Option B: Lokal ohne Docker

1. Virtuelle Umgebung + Dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start aus dem `volumes`-Verzeichnis (wichtig für relative Pfade):
```bash
cd volumes
export UPLOAD_PASSWORD=dein_starkes_passwort
python app.py
```

3. App öffnen: `http://localhost:5000`

## Bedienung

1. Bild hochladen oder ein Sample-Bild auswählen.
2. Text eingeben (mehrere Zeilen möglich).
3. Schrift, Farben, Position und Box-Parameter einstellen.
4. `Vorschau erstellen` klicken.
5. Ergebnis mit `Bild herunterladen` speichern.
6. Optional: über das Zahnrad oben rechts neue Sample-Bilder hochladen (Passwort benötigt).

## API / Routen

- `GET /`  
  Rendered die Hauptseite mit verfügbaren Samples und Fonts.

- `GET /sample_image/<filename>`  
  Liefert Sample-Bilder aus `sample_images`.

- `POST /process`  
  Nimmt Formdaten entgegen, rendert Overlay mit Pillow und liefert ein JPG zurück.

- `POST /upload_sample`  
  Passwortgeschützter Upload von Sample-Bildern.

## Code und Architektur

### 1) Backend (`volumes/app.py`)

- Flask-App mit zentraler Konfiguration (`UPLOAD_FOLDER`, `SAMPLE_IMAGES`, `FONTS_FOLDER`, `MAX_CONTENT_LENGTH`, etc.)
- Font-Erkennung via Scan von `fonts/*.ttf`
- Bildpipeline in `/process`:
  - Eingabebild laden (Upload oder Sample)
  - Text umbrechen (maximale Breite abhängig von Box-Breite in %)
  - Textblock-Position berechnen
  - optionalen Blur im Box-Bereich anwenden
  - semitransparente Rounded-Rectangle zeichnen
  - Text mit Outline rendern
  - Ergebnis als JPEG im Memory-Stream zurückgeben

### 2) Frontend (`volumes/templates` + `volumes/static`)

- `index.html` enthält Formular, Vorschaubereich, URL-Box und Admin-Modal
- `app.js`:
  - initialisiert Formularzustand aus URL-Parametern
  - erzeugt laufend Share-URL
  - sendet Formular per `fetch('/process')`
  - zeigt Preview an und steuert Download
  - verarbeitet Sample-Uploads (`/upload_sample`)
- `style.css` liefert Layout/Modal/Form-Styling

### 3) Deployment

- `Dockerfile` nutzt `python:3.11-slim`, installiert Requirements, startet Gunicorn
- `docker-compose.yml` mountet Quellcode und Assets aus `./volumes/*` in den Container
- Compose enthält Traefik-Labels für Reverse Proxy/TLS-Middleware

## Directory Layout

```text
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── templates/                  # optional/leer im aktuellen Stand
├── uploads/                    # optional/legacy im Root
└── volumes/
    ├── app.py                  # Flask-Backend
    ├── templates/
    │   └── index.html          # Hauptseite (Jinja2)
    ├── static/
    │   ├── css/style.css       # Styling
    │   └── js/app.js           # Frontend-Logik
    ├── fonts/                  # .ttf-Schriften für Auswahl im UI
    ├── sample_images/          # auswählbare Beispielbilder
    └── uploads/                # Upload-Ziel (falls verwendet)
```

## Konfiguration

- `UPLOAD_PASSWORD` (Env-Variable): Passwort für `/upload_sample`
- `MAX_CONTENT_LENGTH`: derzeit 16 MB pro Upload
- `ALLOWED_EXTENSIONS`: `png`, `jpg`, `jpeg`, `gif`, `webp`

## Hinweise

- Die App speichert das Ergebnis nicht serverseitig dauerhaft, sondern liefert das verarbeitete Bild direkt als Response.
- Für Produktion Passwort ändern und Zugriff auf Upload-Funktion zusätzlich absichern (z. B. Reverse-Proxy Auth).
