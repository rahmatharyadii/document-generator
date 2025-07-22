import streamlit as st
import re
import json
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from datetime import datetime, date as date_class
import tempfile
import os
import subprocess  # Added for LibreOffice conversion
from urllib.parse import urlparse


# Function to convert DOCX to PDF using LibreOffice
def convert_docx_to_pdf_libreoffice(input_docx_path, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Construct the command to run LibreOffice in headless mode
    command = [
        # "libreoffice", # untuk versi Linux
        "soffice",  # untuk versi Windows
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


st.title("🧪 Unit Test Document Generator")

# --- Upload file JSON ---
uploaded_file = st.file_uploader("Upload hasil console log Postman (result_json.txt)", type=["txt"])

if uploaded_file:
    raw = uploaded_file.read().decode("utf-8", errors="replace")  # handle karakter tidak valid

    # --- Temukan blok API ---
    api_blocks = re.findall(
        r"(GET|POST|PUT|DELETE)\s+(http[^\s]+):\s+\{(.*?\"Response Body\"\s*:\s*\"(?:[^\"\\]|\\.)*\")\s*\}",
        raw, re.DOTALL
    )

    with st.form("form_info"):
        st.subheader("🔧 Informasi Umum")
        group = st.text_input("Group")  # Monitoring & Notification Services Delivery
        title = st.text_input("Judul Pengujian")  # Seri Redeem API Test
        date_input = st.date_input("Date", value=date_class.today())
        description = st.text_area("Deskripsi")  # Pengujian API terhadap endpoint seriRedeemId
        image_file = st.file_uploader("Upload gambar Sequence Diagram", type=["png", "jpg", "jpeg"])

        st.subheader("📝 Judul Test Case per API")
        test_case_titles = []
        test_case_logs = []
        for i, (method, url, _) in enumerate(api_blocks, start=1):
            parsed_url = urlparse(url)
            endpoint_only = parsed_url.path
            st.markdown(f"#### Test Case {i}: {method} {endpoint_only}")
            test_case_title = st.text_input("Judul Test Case", key=f"test_case_title_{i}")
            test_case_log = st.text_area("Log Pengujian (manual)", key=f"test_case_log_{i}")
            test_case_titles.append(test_case_title)
            test_case_logs.append(test_case_log)

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

        submitted = st.form_submit_button("Generate Dokumen")

    if submitted:
        # --- Format tanggal ---
        bulan_indo = {
            1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
            5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
            9: "September", 10: "Oktober", 11: "November", 12: "Desember"
        }
        tanggal_indo = f"{date_input.day} {bulan_indo[date_input.month]} {date_input.year}"

        test_case_data = []

        for i, (method, url, body_block) in enumerate(api_blocks, start=1):
            headers_match = re.search(r'"Request Headers"\s*:\s*\{(.*?)\}', body_block, re.DOTALL)
            req_match = re.search(r'"Request Body"\s*:\s*"((?:[^"\\]|\\.)*)"', body_block)

            curl_lines = [f'curl -X {method} "{url}"']

            # Add headers if found
            if headers_match:
                headers_raw = headers_match.group(1)
                try:
                    headers_dict = json.loads("{" + headers_raw + "}")
                    for key, value in headers_dict.items():
                        curl_lines.append(f'  -H "{key}: {value}"')
                except Exception as e:
                    curl_lines.append(f'  # Failed to parse headers: {e}')

            # Add body if found
            if req_match:
                try:
                    req_str = req_match.group(1).encode().decode("unicode_escape")
                    req_json = json.loads(req_str)
                    request_body_str = json.dumps(req_json, ensure_ascii=False)
                    curl_lines.append(f"  -d '{request_body_str}'")
                except Exception as e:
                    curl_lines.append(f'  # Failed to parse body: {e}')

            # If only 1 line (curl) = no headers/body found
            if len(curl_lines) == 1:
                request_body = "[no Request Body or Headers found]"
            else:
                request_body = "\n".join(curl_lines)

            res_match = re.search(r'"Response Body"\s*:\s*"((?:[^"\\]|\\.)*)"', body_block)
            if res_match:
                try:
                    res_body_clean = res_match.group(1).encode().decode("unicode_escape")
                    res_json = json.loads(res_body_clean)
                    response_body = json.dumps(res_json, indent=2, ensure_ascii=False).strip()
                except Exception as e:
                    res_json = {}
                    response_body = f"[decode failed: {e}]"
            else:
                res_json = {}
                response_body = "[not found]"

            status = res_json.get("status", "Unknown")
            status_code = res_json.get("statusCode", res_json.get("code", "N/A"))
            message = res_json.get("message", "No message")

            test_case_data.append({
                "loop_index": f"{i:02d}",
                "test_condition": "Normal" if str(status_code) in ["200", "00"] else "Abnormal",
                "test_case": test_case_titles[i - 1] if i - 1 < len(test_case_titles) else f"{method} {url}",
                "request_body": request_body,
                "response_body": response_body,
                "log": test_case_logs[i - 1] if i - 1 < len(
                    test_case_logs) else f"Status: {status}, Code: {status_code}, Message: {message}"
            })

        # --- Buat dokumen sementara ---
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, "API_Test_Report.docx")
            # pdf_path = os.path.join(tmpdir, "API_Test_Report.pdf") # This will be returned by the function
            template_path = "Test-Automation.docx"  # pastikan file ini ada

            doc = DocxTemplate(template_path)

            if image_file:
                image_path = os.path.join(tmpdir, image_file.name)
                with open(image_path, "wb") as f:
                    f.write(image_file.read())
                sequence_diagram = InlineImage(doc, image_path, width=Inches(4))
            else:
                sequence_diagram = ""

            context = {
                "group": group,
                "title": title,
                "date": tanggal_indo,
                "description": description,
                "test_cases": test_case_data,
                "sequence_diagram": sequence_diagram,
                "dev_name": dev_name,
                "dev_npp": dev_npp,
                "mgr_name": mgr_name,
                "mgr_npp": mgr_npp,
                "dept_head_name": dept_head_name,
                "dept_head_npp": dept_head_npp
            }

            try:
                with st.spinner("📄 Membuat dokumen dan mengonversi ke PDF..."):
                    doc.render(context)
                    doc.save(docx_path)

                    # Use the new LibreOffice conversion function
                    pdf_path = convert_docx_to_pdf_libreoffice(docx_path, tmpdir)

                    with open(pdf_path, "rb") as pdf_file:
                        st.success("✅ Dokumen berhasil dibuat!")
                        st.download_button("📄 Download PDF", data=pdf_file, file_name="API_Test_Report.pdf",
                                           mime="application/pdf")
            except Exception as e:
                st.error(f"❌ Gagal membuat dokumen: {e}")
