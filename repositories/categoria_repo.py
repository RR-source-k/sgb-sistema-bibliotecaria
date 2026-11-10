"""Category repository - CRUD for categories."""

import logging
from model.modelos import Categoria
from .archivo_util import ArchivoUtil

logger = logging.getLogger(__name__)
FILE = "categorias.txt"


class CategoriaRepository:
    def __init__(self):
        self.archivo = ArchivoUtil(FILE)

    def obtener_todos(self) -> list[Categoria]:
        lines = self.archivo.leer_lineas()
        categorias = []
        for line in lines:
            try:
                categorias.append(Categoria.from_line(line))
            except ValueError as e:
                logger.warning(f"Skipping invalid category line: {e}")
        return categorias

    def obtener_por_codigo(self, codigo: str) -> Categoria | None:
        for cat in self.obtener_todos():
            if cat.codigo == codigo:
                return cat
        return None

    def guardar(self, categoria: Categoria) -> bool:
        if self.obtener_por_codigo(categoria.codigo) is not None:
            logger.warning(f"Category {categoria.codigo} already exists.")
            return False
        return self.archivo.escribir_linea(categoria.to_line())

    def actualizar(self, categoria: Categoria) -> bool:
        existing = self.obtener_por_codigo(categoria.codigo)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = []
        for line in lines:
            try:
                c = Categoria.from_line(line)
                if c.codigo == categoria.codigo:
                    new_lines.append(categoria.to_line())
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
