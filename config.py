import os
from datetime import timedelta

class Config:
    # Basic Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DEBUG = False
    TESTING = False
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join('static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Model Configuration
    MODEL_PATH = os.path.join('models', 'ear_model.h5')
    MODEL_INPUT_SIZE = (224, 224)
    DISEASE_CLASSES = [
        'Normal',
        'Acute Otitis Media',
        'Chronic Otitis Media',
        'Earwax',
        'Otitis Externa'
    ]
    
    # Session Configuration
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Security Configuration
    CSRF_ENABLED = True
    
    # API Configuration
    API_RATE_LIMIT = '100 per minute'
    
    # Cache Configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Database Configuration (if needed)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///ear_disease.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    
    # Development-specific settings
    SESSION_COOKIE_SECURE = False
    
    # Enable more detailed error messages
    PROPAGATE_EXCEPTIONS = True
