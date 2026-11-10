# SGB — Sistema de Gestión Bibliotecaria

**Autor:** Erick Santiago Rincon Rojas · **Código:** 01251151002
**Universidad:** UDES — Ingeniería en Ciencias de la Computación e Inteligencia Artificial
**Materia:** Programación de Computadores II (BUC372501B) · **Evaluación:** Parcial 3

---

## 1. Descripción del sistema

El SGB es una aplicación de escritorio para gestionar el ciclo completo de servicio de una biblioteca:
registro de usuarios y libros, préstamos y devoluciones, reservas, multas por retraso y análisis estadístico
del uso de la colección.

Está escrita en Python con interfaz gráfica **customtkinter**, sigue una arquitectura en **3 capas**
(Modelo → Servicios → Repositorios) y persiste sus datos en archivos de texto `.txt` delimitados por `|`.

### Funcionalidades (una pestaña por módulo)

| Pestaña | Funcionalidad |
|---|---|
| **Usuarios** | Registrar, actualizar y desactivar (soft-delete) usuarios. Clic en una fila carga el formulario. |
| **Libros** | Registrar, actualizar, eliminar, buscar por título/autor, agregar ejemplares y crear categorías (botón «+ Nueva»). |
| **Préstamos** | Crear préstamos (con fecha opcional), registrar devoluciones y filtrar por Activos / Vencidos / Todos. |
| **Reservas** | Crear, cancelar y activar (atender) reservas; filtros por Activas / Todas / Usuario / ISBN. |
| **Multas** | Ver por estado o documento, cobrar, generar multas de préstamos vencidos y reporte de morosidad. |
| **Análisis** | Dashboard con KPIs, libros más prestados, préstamos por categoría, tasa de infracción y reporte de multas. |

---

## 2. Arquitectura

```
sgb-sistema-bibliotecaria/
├── main.py                  # Punto de entrada
├── requirements.txt
├── model/                   # CAPA DE MODELO (dominio)
│   ├── enums.py             #   Enumeraciones (tipos y estados)
│   └── modelos.py           #   Usuario, Categoria, Libro, Prestamo, Multa, Reserva
├── services/                # CAPA DE SERVICIOS (lógica de negocio)
│   ├── usuario_service.py   ├── libro_service.py      ├── prestamo_service.py
│   ├── multa_service.py     ├── reserva_service.py    ├── analisis_service.py
│   └── datos_ejemplo.py     #   datos base de la demostración
├── repositories/            # CAPA DE REPOSITORIOS (persistencia)
│   ├── archivo_util.py      #   Lectura/escritura de .txt y generación de códigos
│   └── *_repo.py            #   Un repositorio por entidad
├── ui/                      # INTERFAZ GRÁFICA (customtkinter)
│   ├── main_window.py       #   Ventana principal con 6 pestañas
│   ├── demo.py              #   Demostración paso a paso (escribe en los formularios)
│   ├── dialogo_categoria.py #   Diálogo para crear categorías
│   ├── tabla.py             #   Helper común para dibujar tablas
│   └── tabs_*.py            #   Una clase por pestaña
├── data/                    # Archivos de persistencia (vacíos al entregar)
├── puml/                    # Diagramas PlantUML (fuente)
└── docs/                    # Esta documentación y las imágenes de los diagramas
```

**Flujo de dependencias:** `ui → services → repositories → archivos .txt`; todas las capas usan `model`.
La UI nunca accede directamente a los archivos, y los repositorios no contienen reglas de negocio.

**Convención de retorno:** los servicios que ejecutan una acción devuelven una tupla `(bool, str)`
—éxito y mensaje para mostrar al usuario—, que la UI presenta con `messagebox`.

---

## 3. Reglas de negocio

| Regla | Detalle |
|---|---|
| Cupo de préstamos activos | Estudiante = 3 · Docente = 5 · Externo = 2 |
| Plazo de préstamo | Estudiante = 7 días · Docente = 15 días · Externo = 5 días (desde la fecha del préstamo) |
| Multa por retraso | **$1.000 COP por día** de retraso |
| Fecha del préstamo | Opcional (`AAAA-MM-DD`); por defecto hoy; no puede ser futura. La fecha límite se calcula a partir de ella |
| Categorías | Código de 2 a 5 letras/números (se guarda en mayúsculas); código y nombre únicos; no se admite `\|` |
| Usuario habilitado | Debe existir y estar en estado `Activo` |
| Multas pendientes | Un usuario con multas pendientes **no puede** tomar nuevos préstamos |
| Disponibilidad | No se presta un libro sin ejemplares disponibles; al prestar baja `disponibles`, al devolver sube |
| Reservas | Solo se reserva un libro **sin** ejemplares disponibles; un usuario no puede tener dos reservas activas del mismo libro |
| Estado de reserva | `Activa` → `Cancelada` o `Entregada` (solo se cancela/atiende una reserva `Activa`) |
| Desactivación | Los usuarios no se borran: `estado = "Inactivo"` (soft-delete) |
| Préstamo vencido | Es un préstamo `Activo` cuya `fecha_limite` ya pasó; la UI lo muestra como `Vencido` |
| Multa al devolver | Si se devuelve con retraso, se crea la multa; si ya existía una generada por vencimiento, se actualiza (no se duplica) |

### Indicadores del módulo de análisis

| Indicador | Definición |
|---|---|
| Libros más prestados | Conteo de préstamos por ISBN (Top 10), con título |
| Préstamos por categoría | Conteo por categoría y porcentaje sobre el total |
| Tasa de infracción | `(préstamos con infracción / total) × 100` por tipo de usuario. Hay infracción si el préstamo sigue sin devolver pasada su fecha límite, o se devolvió después de ella |
| Duración promedio | Promedio de días entre `fecha_prestamo` y `fecha_devolucion` de préstamos devueltos |
| Reporte de multas | Cantidad y valor generado, pagado y pendiente |

---

## 4. Estructura de los datos

Carpeta `data/`. Un registro por línea, campos separados por `|`. Los códigos son secuenciales
(`PRE0001`, `MUL0001`, `RES0001`).

| Archivo | Formato de línea |
|---|---|
| `usuarios.txt` | `DOCUMENTO\|NOMBRE\|TIPO\|CORREO\|TELEFONO\|ESTADO` |
| `categorias.txt` | `CODIGO\|NOMBRE\|DESCRIPCION` |
| `libros.txt` | `ISBN\|TITULO\|AUTOR\|COD_CATEGORIA\|ANIO\|TOTAL_EJEMPLARES\|DISPONIBLES` |
| `prestamos.txt` | `CODIGO\|ISBN\|DOCUMENTO\|FECHA_PRESTAMO\|FECHA_LIMITE\|FECHA_DEVOLUCION\|ESTADO` |
| `multas.txt` | `CODIGO\|CODIGO_PRESTAMO\|DIAS_RETRASO\|VALOR\|ESTADO` |
| `reservas.txt` | `CODIGO\|ISBN\|DOCUMENTO\|FECHA_RESERVA\|ESTADO` |

Valores válidos — **Tipo:** `Estudiante`, `Docente`, `Externo` · **Estado usuario:** `Activo`, `Inactivo` ·
**Estado préstamo:** `Activo`, `Devuelto`, `Vencido` · **Estado multa:** `Pendiente`, `Pagada` ·
**Estado reserva:** `Activa`, `Cancelada`, `Entregada` · **Fechas:** `AAAA-MM-DD` ·
**Categorías:** `LIT`, `TEC`, `CIA`, `MAT`, `HIS`, `DER`, `MED`, `OTH`.
Un `FECHA_DEVOLUCION` vacío indica que el libro no ha sido devuelto.

### Datos de ejemplo

El sistema se entrega **sin datos** en `usuarios`, `libros`, `prestamos`, `multas` y `reservas`
(solo se incluye `categorias.txt` con 8 categorías base; se pueden crear más desde la pestaña Libros).
El botón **«Cargar casos de ejemplo»** de la barra superior ejecuta una demostración (`ui/demo.py`) que escribe
letra por letra en los formularios y pulsa los botones reales, por lo que pasa por las validaciones y reglas del
sistema; los datos base están en `services/datos_ejemplo.py`. **«Vaciar datos»** los borra para repetir la demostración.
Todo lo que hace se puede reproducir a mano desde la interfaz: para los préstamos antiguos (vencido, devoluciones tardías)
escribe una fecha en el campo opcional **Fecha préstamo**. La velocidad se ajusta con `VELOCIDAD` en `ui/demo.py`.

Los datos cargados son 5 usuarios (2 estudiantes, 1 docente, 2 externos — uno inactivo), 8 libros en las
8 categorías, 7 préstamos, 2 multas y 3 reservas, y cubren:

- Préstamos activos, devueltos a tiempo, devueltos tarde y uno **vencido** (`PRE0004`) sin multa generada,
  para probar *Generar por vencidos*. Las fechas son relativas a la fecha actual.
- Una multa pendiente (`MUL0001`, de Carlos Gómez → no puede pedir nuevos préstamos) y una pagada.
- El libro *Estructuras de datos en Python* está agotado y tiene 2 reservas activas (y una cancelada).
- Una multa pendiente y otra pagada: las genera el sistema al devolver con retraso.

---

## 5. Instalación y ejecución

**Requisitos:** Python 3.10 o superior (se usan anotaciones `X | None`) y `customtkinter`.
En Linux puede hacer falta instalar tkinter: `sudo apt install python3-tk`.

```bash
pip install -r requirements.txt     # o: pip install customtkinter
python main.py
```

Al abrir la aplicación por primera vez estará vacía: pulsa **«Cargar casos de ejemplo»** para llenarla.
La ruta de `data/` se resuelve respecto al proyecto, por lo que `main.py` puede ejecutarse desde cualquier directorio.
Si no existe algún `.txt`, se trata como vacío y se crea al guardar el primer registro.

---

## 6. Diagramas UML

Los fuentes PlantUML están en `puml/`, las imágenes PNG generadas en `docs/img/` y las imágenes que se ven
abajo se cargan desde plantuml.com mediante URLs generadas con `puml/plantuml_url.py` (carpeta fuera del proyecto).

| Tipo de diseño | Diagrama | Archivo |
|---|---|---|
| Estructural | Dominio parcial | `puml/diagrama_dominio_parcial.puml` |
| Estructural | Dominio | `puml/diagrama_dominio.puml` |
| Estructural | Clases (capa de modelo) | `puml/diagrama_clases.puml` |
| Estructural | Clases (arquitectura por capas) | `puml/diagrama_clases_capas.puml` |
| Estructural | Objetos | `puml/diagrama_objetos.puml` |
| Comportamiento | Estructurado: crear préstamo | `puml/diagrama_estructurado_prestamo.puml` |
| Comportamiento | Estructurado: devolución y multa | `puml/diagrama_estructurado_devolucion.puml` |
| Interacción | Secuencia: crear préstamo | `puml/diagrama_secuencia_prestamo.puml` |
| Interacción | Secuencia: devolución y cobro de multa | `puml/diagrama_secuencia_devolucion.puml` |
| Interacción | Secuencia: reservas | `puml/diagrama_secuencia_reserva.puml` |

### 6.1 Diseño estructural

#### Diagrama de dominio parcial
Primera etapa del modelado: solo los **conceptos** (sustantivos) extraídos del planteamiento del caso, como clases
vacías, sin atributos ni asociaciones.

![Diagrama de dominio parcial](https://www.plantuml.com/plantuml/svg/NP9DImD138Rl-oi27gnGGJs8ntwk2Yh5uirBEfkkeREJ9JFR-e7_tKoxGlKsUPCyoHjc51DgwXfV94wUO7axWNEOCTQA3K95C9E60miiK1sZVmq39y5HcoG2LnGIhzbX9N48aGDWKbvrEHaOC8hrE9P0yQmeueP3YmO6vp76SJhKqhqHb_n9S75K4jyCkkDGmnfzfADCHMliV2ebf2Ti2Ex8RodP4ly7m5S1C46tgLMwK4t5Yy99EIldvJndH2lINhsQtrnFBqqTgyhkh_XT5AUmxEnKvdPhreo-9Q3tfCZct3Roq7hB4ZPi9v6zuio-DGwKQev9imXTx50v7yjXGY_rNlMyKiDyP95gKSOuj4vebMneayiRSumHMbjBoUP6iN9BasxHRdlm-tAWzz7q5zR73tbA_rxqv3vypFJ-_No05iM8GfL_nWy)

*Fuente:* `puml/diagrama_dominio_parcial.puml` · *PNG local:* `img/diagrama_dominio_parcial.png`

#### Diagrama de dominio
Segunda etapa: a los mismos conceptos se les agregan **atributos conceptuales** y las **asociaciones con
multiplicidad y verbo**. No hay métodos ni detalles técnicos (rutas, repositorios, UI).

![Diagrama de dominio](https://www.plantuml.com/plantuml/svg/XLNRRjim37ttLn3PWExM8XsmTGsmeKtYR0MwBMYnFUs5aHb7hIm6afnsjtyVPUTYP_Ns58KwEkGvfEGp7z25iZ19qC4GNByVmY6CDUOE2uICOCo5jfg_sIUAhQ9bO2zX0vPoLffV00QdPsKCVuUYD44lZLOwmupyqoJnjzekKSX06VJ-FDHekX2sQ_s3eD-0-0LcVATj3dCqdXex6SrHk2TimoSi23wGML7G2lSJmCy4O8ZgDdTSscp4XXqycemdwIIDE-moSkleo_JDwz6nHC-Tuxjsy7U3s7AW3jvqSfgUxFCEJqvVzOT2aHp0cEPYdnXbevcnHF8WsXkshNqjqP1FQX5VV8bESvNq-RKWnH9R5kHup4f-RU3c3XSpHus0zA2vhzWvQWO26PgpROP81Y7ZM7DTmGY3DDXfRDMWEDFvFrDBrvNJooXuHtQfPwujHlkPRHKSIjFaHN76nV_Q1a2PlyqwS42Jtb2nDEZ4htKuqtx9Li-YXTkqKnTL5TmXOImIOKvgWHjWEtgf2nse7HlJYarPgUlsxgDCQfTlTR7ehoWuzDlG2asjjuFoYZov5VvNoHht8DE1i1YCjTC3TpNPp5plk0U7Xz3h7nqzw-qy783d21Pbxpgmco87i4150jiDKHjOpyC0v9Kfbv6l3dHcbdfvTaE1unrw6BtBlGVUqZJmigfxD82SBBbOGbBTSgVpHG2URswW61alqm1I7qhfcnNCBtaJ5TMhz3wGgovIxVC0pbNGAvQj2ulLCY6RLK_8EiMCG-0YvcYCtL-dPT1ACY4klvAL7aNKtWZAr2ZnzgsmYzOQtvsjKYmarQZ9eSOKmZqyFZxgz_im-ZnjL3CLChrMEiKSC-octqrUImlAqH7A0sVaT3JC1aSL4yI1gffaOZyzU6rRztYNwaoMyHlr1m)

*Fuente:* `puml/diagrama_dominio.puml` · *PNG local:* `img/diagrama_dominio.png`

#### Diagrama de clases
Capa de modelo tal como está en el código (`model/modelos.py` y `model/enums.py`): atributos con tipo, métodos
`to_line`/`from_line`, enumeraciones y asociaciones. En el código las entidades se enlazan por clave
(`numero_documento`, `isbn`, `codigo_prestamo`), no por referencia a objetos.

![Diagrama de clases del modelo](https://www.plantuml.com/plantuml/svg/hLTRRzis57xNho2yXoPhuxORMWp6DbILw4I0OmUs4knXW41BnmvNcXGeobrQvB_taBhQYVtGs80Dyl0xzmlfJuLXsfGRuHbk1935vMToGKBErffj6Cc0188LK8n8odAtlrOP2FMlF4lT0NaW8CiDQ9Po9N6Fa8s5l7M_gXZc3uYfI1Pf2UUULtpXCcUeX5WvXM-CvilIG9GgkU3VWBphGOfxbgclNAx9Yea2UYSPh5Wfp5X9CsKR85SWjc1uodeOmIMOXno8qkPUxMictpr2FhFqorghKcQ14agJNyRXc8wfFL4w0rrJVwD_V0pU8zNNMdtT9JxsxJMWGLcTmHF9uOVn1_gxvxqY5p_z8LGQdh4C2g_ouROecURA-VBQfKCbcKfn8OqY8pH8knErMMhezeRdlTDKQRIwTme2LahsA83LadNxYmi7KucDyDbvI_-ECCp18tczqcfJdTgV2c1njRqrUyPJuzZjmjAI1759qefyz6e_0sPWhJHdbQUfolZwY7yOe5Jpt5Rc2OnkbHyrSSANkau4BvQo7snJYfwnh3HO3xteMr-IjFMm0qfksRWqbUM6YGJ-WqqkcCQ6QqyoNkHAygNe4N_UM-V7KKzljAs7ZNe-5xlE7wx95QJtBCaRMNjqmJVSm3urWwqIvKvQJrURZLj7VR_6eNEW2Ej4FlKeuwn8D1ZDYbu-jqouCgYt9tF3MNZKXpaKeBVi5EdJjQZJPwCsye0ZBnoYlNlBitSJYN4WrhF9dhhGq4Ly6qR-DARaBpAWXIanaTB00C_2MK3hWr2bK5FfFp6TJsSE_ZzU1L8DsXXK1TrMHzsf68bSgnoqUNXiIwLNGViGTDtPIrsOcufjJVQ3EBfp-ltKyArJ7zAxMpg97JM4RGd2EFeTdGPHwCXt85EU8NLNlAkaLlODdOPHu_GDo8mtRj_ubtxeEp9RiupjowbJkMkbtrh9h8p0dmPqKei9c4n1E4aOr6ayfuq2lFyqxEfeftChVn9X6lpuTkvOS6V5n3IOpYQpoyWHSUUqHZO8_i8fZNnBklPZYjyeS3XSMU9Lj8XdyueLrrLOvpIugg9AvuwJXb4GJIi-6bhIB9xFdF1PV3LuSTtwXKfvKxQlo1b80eBK3Lm0liS4-yOaoN6kOATl0I_Mfd7V4DlORshqkTSy70Rl1-HFb3ruDnp-EkX6-uZij_uXbdax0fvmL5VYOHNMfET1dL27wQx_FLp5F2BxbwZNQkapuBAQtor3qselp4m8EJQ4xI9Me6ZfdiOkH_WG9gnwuYhtHgu6v5lt0bjZG3FciZZ4ww042qYnkljFwovNm-7VJmRLY5X9dRiMyynm6DLwlSh_3jNrU0jfOj-1-WtSmhgSME1k5pRnBSWI_ojutYUCZlslyGC)

*Fuente:* `puml/diagrama_clases.puml` · *PNG local:* `img/diagrama_clases.png`

Vista de la arquitectura completa de 3 capas más la interfaz (`ui → services → repositories → ArchivoUtil`):

![Diagrama de clases por capas](https://www.plantuml.com/plantuml/svg/jLhlRzis6lwklu9OFvnpIu9kXxH1WGtpOljc86cAEDa-x0g1bXY7BKKA9ELUD-n_lvUKA54KPQjBhq1Rc-z3ylr5lWz9_wGqbhegMAAfPWHj_lqpEaCBYdSI5nZb15qnh8X2fP0emoLM_-4FQtJs8zeGkQSP5SfykIEbK5GBsNoVo-o9xk7pkVwlHZCjSgnGfJ17XA4RaHCcJf94VQIyn30Hoc0IDTTQqcsboJeJV4F_8EYb1r5FE1UVAD-XHymKyIGvUSGLqol1zLjS4FGBONkYQOOzJ8cpZtX7Dlep62b9fZ7VCH9gWFvC4FePe3ifAfvV2GPMlrWjLilLqaY4p8biMhzVNhww-WvQvrAAJqtZnQjN5w__bVmrdBaUsX_WzUhowd81hKRnMh6jO3bqJlw1VlYRVz3DxM9vVPkuMRyfZBFHB1S5vLISV8CW4EN7dOq1Uh6ShxvVNLhTQWSyg0f34DllLrYJ7OGLjotNT2ix-Jj988EAhk468j61xuY2D37V2QyAT4zBqSomXE-kUGb3vC8DDPJOCOVDpU1My3odtItVtMxMzxTtwzjDvphP9ZNa_wmaKb6b2SyeRjreyXuIPBcwMBxslDYa_uEcpBOYzErYVZzF5-ixz0OfBT6VO06aw5-ry94omatgMc7NLcBzvBSnGcJAA2TOpKv0m42Xtq7wlXOJbS42eWraPl-jknlmLWXMuoHno1gZ_A5wKASc-dP7E95Offd8wKxCIaaUwGTHZtwAUiESj2f3L8B4QZUApyunOglDq2di4SApgi6_xuDW5qfpaLK5uLhCsa-TaLt-GgyTVCwnd5LrOoVkkmDdkiAC_d4SIHY5PGIuoCmDoZEvNJkJZMvxHCnk75__rqthBr3FvCmr-v1HioUWMzD31OPssnrYiiqM7R6NgYsVcN-wgTpM0yXjfJ9S0w5mLKpCD96WeAVOO7IlJslmm9n1B-THPjgS4gEUF81gFTWtQkW_jn5ETg7hC3rhl6tRwm1scA8zQU1cfSHMmh6kaSZ6kZZ7bqspf_Qe-uzYZwKnGY_IGrjTT6-pzMboj2nwUgXSGGtGpj86dtgM-pwDJaPuJY5av8XIMcZCEhG5KwxxqIbCHwVcQ5mEeFul4McemUIODFZfKUc8JRX-yAHXnzR0U8zZ2wxVquL7rgsTngCXEeBycc5w7bdRBEz-NL_rc9goPn73qfZO0V4tvnOE6tpcCTwDt0FVlLnThYw6VBS-p92lmqb6s8WaEnX4Zh6CcN7agUqvZPOCElZifDCXDYvawK5KMCodkUSvbVmPvVj05wT5YrTfJbKfEDqoV_VJLSd8-o1C0v9mYhWejfASGdeP_bn2Ul6eYxjG3_Z0eJ0V1uzmY06EyamIav1W1lb0Yf9XMD-sroaSuxccESuFnjsLpo3qrxVpj-cx9HoK5XledjDC1sSPYxXUtwplHm2_pgzlxzARXsjx89hNHGNzWBvx-V9b00KZi5VgQlNRjNQA7adsX5jvr1CvsGku3f3ZTNBGvSjOrjyaJTFeqjuSDmzfCRejZmRMbk1f2_evv27aA5DuoK4FJM0eyTujPHdhPO_r1UxpcnBl8FKiRpdYMvEdc6KLStZLX0sFkCYLoHXuD1aB8ONoWsDMrliewvaMt3ZJ-08ACnwgvzAUUjatX2HSzIC1u1bXNgUZ8MkguCGEdfFd77PhI9a5ra85hhORk4eBY6gT-yRZMfGfhrChMd3SAb51QOk28M5mIlcZn9cfFd5GNe4OfA24A4XEkrtFuX-PmDeLAfWJba2TYbPgyie9bN4vq3ce7qGBN_nS4lUmxjXRHT4igvGMXOPRKo02BMTxe72vTh5SzgueuOhw1bF-6-Lm7-myh_5sJyadStzn__6-_c8bPn1Xi3TFCMCfeC38fXt8nAujZw9htuFle3qtyPtLmNTJmy0D0LDkOk2uuASdCpGZxHWT0N0jNfbtJS0Y71SRJ6CfmDUOf2qGBMO7_Vgqm8aQAkQ-yehiiP-GePAk5XtHCwZYdVbrPKxjgXcEtkm9amPtgxYBRR0VU1xgBVl1h7QZFZAdhGtjDxUTT_ju8m37M1xPRjtXN6uh6P-jWyEJ39njnF0-Va7WohpEOJSEtFIR56v6UExL-FKS3bjlbniO1LPjV_Nzy-pCNnHnQPtBSLcRGd6nou6uj8vLNEPy6qZFpt_iUUmDCWcKT2lE0W9V0me3xq_yZWRN7_eDAZ0d7t2I-Dl46Ro6zG-PtcH6w1-majwYCjA0XYV-kZYp3sz-oK-w13P2d-ebVhuPOQoEcKmPVTTBWhEoPrbtpvBqpekjVOS0aMlo93nz-Auu0WldYs66QiTGmRLUqcFEam0HbGUOeIu1ZVF2V1WKMXw1J9eiedMKz7mfDdJNA30qP1GuD6SK6iiooFQHXslxSWVF8Zb6XYBPJGAf2W6XAk4UnaET9CENBRC5UP0azX0KOi97ar0UUHG88U4rT2WVNeg6Y8GBRLwXDN0n91xRXsAe8_Vs2HygJlqhWFOntxulYpUc73blDVv4Ez0OM2X65VmbzPq3u3uZO5j8jTkC7Ibu6Ju7t8B0CGqUnGa7qbd_7Y7Dx8yHpalpWmKulo6ZRvBy11zDo_y0)

*Fuente:* `puml/diagrama_clases_capas.puml` · *PNG local:* `img/diagrama_clases_capas.png`

#### Diagrama de objetos
Instantánea del sistema después de pulsar «Cargar casos de ejemplo» (con fecha de referencia 2026-11-10): un préstamo
vencido (`PRE0005`), una multa pendiente (`MUL0001`) y un libro agotado con reservas activas.

![Diagrama de objetos](https://www.plantuml.com/plantuml/svg/fLTVRzis47_Nfo2y0ak1EP2io7OwR6ZZs5q7fmtIP4y3WhDqTfXAf45IRhjX7sWFVIZw4Vp5TgGaMr9i5qk2F8Y_Env_Txm_z4jjG9ayIpt3JOhi_UiprcNd71OACc09idUpUpHI_ocEk21bGVy8p2ZGh3C2jG35Oj1IMrsynsoPoixFx4v-Ph-mdj_hTuEW6_ZFFKz_u689P9RfEqZaHouMR0wfnfeamJdagPb8OTv2XkmtJ5TeU0mr7Kc4OiF-zXWxW_Z3GibS92EPIiL-c9nFnfEnbKYLe2hHtdZO7mM4lb9AVYp1gD-F1g7tJysoa0Rts1rFJiU3jjspmMdadv49xqVMVVGVkz4vA2wrLthMoMW9x4Kbw32ATO5PSYBFKCdRHCRq8OoaE7S2_tGuw4SdOQzZDMGsKsZn2r3hBy2cwszB_CkA35-w3MDjyeJJRQ95aIusSVYhsF2Lx5YVAZOng9Ikjqcd1FVpYIY-Wy5msEGpAhQzNd_BMdm-6LH2VfTC2hbgXwR0zbFf-Q5_uaT-ayhKxQ80cVKNyUZWtESWMdGSj9-D7_J2awW_QBBvtMwwNF-hcapEPOo7Q3mfxqPW89KBkN76O4o-48mBITdclB6OTIQM2L-uuw_7eoRtQum55SI2CgrvLzmyC6Unfhdfc-lMnN1A1J1qEmrhvB_AOmlRN9pocIh2NSUjPQvdmfev7GnFex8eWYAc9a-h-zrieQwL0FKtXXJ_p-PEYiw6tcrSSQ_vRIH5xRReTA1GspP7SCBrKWe-IntYDmg8esXGTi13hb6H6qsk8wiBwwz5WzKonGIIVHJBMEwW63sW63qvVowLpScirhYM2dtV3ydPIkRyhU3cnLzUZIrg2SynleFRPRd72el9uNV3O2jFUKQfiPK6NJ_QIXDSoJIFkHHrZS1lriuvhd9CJRE82txHRjhHJjhHOTgz0xH9Ejn7-xlzfk3KtqsrlvDg_n3LAaBx8XmC_ZVL9-NK1Kr_s0x2F2K70lBMuSKWBB6cgnStKujsN9g3lbLeNoYopFmLs7bDtwJJe7s98k55XtqgyolKg5QmBGQADHtN8_AboD6lq2Rzg_5xYsvZhOejXrBPXRpP8mlZuSuZmvr7Xeyzyacn6eiKOjIU7IwqhBLmpmu8WcoBzBpobK7hieLuLIkfL6hhCZ4yhtWgRJP5NbN8hQEyuk6mKUnxLHcr5RSyoklpt93Vh4ElkjRMpYhqROFkfQduuiumET_mf0UgAoEw9T6io2LeIE05QQJ0RjumcWrPRYq2wL8zT_v04VF4lP-EWj3LW9qNPHdyn20NJ7DXWsJWkKTfxrwxRIPL31ahNsgkvbTSigYmIRyM4hGy8lQ9FGkEIPiIurdaFaRlBez9T64hIXMZ6TccnEX0jimnGJUXw9BeWKJMNVCgviXncrUASqUh7hi7evPrVxLpKJ98RAn8eSnapOvw35pAwhhBB-dJ_kBv3m)

*Fuente:* `puml/diagrama_objetos.puml` · *PNG local:* `img/diagrama_objetos.png`

### 6.2 Diseño de comportamiento

#### Diagrama estructurado
Algoritmo de cada operación con las tres estructuras de control (secuencia, decisión e iteración), siguiendo el
orden real de validaciones del servicio.

![Diagrama estructurado de crear préstamo](https://www.plantuml.com/plantuml/svg/bLPDSzis4BtpL-me5seYQU9qN2TId4QEgDGp_XhPFIKT3qH0CXeGu02W6gUJ7vDZ3Zdbq7lrnxe0I8hwgENgGXBOnUvx-nQhDyOIROjCH9PRmU3wtGbqOSJ9N9EC03DM5wajDA6g3rSQlqcchfbUy9JrKis8litBrPYRgUm0LMcHCMbL1sOilIFrVZkAp4SkSu8dWxd34__aSWup8Wnhx50s8uMmOoNj1SaO_Ch4WbcUaeODIIrVS7iFVqK09oJzEDUgaFIj4ah3a_5ed8mJjwCqPRfSVPwy-Fdj0QuYk4n9kksMZ5ycHms3flV9qSl3PoVH5yJW28lw0HkNFEKANdNXJjqFeeZF85v73LpEbCu89R-qmTun2R7XROpYJTsELJ34N_Vyl3iQmO88JbLjAvMp1UXFaflBoSLm0l7O4TQ1rjZ5GReWryjlLQp5yYlwarPxuDsCLJc-CFIeuZ99-GoVMmZyzohTGPLZqumPc1LE3XjWTYPuHiepfOAyO9YfORhqtvbW01iINAs4xwXVc8Bea6hvUgjPhdfgQfbag4EbRslnnVKR1d8mAc_sYHlBDlZTaVnlfJtcpcIAOdGj4BBsEQye3VarOlHSvQc2usDe3PrILUlnyIWpNjqFHulwgQ9yhenZ8rt-2E_8iC17hGUt8Ygo1b4_Tyx82VDk6NOPGUlLObhSAmW7h_IBZ-LNvA3SC87EXfVqDWILc_9DNUm0UeDkR3lu5jXcwGMVQbzu_x9TTdVp-EkdB7QmVsofpxpr_ocqFxz7kScLv5E19Bo6P_i3NNC9x0-MvO8Wkz3mVx3KWcVSCWV_x79uSNjsUdvwS_s-4flbkVhzWumJOmlA2N89Fy4_VyD8fOvOE7GVoIVBD29yZd7wNbz1EWsf3ClLDSaui2cUYLSAZKk_Dhm-Xf3J_ceF1Rf_Nlx03WUn_Ew1DA-iX-kUCyo2gXhwLJ8vlHmzYFseYVrW3VoX0n-kinMbQzVRKwWYqkLtWb8lsymPpftQSDo5bRXrDKbSxlswKT2c6f1nCEh0vaZy89lngWaPia6sMftwncYNqyHhVOvmAT5nFKgTjgqoQh_c4grnVX41cisn7H21AqND_nxXRSgyQi6rnIuSDDekT2TgfS19zXcJzglR6Mz9vaONBk6hUfgvlnTKzI0Ckb8zVUZrUZj5WuVvqCpHAJ5mA48Ra4Gbn1JdlNTxBAod3bPb_X-e1dj8NpdKtSxTVAPD187jD_Xq_yF-1G)

*Fuente:* `puml/diagrama_estructurado_prestamo.puml` · *PNG local:* `img/diagrama_estructurado_prestamo.png`

![Diagrama estructurado de devolución](https://www.plantuml.com/plantuml/svg/XLNDRjD04BxxAKRcueWqIf6WDA5GqYPmeALgom41YYRsnbbgxqQxQzE2U23EF49VZDdrnZz9WLEoC_FDp_VD9CVQe395dWM6cup1rPi9xC4fnrHXZi2qKKLi2eM97C65eZVcyegfaiTiaB1IPYLJKImJdihvsljxGQ1lk5WZvG2z8kmtBb9OOgPPovEm9HQPcKbXpZ5dy9PHCiDZRCLWR7Z9pHty200c6D-aIXOYEP6PLF1eTZgRpgRM8rN2bBS-cJv_Th9FLXeZboBPXKrdXzE3La0RFJauV3gS13zf1ajDCDfC1I_sGB6r7CY5OOAf-LggUJNv3W7ZW2yXgf7ibcl3NlN0h9Y0I1130AFBwVNxo_FNbn3DB3Dz22_K_QyA8GWaOcB6CXzIFW1jv3fW50YHvhs0YOGlEsK6zYEHS7G4uIah2vOP6TP5BUR1eXyHbWKZDJnYkvZjjYeMZ5RopjAmPF4AhJO5PkDWv9xpZEVSCEkk6sexnWsJtkxMfuYv51P4gTiXVXPoDBDKh3eDgjhyEwfw_9wbsKWj_y_pL2cI6ZDeqW3Bg6zF_py83qOPNoZNcFiotra9hXUYqSI-_3fKmArTyB8uto3XUYq5NsHCrmKwniUmFwx3vzjCE2iLszKjuQWfdBP9kzPpl8sibbvABr4VXeGUbKY7CC_fDD76Th2ti3yS3YaePqBZLxOHo0bv_rlGXQGq7sqjUZdeieLX0nBFaT39zXA6sqHKz132CU2QsALumww_EwUMJTu2smEY62WnvhXLXChKqpMGJyCluvPpiCrP-zq9T7pPY1PnFY0jK2MMY-uiBSsSrGtGgDRjyCn-YL8xFDO_EE7PXtTXhm_Li_zPjBlhjpknFojs3UoCrLx_lQ_At6dABL35xWRq09j-6HuVmOQmkoelL7qd-D243IeakSYtBkZaDnka8CCgITXqihlQpNLVgu9Ms6Ubxjtz1iSKQF_V_W0)

*Fuente:* `puml/diagrama_estructurado_devolucion.puml` · *PNG local:* `img/diagrama_estructurado_devolucion.png`

### 6.3 Diseño de interacción

#### Diagramas de secuencia

![Secuencia de crear préstamo](https://www.plantuml.com/plantuml/svg/TLRDJYD74BxFKvISYwqOmX9j5g60Ti5s5ib6o5vE8KBbcSBqRa_tf7l6QqZo07cC75744-IsVh5KTy_OCsD00WpryrLz_LLtlRSvchn8PPIBN1BCVZc3FHW8N1XC4HB-3yK5gLZWCSI6q42X83Fh9mvCTHJPBq9boCvWxp7HNuLQm1rAIpLBGdTOo7oaLNw9AS57aalAHOprQFhTmH3y4G5SSKqY5Xcg_0pZBmkZ2vMSQwaDV3SQZ8QZOSj9cuHCwN0uFFhf_0qxZCKTZOMYXlNTwEZyQC3M3yRehysGlshrfBYQaBMue9bu93WyF8WYZ7Fsxfo9kHGwfnYDq1r02zTHjYq6EfzmVcN84sHlLFVweXUyBffkbS-Cp5B4v7rcJPThMpYGAMNQ2WP_28ccJQy9auijdqdBPopcffrdF7sve9RRrJHACCSvMe8EclXUBBM5_NoLU_CeYgvXxvJRWsCW6nin9xYOdLts8T5naPBADJp07SNt25sTnK8hbBqRzG1P8It2jt_FlR2kAbLz-yzHBPQOaoED4rVfRxq4RxEoq2vdMQ8K2GAhnuCoqXPLQIueNpyfM6AyVjQsp3M3KipRJCBELQtWVgYtjora5aMpAhR4lDCcHT-SGvTOziYeblYF8YyCbb7NKmxJyvmKCQWsjnkaxkPJ3OnFc2CuRiHXaeYdBYZ1EjgzhIobL0Zy2PTQKPHGFKU4CgyYFHahOTaIMFa7BfHtrZmDCv_GSzmTkV7jRyJd0rNCmsjumE477cSRG1BTwKN4pXkCUvmBANAsX9odB9vMuwLhlMs0JT6iDN0nzTQhCmgz1tFPlUH-Vgra-nlRQlrpggg8IQC8KebWOBBT1lJ4GK-QqAcRh0ftqiBrOzS2dNXGHtlE65GcW2qcMrzcUq0yDXakU10aH-m4TbondcmhrEjvJtcgMumxQNjzzxpJfjRnrFyzRhOitKLHjHoiPTF-2gc4vcorliU-xz2vpz2GMo9ifXLVcsJXvnCuyAulqp3U1DSbvrgcpvHc4ar9HKd6FJxKBDl4BUK5eOSJTr-lQwXqS8sKGTodt2Zyz0JY8jDyhGzjNYI2Bqw27_imqB4x1tZRX-4g9yCT75PWhtIwVau5H_0RktbFBUF6g1x3Q8LOtsR2oPaNLuc3hoSENVYhvrOAd_Aal8c-1wRbiLNikssnRshLleLa_OosrqpjIRnTE0xvjenr8XQwsxcQ3ZjRnngNpd9mSA0wBsHPC849ccv5TJD1K22l7UGdOFsi-0ebjJFyEv2VJ47HBXzUXFjruUsTm9kcdvyKFkI2h_D7hip7RClQ3eQXyAw9dV5eZOWhXkNgZtXRbDCIxqJyGA2iuV79XdGRnpfTvCvISLM1z1xmEscqb7DUYFY1R8Myt8gFSVpnGrGVmdRyZZQ7l1oPLhLLl71lNr8xVo_GzTEADuPNqZfQ-cw_A6Nk7zz4xyF8orI6IJY63_orDvdi3GRrz2g9cf_2R_VJVTTkeLbuyMmHnxoxiK-vEd0DQLZcvde5dVNVhjREZMAACu4GOyeB3p_Znkrq2tHFEUyx4iFZHewCLvDvgZh0bvKxJtxHB7wcTc6ynKJl-NzkqVuV)

*Fuente:* `puml/diagrama_secuencia_prestamo.puml` · *PNG local:* `img/diagrama_secuencia_prestamo.png`

![Secuencia de devolución y cobro de multa](https://www.plantuml.com/plantuml/svg/bLR1RXit4BtlLmpK72GqKMKVMiE0WjIorGRGfe8Ldwf26EsEP3OKkIMvYfMs7vDZKVIKOs_nZtL8xagxadFeKSitRsRU31_roZeqhjp8n0ad2MO_NC4Bk1QuDhX1oFaBPIMfJE0b_zfgkIK3fG8fbaP3DzCAiiUFCYkbzkXDAHtsO0UPNXeq835-IXBxJgW2cHNiFURwlL1hMA6qr3Z9QOMC7clbtk26u4VYT4vas8octtmz1Byd05CkNcIYGEMkC7ktDhfK-KXBRU2hyVNuPdnp1D8c9rC1pcyklXsTCM0YLZGHYbgdtuqlHXVNVFgzCVfzE-JFHZqRV4Z9MbpJJ7mWE3yV90bcZj6TAx6KGZlAq0ZT0RHmbnI7Og3p5fTJGpo2ZRPprRrxtOkersrOZPcHsOgC0cRsDEIM2cq5Pzy5rFIs3PlugHrX9aUOrC_h29FUdXGUOAsgqoTucYMdioH7Xqkq11qqsRtOQWjzz-32yJX9XaEuzZjMPkBnauBXCBc35ozP3xW4ifaHImAIl72VSh7s-oQXC8z_XSxdQWT5AIt2vx-lwqKD_Nx-rmz4RD6HbvRPc7C6XttcBVPyYw8IiNV0pvAPHqzl6QwNZXIPHQ7D8aPKWRs4pnarPf0aJbiJMTzSEAmorcE2F-2DLiIR8Xqe3VGWB6VJi4Dkr3r-X0xtK99qkiChE0i4GORksD-PvtxYLUCXNl55T8Rl5NpZEV8wk9SGmmygGUXCHyvOqugoUrpabUvyduTmhtTpvIjblk59APKSp5IY51_GT0_20HoaC1Hd9eu5YQ0g_LjJiWuLyUHOPs6NQa_VzxzyZiaXF4ousKumfdukRA4Ltp-oyFKGpbe96fK7T4rvKdOuZJKtK-G2xS8GwsszFkm0NLQCVJDAASL6E1xHe3TNM_I-CMo7FC2pi_vWCF2akd3jmvSmuCzLjlHOZrgA_UPvQDhUlc2ujTBnTA-DTJ-7U_bBEFBRvpSkRb-fAhE6xjedn1o1SyBMs_z6a79LlcPn3IsZzyzLgvqTH0bKoGjcGtZOoFtIdp0kOlBz7UkaTvDEdRZHZF_E8ghE2SEwH9DpGQ5JY7iyx4o9A-Ccg2BZdqVgxUVUKZ3YcbVGh-ppS2tsLcLepSruoVfm6rk_10Nvup_C0w6GItWMfHZzDFNtacbpQXXDzAKxJh29xybIFx1ynZyVQ_GlANkdn6OGkvdtp97sRp6_llLhUt3EbEaiIShypGuaAo6nYMtwvYWysYs_J1FcyC9woGjSyrn2MEsPSUY703RvzEdLFRBCQfA1DmwgyiGlM-AKq-VevvrMuqWRZhWXPV5NgXslddQ5hZA5Sli7QsjJVccda-QMDFoXjIUjcgeLYOqL8Odlo6dB_skuglxf1h1oKUh_jm9fahnY9lyNxZy)

*Fuente:* `puml/diagrama_secuencia_devolucion.puml` · *PNG local:* `img/diagrama_secuencia_devolucion.png`

![Secuencia de reservas](https://www.plantuml.com/plantuml/svg/pLPDRzj64BtpLqpPYmGuhkf3QnYG4Nz8ZG7NACJeK3I5CIJ7qZRBNNLtwLXfycDwB8gSUkmj-cETNIubIhA3jeUY1ma2zytCldblHdnk7HfNLp9nmac2x9jpU0QN0cS6AuIIdr1Haoe4da1X2Cq15AWAacXW2UX8bMIWLWY6B9bxJ1BxMgW5SZpOEPRwZL0pk4DfgNDIqXtMqesrSZTO4RmWUKzE5DYDffzzPO9V4e3l-9gY40jKxXoBrpEZQrLUQAaDV3w-78_6ensGDdon23WQ7NzryIK3hiKTNGj5MwTVZuylZY_vzCmO_MOxv7tdFXK-V4lMuemoyPRWw6YG95WuHgVd8fT2EohG29q2MfWcYyrb87s9-QJfZtsbUjEhVWEwsaP5ICPVeg00oROHKrlx4XDQQ2kuzBB9Czb6NOlSx6Ak9u_Msa5D9ac93dEq12cQOYxkjOL3z-32yJX9XaEuy3vezORXC9d2irCc0oT0jZ0Y9xZApc_O7wKkwegKqw_K4XQrj0WVVs_2O_sFV_eUYdjsacy79-5K6KIptSOYFM5pTR19rzy4PKaMgayuHkViHpAt2srkrzXU9ufHZ1qpL9AtRTDDw_c5irWxTXdUmOrMn2fBrs91QQ07ORao_x1kzIjSgN0PpGxAGehGYTxOM_vWBLa8L0KRtl1Gm1Sy0hOXKUgqdn23rpNcc0if79yqEKzPlHrwlY6XAtrlwsrQqilVa6hE8grWYvOKW6SLe1jE_FHn4jTht9f2wYk7QuSaXwMm2wru4CZ2AGoUJFK2bq0_KRNW5KBs1AoMebXzS2Gr5BhIi32httWjLPqALgXE37HAjMLEsRexBOhTxEhlmPDDGoHp_Y4QySTmw7koH722itIt6gHdGQkKPPDG2Sltz1uFGO_p_3wciLjv6idJvYg1syA8YimkOfCuChkTUM8y4eKknKptqiaeYscsEFddWy50fNiPPjoE4aql4lRkPHc7BRC3kADYZiEvNdRJDhxY_mEQyTJArGT57AhQwxOss-t2IrFx9hIr_3INw5tcj4Ml1hKzK6NIVFjFIPt1RfR1bDDLpTxDzGCl5UFNx0n1SeCnbzWDuXKIDbJx5_N99SLA5gi_V3UXivrYwDEBAGBMkwaHP7ybxHaoAjVYEwArROgpwLsuisVyplXikBRX4xkcpTCTLEHTismUXNMrTc1mtzfjMSilqZgCHRbcR4dPbetKEBH6ATwofMACLtJZ6KDDeuNPDSkdZDBMslNAdZlsLJ-BRoEzvi3q_uNyJN-VLZ-c_Z-Ad_6R2wmbtKoedzQOvEmVQpzY3_7a_oVQXxT9KUBVKFiv0_nRwry)

*Fuente:* `puml/diagrama_secuencia_reserva.puml` · *PNG local:* `img/diagrama_secuencia_reserva.png`

### 6.4 Regenerar los diagramas

```bash
# PNG locales (desde la carpeta del proyecto)
java -jar plantuml.jar -tpng -o ../docs/img puml/*.puml

# URL de plantuml.com para un diagrama (script fuera del proyecto)
python ../puml/plantuml_url.py < puml/diagrama_dominio.puml
```

---

## 7. Limitaciones conocidas

- La persistencia en archivos de texto no soporta concurrencia: está pensada para un solo usuario a la vez.
- Cada operación relee y reescribe archivos completos; es adecuado para el tamaño de una biblioteca académica pequeña,
  no para volúmenes grandes.
- Un préstamo vencido no cambia su estado a `Vencido` en el archivo: se calcula al consultarlo por fecha límite.
- La interfaz usa tema claro fijo.
- No hay cola de notificación de reservas: *Activar* solo marca la reserva como atendida.
