# Resultados de intermediarios de seguros

Automatizacion del proceso trimestral: entrar a los enlaces de los intermediarios,
descargar los estados financieros en PDF, leerlos y agregar los valores al historico
en `resultados/`.

La fuente de verdad del proyecto es [`AGENTS.md`](AGENTS.md).

## Estado actual

**Esqueleto de despliegue.** La aplicacion arranca y responde, pero la descarga de
PDF, la lectura de los estados financieros y la carga al historico todavia no estan
construidas. Esta version sirve para validar el despliegue y el entorno.

Rutas disponibles:

| Metodo | Ruta | Descripcion |
|---|---|---|
| `GET` | `/` | Pantalla de inicio con el estado del despliegue |
| `GET` | `/salud` | Verificacion de vida (`{"estado": "ok"}`) |

## Requisitos

- [uv](https://docs.astral.sh/uv/) (instala Python 3.12 por su cuenta)

## Correr en local

```bash
uv sync
uv run flask --app app run --host 0.0.0.0 --port 5000
```

Abrir `http://localhost:5000`.

## Desplegar en Render

### Opcion A: Blueprint (recomendada)

1. En Render: **New > Blueprint**.
2. Conectar el repositorio `nathasjm97/InformesFinancieros` (rama `master`).
   Render lee `render.yaml` y crea el servicio.
3. Aplicar.

### Opcion B: Web Service manual

| Campo | Valor |
|---|---|
| Environment | `Python` |
| Build Command | `pip install uv && uv sync --frozen --no-dev` |
| Start Command | `uv run gunicorn "app:create_app()" --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
| Health Check Path | `/salud` |

Variable de entorno:

| Variable | Valor |
|---|---|
| `PYTHON_VERSION` | `3.12` |

### Como saber que el despliegue quedo bien

1. El registro de build termina con `uv sync` sin errores y crea `.venv`.
2. `https://<servicio>.onrender.com/salud` devuelve `{"estado":"ok"}`.
3. La pantalla de inicio muestra `Version de Python 3.12.x`, `Sistema Linux` y el
   puerto asignado. Si el sistema dice `Windows`, se desplego desde la maquina local
   y no desde Render.

## Estructura

```
app.py                     Punto de entrada (fabrica create_app)
views/rutas.py             Rutas HTTP, delegan en los controllers
views/templates/           Plantillas Jinja
controllers/               Reciben la peticion y orquestan
services/                  Descarga de PDF, extraccion, escritura del CSV
models/                    Entidades y reglas del negocio
data/                      Unica capa que abre archivos
public/static/             Estilos e imagenes
insumos/                   Links.txt y PDFs descargados
resultados/                CSV historico (entregable)
```

## Advertencia sobre los datos

Render usa **disco efimero**: todo lo que la aplicacion escriba en `insumos/` o
`resultados/` se pierde en cada despliegue o reinicio. Mientras el historico viva en
el repositorio, el CSV se conserva; cuando la app empiece a escribir filas nuevas,
hace falta un disco persistente o un almacenamiento externo.
