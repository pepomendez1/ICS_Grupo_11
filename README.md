# EcoHarmony Park — Comprar entradas (TDD)

Ingeniería y Calidad de Software — UTN FRC.

EcoHarmony Park es un **parque de diversiones** con seis atracciones: calesita,
montaña rusa, rueda de la fortuna, casa del terror, autitos chocadores y hamacas.

| Pase | Incluye |
|---|---|
| Regular | Acceso a las 6 atracciones haciendo la fila común. |
| VIP | Todo lo del Regular, más fila rápida en todas las atracciones y vueltas ilimitadas en la montaña rusa. |

**User story:** COMO visitante QUIERO comprar una entrada PARA asegurar mi visita al parque.

App web en Flask con base de datos en Supabase (Postgres), deployable en Vercel.
La lógica de la compra está separada de la web y se desarrolló con TDD.

## Estructura

```
parque/compra.py                 Lógica de negocio (validaciones de la user story)
web/__init__.py                  App Flask: rutas y pantallas
web/repositorio.py               Persistencia: Postgres (Supabase) o memoria
web/servicios.py                 Calendario del parque, Mercado Pago y mail (reales y simulados)
web/contenido.py                 Textos de atracciones y pases
web/templates/                   Pantallas HTML
supabase/schema.sql              Tablas de la base
app.py                           Entrada para Vercel
run.py                           Entrada para correr local
tests/test_comprar_entradas.py   24 tests unitarios de la user story (TDD) + TestIntegraciones
tests/test_web.py                Tests de integración de la web (incluye webhook de MP)
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

Abrí http://localhost:5001 (no el 5000: en Mac lo ocupa AirPlay). Usuario de prueba: `demo@ecoharmony.com` / `demo123`.

`run.py` lee el archivo `.env` (que **no** se sube a git). Cada variable que
falte cae en una versión local:

| Variable | Si no está |
|---|---|
| `DATABASE_URL` | Todo se guarda en memoria (se pierde al reiniciar). |
| `MP_ACCESS_TOKEN` | Checkout de Mercado Pago simulado. |
| `GMAIL_USER` + `GMAIL_APP_PASSWORD` | El mail no sale: queda solo en **Mis mails**. |

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

## Mercado Pago (Checkout Pro, entorno de prueba)

Sin `MP_ACCESS_TOKEN` la app usa un checkout propio que simula el de Mercado
Pago. Con el token usa `PasarelaMercadoPago` (SDK oficial `mercadopago`):

1. La compra con tarjeta crea una **preferencia** con `external_reference` = id
   de la compra, `back_urls` a `/compras/<id>?mp=success|failure|pending`,
   `auto_return=approved` y `notification_url` = `/mercadopago/webhook`.
2. El visitante paga en Mercado Pago y vuelve a la confirmación. Los query
   params de esa vuelta **no** marcan nada: solo cambian el aviso que se muestra.
3. Mercado Pago llama al **webhook**, que consulta el pago a la API y marca la
   compra como pagada solo si el estado es `approved` y el monto coincide.

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
para volver a la app y para llamar al webhook, así que tiene que ser accesible
desde internet:

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

Sin `GMAIL_USER` y `GMAIL_APP_PASSWORD` el mail de confirmación no sale: se guarda
en la base y se ve en **Mis mails**. Con las dos variables, `NotificadorGmail` lo
manda por `smtp.gmail.com:587` con STARTTLS. Es un mail en HTML con versión de
texto plano que incluye el parque, la cantidad de entradas, la fecha, el tipo de
pase, el total y la forma de pago. También guarda una copia en **Mis mails**.

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

## Trazabilidad criterios ↔ tests

| Criterio de aceptación | Clase | Tests |
|---|---|---|
| Solo usuarios registrados | `TestAcceso` | `sin_estar_logueado_falla`, `usuario_registrado_pasa` |
| Indicar cantidad; no mayor a 10 | `TestCantidad` | `sin_seleccionar_cantidad_falla`, `cero_entradas_falla`, `una_entrada_pasa`, `diez_entradas_pasa`, `once_entradas_falla` |
| Fecha actual o futura; parque abierto | `TestFechaVisita` | `con_fecha_anterior_a_actual_falla`, `fecha_actual_pasa`, `fecha_futura_pasa`, `fecha_parque_cerrado_falla` |
| Edad de cada visitante | `TestDatosVisitantes` | `sin_asignar_edad_todos_visitantes_falla`, `cantidad_edades_no_coincide_cantidad_entradas_falla`, `con_edad_de_todos_los_visitantes_pasa` |
| Tipo de pase (VIP o regular) | `TestTipoPase` | `sin_indicar_tipo_de_pase_falla`, `pase_vip_pasa`, `pase_regular_pasa` |
| Forma de pago; tarjeta redirige a Mercado Pago | `TestFormaPago` | `sin_indicar_forma_de_pago_falla`, `con_tarjeta_redirige_mp_pasa`, `con_efectivo_pasa`, `con_efectivo_no_redirige_mp_pasa` |
| Mail de confirmación; informar cantidad y fecha | `TestConfirmacion` | `exitosa_envia_mail_confirmacion_pasa`, `exitosa_informa_cantidad_y_fecha_pasa`, `fallida_no_envia_mail_falla` |
| Tarjeta redirige a Mercado Pago (referencia); mail de confirmación (detalle) | `TestIntegraciones` | `con_tarjeta_envia_referencia_de_compra_a_mp_pasa`, `exitosa_envia_detalle_de_compra_al_mail_pasa` |

Las integraciones reales tienen sus propios tests, siempre con mocks:
`tests/test_mercadopago.py` (preferencia, consulta de pagos y elección de
pasarela), `tests/test_gmail.py` (SMTP, contenido del mail, fallas y elección de
notificador) y `TestMercadoPago` en `tests/test_web.py` (webhook y vuelta del
checkout).
