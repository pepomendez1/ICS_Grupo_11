"""Persistencia de la app web.

- RepositorioPostgres: se usa cuando existe la variable DATABASE_URL
  (la connection string de Supabase). Es lo que corre en Vercel.
- RepositorioMemoria: se usa cuando no hay DATABASE_URL (desarrollo local y tests).

Ambos exponen la misma interfaz, así que el resto de la app no sabe cuál usa.
"""
import os
import threading
from contextlib import contextmanager
from datetime import date, datetime, timezone

from parque.compra import CompraExistente, Entrada, FormaPago, ResultadoCompra, TipoPase
from parque.precios import tarifa_para


def _como_compra_existente(fila: dict) -> CompraExistente:
    return CompraExistente(
        id=fila["id"], cantidad=fila["cantidad"], forma_pago=FormaPago(fila["forma_pago"]),
        pagada=fila["pagada"], estado=fila.get("estado") or "activa", monto=fila["monto"],
        creado=fila.get("creado"),
    )


def _armar_entrada(fila: dict, tipo_pase: str) -> Entrada:
    """El precio guardado es el que se cobró; el nombre de la tarifa y el
    descuento se derivan de la edad (las entradas viejas no tienen precio)."""
    tarifa = tarifa_para(tipo_pase, fila["edad"])
    precio = fila.get("precio")
    return Entrada(
        numero=fila["numero"], edad=fila["edad"], codigo=fila["codigo"],
        precio=tarifa.precio if precio is None else precio,
        descuento=tarifa.descuento, tarifa=tarifa.nombre,
    )


def _armar_compra(fila: dict, entradas=()) -> dict:
    return {
        "id": fila["id"],
        "email": fila["email"],
        "pagada": fila["pagada"],
        "estado": fila.get("estado") or "activa",  # "activa" | "rechazada" | "cancelada"
        "edades": list(fila.get("edades") or []),
        "existente": _como_compra_existente(fila),  # para las reglas del dominio
        "pago_id": fila.get("pago_id"),
        "resultado": ResultadoCompra(
            cantidad=fila["cantidad"],
            fecha_visita=fila["fecha_visita"],
            url_pago=fila.get("url_pago"),
            monto=fila["monto"],
            tipo_pase=TipoPase(fila["tipo_pase"]),
            forma_pago=FormaPago(fila["forma_pago"]),
            entradas=[
                _armar_entrada(e, fila["tipo_pase"])
                for e in sorted(entradas, key=lambda e: e["numero"])
            ],
        ),
    }


class _CandadosPorClave:
    """Un candado por (email, fecha) para los hilos de este proceso."""

    def __init__(self):
        self._candados = {}
        self._mutex = threading.Lock()

    @contextmanager
    def tomar(self, *clave):
        with self._mutex:
            candado = self._candados.setdefault(clave, threading.Lock())
        with candado:
            yield


class RepositorioMemoria:
    def __init__(self):
        self._usuarios, self._pagos, self._compras, self._mails = {}, {}, {}, []
        self._entradas = {}  # codigo -> fila
        self._candados = _CandadosPorClave()

    @contextmanager
    def bloqueo_de_cupo(self, email, fecha):
        """FAQ 27: contar las entradas y guardar la compra de una persona para una
        fecha tiene que ser atómico; si no, dos compras simultáneas pasan las dos."""
        with self._candados.tomar(email, fecha):
            yield

    # Usuarios
    def crear_usuario(self, nombre, email, password_hash):
        if email in self._usuarios:
            return False
        self._usuarios[email] = {"nombre": nombre, "email": email, "password": password_hash}
        return True

    def obtener_usuario(self, email):
        return self._usuarios.get(email)

    # Pagos (Mercado Pago simulado)
    def guardar_pago(self, pago_id, monto, email):
        self._pagos[pago_id] = {"id": pago_id, "monto": monto, "email": email, "estado": "pendiente"}

    def obtener_pago(self, pago_id):
        return self._pagos.get(pago_id)

    def aprobar_pago(self, pago_id):
        if pago_id in self._pagos:
            self._pagos[pago_id]["estado"] = "aprobado"

    # Compras
    def guardar_compra(self, compra_id, email, resultado: ResultadoCompra, edades, pago_id=None, creado=None):
        self._compras[compra_id] = {
            "creado": creado or datetime.now(timezone.utc),
            "id": compra_id, "email": email, "pagada": False, "estado": "activa", "pago_id": pago_id,
            "cantidad": resultado.cantidad, "fecha_visita": resultado.fecha_visita,
            "url_pago": resultado.url_pago, "monto": resultado.monto,
            "tipo_pase": resultado.tipo_pase.value, "forma_pago": resultado.forma_pago.value,
            "edades": list(edades),
        }
        for e in resultado.entradas:
            self._entradas[e.codigo] = {
                "codigo": e.codigo, "compra_id": compra_id, "numero": e.numero, "edad": e.edad,
                "precio": e.precio,
            }

    def obtener_compra(self, compra_id):
        fila = self._compras.get(compra_id)
        if not fila:
            return None
        return _armar_compra(fila, [e for e in self._entradas.values() if e["compra_id"] == compra_id])

    def compras_para(self, email, fecha):
        """Puerto ComprasDelVisitante (FAQ 27)."""
        return [
            _como_compra_existente(f) for f in self._compras.values()
            if f["email"] == email and f["fecha_visita"] == fecha
        ]

    def obtener_entrada(self, codigo):
        fila = self._entradas.get(codigo)
        if not fila:
            return None
        return {"numero": fila["numero"], "edad": fila["edad"], "codigo": codigo,
                "compra": self.obtener_compra(fila["compra_id"])}

    def marcar_compra_pagada(self, compra_id):
        """Devuelve True solo si la compra pasó de no pagada a pagada."""
        fila = self._compras.get(compra_id)
        if not fila or fila["pagada"]:
            return False
        fila["pagada"], fila["estado"] = True, "activa"
        return True

    def marcar_compra_rechazada(self, compra_id):
        """Rechaza la compra si no está pagada. Devuelve True si cambió el estado."""
        fila = self._compras.get(compra_id)
        if not fila or fila["pagada"] or fila["estado"] == "rechazada":
            return False
        fila["estado"] = "rechazada"
        return True

    def marcar_compra_cancelada(self, compra_id):
        """Cancela la compra si no está pagada. Devuelve True si cambió el estado."""
        fila = self._compras.get(compra_id)
        if not fila or fila["pagada"] or fila["estado"] != "activa":
            return False
        fila["estado"] = "cancelada"
        return True

    # Mails
    def guardar_mail(self, para, asunto, cuerpo, adjunto=None, adjunto_nombre=None):
        self._mails.append({
            "id": len(self._mails) + 1, "para": para, "asunto": asunto, "cuerpo": cuerpo,
            "enviado": datetime.now(), "adjunto": adjunto, "adjunto_nombre": adjunto_nombre,
        })

    def mails_de(self, email):
        return [m for m in reversed(self._mails) if m["para"] == email]

    def obtener_adjunto(self, mail_id):
        """(para, nombre, contenido) del PDF adjunto de un mail, o None."""
        mail = next((m for m in self._mails if m["id"] == mail_id and m["adjunto"]), None)
        return (mail["para"], mail["adjunto_nombre"], mail["adjunto"]) if mail else None

    def todos_los_mails(self):
        return list(self._mails)


class RepositorioPostgres:
    def __init__(self, url: str):
        import psycopg
        from psycopg.rows import dict_row

        self._psycopg = psycopg
        self._dict_row = dict_row
        self._url = url
        self._con = None
        self._candados = _CandadosPorClave()

    def _conexion(self):
        """Reutiliza una sola conexión mientras la instancia siga viva.

        Abrir una conexión nueva cuesta varios viajes de ida y vuelta a la base
        (TCP + TLS + login). En Vercel la instancia queda "tibia" entre requests,
        así que reutilizarla ahorra la mayor parte del tiempo.
        """
        if self._con is None or self._con.closed or self._con.broken:
            # prepare_threshold=None: compatible con el pooler de Supabase (pgbouncer)
            self._con = self._psycopg.connect(
                self._url, row_factory=self._dict_row, prepare_threshold=None, autocommit=True
            )
        return self._con

    def _ejecutar(self, sql, params=(), uno=False, todos=False):
        for intento in range(2):
            try:
                with self._conexion().cursor() as cur:
                    cur.execute(sql, params)
                    if uno:
                        return cur.fetchone()
                    if todos:
                        return cur.fetchall()
                    return cur.rowcount
            except self._psycopg.OperationalError:
                # La conexión se cortó (por ejemplo, la instancia estuvo dormida): reintentar una vez.
                self._con = None
                if intento == 1:
                    raise

    def _en_transaccion(self, pasos):
        """Corre pasos(cursor) en una transacción, con el mismo reintento que _ejecutar.
        Si algo falla, la transacción se deshace entera, así que reintentar es seguro."""
        for intento in range(2):
            try:
                con = self._conexion()
                with con.transaction(), con.cursor() as cur:
                    return pasos(cur)
            except self._psycopg.OperationalError:
                self._con = None
                if intento == 1:
                    raise

    @contextmanager
    def bloqueo_de_cupo(self, email, fecha):
        """FAQ 27: contar y guardar es atómico por persona y fecha, también entre
        instancias (Vercel puede correr varias). Se usa un advisory lock de
        transacción en una conexión aparte: con el pooler de Supabase (modo
        transacción) un lock de sesión podría quedar colgado en otra conexión.
        El candado local cubre los hilos de este proceso, que comparten conexión."""
        with self._candados.tomar(email, fecha):
            with self._psycopg.connect(self._url, prepare_threshold=None, autocommit=True) as con:
                with con.transaction():
                    con.execute("select pg_advisory_xact_lock(hashtextextended(%s, 0))",
                                (f"compra:{email}:{fecha}",))
                    yield

    def crear_tablas(self):
        ruta = os.path.join(os.path.dirname(__file__), "..", "supabase", "schema.sql")
        with open(ruta, encoding="utf-8") as f:
            sql = f.read()
        self._conexion().execute(sql)

    # Usuarios
    def crear_usuario(self, nombre, email, password_hash):
        filas = self._ejecutar(
            "insert into usuarios (nombre, email, password_hash) values (%s, %s, %s) "
            "on conflict (email) do nothing",
            (nombre, email, password_hash),
        )
        return filas == 1

    def obtener_usuario(self, email):
        fila = self._ejecutar(
            "select nombre, email, password_hash as password from usuarios where email = %s",
            (email,), uno=True,
        )
        return dict(fila) if fila else None

    # Pagos
    def guardar_pago(self, pago_id, monto, email):
        self._ejecutar(
            "insert into pagos (id, monto, email) values (%s, %s, %s)", (pago_id, monto, email)
        )

    def obtener_pago(self, pago_id):
        fila = self._ejecutar("select * from pagos where id = %s", (pago_id,), uno=True)
        return dict(fila) if fila else None

    def aprobar_pago(self, pago_id):
        self._ejecutar("update pagos set estado = 'aprobado' where id = %s", (pago_id,))

    # Compras
    def guardar_compra(self, compra_id, email, resultado: ResultadoCompra, edades, pago_id=None, creado=None):
        # La compra y sus entradas se guardan juntas o no se guarda nada.
        def pasos(cur):
            cur.execute(
                "insert into compras (id, email, fecha_visita, cantidad, edades, tipo_pase, forma_pago, "
                "monto, url_pago, pago_id, creado) "
                "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, coalesce(%s, now()))",
                (
                    compra_id, email, resultado.fecha_visita, resultado.cantidad, list(edades),
                    resultado.tipo_pase.value, resultado.forma_pago.value, resultado.monto,
                    resultado.url_pago, pago_id, creado,
                ),
            )
            cur.executemany(
                "insert into entradas (codigo, compra_id, numero, edad, precio) values (%s, %s, %s, %s, %s)",
                [(e.codigo, compra_id, e.numero, e.edad, e.precio) for e in resultado.entradas],
            )
        self._en_transaccion(pasos)

    def obtener_compra(self, compra_id):
        fila = self._ejecutar("select * from compras where id = %s", (compra_id,), uno=True)
        if not fila:
            return None
        entradas = self._ejecutar(
            "select codigo, numero, edad, precio from entradas where compra_id = %s", (compra_id,), todos=True
        )
        return _armar_compra(dict(fila), [dict(e) for e in entradas])

    def compras_para(self, email, fecha):
        """Puerto ComprasDelVisitante (FAQ 27): una sola consulta por email y fecha."""
        filas = self._ejecutar(
            "select id, cantidad, forma_pago, pagada, estado, monto, creado from compras "
            "where email = %s and fecha_visita = %s",
            (email, fecha), todos=True,
        )
        return [_como_compra_existente(dict(f)) for f in filas]

    def obtener_entrada(self, codigo):
        fila = self._ejecutar(
            "select codigo, compra_id, numero, edad from entradas where codigo = %s", (codigo,), uno=True
        )
        if not fila:
            return None
        return {"numero": fila["numero"], "edad": fila["edad"], "codigo": codigo,
                "compra": self.obtener_compra(fila["compra_id"])}

    def marcar_compra_pagada(self, compra_id):
        """Devuelve True solo si la compra pasó de no pagada a pagada. Es atómico:
        si llegan dos webhooks a la vez, solo uno ve el cambio."""
        # Si MP termina cobrando una compra rechazada, el cobro manda: vuelve a activa.
        filas = self._ejecutar(
            "update compras set pagada = true, estado = 'activa' where id = %s and not pagada",
            (compra_id,),
        )
        return filas == 1

    def marcar_compra_rechazada(self, compra_id):
        """Rechaza la compra si no está pagada. Devuelve True si cambió el estado."""
        filas = self._ejecutar(
            "update compras set estado = 'rechazada' "
            "where id = %s and not pagada and estado = 'activa'",
            (compra_id,),
        )
        return filas == 1

    def marcar_compra_cancelada(self, compra_id):
        """Cancela la compra si no está pagada (atómico). True si cambió el estado."""
        filas = self._ejecutar(
            "update compras set estado = 'cancelada' "
            "where id = %s and not pagada and estado = 'activa'",
            (compra_id,),
        )
        return filas == 1

    # Mails
    def guardar_mail(self, para, asunto, cuerpo, adjunto=None, adjunto_nombre=None):
        self._ejecutar(
            "insert into mails (para, asunto, cuerpo, adjunto, adjunto_nombre) values (%s, %s, %s, %s, %s)",
            (para, asunto, cuerpo, adjunto, adjunto_nombre),
        )

    def mails_de(self, email):
        filas = self._ejecutar(
            "select id, para, asunto, cuerpo, enviado, adjunto_nombre from mails "
            "where para = %s order by enviado desc",
            (email,), todos=True,
        )
        return [dict(f) for f in filas]

    def todos_los_mails(self):
        return [dict(f) for f in self._ejecutar("select * from mails order by enviado", todos=True)]

    def obtener_adjunto(self, mail_id):
        """(para, nombre, contenido) del PDF adjunto de un mail, o None."""
        fila = self._ejecutar(
            "select para, adjunto_nombre, adjunto from mails where id = %s and adjunto is not null",
            (mail_id,), uno=True,
        )
        return (fila["para"], fila["adjunto_nombre"], bytes(fila["adjunto"])) if fila else None


def crear_repositorio():
    url = os.environ.get("DATABASE_URL")
    if url:
        repo = RepositorioPostgres(url)
        if os.environ.get("CREAR_TABLAS", "1") == "1":
            repo.crear_tablas()
        return repo
    return RepositorioMemoria()
