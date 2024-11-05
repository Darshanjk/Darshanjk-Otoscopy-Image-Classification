from flask import Flask, render_template, request, jsonify, current_app
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import logging
from werkzeug.utils import secure_filename
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
class Config:
    UPLOAD_FOLDER = Path('static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    MODEL_PATH = Path('models/my_model.h5')

app.config.from_object(Config)

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load model
try:
    logger.info("Loading model...")
    model = tf.keras.models.load_model(Config.MODEL_PATH)
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    model = None

# Disease classes
DISEASE_CLASSES = [
    'aom',
    'csom',
    'earVentilationTube',
    'earwax',
    'foreignObjectEar',
    'normal',
    'otitisexterna',
    'pseudoMembranes',
    'tympanoskleros',

]

def allowed_file(filename: str) -> bool:
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def preprocess_image(image_path: Path) -> tf.Tensor:
    """
    Preprocess image using TensorFlow operations with error handling
    """
    try:
        logger.debug(f"Processing image: {image_path}")
        
        # Read and verify image
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize image
            img = img.resize((224, 224))
            
            # Convert to numpy array
            img_array = np.array(img)
            
            # Normalize
            img_array = img_array.astype(np.float32) / 255.0
            
            # Add batch dimension
            img_array = np.expand_dims(img_array, axis=0)
            
            logger.debug("Image preprocessing completed successfully")
            return img_array

    except Exception as e:
        logger.error(f"Error in image preprocessing: {e}")
        raise ValueError(f"Error processing image: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    logger.debug("Prediction request received")
    
    if not model:
        logger.error("Model not loaded")
        return jsonify({'error': 'Model not loaded'}), 500

    if 'file' not in request.files:
        logger.error("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    if not file or not allowed_file(file.filename):
        logger.error("Invalid file type")
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        # Save file
        filename = secure_filename(file.filename)
        filepath = app.config['UPLOAD_FOLDER'] / filename
        file.save(filepath)
        logger.debug(f"File saved to {filepath}")

        # Preprocess image
        img_array = preprocess_image(filepath)
        logger.debug("Image preprocessed successfully")

        # Make prediction
        logger.debug("Making prediction...")
        predictions = model.predict(img_array, verbose=0)
        
        # Get prediction results
        predicted_class_index = np.argmax(predictions[0])
        predicted_class = DISEASE_CLASSES[predicted_class_index]
        confidence = float(predictions[0][predicted_class_index]) * 100

        logger.debug(f"Prediction successful: {predicted_class} ({confidence}%)")

        return jsonify({
            'prediction': predicted_class,
            'confidence': confidence,
            'image_path': str(Path('uploads') / filename)
        })

    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Check for GPU availability
    physical_devices = tf.config.list_physical_devices('GPU')
    if physical_devices:
        logger.info("GPU is available:")
        for device in physical_devices:
            logger.info(f" - {device}")
    else:
        logger.info("No GPU available, using CPU")

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5004)
