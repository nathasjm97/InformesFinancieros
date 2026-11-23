# AGENTS.md - Automatización de Resultados de Intermediarios Financieros

## 1. Reglas para el agente

- No construir la app todavía: este archivo solo especifica el contrato de arquitectura y negocio.
- Toda extracción de datos debe hacerse desde los PDF de estados financieros publicados en los enlaces de `insumos/Links.txt`.
- No inventar datos. Si un valor no está legible o falta en el PDF, dejarlo vacío en el CSV y registrar el intermediario/trimestre como incompleto.
- Davivienda y DaviBank son el mismo intermediario (fusión/adquisición). Unificar bajo el nombre `DaviBank` en todas las capas.
- No usar datos reales de clientes ni de la empresa. Usar solo los estados financieros públicos de los intermediarios.
- El analista hace este proceso manualmente cada trimestre; la app debe reproducir ese mismo paso a paso sin interpretar criterios de negocio que no estén escritos.
- Si el PDF de un intermediario no se puede descargar o leer, la app debe continuar con los demás y reportar el fallo al final, no detenerse.

## 2. Tecnología

- Gestor de paquetes y entornos: **uv**
- Lenguaje: **Python 3.12**
- Framework web: **Flask**
- Manipulación de datos: **pandas**
- Lenguaje de respuestas al usuario: español

## 3. Arquitectura por capas

| Capa | Responsabilidad | Ejemplo de módulos |
|---|---|---|
| `data` | Lectura/escritura de archivos (CSV de resultados, PDFs descargados, Links.txt) | `data/csv_repo.py`, `data/pdf_downloader.py` |
| `models` | Entidades de dominio (Intermediario, EstadoFinanciero, Trimestre) | `models/intermediario.py`, `models/estado_financiero.py` |
| `services` | Lógica de negocio: descarga PDF, parseo de PDF, extracción de campos, normalización de nombres, escritura al CSV | `services/extractor.py`, `services/normalizador.py`, `services/trimestre_service.py` |
| `controllers` | Recibe peticiones HTTP, orquesta services, devuelve respuestas | `controllers/proceso_controller.py` |
| `views` | Templates Flask (HTML) y rutas de renderizado | `views/templates/*.html`, `views/rutas.py` |

Flujo de una petición: `views/rutas.py` → `controllers/proceso_controller.py` → `services/*` → `models/*` y `data/*`.

## 4. Formato de los insumos

### `insumos/Links.txt`
Archivo de texto con una URL por línea (líneas en blanco ignoradas). Actualmente contiene 2 enlaces:
1. `https://popularseguros.com/documentos-e-informes/estados-financieros-2/`
2. `https://www.baccredomatic.com/es-cr/nuestra-empresa/estados-financieros-no-auditados?title=&year=2026&period=All&category=8276&sort_by=created`

### `insumos/*.PDF`
Uno por intermediario (ej. `BAC IIIT 2026.pdf`, `DAVIbank IIIT 2026.pdf`). Contienen el estado financiero del trimestre vigente. Los campos a extraer (según la guía de negocio) son:
- Ingreso Operativo
- Ingreso por Comisión
- Ingresos Totales
- Gastos Operativos
- Gasto Administrativo
- Gastos Totales
- Utilidad Antes de Impuestos
- Impuesto de Renta y Participación en la Utilidad
- Utilidad Neta
- Activo
- Patrimonio

### `resultados/Intermediarios(query - ...).csv`
Entregable histórico. Características detectadas:
- **Codificación:** Windows-1252 (no UTF-8). Las tildes y la ñ aparecen como `�`.
- **Separador:** `;`
- **Decimales:** coma `,`; **miles:** punto `.`
- **Valores nulos / ausentes:** celdas vacías, `?` al inicio, o `?-   ` (guion con espacios).
- **16 columnas en orden:**
  1. `Título` (año, ej. 2026; a veces con espacio al final, ej. `2018 `)
  2. `Mes` (Marzo, Junio, Septiembre, Diciembre)
  3. `Intermediario` (nombre; variantes: `Confía`/`Conf�a`, `IBG `/`IBG`, `CSS `/`CSS`, `Seguros Metropolitanos `/`Seguros Metropolitanos`)
  4. `Ingreso Operativo`
  5. `Ingreso por Comisión`
  6. `Ingresos Totales`
  7. `Gastos Operativos`
  8. `Gasto Administrativo`
  9. `Gastos Totales`
  10. `Utilidad Antes de Impuestos`
  11. `Impuesto de Renta y Participación en la Utilidad`
  12. `Utilidad Neta`
  13. `Activo`
  14. `Patrimonio`
  15. `Tipo de elemento` (siempre `Elemento`; metadato de SharePoint)
  16. `Ruta de acceso` (siempre `sites/BNCorredora/Planeacion/Lists/IntermediariasdeSeguros`; metadato de SharePoint)

Registros actuales: 1.394 filas de datos (2015–2026). 44 intermediarios distintos. Una fila lógica puede ocupar 2 líneas físicas si contiene salto de línea entre comillas.

## 5. Reglas del negocio

**Proceso trimestral (pasos del analista):**
1. Visitar los sitios web de los intermediarios y Sugese.
2. Validar el período del último reporte publicado.
3. Identificar que el último reporte cargado coincida con el trimestre en consulta.
4. Descargar los archivos de estados financieros.
5. Leer todos los estados de resultados.
6. Identificar la información requerida (comisión, ingresos totales, utilidad neta, patrimonio, ingresos operativos, gastos totales).
7. Transcribir los resultados por intermediario.
8. Actualizar la base de datos (CSV en `resultados/`).

**Reglas de negocio escritas:**
- Cada trimestre se busca en los enlaces de `Links.txt` el estado de resultados vigente y se agrega al historial del CSV.
- No hay clasificación de categorías (no hay umbrales de rentabilidad, tamaño, etc.). El entregable es la acumulación de registros en el CSV.
- Davivienda = DaviBank: unificar nombre antes de escribir en el CSV.
- Los campos `Tipo de elemento` y `Ruta de acceso` son metadatos de SharePoint y se conservan tal cual al agregar filas nuevas.
- Si un valor no está en el PDF, se deja vacío en el CSV.

**Resultado esperado:**
- El CSV de `resultados/` crece con una fila nueva por intermediario y trimestre procesado.
- Cada fila tiene los 16 campos con el formato descrito en la sección 4.

**Casos de control (para verificar la extracción manualmente):**

| Línea CSV | Año | Mes | Intermediario | Utilidad Neta (col. 12) | Comprobación |
|---|---|---|---|---|---|
| 1251 | 2025 | Diciembre | BN Seguros | +5.911.008.333,00 | Valor positivo grande; campo 12 es `?5.911.008.333,00` |
| 887 | 2023 | Marzo | Unity | -151.012.424,00 | Valor negativo; campo 12 es `-?151.012.424,00` |
| 32 | 2015 | Junio | Uniserse | (vacío) | Campo 12 vacío entre `;;` |

**Cómo verificar a mano un caso de control:**
1. Abrir el CSV con separador `;` y codificación Windows-1252.
2. Ir al número de línea indicado.
3. Contar los campos separados por `;` hasta llegar al campo 12.
4. El valor debe coincidir con la tabla anterior después de quitar el `?` inicial, los puntos de miles y cambiar la coma decimal por punto.

## 6. Rutas de la app

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Página de inicio: estado del proceso, último trimestre procesado, botón para iniciar descarga y lectura. |
| `GET` | `/procesar` | Inicia el ciclo trimestral: lee `Links.txt`, descarga PDFs, extrae campos y agrega al CSV. Devuelve resumen de cuántos intermediarios se procesaron y cuántos fallaron. |
| `GET` | `/resultados` | Muestra el contenido del CSV de resultados (historial) con paginación y filtro por intermediario/año/mes. |
| `POST` | `/cargar` | Carga un CSV externo y lo valida contra el formato esperado antes de fusionarlo al historial. |

Todas las rutas devuelven HTML (templates Flask) salvo que se indique lo contrario. Los mensajes de error y éxito se muestran en español.
