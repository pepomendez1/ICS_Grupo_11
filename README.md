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

Contiene el material institucional provisto por la cátedra, como el plan de cátedra, las condiciones de cursado y documentos equivalentes.

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

**Salidas de trabajos prácticos**

El archivo de salida principal deberá utilizar la convención `tp<nro>-salida.<extension>`. Ejemplos:

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

Se consideran **Ítems de Configuración (IC)** aquellos elementos que, debido a su relevancia dentro del proyecto, requieren identificación, versionado y control de cambios.

| Ítem de Configuración | Regla de nombrado | Ubicación física | Tipo |
|-----------------------|-------------------|------------------|------|
| README | `README.md` | `/` | Documentación |
| Material de cátedra | `<descripcion>.<ext>` | `/catedra/` | Documentación |
| Diapositivas | `<nro>-<tema>.<ext>` | `/material-teorico/diapositivas/` | Documentación |
| Bibliografía | `<tema>-<titulo>.<ext>` | `/material-teorico/bibliografia/` | Documentación |
| Apuntes | `<fecha>-<tema>.<ext>` | `/material-teorico/apuntes/` | Documentación |
| Enunciados de TP | `isw-enunciados-tp-evaluables-<año>.pdf` | `/trabajos-practicos/` | Documentación |
| Trabajos prácticos | `tp<nro>-<descripcion>.<ext>` | `/trabajos-practicos/tp<nro>/` | Producto |
| Salidas de TP | `tp<nro>-salida.<ext>` | `/trabajos-practicos/tp<nro>/` | Producto |
| Trabajos de investigación | `ti<nro>-<descripcion>.<ext>` | `/trabajos-investigacion/ti<nro>/` | Producto |
| Lineamientos de trabajos de investigación | `isw-lineamientos-trabajos-investigacion-<año>-<cuatrimestre>.pdf` | `/trabajos-investigacion/` | Documentación |
| Parciales | `<descripcion>.<ext>` | `/parciales/` | Producto |

Los ítems definidos en esta tabla se encuentran sujetos a las reglas de gestión de configuración establecidas por el grupo.

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

Una **línea base** representa una versión formalmente revisada y/o aprobada de un conjunto de ítems de configuración.

Para este proyecto, se establecerá una línea base luego de la revisión y/o aprobación por parte del equipo docente de cada trabajo práctico.

Una vez establecida una línea base, cualquier modificación posterior deberá estar debidamente justificada, por ejemplo:

- Corrección solicitada por el equipo docente.
- Error detectado luego de la entrega.
- Cambio necesario en algún ítem de configuración.
- Nueva versión aprobada del entregable.

### Convención de líneas base

Las líneas base se identificarán mediante **tags de Git** utilizando la estructura `lb<nro>-tp<nro>-v<version>`.

Ejemplo:

```
lb1-tp04-v1
```

Donde:

- `lb1` → primera línea base establecida para ese TP.
- `tp04` → trabajo práctico al que corresponde.
- `v1` → primera versión aprobada.

En caso de generarse una nueva versión:

```
lb1-tp04-v2
```

Si posteriormente se establece una nueva línea base:

```
lb2-tp04-v1
```

De esta manera se mantiene la trazabilidad de las versiones aprobadas a lo largo del proyecto.

---

## Gestión de cambios

Los cambios realizados sobre ítems que formen parte de una línea base deberán ser controlados y justificados.

El proceso general será:

1. Identificar la necesidad del cambio.
2. Determinar el ítem de configuración afectado.
3. Realizar la modificación correspondiente.
4. Registrar el cambio mediante un commit descriptivo.
5. Verificar que la modificación no afecte negativamente otros ítems.
6. Generar una nueva versión cuando corresponda.
7. Establecer una nueva línea base si la modificación es revisada y/o aprobada.

Esto permite mantener la integridad, trazabilidad y reproducibilidad de los elementos almacenados en el repositorio.

---

## Glosario

**`<nro>`**

Número entero de dos dígitos utilizado como identificador correlativo de un elemento. Ejemplos: `tp01`, `tp02`, `tp03`, ..., `tp10`.

**`<nro>` en diapositivas**

Número correlativo de dos dígitos utilizado para representar el orden de las diapositivas. Ejemplos: `00`, `01`, `02`, `03`, ...

**`<fecha>`**

Fecha en la que se genera o incorpora un archivo al repositorio. Se utiliza el estándar ISO 8601: `AAAA-MM-DD` (ejemplo: `2026-08-18`).

**`<cuatrimestre>`**

Cuatrimestre correspondiente al cursado. Se utiliza `1c` para el primer cuatrimestre y `2c` para el segundo cuatrimestre.

**`<año>`**

Año correspondiente al cursado, expresado con cuatro dígitos. Ejemplo: `2026`.

**`<tema>`**

Palabra o conjunto de palabras (en kebab-case) que describen el contenido principal del archivo. Ejemplos: `scm`, `tdd`, `nexus`, `kanban`, `control-versiones`.

**`<titulo>`**

Título descriptivo utilizado para identificar el contenido específico de un documento. Ejemplo: `scm-software-configuration-management.pdf`.

**`<descripcion>`**

Descripción breve y representativa del contenido de un archivo. Ejemplos: `tp04-salida.pdf`, `tp04-matriz-riesgos.xlsx`, `tp04-evidencias.pdf`.

**`<version>`**

Número entero que identifica la versión correspondiente de una línea base. Ejemplos: `lb1-tp04-v1`, `lb1-tp04-v2`, `lb2-tp04-v1`.

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
