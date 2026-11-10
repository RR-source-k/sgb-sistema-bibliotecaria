# 📚 SGB — Sistema de Gestión Bibliotecaria

Aplicación de escritorio en Python (interfaz **customtkinter**) para gestionar una biblioteca:
usuarios, libros, préstamos, reservas, multas y análisis estadístico del uso de la colección.

**Autor:** Erick Santiago Rincon Rojas · **Código:** 01251151002
**Universidad:** UDES · **Materia:** Programación de Computadores II (BUC372501B) · **Evaluación:** Parcial 3

---

## Inicio rápido

Requisitos: **Python 3.10 o superior**.

```bash
# 1. Entrar a la carpeta del proyecto (la que contiene main.py)
cd sgb-sistema-bibliotecaria

# 2. Instalar la dependencia
pip install -r requirements.txt

# 3. Ejecutar
python main.py
```

> En Linux puede hacer falta `sudo apt install python3-tk`. En Mac/Linux usa `python3` si `python` no funciona.
> Si `pip` instala en otro Python distinto al que ejecuta la app, usa `python -m pip install customtkinter`.

## Datos de ejemplo (para la demostración)

El sistema **se entrega sin datos** (solo el catálogo de categorías). Para probarlo:

1. Abre la aplicación.
2. Pulsa **«Cargar casos de ejemplo»** (botón verde, arriba).

El sistema registra los datos paso a paso —cambiando de pestaña y mostrando en la barra superior qué
registra en cada momento— y termina en el dashboard de **Análisis**. Tarda unos 10 segundos.

| Botón | Qué hace |
|---|---|
| **Cargar casos de ejemplo** | Registra 5 usuarios, 8 libros, 7 préstamos, 2 multas y 3 reservas. Si ya hay datos, pregunta antes de borrarlos y cargar desde cero. |
| **Vaciar datos** | Borra usuarios, libros, préstamos, multas y reservas (conserva las categorías). Útil para repetir la demostración. |

Los datos de ejemplo cubren los casos importantes: préstamos activos, devueltos a tiempo, devueltos con
retraso y uno **vencido** (sin multa todavía), un usuario inactivo, un libro agotado con reservas activas,
una multa pendiente y otra pagada. Las fechas son relativas a *hoy*, así que el préstamo vencido siempre lo está.

> Para cambiar la velocidad de la carga, modifica `DELAY_PASO_MS` (milisegundos) en `ui/main_window.py`.

### Guion sugerido para probar cada módulo

1. **Análisis** — revisar el dashboard recién cargado (KPIs, ranking de libros, tasa de infracción).
2. **Multas → «Generar por vencidos»** — crea la multa del préstamo vencido (`PRE0004`, 13 días = $13.000).
3. **Multas → clic en una fila → «Cobrar»** — marca la multa como pagada.
4. **Préstamos** — crear un préstamo (ISBN `9789585001234`, documento `1001234567`). Probar con `1055667788` (Carlos): se rechaza por tener una multa pendiente.
5. **Préstamos → clic en un préstamo activo → «Devolver Libro»** — actualiza el stock del libro.
6. **Reservas** — reservar `9789587654321` (agotado) para otro usuario; cancelar y activar reservas.
7. **Usuarios / Libros** — registrar, actualizar y desactivar; clic en una fila carga el formulario.

---

## Módulos (pestañas)

| Pestaña | Funcionalidad |
|---|---|
| **Usuarios** | Registrar, actualizar y desactivar (soft-delete) usuarios. |
| **Libros** | Registrar, actualizar, eliminar, buscar por título/autor y agregar ejemplares. |
| **Préstamos** | Crear préstamos, registrar devoluciones, filtrar por Activos / Vencidos / Todos. |
| **Reservas** | Crear, cancelar y activar reservas; filtrar por Activas / Todas / Usuario / ISBN. |
| **Multas** | Ver por estado o documento, cobrar, generar multas por vencidos y reporte de morosidad. |
| **Análisis** | KPIs, libros más prestados, préstamos por categoría, tasa de infracción y reporte de multas. |

## Reglas de negocio

| Regla | Detalle |
|---|---|
| Cupo de préstamos | Estudiante = 3 · Docente = 5 · Externo = 2 |
| Plazo de préstamo | Estudiante = 7 días · Docente = 15 días · Externo = 5 días |
| Multa | **$1.000 COP por día** de retraso |
| Multas pendientes | Impiden nuevos préstamos |
| Reservas | Solo de libros sin ejemplares disponibles; una reserva activa por usuario y libro |
| Usuarios | No se borran: pasan a estado `Inactivo` |

## Arquitectura

Tres capas: **Modelo → Servicios → Repositorios**, más la interfaz gráfica. Persistencia en archivos
`.txt` con campos separados por `|` (carpeta `data/`).

```
sgb-sistema-bibliotecaria/
├── main.py · requirements.txt · README.md
├── model/          enums.py, modelos.py
├── repositories/   archivo_util.py, *_repo.py
├── services/       *_service.py, datos_ejemplo.py (carga de ejemplo)
├── ui/             main_window.py, tabla.py, tabs_*.py
├── data/           archivos .txt (vacíos al entregar)
├── puml/           diagramas PlantUML (clases, secuencia, casos de uso)
└── docs/           DOCUMENTACION.md + imágenes de los diagramas
```

La documentación completa (formato de los archivos, indicadores, diagramas UML y limitaciones)
está en [`docs/DOCUMENTACION.md`](docs/DOCUMENTACION.md).
