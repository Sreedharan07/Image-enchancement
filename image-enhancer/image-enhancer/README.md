# LUMEX — Image Enhancement Studio

A full-stack image enhancement web app built with **Flask** + **Pillow** backend and a dark, professional HTML/CSS/JS frontend.

## Features

| Category | Options |
|---|---|
| **Tone** | Brightness, Contrast, Saturation, Sharpness |
| **Filters** | Blur, Sharpen, Smooth, Detail, Edge Detection, Emboss, Grayscale (B&W), Sepia, Invert, Auto-Contrast, Equalize |
| **Transform** | Flip Horizontal, Flip Vertical, Rotate (±90°) |
| **Resize** | Custom width × height (LANCZOS resampling) |
| **Output** | Adjustable JPEG quality (10–100) |
| **Views** | Original / Enhanced / Split comparison |
| **Download** | One-click download of processed image |

## Supported Formats

PNG · JPG · JPEG · WEBP · BMP · TIFF

## Project Structure

```
image-enhancer/
├── app.py                 # Flask backend + image processing
├── requirements.txt
├── templates/
│   └── index.html         # Full frontend (HTML/CSS/JS)
└── static/
    ├── uploads/           # Uploaded originals (auto-created)
    └── outputs/           # Processed results (auto-created)
```

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the app
```bash
python app.py
```

### 3. Open in browser
```
http://localhost:5000
```

## How to Use

1. **Upload** — Click the canvas or drag & drop an image
2. **Adjust** — Use the left sidebar sliders, filters, and transforms
3. **Enhance** — Click the ⚡ Enhance Image button
4. **Compare** — Switch between Original / Enhanced / Split views
5. **Download** — Click ↓ Download Result to save

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serve the frontend |
| POST | `/upload` | Upload an image, returns metadata |
| POST | `/enhance` | Apply enhancements, returns output URL |
| GET | `/download/<filename>` | Download a processed file |
