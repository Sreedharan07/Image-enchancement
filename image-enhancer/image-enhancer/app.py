from flask import Flask, request, jsonify, send_from_directory, render_template
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import os
import uuid
import numpy as np

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
OUTPUT_FOLDER = 'static/outputs'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'bmp', 'tiff'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def apply_enhancements(img, options):
    """Apply a chain of enhancements based on user options."""

    # Brightness
    brightness = float(options.get('brightness', 1.0))
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)

    # Contrast
    contrast = float(options.get('contrast', 1.0))
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)

    # Saturation
    saturation = float(options.get('saturation', 1.0))
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)

    # Sharpness
    sharpness = float(options.get('sharpness', 1.0))
    if sharpness != 1.0:
        img = ImageEnhance.Sharpness(img).enhance(sharpness)

    # Filters
    filter_type = options.get('filter', 'none')

    if filter_type == 'blur':
        radius = float(options.get('blur_radius', 2))
        img = img.filter(ImageFilter.GaussianBlur(radius=radius))

    elif filter_type == 'sharpen':
        img = img.filter(ImageFilter.SHARPEN)

    elif filter_type == 'edge':
        img = img.filter(ImageFilter.FIND_EDGES)

    elif filter_type == 'emboss':
        img = img.filter(ImageFilter.EMBOSS)

    elif filter_type == 'smooth':
        img = img.filter(ImageFilter.SMOOTH_MORE)

    elif filter_type == 'detail':
        img = img.filter(ImageFilter.DETAIL)

    elif filter_type == 'grayscale':
        img = ImageOps.grayscale(img).convert('RGB')

    elif filter_type == 'sepia':
        img = ImageOps.grayscale(img).convert('RGB')
        arr = np.array(img, dtype=np.float64)
        r = np.clip(arr[:, :, 0] * 0.393 + arr[:, :, 1] * 0.769 + arr[:, :, 2] * 0.189, 0, 255)
        g = np.clip(arr[:, :, 0] * 0.349 + arr[:, :, 1] * 0.686 + arr[:, :, 2] * 0.168, 0, 255)
        b = np.clip(arr[:, :, 0] * 0.272 + arr[:, :, 1] * 0.534 + arr[:, :, 2] * 0.131, 0, 255)
        sepia = np.stack([r, g, b], axis=2).astype(np.uint8)
        img = Image.fromarray(sepia)

    elif filter_type == 'invert':
        img = ImageOps.invert(img)

    elif filter_type == 'autocontrast':
        img = ImageOps.autocontrast(img)

    elif filter_type == 'equalize':
        img = ImageOps.equalize(img)

    # Rotation
    rotation = int(options.get('rotation', 0))
    if rotation != 0:
        img = img.rotate(-rotation, expand=True)

    # Flip
    flip_h = options.get('flip_h') == 'true'
    flip_v = options.get('flip_v') == 'true'
    if flip_h:
        img = ImageOps.mirror(img)
    if flip_v:
        img = ImageOps.flip(img)

    # Resize
    resize_w = options.get('resize_w', '')
    resize_h = options.get('resize_h', '')
    if resize_w and resize_h:
        try:
            w, h = int(resize_w), int(resize_h)
            img = img.resize((w, h), Image.LANCZOS)
        except Exception:
            pass

    return img


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    img = Image.open(filepath)
    w, h = img.size
    mode = img.mode
    size_kb = round(os.path.getsize(filepath) / 1024, 1)

    return jsonify({
        'filename': filename,
        'width': w,
        'height': h,
        'mode': mode,
        'size_kb': size_kb,
        'url': f'/static/uploads/{filename}'
    })


@app.route('/enhance', methods=['POST'])
def enhance():
    data = request.json
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename'}), 400

    src = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(src):
        return jsonify({'error': 'File not found'}), 404

    try:
        img = Image.open(src).convert('RGB')
        img = apply_enhancements(img, data)

        out_name = f"enhanced_{uuid.uuid4().hex}.jpg"
        out_path = os.path.join(OUTPUT_FOLDER, out_name)
        quality = int(data.get('quality', 92))
        img.save(out_path, 'JPEG', quality=quality)

        w, h = img.size
        size_kb = round(os.path.getsize(out_path) / 1024, 1)

        return jsonify({
            'url': f'/static/outputs/{out_name}',
            'filename': out_name,
            'width': w,
            'height': h,
            'size_kb': size_kb
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/download/<path:filename>')
def download(filename):
    folder = OUTPUT_FOLDER if filename.startswith('enhanced_') else UPLOAD_FOLDER
    return send_from_directory(folder, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
