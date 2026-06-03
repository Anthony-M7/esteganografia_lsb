# 🕵️‍♂️ Laboratorio Visual: Esteganografía LSB

Una aplicación web educativa desarrollada en Flask para demostrar de forma interactiva cómo funciona la **Esteganografía digital** mediante el método de sustitución del Bit Menos Significativo (LSB). 

Este proyecto permite ocultar mensajes de texto dentro de imágenes (PNG/BMP) y revelarlos posteriormente, mostrando en tiempo real un registro detallado de cómo se alteran los bits de los píxeles durante el proceso.

## ✨ Características Principales
* **Ocultar Mensajes:** Inyecta texto secreto en imágenes sin alterar su apariencia visual.
* **Revelar Mensajes:** Extrae mensajes ocultos de imágenes esteganográficas.
* **Protección Anti-Compresión:** Detecta imágenes JPEG y fuerza la salida a PNG para evitar la pérdida de datos.
* **Log Didáctico a Nivel de Bits:** Muestra una consola visual detallando los cambios matemáticos exactos en los primeros píxeles procesados.
* **Revelado en Tiempo Real:** Permite verificar el mensaje recién oculto sin necesidad de descargar y volver a subir la imagen.

---

## 🛠️ Requisitos Previos

Para ejecutar este proyecto en tu entorno local, necesitarás tener instalado:
* **Python 3.7** o superior.
* **pip** (Gestor de paquetes de Python).

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para clonar y levantar el servidor localmente:

**1. Clonar el repositorio**
Abre tu terminal y ejecuta:
```bash
git clone https://github.com/Anthony-M7/esteganografia_lsb.git
cd esteganografia_lsb
