"""Fine repository - CRUD for fines."""

import logging
from model.modelos import Multa
from .archivo_util import ArchivoUtil

logger = logging.getLogger(__name__)
FILE = "multas.txt"


class MultaRepository:
    def __init__(self):
        self.archivo = ArchivoUtil(FILE)

    def obtener_todos(self) -> list[Multa]:
        lines = self.archivo.leer_lineas()
        multas = []
        for line in lines:
            try:
                multas.append(Multa.from_line(line))
            except ValueError as e:
                logger.warning(f"Skipping invalid fine line: {e}")
        return multas

    def obtener_por_codigo(self, codigo: str) -> Multa | None:
        for fine in self.obtener_todos():
            if fine.codigo == codigo:
                return fine
        return None

    def obtener_por_prestamo(self, codigo_prestamo: str) -> list[Multa]:
        return [fine for fine in self.obtener_todos()
                if fine.codigo_prestamo == codigo_prestamo]

    def obtener_pendientes(self) -> list[Multa]:
        return [fine for fine in self.obtener_todos() if fine.estado == "Pendiente"]

    def obtener_por_usuario(self, documento: str) -> list[Multa]:
        """Get all fines for a user by looking up loans linked to this user."""
        all_multas = self.obtener_todos()
        # We need to cross-reference with loans to get fines by user document
        # This is a limitation of the file-based approach
        # The service layer will handle this cross-reference
        return all_multas

    def obtener_total_pendiente(self) -> int:
        return sum(fine.valor for fine in self.obtener_pendientes())

    def _generar_codigo(self, prefijo: str) -> str:
        """Genera el siguiente código secuencial (ej. PRE0008)."""
        return ArchivoUtil.generar_codigo(prefijo, self.archivo.leer_lineas())

    def guardar(self, multa: Multa) -> bool:
        if self.obtener_por_codigo(multa.codigo) is not None:
            logger.warning(f"Fine {multa.codigo} already exists.")
            return False
        return self.archivo.escribir_linea(multa.to_line())

    def actualizar(self, multa: Multa) -> bool:
        existing = self.obtener_por_codigo(multa.codigo)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = []
        for line in lines:
            try:
                m = Multa.from_line(line)
                if m.codigo == multa.codigo:
                    new_lines.append(multa.to_line())
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
