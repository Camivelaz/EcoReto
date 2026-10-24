import os
import sqlite3
from flask import Flask

def create_app():
    app = Flask(
        __name__,
        template_folder='../templates',
        static_folder='../static'
    )

    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "eco-reto-clave-local"
    )

    app.config["DATABASE"] = os.path.join(
        app.root_path, "eco_reto.db"
    )

    os.makedirs(app.instance_path, exist_ok=True)

    with sqlite3.connect(app.config["DATABASE"]) as conexion:
        conexion.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL
            )
        """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS acciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha TEXT NOT NULL,
                impacto REAL NOT NULL,
                unidad TEXT NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

    from app.routes import rutas
    app.register_blueprint(rutas)

    return app