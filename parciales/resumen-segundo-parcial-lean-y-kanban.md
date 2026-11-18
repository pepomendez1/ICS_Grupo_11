# Resumen 2º parcial — Filosofía Lean y Método Kanban

**Asignatura:** Ingeniería y Calidad de Software
**Unidad 2:** Gestión Lean Agile de Productos de Software
**Fuente:** diapositivas de la cátedra [`11-lean-y-kanban.pdf`](../material-teorico/diapositivas/11-lean-y-kanban.pdf)

---

## 1. Filosofía Lean

### Principios Lean
1. **Eliminar desperdicios**
2. **Amplificar el aprendizaje**
3. **Embeber la integridad conceptual**
4. **Diferir compromisos** (decidir lo más tarde posible, con más información)
5. **Dar poder al equipo**
6. **Ver el todo**
7. **Entregar lo antes posible**

### Tipos de desperdicio
| Tipo | Qué es | Qué hacer |
|---|---|---|
| Tipo 1 | Desperdicio **necesario** | Minimizarlo |
| Tipo 2 | **Puro** desperdicio | Evitarlo |

### Los 7 (+1) desperdicios: manufactura vs. software
| Manufactura | Servicios basados en conocimiento (software) |
|---|---|
| Inventario | Trabajo parcialmente terminado |
| Sobreproducción | Características extra |
| Proceso extra | Proceso extra |
| Transporte | Transferencia de conocimiento |
| Movimiento | Cambio de tareas / cambio de contexto (seteo) |
| Esperas | Esperas / demoras |
| Defectos | Defectos |
| **+1:** Talento no utilizado | Talento no utilizado |

---

## 2. Kanban

### ¿Qué es?
Un **método para definir, gestionar y mejorar servicios que entregan trabajo del conocimiento** (servicios profesionales, actividades creativas, diseño de productos de software o físicos).

- *Kan-ban* (看板) = **tarjeta de señal**.
- **Origen:** Toyota, a fines de 1940, estudiando cómo los supermercados reponían stock → **Just in Time**.
- Es un sistema **pull, no push**: el trabajo se "tira" cuando hay capacidad, no se "empuja".
- El foco está en el **flujo de punta a punta**, centrado en el cliente.

### Valores (9)
Transparencia · Equilibrio · Colaboración · Foco en el cliente · Flujo · Liderazgo · Entendimiento · Acuerdo · Respeto.

### Principios
**Gestión del cambio**
- Comenzar con lo que hacés ahora (entender el proceso actual tal como es).
- Acordar la búsqueda de la mejora a través del **cambio evolutivo**.
- Fomentar actos de liderazgo en todos los niveles.

**Entrega de servicios**
- Comprender y enfocarse en las necesidades y expectativas del cliente.
- Gestionar el trabajo y dejar que las personas se autoorganicen en torno a él.
- Revisar periódicamente la red de servicios y sus políticas para mejorar los resultados.

> Kanban **respeta los roles, responsabilidades y puestos actuales**: no impone un proceso nuevo.

### Prácticas generales
1. **Visualizar** el trabajo: todos ven la misma imagen → decisiones más rápidas y colaborativas.
2. **Limitar el WIP** (trabajo en progreso): límites explícitos de ítems por estado del flujo.
   - Al 100 % de ocupación el rendimiento es mínimo (como una autopista en hora pico).
   - Importa más el **flujo** que tener a todos ocupados.
   - Limitar el WIP provoca conversación y mejora.
3. **Gestionar el flujo**: buscar un flujo suave y predecible a ritmo sostenido; medirlo sirve para gestionar expectativas, predecir y mejorar.
4. **Hacer explícitas las políticas**: acordadas por todos (cliente, interesados y equipo) y expuestas en un lugar visible. Deben ser **pocas, sencillas, bien definidas, visibles, aplicables en todo momento y fácilmente modificables** por quienes prestan el servicio.
5. **Mejorar colaborativamente**, con experimentos basados en modelos y en el método científico, en entornos donde fallar es seguro. Si el resultado no es bueno, se vuelve fácilmente al estado anterior.

### ¿Cómo aplicar Kanban?
| Paso | Qué implica |
|---|---|
| **Proceso** | Modelar el proceso real como columnas del tablero (ej.: Cola de producto → Análisis → Desarrollo → Listo para build → Testing → Producción, con subcolumnas *En progreso / Hecho*). |
| **Trabajo** | Decidir la unidad de trabajo y los **tipos de trabajo** (US, defectos, mantenimiento, mejoras…), asignando capacidad según la demanda (ej.: 60 % casos de uso, 30 % mantenimiento, 10 % defectos). |
| **Límites de WIP** | Definir el WIP de cada columna. |
| **Políticas** | Definir políticas de calidad: reposición del tablero, criterio de "terminado" de cada estado, límites de WIP, clases de servicio, cadencia de reuniones. |
| **Cuellos de botella y flujo** | Mover recursos a los cuellos de botella. |
| **Clases de servicio** | Cada tipo de trabajo con sus propias políticas y su definición de "hecho". |
| **Cadencia** | Releases, planificaciones y revisiones. |

### Clases de servicio (ejemplo de la cátedra)
| Clase | Color de tarjeta | Política |
|---|---|---|
| **Expreso** | Blanco | WIP = 1; tiene capacidad reservada; puede exceder el límite de WIP; los demás trabajos esperan; puede tener una entrega especial a producción. |
| **Fecha fija** | Rosa | Queda en la cola hasta que convenga que ingrese; respeta el WIP; si la fecha está en riesgo, puede **promoverse a Expreso**. |
| **Estándar** | Amarillo | Respeta el WIP; FIFO si no hay Expresos o de Fecha fija; se prioriza por valor de negocio. |
| **Intangible** | Verde | Respeta el WIP; FIFO si no hay Expresos o de Fecha fija; se prioriza por valor de negocio. |

---

## 3. Métricas en Kanban

| Métrica | Definición | Vista |
|---|---|---|
| **Lead Time** | Tiempo desde que **se pide** un ítem hasta que **se entrega**. Mide el ritmo de entrega. | **Del cliente** |
| **Cycle Time** | Tiempo entre el **inicio y el fin del proceso** para un ítem. Mide la capacidad del proceso (ritmo de terminación). | **Interna** |
| **Touch Time** | Tiempo en que el ítem fue **realmente trabajado** (en columnas de trabajo en curso, no en colas ni bloqueado). | Interna |
| **Eficiencia del ciclo de proceso** | **Touch Time / Elapsed Time** (en %) | Interna |

### Métricas orientadas a servicio
- **Expectativa** de nivel de servicio: lo que el cliente espera.
- **Capacidad** de nivel de servicio: lo que el sistema puede entregar.
- **Acuerdo** de nivel de servicio: lo pactado con el cliente.
- **Umbral** de adecuación del servicio: el nivel por debajo del cual el servicio es inaceptable para el cliente.

---

## Para recordar
- Lean = **eliminar desperdicios**. Kanban = **visualizar, limitar el WIP y gestionar el flujo**.
- Kanban **no** prescribe roles ni iteraciones: se empieza desde el proceso actual y se mejora de forma evolutiva.
- **Lead Time ≥ Cycle Time**: el Lead Time incluye la espera antes de empezar.
