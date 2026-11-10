"""Diálogo para registrar una categoría nueva de libros."""

import customtkinter as ctk
from tkinter import messagebox


class DialogoCategoria(ctk.CTkToplevel):
    """
    Ventana emergente con código, nombre y descripción.

    guardar(codigo, nombre, descripcion) -> (bool, str)  : acción de registro
    al_guardar(nombre)                                   : se llama si se registró
    """

    def __init__(self, parent, guardar, al_guardar):
        super().__init__(parent)
        self._guardar = guardar
        self._al_guardar = al_guardar

        self.title("Nueva categoría")
        ancho, alto = 420, 290
        raiz = parent.winfo_toplevel()
        raiz.update_idletasks()
        x = raiz.winfo_rootx() + max((raiz.winfo_width() - ancho) // 2, 0)
        y = raiz.winfo_rooty() + max((raiz.winfo_height() - alto) // 3, 0)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.configure(fg_color="#ffffff")

        ctk.CTkLabel(
            self, text="Nueva categoría", text_color="#222222",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(18, 10), sticky="w")

        ctk.CTkLabel(self, text="Código:", text_color="#222222").grid(
            row=1, column=0, padx=(20, 5), pady=6, sticky="w")
        self.entry_codigo = ctk.CTkEntry(self, width=120, placeholder_text="Ej. ART")
        self.entry_codigo.grid(row=1, column=1, padx=5, pady=6, sticky="w")

        ctk.CTkLabel(self, text="Nombre:", text_color="#222222").grid(
            row=2, column=0, padx=(20, 5), pady=6, sticky="w")
        self.entry_nombre = ctk.CTkEntry(self, width=260, placeholder_text="Ej. Arte")
        self.entry_nombre.grid(row=2, column=1, padx=5, pady=6, sticky="w")

        ctk.CTkLabel(self, text="Descripción:", text_color="#222222").grid(
            row=3, column=0, padx=(20, 5), pady=6, sticky="w")
        self.entry_descripcion = ctk.CTkEntry(self, width=260, placeholder_text="(opcional)")
        self.entry_descripcion.grid(row=3, column=1, padx=5, pady=6, sticky="w")

        botones = ctk.CTkFrame(self, fg_color="transparent")
        botones.grid(row=4, column=0, columnspan=2, pady=20)
        ctk.CTkButton(botones, text="Guardar", width=110,
                      fg_color="#2ecc71", hover_color="#27ae60",
                      command=self._on_guardar).grid(row=0, column=0, padx=8)
        ctk.CTkButton(botones, text="Cancelar", width=110,
                      fg_color="#95a5a6", hover_color="#7f8c8d",
                      command=self.destroy).grid(row=0, column=1, padx=8)

        self.after(100, self._enfocar)

    def _enfocar(self):
        try:
            self.grab_set()
            self.entry_codigo.focus_set()
        except Exception:
            pass

    def _on_guardar(self):
        ok, mensaje = self._guardar(
            self.entry_codigo.get(), self.entry_nombre.get(), self.entry_descripcion.get())
        if ok:
            nombre = self.entry_nombre.get().strip()
            messagebox.showinfo("Éxito", mensaje, parent=self)
            self._al_guardar(nombre)
            self.destroy()
        else:
            messagebox.showerror("Error", mensaje, parent=self)
