#config.py
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'construction_materials.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = 'supersecretkey'

KAFKA_BOOTSTRAP_SERVERS = 'localhost:29092'
KAFKA_PRODUCT_TOPIC = 'products'