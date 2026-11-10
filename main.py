"""
Sistema de Gestión Bibliotecaria (SGB)
Main entry point.
Author: Erick Santiago Rincon Rojas
Code: 01251151002
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from ui.main_window import SGBMainWindow

if __name__ == "__main__":
    ctk.set_appearance_mode("Light")  # la UI usa colores claros fijos
    ctk.set_default_color_theme("blue")

    app = SGBMainWindow()
    app.mainloop()
