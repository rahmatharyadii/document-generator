import streamlit as st
from datetime import date
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
import tempfile
import os
import subprocess
import re


def convert_docx_to_pdf_libreoffice(input_docx_path: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "libreoffice", # untuk versi Linux
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
        raise RuntimeError(f"Gagal konversi PDF: {e.stderr}") from e
    except FileNotFoundError:
        raise RuntimeError("LibreOffice tidak ditemukan di PATH.")


def format_src_lines_sorted_grouped(src_text: str) -> str:
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


def main() -> None:
    # Page configuration
    st.set_page_config(
        page_title="Delivery Form Generator",
        page_icon="📄",
        layout="wide",
    )
    st.title("📄 Delivery Form Generator")

    # Template path – update this if your template lives elsewhere
    TEMPLATE_PATH = "Delivery-Form.docx"

    # Initialise session state variables
    if "impl_date" not in st.session_state:
        st.session_state.impl_date = None
    if "dev_notes" not in st.session_state:
        st.session_state.dev_notes = []
    if "setup_steps" not in st.session_state:
        st.session_state.setup_steps = []
    if "setup_rollback" not in st.session_state:
        st.session_state.setup_rollback = []
    if "sql_notes" not in st.session_state:
        st.session_state.sql_notes = []
    if "sequence_diagram" not in st.session_state:
        st.session_state.sequence_diagram = None

    # Informasi Proyek
    st.subheader("📌 Informasi Proyek")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            project_name = st.text_input("Project Name")
            service_name = st.text_input("Service")
            no_cr = st.text_input("No. IR/CR")
        with col2:
            sub_system = st.text_input("SubSystem")
            ref = st.text_input("Reference Trace IR/CR")
            impl_date_input = st.date_input(
                "Date to be Implemented",
                value=st.session_state.impl_date or date.today(),
                format="YYYY-MM-DD",
                help="Tanggal implementasi.",
            )
            st.session_state.impl_date = impl_date_input
        description = st.text_area("Short Description", height=80)

    st.markdown("---")

    # Source Program Delivered
    with st.expander("📂 Source Program Delivered", expanded=False):
        st.markdown("Masukkan informasi sumber program yang dikirimkan.")
        src = st.text_area(
            "Source (+ added, - deleted, * modified)",
            placeholder="Contoh: + file1.py\n- file2.py\n* file3.py",
        )
        formatted_src = format_src_lines_sorted_grouped(src)
        documentation = st.text_area("Documentation Gitlab URL")
        src_file = st.text_area("Source File Gitlab URL", height=80)
        script = st.text_area("Script Gitlab URL")
        # Display formatted source as a code block when available
        if formatted_src:
            with st.expander("Lihat Source Terformat", expanded=False):
                st.code(formatted_src)

    st.markdown("---")

    # Sequence Diagram section
    with st.expander("📈 Sequence Diagram", expanded=False):
        st.markdown("Unggah diagram urutan (opsional). Format yang didukung: JPG, JPEG, PNG.")
        sequence_diagram = st.file_uploader(
            "Upload Sequence Diagram",
            type=["jpg", "jpeg", "png"],
        )

    st.markdown("---")

    # Notes / Special Instruction
    with st.expander("📝 Notes / Special Instruction", expanded=False):
        st.markdown("Tambahkan catatan atau instruksi khusus.")
        add_note_col, _ = st.columns([1, 5])
        if add_note_col.button("➕ Add Note", key="add_dev_note"):
            st.session_state.dev_notes.append({"text": ""})
            st.rerun()
        # Display existing notes
        for idx, devnote in enumerate(st.session_state.dev_notes):
            with st.expander(f"Note {idx + 1}", expanded=False):
                col_text, col_delete = st.columns([6, 1])
                with col_text:
                    note_text = st.text_area(
                        f"Deskripsi Note {idx + 1}",
                        key=f"devnote_text_{idx}",
                        value=devnote.get("text", ""),
                    )
                    st.session_state.dev_notes[idx]["text"] = note_text
                with col_delete:
                    if st.button("🗑️", key=f"delete_devnote_{idx}"):
                        st.session_state.dev_notes.pop(idx)
                        st.rerun()

    st.markdown("---")

    # Setup Deployment section
    with st.expander("🚀 Setup Deployment App - Langkah per Langkah", expanded=False):
        st.markdown("Tambahkan langkah-langkah deploy.")
        add_step_col, _ = st.columns([1, 5])
        if add_step_col.button("➕ Add Deploy Step", key="add_setup_step"):
            st.session_state.setup_steps.append({"text": "", "image": None})
            st.rerun()
        for idx, step in enumerate(st.session_state.setup_steps):
            with st.expander(f"Langkah {idx + 1}", expanded=False):
                col_text, col_delete = st.columns([6, 1])
                with col_text:
                    step_text = st.text_area(
                        f"Deskripsi Langkah {idx + 1}",
                        key=f"step_text_{idx}",
                        value=step.get("text", ""),
                    )
                    step_image = st.file_uploader(
                        f"Gambar Langkah {idx + 1} (opsional)",
                        type=["jpg", "jpeg", "png"],
                        key=f"step_img_{idx}",
                    )
                    st.session_state.setup_steps[idx]["text"] = step_text
                    st.session_state.setup_steps[idx]["image"] = step_image
                with col_delete:
                    if st.button("🗑️", key=f"delete_step_{idx}"):
                        st.session_state.setup_steps.pop(idx)
                        st.rerun()

    st.markdown("---")

    # Setup Rollback section
    with st.expander("🚀 Setup Rollback App - Langkah per Langkah", expanded=False):
        st.markdown("Tambahkan langkah-langkah rollback.")
        add_rb_col, _ = st.columns([1, 5])
        if add_rb_col.button("➕ Add Rollback Step", key="add_setup_rollback"):
            st.session_state.setup_rollback.append({"text": "", "image": None})
            st.rerun()
        for idx, rb in enumerate(st.session_state.setup_rollback):
            with st.expander(f"Langkah {idx + 1}", expanded=False):
                col_text, col_delete = st.columns([6, 1])
                with col_text:
                    rb_text = st.text_area(
                        f"Deskripsi Langkah {idx + 1}",
                        key=f"rb_text_{idx}",
                        value=rb.get("text", ""),
                    )
                    rb_image = st.file_uploader(
                        f"Gambar Langkah {idx + 1} (opsional)",
                        type=["jpg", "jpeg", "png"],
                        key=f"rb_img_{idx}",
                    )
                    st.session_state.setup_rollback[idx]["text"] = rb_text
                    st.session_state.setup_rollback[idx]["image"] = rb_image
                with col_delete:
                    if st.button("🗑️", key=f"delete_rb_{idx}"):
                        st.session_state.setup_rollback.pop(idx)
                        st.rerun()

    st.markdown("---")

    # SQL Script section
    with st.expander("🧾 SQL Script", expanded=False):
        sql_script_name = st.text_input("SQL Script Name")
        sql_script = st.text_area("SQL Script", height=120)
        st.markdown("#### Notes")
        add_sql_note_col, _ = st.columns([1, 5])
        if add_sql_note_col.button("➕ Add SQL Note", key="add_sql_note"):
            st.session_state.sql_notes.append({"text": ""})
            st.rerun()
        for idx, note in enumerate(st.session_state.sql_notes):
            with st.expander(f"Note {idx + 1}", expanded=False):
                col_text, col_delete = st.columns([6, 1])
                with col_text:
                    note_text = st.text_area(
                        f"Deskripsi Note {idx + 1}",
                        key=f"note_text_{idx}",
                        value=note.get("text", ""),
                    )
                    st.session_state.sql_notes[idx]["text"] = note_text
                with col_delete:
                    if st.button("🗑️", key=f"delete_note_{idx}"):
                        st.session_state.sql_notes.pop(idx)
                        st.rerun()

    st.markdown("---")

    # Approval section
    with st.expander("✔️ Delivery Approval", expanded=False):
        st.markdown("Masukkan informasi persetujuan dari tim.")
        with st.expander("IT Developer", expanded=False):
            dev_name = st.text_input("Name Developer")
            dev_npp = st.text_input("NPP Developer")
        with st.expander("IT Developer (MGR)", expanded=False):
            mgr_name = st.text_input("Name Manager")
            mgr_npp = st.text_input("NPP Manager")
        with st.expander("Dept Head", expanded=False):
            dept_head_name = st.text_input("Name Dept Head")
            dept_head_npp = st.text_input("NPP Dept Head")

    # Generate document button
    st.markdown("---")
    if st.button("📄 Generate Dokumen"):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_docx = os.path.join(tmpdir, "Delivery_Form.docx")
            doc = DocxTemplate(TEMPLATE_PATH)

            # Render deploy steps
            step_rendered: list[dict[str, object]] = []
            for step in st.session_state.setup_steps:
                img = None
                if step.get("image"):
                    img_path = os.path.join(tmpdir, step["image"].name)
                    with open(img_path, "wb") as f:
                        f.write(step["image"].read())
                    img = InlineImage(doc, img_path, width=Inches(5))
                step_rendered.append({"text": step.get("text", ""), "image": img})

            # Render rollback steps
            rollback_rendered: list[dict[str, object]] = []
            for rb in st.session_state.setup_rollback:
                img = None
                if rb.get("image"):
                    img_path = os.path.join(tmpdir, rb["image"].name)
                    with open(img_path, "wb") as f:
                        f.write(rb["image"].read())
                    img = InlineImage(doc, img_path, width=Inches(5))
                rollback_rendered.append({"text": rb.get("text", ""), "image": img})

            # Render SQL notes
            note_rendered: list[dict[str, str]] = []
            for note in st.session_state.sql_notes:
                note_rendered.append({"text": note.get("text", "")})

            # Render dev notes
            devnote_rendered: list[dict[str, str]] = []
            for devnote in st.session_state.dev_notes:
                devnote_rendered.append({"text": devnote.get("text", "")})

            # Sequence diagram image
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
                "date": str(st.session_state.impl_date) if st.session_state.impl_date else "",
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
                "dev_notes": devnote_rendered,
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
                        st.download_button(
                            "📥 Download PDF",
                            data=pdf_file,
                            file_name="Delivery-Form.pdf",
                            mime="application/pdf",
                        )
            except Exception as e:
                st.error(f"❌ Gagal membuat dokumen: {e}")


if __name__ == "__main__":
    main()