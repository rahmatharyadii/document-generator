import streamlit as st
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
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
if "flow_diagram" not in st.session_state:
    st.session_state.flow_diagram = []

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

# Tombol tambah flow diagram baru
if st.button("➕ Tambah Flow Diagram"):
    st.session_state.flow_diagram.append({
        "diagram_name": "",
        "pictures": []  # list untuk menyimpan beberapa gambar
    })

# Loop tiap flow diagram untuk input detailnya
for idx, flow in enumerate(st.session_state.flow_diagram):
    with st.expander(f"Flow Diagram #{idx + 1}", expanded=True):
        # Input nama diagram
        st.session_state.flow_diagram[idx]["diagram_name"] = st.text_input(
            f"Diagram Name #{idx + 1}",
            value=flow["diagram_name"],
            key=f"diagram_name_{idx}"
        )

        # Input gambar, bisa upload lebih dari 1 (gunakan file_uploader dengan accept_multiple_files=True)
        uploaded_files = st.file_uploader(
            f"Upload Images for Diagram #{idx + 1} (multiple allowed)",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
            key=f"upload_images_{idx}"
        )

        # Jika ada file baru yang diupload, tambahkan ke list pictures
        if uploaded_files:
            # Agar tidak hilang upload lama, gabungkan dengan gambar lama
            existing_pictures = st.session_state.flow_diagram[idx].get("pictures", [])
            # Simpan file dalam memori, misal dalam list berisi bytes dan nama file
            for file in uploaded_files:
                # Cek apakah file sudah ada berdasarkan nama, supaya gak duplikat
                if file.name not in [pic["name"] for pic in existing_pictures]:
                    existing_pictures.append({
                        "name": file.name,
                        "data": file.read()
                    })
            st.session_state.flow_diagram[idx]["pictures"] = existing_pictures

        # Tampilkan thumbnail gambar yang sudah diupload
        pictures = st.session_state.flow_diagram[idx].get("pictures", [])
        if pictures:
            st.write("Uploaded Images:")
            for pic in pictures:
                st.image(pic["data"], caption=pic["name"], width=150)

        # Tambahkan tombol untuk menghapus flow diagram jika perlu
        if st.button(f"🗑️ Hapus Flow Diagram #{idx + 1}", key=f"del_flow_{idx}"):
            st.session_state.flow_diagram.pop(idx)
            st.experimental_rerun()

st.subheader("3. Technical Stack")
software = st.text_input("Software")
database = st.text_input("Database")
caching = st.text_input("Caching")
logging = st.text_input("Logging")

st.subheader("5. Deployment Environtment")
environment = st.text_input("Environment")
configuration = st.text_input("Configuration")
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

    flow_diagram_context = []
    for flow in st.session_state.flow_diagram:
        pictures = []
        for pic in flow["pictures"]:
            # Simpan gambar ke file temporer supaya bisa dibaca InlineImage
            temp_img_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_img_file.write(pic["data"])
            temp_img_file.flush()
            temp_img_file.close()

            img = InlineImage(doc, temp_img_file.name, width=Mm(80))  # ukuran gambar 80 mm
            pictures.append(img)

        flow_diagram_context.append({
            "diagram_name": flow["diagram_name"],
            "pictures": pictures
        })

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
        "approval_nip": approval_nip,
        "flow_diagram": flow_diagram_context,
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