"""
Usuarios tab - User management interface.
"""

import customtkinter as ctk
from tkinter import messagebox
from repositories.usuario_repo import UsuarioRepository
from services.usuario_service import UsuarioService
from model.enums import TipoUsuarioEnum
from model.modelos import Usuario
from ui.tabla import dibujar_tabla, COLOR_VERDE, COLOR_ROJO


class TabUsuarios(ctk.CTkFrame):
    """Tab for user management (CRUD operations)."""

    def __init__(self, parent):
        super().__init__(parent)

        self.usuario_repo = UsuarioRepository()
        self.usuario_service = UsuarioService()

        # --- Form Frame ---
        form_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(3, weight=1)

        # Title
        form_title = ctk.CTkLabel(
            form_frame,
            text="Gestión de Usuarios",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        form_title.grid(row=0, column=0, columnspan=4, padx=15, pady=(10, 5))

        # Documento
        ctk.CTkLabel(form_frame, text="Documento:").grid(row=1, column=0, padx=15, pady=5, sticky="w")
        self.entry_doc = ctk.CTkEntry(form_frame, width=180)
        self.entry_doc.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Nombre
        ctk.CTkLabel(form_frame, text="Nombre:").grid(row=1, column=2, padx=(15, 0), pady=5, sticky="w")
        self.entry_nombre = ctk.CTkEntry(form_frame, width=250)
        self.entry_nombre.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Tipo
        ctk.CTkLabel(form_frame, text="Tipo:").grid(row=2, column=0, padx=15, pady=5, sticky="w")
        self.combo_tipo = ctk.CTkComboBox(
            form_frame,
            values=[t.value for t in TipoUsuarioEnum],
            width=180,
        )
        self.combo_tipo.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Correo
        ctk.CTkLabel(form_frame, text="Correo:").grid(row=2, column=2, padx=(15, 0), pady=5, sticky="w")
        self.entry_correo = ctk.CTkEntry(form_frame, width=250)
        self.entry_correo.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # Telefono
        ctk.CTkLabel(form_frame, text="Teléfono:").grid(row=3, column=0, padx=15, pady=5, sticky="w")
        self.entry_telefono = ctk.CTkEntry(form_frame, width=180)
        self.entry_telefono.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Estado
        ctk.CTkLabel(form_frame, text="Estado:").grid(row=3, column=2, padx=(15, 0), pady=5, sticky="w")
        self.combo_estado = ctk.CTkComboBox(
            form_frame,
            values=["Activo", "Inactivo"],
            width=100,
        )
        self.combo_estado.grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.combo_estado.set("Activo")

        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=4, padx=15, pady=10)

        self.btn_register = ctk.CTkButton(
            btn_frame, text="Registrar Usuario",
            command=self._registrar,
            fg_color="#2ecc71", hover_color="#27ae60",
            width=150,
        )
        self.btn_register.grid(row=0, column=0, padx=5)

        self.btn_update = ctk.CTkButton(
            btn_frame, text="Actualizar",
            command=self._actualizar,
            fg_color="#3498db", hover_color="#2980b9",
            width=120,
        )
        self.btn_update.grid(row=0, column=1, padx=5)

        self.btn_deactivate = ctk.CTkButton(
            btn_frame, text="Desactivar",
            command=self._desactivar,
            fg_color="#e74c3c", hover_color="#c0392b",
            width=120,
        )
        self.btn_deactivate.grid(row=0, column=2, padx=5)

        self.btn_clear = ctk.CTkButton(
            btn_frame, text="Limpiar",
            command=self._limpiar_form,
            fg_color="#95a5a6", hover_color="#7f8c8d",
            width=100,
        )
        self.btn_clear.grid(row=0, column=3, padx=5)

        # --- Table Frame ---
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        table_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        table_title = ctk.CTkLabel(
            table_frame,
            text="Lista de Usuarios",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        table_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        # Scrollable frame for table
        self.scroll_frame = ctk.CTkScrollableFrame(
            table_frame,
            width=900,
            height=350,
        )
        self.scroll_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        # Refresh on load
        self.refresh_table()

    def _limpiar_form(self):
        """Clear all form fields."""
        self.entry_doc.delete(0, "end")
        self.entry_nombre.delete(0, "end")
        self.entry_correo.delete(0, "end")
        self.entry_telefono.delete(0, "end")
        self.combo_tipo.set(TipoUsuarioEnum.ESTUDIANTE.value)
        self.combo_estado.set("Activo")

    def _cargar_form(self, usuario):
        """Load a user into the form fields."""
        self._limpiar_form()
        self.entry_doc.insert(0, usuario.numero_documento)
        self.entry_nombre.insert(0, usuario.nombre)
        self.combo_tipo.set(usuario.tipo)
        self.entry_correo.insert(0, usuario.correo)
        self.entry_telefono.insert(0, usuario.telefono)
        self.combo_estado.set(usuario.estado)

    def _registrar(self):
        """Register a new user."""
        doc = self.entry_doc.get().strip()
        nombre = self.entry_nombre.get().strip()
        tipo = self.combo_tipo.get()
        correo = self.entry_correo.get().strip()
        telefono = self.entry_telefono.get().strip()
        estado = self.combo_estado.get()

        if not doc or not nombre or not correo:
            messagebox.showwarning("Campo requerido", "Documento, Nombre y Correo son obligatorios.")
            return

        success, message = self.usuario_service.registrar(
            Usuario(doc, nombre, tipo, correo, telefono, estado)
        )

        if success:
            messagebox.showinfo("Éxito", message)
            self._limpiar_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def _actualizar(self):
        """Update an existing user."""
        doc = self.entry_doc.get().strip()
        if not doc:
            messagebox.showwarning("Campo requerido", "Ingrese el documento del usuario a actualizar.")
            return

        nombre = self.entry_nombre.get().strip()
        tipo = self.combo_tipo.get()
        correo = self.entry_correo.get().strip()
        telefono = self.entry_telefono.get().strip()
        estado = self.combo_estado.get()

        if not nombre:
            messagebox.showwarning("Campo requerido", "El nombre es obligatorio.")
            return

        success, message = self.usuario_service.actualizar(
            Usuario(doc, nombre, tipo, correo, telefono, estado)
        )

        if success:
            messagebox.showinfo("Éxito", message)
            self._limpiar_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def _desactivar(self):
        """Deactivate a user (soft delete)."""
        doc = self.entry_doc.get().strip()
        if not doc:
            messagebox.showwarning("Campo requerido", "Ingrese el documento del usuario a desactivar.")
            return

        success, message = self.usuario_service.eliminar(doc)

        if success:
            messagebox.showinfo("Éxito", message)
            self._limpiar_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def refresh_table(self):
        """Refresh the user table display."""
        usuarios = self.usuario_repo.obtener_todos()
        por_doc = {u.numero_documento: u for u in usuarios}
        filas = [
            (u.numero_documento, u.nombre, u.tipo, u.correo, u.telefono, u.estado)
            for u in usuarios
        ]
        dibujar_tabla(
            self.scroll_frame,
            ["Documento", "Nombre", "Tipo", "Correo", "Teléfono", "Estado"],
            filas, header_color="#2E86C1", col_estado=5,
            colores_estado={"Activo": COLOR_VERDE, "Inactivo": COLOR_ROJO},
            on_select=lambda fila: self._cargar_form(por_doc[fila[0]]),
            mensaje_vacio="No hay usuarios registrados.",
        )
