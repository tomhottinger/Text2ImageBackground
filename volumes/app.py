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

        

        # Neue Parameter für Background-Box

        bg_color = request.form.get('bg_color', '#000000')

        bg_opacity = int(request.form.get('bg_opacity', 128))  # 0-255

        bg_blur = int(request.form.get('bg_blur', 10))

        bg_padding = int(request.form.get('bg_padding', 20))

        bg_radius = int(request.form.get('bg_radius', 15))

        

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

        bg_color_rgb = tuple(int(bg_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

        

        # Verarbeite mehrzeiligen Text

        lines = text.split('\n')

        

        # Berechne Dimensionen für mehrzeiligen Text

        draw = ImageDraw.Draw(txt_layer)

        line_height = font_size + 10  # Zusätzlicher Zeilenabstand

        

        # Berechne Breite und Höhe des Textblocks

        max_width = 0

        total_height = 0

        line_bboxes = []

        

        for line in lines:

            bbox = draw.textbbox((0, 0), line, font=font)

            line_width = bbox[2] - bbox[0]

            line_height_actual = bbox[3] - bbox[1]

            max_width = max(max_width, line_width)

            line_bboxes.append((line_width, line_height_actual))

            total_height += line_height

        

        # Berechne Position des Textblocks

        if position == 'center':

            x = (img.size[0] - max_width) // 2 + x_offset

            y = (img.size[1] - total_height) // 2 + y_offset

        elif position == 'top':

            x = (img.size[0] - max_width) // 2 + x_offset

            y = 20 + y_offset

        elif position == 'bottom':

            x = (img.size[0] - max_width) // 2 + x_offset

            y = img.size[1] - total_height - 20 + y_offset

        elif position == 'top-left':

            x = 20 + x_offset

            y = 20 + y_offset

        elif position == 'top-right':

            x = img.size[0] - max_width - 20 + x_offset

            y = 20 + y_offset

        elif position == 'bottom-left':

            x = 20 + x_offset

            y = img.size[1] - total_height - 20 + y_offset

        elif position == 'bottom-right':

            x = img.size[0] - max_width - 20 + x_offset

            y = img.size[1] - total_height - 20 + y_offset

        

        # Berechne Background-Box Dimensionen

        box_x1 = x - bg_padding

        box_y1 = y - bg_padding

        box_x2 = x + max_width + bg_padding

        box_y2 = y + total_height + bg_padding

        

        # Erstelle Blur-Effekt durch Cropping und Blurring des Originalbildes

        if bg_blur > 0:

            # Schneide den Bereich aus, der geblurred werden soll

            box_region = img.crop((max(0, box_x1), max(0, box_y1), 

                                  min(img.size[0], box_x2), min(img.size[1], box_y2)))

            

            # Blur den Bereich

            from PIL import ImageFilter

            blurred_region = box_region.filter(ImageFilter.GaussianBlur(radius=bg_blur))

            

            # Erstelle eine Maske für abgerundete Ecken

            mask = Image.new('L', blurred_region.size, 0)

            mask_draw = ImageDraw.Draw(mask)

            mask_draw.rounded_rectangle(

                [(0, 0), (blurred_region.size[0], blurred_region.size[1])],

                radius=bg_radius,

                fill=255

            )

            

            # Füge den geblurrten Bereich zurück ins Bild mit Maske

            img.paste(blurred_region, (max(0, box_x1), max(0, box_y1)), mask)

        

        # Zeichne semi-transparente farbige Box mit abgerundeten Ecken

        draw_overlay = ImageDraw.Draw(txt_layer)

        draw_overlay.rounded_rectangle(

            [(box_x1, box_y1), (box_x2, box_y2)],

            radius=bg_radius,

            fill=bg_color_rgb + (bg_opacity,)

        )

        

        # Zeichne Text Zeile für Zeile mit Outline

        current_y = y

        outline_color = (0, 0, 0, 200)

        

        for i, line in enumerate(lines):

            # Zentriere jede Zeile innerhalb der Box

            line_width = line_bboxes[i][0]

            line_x = x + (max_width - line_width) // 2

            

            # Zeichne Outline

            for adj_x in range(-2, 3):

                for adj_y in range(-2, 3):

                    draw_overlay.text((line_x + adj_x, current_y + adj_y), line, font=font, fill=outline_color)

            

            # Zeichne Text

            draw_overlay.text((line_x, current_y), line, font=font, fill=text_color_rgb + (255,))

            current_y += line_height

        

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
