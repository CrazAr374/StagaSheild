from flask import Flask, request, render_template, jsonify, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import os
import io
from steganography import embed_message, extract_message
import zipfile
from steganalysis import analyze_image

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'}  # Extended format support

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/stego')  # Changed from '/app' to '/stego'
def stego_app():      # Changed from 'index' to 'stego_app'
    return render_template('index.html')

@app.route('/embed', methods=['POST'])
def embed():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    message = request.form.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    if file and allowed_file(file.filename):
        try:
            image = Image.open(file)
            result_image = embed_message(image, message)
            
            img_io = io.BytesIO()
            result_image.save(img_io, 'PNG')
            img_io.seek(0)
            
            return send_file(img_io, 
                           mimetype='image/png', 
                           as_attachment=True, 
                           download_name='stego_image.png')
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/extract', methods=['POST'])
def extract():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Open and validate image
        image = Image.open(file)
        
        # Try to extract message
        message = extract_message(image)
        
        if not message:
            return jsonify({'error': 'No message found in image'}), 400
        
        return jsonify({'message': message, 'success': True})
    
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to process image. Please try another image.'}), 400

@app.route('/batch-embed', methods=['POST'])
def batch_embed():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400
    
    files = request.files.getlist('images')
    message = request.form.get('message', '')
    
    if not message or not files:
        return jsonify({'error': 'Missing message or files'}), 400
    
    # Create ZIP file for batch download
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    image = Image.open(file)
                    result_image = embed_message(image, message)
                    
                    # Save processed image to memory
                    img_buffer = io.BytesIO()
                    result_image.save(img_buffer, 'PNG')
                    img_buffer.seek(0)
                    
                    # Add to ZIP
                    zip_file.writestr(
                        f'stego_{secure_filename(file.filename)}.png',
                        img_buffer.getvalue()
                    )
                except Exception as e:
                    return jsonify({'error': f'Error processing {file.filename}: {str(e)}'}), 400
    
    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='stego_images.zip'
    )

@app.route('/batch-extract', methods=['POST'])
def batch_extract():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400
    
    files = request.files.getlist('images')
    messages = []
    
    for file in files:
        if file and allowed_file(file.filename):
            try:
                image = Image.open(file)
                message = extract_message(image)
                messages.append({
                    'filename': file.filename,
                    'message': message
                })
            except Exception as e:
                messages.append({
                    'filename': file.filename,
                    'error': str(e)
                })
    
    return jsonify({'results': messages})

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    
    file = request.files['image']
    
    if file and allowed_file(file.filename):
        try:
            image = Image.open(file)
            analysis_result = analyze_image(image)
            return jsonify(analysis_result)
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)
