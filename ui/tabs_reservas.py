"""
Reservas tab - Reservation management interface.
"""

import customtkinter as ctk
from tkinter import messagebox

from services.reserva_service import ReservaService
from repositories.usuario_repo import UsuarioRepository
from model.enums import EstadoReservaEnum
from ui.tabla import dibujar_tabla, COLOR_VERDE, COLOR_ROJO, COLOR_GRIS

COLUMNAS = ["Código", "ISBN", "Documento", "Usuario", "Fecha Reserva", "Estado"]
COLORES_ESTADO = {
    EstadoReservaEnum.ACTIVA.value: COLOR_VERDE,
    EstadoReservaEnum.CANCELADA.value: COLOR_ROJO,
    EstadoReservaEnum.ENTREGADA.value: COLOR_GRIS,
}


class TabReservas(ctk.CTkFrame):
    """Tab for reservation management (create, cancel, activate, filter)."""

    def __init__(self, parent):
        super().__init__(parent)

        self.service = ReservaService()
        self.usuario_repo = UsuarioRepository()
        self.filtro_actual = "activas"

        # --- Row 0: formulario y acciones ---
        form = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        form.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(
            form, text="Gestión de Reservas", text_color="#222222",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=6, padx=15, pady=(10, 5), sticky="w")

        ctk.CTkLabel(form, text="ISBN:", text_color="#222222").grid(
            row=1, column=0, padx=(15, 5), pady=5, sticky="w")
        self.isbn_entry = ctk.CTkEntry(form, width=170)
        self.isbn_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(form, text="Documento:", text_color="#222222").grid(
            row=1, column=2, padx=(15, 5), pady=5, sticky="w")
        self.documento_entry = ctk.CTkEntry(form, width=150)
        self.documento_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        ctk.CTkButton(
            form, text="Crear Reserva", width=130,
            fg_color="#2E86C1", hover_color="#1B4F72",
            command=self._crear_reserva,
        ).grid(row=1, column=4, padx=10, pady=5)

        # Acciones sobre una reserva existente (por código)
        ctk.CTkLabel(form, text="Código reserva:", text_color="#222222").grid(
            row=2, column=0, padx=(15, 5), pady=5, sticky="w")
        self.codigo_entry = ctk.CTkEntry(
            form, width=170, placeholder_text="Clic en una fila para elegir")
        self.codigo_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkButton(
            form, text="Cancelar", width=100,
            fg_color=COLOR_ROJO, hover_color="#C0392B",
            command=self._cancelar_reserva,
        ).grid(row=2, column=2, padx=5, pady=5, sticky="w")

        ctk.CTkButton(
            form, text="Activar (atender)", width=130,
            fg_color=COLOR_VERDE, hover_color="#1E8449",
            command=self._activar_reserva,
        ).grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # Filtros
        filtros = ctk.CTkFrame(form, fg_color="transparent")
        filtros.grid(row=3, column=0, columnspan=6, padx=10, pady=(5, 10), sticky="w")
        ctk.CTkLabel(filtros, text="Filtrar:", text_color="#222222").grid(
            row=0, column=0, padx=5)
        for i, (texto, color, hover, accion) in enumerate([
            ("Activas", "#2E86C1", "#1B4F72", lambda: self._filtrar("activas")),
            ("Todas", "#7F8C8D", "#626D6F", lambda: self._filtrar("todas")),
            ("Por usuario", "#8E44AD", "#6C3483", lambda: self._filtrar("usuario")),
            ("Por ISBN", "#16A085", "#117A65", lambda: self._filtrar("isbn")),
        ], start=1):
            ctk.CTkButton(filtros, text=texto, width=100, fg_color=color,
                          hover_color=hover, command=accion).grid(
                row=0, column=i, padx=4)

        # --- Row 1: tabla scrollable ---
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        table_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_table = ctk.CTkScrollableFrame(table_frame, fg_color="#ffffff")
        self.scrollable_table.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.refresh_table()

    # ------------------------------------------------------------------ tabla
    def refresh_table(self):
        """Recarga la tabla con el filtro vigente."""
        self._mostrar(self._reservas_del_filtro())

    def _reservas_del_filtro(self):
        if self.filtro_actual == "todas":
            return self.service.obtener_todos()
        if self.filtro_actual == "usuario":
            doc = self.documento_entry.get().strip()
            return self.service.obtener_por_usuario(doc) if doc else []
        if self.filtro_actual == "isbn":
            isbn = self.isbn_entry.get().strip()
            return self.service.obtener_por_isbn(isbn) if isbn else []
        return self.service.obtener_activas()

    def _nombre_usuario(self, documento: str) -> str:
        usuario = self.usuario_repo.obtener_por_documento(documento)
        return usuario.nombre if usuario else "(desconocido)"

    def _mostrar(self, reservas):
        filas = [
            (r.codigo, r.isbn, r.numero_documento,
             self._nombre_usuario(r.numero_documento), r.fecha_reserva, r.estado)
            for r in reservas
        ]
        dibujar_tabla(
            self.scrollable_table, COLUMNAS, filas,
            header_color="#2E86C1", col_estado=5, colores_estado=COLORES_ESTADO,
            on_select=self._seleccionar_fila,
            mensaje_vacio="No hay reservas para este filtro.",
        )

    def _seleccionar_fila(self, fila):
        self.codigo_entry.delete(0, "end")
        self.codigo_entry.insert(0, fila[0])

    def _filtrar(self, tipo):
        if tipo == "usuario" and not self.documento_entry.get().strip():
            messagebox.showerror("Error", "Ingrese un documento para filtrar por usuario.")
            return
        if tipo == "isbn" and not self.isbn_entry.get().strip():
            messagebox.showerror("Error", "Ingrese un ISBN para filtrar por libro.")
            return
        self.filtro_actual = tipo
        self.refresh_table()

    # ---------------------------------------------------------------- acciones
    def _crear_reserva(self):
        isbn = self.isbn_entry.get().strip()
        documento = self.documento_entry.get().strip()
        if not isbn or not documento:
            messagebox.showerror("Error", "Debe ingresar ISBN y documento.")
            return

        ok, mensaje = self.service.crear_reserva(isbn, documento)
        if ok:
            messagebox.showinfo("Éxito", mensaje)
            self.isbn_entry.delete(0, "end")
            self.documento_entry.delete(0, "end")
            self.filtro_actual = "activas"
            self.refresh_table()
        else:
            messagebox.showerror("Error", mensaje)

    def _codigo(self):
        codigo = self.codigo_entry.get().strip()
        if not codigo:
            messagebox.showerror("Error", "Seleccione una reserva (clic en la tabla) "
                                          "o escriba su código.")
        return codigo

    def _cancelar_reserva(self):
        codigo = self._codigo()
        if not codigo:
            return
        if not messagebox.askyesno("Confirmar", f"¿Cancelar la reserva {codigo}?"):
            return
        self._resultado(self.service.cancelar_reserva(codigo))

    def _activar_reserva(self):
        codigo = self._codigo()
        if codigo:
            self._resultado(self.service.activar_reserva(codigo))

    def _resultado(self, resultado):
        ok, mensaje = resultado
        if ok:
            messagebox.showinfo("Éxito", mensaje)
            self.codigo_entry.delete(0, "end")
            self.refresh_table()
        else:
            messagebox.showerror("Error", mensaje)
