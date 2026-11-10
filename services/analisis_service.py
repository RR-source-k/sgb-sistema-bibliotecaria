"""Analysis service - Business logic for reports and analytics."""

import logging
from collections import Counter
from datetime import datetime

from repositories.prestamo_repo import PrestamoRepository
from repositories.multa_repo import MultaRepository
from repositories.libro_repo import LibroRepository
from repositories.usuario_repo import UsuarioRepository
from repositories.categoria_repo import CategoriaRepository

logger = logging.getLogger(__name__)


class AnalisisDatosService:
    def __init__(self):
        self.prestamo_repo = PrestamoRepository()
        self.multa_repo = MultaRepository()
        self.libro_repo = LibroRepository()
        self.usuario_repo = UsuarioRepository()
        self.categoria_repo = CategoriaRepository()

    def libros_mas_prestados(self, top_n: int = 10) -> list[tuple[str, int]]:
        """Return the most loaned books as [(isbn, count), ...]."""
        todos = self.prestamo_repo.obtener_todos()
        isbn_counts = Counter(p.isbn for p in todos)
        resultados = []
        for isbn, count in isbn_counts.most_common(top_n):
            libro = self.libro_repo.obtener_por_isbn(isbn)
            titulo = libro.titulo if libro else isbn
            resultados.append((isbn, titulo, count))
        return resultados

    def prestamos_por_categoria(self) -> list[tuple[str, str, int]]:
        """Return loans count per category as [(codigo_cat, nombre_cat, count), ...]."""
        todos = self.prestamo_repo.obtener_todos()
        cat_counts: Counter = Counter()

        for prestamo in todos:
            libro = self.libro_repo.obtener_por_isbn(prestamo.isbn)
            if libro:
                cat_counts[libro.codigo_categoria] += 1

        nombres = {c.codigo: c.nombre for c in self.categoria_repo.obtener_todos()}
        resultados = []
        for cat_code, count in cat_counts.most_common():
            resultados.append((cat_code, nombres.get(cat_code, cat_code), count))
        return resultados

    def tasa_infraccion(self) -> list[tuple[str, float, int, int]]:
        """
        Return delinquency rate by user type.
        Returns [(tipo_usuario, tasa_porcentaje, total_prestamos, prestamos_vencidos), ...].
        """
        todos = self.prestamo_repo.obtener_todos()
        today = datetime.now().strftime("%Y-%m-%d")

        # Group by user document
        user_prestamos: dict[str, list] = {}
        for p in todos:
            user_prestamos.setdefault(p.numero_documento, []).append(p)

        tipo_stats: dict[str, dict] = {}
        for documento, prestamos in user_prestamos.items():
            usuario = self.usuario_repo.obtener_por_documento(documento)
            if not usuario:
                continue
            tipo = usuario.tipo
            if tipo not in tipo_stats:
                tipo_stats[tipo] = {"total": 0, "vencidos": 0}
            tipo_stats[tipo]["total"] += len(prestamos)
            for p in prestamos:
                sin_devolver_vencido = p.estado != "Devuelto" and p.fecha_limite < today
                devuelto_tarde = (
                    p.estado == "Devuelto" and p.fecha_devolucion
                    and p.fecha_devolucion > p.fecha_limite
                )
                if sin_devolver_vencido or devuelto_tarde:
                    tipo_stats[tipo]["vencidos"] += 1

        resultados = []
        for tipo, stats in tipo_stats.items():
            tasa = (stats["vencidos"] / stats["total"] * 100) if stats["total"] > 0 else 0.0
            resultados.append((tipo, round(tasa, 2), stats["total"], stats["vencidos"]))
        return resultados

    def duracion_promedio_prestamo(self) -> float:
        """Return average loan duration in days (only for returned loans)."""
        todos = self.prestamo_repo.obtener_todos()
        duraciones = []

        for p in todos:
            if p.estado == "Devuelto" and p.fecha_devolucion:
                fecha_prestamo = datetime.strptime(p.fecha_prestamo, "%Y-%m-%d")
                fecha_devolucion = datetime.strptime(p.fecha_devolucion, "%Y-%m-%d")
                duracion = (fecha_devolucion - fecha_prestamo).days
                duraciones.append(duracion)

        if not duraciones:
            return 0.0
        return round(sum(duraciones) / len(duraciones), 2)

    def reporte_multas(self) -> dict:
        """
        Generate a fine summary report.
        Returns a dict with:
          - total_multas: total count
          - total_pendientes: pending count
          - total_pagadas: paid count
          - monto_total: total fine amount
          - monto_pendiente: pending fine amount
          - monto_pagado: paid fine amount
        """
        todas = self.multa_repo.obtener_todos()

        pendientes = [m for m in todas if m.estado == "Pendiente"]
        pagadas = [m for m in todas if m.estado == "Pagada"]

        return {
            "total_multas": len(todas),
            "total_pendientes": len(pendientes),
            "total_pagadas": len(pagadas),
            "monto_total": sum(m.valor for m in todas),
            "monto_pendiente": sum(m.valor for m in pendientes),
            "monto_pagado": sum(m.valor for m in pagadas),
        }

    def resumen_completo(self) -> dict:
        """Generate a complete summary report with all analytics."""
        return {
            "libros_mas_prestados": self.libros_mas_prestados(),
            "prestamos_por_categoria": self.prestamos_por_categoria(),
            "tasa_infraccion": self.tasa_infraccion(),
            "duracion_promedio": self.duracion_promedio_prestamo(),
            "reporte_multas": self.reporte_multas(),
            "estadisticas_generales": {
                "total_libros": len(self.libro_repo.obtener_todos()),
                "total_usuarios": len(self.usuario_repo.obtener_todos()),
                "total_prestamos": len(self.prestamo_repo.obtener_todos()),
                "prestamos_activos": len(self.prestamo_repo.obtener_activos()),
            },
        }
