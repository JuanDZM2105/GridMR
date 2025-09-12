import streamlit as st
from cliente import submit_job, get_status, get_results

st.set_page_config(page_title="Cliente GridMR", page_icon="🖥️")

st.title("🖥️ Cliente GridMR")
st.write("Sube un archivo de texto, envíalo al Maestro y consulta resultados.")

# --- Subida de archivo ---
uploaded_file = st.file_uploader("Sube un archivo de texto (.txt)", type=["txt"])

if st.button("Enviar Job"):
    if uploaded_file is not None:
        data = uploaded_file.read().decode("utf-8")
        try:
            response = submit_job(data)
            st.session_state["job_id"] = response["job_id"]  # guardamos job_id
            st.success(f"Job enviado ✅ | ID: {st.session_state['job_id']}")
        except Exception as e:
            st.error(f"❌ Error al enviar job: {e}")
    else:
        st.warning("⚠️ Debes subir un archivo .txt")

# --- Consultar estado ---
if "job_id" in st.session_state and st.button("Consultar Estado"):
    try:
        st.json(get_status(st.session_state["job_id"]))
    except Exception as e:
        st.error(f"❌ {e}")

# --- Obtener resultados ---
if "job_id" in st.session_state and st.button("Obtener Resultados"):
    try:
        st.json(get_results(st.session_state["job_id"]))
    except Exception as e:
        st.error(f"❌ {e}")
