import re
import json
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches
from docx2pdf import convert
from datetime import datetime

# --- Load raw Postman console export ---
with open("result_json.txt", encoding="utf-8") as f:
    raw = f.read()

# --- Temukan semua blok API Call ---
# Ini mencari method + URL + Response Body (dengan optional Request Body)
api_blocks = re.findall(
    r"(GET|POST|PUT|DELETE)\s+(http[^\s]+):\s+\{(.*?\"Response Body\"\s*:\s*\"(?:[^\"\\]|\\.)*\")\s*\}",
    raw, re.DOTALL
)

test_case_data = []

for i, (method, url, body_block) in enumerate(api_blocks, start=1):
    # Ambil Request Body (jika ada)
    req_match = re.search(r'"Request Body"\s*:\s*"((?:[^"\\]|\\.)*)"', body_block)
    if req_match:
        try:
            req_str = req_match.group(1).encode().decode("unicode_escape")
            req_json = json.loads(req_str)
            request_body = json.dumps(req_json, indent=2, ensure_ascii=False)
        except Exception as e:
            request_body = f"[decode failed: {e}]"
    else:
        request_body = "{}"


    # Ambil Response Body
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

    # Ambil info dari response
    status = res_json.get("status", "Unknown")
    status_code = res_json.get("statusCode", res_json.get("code", "N/A"))
    message = res_json.get("message", "No message")

    # Custom judul test case
    custom_test_cases = [
        "Sukses Get Data",
        "Client ID kosong",
        "Data tidak ditemukan"
    ]

    # Simpan test case
    test_case_data.append({
        "loop_index": f"{i:02d}",
        # "test_condition": "Normal" if i == 1 else "Abnormal",
        "test_condition": "Normal" if str(status_code) in ["200", "00"] else "Abnormal",
        "test_case": custom_test_cases[i - 1] if i - 1 < len(custom_test_cases) else f"{method} {url}",
        "request_body": request_body,
        "response_body": response_body,
        "log": f"Status: {status}, Code: {status_code}, Message: {message}"
    })

# --- Setup template dan gambar ---
doc = DocxTemplate("Test-Automation.docx")
sequence_diagram = InlineImage(doc, "flowElastic_fixed.jpg", width=Inches(4))

# --- Format tanggal indo ---
bulan_indo = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

today = datetime.today()
tanggal_indo = f"{today.day} {bulan_indo[today.month]} {today.year}"

context = {
    "title": "Seri Redeem API Test",
    # "date": datetime.today().strftime("%Y-%m-%d"), # format "%Y-%m-%d" atau "%d/%m/%Y"
    "date": tanggal_indo,
    "description": "Pengujian valid dan invalid Client ID terhadap endpoint seriRedeemId",
    "test_cases": test_case_data,
    "sequence_diagram": sequence_diagram
}

# --- Render dan Save Word ---
doc.render(context)
doc.save("API_Test_Report.docx")
print("✅ DOCX berhasil dibuat: API_Test_Report.docx")

# --- Konversi ke PDF ---
convert("API_Test_Report.docx")
print("📄 PDF juga berhasil dibuat: API_Test_Report.pdf")
