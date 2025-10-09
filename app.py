from flask import Flask, render_template, request, send_file, jsonify

from PIL import Image, ImageDraw, ImageFont

import io

import os

from pathlib import Path



app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = 'uploads'

app.config['SAMPLE_IMAGES'] = 'sample_images'



# Erstelle notwendige Ordner

Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)

Path(app.config['SAMPLE_IMAGES']).mkdir(exist_ok=True)



@app.route('/')

def index():

    # Liste verfügbare Sample-Bilder

    sample_images = []

    if os.path.exists(app.config['SAMPLE_IMAGES']):

        sample_images = [f for f in os.listdir(app.config['SAMPLE_IMAGES']) 

                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    

    return render_template('index.html', sample_images=sample_images)



@app.route('/sample_image/<filename>')

def sample_image(filename):

    """Serve sample images"""

    return send_file(os.path.join(app.config['SAMPLE_IMAGES'], filename))



@app.route('/process', methods=['POST'])

def process_image():

    try:

        # Hole Parameter

        text = request.form.get('text', 'Sample Text')

        font_size = int(request.form.get('font_size', 40))

        text_color = request.form.get('text_color', '#FFFFFF')

        position = request.form.get('position', 'center')

        x_offset = int(request.form.get('x_offset', 0))

        y_offset = int(request.form.get('y_offset', 0))

        

        # Lade Bild

        if 'image' in request.files and request.files['image'].filename:

            # Upload-Bild

            file = request.files['image']

            img = Image.open(file.stream).convert('RGBA')

        elif 'sample_image' in request.form:

            # Sample-Bild

            sample_name = request.form.get('sample_image')

            img_path = os.path.join(app.config['SAMPLE_IMAGES'], sample_name)

            img = Image.open(img_path).convert('RGBA')

        else:

            return jsonify({'error': 'Kein Bild ausgewählt'}), 400

        

        # Erstelle transparenten Overlay-Layer

        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))

        draw = ImageDraw.Draw(txt_layer)

        

        # Lade Font (Fallback auf default wenn nicht vorhanden)

        try:

            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)

        except:

            font = ImageFont.load_default()

        

        # Konvertiere Hex-Farbe zu RGB

        text_color_rgb = tuple(int(text_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        

        # Berechne Text-Position

        bbox = draw.textbbox((0, 0), text, font=font)

        text_width = bbox[2] - bbox[0]

        text_height = bbox[3] - bbox[1]

        

        if position == 'center':

            x = (img.size[0] - text_width) // 2 + x_offset

            y = (img.size[1] - text_height) // 2 + y_offset

        elif position == 'top':

            x = (img.size[0] - text_width) // 2 + x_offset

            y = 20 + y_offset

        elif position == 'bottom':

            x = (img.size[0] - text_width) // 2 + x_offset

            y = img.size[1] - text_height - 20 + y_offset

        elif position == 'top-left':

            x = 20 + x_offset

            y = 20 + y_offset

        elif position == 'top-right':

            x = img.size[0] - text_width - 20 + x_offset

            y = 20 + y_offset

        elif position == 'bottom-left':

            x = 20 + x_offset

            y = img.size[1] - text_height - 20 + y_offset

        elif position == 'bottom-right':

            x = img.size[0] - text_width - 20 + x_offset

            y = img.size[1] - text_height - 20 + y_offset

        

        # Zeichne Text mit Outline für bessere Lesbarkeit

        outline_color = (0, 0, 0, 200)

        for adj_x in range(-2, 3):

            for adj_y in range(-2, 3):

                draw.text((x + adj_x, y + adj_y), text, font=font, fill=outline_color)

        

        draw.text((x, y), text, font=font, fill=text_color_rgb + (255,))

        

        # Kombiniere Bilder

        result = Image.alpha_composite(img, txt_layer)

        result = result.convert('RGB')

        

        # Speichere in Memory

        img_io = io.BytesIO()

        result.save(img_io, 'JPEG', quality=95)

        img_io.seek(0)

        

        return send_file(img_io, mimetype='image/jpeg', as_attachment=True, 

                        download_name='image_with_text.jpg')

    

    except Exception as e:

        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=False)
