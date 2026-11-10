"""
Multas tab - Fine management interface.
"""

import customtkinter as ctk
from tkinter import messagebox

from services.multa_service import MultaService
from repositories.prestamo_repo import PrestamoRepository
from model.enums import EstadoMultaEnum
from ui.tabla import dibujar_tabla, COLOR_VERDE, COLOR_ROJO

COLUMNAS = ["Código", "Préstamo", "Documento", "Días retraso", "Valor", "Estado"]
COLORES_ESTADO = {
    EstadoMultaEnum.PENDIENTE.value: COLOR_ROJO,
    EstadoMultaEnum.PAGADA.value: COLOR_VERDE,
}


class TabMultas(ctk.CTkFrame):
    """Tab for fine management (display, payment, delinquency)."""

    def __init__(self, parent):
        super().__init__(parent)

        self.service = MultaService()
        self.prestamo_repo = PrestamoRepository()
        self.filtro_actual = "pendientes"

        # --- Row 0: acciones ---
        action = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        action.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(
            action, text="Gestión de Multas", text_color="#222222",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=6, padx=15, pady=(10, 5), sticky="w")

        ctk.CTkLabel(action, text="Documento:", text_color="#222222").grid(
            row=1, column=0, padx=(15, 5), pady=5, sticky="w")
        self.documento_entry = ctk.CTkEntry(action, width=150)
        self.documento_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkButton(
            action, text="Ver por documento", width=150,
            fg_color="#8E44AD", hover_color="#6C3483",
            command=lambda: self._filtrar("documento"),
        ).grid(row=1, column=2, padx=5, pady=5)

        ctk.CTkButton(
            action, text="Generar por vencidos", width=170,
            fg_color="#E67E22", hover_color="#D35400",
            command=self._generar_vencidas,
        ).grid(row=1, column=3, padx=5, pady=5)
        ctk.CTkButton(
            action, text="Reporte de morosidad", width=170,
            fg_color="#C0392B", hover_color="#922B21",
            command=self._mostrar_morosos,
        ).grid(row=1, column=4, padx=5, pady=5)

        ctk.CTkLabel(action, text="Código multa:", text_color="#222222").grid(
            row=2, column=0, padx=(15, 5), pady=5, sticky="w")
        self.codigo_entry = ctk.CTkEntry(
            action, width=150, placeholder_text="Clic en una fila")
        self.codigo_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkButton(
            action, text="Cobrar (marcar pagada)", width=190,
            fg_color=COLOR_VERDE, hover_color="#1E8449",
            command=self._pagar,
        ).grid(row=2, column=2, columnspan=2, padx=5, pady=5, sticky="w")

        filtros = ctk.CTkFrame(action, fg_color="transparent")
        filtros.grid(row=3, column=0, columnspan=6, padx=10, pady=(5, 10), sticky="w")
        ctk.CTkLabel(filtros, text="Filtrar:", text_color="#222222").grid(row=0, column=0, padx=5)
        for i, (texto, color, hover, tipo) in enumerate([
            ("Pendientes", "#2E86C1", "#1B4F72", "pendientes"),
            ("Pagadas", COLOR_VERDE, "#1E8449", "pagadas"),
            ("Todas", "#7F8C8D", "#626D6F", "todas"),
        ], start=1):
            ctk.CTkButton(filtros, text=texto, width=100, fg_color=color,
                          hover_color=hover,
                          command=lambda t=tipo: self._filtrar(t)).grid(
                row=0, column=i, padx=4)

        # --- Row 1: tabla ---
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        table_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.total_label = ctk.CTkLabel(
            table_frame, text="", text_color="#222222",
            font=ctk.CTkFont(size=13, weight="bold"))
        self.total_label.grid(row=0, column=0, padx=15, pady=(8, 0), sticky="w")

        self.scrollable_table = ctk.CTkScrollableFrame(table_frame, fg_color="#ffffff")
        self.scrollable_table.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_table()

    # ------------------------------------------------------------------ tabla
    def refresh_table(self):
        """Recarga la tabla con el filtro vigente."""
        self._filtrar(self.filtro_actual, silencioso=True)

    def _documento_de(self, multa) -> str:
        prestamo = self.prestamo_repo.obtener_por_codigo(multa.codigo_prestamo)
        return prestamo.numero_documento if prestamo else "-"

    def _filtrar(self, tipo, silencioso=False):
        if tipo == "documento":
            doc = self.documento_entry.get().strip()
            if not doc:
                if not silencioso:
                    messagebox.showerror("Error", "Debe ingresar un documento.")
                return
            multas = self.service.obtener_por_usuario(doc)
        elif tipo == "pagadas":
            multas = [m for m in self.service.obtener_todos()
                      if m.estado == EstadoMultaEnum.PAGADA.value]
        elif tipo == "todas":
            multas = self.service.obtener_todos()
        else:
            tipo = "pendientes"
            multas = self.service.obtener_pendientes()

        self.filtro_actual = tipo
        filas = [
            (m.codigo, m.codigo_prestamo, self._documento_de(m), m.dias_retraso,
             f"${m.valor:,} COP", m.estado)
            for m in multas
        ]
        dibujar_tabla(
            self.scrollable_table, COLUMNAS, filas,
            header_color="#E74C3C", col_estado=5, colores_estado=COLORES_ESTADO,
            on_select=self._seleccionar_fila,
            mensaje_vacio="No hay multas para este filtro.",
        )
        total = sum(m.valor for m in multas if m.estado == EstadoMultaEnum.PENDIENTE.value)
        self.total_label.configure(
            text=f"{len(multas)} multa(s) — Pendiente en esta vista: ${total:,} COP")

    def _seleccionar_fila(self, fila):
        self.codigo_entry.delete(0, "end")
        self.codigo_entry.insert(0, fila[0])

    # ---------------------------------------------------------------- acciones
    def _pagar(self):
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showerror("Error", "Seleccione una multa o escriba su código.")
            return
        ok, mensaje = self.service.pagar_multa(codigo)
        if ok:
            messagebox.showinfo("Éxito", mensaje)
            self.codigo_entry.delete(0, "end")
            self.refresh_table()
        else:
            messagebox.showerror("Error", mensaje)

    def _generar_vencidas(self):
        ok, mensaje = self.service.generar_multas_vencidas()
        (messagebox.showinfo if ok else messagebox.showerror)(
            "Multas por vencimiento" if ok else "Error", mensaje)
        self._filtrar("pendientes")

    def _mostrar_morosos(self):
        morosos = self.service.obtener_morosos()
        filas = [(u["documento"], u["nombre"], u["cantidad_multas"],
                  f"${u['monto_total']:,} COP") for u in morosos]
        dibujar_tabla(
            self.scrollable_table,
            ["Documento", "Nombre", "Multas pendientes", "Monto total"], filas,
            header_color="#922B21",
            mensaje_vacio="No hay usuarios morosos actualmente.",
        )
        self.total_label.configure(text=f"Reporte de morosidad — {len(morosos)} usuario(s)")
