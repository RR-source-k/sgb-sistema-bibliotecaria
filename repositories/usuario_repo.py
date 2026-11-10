"""User repository - CRUD for users."""

import logging
from model.modelos import Usuario
from .archivo_util import ArchivoUtil

logger = logging.getLogger(__name__)
FILE = "usuarios.txt"


class UsuarioRepository:
    def __init__(self):
        self.archivo = ArchivoUtil(FILE)

    def obtener_todos(self) -> list[Usuario]:
        lines = self.archivo.leer_lineas()
        usuarios = []
        for line in lines:
            try:
                usuarios.append(Usuario.from_line(line))
            except ValueError as e:
                logger.warning(f"Skipping invalid user line: {e}")
        return usuarios

    def obtener_por_documento(self, documento: str) -> Usuario | None:
        for user in self.obtener_todos():
            if user.numero_documento == documento:
                return user
        return None

    def guardar(self, usuario: Usuario) -> bool:
        if self.obtener_por_documento(usuario.numero_documento) is not None:
            logger.warning(f"User {usuario.numero_documento} already exists.")
            return False
        return self.archivo.escribir_linea(usuario.to_line())

    def actualizar(self, usuario: Usuario) -> bool:
        existing = self.obtener_por_documento(usuario.numero_documento)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = []
        for line in lines:
            try:
                u = Usuario.from_line(line)
                if u.numero_documento == usuario.numero_documento:
                    new_lines.append(usuario.to_line())
                else:
                    new_lines.append(line)
            except ValueError:
                new_lines.append(line)
        return self.archivo.reescribir(new_lines)

    def eliminar(self, documento: str) -> bool:
        existing = self.obtener_por_documento(documento)
        if existing is None:
            return False
        lines = self.archivo.leer_lineas()
        new_lines = [l for l in lines if l and not l.startswith(documento + "|")]
        return self.archivo.reescribir(new_lines)
