# EcoHarmony Park — Comprar entradas (TDD)

Ingeniería y Calidad de Software — UTN FRC.

EcoHarmony Park es un **bioparque**: animales, exhibiciones y senderos en tres
sectores (terrestre, acuático y aéreo), con horarios de alimentación. Abre de
martes a domingo, de 8:30 a 19:00. Las actividades Tirolesa, Safari, Palestra y
Jardinería tienen inscripción aparte (otra user story): no se venden ni se
incluyen en el pase.

| Pase | Incluye | Precio por entrada |
|---|---|---|
| Regular | Acceso al parque, senderos y exhibiciones. | $10.000 |
| VIP | Lo mismo: la única diferencia es el precio. | $20.000 |

Descuento por visitante según la edad: hasta 3 años sin cargo; de 4 a 15 años y
desde 60 años, 50% off.

Todas las reglas del negocio están en un solo módulo, `parque/config.py`. Ver
[Definiciones de la PO](#definiciones-de-la-po).

**User story:** COMO visitante QUIERO comprar una entrada PARA asegurar mi visita al parque.

App web en Flask con base de datos en Supabase (Postgres), deployable en Vercel.
La lógica de la compra (`parque/`) está separada de la web y se desarrolló con TDD.

Las decisiones de diseño del proyecto (arquitectura en capas, inyección de
dependencias, ciclo TDD, dobles de prueba y más) están documentadas en
[`DECISIONES_DISENO.md`](DECISIONES_DISENO.md).

## Estructura

```
parque/config.py                 Definiciones de la PO: calendario, horario, precios, descuentos, límites
parque/calendario.py             Qué días abre el parque y para qué fechas se venden entradas
parque/precios.py                Tarifa de cada entrada según pase y edad
parque/compra.py                 Caso de uso "comprar entradas": validaciones, entradas y estados
web/__init__.py                  App Flask: rutas y pantallas
web/repositorio.py               Persistencia: Postgres (Supabase) o memoria
web/servicios.py                 Mercado Pago y mail (reales y simulados)
web/pdf_entradas.py              PDF con las entradas (fpdf2)
web/calendario_compra.py         Arma la grilla del calendario de compra (solo presentación)
web/entradas.py                  URL, QR (segno) y estado de cada entrada
web/contenido.py                 Textos del bioparque: sectores, actividades y pases
web/templates/                   Pantallas HTML
web/static/                      Logo, favicon y la fuente Lato
scripts/generar_iconos.py        Regenera favicon, ícono de app y logo del mail desde los SVG
scripts/ver_preferencia.py       Consulta una preferencia de Mercado Pago (diagnóstico)
supabase/schema.sql              Tablas de la base
app.py                           Entrada para Vercel
run.py                           Entrada para correr local
tests/test_comprar_entradas.py   Tests unitarios de la user story (los 24 originales + los agregados)
tests/test_calendario.py         Calendario, feriados, horario y "1 mes calendario"
tests/test_web.py                Tests de integración de la web (memoria y Postgres)
tests/test_mercadopago.py        PasarelaMercadoPago con el SDK mockeado
tests/test_gmail.py              Mails y PDF con smtplib mockeado
tests/test_paleta.py             Paleta, contraste AA, tipografía y logo
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
| `GMAIL_USER` + `GMAIL_APP_PASSWORD` | El mail no sale: queda en **Mis mails**, con el PDF para descargar. |
| `APP_BASE_URL` | Los QR de las páginas apuntan a la URL con la que abriste la app; los de los mails, a `http://localhost:5001`. |

## Tests

```bash
pytest -v
```

- Unitarios: Mercado Pago, el mail y las compras anteriores del visitante se
  reemplazan con dobles (`Mock` y fakes). El reloj se inyecta fijo: martes
  06/10/2026 a las 10:00 (hora de Córdoba).
- Web: recorren el flujo completo por HTTP. Por defecto usan memoria; si definís
  `TEST_DATABASE_URL` corren **también** contra Postgres.

`TEST_DATABASE_URL` tiene que apuntar a una base de prueba local, **nunca a
Supabase**: los tests vacían las tablas. Con [Postgres.app](https://postgresapp.com):

```bash
createdb ecoharmony_test        # una sola vez
TEST_DATABASE_URL=postgresql://localhost/ecoharmony_test pytest -v
```

Para correr un solo grupo: `pytest -v -k TestCantidad`.

## Deploy: Supabase + Vercel

### 1. Supabase

1. Creá un proyecto en https://supabase.com (región São Paulo, la más cercana).
2. Copiá la connection string desde **Connect** → **Transaction pooler** (puerto 6543)
   y reemplazá `[YOUR-PASSWORD]` por la contraseña del proyecto.
   Tiene que ser la del pooler: la conexión directa es solo IPv6 y Vercel no llega.
3. Las tablas se crean y se actualizan solas cada vez que arranca la app
   (`supabase/schema.sql` es idempotente: `create table if not exists` y
   `alter table ... add column if not exists`). Si preferís hacerlo a mano,
   pegá ese archivo en el **SQL Editor**.

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

## Comprar: calendario, precios y límite

- **Calendario (FAQ 2):** la fecha se elige en un calendario que no deja
  seleccionar días pasados, lunes, 25/12, 1/1, días más allá de un mes ni hoy
  después de las 17:30. Los días deshabilitados los calcula el backend con la
  misma función que valida la compra (`parque.calendario.motivo_sin_venta`): la
  lógica no está duplicada en JavaScript. Es una grilla de radios: se usa con
  teclado (Tab entra, las flechas se mueven) y funciona sin JS. El backend
  valida todo igual aunque se manipule el HTML.
- **Precios (FAQ 6, 7 y 21):** antes de elegir la forma de pago se ve el
  desglose por visitante (edad, tarifa, descuento y subtotal) y el total. La
  pantalla calcula con las reglas que manda el backend en un JSON; el backend
  recalcula siempre al confirmar y guarda el precio final de cada entrada.
- **Límite (FAQ 27):** máximo 10 entradas por usuario y por fecha de visita,
  sumando sus compras. El error dice cuántas le quedan disponibles.

### Compras pendientes, cancelación y vencimiento

Una compra con tarjeta que todavía no fue aprobada es **pendiente**. Las compras
en efectivo nunca son pendientes.

| Estado | Cuenta para el límite | Entradas válidas |
|---|---|---|
| Confirmada (efectivo, sin cargo o pagada) | Sí | Sí |
| Pendiente (tarjeta sin aprobar, menos de 30 min) | Sí | No |
| Vencida (tarjeta sin aprobar, 30 min o más) | No | No |
| Rechazada (volvió de MP con `failure`) | No | No |
| Cancelada (la canceló el visitante) | No | No |

- Si el límite se supera por compras pendientes, el error lo explica ("Ya tenés
  11 entradas para el 24/10: 2 confirmadas y 9 con pago pendiente. Pagá o
  cancelá la compra pendiente para liberar lugar.") con links a cada compra
  pendiente de esa fecha.
- **Cancelar compra:** en la pantalla de una compra pendiente (POST, solo el
  dueño, con un segundo botón de confirmación). Una compra pagada o en efectivo
  no se puede cancelar desde la app.
- **Vencimiento:** se calcula por la fecha de creación (sin cron). La
  preferencia de Mercado Pago vence a los mismos 30 minutos y excluye los medios
  en efectivo y de cajero (`ticket`, `atm`): MP solo ofrece tarjetas.
- **Caso borde:** si a pesar de todo llega por webhook la aprobación de una
  compra cancelada, vencida o rechazada, **se acepta** (la persona pagó), la
  compra vuelve a ser válida, se mandan las entradas y queda un log de
  advertencia (`Llegó la aprobación de la compra ..., que estaba cancelada: se
  acepta porque la persona pagó`). Hay que revisar esos casos a mano: la
  persona podría tener más de 10 entradas para esa fecha.

## Entradas con QR

Cada entrada de una compra es individual: si comprás 3, se generan 3, cada una
con la edad de su visitante, su tarifa y un código propio (`secrets.token_urlsafe`,
no se puede adivinar). El QR apunta a `{APP_BASE_URL}/entradas/<codigo>`, una
página pública con el parque, la fecha, el tipo de pase, la edad, la tarifa, el
número de entrada (por ejemplo, 1 de 3) y el estado:

| Compra | Estado de la entrada | QR |
|---|---|---|
| Efectivo | Válida · Pagar en boletería | Sí |
| Total $0 (todos hasta 3 años) | Válida · Sin cargo | Sí |
| Tarjeta, pago pendiente | Esperando confirmación del pago | No |
| Tarjeta, aprobada por el webhook | Válida · Pagada con Mercado Pago | Sí |
| Tarjeta, vencida | Pago vencido · Entrada no válida | No |
| Tarjeta, rechazada o cancelada | Compra cancelada · Entrada no válida | No |

La confirmación muestra las entradas como tickets con talón y se pueden imprimir.

**Mails (FAQ 5):**

- **Efectivo o total $0:** el mail de confirmación sale al comprar, con los QR y el PDF.
- **Tarjeta:** no sale ningún mail hasta que se aprueba el pago. Cuando el
  webhook (o el checkout simulado) lo aprueba, se manda **Tus entradas** con los
  QR y el PDF, una sola vez aunque Mercado Pago repita la notificación. Si la
  compra se rechaza, se cancela o vence, no se manda nada
  (`NotificadorSegunPago` en `web/servicios.py`).
- Todos los mails traen el desglose por visitante y el total.
- **PDF adjunto** (`web/pdf_entradas.py`, fpdf2 y Lato): una página de resumen
  con el desglose, el total y la forma de pago, y una página por entrada con QR,
  fecha, tipo de pase, edad, tarifa, número y código.
- Los QR y el logo van como imágenes inline con `Content-ID` (no como `data:`
  URI) y el remitente es `EcoHarmony Park <GMAIL_USER>`.
- Sin Gmail, **Mis mails** muestra el PDF adjunto y deja descargarlo.

## Mercado Pago (Checkout Pro, entorno de prueba)

Sin `MP_ACCESS_TOKEN` la app usa un checkout propio que simula el de Mercado
Pago. Con el token usa `PasarelaMercadoPago` (SDK oficial `mercadopago`). Con
total $0 no se pasa por Mercado Pago aunque se haya elegido tarjeta.

1. La compra con tarjeta crea una **preferencia** con `external_reference` = id
   de la compra, `back_urls` a `/compras/<id>?mp=success|failure|pending`,
   `auto_return=approved`, `notification_url` = `/mercadopago/webhook`,
   vencimiento a 30 minutos y sin medios en efectivo ni de cajero. Las fechas
   van en ISO 8601 con offset (`2026-10-19T21:20:00.000-03:00`); la preferencia
   es válida desde 5 minutos antes de crearla, por si el reloj de Mercado Pago
   está atrasado respecto del nuestro.
2. El visitante paga en Mercado Pago y vuelve a la confirmación. Esa vuelta
   (`?mp=...`) **nunca** marca la compra como pagada; solo decide qué se muestra:

   | Vuelta | Pantalla |
   |---|---|
   | `success` (o `approved`) | Si el webhook ya llegó: "¡Listo, te esperamos!" con los QR. Si no: "Estamos confirmando tu pago…"; la página consulta `/compras/<id>/estado` (JSON, solo del dueño) cada 3 s y recarga cuando la compra figura pagada. A los 60 s sin novedades corta y avisa que las entradas llegan por mail. |
   | `pending` | "Tu pago está pendiente": sin error ni QR, con la opción de cancelar. |
   | `failure` (rechazado o volvió sin pagar) | "No se pudo completar el pago". La compra queda rechazada y **Volver e intentar de nuevo** abre `/comprar` precargado. Al confirmar se crea una compra nueva. |

   Lo guardado manda sobre el query param: si el webhook ya aprobó el pago, se
   muestra aprobada aunque la vuelta diga `failure`.
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
para volver a la app y para llamar al webhook, y los QR de las entradas apuntan
a ella, así que tiene que ser accesible desde internet:

- **Vercel:** la URL de producción, por ejemplo `https://ecoharmony-park.vercel.app`.
  No uses la URL de un deploy puntual (`...-git-xxx.vercel.app`): esas están
  protegidas por Vercel y Mercado Pago recibe un 401.
- **Local:** levantá un túnel con `ngrok http 5001` y usá la URL `https://...`
  que te da. Con `localhost` Mercado Pago no puede llamar al webhook y la compra
  queda pendiente.

### Si el checkout no deja pagar

Para ver cómo quedó guardada una preferencia (vencimiento, medios excluidos,
etc.), con el `pref_id` de la URL del checkout:

```bash
MP_ACCESS_TOKEN=... python scripts/ver_preferencia.py <pref_id>
```

En el entorno de prueba, "Pagar" también queda deshabilitado si en el
checkout estás logueado con la cuenta del **vendedor** o con una cuenta real:
abrilo en una ventana de incógnito y entrá con el **comprador de prueba**.

### Cargarlas en Vercel

**Settings** → **Environment Variables** → agregá `MP_ACCESS_TOKEN` y
`APP_BASE_URL` para el entorno **Production** → **Redeploy**.

## Mail con Gmail

Sin `GMAIL_USER` y `GMAIL_APP_PASSWORD` los mails no salen: se guardan en la base
y se ven en **Mis mails** (la bandeja simulada, con su link en el menú y su botón
en la confirmación). Con las dos variables, `NotificadorGmail` los manda por
`smtp.gmail.com:587` con STARTTLS, en HTML con versión de texto plano (ver
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

## Marca: paleta, tipografía y logo (FAQ 3)

- **Paleta:** `#386641` (primario: botones, títulos, links), `#6A994E` y
  `#A7C957` (solo decorativos: como texto no llegan a contraste AA) y `#F2E8CF`
  (fondo). `#BC4749` se usa solo para errores, siempre sobre fondo claro
  (sobre crema no llega a AA). El texto corrido usa un tono oscuro de
  `#386641`. Los contrastes se verifican en `tests/test_paleta.py`.
- **Tipografía:** Lato en toda la app (Google Fonts), en los mails (con
  fallback a Helvetica/Arial) y en el PDF (`web/static/fonts`, licencia OFL).
- **Logo** (pendiente de validación de la PO):
  - `web/static/logo.svg`: el logo completo. Lo usan el header, el PDF y el mail.
  - `web/static/logo-icono.svg`: la hoja con el ave, para el favicon y el ícono
    de app (se lee a 32 px).
  - Para cambiarlo, reemplazá esos archivos y corré
    `python scripts/generar_iconos.py` (necesita Chrome): regenera
    `favicon.ico`, `apple-touch-icon.png` y `logo-mail.png` (el mail usa PNG
    porque Gmail y Outlook no muestran SVG).

## Definiciones de la PO

Según la FAQ oficial de la cátedra, para esta user story. Todas las constantes
están en `parque/config.py`.

| FAQ | Definición | Dónde |
|---|---|---|
| 1 | El parque cierra todos los lunes y el 25/12 y el 1/1 de cualquier año. | `DIA_CIERRE`, `FERIADOS_CERRADO`; `parque/calendario.py` |
| 11 | Horario: de 8:30 a 19:00. Se muestra en la home y en la compra. | `HORA_APERTURA`, `HORA_CIERRE` |
| 25 | Se puede comprar hasta hoy + 1 mes calendario, inclusive. | `HORIZONTE_MESES`; `sumar_meses` |
| 26 | Para el mismo día se puede comprar hasta las 17:30 inclusive (hora de Córdoba). | `HORA_LIMITE_COMPRA_PARA_HOY`, `ZONA_HORARIA` |
| 2 | La fecha se elige en un calendario que no deja seleccionar días sin venta. | `web/calendario_compra.py`, `comprar.html` |
| 6 | Regular $10.000 y VIP $20.000; la única diferencia entre los pases es el precio. | `PRECIOS` |
| 7 y 21 | Descuento por edad: hasta 3 años gratis; de 4 a 15 años y desde 60, 50% off. | `DESCUENTOS_POR_EDAD`; `parque/precios.py` |
| 27 | Máximo 10 entradas por usuario y por fecha de visita, sumando sus compras. | `CANTIDAD_MAXIMA_ENTRADAS`; `ServicioCompraEntradas` |
| 5 | El mail con las entradas lleva un PDF adjunto. | `web/pdf_entradas.py` |
| 3 | Paleta #386641 #6A994E #A7C957 #F2E8CF #BC4749, tipografía Lato y logo propio. | `base.html`, `web/static/` |

Las definiciones de la US "Inscribirme a actividad" no se implementaron: es otra
user story.

### Supuestos del equipo (sin confirmar por la PO)

| Supuesto | Dónde se cambia |
|---|---|
| La edad de cada visitante tiene que estar entre 0 y 150 años. | `EDAD_MAXIMA` |
| "1 mes calendario": mismo día del mes siguiente; si no existe (31/01), el último día de ese mes (28/02 o 29/02). | `parque.calendario.sumar_meses` |
| Las compras con tarjeta pendientes cuentan para el límite de 10 durante 30 minutos; después vencen. | `VENCIMIENTO_PAGO_MINUTOS` |
| Si el total da $0 (todos hasta 3 años), no se pasa por Mercado Pago aunque se haya elegido tarjeta: la compra queda confirmada. | `ServicioCompraEntradas.comprar` |
| Las descripciones de sectores y actividades y los horarios de alimentación son textos de ejemplo. | `web/contenido.py` |

## Trazabilidad criterios ↔ tests

Tests unitarios de la user story (`tests/test_comprar_entradas.py`). Los 24
originales siguen igual; el resto se agregó con cada definición.

| Criterio / definición | Clase | Tests |
|---|---|---|
| Solo usuarios registrados | `TestAcceso` | `sin_estar_logueado_falla`, `usuario_registrado_pasa` |
| Indicar cantidad; no mayor a 10 (FAQ 27: por usuario y fecha) | `TestCantidad` | `sin_seleccionar_cantidad_falla`, `cero_entradas_falla`, `una_entrada_pasa`, `diez_entradas_pasa`, `once_entradas_falla`, `tres_entradas_con_siete_previas_misma_fecha_pasa`, `cuatro_entradas_con_siete_previas_misma_fecha_falla`, `compras_rechazadas_no_cuentan_para_el_limite_pasa`, `entradas_de_otra_fecha_no_cuentan_para_el_limite_pasa`, `entradas_de_otro_usuario_no_cuentan_para_el_limite_pasa` |
| Compras pendientes y el límite (supuesto del equipo) | `TestComprasPendientes` | `compra_pendiente_cuenta_para_el_limite_pasa`, `limite_superado_por_pendientes_informa_detalle_falla`, `compra_en_efectivo_no_se_considera_pendiente_pasa`, `compra_pendiente_vencida_no_cuenta_para_el_limite_pasa`, `compra_pendiente_a_los_29_minutos_todavia_cuenta_falla`, `compra_cancelada_no_cuenta_para_el_limite_pasa`, `compra_pagada_con_tarjeta_es_confirmada_aunque_haya_vencido_pasa` |
| Fecha actual o futura; parque abierto (FAQ 1, 25 y 26) | `TestFechaVisita` | `con_fecha_anterior_a_actual_falla`, `fecha_actual_pasa`, `fecha_futura_pasa`, `fecha_parque_cerrado_falla`, `fecha_a_un_mes_pasa`, `fecha_a_un_mes_y_un_dia_falla`, `para_hoy_a_las_17_30_pasa`, `para_hoy_a_las_17_31_falla`, `para_manana_a_las_18_pasa` |
| Edad de cada visitante (entre 0 y 150) | `TestDatosVisitantes` | `sin_asignar_edad_todos_visitantes_falla`, `cantidad_edades_no_coincide_cantidad_entradas_falla`, `con_edad_de_todos_los_visitantes_pasa`, `edad_negativa_falla`, `edad_cero_pasa`, `edad_150_pasa`, `edad_151_falla` |
| Tipo de pase (VIP o regular) | `TestTipoPase` | `sin_indicar_tipo_de_pase_falla`, `pase_vip_pasa`, `pase_regular_pasa` |
| Precio de cada pase y descuentos por edad (FAQ 6, 7 y 21) | `TestPrecios` | `precio_regular_adulto_pasa`, `precio_vip_adulto_pasa`, `precio_edad_3_gratis_pasa`, `precio_edad_4_mitad_pasa`, `precio_edad_15_mitad_pasa`, `precio_edad_16_completo_pasa`, `precio_edad_59_completo_pasa`, `precio_edad_60_mitad_pasa`, `total_compra_mixta_pasa`, `compra_total_cero_con_tarjeta_no_redirige_mp_pasa` |
| Forma de pago; tarjeta redirige a Mercado Pago | `TestFormaPago` | `sin_indicar_forma_de_pago_falla`, `con_tarjeta_redirige_mp_pasa`, `con_efectivo_pasa`, `con_efectivo_no_redirige_mp_pasa` |
| Mail de confirmación; informar cantidad y fecha | `TestConfirmacion` | `exitosa_envia_mail_confirmacion_pasa`, `exitosa_informa_cantidad_y_fecha_pasa`, `fallida_no_envia_mail_falla` |
| Tarjeta redirige a Mercado Pago (referencia); mail con el detalle | `TestIntegraciones` | `con_tarjeta_envia_referencia_de_compra_a_mp_pasa`, `exitosa_envia_detalle_de_compra_al_mail_pasa` |
| Una entrada por visitante, con su edad | `TestEntradas` | `genera_tres_entradas_con_la_edad_de_cada_visitante_pasa`, `cada_una_tiene_codigo_unico_pasa`, `codigo_no_adivinable_pasa` |

Las definiciones de la PO también están probadas en el resto de los archivos:

| FAQ / tema | Archivo y clase | Qué cubre |
|---|---|---|
| 1, 11 y 25 | `test_calendario.py` | Lunes, 25/12 y 1/1 de cualquier año, martes abierto, motivo de cierre, horario de 8:30 a 19:00, "1 mes calendario" en fin de mes y diciembre. |
| 11 | `test_web.py` · `TestHorario` | El horario se ve en la home y en la compra. |
| 2 | `test_web.py` · `TestCalendarioDeCompra` | El calendario reemplaza al input date y deshabilita lunes, pasados, más allá de un mes, hoy después de las 17:30, 25/12 y 1/1, con el motivo; el backend rechaza esas fechas aunque se manipule el HTML. |
| 6, 7 y 21 | `test_web.py` · `TestPreciosEnLaWeb` | Precio final guardado por entrada, desglose antes de la forma de pago, cálculo con las reglas del backend, total $0 sin MP y desglose en la confirmación. |
| 27 | `test_web.py` · `TestLimitePorFecha` | El límite contra la base real (memoria y Postgres). |
| Pendientes | `test_web.py` · `TestCancelarCompra`, `TestCompraVencida`, `TestAprobacionTardia` | Cancelar (libera el cupo; no pagadas ni en efectivo; 404 si es de otro; confirmación en dos pasos; links en el error), compra vencida y aprobación tardía aceptada con log. |
| Pendientes | `test_mercadopago.py` · `TestPreferenciaConVencimiento` | La preferencia excluye `ticket` y `atm` y vence a los 30 minutos. |
| 5 | `test_gmail.py` · `TestPdfDeEntradas`, `TestDesgloseEnElMail`; `test_web.py` · `TestBandejaConAdjunto` | PDF adjunto (y cuándo no), código de cada entrada y páginas del PDF, desglose y total en el mail, adjunto en Mis mails solo para el dueño. |
| 3 | `test_paleta.py`; `test_gmail.py` · `TestMarcaEnElMail` | Paleta, colores viejos, contraste AA, foco, Lato en la app, mail y PDF, logo e ícono solo con los verdes, favicon, logo inline en el mail. |

Otros tests de integración en `tests/test_web.py`: `TestWeb`, `TestMercadoPago`,
`TestVueltaDeMercadoPago`, `TestConfirmandoPago`, `TestReintentoDeCompraRechazada`,
`TestEntradasConQR`, `TestMailTusEntradas`, `TestBandejaSimulada`,
`TestBioparque` y `TestSinUsuarioDemo`.
