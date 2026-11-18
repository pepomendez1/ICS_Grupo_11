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

El [plan de cátedra](../../catedra/plan-de-catedra.pdf) y el [cronograma oficial del curso 2026](../../catedra/cronograma-catedra-2026.pdf) están incorporados en `catedra/`. Se conserva exactamente el PDF del cronograma proporcionado, reformateado para mejorar su legibilidad.

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

El cronograma solicitado por la profesora está registrado en el inventario como **referencia externa (F-096)**; su incorporación no implica aprobación docente ni la creación de una nueva línea base.
## 4. Reglas de nombrado

Se aplican las [reglas y excepciones del README](../../README.md#convenciones-y-reglas-de-nombrado). Los nombres de documentos externos conservan la identificación de su edición; `2c` sólo identifica el archivo oficial de lineamientos y no agrega un campo a todos los entregables. Las revisiones se recuperan por Git, no mediante un sufijo de versión de LB.

## 5. Criterio para la creación de líneas base

### 5.1. Definición adoptada

Una **línea base** es una configuración que ha sido formalmente revisada y acordada, que sirve como base para desarrollos posteriores y que sólo puede modificarse a través de un procedimiento formal de control de cambios.

### 5.2. Momento de creación

**Se establecerá una línea base cuando el grupo revise y acuerde que un trabajo práctico se encuentra completo y listo para su entrega. Si el equipo docente solicita correcciones, se generará una nueva versión de esa línea base.**

Se eligió ese momento porque:

- Marca un estado **cerrado y verificable** del conjunto de ítems de configuración.
- Permite reproducir exactamente el contenido entregado, independientemente de los cambios posteriores.
- Está precedido por una revisión formal y un acuerdo explícito del equipo, que es lo que distingue una línea base de un simple punto de guardado.

### 5.3. Mecanismo de marcado

Las líneas base se marcan mediante **tags de Git**, que asocian un nombre estable a un commit determinado. A diferencia de una rama, un tag no se desplaza cuando se agregan nuevos commits, por lo que preserva de forma permanente el estado del repositorio en ese instante.

### 5.4. Convención de nomenclatura

```
lb<nro>-tp<nro>-v<version>
```

Ejemplo: `lb1-tp04-v1`

| Componente | Significado |
|------------|-------------|
| `lb1` | Primera línea base establecida para ese trabajo práctico. |
| `tp04` | Trabajo práctico al que corresponde. |
| `v1` | Primera versión aprobada. |

Evolución posible:

| Tag | Situación |
|-----|-----------|
| `lb1-tp04-v1` | Primera versión aprobada de la primera línea base. |
| `lb1-tp04-v2` | Nueva versión de esa misma línea base (por ejemplo, tras una corrección solicitada). |
| `lb2-tp04-v1` | Se establece una nueva línea base para el mismo trabajo práctico. |

### 5.5. Modificaciones posteriores

Una vez establecida una línea base, toda modificación sobre los ítems que la integran deberá estar justificada. Motivos admitidos:

- Corrección solicitada por el equipo docente.
- Error detectado luego de la entrega.
- Cambio necesario en algún ítem de configuración.
- Nueva versión aprobada del entregable.

Procedimiento:

1. Identificar la necesidad del cambio.
2. Determinar el ítem de configuración afectado.
3. Realizar la modificación correspondiente.
4. Registrar el cambio mediante un commit descriptivo.
5. Verificar que la modificación no afecte negativamente otros ítems.
6. Generar una nueva versión cuando corresponda.
7. Establecer una nueva línea base si la modificación es revisada y/o aprobada.

---

_Ingeniería y Calidad de Software · UTN FRC · Grupo 11_
