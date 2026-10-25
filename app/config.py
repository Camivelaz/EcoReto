import os

# Toma la URL de la base de datos de Render
DATABASE_URL = os.environ.get('DATABASE_URL')

# Clave secreta
SECRET_KEY = os.environ.get('SECRET_KEY', 'ecoreto-key')
