"""
Análisis tab - Dashboard analítico (KPIs, rankings y reportes).
"""

import customtkinter as ctk

from services.analisis_service import AnalisisDatosService
from ui.tabla import dibujar_tabla, limpiar


class TabAnalisis(ctk.CTkFrame):
    """Dashboard con indicadores de uso de la colección y morosidad."""

    def __init__(self, parent):
        super().__init__(parent)

        self.service = AnalisisDatosService()

        # --- Row 0: encabezado + botón actualizar ---
        header = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        header.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header, text="Dashboard Analítico", text_color="#222222",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")
        ctk.CTkButton(
            header, text="Actualizar", width=110,
            fg_color="#2E86C1", hover_color="#1B4F72",
            command=self.refresh_table,
        ).grid(row=0, column=1, padx=15, pady=10)

        # --- Row 1: contenido scrollable ---
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="#f5f5f5")
        self.scroll.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)
        self.scroll.grid_columnconfigure(1, weight=1)

        self.kpi_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
        self.kpi_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.frame_top = self._seccion(1, 0, "Libros más prestados (Top 10)")
        self.frame_cat = self._seccion(1, 1, "Préstamos por categoría")
        self.frame_inf = self._seccion(2, 0, "Tasa de infracción por tipo de usuario")
        self.frame_mul = self._seccion(2, 1, "Reporte de multas")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_table()

    def _seccion(self, row, col, titulo):
        """Crea una tarjeta con título y devuelve el frame de contenido."""
        card = ctk.CTkFrame(self.scroll, fg_color="#ffffff", corner_radius=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            card, text=titulo, text_color="#222222",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(10, 4), sticky="w")
        contenido = ctk.CTkFrame(card, fg_color="transparent")
        contenido.grid(row=1, column=0, padx=8, pady=(0, 10), sticky="nsew")
        return contenido

    def _kpi(self, col, titulo, valor, color):
        card = ctk.CTkFrame(self.kpi_frame, fg_color=color, corner_radius=10)
        card.grid(row=0, column=col, padx=5, sticky="nsew")
        self.kpi_frame.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(card, text=str(valor), text_color="white",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(padx=12, pady=(12, 0))
        ctk.CTkLabel(card, text=titulo, text_color="white",
                     font=ctk.CTkFont(size=11)).pack(padx=12, pady=(0, 12))

    # ------------------------------------------------------------------ datos
    def refresh_table(self):
        """Recalcula y redibuja todas las secciones del dashboard."""
        datos = self.service.resumen_completo()
        gen = datos["estadisticas_generales"]
        multas = datos["reporte_multas"]

        # KPIs
        limpiar(self.kpi_frame)
        tasa_global = self._tasa_global(datos["tasa_infraccion"])
        self._kpi(0, "Total préstamos", gen["total_prestamos"], "#2E86C1")
        self._kpi(1, "Préstamos activos", gen["prestamos_activos"], "#16A085")
        self._kpi(2, "Duración promedio (días)", f"{datos['duracion_promedio']:.1f}", "#8E44AD")
        self._kpi(3, "Tasa de infracción", f"{tasa_global:.1f}%", "#E67E22")
        self._kpi(4, "Multas pendientes", f"${multas['monto_pendiente']:,}", "#C0392B")

        # Top libros
        dibujar_tabla(
            self.frame_top, ["#", "Título", "Préstamos"],
            [(i, titulo, n) for i, (_isbn, titulo, n)
             in enumerate(datos["libros_mas_prestados"], start=1)],
            header_color="#2E86C1", mensaje_vacio="Aún no hay préstamos.")

        # Por categoría (con porcentaje)
        total_cat = sum(n for _c, _nom, n in datos["prestamos_por_categoria"]) or 1
        dibujar_tabla(
            self.frame_cat, ["Código", "Categoría", "Préstamos", "%"],
            [(c, nom, n, f"{n / total_cat * 100:.1f}%")
             for c, nom, n in datos["prestamos_por_categoria"]],
            header_color="#16A085", mensaje_vacio="Aún no hay préstamos.")

        # Tasa de infracción
        dibujar_tabla(
            self.frame_inf, ["Tipo de usuario", "Préstamos", "Con infracción", "Tasa"],
            [(tipo, total, venc, f"{tasa:.1f}%")
             for tipo, tasa, total, venc in datos["tasa_infraccion"]],
            header_color="#E67E22", mensaje_vacio="Aún no hay préstamos.")

        # Reporte de multas
        dibujar_tabla(
            self.frame_mul, ["Concepto", "Cantidad", "Valor (COP)"],
            [
                ("Generadas", multas["total_multas"], f"${multas['monto_total']:,}"),
                ("Pagadas", multas["total_pagadas"], f"${multas['monto_pagado']:,}"),
                ("Pendientes", multas["total_pendientes"], f"${multas['monto_pendiente']:,}"),
            ],
            header_color="#C0392B")

    @staticmethod
    def _tasa_global(tasas) -> float:
        total = sum(t[2] for t in tasas)
        infr = sum(t[3] for t in tasas)
        return (infr / total * 100) if total else 0.0
