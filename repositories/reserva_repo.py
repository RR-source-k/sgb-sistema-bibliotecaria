"""Reservation repository - CRUD for reservations."""

import logging
from model.modelos import Reserva
from .archivo_util import ArchivoUtil

logger = logging.getLogger(__name__)
FILE = "reservas.txt"


class ReservaRepository:
    def __init__(self):
        self.archivo = ArchivoUtil(FILE)

    def obtener_todos(self) -> list[Reserva]:
        lines = self.archivo.leer_lineas()
        reservas = []
        for line in lines:
            try:
                reservas.append(Reserva.from_line(line))
            except ValueError as e:
                logger.warning(f"Skipping invalid reservation line: {e}")
        return reservas

    def obtener_por_codigo(self, codigo: str) -> Reserva | None:
        for res in self.obtener_todos():
            if res.codigo == codigo:
                return res
        return None

    def obtener_activas(self) -> list[Reserva]:
        return [res for res in self.obtener_todos() if res.estado == "Activa"]

    def obtener_por_isbn(self, isbn: str) -> list[Reserva]:
        return [res for res in self.obtener_todos() if res.isbn == isbn]

    def obtener_por_usuario(self, documento: str) -> list[Reserva]:
        return [res for res in self.obtener_todos()
                if res.numero_documento == documento]

    def obtener_activas_por_isbn(self, isbn: str) -> list[Reserva]:
        """Get active reservations for a specific book."""
        return [res for res in self.obtener_activas() if res.isbn == isbn]

    def _generar_codigo(self, prefijo: str) -> str:
        """Genera el siguiente código secuencial (ej. PRE0008)."""
        return ArchivoUtil.generar_codigo(prefijo, self.archivo.leer_lineas())

    def guardar(self, reserva: Reserva) -> bool:
        if self.obtener_por_codigo(reserva.codigo) is not None:
            logger.warning(f"Reservation {reserva.codigo} already exists.")
            return False
        return self.archivo.escribir_linea(reserva.to_line())

    def actualizar(self, reserva: Reserva) -> bool:
        existing = self.obtener_por_codigo(reserva.codigo)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = []
        for line in lines:
            try:
                r = Reserva.from_line(line)
                if r.codigo == reserva.codigo:
                    new_lines.append(reserva.to_line())
                else:
                    new_lines.append(line)
            except ValueError:
                new_lines.append(line)
        return self.archivo.reescribir(new_lines)

    def eliminar(self, codigo: str) -> bool:
        existing = self.obtener_por_codigo(codigo)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = [l for l in lines if l and not l.startswith(codigo + "|")]
        return self.archivo.reescribir(new_lines)
