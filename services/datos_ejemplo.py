"""
Datos de ejemplo para demostrar el sistema.

El sistema se entrega con los archivos de datos vacíos. Este módulo contiene los datos
y utilidades de apoyo; la animación paso a paso (escribir en los formularios y pulsar
los botones) está en `ui/demo.py`.
"""

import logging

from model.modelos import Categoria
from repositories.archivo_util import ArchivoUtil
from repositories.categoria_repo import CategoriaRepository

logger = logging.getLogger(__name__)

# Archivos que se vacían al reiniciar (las categorías son catálogo y se conservan)
ARCHIVOS_DATOS = ["usuarios.txt", "libros.txt", "prestamos.txt", "multas.txt", "reservas.txt"]

CATEGORIAS = [
    ("LIT", "Literatura", "Novela, poesía, cuento y ensayo literario"),
    ("TEC", "Tecnología", "Tecnología, computación e ingeniería"),
    ("CIA", "Ciencias", "Ciencias naturales y aplicadas"),
    ("MAT", "Matemática", "Matemáticas puras y aplicadas"),
    ("HIS", "Historia", "Historia y ciencias sociales"),
    ("DER", "Derecho", "Derecho y ciencias jurídicas"),
    ("MED", "Medicina", "Medicina y ciencias de la salud"),
    ("OTH", "Otros", "Otras áreas del conocimiento"),
]

# documento, nombre, tipo, correo, teléfono, estado
USUARIOS = [
    ("1098765432", "María López", "Estudiante", "maria.lopez@udes.edu.co", "3001234567", "Activo"),
    ("1001234567", "Juan Pérez", "Docente", "juan.perez@udes.edu.co", "3109876543", "Activo"),
    ("1055667788", "Carlos Gómez", "Externo", "carlos.gomez@correo.com", "3205551234", "Activo"),
    ("1020304050", "Laura Martínez", "Estudiante", "laura.martinez@udes.edu.co", "3157778899", "Activo"),
    ("1077889900", "Pedro Ramírez", "Externo", "pedro.ramirez@correo.com", "3012223344", "Inactivo"),
]

# isbn, título, autor, código de categoría, año, ejemplares
LIBROS = [
    ("9789585001234", "Cien años de soledad", "Gabriel García Márquez", "LIT", 1967, 5),
    ("9789587654321", "Estructuras de datos en Python", "Ana Gómez", "TEC", 2020, 2),
    ("9780132350884", "Clean Code", "Robert C. Martin", "TEC", 2008, 3),
    ("9780553380163", "Breve historia del tiempo", "Stephen Hawking", "CIA", 1988, 4),
    ("9789587000111", "Álgebra Lineal", "Stanley Grossman", "MAT", 2012, 3),
    ("9789587410440", "Historia de Colombia", "Jorge Orlando Melo", "HIS", 2017, 2),
    ("9789587300215", "Manual de Derecho Constitucional", "Luis Carlos Sáchica", "DER", 2015, 2),
    ("9789587222333", "Anatomía Humana", "Frank Netter", "MED", 2019, 2),
]


class CargadorEjemplo:
    """Utilidades de apoyo para la carga de datos de ejemplo."""

    def hay_datos(self) -> bool:
        """True si algún archivo de datos (no de categorías) ya tiene registros."""
        return any(ArchivoUtil(f).leer_lineas() for f in ARCHIVOS_DATOS)

    def limpiar(self) -> None:
        """Vacía usuarios, libros, préstamos, multas y reservas."""
        for nombre in ARCHIVOS_DATOS:
            ArchivoUtil(nombre).reescribir([])
        logger.info("Datos reiniciados.")

    def asegurar_categorias(self) -> None:
        """Registra las categorías que falten (catálogo base)."""
        repo = CategoriaRepository()
        for cod, nombre, desc in CATEGORIAS:
            if repo.obtener_por_codigo(cod) is None:
                repo.guardar(Categoria(cod, nombre, desc))
