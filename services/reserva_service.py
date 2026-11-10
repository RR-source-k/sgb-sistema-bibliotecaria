"""Reservation service - Business logic for reservation management."""

import logging
from datetime import datetime
from model.modelos import Reserva
from repositories.reserva_repo import ReservaRepository
from repositories.libro_repo import LibroRepository
from repositories.usuario_repo import UsuarioRepository
from repositories.prestamo_repo import PrestamoRepository

logger = logging.getLogger(__name__)


class ReservaService:
    def __init__(self):
        self.repo = ReservaRepository()
        self.libro_repo = LibroRepository()
        self.usuario_repo = UsuarioRepository()
        self.prestamo_repo = PrestamoRepository()

    def obtener_todos(self) -> list[Reserva]:
        return self.repo.obtener_todos()

    def obtener_activas(self) -> list[Reserva]:
        return self.repo.obtener_activas()

    def obtener_por_usuario(self, numero_documento: str) -> list[Reserva]:
        return self.repo.obtener_por_usuario(numero_documento)

    def obtener_por_isbn(self, isbn: str) -> list[Reserva]:
        return self.repo.obtener_por_isbn(isbn)

    def crear_reserva(self, isbn: str, numero_documento: str) -> tuple[bool, str]:
        """
        Create a reservation. Returns (success, message).
        Validates:
          - User exists and is active
          - Book exists
          - Book has no available copies (reservations only apply to unavailable books)
          - User doesn't already have an active reservation for this book
        """
        # 1. Validate user
        usuario = self.usuario_repo.obtener_por_documento(numero_documento)
        if usuario is None:
            return False, f"Usuario con documento {numero_documento} no encontrado."
        if usuario.estado != "Activo":
            return False, f"Usuario {numero_documento} está desactivado."

        # 2. Validate book
        libro = self.libro_repo.obtener_por_isbn(isbn)
        if libro is None:
            return False, f"Libro con ISBN {isbn} no encontrado."

        # 2b. Solo se reservan libros sin ejemplares disponibles (RF-04)
        if libro.disponibles > 0:
            return False, (
                f"'{libro.titulo}' tiene {libro.disponibles} ejemplar(es) disponible(s); "
                f"puede solicitarse como préstamo directamente."
            )

        # 3. Check for existing active reservation by user for this book
        reservas_existentes = self.obtener_por_usuario(numero_documento)
        for res in reservas_existentes:
            if res.isbn == isbn and res.estado == "Activa":
                return False, (
                    f"Ya tienes una reserva activa para '{libro.titulo}'."
                )

        # 4. Create reservation
        codigo = self.repo._generar_codigo("RES")
        reserva = Reserva(
            codigo=codigo,
            isbn=isbn,
            numero_documento=numero_documento,
            fecha_reserva=datetime.now().strftime("%Y-%m-%d"),
            estado="Activa",
        )

        if not self.repo.guardar(reserva):
            return False, "Error al registrar la reserva."

        logger.info(f"Reservation created: {codigo} - {isbn} - {numero_documento}")
        return True, (
            f"Reserva creada exitosamente para '{libro.titulo}'. "
            f"Se te notificará cuando el libro esté disponible."
        )

    def cancelar_reserva(self, codigo: str) -> tuple[bool, str]:
        """Cancel a reservation. Returns (success, message)."""
        reserva = self.repo.obtener_por_codigo(codigo)
        if reserva is None:
            return False, "Reserva no encontrada."
        if reserva.estado != "Activa":
            return False, "Esta reserva ya no está activa."

        reserva.estado = "Cancelada"
        if self.repo.actualizar(reserva):
            logger.info(f"Reservation cancelled: {codigo}")
            return True, "Reserva cancelada exitosamente."
        return False, "Error al cancelar la reserva."

    def activar_reserva(self, codigo: str) -> tuple[bool, str]:
        """
        Activate a reservation (when a book becomes available).
        In a real system this would send a notification.
        Returns (success, message).
        """
        reserva = self.repo.obtener_por_codigo(codigo)
        if reserva is None:
            return False, "Reserva no encontrada."

        if reserva.estado != "Activa":
            return False, "Solo se pueden activar reservas en estado Activa."

        reserva.estado = "Entregada"
        if self.repo.actualizar(reserva):
            logger.info(f"Reservation activated: {codigo}")
            return True, "Reserva atendida. El libro queda disponible para el usuario."
        return False, "Error al activar la reserva."
