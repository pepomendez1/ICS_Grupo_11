"""Persistencia de la app web.

- RepositorioPostgres: se usa cuando existe la variable DATABASE_URL
  (la connection string de Supabase). Es lo que corre en Vercel.
- RepositorioMemoria: se usa cuando no hay DATABASE_URL (desarrollo local y tests).

Ambos exponen la misma interfaz, así que el resto de la app no sabe cuál usa.
"""
import os
from datetime import date, datetime

from parque.compra import FormaPago, ResultadoCompra, TipoPase


def _armar_compra(fila: dict) -> dict:
    return {
        "id": fila["id"],
        "email": fila["email"],
        "pagada": fila["pagada"],
        "pago_id": fila.get("pago_id"),
        "resultado": ResultadoCompra(
            cantidad=fila["cantidad"],
            fecha_visita=fila["fecha_visita"],
            url_pago=fila.get("url_pago"),
            monto=fila["monto"],
            tipo_pase=TipoPase(fila["tipo_pase"]),
            forma_pago=FormaPago(fila["forma_pago"]),
        ),
    }


class RepositorioMemoria:
    def __init__(self):
        self._usuarios, self._pagos, self._compras, self._mails = {}, {}, {}, []

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
    def guardar_compra(self, compra_id, email, resultado: ResultadoCompra, edades, pago_id=None):
        self._compras[compra_id] = {
            "id": compra_id, "email": email, "pagada": False, "pago_id": pago_id,
            "cantidad": resultado.cantidad, "fecha_visita": resultado.fecha_visita,
            "url_pago": resultado.url_pago, "monto": resultado.monto,
            "tipo_pase": resultado.tipo_pase.value, "forma_pago": resultado.forma_pago.value,
            "edades": list(edades),
        }

    def obtener_compra(self, compra_id):
        fila = self._compras.get(compra_id)
        return _armar_compra(fila) if fila else None

    def marcar_compra_pagada(self, compra_id):
        if compra_id in self._compras:
            self._compras[compra_id]["pagada"] = True

    # Mails
    def guardar_mail(self, para, asunto, cuerpo):
        self._mails.append({"para": para, "asunto": asunto, "cuerpo": cuerpo, "enviado": datetime.now()})

    def mails_de(self, email):
        return [m for m in reversed(self._mails) if m["para"] == email]

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
    def guardar_compra(self, compra_id, email, resultado: ResultadoCompra, edades, pago_id=None):
        self._ejecutar(
            "insert into compras (id, email, fecha_visita, cantidad, edades, tipo_pase, forma_pago, "
            "monto, url_pago, pago_id) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                compra_id, email, resultado.fecha_visita, resultado.cantidad, list(edades),
                resultado.tipo_pase.value, resultado.forma_pago.value, resultado.monto,
                resultado.url_pago, pago_id,
            ),
        )

    def obtener_compra(self, compra_id):
        fila = self._ejecutar("select * from compras where id = %s", (compra_id,), uno=True)
        return _armar_compra(dict(fila)) if fila else None

    def marcar_compra_pagada(self, compra_id):
        self._ejecutar("update compras set pagada = true where id = %s", (compra_id,))

    # Mails
    def guardar_mail(self, para, asunto, cuerpo):
        self._ejecutar(
            "insert into mails (para, asunto, cuerpo) values (%s, %s, %s)", (para, asunto, cuerpo)
        )

    def mails_de(self, email):
        filas = self._ejecutar(
            "select para, asunto, cuerpo, enviado from mails where para = %s order by enviado desc",
            (email,), todos=True,
        )
        return [dict(f) for f in filas]

    def todos_los_mails(self):
        return [dict(f) for f in self._ejecutar("select * from mails order by enviado", todos=True)]


def crear_repositorio():
    url = os.environ.get("DATABASE_URL")
    if url:
        repo = RepositorioPostgres(url)
        if os.environ.get("CREAR_TABLAS", "1") == "1":
            repo.crear_tablas()
        return repo
    return RepositorioMemoria()
