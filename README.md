# Ingeniería y Calidad de Software — Grupo 11

Repositorio académico del **Grupo 11** de la materia **Ingeniería y Calidad de Software**, correspondiente a la carrera Ingeniería en Sistemas de Información de la **Universidad Tecnológica Nacional — Facultad Regional Córdoba (UTN FRC)**.

El objetivo de este repositorio es centralizar, organizar y versionar los distintos artefactos generados y utilizados durante el cursado de la materia, aplicando los conceptos de **Gestión de Configuración de Software (SCM)** estudiados en la cátedra.

---

## Tabla de contenidos

1. [Información general](#información-general)
2. [Integrantes del grupo](#integrantes-del-grupo)
3. [Objetivos del repositorio](#objetivos-del-repositorio)
4. [Repositorio del proyecto](#repositorio-del-proyecto)
5. [Estructura del proyecto](#estructura-del-proyecto)
6. [Convenciones y reglas de nombrado](#convenciones-y-reglas-de-nombrado)
7. [Ítems de configuración](#ítems-de-configuración)
8. [Control de versiones](#control-de-versiones)
9. [Líneas base del proyecto](#líneas-base-del-proyecto)
10. [Gestión de cambios](#gestión-de-cambios)
11. [Glosario](#glosario)

---

## Información general

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

## Integrantes del grupo

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

---

## Objetivos del repositorio

Este repositorio tiene como finalidad:

- Centralizar el material utilizado durante el cursado de la materia.
- Mantener organizados los trabajos prácticos y sus respectivos entregables.
- Identificar y controlar los Ítems de Configuración (IC).
- Aplicar reglas de nombrado uniformes para archivos y directorios.
- Mantener trazabilidad sobre las modificaciones realizadas.
- Utilizar Git como herramienta de control de versiones.
- Establecer y mantener líneas base de los trabajos prácticos aprobados.
- Facilitar el trabajo colaborativo entre los integrantes del grupo.
- Preservar un historial de cambios que permita recuperar versiones anteriores cuando sea necesario.

---

## Repositorio del proyecto

El proyecto utiliza **Git** como sistema de control de versiones y **GitHub** como plataforma para alojar y gestionar el repositorio remoto.

> **Repositorio GitHub:** [ICS_Grupo_11](https://github.com/pepomendez1/ICS_Grupo_11)

---

## Estructura del proyecto

La estructura general del repositorio es la siguiente:

```
ICS_Grupo_11/
│
├── catedra/
│   ├── plan-de-catedra.pdf
│   └── inventario-items.md
│
├── material-teorico/
│   ├── apuntes/
│   ├── bibliografia/
│   └── diapositivas/
│
├── parciales/
│
├── trabajos-practicos/
│   ├── isw-enunciados-tp-evaluables-2026.pdf
│   │
│   ├── tp01/
│   ├── tp02/
│   ├── tp03/
│   ├── tp04/
│   ├── tp05/
│   ├── tp06/
│   ├── tp07/
│   ├── tp08/
│   ├── tp09/
│   ├── tp10/
│   ├── tp11/
│   ├── tp12/
│   ├── tp13/
│   └── tp14/
│
├── trabajos-investigacion/
│   ├── isw-lineamientos-trabajos-investigacion-2026-2c.pdf
│   ├── ti01/
│   └── ti02/
│
└── README.md
```

### Descripción de directorios

**`catedra/`**

Contiene el [plan de cátedra](catedra/plan-de-catedra.pdf) ya incorporado y el [inventario de ítems](catedra/inventario-items.md). El cronograma oficial del curso está **pendiente de incorporación**: no se encontró en el repositorio y no se reemplaza por fechas estimadas. Cuando el grupo disponga del original, deberá incorporarlo aquí como `cronograma-catedra-2026.<ext>` y registrarlo en el inventario.

**`material-teorico/`**

Contiene el material académico utilizado durante el cursado.

- `apuntes/`: resúmenes, notas y apuntes realizados durante las clases.
- `bibliografia/`: libros, artículos, papers y demás bibliografía complementaria.
- `diapositivas/`: presentaciones y filminas utilizadas por la cátedra.

**`parciales/`**

Contiene el material correspondiente a las instancias de evaluación parcial, como los temas incluidos en cada parcial y la documentación asociada.

**`trabajos-practicos/`**

Contiene los enunciados, archivos de trabajo, ítems de configuración y entregables correspondientes a los diferentes trabajos prácticos.

Cada trabajo práctico posee su propio directorio bajo la convención `tp<nro>/` (numeración de dos dígitos). Por ejemplo:

```
tp01/
tp02/
tp03/
...
tp14/
```

**`trabajos-investigacion/`**

Contiene los lineamientos generales y los trabajos de investigación desarrollados durante el cursado.

Los lineamientos generales provistos por la cátedra se almacenan directamente en este directorio.

Cada trabajo de investigación posee su propio directorio bajo la convención `ti<nro>/` (numeración de dos dígitos). Por ejemplo:

```text
ti01/
ti02/
```

**`README.md`**

Contiene la información general del repositorio, integrantes del grupo, estructura, convenciones, ítems de configuración y reglas utilizadas para la gestión de configuración.

---

## Convenciones y reglas de nombrado

Con el objetivo de mantener una estructura consistente y facilitar la identificación de los archivos, se establecen las siguientes convenciones.

### Reglas generales

- Los nombres de carpetas y archivos deberán utilizar la convención **kebab-case**: todo en minúsculas, palabras separadas por `-` (guion medio), sin espacios, sin guiones bajos ni mayúsculas.
- Evitar caracteres especiales y tildes en los nombres de archivos y carpetas.
- Mantener las extensiones originales de los documentos.
- Respetar las convenciones definidas para cada tipo de ítem.
- Las fechas deberán expresarse utilizando el estándar **ISO 8601**: `AAAA-MM-DD` (ejemplo: `2026-08-18`).
- Los números correlativos (trabajos prácticos, diapositivas, etc.) se escriben con **dos dígitos** para permitir el ordenamiento automático: `01`, `02`, ..., `14`.

> **Excepciones:** `README.md` conserva el nombre estándar. Dentro de `tp06-ecoharmony-park/` se conservan los nombres requeridos por Python, herramientas, recursos y documentación existente (por ejemplo, `__init__.py`, `test_*.py`, `requirements.txt`, `DECISIONES_DISENO.md`). No se renombran automáticamente porque pueden tener referencias internas.

> **Nota:** el nombre del repositorio (`ICS_Grupo_11`) se conserva tal cual para no romper los enlaces ya compartidos. La convención kebab-case aplica al contenido interno del repositorio.

### Trabajos prácticos

Los trabajos prácticos se almacenarán en carpetas con la estructura `tp<nro>/`. Ejemplos:

```
tp01/
tp04/
tp10/
tp14/
```

Se utiliza la expresión `tp*` para hacer referencia de manera genérica al conjunto de todos los trabajos prácticos (tp01, tp02, tp03, etc.).

Dentro de cada carpeta se almacenarán tanto los archivos necesarios para realizar el trabajo como su salida o entregable final.

**Entregables de trabajos prácticos (salidas)**

Una salida es el resultado exigido por la consigna, no necesariamente un único archivo. En el TP04 es la URL del repositorio y el documento de SCM (`tp04-salida.md`); en el TP06 está el proyecto `tp06-ecoharmony-park/`; en el TP07 están `tp07-salida.pdf` y sus evidencias. La palabra `salida` no define una categoría adicional de IC que duplique los mismos archivos.

Cuando el entregable principal sea un informe, deberá utilizar la convención `tp<nro>-salida.<extension>`. Ejemplos:

```
tp04-salida.pdf
tp07-salida.xlsx
tp14-salida.pdf
```

En caso de existir otros archivos necesarios para el desarrollo del TP, se utilizará `tp<nro>-<descripcion>.<extension>`. Ejemplos:

```
tp04-matriz-riesgos.xlsx
tp06-diagrama-clases.pdf
tp10-evidencias.pdf
```

### Trabajos de investigación

Los trabajos de investigación se almacenarán en carpetas con la estructura `ti<nro>/`, utilizando numeración de dos dígitos. Ejemplos:

```text
ti01/
ti02/
```
Dentro de cada carpeta se almacenarán los archivos necesarios para el desarrollo del trabajo de investigación.
Los archivos deberán utilizar la convención `ti<nro>-<descripcion>.<extension>`.

### Diapositivas

Las diapositivas deberán utilizar la convención `<nro>-<tema>.<extension>`, donde `<nro>` representa el número correlativo de la presentación. Ejemplos:

```
01-scm.pdf
02-gestion-configuracion.pdf
03-control-versiones.pdf
```

### Bibliografía

Los documentos correspondientes a bibliografía deberán utilizar `<tema>-<titulo>.<extension>`. Ejemplos:

```
scm-software-configuration-management.pdf
tdd-test-driven-development.pdf
kanban-guia-practica.pdf
```

El nombre deberá representar de forma clara el contenido principal del documento.

### Apuntes

Los apuntes deberán utilizar la convención `<fecha>-<tema>.<extension>`. La fecha deberá respetar el formato ISO 8601. Ejemplos:

```
2026-08-18-scm.md
2026-08-25-control-versiones.pdf
2026-09-01-lineas-base.md
```

Esto permite ordenar los archivos cronológicamente de forma automática.

### Material de cátedra

Los documentos de la carpeta `catedra/` deberán utilizar un nombre descriptivo en kebab-case. Ejemplos:

```
plan-de-catedra.pdf
condiciones-de-cursado.pdf
reglas-de-comunicacion.md
```

---

## Ítems de configuración

Se controlan tanto los entregables del grupo como las copias de referencia necesarias para reproducir el trabajo. Se distingue su función: un material de estudio no es un producto desarrollado. Las categorías siguientes corresponden a archivos presentes; los directorios reservados sin entregables no se presentan como trabajos terminados.

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

El [inventario individual](catedra/inventario-items.md) identifica los archivos y sus revisiones. “Presente” no significa “aprobado”.

---

## Control de versiones

El control de versiones del proyecto se realizará utilizando **Git**.

Cada modificación relevante deberá quedar registrada mediante un commit que describa de manera clara el cambio realizado.

### Convención para commits

Se recomienda utilizar mensajes breves y descriptivos bajo la estructura `<tipo>: <descripcion>`.

Tipos sugeridos:

| Tipo | Uso |
|------|-----|
| `add` | Incorporación de un nuevo archivo o contenido |
| `update` | Actualización de contenido existente |
| `fix` | Corrección de errores |
| `docs` | Cambios relacionados con documentación |
| `refactor` | Reorganización sin modificar el contenido funcional |
| `remove` | Eliminación de archivos o contenido |

Ejemplos:

```
add: incorporar salida del tp04
update: modificar apuntes de scm
fix: corregir nomenclatura de archivos del tp03
docs: actualizar README
remove: eliminar archivo duplicado
```

Los commits deberán representar, siempre que sea posible, una unidad lógica de cambio.

---

## Líneas base del proyecto

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

---

## Gestión de cambios

Los cambios sobre ítems incluidos en una LB requieren:
1. Registrar la solicitud, su motivo, solicitante e ítems afectados.
2. Analizar impacto en entregables, código, pruebas y documentación.
3. Registrar la decisión del grupo antes de modificar el conjunto controlado.
4. Implementar el cambio y registrarlo en commits descriptivos.
5. Revisar el resultado y guardar la evidencia de las verificaciones.
6. Actualizar el inventario y el estado de los ítems.
7. Cuando se cumpla el criterio de cierre, establecer **otra LB con un nuevo identificador**, enlazando la anterior y la solicitud.

La LB anterior permanece recuperable sin alteraciones.

---

## Glosario

**`<nro>`**

Número entero de dos dígitos utilizado como identificador correlativo de un elemento. Ejemplos: `tp01`, `tp02`, `tp03`, ..., `tp10`.

**`<nro>` en diapositivas**

Número correlativo de dos dígitos utilizado para representar el orden de las diapositivas. Ejemplos: `00`, `01`, `02`, `03`, ...

**`<fecha>`**

Fecha en la que se genera o incorpora un archivo al repositorio. Se utiliza el estándar ISO 8601: `AAAA-MM-DD` (ejemplo: `2026-08-18`).

**`<cuatrimestre>`**

La mención `2c` se conserva únicamente como parte del nombre del documento oficial de lineamientos de investigación para identificar su edición. No es un campo requerido para nombrar los entregables del grupo.

**`<año>`**

Año correspondiente al cursado, expresado con cuatro dígitos. Ejemplo: `2026`.

**`<tema>`**

Palabra o conjunto de palabras (en kebab-case) que describen el contenido principal del archivo. Ejemplos: `scm`, `tdd`, `nexus`, `kanban`, `control-versiones`.

**`<titulo>`**

Título descriptivo utilizado para identificar el contenido específico de un documento. Ejemplo: `scm-software-configuration-management.pdf`.

**`<descripcion>`**

Descripción breve y representativa del contenido de un archivo. Ejemplos: `tp04-salida.pdf`, `tp04-matriz-riesgos.xlsx`, `tp04-evidencias.pdf`.

**`<secuencia>` y `<hito>`**

Secuencia global de dos dígitos de una nueva LB y descripción del hito que representa. Las versiones o revisiones corresponden a los ítems; cada LB tiene una identidad distinta.

---

## Consideraciones finales

Todos los integrantes del **Grupo 11** deberán respetar las convenciones definidas en este documento al incorporar o modificar elementos del repositorio.

El objetivo de estas reglas es garantizar:

- Consistencia en la estructura del repositorio.
- Trazabilidad de las modificaciones.
- Identificación clara de los ítems de configuración.
- Control sobre las versiones y líneas base.
- Colaboración ordenada entre los integrantes.
- Reproducibilidad de los entregables del proyecto.

Las convenciones podrán actualizarse durante el cursado si el grupo o la cátedra identifican la necesidad de incorporar nuevas reglas. Cualquier modificación deberá quedar registrada en el historial de versiones del repositorio.

---

_Ingeniería y Calidad de Software · UTN FRC · Grupo 11_
