-- Esquema de EcoHarmony Park.
-- Se puede correr en el SQL Editor de Supabase; la app también lo ejecuta
-- al iniciar (es idempotente gracias a "if not exists").

create table if not exists usuarios (
  email          text primary key,
  nombre         text not null,
  password_hash  text not null,
  creado         timestamptz not null default now()
);

create table if not exists pagos (
  id      text primary key,
  monto   integer not null check (monto > 0),
  email   text not null references usuarios(email),
  estado  text not null default 'pendiente' check (estado in ('pendiente', 'aprobado')),
  creado  timestamptz not null default now()
);

create table if not exists compras (
  id            text primary key,
  email         text not null references usuarios(email),
  fecha_visita  date not null,
  cantidad      integer not null check (cantidad between 1 and 10),
  edades        integer[] not null,
  tipo_pase     text not null check (tipo_pase in ('VIP', 'REGULAR')),
  forma_pago    text not null check (forma_pago in ('TARJETA', 'EFECTIVO')),
  monto         integer not null,
  url_pago      text,
  pago_id       text references pagos(id),
  pagada        boolean not null default false,
  creado        timestamptz not null default now()
);

-- Una fila por entrada individual de la compra. El código es el que va en el
-- QR (secrets.token_urlsafe): no se puede adivinar.
create table if not exists entradas (
  codigo     text primary key,
  compra_id  text not null references compras(id),
  numero     integer not null check (numero between 1 and 10),
  edad       integer not null check (edad between 0 and 150),
  unique (compra_id, numero)
);

create table if not exists mails (
  id       bigint generated always as identity primary key,
  para     text not null,
  asunto   text not null,
  cuerpo   text not null,
  enviado  timestamptz not null default now()
);

-- La app accede con la connection string (rol postgres), no por la API REST.
-- Activamos RLS sin políticas para que las tablas no queden expuestas
-- públicamente a través de la API de Supabase.
alter table usuarios enable row level security;
alter table pagos    enable row level security;
alter table compras  enable row level security;
alter table entradas enable row level security;
alter table mails    enable row level security;
