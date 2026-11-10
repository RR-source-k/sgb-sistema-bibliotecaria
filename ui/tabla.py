"""Helper compartido para dibujar tablas con CTkLabel dentro de un frame."""

import customtkinter as ctk

COLOR_VERDE = "#27AE60"
COLOR_ROJO = "#E74C3C"
COLOR_GRIS = "#7F8C8D"
COLOR_TEXTO = "#222222"


def limpiar(frame) -> None:
    """Elimina todos los widgets hijos del frame."""
    for widget in frame.winfo_children():
        widget.destroy()


def dibujar_tabla(frame, columnas, filas, header_color="#2E86C1",
                  col_estado=None, colores_estado=None, on_select=None,
                  mensaje_vacio="No hay registros para mostrar."):
    """
    Dibuja una tabla dentro de `frame` (limpiándolo antes).

    columnas       -- lista de títulos
    filas          -- lista de tuplas/listas de valores (se convierten a str)
    col_estado     -- índice de la columna cuyo texto se colorea según su valor
    colores_estado -- dict {valor: color}
    on_select      -- callback(fila) al hacer clic en una fila
    """
    limpiar(frame)
    colores_estado = colores_estado or {}

    for i in range(len(columnas)):
        frame.grid_columnconfigure(i, weight=1)

    for c, titulo in enumerate(columnas):
        ctk.CTkLabel(
            frame, text=titulo, text_color="white", fg_color=header_color,
            font=ctk.CTkFont(weight="bold"), corner_radius=0,
        ).grid(row=0, column=c, sticky="nsew", padx=1, pady=(0, 2), ipady=4)

    if not filas:
        ctk.CTkLabel(frame, text=mensaje_vacio, text_color=COLOR_GRIS).grid(
            row=1, column=0, columnspan=len(columnas), pady=20)
        return

    for r, fila in enumerate(filas, start=1):
        fondo = "#f8f9fa" if r % 2 else "#eceff1"
        for c, valor in enumerate(fila):
            color = COLOR_TEXTO
            fuente = ctk.CTkFont()
            if col_estado is not None and c == col_estado:
                color = colores_estado.get(str(valor), COLOR_TEXTO)
                fuente = ctk.CTkFont(weight="bold")
            lbl = ctk.CTkLabel(frame, text=str(valor), text_color=color,
                               fg_color=fondo, font=fuente, corner_radius=0)
            lbl.grid(row=r, column=c, sticky="nsew", padx=1, pady=1, ipady=3)
            if on_select is not None:
                lbl.bind("<Button-1>", lambda _e, f=fila: on_select(f))
                lbl.configure(cursor="hand2")
