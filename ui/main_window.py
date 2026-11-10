"""
Main application window for SGB - Sistema de Gestión Bibliotecaria.
"""

import customtkinter as ctk
from tkinter import messagebox
import logging

from ui.tabs_usuarios import TabUsuarios
from ui.tabs_libros import TabLibros
from ui.tabs_prestamos import TabPrestamos
from ui.tabs_multas import TabMultas
from ui.tabs_reservas import TabReservas
from ui.tabs_analisis import TabAnalisis
from services.datos_ejemplo import CargadorEjemplo
from ui.demo import DemoEjemplo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SGBMainWindow(ctk.CTk):
    """Main window with tabbed interface for the Library Management System."""

    def __init__(self):
        super().__init__()

        self.title("Sistema de Gestión Bibliotecaria (SGB)")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        # Configure grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top frame with title
        top_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", columnspan=1)
        top_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            top_frame,
            text="📚 Sistema de Gestión Bibliotecaria",
            font=ctk.CTkFont(size=20, weight="bold", family="Helvetica"),
            text_color="#ffffff",
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        user_label = ctk.CTkLabel(
            top_frame,
            text="Erick Santiago Rincon Rojas | Código: 01251151002",
            font=ctk.CTkFont(size=11, family="Helvetica"),
            text_color="#aaaaaa",
        )
        user_label.grid(row=0, column=3, padx=20, pady=10, sticky="e")

        self.btn_cargar = ctk.CTkButton(
            top_frame, text="Cargar casos de ejemplo", width=190,
            fg_color="#27AE60", hover_color="#1E8449",
            command=self._cargar_ejemplos,
        )
        self.btn_cargar.grid(row=0, column=1, padx=5, pady=10)

        self.btn_reiniciar = ctk.CTkButton(
            top_frame, text="Vaciar datos", width=120,
            fg_color="#C0392B", hover_color="#922B21",
            command=self._vaciar_datos,
        )
        self.btn_reiniciar.grid(row=0, column=2, padx=5, pady=10)

        self.estado_label = ctk.CTkLabel(
            top_frame, text="", text_color="#7fd1a0",
            font=ctk.CTkFont(size=12, family="Helvetica"),
        )
        self.estado_label.grid(row=1, column=0, columnspan=4, padx=20, pady=(0, 8), sticky="w")

        # Tabview
        self.tabview = ctk.CTkTabview(
            self,
            width=1160,
            height=680,
            border_width=1,
            corner_radius=10,
            fg_color="#f5f5f5",
            segmented_button_fg_color="#ffffff",
            segmented_button_selected_hover_color="#4a90d9",
            segmented_button_selected_color="#3a7bc8",
        )
        self.tabview.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

        # Create tabs
        self.tab_usuarios = self.tabview.add("Usuarios")
        self.tab_libros = self.tabview.add("Libros")
        self.tab_prestamos = self.tabview.add("Préstamos")
        self.tab_reservas = self.tabview.add("Reservas")
        self.tab_multas = self.tabview.add("Multas")
        self.tab_analisis = self.tabview.add("Análisis")

        # Configure tab grid
        for tab in [self.tab_usuarios, self.tab_libros, self.tab_prestamos,
                     self.tab_reservas, self.tab_multas, self.tab_analisis]:
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)

        # Initialize tab content
        self.tab_usuario_instance = TabUsuarios(self.tab_usuarios)
        self.tab_libro_instance = TabLibros(self.tab_libros)
        self.tab_prestamo_instance = TabPrestamos(self.tab_prestamos)
        self.tab_reserva_instance = TabReservas(self.tab_reservas)
        self.tab_multa_instance = TabMultas(self.tab_multas)
        self.tab_analisis_instance = TabAnalisis(self.tab_analisis)

        # Colocar cada tab dentro de su pestaña (sin esto las pestañas quedan vacías)
        for instancia in [self.tab_usuario_instance, self.tab_libro_instance,
                          self.tab_prestamo_instance, self.tab_reserva_instance,
                          self.tab_multa_instance, self.tab_analisis_instance]:
            instancia.grid(row=0, column=0, sticky="nsew")

        # Load initial data in all tabs
        self._reload_all_tabs()

    def _reload_all_tabs(self):
        """Reload data in all tabs."""
        try:
            self.tab_usuario_instance.refresh_table()
            self.tab_libro_instance.refresh_table()
            self.tab_prestamo_instance.refresh_table()
            self.tab_reserva_instance.refresh_table()
            self.tab_multa_instance.refresh_table()
            self.tab_analisis_instance.refresh_table()
        except Exception as e:
            logger.error(f"Error reloading tabs: {e}")

    # ------------------------------------------------------- datos de ejemplo
    def _set_botones(self, estado: str):
        self.btn_cargar.configure(state=estado)
        self.btn_reiniciar.configure(state=estado)

    def _vaciar_datos(self):
        """Borra usuarios, libros, préstamos, multas y reservas."""
        if not messagebox.askyesno(
            "Vaciar datos",
            "Se borrarán usuarios, libros, préstamos, multas y reservas.\n¿Continuar?",
        ):
            return
        CargadorEjemplo().limpiar()
        self.tab_libro_instance._load_categories()
        self._reload_all_tabs()
        self.estado_label.configure(text="Datos vaciados.", text_color="#7fd1a0")

    def _cargar_ejemplos(self):
        """Llena el sistema paso a paso escribiendo en los formularios (ui/demo.py)."""
        cargador = CargadorEjemplo()
        if cargador.hay_datos():
            if not messagebox.askyesno(
                "Cargar casos de ejemplo",
                "Ya hay datos registrados.\n"
                "¿Borrarlos y cargar los casos de ejemplo desde cero?",
            ):
                return
            cargador.limpiar()
            self._reload_all_tabs()
        DemoEjemplo(self).iniciar()
