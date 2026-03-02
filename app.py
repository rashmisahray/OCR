import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from core.engine import OCREngine

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize OCR Engine
tesseract_exe = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
tessdata_path = os.path.join(os.path.dirname(__file__), 'tessdata')
ocr_engine = OCREngine(tesseract_path=tesseract_exe, tessdata_dir=tessdata_path)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Render the main application page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_upload():
    """Handle image uploads and perform OCR processing."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Empty filename'})
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        try:
            # Extract text using the core engine
            extracted_text = ocr_engine.extract_text(save_path)
            
            return jsonify({
                'success': True,
                'text': extracted_text or "No text recognized. Please try a clearer image."
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
        finally:
            # Optional: Keep or Delete uploaded files based on preference
            # os.remove(save_path)
            pass
            
    return jsonify({'success': False, 'error': 'Unsupported file format'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
