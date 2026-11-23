"""Recibe las peticiones y delega. No aplica reglas del negocio."""

import os
import platform

from flask import jsonify, render_template

# Valores de presentacion mientras la extraccion no esta construida.
ULTIMO_TRIMESTRE_PENDIENTE = "Sin procesar"
REGISTROS_EN_PANTALLA = 0


def mostrar_inicio():
    """Muestra la pantalla de inicio con el estado del despliegue."""
    entorno = {
        "python": platform.python_version(),
        "plataforma": platform.system(),
        "puerto": os.environ.get("PORT", "5000"),
    }
    return render_template(
        "index.html",
        entorno=entorno,
        estado={
            "ultimo_trimestre": ULTIMO_TRIMESTRE_PENDIENTE,
            "registros": REGISTROS_EN_PANTALLA,
        },
    )


def responder_salud():
    """Responde la verificacion de vida usada por Render."""
    return jsonify({"estado": "ok"})
