"""Domain model classes."""

from datetime import date


class Usuario:
    def __init__(self, numero_documento: str, nombre: str, tipo: str,
                 correo: str = "", telefono: str = "", estado: str = "Activo"):
        self.numero_documento = numero_documento
        self.nombre = nombre
        self.tipo = tipo
        self.correo = correo
        self.telefono = telefono
        self.estado = estado

    def __str__(self):
        return f"{self.nombre} ({self.numero_documento}) - {self.tipo}"

    def to_line(self) -> str:
        return "|".join([self.numero_documento, self.nombre, self.tipo,
                         self.correo, self.telefono, self.estado])

    @staticmethod
    def from_line(line: str) -> "Usuario":
        parts = line.split("|")
        if len(parts) != 6:
            raise ValueError(f"Invalid user line format: {line}")
        return Usuario(parts[0], parts[1], parts[2], parts[3], parts[4], parts[5])

    def to_dict(self) -> dict:
        return {"numero_documento": self.numero_documento, "nombre": self.nombre,
                "tipo": self.tipo, "correo": self.correo, "telefono": self.telefono,
                "estado": self.estado}


class Categoria:
    def __init__(self, codigo: str, nombre: str, descripcion: str = ""):
        self.codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    def to_line(self) -> str:
        return "|".join([self.codigo, self.nombre, self.descripcion])

    @staticmethod
    def from_line(line: str) -> "Categoria":
        parts = line.split("|")
        if len(parts) != 3:
            raise ValueError(f"Invalid category line format: {line}")
        return Categoria(parts[0], parts[1], parts[2])


class Libro:
    def __init__(self, isbn: str, titulo: str, autor: str, codigo_categoria: str,
                 anio: int, total_ejemplares: int, disponibles: int):
        self.isbn = isbn
        self.titulo = titulo
        self.autor = autor
        self.codigo_categoria = codigo_categoria
        self.anio = anio
        self.total_ejemplares = total_ejemplares
        self.disponibles = disponibles

    def __str__(self):
        return f"{self.titulo} - {self.autor} (disponibles: {self.disponibles}/{self.total_ejemplares})"

    def to_line(self) -> str:
        return "|".join([self.isbn, self.titulo, self.autor, self.codigo_categoria,
                         str(self.anio), str(self.total_ejemplares), str(self.disponibles)])

    @staticmethod
    def from_line(line: str) -> "Libro":
        parts = line.split("|")
        if len(parts) != 7:
            raise ValueError(f"Invalid book line format: {line}")
        return Libro(parts[0], parts[1], parts[2], parts[3], int(parts[4]),
                     int(parts[5]), int(parts[6]))


class Prestamo:
    def __init__(self, codigo: str, isbn: str, numero_documento: str,
                 fecha_prestamo: str, fecha_limite: str, fecha_devolucion: str = "",
                 estado: str = "Activo"):
        self.codigo = codigo
        self.isbn = isbn
        self.numero_documento = numero_documento
        self.fecha_prestamo = fecha_prestamo
        self.fecha_limite = fecha_limite
        self.fecha_devolucion = fecha_devolucion
        self.estado = estado

    def __str__(self):
        return f"Prestamo {self.codigo}: {self.isbn} -> {self.numero_documento} [{self.estado}]"

    def to_line(self) -> str:
        return "|".join([self.codigo, self.isbn, self.numero_documento,
                         self.fecha_prestamo, self.fecha_limite, self.fecha_devolucion,
                         self.estado])

    @staticmethod
    def from_line(line: str) -> "Prestamo":
        parts = line.split("|")
        if len(parts) != 7:
            raise ValueError(f"Invalid loan line format: {line}")
        return Prestamo(parts[0], parts[1], parts[2], parts[3], parts[4],
                        parts[5], parts[6])


class Multa:
    def __init__(self, codigo: str, codigo_prestamo: str, dias_retraso: int,
                 valor: int, estado: str = "Pendiente"):
        self.codigo = codigo
        self.codigo_prestamo = codigo_prestamo
        self.dias_retraso = dias_retraso
        self.valor = valor
        self.estado = estado

    def __str__(self):
        return f"Multa {self.codigo}: ${self.valor} ({self.dias_retraso} dias) [{self.estado}]"

    def to_line(self) -> str:
        return "|".join([self.codigo, self.codigo_prestamo, str(self.dias_retraso),
                         str(self.valor), self.estado])

    @staticmethod
    def from_line(line: str) -> "Multa":
        parts = line.split("|")
        if len(parts) != 5:
            raise ValueError(f"Invalid fine line format: {line}")
        return Multa(parts[0], parts[1], int(parts[2]), int(parts[3]), parts[4])


class Reserva:
    def __init__(self, codigo: str, isbn: str, numero_documento: str,
                 fecha_reserva: str, estado: str = "Activa"):
        self.codigo = codigo
        self.isbn = isbn
        self.numero_documento = numero_documento
        self.fecha_reserva = fecha_reserva
        self.estado = estado

    def __str__(self):
        return f"Reserva {self.codigo}: {self.isbn} -> {self.numero_documento} [{self.estado}]"

    def to_line(self) -> str:
        return "|".join([self.codigo, self.isbn, self.numero_documento,
                         self.fecha_reserva, self.estado])

    @staticmethod
    def from_line(line: str) -> "Reserva":
        parts = line.split("|")
        if len(parts) != 5:
            raise ValueError(f"Invalid reservation line format: {line}")
        return Reserva(parts[0], parts[1], parts[2], parts[3], parts[4])
