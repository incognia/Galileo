import streamlit as st
import subprocess
from theme import set_custom_theme
import matplotlib.pyplot as plt
import os
import platform
import psutil

# Personaliza el título de la página y el diseño de la página
st.set_page_config(
    page_title="Galileo | System Dashboard",
    page_icon="📊",  # Ícono opcional para la pestaña del navegador
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

# Checkbox para mostrar/ocultar la sección de contenedores Docker
mostrar_docker = st.sidebar.checkbox("Contenedores Docker")

# Agregar separador al sidebar
st.sidebar.markdown("---")  # Separador visual

# Checkbox para mostrar/ocultar la sección de Uso de CPU
mostrar_cpu = st.sidebar.checkbox("Uso de CPU")

# Checkbox para mostrar/ocultar la sección de Uso de RAM
mostrar_ram = st.sidebar.checkbox("Uso de RAM")

# Checkbox para mostrar/ocultar la sección de Uso de HDD
mostrar_hdd = st.sidebar.checkbox("Uso de HDD")

# Agregar separador al sidebar
st.sidebar.markdown("---")  # Separador visual

# Checkbox para mostrar/ocultar la sección de procesos por uso de CPU
mostrar_proc_cpu = st.sidebar.checkbox("Procesos x CPU (%)")

# Checkbox para mostrar/ocultar la sección de procesos por uso de RAM
mostrar_proc_ram = st.sidebar.checkbox("Procesos x RAM (MB)")

# Checkbox para mostrar/ocultar la sección de procesos por uso de HDD
mostrar_proc_hdd = st.sidebar.checkbox("Procesos x HDD (MB)")

# --------[ Sección de contenedores Docker ]------------------------------------

if mostrar_docker:
    st.title("Contenedores Docker")
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

if mostrar_proc_cpu:
    # Título de la sección
    st.title("Procesos por uso de CPU (%)")

    # Obtener la lista de procesos y ordenarla por uso de CPU en orden descendente
    procesos = sorted(psutil.process_iter(attrs=['pid', 'name', 'cpu_percent']), key=lambda x: x.info['cpu_percent'], reverse=True)

    # Crear una lista de diccionarios con información de procesos
    data = []
    for proceso in procesos[:16]:
        pid = proceso.info['pid']
        nombre = proceso.info['name']
        uso_cpu = proceso.info['cpu_percent']
        data.append({"PID": pid, "Nombre": nombre, "Uso de CPU (%)": uso_cpu})

    # Mostrar los datos en una tabla
    st.table(data)

# --------[ Uso de RAM ]--------------------------------------------------------

if mostrar_ram:
    # Obtener el uso actual de la RAM
    memoria = psutil.virtual_memory()

    # Convertir bytes a GB
    memoria_total_gb = memoria.total / (1024 ** 3)
    memoria_usada_gb = memoria.used / (1024 ** 3)
    memoria_disponible_gb = memoria.available / (1024 ** 3)

    # Título y encabezado para la sección de Uso de RAM
    st.title("Uso de RAM")
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

if mostrar_proc_ram:
    # Título de la sección
    st.title("Procesos por uso de RAM (MB)")

    # Obtener la lista de procesos y ordenarla por uso de memoria
    procesos = sorted(psutil.process_iter(attrs=['pid', 'name', 'memory_info']), key=lambda x: x.info['memory_info'].rss, reverse=True)

    # Crear una lista de diccionarios con información de procesos
    data = []
    for proceso in procesos[:16]:
        pid = proceso.info['pid']
        nombre = proceso.info['name']
        memoria_mb = proceso.info['memory_info'].rss / (1024 * 1024)  # Convertir bytes a MB
        data.append({"PID": pid, "Nombre": nombre, "Uso de RAM (MB)": memoria_mb})

    # Mostrar los datos en una tabla
    st.table(data)

# --------[ Uso de HDD ]--------------------------------------------------------

if mostrar_hdd:
    # Obtener el uso actual del HDD
    uso_hdd = psutil.disk_usage('/')

    hdd_total_gb = uso_hdd.total / (1024** 3)
    hdd_usado_gb = uso_hdd.used / (1024 ** 3)
    hdd_disponible_gb = uso_hdd.free / (1024 ** 3)
    hdd_porcentaje = uso_hdd.percent

    st.title("Uso de HDD")
    st.write(f"HDD total: {hdd_total_gb:.2f} GB")
    st.write(f"HDD usado: {hdd_usado_gb:.2f} GB")
    st.write(f"HDD disponible: {hdd_disponible_gb:.2f} GB")
    st.write(f"HDD porcentaje de uso: {hdd_porcentaje:.2f} %")

if mostrar_proc_hdd:
    # Título de la sección
    st.title("Procesos por uso de HDD (MB)")

    # Obtener la lista de procesos y ordenarla por uso de disco duro (almacenamiento)
    procesos = sorted(psutil.process_iter(attrs=['pid', 'name', 'memory_info', 'io_counters']), key=lambda x: getattr(x.info.get('io_counters', None), 'write_bytes', 0), reverse=True)

    # Crear una lista de diccionarios con información de procesos
    data = []
    for proceso in procesos[:16]:
        pid = proceso.info['pid']
        nombre = proceso.info['name']
        io_info = proceso.info.get('io_counters', None)
        disco_mb = getattr(io_info, 'write_bytes', 0) / (1024 * 1024) if io_info else 0  # Convertir bytes a MB si la info de I/O está presente
        data.append({"PID": pid, "Nombre": nombre, "Uso de Disco Duro (MB)": disco_mb})

    # Mostrar los datos en una tabla
    st.table(data)
