"""Punto de entrada de la aplicacion Flask.

Solo arma la aplicacion y registra las rutas. La logica del negocio vive en
models/ y services/; las vistas no calculan nada.
"""

import os

from flask import Flask

from views.rutas import bp_principal


def create_app() -> Flask:
    """Crea la aplicacion con las carpetas de plantillas y estaticos del proyecto."""
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="public/static",
    )
    app.register_blueprint(bp_principal)
    return app


if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", "5000"))
    create_app().run(host="0.0.0.0", port=puerto)
