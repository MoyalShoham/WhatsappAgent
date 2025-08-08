# settings.py

import os

class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    WHATSAPP_API_URL = os.getenv('WHATSAPP_API_URL')
    WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')
    DATABASE_URL = os.getenv('DATABASE_URL')

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True

class ProductionConfig(Config):
    """Production configuration."""
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}