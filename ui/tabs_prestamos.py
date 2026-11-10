"""
Prestamos tab - Loan management interface.
"""

import customtkinter as ctk
from tkinter import messagebox

from repositories.prestamo_repo import PrestamoRepository
from repositories.libro_repo import LibroRepository
from repositories.usuario_repo import UsuarioRepository
from services.prestamo_service import PrestamoService
from model.enums import EstadoPrestamoEnum
from ui.tabla import dibujar_tabla, COLOR_VERDE, COLOR_ROJO, COLOR_GRIS


class TabPrestamos(ctk.CTkFrame):
    """Tab for loan management (create, return, display)."""

    def __init__(self, parent):
        super().__init__(parent)

        self.prestamo_service = PrestamoService()
        self.libro_repo = LibroRepository()
        self.usuario_repo = UsuarioRepository()

        # --- Form Frame ---
        form_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(3, weight=1)

        form_title = ctk.CTkLabel(
            form_frame,
            text="Gestión de Préstamos",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        form_title.grid(row=0, column=0, columnspan=4, padx=15, pady=(10, 5))

        # ISBN
        ctk.CTkLabel(form_frame, text="ISBN:").grid(
            row=1, column=0, padx=15, pady=5, sticky="w"
        )
        self.isbn_entry = ctk.CTkEntry(form_frame, width=250)
        self.isbn_entry.grid(row=1, column=1, padx=15, pady=5, sticky="ew")

        # Documento
        ctk.CTkLabel(form_frame, text="Documento:").grid(
            row=1, column=2, padx=15, pady=5, sticky="w"
        )
        self.documento_entry = ctk.CTkEntry(form_frame, width=200)
        self.documento_entry.grid(row=1, column=3, padx=15, pady=5, sticky="ew")

        # Fecha de préstamo (opcional)
        ctk.CTkLabel(form_frame, text="Fecha préstamo:").grid(
            row=2, column=0, padx=15, pady=5, sticky="w"
        )
        self.fecha_entry = ctk.CTkEntry(
            form_frame, width=250, placeholder_text="AAAA-MM-DD (vacío = hoy)"
        )
        self.fecha_entry.grid(row=2, column=1, padx=15, pady=5, sticky="ew")

        # Botón crear préstamo
        btn_create = ctk.CTkButton(
            form_frame,
            text="Crear Préstamo",
            fg_color="#2E86C1",
            hover_color="#1B4F72",
            command=self._crear_prestamo,
        )
        btn_create.grid(row=3, column=0, columnspan=4, padx=15, pady=10)

        # Separador
        separator1 = ctk.CTkFrame(form_frame, fg_color="#E0E0E0", height=2)
        separator1.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

        # --- Return Section ---
        return_frame = ctk.CTkFrame(form_frame, fg_color="#f9f9f9", corner_radius=8)
        return_frame.grid(
            row=5, column=0, columnspan=4, padx=15, pady=5, sticky="ew"
        )

        ctk.CTkLabel(
            return_frame,
            text="Registrar Devolución",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(return_frame, text="Código Préstamo:").grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        self.codigo_prestamo_entry = ctk.CTkEntry(return_frame, width=200)
        self.codigo_prestamo_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        btn_return = ctk.CTkButton(
            return_frame,
            text="Devolver Libro",
            fg_color="#27AE60",
            hover_color="#1E8449",
            command=self._devolver_libro,
        )
        btn_return.grid(row=1, column=2, padx=10, pady=5, sticky="w")

        # --- Table Frame ---
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        filter_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        for i, (texto, color, hover, tipo) in enumerate([
            ("Activos", "#2E86C1", "#1B4F72", "activos"),
            ("Vencidos", COLOR_ROJO, "#C0392B", "vencidos"),
            ("Todos", "#7F8C8D", "#626D6F", "todos"),
        ]):
            ctk.CTkButton(
                filter_frame, text=texto, width=90, fg_color=color, hover_color=hover,
                command=lambda t=tipo: self._load_table(t),
            ).grid(row=0, column=i, padx=5)

        self.scrollable_table = ctk.CTkScrollableFrame(table_frame, fg_color="#ffffff")
        self.scrollable_table.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.filtro_actual = "activos"
        self._load_table("activos")

    def _load_table(self, filter_type="activos"):
        """Load loans table based on filter type."""
        self.filtro_actual = filter_type
        vencidos = {p.codigo for p in self.prestamo_service.obtener_vencidos()}

        if filter_type == "activos":
            loans = self.prestamo_service.obtener_activos()
        elif filter_type == "vencidos":
            loans = [l for l in self.prestamo_service.obtener_activos()
                     if l.codigo in vencidos]
        else:
            loans = self.prestamo_service.obtener_todos()

        def estado_visible(loan):
            # Un préstamo activo pasado de fecha se muestra como Vencido
            return EstadoPrestamoEnum.VENCIDO.value if loan.codigo in vencidos else loan.estado

        filas = [
            (l.codigo, l.isbn, l.numero_documento, estado_visible(l),
             l.fecha_prestamo, l.fecha_limite, l.fecha_devolucion or "Pendiente")
            for l in loans
        ]
        dibujar_tabla(
            self.scrollable_table,
            ["Código", "ISBN", "Documento", "Estado", "Fecha Préstamo",
             "Fecha Límite", "Fecha Devolución"],
            filas, header_color="#2E86C1", col_estado=3,
            colores_estado={
                EstadoPrestamoEnum.ACTIVO.value: "#2E86C1",
                EstadoPrestamoEnum.VENCIDO.value: COLOR_ROJO,
                EstadoPrestamoEnum.DEVUELTO.value: COLOR_VERDE,
            },
            on_select=self._seleccionar_fila,
            mensaje_vacio="No hay préstamos para este filtro.",
        )

    def refresh_table(self):
        """Refresh the current table view."""
        self._load_table(self.filtro_actual)

    def _seleccionar_fila(self, fila):
        """Clic en una fila: carga el código en el campo de devolución."""
        self.codigo_prestamo_entry.delete(0, "end")
        self.codigo_prestamo_entry.insert(0, fila[0])

    def _crear_prestamo(self):
        """Create a new loan."""
        isbn = self.isbn_entry.get().strip()
        documento = self.documento_entry.get().strip()

        if not isbn or not documento:
            messagebox.showerror("Error", "Debe ingresar ISBN y documento.")
            return

        fecha = self.fecha_entry.get().strip()
        success, message = self.prestamo_service.crear_prestamo(isbn, documento, fecha or None)

        if success:
            messagebox.showinfo("Éxito", message)
            self.isbn_entry.delete(0, "end")
            self.documento_entry.delete(0, "end")
            self.fecha_entry.delete(0, "end")
            self._load_table("activos")
        else:
            messagebox.showerror("Error", message)

    def _devolver_libro(self):
        """Process a book return."""
        codigo = self.codigo_prestamo_entry.get().strip()

        if not codigo:
            messagebox.showerror("Error", "Debe ingresar el código del préstamo.")
            return

        success, message = self.prestamo_service.devolver(codigo)

        if success:
            messagebox.showinfo("Éxito", message)
            self.codigo_prestamo_entry.delete(0, "end")
            self._load_table(self.filtro_actual)
        else:
            messagebox.showerror("Error", message)
