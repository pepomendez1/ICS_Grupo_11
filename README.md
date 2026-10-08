# EcoHarmony Park — Comprar entradas (TDD)

Ingeniería y Calidad de Software — UTN FRC.

EcoHarmony Park es un **bioparque**: animales, exhibiciones y senderos en tres
sectores (terrestre, acuático y aéreo), con horarios de alimentación. Las
actividades Tirolesa, Safari, Palestra y Jardinería tienen inscripción aparte:
no se venden ni se incluyen en el pase.

| Pase | Incluye | Precio |
|---|---|---|
| Regular | Acceso al parque, senderos y exhibiciones. | $50.000 |
| VIP | Lo mismo, con ingreso por fila preferencial. | $75.000 |

Precios, día de cierre, cantidad máxima y edad máxima están en un solo lugar:
las constantes del principio de `parque/compra.py`. Ver
[Supuestos a confirmar con la PO](#supuestos-a-confirmar-con-la-po).

**User story:** COMO visitante QUIERO comprar una entrada PARA asegurar mi visita al parque.

App web en Flask con base de datos en Supabase (Postgres), deployable en Vercel.
La lógica de la compra está separada de la web y se desarrolló con TDD.

## Estructura

```
parque/compra.py                 Lógica de negocio (validaciones de la user story)
web/__init__.py                  App Flask: rutas y pantallas
web/repositorio.py               Persistencia: Postgres (Supabase) o memoria
web/servicios.py                 Calendario del parque, Mercado Pago y mail (reales y simulados)
web/contenido.py                 Textos del bioparque: sectores, actividades y pases
web/entradas.py                  URL, QR (segno) y estado de cada entrada
web/templates/                   Pantallas HTML
supabase/schema.sql              Tablas de la base
app.py                           Entrada para Vercel
run.py                           Entrada para correr local
tests/test_comprar_entradas.py   Tests unitarios de la user story (los 24 originales + los agregados)
tests/test_calendario.py         Día de cierre configurable
tests/test_web.py                Tests de integración de la web (webhook, entradas, QR, bandeja)
tests/test_mercadopago.py        PasarelaMercadoPago con el SDK mockeado
tests/test_gmail.py              NotificadorGmail con smtplib mockeado
```

## Correrlo local

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # descomentá y completá lo que quieras usar (todo es opcional)
python run.py
```

Abrí http://localhost:5001 (no el 5000: en Mac lo ocupa AirPlay) y creá una cuenta en
**Crear cuenta** para poder comprar.

`run.py` lee el archivo `.env` (que **no** se sube a git). Cada variable que
falte cae en una versión local:

| Variable | Si no está |
|---|---|
| `DATABASE_URL` | Todo se guarda en memoria (se pierde al reiniciar). |
| `MP_ACCESS_TOKEN` | Checkout de Mercado Pago simulado. |
| `GMAIL_USER` + `GMAIL_APP_PASSWORD` | El mail no sale: queda solo en **Mis mails**. |
| `APP_BASE_URL` | Los QR de las páginas apuntan a la URL con la que abriste la app; los de los mails, a `http://localhost:5001`. |

## Tests

```bash
pytest -v
```

- Unitarios: Mercado Pago y el mail se reemplazan con `Mock`, el calendario con un
  fake (cierra los lunes) y la fecha actual se inyecta fija (06/10/2026).
- Web: recorren el flujo completo por HTTP. Por defecto usan memoria; si definís
  `TEST_DATABASE_URL` (una base de prueba, **no** la de producción, porque se vacía)
  corren también contra Postgres.

Para correr un solo grupo: `pytest -v -k TestCantidad`.

## Deploy: Supabase + Vercel

### 1. Supabase

1. Creá un proyecto en https://supabase.com (región São Paulo, la más cercana).
2. Copiá la connection string desde **Connect** → **Transaction pooler** (puerto 6543)
   y reemplazá `[YOUR-PASSWORD]` por la contraseña del proyecto.
   Tiene que ser la del pooler: la conexión directa es solo IPv6 y Vercel no llega.
3. Las tablas se crean solas la primera vez que arranca la app. Si preferís
   crearlas a mano, pegá `supabase/schema.sql` en el **SQL Editor**.

### 2. Vercel

1. Subí el proyecto a un repo de GitHub.
2. En https://vercel.com → **Add New Project** → importá el repo.
   Vercel detecta Flask por el `app.py`.
3. En **Environment Variables** cargá:
   - `DATABASE_URL`: la connection string del paso anterior.
   - `SECRET_KEY`: un texto largo y aleatorio. Tiene que ser fijo, si no se
     pierde la sesión entre requests.
   - `MP_ACCESS_TOKEN` y `APP_BASE_URL`: ver [Mercado Pago](#mercado-pago-checkout-pro-entorno-de-prueba).
   - `GMAIL_USER` y `GMAIL_APP_PASSWORD`: ver [Mail con Gmail](#mail-con-gmail).
4. **Deploy**.

Si cambiás una variable después del deploy, hay que hacer **Redeploy** para que
la tome.

## Entradas con QR

Cada entrada de una compra es individual: si comprás 3, se generan 3, cada una
con la edad de su visitante y un código propio (`secrets.token_urlsafe`, no se
puede adivinar). Se guardan en la tabla `entradas` y el QR apunta a
`{APP_BASE_URL}/entradas/<codigo>`, una página pública con el parque, la fecha,
el tipo de pase, la edad, el número de entrada (por ejemplo, 1 de 3) y el estado:

| Forma de pago | Estado | QR |
|---|---|---|
| Efectivo | Válida · Pagar en boletería | Sí |
| Tarjeta, pago pendiente | Esperando confirmación del pago | No |
| Tarjeta, aprobada por el webhook | Válida · Pagada con Mercado Pago | Sí |
| Tarjeta, rechazada o cancelada | Compra cancelada · Entrada no válida | No |

La confirmación de la compra muestra las entradas como tickets con talón y se
pueden imprimir. Los QR se generan con `segno` (Python puro, sin Pillow).

Mails:

- **Efectivo:** el mail de confirmación incluye los QR.
- **Tarjeta:** el mail de confirmación dice "pago pendiente de confirmación".
  Cuando el webhook aprueba el pago se manda un segundo mail, **Tus entradas**,
  con los QR (una sola vez, aunque Mercado Pago repita la notificación).
- Los QR van como imágenes inline con `Content-ID` (no como `data:` URI) y el
  remitente es `EcoHarmony Park <GMAIL_USER>`.

## Mercado Pago (Checkout Pro, entorno de prueba)

Sin `MP_ACCESS_TOKEN` la app usa un checkout propio que simula el de Mercado
Pago. Con el token usa `PasarelaMercadoPago` (SDK oficial `mercadopago`):

1. La compra con tarjeta crea una **preferencia** con `external_reference` = id
   de la compra, `back_urls` a `/compras/<id>?mp=success|failure|pending`,
   `auto_return=approved` y `notification_url` = `/mercadopago/webhook`.
2. El visitante paga en Mercado Pago y vuelve a la confirmación. Esa vuelta
   (`?mp=...`) **nunca** marca la compra como pagada; solo decide qué se muestra:

   | Vuelta | Pantalla |
   |---|---|
   | `success` | "¡Listo, te esperamos!"; los QR aparecen cuando llega el webhook. |
   | `pending` | "Tu pago está pendiente": sin error ni QR; las entradas llegan por mail al aprobarse. |
   | `failure` (rechazado o volvió sin pagar) | "No se pudo completar el pago". La compra queda `rechazada` (columna `compras.estado`), sus entradas no son válidas y el botón **Volver e intentar de nuevo** abre `/comprar` precargado. Al confirmar se crea una compra nueva. |

   Lo guardado manda sobre el query param: si el webhook ya aprobó el pago, se
   muestra aprobada aunque la vuelta diga `failure`.
3. Mercado Pago llama al **webhook**, que consulta el pago a la API y marca la
   compra como pagada solo si el estado es `approved` y el monto coincide. Si
   MP termina cobrando una compra que había quedado rechazada (por ejemplo, un
   medio de pago que se acredita tarde), el cobro manda: la compra vuelve a ser
   válida y se mandan las entradas.

### Cómo obtener las credenciales

1. Entrá a https://www.mercadopago.com.ar/developers/panel/app con tu cuenta y
   creá una aplicación (producto: **Checkout Pro**, pagos online).
2. En **Cuentas de prueba** creá dos usuarios: uno **vendedor** y uno **comprador**.
   Anotá usuario y contraseña de cada uno.
3. Abrí una ventana de incógnito, iniciá sesión con el **vendedor de prueba**,
   creá una aplicación igual que en el paso 1 y copiá su **Access Token** de
   **Credenciales de producción**. Es de una cuenta de prueba, así que no
   mueve plata real. Ese valor va en `MP_ACCESS_TOKEN`.
   Si tu panel todavía te da credenciales que empiezan con `TEST-`, también
   sirven: la app usa automáticamente el checkout de sandbox.
4. Para pagar, iniciá sesión en el checkout con el **comprador de prueba** y
   usá una tarjeta de prueba, por ejemplo Mastercard `5031 7557 3453 0604`,
   CVV `123`, vencimiento `11/30`. En el nombre del titular poné `APRO` para un
   pago aprobado u `OTHE` para uno rechazado.

`APP_BASE_URL` es la URL pública de la app, sin `/` al final. Mercado Pago la usa
para volver a la app y para llamar al webhook, y los QR de las entradas apuntan
a ella, así que tiene que ser accesible desde internet:

- **Vercel:** la URL de producción, por ejemplo `https://ecoharmony-park.vercel.app`.
  No uses la URL de un deploy puntual (`...-git-xxx.vercel.app`): esas están
  protegidas por Vercel y Mercado Pago recibe un 401.
- **Local:** levantá un túnel con `ngrok http 5001` y usá la URL `https://...`
  que te da. Con `localhost` Mercado Pago no puede llamar al webhook y la compra
  queda pendiente.

### Cargarlas en Vercel

**Settings** → **Environment Variables** → agregá `MP_ACCESS_TOKEN` y
`APP_BASE_URL` para el entorno **Production** → **Redeploy**.

## Mail con Gmail

Sin `GMAIL_USER` y `GMAIL_APP_PASSWORD` los mails no salen: se guardan en la base
y se ven en **Mis mails** (la bandeja simulada, con su link en el menú y su botón
en la confirmación). Con las dos variables, `NotificadorGmail` los manda por
`smtp.gmail.com:587` con STARTTLS, en HTML con versión de texto plano: parque,
cantidad de entradas, fecha, tipo de pase, total, forma de pago y los QR (ver
[Entradas con QR](#entradas-con-qr)). Con Gmail real la bandeja simulada
desaparece: no hay link ni botón y `/mails` devuelve 404.

Si Gmail falla (contraseña mal, sin red, límite diario), el error queda en el log
(`No se pudo enviar el mail de confirmación a ...`) y la compra se completa igual.

### Cómo obtener las credenciales

1. Usá una cuenta de Gmail para el parque. Conviene que sea una nueva y no la
   personal.
2. Activá la **verificación en 2 pasos** en https://myaccount.google.com/security.
   Sin ella Google no deja crear contraseñas de aplicación.
3. Entrá a https://myaccount.google.com/apppasswords, creá una con el nombre
   `EcoHarmony Park` y copiá los 16 caracteres que te muestra. Se ve una sola vez.
4. `GMAIL_USER` es la dirección completa (`algo@gmail.com`) y
   `GMAIL_APP_PASSWORD` es esa contraseña de aplicación (con o sin espacios).
   **No** es la contraseña de la cuenta.

Gmail permite unos 500 envíos por día, que alcanza para el TP.

### Cargarlas en Vercel

**Settings** → **Environment Variables** → agregá `GMAIL_USER` y
`GMAIL_APP_PASSWORD` → **Redeploy**. Si los mails no llegan, buscá el error en
**Logs** del proyecto.

## Supuestos a confirmar con la PO

| Tema | Supuesto actual | Dónde se cambia |
|---|---|---|
| Precios | Regular $50.000 y VIP $75.000 por entrada, iguales para todas las edades. | `PRECIOS` en `parque/compra.py` |
| Día de cierre | Cierra los lunes. También están cerrados el 25/12 y el 1/1. | `DIA_CIERRE` en `parque/compra.py`; feriados en `CalendarioEcoHarmony` |
| Para qué se usa la edad | Hoy solo se pide y queda en cada entrada. ¿Hay precio diferencial por edad (menores, jubilados, bebés sin cargo)? ¿Alguna actividad o sector tiene edad mínima? | `ServicioCompraEntradas.comprar` |
| Límite de edad | Se aceptan edades de 0 a 150 años. ¿Hay un mínimo? ¿Un bebé ocupa una de las 10 entradas? | `EDAD_MAXIMA` en `parque/compra.py` |
| Contenido | Las descripciones de los sectores y actividades y los horarios de alimentación son textos de ejemplo. | `web/contenido.py` |
| Uso de la entrada | El QR identifica la entrada pero no se marca como "usada" en el ingreso. | Fuera del alcance de esta user story |

## Trazabilidad criterios ↔ tests

| Criterio de aceptación | Clase | Tests |
|---|---|---|
| Solo usuarios registrados | `TestAcceso` | `sin_estar_logueado_falla`, `usuario_registrado_pasa` |
| Indicar cantidad; no mayor a 10 | `TestCantidad` | `sin_seleccionar_cantidad_falla`, `cero_entradas_falla`, `una_entrada_pasa`, `diez_entradas_pasa`, `once_entradas_falla` |
| Fecha actual o futura; parque abierto | `TestFechaVisita` | `con_fecha_anterior_a_actual_falla`, `fecha_actual_pasa`, `fecha_futura_pasa`, `fecha_parque_cerrado_falla` |
| Edad de cada visitante (entre 0 y 150) | `TestDatosVisitantes` | `sin_asignar_edad_todos_visitantes_falla`, `cantidad_edades_no_coincide_cantidad_entradas_falla`, `con_edad_de_todos_los_visitantes_pasa`, `edad_negativa_falla`, `edad_cero_pasa`, `edad_150_pasa`, `edad_151_falla` |
| Tipo de pase (VIP o regular) | `TestTipoPase` | `sin_indicar_tipo_de_pase_falla`, `pase_vip_pasa`, `pase_regular_pasa` |
| Forma de pago; tarjeta redirige a Mercado Pago | `TestFormaPago` | `sin_indicar_forma_de_pago_falla`, `con_tarjeta_redirige_mp_pasa`, `con_efectivo_pasa`, `con_efectivo_no_redirige_mp_pasa` |
| Mail de confirmación; informar cantidad y fecha | `TestConfirmacion` | `exitosa_envia_mail_confirmacion_pasa`, `exitosa_informa_cantidad_y_fecha_pasa`, `fallida_no_envia_mail_falla` |
| Tarjeta redirige a Mercado Pago (referencia); mail de confirmación (detalle) | `TestIntegraciones` | `con_tarjeta_envia_referencia_de_compra_a_mp_pasa`, `exitosa_envia_detalle_de_compra_al_mail_pasa` |
| Tipo de pase (precio de cada pase) | `TestPrecios` | `tres_entradas_regulares_cobra_150000_pasa`, `dos_entradas_vip_cobra_150000_pasa` |
| Indicar la edad de cada visitante (una entrada por visitante) | `TestEntradas` | `genera_tres_entradas_con_la_edad_de_cada_visitante_pasa`, `cada_una_tiene_codigo_unico_pasa`, `codigo_no_adivinable_pasa` |

La validación de la edad también está probada de punta a punta en
`tests/test_web.py`: `test_web_backend_rechaza_edad_151_aunque_se_saltee_el_html`
(un POST directo, sin los `min`/`max` del formulario) y
`test_web_inputs_de_edad_limitan_entre_0_y_150`.

Las integraciones reales tienen sus propios tests, siempre con mocks:
`tests/test_mercadopago.py` (preferencia, consulta de pagos y elección de
pasarela), `tests/test_gmail.py` (SMTP, contenido del mail, fallas y elección de
notificador, QR inline) y en `tests/test_web.py`: `TestMercadoPago` (webhook y
vuelta del checkout), `TestEntradasConQR`, `TestMailTusEntradas`,
`TestBandejaSimulada`, `TestBioparque` y `TestSinUsuarioDemo`.
