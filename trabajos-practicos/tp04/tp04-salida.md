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

En las diapositivas 17, 38 y 39 del material de SCM, la cátedra define los IC como artefactos del producto o proyecto que requieren conocer su estado y evolución, exige identificación unívoca, regla de nombrado y ubicación, y distingue **Producto / Proyecto / Iteración**. Por ello, esta tabla clasifica los ítems controlados y no confunde los archivos de consulta con el producto desarrollado.

| ID | Nombre del ítem de configuración | Regla de nombrado | Ubicación física | Tipo de ítem (Producto / Proyecto / Iteración) | Estado y alcance |
|---|---|---|---|---|---|
| IC-01 | Reglas de gestión de configuración del grupo | `README.md` | Raíz | Proyecto (común) | Presente |
| IC-07 | Definición del repositorio y SCM del TP04 | `tp04-salida.md` | `trabajos-practicos/tp04/` | Proyecto (entrega TP04) | Presente; revisión docente pendiente |
| IC-08 | Aplicación EcoHarmony Park: código, diseño, pruebas y recursos | `tp06-ecoharmony-park/` (nombres internos del lenguaje y herramientas) | `trabajos-practicos/tp06/` | Producto | Presente; se controla como conjunto |
| IC-09 | Informe, maqueta y evidencias del TP07 | `tp07-<descripcion>.<ext>` | `trabajos-practicos/tp07/` | Proyecto (entrega TP07) | Presentes; revisar clasificación de gráficos por iteración |
| IC-11 | Documento del trabajo de investigación 01 | `ti01-<descripcion>.pdf` | `trabajos-investigacion/ti01/` | Proyecto (entrega TI01) | Presente |
| IC-12 | Póster del trabajo de investigación 02 | `ti02-<descripcion>.pdf` | `trabajos-investigacion/ti02/` | Proyecto (entrega TI02) | Presente |
| IC-14 | Inventario de elementos del repositorio | `inventario-items.md` | `catedra/` | Proyecto (común) | Presente; registra también referencias |

**Proyecto (común)** indica documentos que acompañan el trabajo del grupo; **Proyecto (entrega)** identifica el hito asociado. **Iteración** se utilizará para artefactos específicos de una iteración cuando estén identificados, por ejemplo un plan o reporte de defectos. No se inventan iteraciones a partir de carpetas de TP. Los gráficos de TP07 deben revisarse antes de asignarles una iteración.

El [inventario individual](../../catedra/inventario-items.md) registra también bibliografía, apuntes, material de cátedra y archivos de referencia, sin equiparar todos esos archivos a IC activos. Los ID de las categorías que se reclasificaron como referencias se reservan por trazabilidad. No se acredita aprobación docente solamente por estar el archivo publicado.

El cronograma solicitado por la profesora **no se encontró en** `catedra/`; se incorporará el original cuando esté disponible.
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
