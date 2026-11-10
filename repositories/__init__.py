"""Repository layer - File-based persistence."""

from .archivo_util import ArchivoUtil
from .usuario_repo import UsuarioRepository
from .categoria_repo import CategoriaRepository
from .libro_repo import LibroRepository
from .prestamo_repo import PrestamoRepository
from .multa_repo import MultaRepository
from .reserva_repo import ReservaRepository

__all__ = [
    "ArchivoUtil", "UsuarioRepository", "CategoriaRepository",
    "LibroRepository", "PrestamoRepository", "MultaRepository", "ReservaRepository",
]
