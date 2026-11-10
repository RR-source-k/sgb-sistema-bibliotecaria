"""Utility for file I/O operations."""

import os
import logging

logger = logging.getLogger(__name__)


class ArchivoUtil:
    """Handles reading, writing, and appending to pipe-delimited text files."""

    # Ruta absoluta a <proyecto>/data, para que funcione desde cualquier cwd
    DATA_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
    )

    def __init__(self, filename: str):
        self.filename = filename
        self.filepath = os.path.join(self.DATA_DIR, filename)
        os.makedirs(self.DATA_DIR, exist_ok=True)

    def leer_lineas(self) -> list[str]:
        if not os.path.exists(self.filepath):
            logger.info(f"File {self.filepath} does not exist yet.")
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            return lines
        except Exception as e:
            logger.error(f"Error reading {self.filename}: {e}")
            return []

    def escribir_linea(self, linea: str) -> bool:
        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(linea + "\n")
            return True
        except Exception as e:
            logger.error(f"Error writing to {self.filename}: {e}")
            return False

    def reescribir(self, lineas: list[str]) -> bool:
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                for linea in lineas:
                    f.write(linea + "\n")
            return True
        except Exception as e:
            logger.error(f"Error rewriting {self.filename}: {e}")
            return False

    @staticmethod
    def generar_codigo(prefijo: str, lineas: list[str] = None) -> str:
        if lineas is None:
            lineas = []
        max_num = 0
        for line in lineas:
            parts = line.split("|")
            if parts:
                try:
                    num_str = parts[0].replace(prefijo, "")
                    num = int(num_str)
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return f"{prefijo}{max_num + 1:04d}"
