import requests

MAESTRO_URL = "http://localhost:8000"

def submit_job(job_id: str, filepath: str):
    """
    Envía un job al maestro leyendo un archivo de texto completo.
    """
    # 👉 Leer archivo .txt y pasarlo como string
    with open(filepath, "r", encoding="utf-8") as f:
        data = f.read()

    job = {
        "job_id": job_id,
        "map_function": """
def map_fn(line):
    return [(w.lower(), 1) for w in line.split()]
        """,
        "reduce_function": """
def reduce_fn(key, values):
    return (key, sum(values))
        """,
        "split_size": 100,
        "num_reducers": 2,
        "data": data   # <- aquí va el contenido del archivo
    }

    r = requests.post(f"{MAESTRO_URL}/submit_job", json=job)
    r.raise_for_status()
    return r.json()

def get_status(job_id: str):
    """
    Consulta el estado del job en el maestro.
    """
    r = requests.get(f"{MAESTRO_URL}/job_status/{job_id}")
    r.raise_for_status()
    return r.json()

def get_results(job_id: str):
    """
    Descarga los resultados de un job terminado.
    """
    r = requests.get(f"{MAESTRO_URL}/job_result/{job_id}")
    r.raise_for_status()
    return r.json()
