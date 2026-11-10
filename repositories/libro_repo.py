"""Book repository - CRUD for books."""

import logging
from model.modelos import Libro
from .archivo_util import ArchivoUtil

logger = logging.getLogger(__name__)
FILE = "libros.txt"


class LibroRepository:
    def __init__(self):
        self.archivo = ArchivoUtil(FILE)

    def obtener_todos(self) -> list[Libro]:
        lines = self.archivo.leer_lineas()
        libros = []
        for line in lines:
            try:
                libros.append(Libro.from_line(line))
            except ValueError as e:
                logger.warning(f"Skipping invalid book line: {e}")
        return libros

    def obtener_por_isbn(self, isbn: str) -> Libro | None:
        for book in self.obtener_todos():
            if book.isbn == isbn:
                return book
        return None

    def buscar_por_titulo(self, termino: str) -> list[Libro]:
        term_lower = termino.lower()
        return [book for book in self.obtener_todos()
                if term_lower in book.titulo.lower() or term_lower in book.autor.lower()]

    def buscar_por_categoria(self, codigo_categoria: str) -> list[Libro]:
        return [book for book in self.obtener_todos()
                if book.codigo_categoria == codigo_categoria]

    def guardar(self, libro: Libro) -> bool:
        if self.obtener_por_isbn(libro.isbn) is not None:
            logger.warning(f"Book {libro.isbn} already exists.")
            return False
        return self.archivo.escribir_linea(libro.to_line())

    def actualizar(self, libro: Libro) -> bool:
        existing = self.obtener_por_isbn(libro.isbn)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = []
        for line in lines:
            try:
                b = Libro.from_line(line)
                if b.isbn == libro.isbn:
                    new_lines.append(libro.to_line())
                else:
                    new_lines.append(line)
            except ValueError:
                new_lines.append(line)
        return self.archivo.reescribir(new_lines)

    def eliminar(self, isbn: str) -> bool:
        existing = self.obtener_por_isbn(isbn)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = [l for l in lines if l and not l.startswith(isbn + "|")]
        return self.archivo.reescribir(new_lines)
