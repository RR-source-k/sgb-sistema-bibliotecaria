"""
Libros tab - Book management interface.
"""

import customtkinter as ctk
from tkinter import messagebox
from services.libro_service import LibroService
from model.modelos import Libro
from ui.tabla import dibujar_tabla


class TabLibros(ctk.CTkFrame):
    """Tab for book management (CRUD operations)."""

    def __init__(self, parent):
        super().__init__(parent)

        self.libro_service = LibroService()

        # --- Form Frame ---
        form_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        form_frame.grid_columnconfigure(3, weight=1)

        form_title = ctk.CTkLabel(
            form_frame,
            text="Gestión de Libros",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        form_title.grid(row=0, column=0, columnspan=4, padx=15, pady=(10, 5))

        # ISBN
        ctk.CTkLabel(form_frame, text="ISBN:").grid(
            row=1, column=0, padx=15, pady=5, sticky="w"
        )
        self.entry_isbn = ctk.CTkEntry(form_frame, width=180)
        self.entry_isbn.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Título
        ctk.CTkLabel(form_frame, text="Título:").grid(
            row=1, column=2, padx=(15, 0), pady=5, sticky="w"
        )
        self.entry_titulo = ctk.CTkEntry(form_frame, width=250)
        self.entry_titulo.grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Autor
        ctk.CTkLabel(form_frame, text="Autor:").grid(
            row=2, column=0, padx=15, pady=5, sticky="w"
        )
        self.entry_autor = ctk.CTkEntry(form_frame, width=180)
        self.entry_autor.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Categoría
        ctk.CTkLabel(form_frame, text="Categoría:").grid(
            row=2, column=2, padx=(15, 0), pady=5, sticky="w"
        )
        self.combo_categoria = ctk.CTkComboBox(
            form_frame, values=[], width=120
        )
        self.combo_categoria.grid(row=2, column=3, padx=5, pady=5, sticky="w")

        # Año
        ctk.CTkLabel(form_frame, text="Año:").grid(
            row=3, column=0, padx=15, pady=5, sticky="w"
        )
        self.entry_anio = ctk.CTkEntry(form_frame, width=180)
        self.entry_anio.grid(row=3, column=1, padx=5, pady=5, sticky="w")

        # Ejemplares
        ctk.CTkLabel(form_frame, text="Ejemplares:").grid(
            row=3, column=2, padx=(15, 0), pady=5, sticky="w"
        )
        self.entry_ejemplares = ctk.CTkEntry(form_frame, width=120)
        self.entry_ejemplares.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # Buttons
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=4, padx=15, pady=10)

        self.btn_register = ctk.CTkButton(
            btn_frame,
            text="Registrar Libro",
            command=self._registrar,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            width=140,
        )
        self.btn_register.grid(row=0, column=0, padx=5)

        self.btn_update = ctk.CTkButton(
            btn_frame,
            text="Actualizar",
            command=self._actualizar,
            fg_color="#3498db",
            hover_color="#2980b9",
            width=120,
        )
        self.btn_update.grid(row=0, column=1, padx=5)

        self.btn_delete = ctk.CTkButton(
            btn_frame,
            text="Eliminar",
            command=self._eliminar,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            width=100,
        )
        self.btn_delete.grid(row=0, column=2, padx=5)

        self.btn_add_copies = ctk.CTkButton(
            btn_frame,
            text="Agregar Ejemplares",
            command=self._agregar_ejemplares,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            width=150,
        )
        self.btn_add_copies.grid(row=0, column=3, padx=5)

        # --- Search Frame ---
        search_frame = ctk.CTkFrame(self, fg_color="#f0f0f0", corner_radius=10)
        search_frame.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
        search_frame.grid_columnconfigure(2, weight=1)

        self.entry_search = ctk.CTkEntry(
            search_frame,
            width=250,
            placeholder_text="Buscar por título o autor...",
        )
        self.entry_search.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.btn_search = ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self._buscar,
            fg_color="#34495e",
            hover_color="#2c3e50",
            width=90,
        )
        self.btn_search.grid(row=0, column=1, padx=5, pady=8)

        self.btn_show_all = ctk.CTkButton(
            search_frame,
            text="Mostrar Todos",
            command=self.refresh_table,
            fg_color="#7f8c8d",
            hover_color="#95a5a6",
            width=120,
        )
        self.btn_show_all.grid(row=0, column=2, padx=5, pady=8)

        # --- Table Frame ---
        table_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=10)
        table_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="nsew")
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        table_title = ctk.CTkLabel(
            table_frame,
            text="Lista de Libros",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        table_title.grid(row=0, column=0, padx=15, pady=(10, 5), sticky="w")

        self.scroll_frame = ctk.CTkScrollableFrame(
            table_frame, width=900, height=250
        )
        self.scroll_frame.grid(row=1, column=0, padx=15, pady=5, sticky="nsew")

        # Refresh on load
        self._load_categories()
        self.refresh_table()

    # ------------------------------------------------------------------ #
    #  Helpers
    # ------------------------------------------------------------------ #

    def _load_categories(self):
        """Load categories into the combo box."""
        categorias = self.libro_service.obtener_categorias_disponibles()
        nombres = [name for _, name in categorias] if categorias else []
        self.combo_categoria.configure(values=nombres)
        if nombres and self.combo_categoria.get() not in nombres:
            self.combo_categoria.set(nombres[0])  # el valor por defecto de ctk no es una categoría

    def _limpiar_form(self):
        """Clear all form fields."""
        self.entry_isbn.delete(0, "end")
        self.entry_titulo.delete(0, "end")
        self.entry_autor.delete(0, "end")
        self.entry_anio.delete(0, "end")
        self.entry_ejemplares.delete(0, "end")
        if self.combo_categoria.cget("values"):
            self.combo_categoria.set(self.combo_categoria.cget("values")[0])

    def _cargar_form(self, libro: Libro):
        """Load a book into the form fields."""
        self._limpiar_form()
        self.entry_isbn.insert(0, libro.isbn)
        self.entry_titulo.insert(0, libro.titulo)
        self.entry_autor.insert(0, libro.autor)
        self.entry_anio.insert(0, str(libro.anio))
        self.entry_ejemplares.insert(0, str(libro.total_ejemplares))

        categorias = self.libro_service.obtener_categorias_disponibles()
        for code, name in categorias:
            if code == libro.codigo_categoria:
                self.combo_categoria.set(name)
                break

    def _resolve_categoria_code(self) -> str:
        """Resolve selected category name to its code."""
        nombre = self.combo_categoria.get()
        categorias = self.libro_service.obtener_categorias_disponibles()
        for code, name in categorias:
            if name == nombre:
                return code
        return ""

    def _parse_int(self, entry: ctk.CTkEntry, default: int = 0) -> int:
        """Safely parse an integer from an entry widget."""
        text = entry.get().strip()
        if not text:
            return default
        try:
            return int(text)
        except ValueError:
            return default

    # ------------------------------------------------------------------ #
    #  Actions
    # ------------------------------------------------------------------ #

    def _registrar(self):
        """Register a new book."""
        isbn = self.entry_isbn.get().strip()
        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()

        if not isbn or not titulo or not autor:
            messagebox.showwarning(
                "Campo requerido",
                "ISBN, título y autor son obligatorios.",
            )
            return

        anio = self._parse_int(self.entry_anio, 2000)
        ejemplares = self._parse_int(self.entry_ejemplares, 1)
        cod_categoria = self._resolve_categoria_code()
        if not cod_categoria:
            messagebox.showwarning("Campo requerido", "Seleccione una categoría.")
            return

        libro = Libro(isbn, titulo, autor, cod_categoria, anio, ejemplares, ejemplares)
        success, message = self.libro_service.registrar(libro)

        if success:
            messagebox.showinfo("Éxito", message)
            self._limpiar_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def _actualizar(self):
        """Update an existing book."""
        isbn = self.entry_isbn.get().strip()
        if not isbn:
            messagebox.showwarning(
                "Campo requerido", "Ingrese el ISBN del libro a actualizar."
            )
            return

        titulo = self.entry_titulo.get().strip()
        autor = self.entry_autor.get().strip()

        if not titulo or not autor:
            messagebox.showwarning(
                "Campo requerido", "Título y autor son obligatorios."
            )
            return

        anio = self._parse_int(self.entry_anio, 2000)
        ejemplares = self._parse_int(self.entry_ejemplares, 1)
        cod_categoria = self._resolve_categoria_code()

        libro_existente = self.libro_service.obtener_por_isbn(isbn)
        if libro_existente is None:
            messagebox.showerror("Error", f"No se encontró un libro con ISBN {isbn}.")
            return

        # Update the existing object
        libro_existente.titulo = titulo
        libro_existente.autor = autor
        libro_existente.codigo_categoria = cod_categoria
        libro_existente.anio = anio
        # Conservar los ejemplares prestados: la diferencia de total se refleja en disponibles
        prestados = libro_existente.total_ejemplares - libro_existente.disponibles
        if ejemplares < prestados:
            messagebox.showerror(
                "Error",
                f"Hay {prestados} ejemplares prestados; el total no puede ser menor.",
            )
            return
        libro_existente.total_ejemplares = ejemplares
        libro_existente.disponibles = ejemplares - prestados

        success, message = self.libro_service.actualizar(libro_existente)
        if success:
            messagebox.showinfo("Éxito", message)
            self._limpiar_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def _eliminar(self):
        """Delete a book by ISBN."""
        isbn = self.entry_isbn.get().strip()
        if not isbn:
            messagebox.showwarning(
                "Campo requerido", "Ingrese el ISBN del libro a eliminar."
            )
            return

        success, message = self.libro_service.eliminar(isbn)
        if success:
            messagebox.showinfo("Éxito", message)
            self._limpiar_form()
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def _agregar_ejemplares(self):
        """Add copies to an existing book."""
        isbn = self.entry_isbn.get().strip()
        if not isbn:
            messagebox.showwarning(
                "Campo requerido", "Ingrese el ISBN del libro."
            )
            return

        cantidad = self._parse_int(self.entry_ejemplares, 1)
        if cantidad <= 0:
            messagebox.showwarning(
                "Valor inválido", "La cantidad de ejemplares debe ser positiva."
            )
            return

        success, message = self.libro_service.incrementar_ejemplares(isbn, cantidad)
        if success:
            messagebox.showinfo("Éxito", message)
            self.entry_ejemplares.delete(0, "end")
            self.refresh_table()
        else:
            messagebox.showerror("Error", message)

    def _buscar(self):
        """Search books by title or author."""
        termino = self.entry_search.get().strip()
        if not termino:
            messagebox.showinfo(
                "Búsqueda", "Ingrese un término de búsqueda."
            )
            return

        libros = self.libro_service.buscar(termino)
        self._render_table(libros)

    # ------------------------------------------------------------------ #
    #  Table rendering
    # ------------------------------------------------------------------ #

    def refresh_table(self):
        """Reload and display all books."""
        libros = self.libro_service.obtener_todos()
        self._render_table(libros)

    def _render_table(self, libros: list[Libro]):
        """Dibuja la tabla de libros (clic en una fila carga el formulario)."""
        nombres = dict(self.libro_service.obtener_categorias_disponibles())
        filas = [
            (l.isbn, l.titulo, l.autor, nombres.get(l.codigo_categoria, l.codigo_categoria),
             l.anio, l.total_ejemplares, l.disponibles)
            for l in libros
        ]
        por_isbn = {l.isbn: l for l in libros}
        dibujar_tabla(
            self.scroll_frame,
            ["ISBN", "Título", "Autor", "Categoría", "Año", "Total", "Disponibles"],
            filas, header_color="#2E86C1",
            on_select=lambda fila: self._cargar_form(por_isbn[fila[0]]),
            mensaje_vacio="No se encontraron libros.",
        )
