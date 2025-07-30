import streamlit as st
from datetime import date
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import tempfile
import os
import subprocess
import re

# Konversi DOCX ke PDF
def convert_docx_to_pdf_libreoffice(input_docx_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "libreoffice",  # untuk versi Linux
        # "soffice",  # untuk versi Windows
        "--headless",
        "--convert-to", "pdf",
        input_docx_path,
        "--outdir", output_dir
    ]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        pdf_filename = os.path.basename(input_docx_path).replace(".docx", ".pdf")
        output_pdf_path = os.path.join(output_dir, pdf_filename)
        if not os.path.exists(output_pdf_path):
            raise FileNotFoundError("LibreOffice gagal membuat PDF.")
        return output_pdf_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Gagal konversi PDF: {e.stderr}")
    except FileNotFoundError:
        raise RuntimeError("LibreOffice tidak ditemukan di PATH.")

# Format source changes
def format_src_lines_sorted_grouped(src_text):
    grouped = {'+': [], '-': [], '*': []}
    for line in src_text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r'^([+\-*])(\S.*)', line)
        if match:
            symbol, rest = match.groups()
            formatted_line = f"{symbol} {rest.strip()}"
            grouped[symbol].append(formatted_line)
    ordered_output = []
    for symbol in ['+', '-', '*']:
        if grouped[symbol]:
            ordered_output.append('\n'.join(grouped[symbol]))
    return '\n\n'.join(ordered_output)

# Layout
st.set_page_config(page_title="Delivery Form Generator", layout="centered")
st.title("📄 Delivery Form Generator")

TEMPLATE_PATH = "Delivery-Form.docx"

# Informasi proyek
st.subheader("📌 Informasi Proyek")
project_name = st.text_input("Project Name")
service_name = st.text_input("Service")
no_cr = st.text_input("No. IR/CR")
sub_system = st.text_input("SubSystem")
ref = st.text_input("Reference Trace IR/CR")
impl_date = st.date_input("Date to be Implemented", value=date.today())
description = st.text_area("Short Description", height=100)

# Source
st.subheader("📂 Source Program Delivered")
src = st.text_area("Source (+ added, - deleted, * modified)")
documentation = st.text_area("Documentation Gitlab URL")
src_file = st.text_area("Source File Gitlab URL", height=100)
script = st.text_area("Script Gitlab URL")
formatted_src = format_src_lines_sorted_grouped(src)

# Sequence Diagram
st.subheader("📈 Sequence Diagram")
sequence_diagram = st.file_uploader("Upload Sequence Diagram (jpg/png)", type=["jpg", "jpeg", "png"])

# Langkah Setup Deployment
st.subheader("🚀 Setup Deployment App - Langkah per Langkah")

if "setup_steps" not in st.session_state:
    st.session_state.setup_steps = []

# Tombol tambah & hapus terakhir
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Setup Deploy"):
        st.session_state.setup_steps.append({"text": "", "image": None})
        st.rerun()

# Tampilkan langkah-langkah
for idx, step in enumerate(st.session_state.setup_steps):
    with st.expander(f"Langkah {idx + 1}", expanded=False):
        col_text, col_delete = st.columns([6, 1])
        with col_text:
            step_text = st.text_area(f"Deskripsi Langkah {idx + 1}", key=f"step_text_{idx}", value=step["text"])
            step_image = st.file_uploader(f"Gambar Langkah {idx + 1} (Opsional)", type=["jpg", "jpeg", "png"], key=f"step_img_{idx}")
            st.session_state.setup_steps[idx]["text"] = step_text
            st.session_state.setup_steps[idx]["image"] = step_image
        with col_delete:
            if st.button("🗑️", key=f"delete_step_{idx}"):
                st.session_state.setup_steps.pop(idx)
                st.rerun()

# Langkah Setup Rollback
st.subheader("🚀 Setup Rollback App - Langkah per Langkah")

if "setup_rollback" not in st.session_state:
    st.session_state.setup_rollback = []

# Tombol tambah & hapus terakhir
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Setup Rollback"):
        st.session_state.setup_rollback.append({"text": "", "image": None})
        st.rerun()

# Tampilkan langkah-langkah rollback
for idx, rb in enumerate(st.session_state.setup_rollback):
    with st.expander(f"Langkah {idx + 1}", expanded=False):
        col_text, col_delete = st.columns([6, 1])
        with col_text:
            rb_text = st.text_area(f"Deskripsi Langkah {idx + 1}", key=f"rb_text_{idx}", value=rb["text"])
            rb_image = st.file_uploader(f"Gambar Langkah {idx + 1} (Opsional)", type=["jpg", "jpeg", "png"], key=f"rb_img_{idx}")
            st.session_state.setup_rollback[idx]["text"] = rb_text
            st.session_state.setup_rollback[idx]["image"] = rb_image
        with col_delete:
            if st.button("🗑️", key=f"delete_rb_{idx}"):
                st.session_state.setup_rollback.pop(idx)
                st.rerun()

# SQL Script
st.subheader("📝 SQL Script")
sql_script_name = st.text_input("SQL Script Name")
sql_script = st.text_area("SQL Script")
st.markdown("#### Notes")

if "sql_notes" not in st.session_state:
    st.session_state.sql_notes = []

# Tombol tambah & hapus terakhir
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("➕ Notes"):
        st.session_state.sql_notes.append({"text": ""})
        st.rerun()

# Tampilkan langkah-langkah rollback
for idx, note in enumerate(st.session_state.sql_notes):
    with st.expander(f"Note {idx + 1}", expanded=False):
        col_text, col_delete = st.columns([6, 1])
        with col_text:
            note_text = st.text_area(f"Deskripsi Note {idx + 1}", key=f"note_text_{idx}", value=note["text"])
            st.session_state.sql_notes[idx]["text"] = note_text
        with col_delete:
            if st.button("🗑️", key=f"delete_note_{idx}"):
                st.session_state.sql_notes.pop(idx)
                st.rerun()

# Approval
st.subheader("📝 Delivery Approval")
st.markdown("#### Developer")
dev_name = st.text_input("Nama Developer")
dev_npp = st.text_input("NPP Developer")
st.markdown("#### Manager")
mgr_name = st.text_input("Nama Manager")
mgr_npp = st.text_input("NPP Manager")
st.markdown("#### Dept Head")
dept_head_name = st.text_input("Nama Dept Head")
dept_head_npp = st.text_input("NPP Dept Head")

# Tombol Generate
if st.button("📄 Generate Dokumen"):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_docx = os.path.join(tmpdir, "Delivery_Form.docx")
        doc = DocxTemplate(TEMPLATE_PATH)

        # Render langkah
        step_rendered = []
        for step in st.session_state.setup_steps:
            img = None
            if step["image"]:
                img_path = os.path.join(tmpdir, step["image"].name)
                with open(img_path, "wb") as f:
                    f.write(step["image"].read())
                img = InlineImage(doc, img_path, width=Inches(5))
            step_rendered.append({"text": step["text"], "image": img})
        
        rollback_rendered = []
        for rb in st.session_state.setup_rollback:
            img = None
            if rb["image"]:
                img_path = os.path.join(tmpdir, rb["image"].name)
                with open(img_path, "wb") as f:
                    f.write(rb["image"].read())
                img = InlineImage(doc, img_path, width=Inches(5))
            rollback_rendered.append({"text": rb["text"], "image": img})

        note_rendered = []
        for rb in st.session_state.sql_notes:
            note_rendered.append({"text": note["text"]})

        # Sequence diagram
        seq_img = None
        if sequence_diagram:
            seq_path = os.path.join(tmpdir, sequence_diagram.name)
            with open(seq_path, "wb") as f:
                f.write(sequence_diagram.read())
            seq_img = InlineImage(doc, seq_path, width=Inches(5))

        context = {
            "project_name": project_name,
            "service_name": service_name,
            "no_cr": no_cr,
            "sub_system": sub_system,
            "ref": ref,
            "date": str(impl_date),
            "description": description,
            "src": formatted_src,
            "documentation": documentation,
            "src_file": src_file,
            "script": script,
            "sequence_diagram": seq_img,
            "setup_steps": step_rendered,
            "setup_rollback": rollback_rendered,
            "sql_script_name": sql_script_name,
            "sql_script": sql_script,
            "sql_notes": note_rendered,
            "dev_name": dev_name,
            "dev_npp": dev_npp,
            "mgr_name": mgr_name,
            "mgr_npp": mgr_npp,
            "dept_head_name": dept_head_name,
            "dept_head_npp": dept_head_npp,
        }

        try:
            with st.spinner("📄 Membuat dokumen dan mengonversi ke PDF..."):
                doc.render(context)
                doc.save(output_docx)
                pdf_path = convert_docx_to_pdf_libreoffice(output_docx, tmpdir)
                with open(pdf_path, "rb") as pdf_file:
                    st.success("✅ Dokumen berhasil dibuat!")
                    st.download_button("📄 Download PDF", data=pdf_file, file_name="Delivery-Form.pdf", mime="application/pdf")
        except Exception as e:
            st.error(f"❌ Gagal membuat dokumen: {e}")