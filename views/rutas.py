"""Rutas HTTP de la aplicacion.

Cada ruta recibe la peticion y delega en un controller. Aqui no se calcula nada.
"""

from flask import Blueprint

from controllers.proceso_controller import mostrar_inicio, responder_salud

bp_principal = Blueprint("principal", __name__)


@bp_principal.get("/")
def inicio():
    """Pagina de inicio del proceso trimestral."""
    return mostrar_inicio()


@bp_principal.get("/salud")
def salud():
    """Verificacion de vida para el despliegue."""
    return responder_salud()
