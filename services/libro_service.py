"""Book service - Business logic for book management."""

import logging
from model.modelos import Libro
from repositories.libro_repo import LibroRepository
from repositories.categoria_repo import CategoriaRepository

logger = logging.getLogger(__name__)


class LibroService:
    def __init__(self):
        self.repo = LibroRepository()
        self.cat_repo = CategoriaRepository()

    def obtener_todos(self) -> list[Libro]:
        return self.repo.obtener_todos()

    def obtener_por_isbn(self, isbn: str) -> Libro | None:
        return self.repo.obtener_por_isbn(isbn)

    def buscar(self, termino: str) -> list[Libro]:
        """Search books by title or author."""
        return self.repo.buscar_por_titulo(termino)

    def buscar_por_categoria(self, codigo_categoria: str) -> list[Libro]:
        """Search books by category code."""
        return self.repo.buscar_por_categoria(codigo_categoria)

    def obtener_categorias_disponibles(self) -> list[tuple[str, str]]:
        """Return list of (codigo, nombre) tuples for all categories."""
        categorias = self.cat_repo.obtener_todos()
        return [(cat.codigo, cat.nombre) for cat in categorias]

    def registrar(self, libro: Libro) -> tuple[bool, str]:
        """Register a new book. Returns (success, message)."""
        if not libro.isbn or not libro.titulo or not libro.autor:
            return False, "ISBN, título y autor son requeridos."

        existente = self.obtener_por_isbn(libro.isbn)
        if existente is not None:
            return False, f"El libro con ISBN {libro.isbn} ya existe."

        if self.repo.guardar(libro):
            logger.info(f"Book registered: {libro}")
            return True, "Libro registrado exitosamente."
        return False, "Error al registrar el libro."

    def actualizar(self, libro: Libro) -> tuple[bool, str]:
        """Update an existing book. Returns (success, message)."""
        existente = self.obtener_por_isbn(libro.isbn)
        if existente is None:
            return False, "Libro no encontrado."

        if self.repo.actualizar(libro):
            logger.info(f"Book updated: {libro}")
            return True, "Libro actualizado exitosamente."
        return False, "Error al actualizar el libro."

    def eliminar(self, isbn: str) -> tuple[bool, str]:
        """Delete a book. Returns (success, message)."""
        existente = self.obtener_por_isbn(isbn)
        if existente is None:
            return False, "Libro no encontrado."

        if self.repo.eliminar(isbn):
            logger.info(f"Book deleted: {isbn}")
            return True, "Libro eliminado exitosamente."
        return False, "Error al eliminar el libro."

    def incrementar_ejemplares(self, isbn: str, cantidad: int) -> tuple[bool, str]:
        """Add copies to an existing book. Returns (success, message)."""
        libro = self.obtener_por_isbn(isbn)
        if libro is None:
            return False, "Libro no encontrado."

        libro.total_ejemplares += cantidad
        libro.disponibles += cantidad
        return self.actualizar(libro)
