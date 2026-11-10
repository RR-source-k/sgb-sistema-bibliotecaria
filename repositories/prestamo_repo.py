"""Loan repository - CRUD for loans."""

import logging
from model.modelos import Prestamo
from .archivo_util import ArchivoUtil

logger = logging.getLogger(__name__)
FILE = "prestamos.txt"


class PrestamoRepository:
    def __init__(self):
        self.archivo = ArchivoUtil(FILE)

    def obtener_todos(self) -> list[Prestamo]:
        lines = self.archivo.leer_lineas()
        prestamos = []
        for line in lines:
            try:
                prestamos.append(Prestamo.from_line(line))
            except ValueError as e:
                logger.warning(f"Skipping invalid loan line: {e}")
        return prestamos

    def obtener_por_codigo(self, codigo: str) -> Prestamo | None:
        for loan in self.obtener_todos():
            if loan.codigo == codigo:
                return loan
        return None

    def obtener_activos(self) -> list[Prestamo]:
        return [loan for loan in self.obtener_todos() if loan.estado == "Activo"]

    def obtener_por_usuario(self, documento: str) -> list[Prestamo]:
        return [loan for loan in self.obtener_todos()
                if loan.numero_documento == documento]

    def obtener_por_isbn(self, isbn: str) -> list[Prestamo]:
        return [loan for loan in self.obtener_todos() if loan.isbn == isbn]

    def obtener_vencidos(self) -> list[Prestamo]:
        activos = self.obtener_activos()
        vencidos = []
        for loan in activos:
            if loan.estado != "Devuelto":
                vencidos.append(loan)
        return vencidos

    def _generar_codigo(self, prefijo: str) -> str:
        """Genera el siguiente código secuencial (ej. PRE0008)."""
        return ArchivoUtil.generar_codigo(prefijo, self.archivo.leer_lineas())

    def guardar(self, prestamo: Prestamo) -> bool:
        if self.obtener_por_codigo(prestamo.codigo) is not None:
            logger.warning(f"Loan {prestamo.codigo} already exists.")
            return False
        return self.archivo.escribir_linea(prestamo.to_line())

    def actualizar(self, prestamo: Prestamo) -> bool:
        existing = self.obtener_por_codigo(prestamo.codigo)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = []
        for line in lines:
            try:
                p = Prestamo.from_line(line)
                if p.codigo == prestamo.codigo:
                    new_lines.append(prestamo.to_line())
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
