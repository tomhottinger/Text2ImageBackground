# ImgOverlay

A small Flask web app to place text with a configurable background box on images and download the result as JPG.

## Features

- Image source: upload your own file or choose from existing `sample_images`
- Multi-line text with automatic line wrapping
- Font selection from `volumes/fonts/*.ttf`
- Configurable: font size, text color, position, text alignment, X/Y offset
- Background box settings: color, opacity, blur, padding, corner radius, box width (%)
- Browser preview + JPG download
- Share/preset URL with current parameters
- Password-protected upload of new sample images (`/upload_sample`)

## Tech Stack

- Backend: Python 3.11, Flask, Pillow
- WSGI/prod server: Gunicorn
- Frontend: server-rendered HTML (Jinja2), Vanilla JS, CSS
- Container: Docker + Docker Compose

## Installation

### Option A: Docker Compose (recommended)

1. Create `.env`:
```bash
cp .env.example .env
```

2. Set the upload password:
```env
UPLOAD_PASSWORD=your_strong_password
```

3. Start the app:
```bash
docker compose up -d --build
```

4. Open the app:
- usually at `http://localhost:5000` in local setups (depends on your proxy/network setup)
- this compose file also includes Traefik labels for reverse-proxy deployment

### Option B: Local run (without Docker)

1. Create virtual env and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start from the `volumes` directory (important because of relative paths):
```bash
cd volumes
export UPLOAD_PASSWORD=your_strong_password
python app.py
```

3. Open: `http://localhost:5000`

## Usage

1. Upload an image or select a sample image.
2. Enter your text (multiple lines supported).
3. Adjust font, colors, position, and background box settings.
4. Click `Vorschau erstellen` (Create Preview).
5. Save the result with `Bild herunterladen` (Download Image).
6. Optional: use the gear icon (top right) to upload new sample images (password required).

## API / Routes

- `GET /`  
  Renders the main page with available sample images and fonts.

- `GET /sample_image/<filename>`  
  Serves sample images from `sample_images`.

- `POST /process`  
  Accepts form data, renders the text overlay with Pillow, and returns a JPG.

- `POST /upload_sample`  
  Password-protected upload endpoint for new sample images.

## Code and Architecture

### 1) Backend (`volumes/app.py`)

- Flask app with central config (`UPLOAD_FOLDER`, `SAMPLE_IMAGES`, `FONTS_FOLDER`, `MAX_CONTENT_LENGTH`, etc.)
- Font discovery by scanning `fonts/*.ttf`
- Image processing pipeline in `/process`:
  - Load input image (upload or sample)
  - Wrap text (max width based on box width in %)
  - Compute text block position
  - Optionally blur the box area
  - Draw semi-transparent rounded rectangle
  - Render outlined text
  - Return result as in-memory JPEG stream

### 2) Frontend (`volumes/templates` + `volumes/static`)

- `index.html` includes the form, preview area, URL box, and admin modal
- `app.js`:
  - initializes form state from URL parameters
  - continuously updates the share URL
  - submits form data via `fetch('/process')`
  - renders preview and handles download
  - handles sample uploads (`/upload_sample`)
- `style.css` provides layout, modal, and form styling

### 3) Deployment

- `Dockerfile` uses `python:3.11-slim`, installs requirements, and starts Gunicorn
- `docker-compose.yml` mounts source code and assets from `./volumes/*` into the container
- Compose includes Traefik labels for reverse proxy/TLS middleware

## Directory Layout

```text
.
├── Dockerfile
├── docker-compose.yml
├── LICENSE
├── requirements.txt
├── .env.example
├── templates/                  # optional/empty in current state
├── uploads/                    # optional/legacy at repo root
└── volumes/
    ├── app.py                  # Flask backend
    ├── templates/
    │   └── index.html          # main page (Jinja2)
    ├── static/
    │   ├── css/style.css       # styling
    │   └── js/app.js           # frontend logic
    ├── fonts/                  # .ttf fonts available in UI
    ├── sample_images/          # selectable sample images
    └── uploads/                # upload target (if used)
```

## Configuration

- `UPLOAD_PASSWORD` (env var): password for `/upload_sample`
- `MAX_CONTENT_LENGTH`: currently 16 MB per upload
- `ALLOWED_EXTENSIONS`: `png`, `jpg`, `jpeg`, `gif`, `webp`

## Notes

- The app does not persist processed results server-side; it returns the generated image directly in the response.
- For production, change the upload password and protect upload access additionally (for example via reverse-proxy auth).
- Run this application only behind a reverse proxy so it is sufficiently secured.
- `docker-compose.yml` already contains example labels if you want to use Traefik.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
