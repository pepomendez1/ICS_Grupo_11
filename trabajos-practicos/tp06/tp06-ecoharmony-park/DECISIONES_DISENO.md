# EcoHarmony Park — Decisiones de Diseño

Ingeniería y Calidad de Software — UTN FRC.
TP 6: Desarrollo Conducido por Pruebas (TDD) — User Story: Comprar entradas.

Este documento justifica las decisiones de diseño tomadas durante la implementación,
siguiendo el ciclo Red → Green → Refactor.

---

## 1. Arquitectura en capas: dominio separado de la web

### Decisión

El dominio de negocio vive exclusivamente en el paquete `parque/` y no importa
nada de Flask ni de ningún detalle de infraestructura. La capa web (`web/`) sí
depende del dominio, pero nunca al revés.

```
parque/config.py      ← constantes del negocio (PO)
parque/calendario.py  ← qué días abre el parque y hasta cuándo se vende
parque/precios.py     ← tarifa de cada entrada según pase y edad
parque/compra.py      ← caso de uso principal: validaciones, entradas, estados
        ↑
web/               ← Flask, repositorio, Mercado Pago, mails, PDF, templates
```

### Por qué

El enunciado pide desarrollar la lógica de la User Story con TDD. Si el dominio
dependiera de Flask o de la base de datos, cada test necesitaría levantar la app
completa. Al separarlo, los 61 tests unitarios de `test_comprar_entradas.py`
(más los 14 de `test_calendario.py`) corren en milisegundos, sin red ni base de
datos.

Esta separación también facilita la trazabilidad: cada criterio de aceptación
de la US tiene su clase de test directamente sobre el dominio, sin pasar por HTTP.

---

## 2. Inyección de dependencias en el servicio

### Decisión

`ServicioCompraEntradas` recibe sus dependencias externas por constructor:

```python
class ServicioCompraEntradas:
    def __init__(
        self,
        calendario: CalendarioParque,
        pasarela_pago: PasarelaMercadoPago,
        notificador: Notificador,
        reloj: Callable[[], datetime] = ahora_en_el_parque,
        compras: Optional[ComprasDelVisitante] = None,
    ):
```

Las dependencias están definidas como `Protocol` (interfaces estructurales de
Python), no como clases abstractas. Esto significa que cualquier objeto con los
métodos correctos satisface la interfaz sin necesidad de herencia explícita.

### Por qué

Esta es la técnica central que hace posible el TDD en este proyecto:

| Dependencia | En producción | En los tests |
|---|---|---|
| `calendario` | `CalendarioEcoHarmony` (reglas reales) | `CalendarioFake` (solo cierra lunes) |
| `pasarela_pago` | `PasarelaMercadoPago` / simulada | `Mock()` con `crear_pago.return_value` |
| `notificador` | `NotificadorGmail` / simulado | `Mock()` — se verifica que se llamó |
| `reloj` | `ahora_en_el_parque()` (hora de Córdoba) | `lambda: HOY` — fecha fija inyectada |
| `compras` | `RepositorioPostgres` / `RepositorioMemoria` | `ComprasFake` (lista en memoria) |

En ningún momento el dominio sabe si está hablando con Mercado Pago de verdad,
con un mock o con la pasarela simulada. Eso lo decide quien construye el servicio.

---

## 3. Configuración centralizada: un único lugar para cambiar las reglas

### Decisión

Todas las constantes del negocio definidas por la PO en la FAQ oficial viven en
`parque/config.py`. El resto del código las lee de ahí; no hay valores hardcodeados
dispersos en otros módulos.

```python
# parque/config.py
DIA_CIERRE = calendar.MONDAY
FERIADOS_CERRADO = {(12, 25), (1, 1)}   # (mes, día), cualquier año
HORA_APERTURA = time(8, 30)
HORA_CIERRE = time(19, 0)
HORIZONTE_MESES = 1
HORA_LIMITE_COMPRA_PARA_HOY = time(17, 30)
CANTIDAD_MAXIMA_ENTRADAS = 10
PRECIOS = {"REGULAR": 10_000, "VIP": 20_000}
DESCUENTOS_POR_EDAD = [
    (0, 3, 100, "Hasta 3 años"),
    (4, 15, 50, "De 4 a 15 años"),
    (60, None, 50, "60 años o más"),
]
```

### Por qué

Cuando la PO confirmó los precios ($10.000 / $20.000) y los descuentos por edad,
el cambio se hizo en un solo archivo. El test `test_cambiar_el_dia_de_cierre_en_la_configuracion_cambia_el_calendario`
en `test_calendario.py` verifica que `monkeypatch`-ear `DIA_CIERRE` impacta
inmediatamente en `CalendarioEcoHarmony`, lo que demuestra que el flujo es
correcto: el calendario lee la config en cada llamada, sin cachear el valor.

---

## 4. Ciclo Red → Green → Refactor

### Decisión

Cada funcionalidad se desarrolló en tres commits separados, con mensajes
prefijados con `test(rojo):`, `feat(verde):` y `refactor:`.

Ejemplo del flujo para los descuentos por edad (FAQ 6, 7 y 21):

1. **`test(rojo)`** — Se escribe `TestPrecios` con casos como
   `test_precio_edad_3_gratis_pasa` (espera `resultado.entradas[0].precio == 0`)
   antes de que `Entrada` tenga el campo `precio`. Los tests fallan.
2. **`feat(verde)`** — Se crea `parque/precios.py` con `tarifa_para(tipo_pase, edad)`,
   se agrega el campo `precio` a `Entrada` y se adapta `ServicioCompraEntradas.comprar`.
   Los tests pasan.
3. **`refactor`** — Se extrae `reglas_de_precio()` para que el formulario web pueda
   calcular el desglose en JavaScript usando las mismas reglas que el backend,
   sin duplicarlas.

Este orden garantiza que las pruebas son las que guían el diseño, no al revés.

---

## 5. Cálculo de precio por entrada individual

### Decisión

El precio se calcula entrada por entrada según la edad del visitante, no como
`cantidad × precio_base`. El resultado queda almacenado en cada `Entrada`:

```python
@dataclass
class Entrada:
    numero: int
    edad: int
    codigo: str
    precio: int = 0      # precio final de esta entrada
    descuento: int = 0   # porcentaje aplicado por la edad
    tarifa: str = ""     # "General", "De 4 a 15 años", ...
```

El monto total de la compra es `sum(e.precio for e in entradas)`.

### Por qué

La FAQ 7 establece descuentos por rango de edad. Para poder mostrar el desglose
en la confirmación, en el mail y en el PDF, cada entrada necesita conocer su
precio individual. Calcularlo solo en el total y distribuirlo después sería
ambiguo cuando hay edades mixtas.

Una consecuencia importante: si todas las entradas tienen precio $0 (por ejemplo,
un grupo de bebés), `ResultadoCompra.sin_cargo` es `True` y el servicio **no
redirige a Mercado Pago**, aunque el visitante haya elegido tarjeta. Esto está
cubierto por el test `test_compra_total_cero_con_tarjeta_no_redirige_mp_pasa`.

---

## 6. Límite de 10 entradas por usuario y fecha (FAQ 27)

### Decisión

El límite de 10 entradas no es por transacción sino **acumulado por usuario para
una fecha de visita**, sumando todas sus compras confirmadas más las pendientes
activas. El servicio consulta el historial antes de aprobar la compra:

```python
def _validar_limite_por_fecha(self, email, fecha, cantidad) -> None:
    for compra in self._compras.compras_para(email, fecha):
        estado = estado_de_compra(compra, ahora)
        if estado == EstadoCompra.CONFIRMADA:
            confirmadas += compra.cantidad
        elif estado == EstadoCompra.PENDIENTE:
            pendientes.append(compra)
    ...
    if cantidad > disponibles:
        raise LimitePorFechaError(mensaje, disponibles, [c.id for c in pendientes])
```

La interfaz `ComprasDelVisitante` (Protocol) desacopla el dominio del repositorio:
en los tests unitarios se usa `ComprasFake` (lista en memoria); en la app real,
el repositorio (Postgres o memoria) implementa el mismo método `compras_para`.

### Por qué

La FAQ 27 especifica que el límite es por persona y fecha, no por compra. Sin esta
validación, un visitante podría hacer diez compras de 10 entradas para el mismo día.

**Compras pendientes:** Una compra con tarjeta aún no aprobada por Mercado Pago
también cuenta para el límite durante **30 minutos** (`VENCIMIENTO_PAGO_MINUTOS`),
igual que la preferencia de MP. Después de ese plazo, la compra vence y libera su
cupo. Esto es un supuesto del equipo, documentado en el README.

**Idempotencia del webhook:** Si Mercado Pago repite la notificación de un pago
ya aprobado, `marcar_compra_pagada` devuelve `False` la segunda vez y el mail con
las entradas no se vuelve a enviar.

---

## 7. Validación de fecha de visita: una sola fuente de verdad

### Decisión

La función `motivo_sin_venta(fecha, ahora, calendario)` en `parque/calendario.py`
es la **única** lógica que decide si una fecha está disponible para compra. La
usan tanto la validación del servicio como la generación del calendario visual:

```
motivo_sin_venta(fecha, ahora, calendario)
    → None si se puede comprar
    → MotivoSinVenta(tipo, mensaje, corto) si no
         tipo: "pasado" | "cerrado" | "horizonte" | "hora_limite"
         mensaje: texto completo para el error del backend
         corto: texto breve para el tooltip del calendario
```

El **orden de prioridad** refleja lo que el visitante ve: primero se informa que
el parque está cerrado (lunes / feriado), y recién después que está fuera del
horizonte de un mes o que ya pasó el horario de venta para hoy. Así, un lunes a
las 20:00 el mensaje dice "el parque cierra los lunes", no "pasó el horario".

### Por qué

Si la validación del formulario y la del servicio fueran independientes, podrían
desincronizarse. Por ejemplo, un visitante que deshabilita el atributo `disabled`
del HTML con las herramientas del navegador y envía un lunes de todos modos: el
backend lo rechaza con el mismo mensaje que mostró el calendario.

---

## 8. Repositorio como adaptador: misma interfaz, dos implementaciones

### Decisión

`RepositorioMemoria` y `RepositorioPostgres` exponen exactamente los mismos
métodos. El resto de la app no sabe cuál está usando: la elección la hace
`crear_repositorio()` en función de si existe `DATABASE_URL`.

```python
def crear_repositorio():
    url = os.environ.get("DATABASE_URL")
    return RepositorioPostgres(url) if url else RepositorioMemoria()
```

Los tests de integración de `test_web.py` reciben el repositorio como fixture y
corren con ambas implementaciones:

```python
@pytest.fixture(params=["memoria", "postgres"])
def repo(request):
    if request.param == "memoria":
        return RepositorioMemoria()
    if not TEST_DATABASE_URL:
        pytest.skip("Definí TEST_DATABASE_URL para probar contra Postgres")
    ...
```

### Por qué

Esto garantiza que la lógica de la web funciona igual con Postgres que en memoria.
Al mismo tiempo, sin `DATABASE_URL` la app arranca sin configuración adicional,
lo que facilita el desarrollo local y los tests en CI.

La conexión a Postgres se reutiliza entre requests (`_conexion()` devuelve la
misma instancia si sigue viva) con un reintento automático ante desconexiones,
necesario porque Vercel puede recibir un request en una instancia que estuvo
dormida con la conexión cortada.

---

## 9. Dobles de prueba: Mocks, Fakes y stubs

### Decisión

Se eligieron distintos tipos de doble según lo que se quiere verificar:

| Doble | Usado para | Ejemplo |
|---|---|---|
| `Mock()` (unittest.mock) | Verificar que se llamó y con qué argumentos | `pasarela_mp`, `notificador` |
| Fake con estado | Simular comportamiento real sin infraestructura | `ComprasFake`, `CalendarioFake` |
| `monkeypatch` | Aislar variables de entorno y constantes de config | `sin_credenciales_reales`, `test_cambiar_el_dia_de_cierre` |
| `lambda: HOY` | Fijar el reloj en un instante concreto | `reloj=lambda: HOY` en el fixture `servicio` |

### Por qué

`Mock` es suficiente para verificar interacciones simples (¿se llamó a
`crear_pago` con los argumentos correctos?). Pero para el historial de compras
del visitante (FAQ 27) necesitamos que el doble tenga comportamiento propio
(filtrar por email y fecha), por lo que se usó `ComprasFake` en lugar de un Mock.

Fijar el reloj con `lambda: HOY` (martes 06/10/2026 a las 10:00, hora de Córdoba)
hace que los tests de fecha y horario sean deterministas independientemente de
cuándo se ejecuten.

---

## 10. Mail y PDF: generación desacoplada del envío

### Decisión

Las funciones `armar_mail_confirmacion` y `armar_mail_entradas` en `web/servicios.py`
devuelven una tupla `(texto_plano, html, imágenes_inline)` sin saber si el
resultado se va a enviar por SMTP o a guardar en la base. El notificador
(real o simulado) decide qué hacer con ellos.

El PDF con las entradas se genera en `web/pdf_entradas.py` con `fpdf2`, incrustando
el logo desde `web/static/logo-mail.png` (PNG generado a partir del SVG porque
Gmail y Outlook no muestran SVG).

### Por qué

Los tests de `test_gmail.py` verifican el contenido del mail (asunto, desglose,
QR inline, que el PDF se adjunta) sin necesidad de una cuenta de Gmail real:
se parchea `smtplib.SMTP` con `Mock` y se inspecciona el mensaje que se habría
enviado. Separar la generación del envío hace esto posible.

---

## 11. Idempotencia y seguridad en el webhook de Mercado Pago

### Decisión

La ruta `/mercadopago/webhook` **nunca confía en el contenido del aviso** de MP
para marcar la compra como pagada. Siempre consulta la API de Mercado Pago con
el id del pago y verifica:

1. Que el estado sea `"approved"`.
2. Que el monto coincida con el de la compra.

Solo si ambas condiciones se cumplen se llama a `acreditar_pago`, que a su vez
llama a `marcar_compra_pagada` (idempotente: devuelve `False` si ya estaba pagada).

### Por qué

Mercado Pago puede repetir la misma notificación varias veces (por reintentos o
errores de red). Gracias a la idempotencia del repositorio, el mail con las
entradas se manda exactamente una vez aunque el webhook llegue tres veces.

Adicionalmente, aceptar el estado directamente del payload del webhook (sin
consultar la API) sería un riesgo de seguridad: cualquiera podría hacer un POST
a `/mercadopago/webhook` con `{"status": "approved"}` y marcar una compra como
pagada sin haber pagado nada.
