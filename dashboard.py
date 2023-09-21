import streamlit as st
import subprocess
from theme import set_custom_theme
import matplotlib.pyplot as plt
import os
import platform
import psutil

# Personaliza el título de la página
st.set_page_config(
    page_title="Galileo | System Dasboard",
    page_icon="✅",  # Ícono opcional para la pestaña del navegador
    layout="wide"   # Diseño de la página (wide o centered)
)

# Configurar el tema personalizado (si es necesario)
set_custom_theme()

# --------[ Información del sistema ]-------------------------------------------

# Función para obtener información del sistema
def obtener_informacion_sistema():
    host = platform.node()
    sistema = platform.system()
    arquitectura = platform.architecture()
    kernel = platform.release()
    release = os.popen("lsb_release -d | cut -f 2").read().strip()
    total_nucleos = psutil.cpu_count(logical=True)  # Contar núcleos lógicos
    total_memoria = psutil.virtual_memory().total / (1024 ** 3)  # Convertir a GB
    uptime = os.popen("uptime -p").read().strip()

    informacion = f"Host: {host}\n"
    informacion += f"Sistema operativo: {sistema}\n"
    informacion += f"Versión: {release}\n"
    informacion += f"Arquitectura: {arquitectura[0]}\n"
    informacion += f"Kernel: {kernel}\n"
    informacion += f"Total de núcleos: {total_nucleos}\n"
    informacion += f"Total de memoria: {total_memoria:.2f} GB\n"
    informacion += f"Tiempo de actividad: {uptime}\n"

    return informacion

# Título y encabezado para la información del sistema
st.title("Información del sistema")
informacion_sistema = obtener_informacion_sistema()

# Mostrar la información del sistema por defecto
st.code(informacion_sistema, language="text")

# --------[ Checkbox para mostrar/ocultar secciones ]---------------------------

# Checkbox para mostrar/ocultar la sección de Uso de CPU
mostrar_cpu = st.sidebar.checkbox("Mostrar Uso de CPU")

# Checkbox para mostrar/ocultar la sección de Uso de memoria
mostrar_memoria = st.sidebar.checkbox("Mostrar Uso de memoria")

# --------[ Sección de Docker PS ]--------------------------------------------

# Checkbox para mostrar/ocultar la sección de Docker PS
mostrar_docker_ps = st.sidebar.checkbox("Mostrar Docker PS")

if mostrar_docker_ps:
    st.title("Docker PS")
    try:
        # Ejecutar el comando "docker ps" y capturar su salida
        resultado = subprocess.check_output(["docker", "ps"], universal_newlines=True, stderr=subprocess.STDOUT)
        
        # Mostrar la salida del comando en un bloque de código
        st.code(resultado, language="text")
    except subprocess.CalledProcessError as e:
        st.error(f"Error al ejecutar 'docker ps': {e.output}")

# --------[ Uso de CPU ]--------------------------------------------------------

if mostrar_cpu:
    # Obtener el uso actual de la CPU
    uso_cpu = psutil.cpu_percent(interval=1, percpu=True)
    
    # Título y encabezado para la sección de Uso de CPU
    st.title("Uso de CPU")
    st.write("Uso de CPU por núcleo:")

    # Crear una gráfica de barras horizontales para cada núcleo
    fig, ax = plt.subplots()
    nucleos = [f"Núcleo {i + 1:02d}" for i in range(len(uso_cpu))]  # Formato de dos dígitos
    ax.barh(nucleos, uso_cpu)
    ax.set_xlabel("Uso de CPU (%)")

    # Personalizar las etiquetas del eje Y
    ax.invert_yaxis()  # Invertir el eje Y para que el núcleo 1 esté en la parte superior

    # Mostrar la gráfica en Streamlit
    st.pyplot(fig)

# --------[ Uso de memoria ]----------------------------------------------------

if mostrar_memoria:
    # Obtener el uso actual de la memoria
    memoria = psutil.virtual_memory()

    # Convertir bytes a GB
    memoria_total_gb = memoria.total / (1024 ** 3)
    memoria_usada_gb = memoria.used / (1024 ** 3)
    memoria_disponible_gb = memoria.available / (1024 ** 3)

    # Título y encabezado para la sección de Uso de memoria
    st.title("Uso de memoria")
    st.write(f"Memoria total: {memoria_total_gb:.2f} GB")
    st.write(f"Memoria usada: {memoria_usada_gb:.2f} GB")
    st.write(f"Memoria disponible: {memoria_disponible_gb:.2f} GB")

    etiquetas = ["Memoria usada", "Memoria disponible", "Memoria total"]
    valores_gb = [memoria_usada_gb, memoria_disponible_gb, memoria_total_gb]

    # Crear un gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(etiquetas, valores_gb, color=['blue', 'green', 'red'])
    ax.set_ylabel("Memoria (GB)")
    ax.set_title("Uso de memoria")

    # Mostrar la gráfica en Streamlit
    st.pyplot(fig)
