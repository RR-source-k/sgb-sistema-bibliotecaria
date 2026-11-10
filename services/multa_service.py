"""Fine service - Business logic for fine management."""

import logging
from model.modelos import Multa
from repositories.multa_repo import MultaRepository
from repositories.prestamo_repo import PrestamoRepository
from repositories.usuario_repo import UsuarioRepository

logger = logging.getLogger(__name__)


class MultaService:
    def __init__(self):
        self.repo = MultaRepository()
        self.prestamo_repo = PrestamoRepository()
        self.usuario_repo = UsuarioRepository()

    def obtener_todos(self) -> list[Multa]:
        return self.repo.obtener_todos()

    def obtener_pendientes(self) -> list[Multa]:
        return self.repo.obtener_pendientes()

    def obtener_por_prestamo(self, codigo_prestamo: str) -> list[Multa]:
        return self.repo.obtener_por_prestamo(codigo_prestamo)

    def obtener_por_usuario(self, numero_documento: str) -> list[Multa]:
        """Get all fines for a user by cross-referencing their loans."""
        # Get all loans for this user
        prestamos = self.prestamo_repo.obtener_por_usuario(numero_documento)
        prestamo_codigos = {p.codigo for p in prestamos}

        # Filter fines by those loan codes
        all_multas = self.repo.obtener_todos()
        return [m for m in all_multas if m.codigo_prestamo in prestamo_codigos]

    def obtener_total_pendiente_usuario(self, numero_documento: str) -> int:
        """Get total pending fine amount for a user."""
        multas = self.obtener_por_usuario(numero_documento)
        return sum(m.valor for m in multas if m.estado == "Pendiente")

    def obtener_total_pendiente_sistema(self) -> int:
        """Get total pending fines across all users."""
        return self.repo.obtener_total_pendiente()

    def pagar_multa(self, codigo_multa: str) -> tuple[bool, str]:
        """Pay a fine by setting its status to 'Pagada'. Returns (success, message)."""
        multa = self.repo.obtener_por_codigo(codigo_multa)
        if multa is None:
            return False, "Multa no encontrada."
        if multa.estado == "Pagada":
            return False, "Esta multa ya fue pagada."

        multa.estado = "Pagada"
        if self.repo.actualizar(multa):
            logger.info(f"Fine paid: {codigo_multa}")
            return True, "Multa pagada exitosamente."
        return False, "Error al procesar el pago de la multa."

    def calcular_multas_vencidas(self) -> list[Multa]:
        """
        Scan overdue loans and generate fines for them.
        Returns list of newly created fines.
        """
        from datetime import datetime

        # Get active loans past due date
        today = datetime.now().strftime("%Y-%m-%d")
        activos = self.prestamo_repo.obtener_activos()
        vencidos = []
        for p in activos:
            if p.fecha_limite < today:
                vencidos.append(p)

        nuevas_multas = []
        for prestamo in vencidos:
            # Check if fine already exists
            existentes = self.obtener_por_prestamo(prestamo.codigo)
            if existentes:
                continue

            fecha_limite = datetime.strptime(prestamo.fecha_limite, "%Y-%m-%d")
            dias_retraso = (datetime.now() - fecha_limite).days
            if dias_retraso <= 0:
                continue

            valor = dias_retraso * 1000
            codigo = self.repo._generar_codigo("MUL")

            multa = Multa(
                codigo=codigo,
                codigo_prestamo=prestamo.codigo,
                dias_retraso=dias_retraso,
                valor=valor,
                estado="Pendiente",
            )

            if self.repo.guardar(multa):
                nuevas_multas.append(multa)
                logger.info(
                    f"Overdue fine generated: {codigo} - "
                    f"${valor} ({dias_retraso} days)"
                )

        return nuevas_multas

    def generar_multas_vencidas(self) -> tuple[bool, str]:
        """Genera multas para los préstamos vencidos. Retorna (éxito, mensaje)."""
        nuevas = self.calcular_multas_vencidas()
        if not nuevas:
            return True, "No hay préstamos vencidos sin multa."
        total = sum(m.valor for m in nuevas)
        return True, f"Se generaron {len(nuevas)} multa(s) por un total de ${total:,} COP."

    def obtener_morosos(self) -> list[dict]:
        """
        Usuarios con multas pendientes.
        Retorna [{documento, nombre, cantidad_multas, monto_total}, ...].
        """
        por_usuario: dict[str, dict] = {}
        for multa in self.obtener_pendientes():
            prestamo = self.prestamo_repo.obtener_por_codigo(multa.codigo_prestamo)
            if prestamo is None:
                continue
            doc = prestamo.numero_documento
            if doc not in por_usuario:
                usuario = self.usuario_repo.obtener_por_documento(doc)
                por_usuario[doc] = {
                    "documento": doc,
                    "nombre": usuario.nombre if usuario else "(desconocido)",
                    "cantidad_multas": 0,
                    "monto_total": 0,
                }
            por_usuario[doc]["cantidad_multas"] += 1
            por_usuario[doc]["monto_total"] += multa.valor
        return sorted(por_usuario.values(), key=lambda u: u["monto_total"], reverse=True)
