import streamlit as st
from docxtpl import DocxTemplate
import tempfile
import datetime
import os
import subprocess  # Added for LibreOffice conversion

# Function to convert DOCX to PDF using LibreOffice
def convert_docx_to_pdf_libreoffice(input_docx_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the command to run LibreOffice in headless mode
    command = [
        "libreoffice",  # untuk versi Linux
        # "soffice",  # untuk versi Windows
        "--headless",
        "--convert-to", "pdf",
        input_docx_path,
        "--outdir", output_dir
    ]

    try:
        # Execute the command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"LibreOffice conversion stdout: {result.stdout}")
        if result.stderr:
            print(f"LibreOffice conversion stderr: {result.stderr}")

        # The output PDF will be in output_dir with the same base name as the DOCX
        pdf_filename = os.path.basename(input_docx_path).replace(".docx", ".pdf")
        output_pdf_path = os.path.join(output_dir, pdf_filename)

        if not os.path.exists(output_pdf_path):
            raise FileNotFoundError(f"LibreOffice did not produce the expected PDF at {output_pdf_path}")

        return output_pdf_path
    except subprocess.CalledProcessError as e:
        print(f"Error during LibreOffice conversion: {e.stderr}")
        raise RuntimeError(f"PDF conversion failed: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("LibreOffice command not found. Make sure LibreOffice is installed and in your PATH.")


# App title and setup
st.set_page_config(page_title="TSD Generator", layout="centered")
st.title("📄 Functional Specification Document Generator")

# Initialize session state for API Specs and Dependencies
# if "api_requirements" not in st.session_state:
#     st.session_state.api_requirements = []
# if "api_specs" not in st.session_state:
#     st.session_state.api_specs = []
# if "api_dependencies" not in st.session_state:
#     st.session_state.api_dependencies = []


st.subheader("Informasi Umum")
group = st.text_input("Group")
project_name = st.text_input("Project Name")
date = st.date_input("Date", value=datetime.date.today())

st.subheader("1. Introduction")
purpose = st.text_input("Purpose")
scope = st.text_input("Scope")
impact_analysis = st.text_input("Impact Analysis")

st.subheader("2. System Architecture")
overview = st.text_input("Overview")

st.subheader("3. Technical Stack")
software = st.text_input("Software")
database =st.text_input("Database")
caching = st.text_input("Caching")
logging = st.text_input("Logging")

st.subheader("5. Deployment Environtment")
environment = st.text_input("Environment")
configuration  = st.text_input("Configuration")
deployment_proccess = st.text_input("Deployment Proccess")

st.subheader("6. Delivery Approval")
with st.expander("IT Developer", expanded=True):
    dev_name = st.text_input("Name")
    dev_nip = st.text_input("NIP")
with st.expander("MGR Developer", expanded=True):
    mgr_name = st.text_input("Name1")
    mgr_nip = st.text_input("NIP1")
with st.expander("Approval", expanded=True):
    approval_name = st.text_input("Name2")
    approval_nip = st.text_input("NIP2")

# Submit button moved to bottom
if st.button("🚀 Generate TSD"):
    doc = DocxTemplate("TSD-Automation.docx")

    context = {
        "group": group,
        "project_name": project_name,
        "date": str(date),
        "purpose": purpose,
        "scope": scope,
        "impact_analysis": impact_analysis,
        "overview": overview,
        "software": software,
        "database": database,
        "caching": caching,
        "logging": logging,
        "environment": environment,
        "configuration": configuration,
        "deployment_proccess": deployment_proccess,
        "dev_name": dev_name,
        "dev_nip": dev_nip,
        "mgr_name": mgr_name,
        "mgr_nip": mgr_nip,
        "approval_name": approval_name,
        "approval_nip": approval_nip
    }

    doc.render(context)

    # print(context["api_dependencies"])

    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
    # output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name # This will be returned by the function
    doc.save(output_path)

    output_pdf = convert_docx_to_pdf_libreoffice(output_path, tempfile.gettempdir())

    with open(output_pdf, "rb") as f:
        st.success("✅ TSD berhasil dibuat!")
        st.download_button("⬇️ Download TSD", f, file_name="Generated_TSD.pdf")