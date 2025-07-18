import re
import json
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Inches

# --- Load raw Postman console export ---
with open("result_json.txt", encoding="utf-8") as f:
    raw = f.read()

# --- Ambil method dan URL ---
url_match = re.search(r"(GET|POST|PUT|DELETE)\s+(http[^\s]+):\s+\{", raw)
method = url_match.group(1) if url_match else "N/A"
url = url_match.group(2) if url_match else "N/A"

# --- Decode Request Body ---
req_match = re.search(r'"Request Body":\s*"((?:[^"\\]|\\.)*)"', raw)
if req_match:
    request_body = req_match.group(1).encode().decode("unicode_escape").replace("\n", "").replace("\r", "").strip()
else:
    request_body = "[not found]"

# --- Decode Response Body ---
res_match = re.search(r'"Response Body":\s*"((?:[^"\\]|\\.)*)"', raw)
if res_match:
    try:
        res_body_clean = res_match.group(1).encode().decode("unicode_escape")
        res_json = json.loads(res_body_clean)
        response_body = json.dumps(res_json, indent=2, ensure_ascii=False).replace("\n", "").replace("\r", "").strip()
    except Exception as e:
        res_json = {}
        response_body = f"[decode failed: {e}]"
else:
    res_json = {}
    response_body = "[not found]"

# --- Info dari response JSON ---
status = res_json.get("status", "Unknown")
status_code = res_json.get("statusCode", res_json.get("code", "N/A"))
message = res_json.get("message", "No message")

# --- Final context (tanpa loop pada title/desc/date) ---
test_case_data = [
    {
        "loop_index": "01",
        "test_condition": "Normal",
        "test_case": "Status code 200 dan token tersedia",
        "request_body": request_body,
        "response_body": response_body,
        "log": f"Status: {status}, Code: {status_code}, Message: {message}"
    },
    {
        "loop_index": "02",
        "test_condition": "Abnormal",
        "test_case": "Tanpa field email",
        "request_body": "{\"password\": \"123456\"}",
        "response_body": "{\"status\":\"Error\", \"statusCode\":\"01\"}",
        "log": "Validasi error - field email kosong"
    }
]

# --- Setup template and inline image ---
doc = DocxTemplate("Test-Automation.docx")

title = "Login API"
date = "2025-07-14"
description = "Pengujian endpoint login user"
# sequence_diagram = InlineImage(doc, "flowElastic.jpg", width=Inches(4))
sequence_diagram = InlineImage(doc, "flowElastic_fixed.jpg", width=Inches(4))


context = {
    "title": title,
    "date": date,
    "description": description,
    "test_cases": test_case_data,
    "sequence_diagram": sequence_diagram
}

# --- Render and save ---
doc.render(context)
doc.save("API_Test_Report.docx")
print("✅ Laporan berhasil dibuat: API_Test_Report.docx")