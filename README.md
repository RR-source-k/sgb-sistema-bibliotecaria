# Sistema de Gestión Bibliotecaria (SGB)

Trabajo final de semestre de **Programación Orientada a Objetos — Ingeniería de Software**.

> **Estado del documento:** borrador sugerido. La estructura, los nombres de módulos y las decisiones de diseño aquí descritas pueden cambiar a medida que avance el desarrollo. Se actualizará en cada prototipo.

## Autor

| Campo | Dato |
|---|---|
| Nombre | Erick Santiago Rincón Rojas |
| Código | 01251151002 |
| Universidad | Universidad de Santander (UDES) |
| Programa | Ingeniería en Ciencias de la Computación e Inteligencia Artificial |
| Asignatura | Programación Orientada a Objetos — Ingeniería de Software |

## Descripción

El SGB es un sistema en Python que apoya la gestión de una biblioteca pública o universitaria, en el marco del programa de modernización de bibliotecas del Ministerio de Cultura de Colombia. Reemplaza las fichas de papel y las hojas de cálculo dispersas por una herramienta que centraliza el ciclo completo de servicio:

1. Registro de usuarios (estudiante, docente o externo).
2. Catalogación de libros y categorías.
3. Préstamo y devolución de libros.
4. Cálculo y pago de multas por retraso.
5. Reservas de libros sin ejemplares disponibles, atendidas por orden de llegada.
6. Consulta del historial de préstamos de cada usuario.
7. Indicadores estadísticos de uso de la colección.

## Restricciones técnicas

| ID | Categoría | Descripción |
|---|---|---|
| RNF-01 | Arquitectura | 3 capas: Modelo (dominio), Servicios (lógica) y Repositorios (persistencia) |
| RNF-02 | Persistencia | Archivos `.txt` con campos delimitados por `\|` (pipe) |
| RNF-03 | Interfaz | Menús con `print()` e `input()` |
| RNF-04 | Lenguaje | Python 3.10 o superior, solo librería estándar |
| RNF-05 | Entorno | Google Colab + Google Drive como entorno de entrega |
| RNF-06 | Legibilidad | Docstrings en todas las clases y métodos públicos |

## Arquitectura

```
Interfaz (menús)  ->  Servicios (reglas de negocio)  ->  Repositorios (archivos .txt)
                              |                                   |
                              +---------->  Modelo (entidades y enums)  <---------+
```

- **Modelo:** entidades `Usuario`, `Categoria`, `Libro`, `Prestamo`, `Multa`, `Reserva` y enums de estado. Cada entidad se serializa con `to_linea()` y `from_linea()`.
- **Repositorios:** `ArchivoUtil` y un repositorio por entidad. Son la única capa que toca los archivos.
- **Servicios:** aplican validaciones y reglas de negocio usando los repositorios.
- **Interfaz:** menús de consola que invocan a los servicios.

## Estructura del repositorio (sugerida)

```
sgb-sistema-bibliotecaria/
├── README.md
├── main.py                      # punto de entrada local
├── sgb/
│   ├── config.py                # rutas de datos (Drive en Colab, ./datos en local)
│   ├── modelo/
│   │   ├── enums.py
│   │   ├── usuario.py
│   │   ├── categoria.py
│   │   ├── libro.py
│   │   ├── prestamo.py
│   │   ├── multa.py
│   │   └── reserva.py
│   ├── repositorios/
│   │   ├── archivo_util.py
│   │   ├── usuario_repository.py
│   │   ├── categoria_repository.py
│   │   ├── libro_repository.py
│   │   ├── prestamo_repository.py
│   │   ├── multa_repository.py
│   │   └── reserva_repository.py
│   ├── servicios/
│   │   ├── usuario_service.py
│   │   ├── libro_service.py
│   │   ├── prestamo_service.py
│   │   ├── multa_service.py
│   │   ├── reserva_service.py
│   │   └── analisis_datos_service.py
│   └── ui/
│       ├── utilidades.py        # leer_texto, leer_entero, leer_fecha, limpiar_pantalla
│       └── menus.py             # menu_principal y submenús
├── datos/                       # archivos .txt de prueba
├── docs/
│   └── diagramas/               # archivos .puml (dominio y clases por capa)
├── notebooks/
│   └── SGB.ipynb                # entregable para Colab (celdas 0 a 5.1)
└── tests/                       # pruebas con unittest
```

El notebook `SGB.ipynb` sigue la numeración de celdas definida en la guía del curso:

| Sección | Contenido |
|---|---|
| Celda 0 | Montaje de Drive y definición de rutas |
| Sección 1 | Modelo: enums y clases (celdas 1.1 a 1.7) |
| Sección 2 | Repositorios: `ArchivoUtil` y seis repositorios (celdas 2.1 a 2.7) |
| Sección 3 | Servicios: seis servicios (celdas 3.1 a 3.6) |
| Sección 4 | Interfaz: funciones auxiliares y menús (celdas 4.0 a 4.6) |
| Sección 5 | Ejecución: `menu_principal()` (celda 5.1) |

## Modelo de dominio

| Entidad | Atributos principales | Relaciones |
|---|---|---|
| Usuario | num_documento, nombre, tipo, correo, telefono, estado | solicita préstamos, hace reservas |
| Categoria | codigo, nombre, descripcion | agrupa libros |
| Libro | isbn, titulo, autor, cod_categoria, anio, total_ejemplares, disponibles | pertenece a una categoría, es objeto de préstamos y reservas |
| Prestamo | codigo, isbn, num_documento, fecha_prestamo, fecha_limite, fecha_devolucion, estado | vincula usuario y libro, puede generar una multa |
| Multa | codigo, cod_prestamo, dias_retraso, valor, estado | se origina en un préstamo |
| Reserva | codigo, isbn, num_documento, fecha_reserva, estado | vincula usuario y libro |

Enums: `TipoUsuarioEnum` (ESTUDIANTE, DOCENTE, EXTERNO), `EstadoPrestamoEnum` (ACTIVO, DEVUELTO, VENCIDO), `EstadoMultaEnum` (PENDIENTE, PAGADA), `EstadoReservaEnum` (ACTIVA, CUMPLIDA, CANCELADA).

### Diagrama de dominio (parcial)

![Diagrama de dominio parcial](docs/diagramas/dominio_parcial.png)

Versión parcial centrada en el núcleo del préstamo: `Usuario`, `Categoria`, `Libro` y `Prestamo`, que corresponden al alcance de los prototipos P1 y P2. No incluye `Multa` ni `Reserva`, que se agregan en P3. El modelo completo está en [`docs/diagramas/dominio.puml`](docs/diagramas/dominio.puml) y la vista parcial en [`docs/diagramas/dominio_parcial.puml`](docs/diagramas/dominio_parcial.puml). Las imágenes se generan al renderizar los `.puml` y se guardan en la misma carpeta.

## Reglas de negocio

| Tipo de usuario | Plazo de préstamo | Cupo máximo |
|---|---|---|
| Estudiante | 7 días | 3 libros |
| Docente | 15 días | 5 libros |
| Externo | 5 días | 2 libros |

- Para prestar, el usuario debe estar **activo**, **sin multas pendientes** y **dentro de su cupo**, y el libro debe tener ejemplares disponibles.
- Al devolver, se actualiza la disponibilidad del libro.
- Si la devolución es posterior a la fecha límite, se genera una multa de **COP 1.000 por cada día de retraso**.
- Solo se puede reservar un libro sin ejemplares disponibles. Las reservas se atienden por orden de llegada.
- Un préstamo se considera vencido cuando la fecha consultada supera su fecha límite y no ha sido devuelto. El estado VENCIDO se calcula al consultar y se persiste cuando la devolución es tardía.

## Persistencia

Los datos se guardan en archivos de texto, un registro por línea, con campos separados por `|`. Los campos opcionales vacíos se escriben como `NINGUNO`. Los códigos de préstamo, multa y reserva se generan con prefijo y marca de tiempo (por ejemplo `PRE-20251015083000`).

| Archivo | Formato de línea |
|---|---|
| `usuarios.txt` | `NUM_DOC\|NOMBRE\|TIPO\|CORREO\|TELEFONO\|ESTADO` |
| `categorias.txt` | `CODIGO\|NOMBRE\|DESCRIPCION` |
| `libros.txt` | `ISBN\|TITULO\|AUTOR\|COD_CATEGORIA\|ANIO\|TOTAL_EJEMPLARES\|DISPONIBLES` |
| `prestamos.txt` | `CODIGO\|ISBN\|NUM_DOC\|FECHA_PRESTAMO\|FECHA_LIMITE\|FECHA_DEVOLUCION\|ESTADO` |
| `multas.txt` | `CODIGO\|COD_PRESTAMO\|DIAS_RETRASO\|VALOR\|ESTADO` |
| `reservas.txt` | `CODIGO\|ISBN\|NUM_DOC\|FECHA_RESERVA\|ESTADO` |

## Requerimientos funcionales

- **RF-01 Usuarios:** registrar, consultar por documento, actualizar contacto y estado (activo o suspendido) y listar.
- **RF-02 Libros y categorías:** registrar libros y categorías, consultar por ISBN, título o categoría y listar los disponibles.
- **RF-03 Préstamos:** prestar con validaciones, devolver, listar préstamos de un usuario y listar vencidos a una fecha dada.
- **RF-04 Reservas y multas:** reservar y cancelar, calcular la multa automáticamente, registrar su pago, consultar multas pendientes y ver el historial cronológico del usuario.
- **RF-05 Análisis de datos:** libros más prestados en un periodo, distribución por categoría, tasa de morosidad por tipo de usuario, duración promedio de los préstamos devueltos y reporte de multas (generado, pagado y pendiente).

## Diagramas

Los diagramas se elaboran en PlantUML y se guardan en `docs/diagramas/`, organizados según el tipo de diseño. Para renderizarlos se puede usar la extensión de PlantUML en VS Code o el servidor web oficial de PlantUML.

| Tipo de diseño | Diagrama | Archivo (sugerido) | Contenido |
|---|---|---|---|
| Dominio | Diagrama de dominio | `dominio.puml`, `dominio_parcial.puml` | Entidades del negocio y sus relaciones (completo y vista parcial del núcleo del préstamo) |
| Estructural | Diagrama de clases | `clases_modelo.puml`, `clases_repositorios.puml`, `clases_servicios.puml` | Clases por capa con atributos, métodos y dependencias |
| Estructural | Diagrama de objetos | `objetos.puml` | Instancias concretas basadas en los registros de ejemplo (usuarios, libros, préstamo y multa) |
| Comportamiento | Diagrama estructurado | `comportamiento_prestamo.puml`, `comportamiento_devolucion.puml` | Flujo de decisiones del préstamo (validaciones) y de la devolución (cálculo de multa) |
| Interacción | Diagrama de secuencias | `secuencia_prestar.puml`, `secuencia_devolver.puml`, `secuencia_reservar.puml` | Mensajes entre interfaz, servicios, repositorios y archivos |

Nota: el diagrama de comportamiento se interpreta como un diagrama de flujo estructurado (equivalente al diagrama de actividades en PlantUML). Si el profesor espera otra notación, se ajusta.

## Ejecución

### Local

Requisitos: Python 3.10 o superior. No se necesitan dependencias externas.

```bash
git clone https://github.com/<usuario>/sgb-sistema-bibliotecaria.git
cd sgb-sistema-bibliotecaria
python main.py
```

Por defecto, el sistema lee y escribe en la carpeta `datos/` del repositorio. La ruta se puede cambiar con la variable de entorno `SGB_DATOS`.

### Google Colab

1. Crear en Google Drive la carpeta `SGB/datos/` y copiar allí los archivos `.txt` de `datos/`.
2. Abrir `notebooks/SGB.ipynb` en Google Colab.
3. Ejecutar todas las celdas en orden (Entorno de ejecución, Ejecutar todo).
4. Interactuar con el menú en la celda 5.1.

### Pruebas

```bash
python -m unittest discover tests
```

## Plan de desarrollo (sugerido)

Trabajo individual. Se mantiene la secuencia de prototipos de la guía del curso.

| Prototipo | Alcance | Estado |
|---|---|---|
| P0 — Base | Estructura del repo, configuración de rutas, enums, `ArchivoUtil` y datos de prueba iniciales | Pendiente |
| P1 — Usuarios y libros | Modelo, repositorios, servicios y menús de usuarios, categorías y libros | Pendiente |
| P2 — Préstamos | `Prestamo`, `PrestamoRepository`, `PrestamoService` y menú de préstamos | Pendiente |
| P3 — Reservas y multas | Reservas, multas, pago e historial del usuario | Pendiente |
| P4 — Análisis de datos | `AnalisisDatosService` con los 5 indicadores y su menú | Pendiente |
| P5 — Integración final | Pruebas, validación de entradas, manejo de excepciones, docstrings, notebook final, documento y exposición | Pendiente |

## Entregables del curso

- Documento con descripción del problema, especificación, diseño de estructura y planificación.
- Notebook `SGB.ipynb` con todas las celdas ejecutadas y sin errores.
- Archivos `.txt` de prueba en `SGB/datos/` de Google Drive.
- Exposición con material de presentación y video de máximo 10 minutos.

## Convenciones

- Nombres de clases, métodos y atributos en español, siguiendo el diseño del curso.
- Docstrings en todas las clases y métodos públicos.
- Solo librería estándar de Python (`collections`, `datetime`, `os`, `unittest`).
- Mensajes de commit descriptivos, por ejemplo: `P1: agrega UsuarioRepository y UsuarioService`.

## Fuentes recomendadas

- Ministerio de Cultura de Colombia: https://www.mincultura.gov.co
- Biblioteca Nacional de Colombia: https://www.bibliotecanacional.gov.co
- Documentación oficial de Python 3: https://docs.python.org/3/
- Google Colab, guía de inicio: https://colab.research.google.com/notebooks/intro.ipynb
- Lutz, Mark. *Learning Python*. 5.ª ed. O'Reilly Media, 2013.
- Ramalho, Luciano. *Fluent Python*. 2.ª ed. O'Reilly Media, 2022.
- Martin, Robert C. *Clean Code*. Prentice Hall, 2008.
