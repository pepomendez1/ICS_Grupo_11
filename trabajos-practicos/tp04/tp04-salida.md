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

## 2. Estructura del repositorio

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
│   ├── ...
│   └── tp14/
│
├── trabajos-investigacion/
│   ├── isw-lineamientos-trabajos-investigacion-2026-2c.pdf
│   ├── ti01/
│   └── ti02/
│
└── README.md
```

| Directorio | Contenido |
|------------|-----------|
| `catedra/` | Material institucional provisto por la cátedra. |
| `material-teorico/apuntes/` | Apuntes y tomas de nota de las clases. |
| `material-teorico/bibliografia/` | Libros, papers y bibliografía complementaria. |
| `material-teorico/diapositivas/` | Presentaciones utilizadas por la cátedra. |
| `parciales/` | Material de las instancias de evaluación parcial. |
| `trabajos-practicos/` | Enunciados y un directorio `tp<nro>/` por trabajo práctico. |
| `trabajos-investigacion/` | Lineamientos y un directorio `ti<nro>/` por trabajo de investigación. |
| `README.md` | Documentación general y reglas de gestión de configuración. |

---

## 3. Definición de ítems de configuración

Se consideran **Ítems de Configuración (IC)** aquellos artefactos que forman parte del producto o del proyecto, que pueden sufrir cambios o necesitan ser compartidos entre los miembros del equipo, y sobre los cuales se necesita conocer su estado y evolución.

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
| Lineamientos de TI | `isw-lineamientos-trabajos-investigacion-<año>-<cuatrimestre>.pdf` | `/trabajos-investigacion/` | Documentación |
| Parciales | `<descripcion>.<ext>` | `/parciales/` | Producto |

---

## 4. Reglas de nombrado

### 4.1. Reglas generales

Aplican a todos los ítems de configuración sin excepción:

- Los nombres de carpetas y archivos utilizan la convención **kebab-case**: todo en minúsculas, palabras separadas por `-` (guion medio), sin espacios, sin guiones bajos ni mayúsculas.
- Se evitan caracteres especiales y tildes.
- Se mantienen las extensiones originales de los documentos.
- Las fechas se expresan según el estándar **ISO 8601**: `AAAA-MM-DD`.
- Los números correlativos se escriben con **dos dígitos** (`01`, `02`, …, `14`) para permitir el ordenamiento automático.

> El nombre del repositorio (`ICS_Grupo_11`) se conserva tal cual para no romper los enlaces ya compartidos. La convención kebab-case aplica al contenido interno.

### 4.2. Reglas por tipo de ítem

| Ítem | Convención | Ejemplo |
|------|------------|---------|
| Apuntes | `<fecha>-<tema>.<ext>` | `2026-08-14-scm.pdf` |
| Diapositivas | `<nro>-<tema>.<ext>` | `02-scm.pdf` |
| Bibliografía | `<tema>-<titulo>.<ext>` | `scm-little-book-of-configuration-management.pdf` |
| Material de cátedra | `<descripcion>.<ext>` | `plan-de-catedra.pdf` |
| Trabajos prácticos | `tp<nro>-<descripcion>.<ext>` | `tp04-matriz-riesgos.xlsx` |
| Salidas de TP | `tp<nro>-salida.<ext>` | `tp04-salida.md` |
| Trabajos de investigación | `ti<nro>-<descripcion>.<ext>` | `ti01-metricas-de-calidad.pdf` |
| Parciales | `<descripcion>.<ext>` | `temas-primer-parcial.md` |

**Criterio de selección del prefijo:** cada convención antepone el dato por el cual conviene ordenar esa carpeta. Los apuntes llevan **fecha** porque interesa el orden cronológico de las clases; las diapositivas llevan **número** porque interesa el orden de dictado; la bibliografía lleva **tema** porque interesa agrupar por materia.

### 4.3. Glosario de componentes

| Componente | Definición |
|------------|------------|
| `<nro>` | Número correlativo de dos dígitos. Ej.: `01`, `02`, `14`. |
| `<fecha>` | Fecha en formato ISO 8601 `AAAA-MM-DD`. Ej.: `2026-08-14`. |
| `<tema>` | Palabra o conjunto de palabras en kebab-case que describen el contenido principal. |
| `<titulo>` | Título descriptivo que identifica el contenido específico de un documento. |
| `<descripcion>` | Descripción breve y representativa del contenido del archivo. |
| `<version>` | Número entero que identifica la versión de una línea base. |
| `<año>` | Año de cursado, cuatro dígitos. Ej.: `2026`. |
| `<cuatrimestre>` | `1c` para el primer cuatrimestre, `2c` para el segundo. |

---

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
