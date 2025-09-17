##### Video explicativo: https://eafit-my.sharepoint.com/:v:/g/personal/jmmunozg1_eafit_edu_co/ETGbk0zOKmVImVd0glsTcCkBGTGNrS3PZMkdh3UyNvtfdw?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJPbmVEcml2ZUZvckJ1c2luZXNzIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXciLCJyZWZlcnJhbFZpZXciOiJNeUZpbGVzTGlua0NvcHkifX0&e=UcmkZ7

# GridMR  

![Python](https://img.shields.io/badge/Python-3.10+-blue)  
![Docker](https://img.shields.io/badge/Docker-Enabled-brightgreen)  
![FastAPI](https://img.shields.io/badge/API-FastAPI-green)  

**GridMR** es un sistema de procesamiento distribuido inspirado en el paradigma **MapReduce**, diseñado para operar sobre una red de nodos heterogéneos (nativos o dockerizados) comunicados a través de Internet o una red local.  

Permite que un cliente externo envíe tareas intensivas en datos y cómputo, que luego son planificadas, ejecutadas y consolidadas por un **nodo maestro** con ayuda de múltiples **workers**.  

El proyecto se inspira en los fundamentos de **Hadoop** y **Spark**, pero implementado de manera ligera en **Python** con soporte para **Docker** y **FastAPI**.  

---

## Características  

- Arquitectura **Maestro–Workers**  
- Cliente externo para enviar trabajos  
- Distribución de datos en *splits* para balancear carga  
- Ejecución de funciones **map()** y **reduce()** definidas por el usuario  
- APIs REST para comunicación entre nodos  
- Compatibilidad con despliegue en **Docker**  
- Caso de uso implementado: **Conteo de palabras**  

---

## Estructura del proyecto  

```bash
GridMR/  
│── cliente/ # Cliente que envía los trabajos al maestro  
│── maestro/ # Nodo maestro: planificación y coordinación  
│── workers/  
│ ├── map_worker.py # Workers que ejecutan las tareas Map  
│ └── reduce_worker.py # Workers que ejecutan las tareas Reduce  
│── docker-compose.yml  
│── requirements.txt  
│── README.md  
```

---

## Requisitos  

- **Python 3.10+**  
- **Docker** y **Docker Compose**  
- Librerías de Python:  
  - `fastapi`  
  - `uvicorn`  
  - `requests`  
  - `pydantic`
  - `streamlit`

## ▶ Instalación y ejecución  

### 1. Clonar el repositorio  
```bash
git clone https://github.com/JuanDZM2105/GridMR.git
```
Navegar hasta la carpeta raíz del proyecto
```bash
cd GridMR
```
### 2. Levantar la infraestructura con Docker
```bash
docker-compose up --build
```
Esto creara contenedores para:
- Maestro
- Map Workers
- Reduce Workers

### 3. Instalar dependencias de cliente:
En la carpeta ráiz del proyecto:
```bash
cd cliente
```
Luego, ejecutar el siguiente comando
```bash
pip install -r requirements.txt
```
-> Tanto el maestro como los workers tienen su propio requirements.txt, sin embargo, al estar empaquetados en docker no es necesario instalar estas dependencias.
En caso de que se quiera instalar las dependencias para los componentes mencionados, es necesario navegar hasta sus respectivas carpetas (cd maestro o cd workers) y ejecutar el comando.

### 4. Enviar un job desde el cliente con interfaz (Streamlit)  

El cliente cuenta con una interfaz en **Streamlit** para enviar los trabajos de manera interactiva.  

Para levantar el cliente:  

Navega hasta la carpeta
```bash
cd cliente
```
Luego, ejecuta el servidor local con:
```bash
streamlit run cliente_ui.py
```
Esto abrirá automáticamente una interfaz web en tu navegador (por defecto en http://localhost:8501).  
Desde allí podrá:  
- Seleccionar el archivo de entrada (.txt)
- Configurar parámetros como split_size y reducers
- Enviar el trabajo al maestro
- Obtener el estado del job
- Obtener el resultado del job

## Flujo del sistema

1. Cliente → Maestro: envío del trabajo (archivo + parámetros)
2. Maestro → Workers Map: distribución de splits
3. Workers Map → Maestro: resultados intermedios
4. Maestro → Workers Reduce: asignación de resultados intermedios
5. Workers Reduce → Maestro: resultados finales consolidados
6. Maestro → Cliente: entrega de salida

## Caso de uso implementado: Conteo de palabras

Entrada: archivo de texto.
Salida: lista de palabras con sus frecuencias.

```bash
Input:
"hola mundo hola Alvaro"

Output:
{"hola": 2, "mundo": 1, "Alvaro": 1}
```
## Referencias  

- [MapReduce: Simplified Data Processing on Large Clusters](https://storage.googleapis.com/gweb-research2023-media/pubtools/4449.pdf) – Dean & Ghemawat (Google)  
- [Spark: Cluster Computing with Working Sets](http://people.csail.mit.edu/matei/papers/2010/hotcloud_spark.pdf) – Zaharia et al.  
- [Apache Hadoop](https://hadoop.apache.org)  
- [Apache Spark](https://spark.apache.org)  

## Autores

Juan David Zapata Moncada (jdzapatam@eafit.edu.co)  
Juan Miguel Muñoz García (jmmunozg1@eafit.edu.co)

