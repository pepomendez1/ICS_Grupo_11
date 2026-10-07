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
web/servicios.py                 Calendario del parque, Mercado Pago y mail (simulados)
web/contenido.py                 Textos de atracciones y pases
web/templates/                   Pantallas HTML
supabase/schema.sql              Tablas de la base
app.py                           Entrada para Vercel
run.py                           Entrada para correr local
tests/test_comprar_entradas.py   24 tests unitarios de la user story (TDD)
tests/test_web.py                8 tests de integración de la web
```

## Correrlo local

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Abrí http://localhost:5000. Usuario de prueba: `demo@ecoharmony.com` / `demo123`.

Sin `DATABASE_URL` la app guarda todo en memoria (se pierde al reiniciar).
Para usar Supabase también local, exportá las variables de `.env.example`
antes de `python run.py`.

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
4. **Deploy**.

## Qué está simulado

- **Mercado Pago:** la app genera un pago y redirige a un checkout propio que
  simula el de Mercado Pago. No se cobra nada.
- **Mail:** los mails de confirmación se guardan en la tabla `mails` y se ven en
  **Mis mails**.

Para hacerlos reales hay que reemplazar las clases de `web/servicios.py` por otras
que usen el SDK de Mercado Pago y un servicio de mail. La lógica de negocio no cambia.

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
