import streamlit as st
from cliente import submit_job, get_status, get_results

st.set_page_config(page_title="Cliente GridMR", page_icon="🖥️")

st.title("🖥️ Cliente GridMR")
st.write("Envía un job MapReduce al Maestro y consulta resultados.")

# --- Formulario ---
with st.form("job_form"):
    job_id = st.text_input("Job ID", "wordcount_001")
    data = st.text_area("Datos de entrada", "Hola mundo hola Grid Map Reduce. Mundo distribuido con MapReduce.")
    submitted = st.form_submit_button("Enviar Job")

if submitted:
    try:
        submit_job(job_id, data)
        st.success(f"Job {job_id} enviado correctamente ✅")
    except Exception as e:
        st.error(f"❌ Error al enviar job: {e}")

if st.button("Consultar Estado"):
    try:
        st.json(get_status(job_id))
    except Exception as e:
        st.error(f"❌ {e}")

if st.button("Obtener Resultados"):
    try:
        st.json(get_results(job_id))
    except Exception as e:
        st.error(f"❌ {e}")
