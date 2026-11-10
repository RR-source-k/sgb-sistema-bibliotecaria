"""User service - Business logic for user management."""

import logging
from model.modelos import Usuario
from repositories.usuario_repo import UsuarioRepository

logger = logging.getLogger(__name__)


class UsuarioService:
    def __init__(self):
        self.repo = UsuarioRepository()

    def obtener_todos(self) -> list[Usuario]:
        return self.repo.obtener_todos()

    def obtener_por_documento(self, documento: str) -> Usuario | None:
        return self.repo.obtener_por_documento(documento)

    def registrar(self, usuario: Usuario) -> tuple[bool, str]:
        """Register a new user. Returns (success, message)."""
        if not usuario.numero_documento or not usuario.nombre or not usuario.tipo:
            return False, "Documento, nombre y tipo son requeridos."

        existente = self.obtener_por_documento(usuario.numero_documento)
        if existente is not None:
            return False, f"El usuario con documento {usuario.numero_documento} ya existe."

        if usuario.estado == "Inactivo":
            logger.info(f"Registering inactive user: {usuario.numero_documento}")

        if self.repo.guardar(usuario):
            logger.info(f"User registered: {usuario}")
            return True, "Usuario registrado exitosamente."
        return False, "Error al registrar el usuario."

    def actualizar(self, usuario: Usuario) -> tuple[bool, str]:
        """Update an existing user. Returns (success, message)."""
        existente = self.obtener_por_documento(usuario.numero_documento)
        if existente is None:
            return False, "Usuario no encontrado."

        if self.repo.actualizar(usuario):
            logger.info(f"User updated: {usuario}")
            return True, "Usuario actualizado exitosamente."
        return False, "Error al actualizar el usuario."

    def eliminar(self, documento: str) -> tuple[bool, str]:
        """Deactivate a user by setting status to 'Inactivo'. Returns (success, message)."""
        existente = self.obtener_por_documento(documento)
        if existente is None:
            return False, "Usuario no encontrado."

        existente.estado = "Inactivo"
        if self.repo.actualizar(existente):
            logger.info(f"User deactivated: {documento}")
            return True, "Usuario desactivado exitosamente."
        return False, "Error al desactivar el usuario."

    def activar(self, documento: str) -> tuple[bool, str]:
        """Activate a previously deactivated user. Returns (success, message)."""
        existente = self.obtener_por_documento(documento)
        if existente is None:
            return False, "Usuario no encontrado."

        existente.estado = "Activo"
        if self.repo.actualizar(existente):
            logger.info(f"User activated: {documento}")
            return True, "Usuario activado exitosamente."
        return False, "Error al activar el usuario."
