"""Enums for the library management system."""

from enum import Enum


class CategoriaEnum(Enum):
    LITERATURA = "LIT"
    TECNOLOGIA = "TEC"
    CIENCIAS = "CIA"
    MATEMATICA = "MAT"
    HISTORIA = "HIS"
    DERECHO = "DER"
    MEDICINA = "MED"
    OTROS = "OTH"


class TipoUsuarioEnum(Enum):
    ESTUDIANTE = "Estudiante"
    DOCENTE = "Docente"
    EXTERNO = "Externo"

    @property
    def limite_prestamos(self) -> int:
        limits = {"Estudiante": 3, "Docente": 5, "Externo": 2}
        return limits[self.value]

    @property
    def dias_prestamo(self) -> int:
        periods = {"Estudiante": 7, "Docente": 15, "Externo": 5}
        return periods[self.value]


class EstadoPrestamoEnum(Enum):
    ACTIVO = "Activo"
    DEVUELTO = "Devuelto"
    VENCIDO = "Vencido"


class EstadoMultaEnum(Enum):
    PENDIENTE = "Pendiente"
    PAGADA = "Pagada"


class EstadoReservaEnum(Enum):
    ACTIVA = "Activa"
    CANCELADA = "Cancelada"
    ENTREGADA = "Entregada"
