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

> **Repositorio GitHub:** [ENLACE](https://github.com/pepomendez1/ICS_Grupo_11)

---

## Estructura del proyecto

La estructura general del repositorio es la siguiente:

```
ICS_Grupo_11/
│
├── README.md
│
├── Material_Teorico/
│   ├── Apuntes/
│   ├── Bibliografia/
│   └── Diapositivas/
│
└── Trabajos_Practicos/
    ├── ISW_Enunciados_TP_Evaluables_2025.pdf
    │
    ├── TP1/
    ├── TP2/
    ├── TP3/
    ├── TP4/
    ├── TP5/
    ├── TP6/
    ├── TP7/
    ├── TP8/
    ├── TP9/
    ├── TP10/
    ├── TP11/
    ├── TP12/
    ├── TP13/
    └── TP14/
        └── TP14_Salida.pdf
```

### Descripción de directorios

**`README.md`**

Contiene la información general del repositorio, integrantes del grupo, estructura, convenciones, ítems de configuración y reglas utilizadas para la gestión de configuración.

**`Material_Teorico/`**

Contiene el material académico utilizado durante el cursado.

- `Apuntes/`: resúmenes, notas y apuntes realizados durante las clases.
- `Bibliografia/`: libros, artículos, papers y demás bibliografía complementaria.
- `Diapositivas/`: presentaciones y filminas utilizadas por la cátedra.

**`Trabajos_Practicos/`**

Contiene los enunciados, archivos de trabajo, ítems de configuración y entregables correspondientes a los diferentes trabajos prácticos.

Cada trabajo práctico posee su propio directorio bajo la convención `TP<nro>/`. Por ejemplo:

```
TP1/
TP2/
TP3/
...
TP14/
```

---

## Convenciones y reglas de nombrado

Con el objetivo de mantener una estructura consistente y facilitar la identificación de los archivos, se establecen las siguientes convenciones.

### Reglas generales

- Los nombres de los archivos deberán utilizar la convención lowerCamelCase (camelCase), comenzando con letra minúscula y utilizando mayúscula al inicio de cada palabra siguiente, sin espacios, guiones ni guiones bajos.
- Evitar caracteres especiales y tildes en los nombres de archivos.
- Mantener las extensiones originales de los documentos.
- Respetar las convenciones definidas para cada tipo de ítem.
- Las fechas deberán expresarse utilizando el estándar **ISO 8601**: `AAAA-MM-DD` (ejemplo: `2026-08-18`).

### Trabajos prácticos

Los trabajos prácticos se almacenarán en carpetas con la estructura `TP<nro>/`. Ejemplos:

```
TP1/
TP4/
TP10/
TP14/
```

Se utiliza la expresión `TP*` para hacer referencia de manera genérica al conjunto de todos los trabajos prácticos (TP1, TP2, TP3, etc.).

Dentro de cada carpeta se almacenarán tanto los archivos necesarios para realizar el trabajo como su salida o entregable final.

**Salidas de trabajos prácticos**

El archivo de salida principal deberá utilizar la convención `TP<nro>_Salida.<extension>`. Ejemplos:

```
TP4_Salida.pdf
TP7_Salida.xlsx
TP14_Salida.pdf
```

En caso de existir otros archivos necesarios para el desarrollo del TP, se utilizará `TP<nro>_<descripcion>.<extension>`. Ejemplos:

```
TP4_Matriz_Riesgos.xlsx
TP6_Diagrama_Clases.pdf
TP10_Evidencias.pdf
```

### Diapositivas

Las diapositivas deberán utilizar la convención `<nro>_<tema>.<extension>`, donde `<nro>` representa el número correlativo de la presentación. Ejemplos:

```
01_SCM.pdf
02_Gestion_Configuracion.pdf
03_Control_Versiones.pdf
```

### Bibliografía

Los documentos correspondientes a bibliografía deberán utilizar `<tema>_<titulo>.<extension>`. Ejemplos:

```
SCM_Software_Configuration_Management.pdf
TDD_Test_Driven_Development.pdf
Kanban_Guia_Practica.pdf
```

El nombre deberá representar de forma clara el contenido principal del documento.

### Apuntes

Los apuntes deberán utilizar la convención `<fecha>_<tema>.<extension>`. La fecha deberá respetar el formato ISO 8601. Ejemplos:

```
2026-08-18_SCM.md
2026-08-25_Control_Versiones.pdf
2026-09-01_Lineas_Base.md
```

Esto permite ordenar los archivos cronológicamente de forma automática.

---

## Ítems de configuración

Se consideran **Ítems de Configuración (IC)** aquellos elementos que, debido a su relevancia dentro del proyecto, requieren identificación, versionado y control de cambios.

| Ítem de Configuración | Regla de nombrado | Ubicación física | Tipo |
|-----------------------|-------------------|------------------|------|
| README | `README.md` | `/` | Documentación |
| Diapositivas | `<nro>_<tema>.<ext>` | `/Material_Teorico/Diapositivas/` | Documentación |
| Bibliografía | `<tema>_<titulo>.<ext>` | `/Material_Teorico/Bibliografia/` | Documentación |
| Apuntes | `<fecha>_<tema>.<ext>` | `/Material_Teorico/Apuntes/` | Documentación |
| Enunciados de TP | `ISW_Enunciados_TP_Evaluables_<año>.pdf` | `/Trabajos_Practicos/` | Documentación |
| Trabajos prácticos | `TP<nro>_<descripcion>.<ext>` | `/Trabajos_Practicos/TP<nro>/` | Producto |
| Salidas de TP | `TP<nro>_Salida.<ext>` | `/Trabajos_Practicos/TP<nro>/` | Producto |

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
add: incorporar salida del TP4
update: modificar apuntes de SCM
fix: corregir nomenclatura de archivos del TP3
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

Las líneas base se identificarán mediante **tags de Git** utilizando la estructura `LB<nro>_TP<nro>_v<version>`.

Ejemplo:

```
LB1_TP4_v1
```

Donde:

- `LB1` → primera línea base establecida para ese TP.
- `TP4` → trabajo práctico al que corresponde.
- `v1` → primera versión aprobada.

En caso de generarse una nueva versión:

```
LB1_TP4_v2
```

Si posteriormente se establece una nueva línea base:

```
LB2_TP4_v1
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

Número entero utilizado como identificador de un elemento. En determinados casos puede utilizarse de forma correlativa. Ejemplos: `TP1`, `TP2`, `TP3`, ..., `TP10`.

**`<nro>` en diapositivas**

Número correlativo de dos dígitos utilizado para representar el orden de las diapositivas. Ejemplos: `00`, `01`, `02`, `03`, ...

**`<fecha>`**

Fecha en la que se genera o incorpora un archivo al repositorio. Se utiliza el estándar ISO 8601: `AAAA-MM-DD` (ejemplo: `2026-08-18`).

**`<tema>`**

Palabra o conjunto de palabras que describen el contenido principal del archivo. Ejemplos: `SCM`, `TDD`, `Nexus`, `Kanban`, `Control_Versiones`.

**`<titulo>`**

Título descriptivo utilizado para identificar el contenido específico de un documento. Ejemplo: `SCM_Software_Configuration_Management.pdf`.

**`<descripcion>`**

Descripción breve y representativa del contenido de un archivo asociado a un trabajo práctico. Ejemplos: `TP4_Salida.pdf`, `TP4_Matriz_Riesgos.xlsx`, `TP4_Evidencias.pdf`.

**`<version>`**

Número entero que identifica la versión correspondiente de una línea base. Ejemplos: `LB1_TP4_v1`, `LB1_TP4_v2`, `LB2_TP4_v1`.

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
