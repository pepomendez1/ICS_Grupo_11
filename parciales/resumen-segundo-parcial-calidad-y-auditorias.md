# Resumen 2º parcial — Calidad, revisiones técnicas y auditorías

**Asignatura:** Ingeniería y Calidad de Software
**Unidad 4:** Aseguramiento de Calidad de Proceso y de Producto
**Fuentes:** diapositivas de la cátedra [`13-ppqa-introduccion.pdf`](../material-teorico/diapositivas/13-ppqa-introduccion.pdf), [`14-revisiones-tecnicas.pdf`](../material-teorico/diapositivas/14-revisiones-tecnicas.pdf) y [`15-auditorias-de-software.pdf`](../material-teorico/diapositivas/15-auditorias-de-software.pdf)

---

## 1. Conceptos generales de calidad (PPQA)

**Calidad:** todos los aspectos y características de un producto o servicio que se relacionan con su habilidad de alcanzar las necesidades manifiestas o implícitas. Es **relativa** a las personas, las circunstancias y el tiempo.

Un software de calidad satisface las expectativas del **cliente**, del **usuario**, de la **gerencia**, del **equipo de desarrollo y mantenimiento** y de otros interesados.

### Principios de calidad
- La calidad **no se inyecta ni se compra: debe estar embebida**.
- Es un esfuerzo de todos; las **personas son la clave** (capacitación).
- Necesita sponsor gerencial, pero se puede empezar por uno y liderar con el ejemplo.
- **No se puede controlar lo que no se mide.**
- Simplicidad: empezar por lo básico.
- El aseguramiento de la calidad **debe planificarse**.
- **Aumentar las pruebas no aumenta la calidad.**
- Debe ser razonable para el negocio.

### Visiones de la calidad
Del usuario · De manufactura · Del producto · Basada en el valor · Trascendental.

### Calidad de producto vs. calidad de proceso
- **Producto:** ISO/IEC 25000 (ISO 25010: calidad de producto y calidad en uso). Características de producto: adecuación funcional, eficiencia de desempeño, compatibilidad, usabilidad, fiabilidad, seguridad, mantenibilidad y portabilidad. Otros modelos: McCall y Barbacci (SEI).
- **Proceso:** el proceso es **el único factor "controlable"** para mejorar la calidad del software y el rendimiento de la organización. Proceso = personas (habilidades, entrenamiento, motivación) + procedimientos y métodos + herramientas y equipos.

> "Lo que no está controlado no está hecho" (Watts Humphrey).

### Actividades de la administración de calidad
| Actividad | Qué hace |
|---|---|
| **Aseguramiento de calidad** | Establece estándares y procedimientos organizacionales de calidad. |
| **Planificación de calidad** | Selecciona y adapta los estándares y procedimientos para un proyecto (plan de calidad). |
| **Control de calidad** | Asegura que el equipo respete esos estándares y procedimientos (revisiones de calidad y evaluaciones o mediciones automáticas). |

- El **Grupo de Aseguramiento de Calidad (GAC)** **no debería reportar al Gerente de Proyecto**.
- Estándares de **producto**: características que deben tener los componentes (ej.: estilo de programación). Estándares de **proceso**: cómo se implementan los procesos.

### Modelos de mejora de procesos
- **SPICE** (Software Process Improvement Capability Evaluation).
- **IDEAL**: **I**nitiating → **D**iagnosing → **E**stablishing → **A**cting → **L**earning/Leveraging.

### CMMI (Capability Maturity Model Integration)
- Evolución del SW-CMM. Lo creó el **SEI** (Carnegie Mellon, fundado por el DoD de EE.UU. en 1984). Desde 2020 pertenece a **ISACA**, versión vigente **2.0**.
- **No es una norma y no se "certifica"**: se **evalúa** a través de *Lead Appraisers*.
- **Constelaciones:** CMMI-DEV (desarrollo), CMMI-SVC (servicios), CMMI-ACQ (adquisiciones).
- **Representaciones:**

| Por etapas | Continua |
|---|---|
| Niveles **1 a 5** de **madurez organizacional** | Niveles **0 a 5** de **capacidad** por área de proceso |
| Clasificación única, permite comparar organizaciones | Permite comparar por área y elegir el orden de las mejoras |

- **Niveles de madurez (por etapas):**
  1. **Inicial**: procesos impredecibles, pobremente controlados, reactivos.
  2. **Administrado**: procesos caracterizados por proyecto; a menudo reactivo. Áreas: Administración de Requerimientos, Planificación de Proyectos, Monitoreo y Control, Acuerdos con Proveedores, Medición y Análisis, **PPQA** y **Administración de Configuración**.
  3. **Definido**: procesos caracterizados por la organización; proactivo.
  4. **Cuantitativamente administrado**: procesos medidos y controlados.
  5. **Optimizado**: foco en la mejora continua de procesos.
- **CMMI vs. Ágil:** hay áreas de CMMI que el ágil soporta, otras neutrales y otras en conflicto. CMMI apunta a la predictibilidad y la estabilidad; ágil, a la performance y la velocidad. Ambos buscan organizaciones de alto desempeño, ambos planifican y ninguno es aplicable a "cualquier proyecto".

---

## 2. Revisiones técnicas

### Verificación y validación (V&V)
- **Validación:** ¿estamos construyendo **el producto correcto**?
- **Verificación:** ¿estamos construyendo **el producto correctamente**?
- Es un proceso de **todo el ciclo de vida**: empieza con la revisión de requerimientos y sigue con diseño, código y prueba.
- **Debe planificarse** y comenzar en etapas tempranas: **el costo de reparar una falla crece en cada etapa**.
- El retrabajo evitable es el **40–50 %** del desarrollo.

### Clasificación de fallas
| Tipo | Descripción |
|---|---|
| **Mayor** | Puede causar una falla operacional o un resultado inesperado (en requerimientos: ambigüedad o información faltante que no cumple la necesidad del cliente). |
| **Menor** | No deseable, pero no causa una falla operacional (ej.: violar estándares de codificación, un requerimiento no comprobable). |
| **Cosmético** | Tipeo, ortografía, gramática; no se cuenta como falla. |

### Revisiones técnicas: características
- Son **V&V estático**: **no requieren ejecutar el programa**.
- Objetivo: **detectar defectos y corregirlos en etapas tempranas**.
- Origen: **Fagan (1976)**, con las inspecciones.
- Se puede inspeccionar **cualquier representación legible** del software, incluso versiones incompletas.
- **Desventajas:** cuesta introducirlas, recargan costos al inicio y parecen ralentizar el desarrollo.

### Tipos
| Walkthrough (recorrida) | Inspección |
|---|---|
| Informal, mínima sobrecarga, poca o ninguna preparación | Proceso **formal**, con checklists |
| Sirve para capacitar y da un retorno rápido | Busca detectar y remover **todos** los defectos |
| No toma mediciones (no es una revisión técnica formal) | Toma **métricas** útiles en todo el ciclo de vida |

### Inspección: roles
**Autor** (creador del producto; inicia el proceso) · **Moderador** (planifica y lidera, entrega el material unas 48 h antes y hace el seguimiento) · **Lector** (lee el producto) · **Anotador** (registra los hallazgos) · **Inspector** (examina el producto antes de la reunión).

### Inspección: proceso
**Planificación → Visión general → Preparación individual → Reunión de inspección → Corrección → Seguimiento**

- Reunión de **2 horas como máximo**.
- **Decisión:** aceptar sin modificaciones, aceptar provisoriamente o rechazar.
- **Informe:** qué se revisó, quién lo revisó, qué se encontró y conclusiones.

### Las inspecciones SON / NO SON
| Son | No son |
|---|---|
| La forma más barata y efectiva de encontrar fallas | Para encontrar **soluciones** a las fallas |
| Una fuente de métricas para el proyecto | Para obtener la **aprobación** de un producto |
| Una forma de compartir conocimiento y promover el trabajo en grupo | Para **evaluar el desempeño** de las personas |

### Métricas sugeridas
- **Densidad de defectos** = total de defectos / tamaño.
- **Total de defectos** = defectos mayores + menores.
- **Esfuerzo de inspección** = planificación + preparación + reunión + retrabajo.
- **Esfuerzo por defecto** = esfuerzo de inspección / total de defectos.
- **Porcentaje de reinspecciones** = reinspecciones / inspecciones.

> **Revisar el producto, no al productor.**

---

## 3. Auditorías de software

**Auditoría de calidad de software** (IEEE Std 1028): evaluación **independiente** de los productos o procesos de software para asegurar el cumplimiento de estándares, lineamientos, especificaciones y procedimientos, basada en un criterio objetivo.

**¿Por qué auditar?** Da una opinión **objetiva e independiente**, identifica áreas de posible insatisfacción del cliente, le asegura al cliente que se cumplen sus expectativas e identifica oportunidades de mejora.

### Tipos de auditoría
| Tipo | Qué valida |
|---|---|
| **De proyecto** | El **cumplimiento del proceso** de desarrollo. Se planifica en el PACS (Plan de Aseguramiento de Calidad de Software). |
| **De configuración funcional** | Que el producto **cumpla con sus requerimientos**: compara el software construido con la ERS. Se valida la matriz de rastreabilidad. |
| **De configuración física** | Que el ítem de configuración, **tal como está construido**, sea consistente con la **documentación técnica** que lo describe. |

### Roles
| Rol | Responsabilidades |
|---|---|
| **Gerente de SQA** | Prepara el plan de auditorías, calcula el costo, asigna recursos y resuelve las no conformidades. |
| **Auditor** | Acuerda fecha y alcance, recolecta evidencia objetiva, realiza la auditoría, prepara el reporte y sigue los planes de acción. |
| **Auditado** | Participa, aporta evidencia, responde al reporte, propone el plan de acción y comunica su cumplimiento. |

### Proceso de auditoría
1. **Preparación y planificación**: alcance, objetivo, fecha, participantes y documentación.
2. **Ejecución**: reunión de apertura, preguntas y pedido de evidencia, checklist.
3. **Análisis y reporte del resultado**: evaluación, reunión de cierre y reporte final.
4. **Seguimiento**: plan de acción, verificación y cierre de las desviaciones.

### Tipos de resultados
| Resultado | ¿Requiere plan de acción? |
|---|---|
| **Buenas prácticas**: algo hecho mucho mejor de lo esperado | No |
| **Desviaciones**: incumplimiento de requerimientos o del proceso definido | **Sí** |
| **Observaciones**: condiciones a mejorar o que pueden derivar en una futura desviación | No |

- **Técnicas y herramientas:** checklist, muestreo, revisión de registros y herramientas automatizadas.
- **Métricas de auditoría:** esfuerzo por auditoría, cantidad de desviaciones, duración, desviaciones por área de proceso de CMMI.

---

## Para recordar
- **Verificación** = producto correctamente; **validación** = producto correcto.
- **Revisiones** = estáticas, sin ejecutar; **testing** = dinámico.
- Las **3 auditorías**: de proyecto, de configuración funcional (vs. requerimientos) y de configuración física (vs. documentación).
- **CMMI no se certifica, se evalúa.** Nivel 2 incluye PPQA y Administración de Configuración.
