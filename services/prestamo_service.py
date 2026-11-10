"""Loan service - Business logic for loan management."""

import logging
from datetime import datetime, timedelta
from model.modelos import Prestamo, Usuario
from repositories.prestamo_repo import PrestamoRepository
from repositories.libro_repo import LibroRepository
from repositories.usuario_repo import UsuarioRepository
from repositories.multa_repo import MultaRepository
from model.modelos import Multa
from model.enums import TipoUsuarioEnum

logger = logging.getLogger(__name__)

# Loan periods by user type (in days)
LOAN_PERIODS = {
    TipoUsuarioEnum.ESTUDIANTE.value: 7,
    TipoUsuarioEnum.DOCENTE.value: 15,
    TipoUsuarioEnum.EXTERNO.value: 5,
}

# Maximum active loans by user type
LOAN_LIMITS = {
    TipoUsuarioEnum.ESTUDIANTE.value: 3,
    TipoUsuarioEnum.DOCENTE.value: 5,
    TipoUsuarioEnum.EXTERNO.value: 2,
}


# Fine per day of delay (COP)
VALOR_MULTA_DIA = 1000


class PrestamoService:
    def __init__(self):
        self.repo = PrestamoRepository()
        self.libro_repo = LibroRepository()
        self.usuario_repo = UsuarioRepository()
        self.multa_repo = MultaRepository()

    def obtener_todos(self) -> list[Prestamo]:
        return self.repo.obtener_todos()

    def obtener_activos(self) -> list[Prestamo]:
        return self.repo.obtener_activos()

    def obtener_por_usuario(self, documento: str) -> list[Prestamo]:
        return self.repo.obtener_por_usuario(documento)

    def crear_prestamo(self, isbn: str, numero_documento: str) -> tuple[bool, str]:
        """
        Create a new loan. Returns (success, message).
        Validates:
          - User exists and is active
          - Book exists and has available copies
          - User hasn't reached their loan limit
        """
        # 1. Validate user
        usuario = self.usuario_repo.obtener_por_documento(numero_documento)
        if usuario is None:
            return False, f"Usuario con documento {numero_documento} no encontrado."
        if usuario.estado != "Activo":
            return False, f"Usuario {numero_documento} está desactivado."

        # 1b. El usuario no debe tener multas pendientes (RF-03)
        codigos_usuario = {
            p.codigo for p in self.repo.obtener_por_usuario(numero_documento)
        }
        multas_pendientes = [
            m for m in self.multa_repo.obtener_pendientes()
            if m.codigo_prestamo in codigos_usuario
        ]
        if multas_pendientes:
            total = sum(m.valor for m in multas_pendientes)
            return False, (
                f"El usuario tiene {len(multas_pendientes)} multa(s) pendiente(s) "
                f"por ${total:,} COP. Debe pagarlas antes de un nuevo préstamo."
            )

        # 2. Validate book
        libro = self.libro_repo.obtener_por_isbn(isbn)
        if libro is None:
            return False, f"Libro con ISBN {isbn} no encontrado."
        if libro.disponibles <= 0:
            return False, f"No hay ejemplares disponibles de '{libro.titulo}'."

        # 3. Check loan limit
        tipo_usuario = usuario.tipo
        limite = LOAN_LIMITS.get(tipo_usuario, 0)
        prestamos_activos = self.obtener_activos()
        prestamos_usuario = [
            p for p in prestamos_activos
            if p.numero_documento == numero_documento
        ]
        if len(prestamos_usuario) >= limite:
            return False, (
                f"El usuario ha alcanzado el límite de {limite} préstamos activos "
                f"(tipo: {tipo_usuario})."
            )

        # 4. Create loan
        periodo = LOAN_PERIODS.get(tipo_usuario, 7)
        fecha_prestamo = datetime.now()
        fecha_limite = fecha_prestamo + timedelta(days=periodo)
        codigo = self.repo._generar_codigo("PRE")

        prestamo = Prestamo(
            codigo=codigo,
            isbn=isbn,
            numero_documento=numero_documento,
            fecha_prestamo=fecha_prestamo.strftime("%Y-%m-%d"),
            fecha_limite=fecha_limite.strftime("%Y-%m-%d"),
            fecha_devolucion="",
            estado="Activo",
        )

        if not self.repo.guardar(prestamo):
            return False, "Error al registrar el préstamo."

        # 5. Decrement available copies
        libro.disponibles -= 1
        if not self.libro_repo.actualizar(libro):
            # Rollback: remove the loan
            self.repo.eliminar(codigo)
            libro.disponibles += 1
            self.libro_repo.actualizar(libro)
            return False, "Error al actualizar disponibilidad del libro."

        logger.info(f"Loan created: {codigo} - {isbn} - {numero_documento}")
        return True, (
            f"Préstamo creado exitosamente. "
            f"Fecha límite: {fecha_limite.strftime('%Y-%m-%d')}."
        )

    def devolver(self, codigo_prestamo: str) -> tuple[bool, str]:
        """
        Process a book return. Returns (success, message).
        Calculates fine if overdue.
        """
        prestamo = self.repo.obtener_por_codigo(codigo_prestamo)
        if prestamo is None:
            return False, "Préstamo no encontrado."
        if prestamo.estado == "Devuelto":
            return False, "Este préstamo ya fue devuelto."

        hoy = datetime.now().date()
        fecha_limite = datetime.strptime(prestamo.fecha_limite, "%Y-%m-%d").date()

        prestamo.fecha_devolucion = hoy.strftime("%Y-%m-%d")
        prestamo.estado = "Devuelto"

        if not self.repo.actualizar(prestamo):
            return False, "Error al actualizar el préstamo."

        # Increment available copies
        libro = self.libro_repo.obtener_por_isbn(prestamo.isbn)
        if libro:
            libro.disponibles += 1
            self.libro_repo.actualizar(libro)

        # Si hay retraso, calcular y PERSISTIR la multa ($1,000 COP por día)
        dias_retraso = max((hoy - fecha_limite).days, 0)
        valor_multa = dias_retraso * VALOR_MULTA_DIA

        mensaje = "Devolución registrada exitosamente."
        if dias_retraso > 0:
            existentes = self.multa_repo.obtener_por_prestamo(prestamo.codigo)
            if existentes:
                # Ya se había generado por vencimiento: actualizar, no duplicar
                multa = existentes[0]
                multa.dias_retraso = dias_retraso
                multa.valor = valor_multa
                guardada = self.multa_repo.actualizar(multa)
            else:
                multa = Multa(
                    codigo=self.multa_repo._generar_codigo("MUL"),
                    codigo_prestamo=prestamo.codigo,
                    dias_retraso=dias_retraso,
                    valor=valor_multa,
                    estado="Pendiente",
                )
                guardada = self.multa_repo.guardar(multa)
            if guardada:
                mensaje += (
                    f" Retraso: {dias_retraso} días. "
                    f"Multa generada: ${valor_multa:,} COP."
                )
            else:
                mensaje += " Atención: no se pudo registrar la multa."
            logger.info(f"Overdue detected: {dias_retraso} days, fine ${valor_multa}")

        logger.info(f"Book returned: {codigo_prestamo}")
        return True, mensaje

    def obtener_vencidos(self) -> list[Prestamo]:
        """Get all overdue loans (active and past due date)."""
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        activos = self.obtener_activos()
        vencidos = []
        for p in activos:
            if p.fecha_limite < today:
                vencidos.append(p)
        return vencidos

    def eliminar(self, codigo: str) -> tuple[bool, str]:
        """Delete a loan. Returns (success, message)."""
        prestamo = self.repo.obtener_por_codigo(codigo)
        if prestamo is None:
            return False, "Préstamo no encontrado."
        if prestamo.estado == "Activo":
            return False, "No se puede eliminar un préstamo activo."
        return self.repo.eliminar(codigo)
