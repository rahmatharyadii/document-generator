import streamlit as st
from docxtpl import DocxTemplate
import tempfile
import datetime
import os
import subprocess # Added for LibreOffice conversion

# Function to convert DOCX to PDF using LibreOffice
def convert_docx_to_pdf_libreoffice(input_docx_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Construct the command to run LibreOffice in headless mode
    command = [
        "libreoffice", # untuk versi Linux
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
st.set_page_config(page_title="FSD Generator", layout="centered")
st.title("📄 Functional Specification Document Generator")

# Upload template first
# uploaded_template = st.file_uploader("📎 Upload Template Word (.docx) untuk memulai", type="docx")

# if uploaded_template:
#     st.success("✅ Template berhasil diupload. Silakan isi data di bawah ini.")

# Initialize session state for API Specs and Dependencies
if "api_requirements" not in st.session_state:
    st.session_state.api_requirements = []
if "api_specs" not in st.session_state:
    st.session_state.api_specs = []
if "api_dependencies" not in st.session_state:
    st.session_state.api_dependencies = []

st.subheader("1. Informasi Umum")
group = st.text_input("Group")
project_name = st.text_input("Project Name")
service = st.text_input("Service Name")
pic = st.text_input("PIC")
author = st.text_input("Author", value=pic)
date = st.date_input("Date", value=datetime.date.today())
activity = st.text_input("Activity", value="Initial Draft")
purpose = st.text_area("Purpose")
scope = st.text_area("Scope")


st.subheader("2. Requirements")
if st.button("➕ Tambah Service"):
    st.session_state.api_requirements.append({
        "service_name": "",
        "description": "",
        "inputs": "",
        "outputs": "",
        "process": ""
    })

for idx, reqs in enumerate(st.session_state.api_requirements):
    with st.expander(f"API Spec #{idx + 1}", expanded=True):
        st.session_state.api_requirements[idx]["service_name"] = st.text_input(f"Service Name #{idx+1}", value=reqs["service_name"], key=f"svc_{idx}")
        st.session_state.api_requirements[idx]["description"] = st.text_input(f"Description #{idx+1}", value=reqs["description"], key=f"desc_{idx}")
        st.session_state.api_requirements[idx]["inputs"] = st.text_input(f"Inputs #{idx+1}", value=reqs["inputs"], key=f"inp_{idx}")
        st.session_state.api_requirements[idx]["outputs"] = st.text_input(f"Outputs #{idx+1}", value=reqs["outputs"], key=f"out_{idx}")
        st.session_state.api_requirements[idx]["process"] = st.text_area(f"Process #{idx+1}", value=reqs["process"], key=f"proc_{idx}")


st.subheader("3. API Specifications")
if st.button("➕ Tambah API Spec"):
    st.session_state.api_specs.append({
        "service_name_spec": "",
        "http_method": "GET",
        "url_path": "",
        "http_headers": "",
        "http_body": "",
        "raw_request": "",
        "raw_response": "",
        "response_code": []
    })

for idx, spec in enumerate(st.session_state.api_specs):
    with st.expander(f"API Spec #{idx + 1}", expanded=True):
        st.session_state.api_specs[idx]["service_name_spec"] = st.text_input(f"Service Name #{idx+1}", value=spec["service_name_spec"], key=f"name_{idx}")
        st.session_state.api_specs[idx]["http_method"] = st.selectbox(f"HTTP Method #{idx+1}", ["GET", "POST", "PUT", "DELETE"], index=["GET", "POST", "PUT", "DELETE"].index(spec["http_method"] if spec["http_method"] in ["GET", "POST", "PUT", "DELETE"] else "GET"), key=f"method_{idx}")
        st.session_state.api_specs[idx]["url_path"] = st.text_input(f"URL Path #{idx+1}", value=spec["url_path"], key=f"path_{idx}")
        st.session_state.api_specs[idx]["http_headers"] = st.text_area(f"HTTP Headers #{idx+1}", value=spec["http_headers"], key=f"headers_{idx}")
        st.session_state.api_specs[idx]["http_body"] = st.text_area(f"HTTP Body #{idx+1}", value=spec["http_body"], key=f"body_{idx}")
        st.session_state.api_specs[idx]["raw_request"] = st.text_area(f"Raw Request #{idx+1}", value=spec["raw_request"], key=f"req_{idx}")
        st.session_state.api_specs[idx]["raw_response"] = st.text_area(f"Raw Response #{idx+1}", value=spec["raw_response"], key=f"res_{idx}")
        # Tambah field response_code (pakai |)
        raw_codes = st.text_area(f"Response Codes #{idx+1} (pisahkan dengan |)", value=" | ".join(spec.get("response_code", [])), key=f"resp_code_{idx}")
        st.session_state.api_specs[idx]["response_code"] = [x.strip() for x in raw_codes.split("|") if x.strip()]


st.subheader("4. Dependencies per API")
if st.button("➕ Tambah API Dependencies"):
    st.session_state.api_dependencies.append({
        "service_name_dependencies": "",
        "dependencies": []
    })

for idx, dep in enumerate(st.session_state.api_dependencies):
    with st.expander(f"Dependencies for API #{idx + 1}", expanded=True):
        st.session_state.api_dependencies[idx]["service_name_dependencies"] = st.text_input(f"Service Name (Dep) #{idx+1}", value=dep["service_name_dependencies"], key=f"dep_name_{idx}")
        raw = st.text_area(f"Dependencies List (pisahkan dengan | pipe) #{idx+1}", value="|".join(dep["dependencies"]), key=f"dep_list_{idx}")
        parts = [d.strip() for d in raw.split("|") if d.strip()]
        st.session_state.api_dependencies[idx]["dependencies"] = parts

st.subheader("5. Riviewer")
reviewer = st.text_input("Reviewer Name")
nip_riviewer = st.text_input("Riviewer NIP")
status_riviewer = st.text_input("Riviewer Status")

st.subheader("6. Approver")
approver = st.text_input("Approver Name")
nip_approver = st.text_input("Approver NIP")
status_approver = st.text_input("Approver Status")

# Submit button moved to bottom
if st.button("🚀 Generate FSD"):
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
    #     tmp.write(doc.read())
    #     template_path = tmp.name
    #
    # doc = DocxTemplate(template_path)


    doc = DocxTemplate("FSD-Automation.docx")

    context = {
        "group": group,
        "project_name": project_name,
        "service": service,
        "pic": pic,
        "vers": "1.0",
        "date": str(date),
        "author": author,
        "activity": activity,
        "purpose": purpose,
        "scope": scope,
        "api_requirements": st.session_state.api_requirements,
        "api_specs": st.session_state.api_specs,
        "api_dependencies": st.session_state.api_dependencies,
        "reviewer": reviewer,
        "nip_riviewer": nip_riviewer,
        "status_riviewer": status_riviewer,
        "approver": approver,
        "nip_approver": nip_approver,
        "status_approver": status_approver,
    }

    doc.render(context)

    print(context["api_dependencies"])

    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".docx").name
    # output_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name # This will be returned by the function
    doc.save(output_path)

    output_pdf = convert_docx_to_pdf_libreoffice(output_path, tempfile.gettempdir())

    with open(output_pdf, "rb") as f:
        st.success("✅ FSD berhasil dibuat!")
        st.download_button("⬇️ Download FSD", f, file_name="Generated_FSD.pdf")
# else:
#     st.info("📥 Silakan upload file template Word terlebih dahulu untuk mulai mengisi form.")

