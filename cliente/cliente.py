import requests

MAESTRO_URL = "http://localhost:8000"

def submit_job(data: str, split_size: int, num_reducers: int = 2):
    """
    Envía un job al maestro con funciones map y reduce incluidas.
    El maestro genera el job_id automáticamente.
    """
    job = {
        "map_function": """
def map_fn(line):
    return [(w.lower(), 1) for w in line.split()]
        """,
        "reduce_function": """
def reduce_fn(key, values):
    return (key, sum(values))
        """,
        "split_size": split_size,
        "num_reducers": num_reducers,
        "data": data
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