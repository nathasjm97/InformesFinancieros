# AGENTS.md - Automatización de Resultados de Intermediarios Financieros

## 1. Reglas para el agente

- No construir la app todavía: este archivo solo especifica el contrato de arquitectura y negocio.
- Toda extracción de datos debe hacerse desde los PDF de estados financieros publicados en los enlaces de `insumos/Links.txt`.
- No inventar datos. Si un valor no está legible o falta en el PDF, dejarlo vacío en el CSV y registrar el intermediario/trimestre como incompleto.
- Davivienda y DaviBank son el mismo intermediario (fusión/adquisición). Unificar bajo el nombre `DaviBank` en todas las capas.
- No usar datos reales de clientes ni de la empresa. Usar solo los estados financieros públicos de los intermediarios.
- El analista hace este proceso manualmente cada trimestre; la app debe reproducir ese mismo paso a paso sin interpretar criterios de negocio que no estén escritos.
- Si el PDF de un intermediario no se puede descargar o leer, la app debe continuar con los demás y reportar el fallo al final, no detenerse.
- **Criterio rector del área:** entre dejar un vacío y escribir un dato probable, se deja el vacío. Un dato equivocado que parece correcto es el peor resultado posible, porque llega al informe de la Junta Directiva sin que nadie lo note.
- Las cifras del CSV son **acumuladas del año** (enero a la fecha de corte). Nunca se suman filas para obtener un acumulado ni se mezclan valores de solo el trimestre.
- El histórico es **de solo agregar**: no se reescriben, corrigen ni borran filas existentes.

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
- **Período:** `Título` es el año de corte y `Mes` el mes de corte (Marzo, Junio, Septiembre, Diciembre). No es la fecha de publicación del PDF.
- **Nombres unificados al consultar:** las filas históricas pueden decir `Davivienda` o `DaviBank`; ambas se conservan tal cual en el archivo y se tratan como un solo intermediario al consultar y filtrar. El archivo no se reescribe.
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
- Davivienda = DaviBank: las filas nuevas se escriben como `DaviBank`; las filas históricas no se reescriben y la unión de los dos nombres se hace al consultar.
- Los campos `Tipo de elemento` y `Ruta de acceso` son metadatos de SharePoint y se conservan tal cual al agregar filas nuevas.
- Si un valor no está en el PDF, se deja vacío en el CSV.
- Las cifras son acumuladas del año (enero a la fecha de corte), tal como las publica el intermediario.

**Resultado esperado:**
- El CSV de `resultados/` crece con una fila nueva por intermediario y trimestre procesado.
- Cada fila tiene los 16 campos con el formato descrito en la sección 4.

**Qué resultado es inaceptable para el área:**
Un dato equivocado que parece correcto. El área prefiere un vacío, porque el vacío se investiga y el número falso pasa inadvertido al informe de la Junta Directiva y al indicador de participación de mercado. También son inaceptables el trimestre duplicado, las cifras de períodos mezclados y el trimestre presentado como completo cuando faltan intermediarios.

**Excepciones y casos especiales (aclaradas con el área):**
1. **Acumulado, no trimestre.** Una fila con `Mes` = Junio contiene enero a junio. No se suman filas para obtener el acumulado del año ni se completa un acumulado con datos de solo un trimestre.
2. **Reporte no publicado.** Si un intermediario no publicó su estado financiero del trimestre, o publicó uno con otro corte, **no se crea la fila**; se informa como "no publicado" en el resumen del proceso.
3. **Dato faltante dentro de un reporte publicado.** Si el reporte existe pero un valor no está o no es legible, **sí se crea la fila**, la celda queda vacía y el intermediario/trimestre se marca como incompleto.
4. **Nunca se imputa.** No se rellena un vacío con cero, con el valor del trimestre anterior ni con un cálculo propio.
5. **Activo y Patrimonio son saldos.** Salen del estado de situación (balance) a la fecha de corte, no del estado de resultados; no son flujos del período.
6. **Columna del período actual.** Cuando el PDF trae dos columnas (período actual y período comparativo del año anterior), se toma la del período actual. La comparativa nunca se usa.
7. **Corte y publicación son cosas distintas.** `Título` es el año de corte, `Mes` es el mes de corte. Un reporte publicado en julio con corte a junio pertenece a Junio.
8. **Los negativos son válidos.** Una utilidad neta negativa (pérdida) es un dato correcto y se conserva con su signo; no es un error de extracción.
9. **Trazabilidad al PDF.** La verificación manual del analista es releer el dato contra el PDF. El resumen del proceso debe indicar de qué archivo salió cada fila, sin agregar columnas al CSV.
10. **La app no opina.** No calcula indicadores, no clasifica intermediarios, no cuadra la fila aritméticamente, no compara contra el trimestre anterior y no corrige lo que el PDF dice.

**Casos de control (para verificar la extracción manualmente):**

| Línea CSV | Año | Mes | Intermediario | Utilidad Neta (col. 12) | Comprobación |
|---|---|---|---|---|---|
| 1251 | 2025 | Diciembre | BN Seguros | +5.911.008.333,00 | Valor positivo grande; campo 12 es `?5.911.008.333,00` |
| 887 | 2023 | Marzo | Unity | -151.012.424,00 | Valor negativo; campo 12 es `-?151.012.424,00` |
| 427 | 2015 | Marzo | Unity | (vacío) | Campo 12 vacío entre `;`; sí tiene col. 5, 13 y 14 |
| 409 | 2016 | Diciembre | Marsh Asprose | (vacío) | Fila casi vacía: solo col. 5; las demás columnas de datos quedan vacías |

> Corrección: el caso anterior usaba la línea 32 (Uniserse, 2015 Junio) como "Utilidad Neta vacía", pero esa fila sí tiene `?48.582.060,00` en la columna 12. Allí lo vacío son las columnas 4, 7, 8 y 11. Se reemplazó por los casos 427 y 409, verificados contra el archivo.

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
