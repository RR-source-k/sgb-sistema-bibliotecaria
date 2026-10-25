# SGB — Sistema Bibliotecario

## 📋 Información del Proyecto

| Campo | Detalle |
|-------|---------|
| **Estudiante** | Erick Santiago Rincon Rojas |
| **Código** | 01251151002 |
| **Universidad** | Universidad de Santander (UDES) |
| **Carrera** | Ingeniería en Ciencias de la Computación e Inteligencia Artificial |
| **Materia** | Programación de Computadores II |
| **Código de la materia** | BUC372501B |
| **Evaluación** | Parcial 3 |

---

## 📖 Descripción

El **SGB (Sistema Bibliotecario)** es una aplicación desarrollada en **Python** que permite la gestión integral de una biblioteca. El sistema ofrece funcionalidades para la administración de usuarios, libros, préstamos y generación de reportes, aplicando los principios de la **Programación Orientada a Objetos (POO)** y patrones de diseño. El proyecto está estructurado para ejecutarse en **Google Colab** mediante notebooks **Jupyter (`.ipynb`)**.

---

## 🚀 Funcionalidades

### 👥 Gestión de Usuarios
- Registro de usuarios (Estudiante, Profesor, Administrador).
- Inicio de sesión y autenticación.
- Búsqueda, edición y eliminación de usuarios.

### 📚 Gestión de Libros
- Registro, búsqueda, edición y eliminación de libros.
- Clasificación por categorías.
- Control de estado del libro (disponible, prestado).

### 📦 Gestión de Préstamos
- Registro de préstamos (con validación de disponibilidad).
- Registro de devoluciones.
- Listado de préstamos activos y vencidos.

### 📊 Reportes
- Libros más prestados.
- Usuarios con préstamos vencidos.
- Inventario general.

---

## 🛠️ Tecnologías

- **Lenguaje:** Python
- **Entorno:** Google Colab / Jupyter Notebooks (`.ipynb`)
- **Persistencia:** Archivos de texto (`.txt` / `.csv`)
- **Diagramas UML:** [Herramienta por definir]

---

## 📁 Estructura del Proyecto

```
sgb-sistema-bibliotecaria/
├── src/
│   ├── modelo/           → Clases del dominio (Usuario, Libro, Préstamo, Categoría)
│   ├── controlador/      → Lógica de negocio
│   ├── vista/            → Interfaz de usuario
│   └── utilidades/       → Helpers (lectura/escritura de archivos, etc.)
├── notebooks/            → Notebooks Jupyter (.ipynb) para ejecución en Colab
├── datos/                → Archivos de persistencia
├── docs/                 → Diagramas UML (Clases, Casos de Uso, Secuencia, Actividad)
├── README.md
└── ...
```

---

## 🎯 Patrones de Diseño (Sugeridos)

| Patrón | Uso Propuesto |
|--------|---------------|
| **Singleton** | Clase principal del sistema (`SistemaBibliotecario`) |
| **Observer** | Notificaciones de vencimiento de préstamos |
| **Strategy** | Diferentes algoritmos de búsqueda de libros |
| **Factory** | Creación de distintos tipos de usuarios |

---

## ⚙️ Instalación y Ejecución

> *Las instrucciones exactas se actualizarán una vez definida la configuración final del proyecto.*

### Opción 1: Google Colab
1. Subir los notebooks a Google Colab.
2. Subir los archivos de datos a Colab si es necesario.
3. Ejecutar las celdas en orden.

### Opción 2: Local
```bash
# Instalar dependencias
pip install jupyter

# Ejecutar Jupyter Notebook
jupyter notebook notebooks/
```

---

## 📐 Diagramas UML

Los diagramas del proyecto se encuentran en la carpeta `docs/`:

- [ ] Diagrama de Clases
- [ ] Diagrama de Casos de Uso
- [ ] Diagrama de Secuencia
- [ ] Diagrama de Actividad

---

## 📝 Notas

- Este proyecto es una **guía de trabajo en progreso**. La estructura, implementación y funcionalidades finales pueden variar respecto a lo descrito aquí.
- Las validaciones de negocio y las reglas de préstamos se ajustarán a las indicaciones del profesor durante el desarrollo.

---

## 📄 Licencia

Proyecto académico — Universidad de Santander (UDES).
