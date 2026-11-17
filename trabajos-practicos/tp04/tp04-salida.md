# Trabajo Práctico N° 4 — SCM: Herramientas de SCM

**Unidad Nro. 3: Gestión del Software como producto**

| Campo | Información |
|-------|-------------|
| Universidad | Universidad Tecnológica Nacional — Facultad Regional Córdoba |
| Carrera | Ingeniería en Sistemas de Información |
| Cátedra | Ingeniería y Calidad de Software |
| Curso | 4K2 |
| Grupo | Grupo 11 |
| Profesora Titular | Ing. Judith Meles |
| Jefa de Trabajos Prácticos | Ing. Cecilia Massano |

---

## 1. Repositorio implementado

| Campo | Detalle |
|-------|---------|
| **URL** | https://github.com/pepomendez1/ICS_Grupo_11 |
| Motor de control de versiones | Git |
| Plataforma de alojamiento | GitHub |
| Visibilidad | **Público** |
| Modelo de repositorio | Distribuido (descentralizado) |

### 1.1. Integrantes y usuarios

Todos los integrantes del grupo poseen cuenta de usuario con acceso al repositorio.

| Nombre y apellido | Legajo |
|-------------------|--------|
| Cardelli Enzo Valentino | 400042 |
| Martín Benjamín | 400021 |
| Fernández Juan Martín | 403831 |
| Ribero Valentín | 400496 |
| Ruiz Michelotti Emiliano | 400491 |
| Camaño Grossi Luca | 400106 |
| Zecchin Valentino | 94444 |
| García Verea Alfonso | 402852 |
| Sánchez Segura Emilio | 400170 |
| Pérez Manuel | 400742 |
| Kilic Aslan Haik Martín | 85246 |
| Lucero Pedro | 400016 |
| Méndez Carranza Pedro | 94214 |
| García Mateo | 400174 |

Usuarios de GitHub con acceso al repositorio:

`Mate1402` · `HaikKilic` · `lucacgrossi` · `PedroLuceroo` · `pepomendez1` · `Emilianoruizzzz` · `EnneAlCuadrado` · `EnzoCardelli64` · `emisanchezsegura` · `juanfernandez204` · `benja1231231` · `alfonchori` · `zecchinvalentino8-boop` · `MPerez6`

---

## 2. Estructura y documentos de entrada

La [estructura del repositorio](../../README.md#estructura-del-proyecto) y las [reglas de nombrado](../../README.md#convenciones-y-reglas-de-nombrado) se mantienen en el README como referencia común.

El [plan de cátedra](../../catedra/plan-de-catedra.pdf) ya está incorporado. El **cronograma oficial del curso está pendiente de incorporación**: debe obtenerse de la cátedra y agregarse a `catedra/`, sin inventar fechas.

La salida de este TP es la URL pública y este documento de definición de IC y criterios de LB, de acuerdo con el [enunciado del TP04, página 9](../isw-enunciados-tp-evaluables-2026.pdf). “Salida” significa entregable exigido por una consigna; no es una segunda clasificación del mismo archivo.

## 3. Definición de ítems de configuración

Se identifican elementos reales del repositorio y se distingue entre entregables, material de estudio, referencias externas y registros de gestión. Una carpeta reservada no acredita un trabajo realizado.

| ID | Ítem / alcance | Descripción y función | Regla de nombrado | Ubicación física | Tipo | Origen / responsable de mantenimiento | Identificación de versión y estado |
|---|---|---|---|---|---|---|---|
| IC-01 | README | Organización y reglas de SCM | `README.md` | Raíz | Documentación de gestión | Grupo 11 | Commit Git; documento en evolución |
| IC-02 | Plan de cátedra | Planificación institucional de la asignatura | `plan-de-catedra.pdf` | `catedra/` | Referencia externa | Cátedra; grupo incorpora el original | Blob Git; presente |
| IC-03 | Apuntes | Notas de clase elaboradas por estudiantes | `<fecha>-<tema>.<ext>` | `material-teorico/apuntes/` | Material de estudio | Autores de los apuntes; grupo mantiene | Blob Git; presentes |
| IC-04 | Bibliografía | Documentos consultados para el cursado | `<tema>-<titulo>.<ext>` | `material-teorico/bibliografia/` | Referencia externa | Autores originales; grupo incorpora | Blob Git; presente |
| IC-05 | Diapositivas | Presentaciones de los temas de la asignatura | `<nro>-<tema>.<ext>` | `material-teorico/diapositivas/` | Referencia externa | Cátedra; grupo incorpora | Blob Git; presentes |
| IC-06 | Enunciados de TP | Consignas y entregables requeridos | `isw-enunciados-tp-evaluables-<año>.pdf` | `trabajos-practicos/` | Referencia externa | Cátedra; grupo incorpora | Blob Git; presente |
| IC-07 | Informe del TP04 | URL, diseño del repositorio y criterios SCM | `tp04-salida.md` | `trabajos-practicos/tp04/` | Entregable documental | Grupo 11 | Commit Git; presente, aprobación docente no acreditada |
| IC-08 | Aplicación del TP06 | Código, pruebas, esquema SQL, configuración, documentación y recursos de EcoHarmony Park | `tp06-ecoharmony-park/`; nombres internos propios de las herramientas | `trabajos-practicos/tp06/` | Producto de software compuesto | Grupo 11 | Commit Git del conjunto; presente |
| IC-09 | Informe y evidencias del TP07 | Informe, gráficos y fotografías de la maqueta | `tp07-<descripcion>.<ext>` | `trabajos-practicos/tp07/` | Entregable documental y evidencias | Grupo 11 | Blob Git por archivo; presentes |
| IC-10 | Lineamientos de investigación | Consigna oficial de investigación | `isw-lineamientos-trabajos-investigacion-2026-2c.pdf` | `trabajos-investigacion/` | Referencia externa | Cátedra; grupo incorpora | Blob Git; presente |
| IC-11 | Trabajo de investigación 01 | Documento sobre release de CRM SaaS multi-tenant | `ti01-<descripcion>.pdf` | `trabajos-investigacion/ti01/` | Entregable documental | Grupo 11 | Blob Git; presente |
| IC-12 | Trabajo de investigación 02 | Póster sobre Scrum at Scale | `ti02-<descripcion>.pdf` | `trabajos-investigacion/ti02/` | Entregable documental | Grupo 11 | Blob Git; presente |
| IC-13 | Material de preparación de parciales | Temarios y resúmenes; no son exámenes resueltos ni productos del proyecto | `<descripcion>.<ext>` | `parciales/` | Material de estudio | Grupo mantiene las copias; autoría según documento | Blob Git; presente |
| IC-14 | Inventario de archivos | Identificación individual, ruta, tipo y revisión de los archivos | `inventario-items.md` | `catedra/` | Registro de gestión | Grupo 11 | Commit Git; actualizar al incorporar, mover o retirar archivos |

El [inventario individual](../../catedra/inventario-items.md) detalla los archivos. No se dispone de la plantilla original de la cátedra para cotejar sus encabezados exactos; se explicitan ID, alcance, descripción, regla, ubicación, tipo, origen/responsabilidad, revisión y estado. Si la plantilla exige otros campos, deben completarse a partir de esa fuente.

## 4. Reglas de nombrado

Se aplican las [reglas y excepciones del README](../../README.md#convenciones-y-reglas-de-nombrado). Los nombres de documentos externos conservan la identificación de su edición; `2c` sólo identifica el archivo oficial de lineamientos y no agrega un campo a todos los entregables. Las revisiones se recuperan por Git, no mediante un sufijo de versión de LB.

## 5. Criterio para la creación de líneas base

Una **línea base (LB)** es un conjunto identificado de ítems de configuración en revisiones concretas, formalmente revisado y acordado como referencia para continuar el trabajo. Su registro debe permitir reconstruir ese conjunto y controlar cualquier cambio posterior.

### Criterio y momento de establecimiento

Se establece una LB al cerrar un hito de entrega de un TP o trabajo de investigación, después de que el grupo verifique:
1. Que los entregables exigidos por la consigna estén presentes y completos.
2. Que cada ítem esté identificado, ubicado y registrado en el inventario.
3. Que los enlaces y documentos sean coherentes; si incluye software, que se registren las comprobaciones y resultados pertinentes.
4. Que exista un acuerdo de revisión que identifique responsables, fecha, alcance, revisiones y observaciones pendientes.

La revisión interna para entregar y la aprobación docente son estados distintos. No se declara aprobación docente sin evidencia.

### Identificación y registro

Los ítems evolucionan mediante revisiones identificadas por commits. **Una corrección revisada y acordada origina una nueva línea base, con otro identificador; no una versión de la misma LB.**

La convención para nuevas etiquetas es `lb<secuencia>-<hito>`, con secuencia global de dos dígitos y un hito descriptivo; por ejemplo, `lb02-tp04-correccion`. El ejemplo es una convención, no una LB ya establecida.

Cada nueva LB se marca mediante un tag anotado sobre el commit revisado. La anotación o el acta enlazada debe indicar: identificador, fecha, motivo/hito, revisores, acuerdo, lista de ítems y revisiones, comprobaciones efectuadas, pendientes y LB anterior. Aunque el tag referencia todo el repositorio, su alcance formal lo determina esa lista. No se mueve ni se sobrescribe un tag ya establecido.

### Línea base histórica verificada

| Tag existente | Commit de referencia | Fecha registrada | Alcance documentado | Tratamiento |
|---|---|---|---|---|
| [`lb1-tp04-v1`](https://github.com/pepomendez1/ICS_Grupo_11/tree/lb1-tp04-v1) | `9d411f0c3ad02441f6a176ad94bc2b52e91e000f` | 2026-08-24 | La anotación declara revisión y acuerdo del grupo para el TP04 y todos los IC disponibles en esa entrega | Se conserva como evidencia histórica. Su sufijo heredado no se utiliza para crear nuevas LB. |

La corrección de esta documentación no constituye por sí sola una nueva LB: falta registrar la revisión y el acuerdo del grupo sobre el conjunto corregido.

## 6. Control de cambios

Los cambios sobre ítems incluidos en una LB requieren:
1. Registrar la solicitud, su motivo, solicitante e ítems afectados.
2. Analizar impacto en entregables, código, pruebas y documentación.
3. Registrar la decisión del grupo antes de modificar el conjunto controlado.
4. Implementar el cambio y registrarlo en commits descriptivos.
5. Revisar el resultado y guardar la evidencia de las verificaciones.
6. Actualizar el inventario y el estado de los ítems.
7. Cuando se cumpla el criterio de cierre, establecer **otra LB con un nuevo identificador**, enlazando la anterior y la solicitud.

La LB anterior permanece recuperable sin alteraciones.

_Ingeniería y Calidad de Software · UTN FRC · Grupo 11_
