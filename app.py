from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compress', methods=['POST'])
def compress():
    file = request.files['image']
    size = request.form.get('size')
    print(f"Selected size range: {size}")
    try:
        image = Image.open(file)
        format = 'jpeg' if image.format.lower() == 'jpg' else image.format.lower()  
        if image.mode == 'RGBA':
            image = image.convert('RGB')
    
        size_ranges = {
            '1-50': (1 * 1024, 50 * 1024, 60),
            '100-500': (100 * 1024, 500 * 1024, 70),
            '500kb-1mb': (500 * 1024, 1 * 1024 * 1024, 80),
            '1mb-3mb': (1 * 1024 * 1024, 3 * 1024 * 1024, 85)
        }
        target_size = size_ranges.get(size)
        
        if not target_size:
            print(f"Invalid size range selected: {size}")
            return "Invalid size range", 400
        
        min_size, max_size, initial_quality = target_size
        quality = initial_quality
        
        # Resize the image if necessary
        while True:
            compressed_io = io.BytesIO()
            image.save(compressed_io, format=format, quality=quality, optimize=True)
            compressed_io_size = compressed_io.tell()
            print(f"Current size: {compressed_io_size} bytes, Target size range: {min_size}-{max_size} bytes, Quality: {quality}")
            if min_size <= compressed_io_size <= max_size:
                break
            quality -= 5  
            if quality < 10:  
               
                width, height = image.size
                image = image.resize((int(width * 0.9), int(height * 0.9)), Image.LANCZOS)
                quality = initial_quality  

        compressed_io.seek(0)
        return send_file(compressed_io, mimetype=f'image/{format}', as_attachment=True, attachment_filename=f'compressed_image.{format}')

    except Exception as e:
        print(f"Error: {e}")
        return str(e), 400
    
@app.route('/complain')
def complain():
    return render_template('complain.html')

if __name__ == '__main__':
    app.run(debug=True)























