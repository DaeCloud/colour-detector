from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2
from colorthief import ColorThief
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Allow CORS from the specific origin
CORS(app, resources={r"/*": {"origins": "https://clothes.vps.daecloud.co.za"}})

def isolate_clothing_item(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(image)
        cv2.drawContours(mask, [largest_contour], -1, (255, 255, 255), -1)
        isolated = cv2.bitwise_and(image, mask)
        return isolated
    return image

@app.route('/detect-color', methods=['POST'])
def detect_color():
    data = request.get_json()

    if 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400

    img_data = base64.b64decode(data['image'])
    image_array = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if image is None or image.size == 0:
        return jsonify({"error": "Invalid image data"}), 400

    isolated_image = isolate_clothing_item(image)

    if isolated_image is None or isolated_image.size == 0:
        return jsonify({"error": "No clothing item found"}), 400

    # Convert the isolated image to a Pillow image
    pil_image = Image.fromarray(cv2.cvtColor(isolated_image, cv2.COLOR_BGR2RGB))

    # Use BytesIO instead of a temporary file
    with BytesIO() as output:
        pil_image.save(output, format='PNG')
        output.seek(0)  # Move the cursor to the start of the BytesIO object

        # Use ColorThief with BytesIO (Read from the output)
        color_thief = ColorThief(output)
        dominant_color = color_thief.get_color(quality=1)

    hex_color = "#{:02x}{:02x}{:02x}".format(*dominant_color)

    return jsonify({"color": hex_color})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
