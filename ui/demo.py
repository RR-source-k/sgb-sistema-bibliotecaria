"""
Demostración paso a paso: escribe en los formularios y pulsa los botones reales.

Todo se hace como lo haría una persona desde la interfaz: se escribe en los campos
(incluida la fecha del préstamo, para simular que ya pasaron días) y se pulsan los
botones reales, de modo que se aplican las validaciones, el stock y las multas del sistema.

Ajusta VELOCIDAD para hacerla más rápida (0.5 = el doble de rápido) o más lenta.
"""

import logging
from datetime import date, timedelta
from tkinter import messagebox

from repositories.prestamo_repo import PrestamoRepository
from services.reserva_service import ReservaService
from services.datos_ejemplo import (
    CargadorEjemplo, USUARIOS, LIBROS, CATEGORIAS,
)

logger = logging.getLogger(__name__)

# ----------------------------------------------------------- velocidad (ms)
VELOCIDAD = 0.5          # multiplicador global de pausas (1.0 = lento, 0.3 = rápido)
MS_POR_LETRA = 22        # tiempo entre letras al "escribir"
MS_ENTRE_CAMPOS = 140    # pausa al pasar de un campo al siguiente
MS_ANTES_BOTON = 450     # pausa antes de pulsar el botón
MS_DESPUES_BOTON = 600   # pausa para ver el resultado

# (isbn, documento, días desde el préstamo, acción final)
#   días = None => préstamo de hoy (no se escribe fecha)
#   La fecha límite la calcula el sistema según el tipo de usuario.
PRESTAMOS = [
    ("9789585001234", "1098765432", 6, "devolver"),     # a tiempo
    ("9789587654321", "1001234567", 13, "devolver"),    # a tiempo
    ("9789585001234", "1055667788", 10, "devolver"),    # 5 días tarde -> multa pendiente
    ("9780553380163", "1020304050", 10, "pagar"),       # 3 días tarde -> multa que se cobra
    ("9789587654321", "1098765432", 20, "dejar"),       # activo y VENCIDO
    ("9789587654321", "1020304050", None, "dejar"),     # activo
    ("9780132350884", "1001234567", None, "dejar"),     # activo
]


def _fecha_atras(dias: int) -> str:
    return (date.today() - timedelta(days=dias)).strftime("%Y-%m-%d")


class DemoEjemplo:
    """Ejecuta la demostración sobre la ventana principal."""

    def __init__(self, ventana):
        self.v = ventana
        self.prestamo_repo = PrestamoRepository()
        self.reserva_service = ReservaService()
        self._originales = {}
        self._gen = None

    # ------------------------------------------------------------- ejecución
    def iniciar(self):
        CargadorEjemplo().asegurar_categorias()
        self.v.tab_libro_instance._load_categories()
        self._silenciar_dialogos()
        self.v._set_botones("disabled")
        self._gen = self._guion()
        self._tick()

    def _tick(self):
        try:
            ms = next(self._gen)
        except StopIteration:
            self._terminar("✔ Casos de ejemplo cargados.")
            return
        except Exception as e:  # noqa: BLE001
            logger.exception("Error en la demostración")
            self._terminar(f"Error en la demostración: {e}")
            return
        try:
            self.v.after(max(1, int(ms * VELOCIDAD)), self._tick)
        except Exception:  # ventana cerrada a mitad
            self._restaurar_dialogos()

    def _terminar(self, texto):
        self._restaurar_dialogos()
        try:
            self.v._reload_all_tabs()
            self.v.tabview.set("Análisis")
            self.v.estado_label.configure(text=texto, text_color="#7fd1a0")
            self.v._set_botones("normal")
        except Exception:
            pass

    # -------------------------------------------------- diálogos silenciosos
    def _silenciar_dialogos(self):
        """Evita que los messagebox detengan la demostración."""
        for nombre in ("showinfo", "showwarning", "showerror", "askyesno"):
            self._originales[nombre] = getattr(messagebox, nombre)
        messagebox.showinfo = lambda t, m, **k: self._aviso(m, False)
        messagebox.showwarning = lambda t, m, **k: self._aviso(m, True)
        messagebox.showerror = lambda t, m, **k: self._aviso(m, True)
        messagebox.askyesno = lambda *a, **k: True

    def _restaurar_dialogos(self):
        for nombre, funcion in self._originales.items():
            setattr(messagebox, nombre, funcion)
        self._originales.clear()

    def _aviso(self, mensaje, es_error):
        color = "#ff9d8f" if es_error else "#7fd1a0"
        self.v.estado_label.configure(text=("⚠ " if es_error else "✔ ") + mensaje,
                                      text_color=color)

    # ---------------------------------------------------------- primitivas
    def _estado(self, texto):
        self.v.estado_label.configure(text=texto, text_color="#7fd1a0")

    def _pestana(self, nombre):
        if self.v.tabview.get() != nombre:
            self.v.tabview.set(nombre)
        yield 350

    def _escribir(self, entry, texto):
        """Escribe `texto` letra por letra en el campo."""
        entry.focus_set()
        for letra in str(texto):
            entry.insert("end", letra)
            yield MS_POR_LETRA
        yield MS_ENTRE_CAMPOS

    def _elegir(self, combo, valor):
        """Selecciona un valor en un combo."""
        yield 200
        combo.set(valor)
        yield MS_ENTRE_CAMPOS + 100

    def _pulsar(self, accion):
        """Pausa, ejecuta el botón y deja ver el resultado."""
        yield MS_ANTES_BOTON
        accion()
        yield MS_DESPUES_BOTON

    # --------------------------------------------------------------- guion
    def _guion(self):
        yield from self._usuarios()
        yield from self._libros()
        yield from self._prestamos()
        yield from self._reservas()

    def _usuarios(self):
        tab = self.v.tab_usuario_instance
        yield from self._pestana("Usuarios")
        for doc, nombre, tipo, correo, tel, estado in USUARIOS:
            self._estado(f"Registrando usuario: {nombre} ({tipo})")
            yield from self._escribir(tab.entry_doc, doc)
            yield from self._escribir(tab.entry_nombre, nombre)
            yield from self._elegir(tab.combo_tipo, tipo)
            yield from self._escribir(tab.entry_correo, correo)
            yield from self._escribir(tab.entry_telefono, tel)
            yield from self._elegir(tab.combo_estado, estado)
            yield from self._pulsar(tab._registrar)

    def _libros(self):
        tab = self.v.tab_libro_instance
        nombres = {cod: nom for cod, nom, _ in CATEGORIAS}
        yield from self._pestana("Libros")
        for isbn, titulo, autor, cat, anio, ejemplares in LIBROS:
            self._estado(f"Registrando libro: {titulo}")
            yield from self._escribir(tab.entry_isbn, isbn)
            yield from self._escribir(tab.entry_titulo, titulo)
            yield from self._escribir(tab.entry_autor, autor)
            yield from self._elegir(tab.combo_categoria, nombres[cat])
            yield from self._escribir(tab.entry_anio, anio)
            yield from self._escribir(tab.entry_ejemplares, ejemplares)
            yield from self._pulsar(tab._registrar)

    def _prestamos(self):
        tab = self.v.tab_prestamo_instance
        multas = self.v.tab_multa_instance
        nombre_de = {u[0]: u[1] for u in USUARIOS}

        for isbn, doc, atras, final in PRESTAMOS:
            yield from self._pestana("Préstamos")
            self._estado(f"Registrando préstamo a {nombre_de[doc]}")
            yield from self._escribir(tab.isbn_entry, isbn)
            yield from self._escribir(tab.documento_entry, doc)
            if atras is not None:
                yield from self._escribir(tab.fecha_entry, _fecha_atras(atras))
            yield from self._pulsar(tab._crear_prestamo)

            existentes = self.prestamo_repo.obtener_por_usuario(doc)
            prestamo = next((p for p in reversed(existentes) if p.isbn == isbn
                             and p.estado == "Activo"), None)
            if prestamo is None:       # el sistema lo rechazó; seguir con el siguiente
                continue

            if final in ("devolver", "pagar"):
                self._estado(f"Registrando devolución del préstamo {prestamo.codigo}")
                yield from self._escribir(tab.codigo_prestamo_entry, prestamo.codigo)
                yield from self._pulsar(tab._devolver_libro)

            if final == "pagar":       # cobrar la multa que generó la devolución
                yield from self._pestana("Multas")
                multa = next((m for m in multas.service.obtener_pendientes()
                              if m.codigo_prestamo == prestamo.codigo), None)
                if multa is not None:
                    self._estado(f"Cobrando la multa {multa.codigo} ({nombre_de[doc]})")
                    multas.refresh_table()
                    yield from self._escribir(multas.codigo_entry, multa.codigo)
                    yield from self._pulsar(multas._pagar)

    def _reservas(self):
        tab = self.v.tab_reserva_instance
        isbn = LIBROS[1][0]                      # el libro agotado
        nombre_de = {u[0]: u[1] for u in USUARIOS}
        yield from self._pestana("Reservas")

        def reservar(doc):
            self._estado(f"Creando reserva: {nombre_de[doc]}")
            yield from self._escribir(tab.isbn_entry, isbn)
            yield from self._escribir(tab.documento_entry, doc)
            yield from self._pulsar(tab._crear_reserva)

        yield from reservar("1055667788")
        ultima = self.reserva_service.obtener_por_usuario("1055667788")
        if ultima:
            self._estado(f"Cancelando la reserva {ultima[-1].codigo}")
            yield from self._escribir(tab.codigo_entry, ultima[-1].codigo)
            yield from self._pulsar(tab._cancelar_reserva)
        yield from reservar("1055667788")
        yield from reservar("1001234567")
