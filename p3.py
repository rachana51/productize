import streamlit as st
import os
import tempfile
import docx
import openai
from PyPDF2 import PdfReader

# === CONFIGURATION ===
openai.api_key = st.secrets["OPENROUTER_API_KEY"]  # You should set this in .streamlit/secrets.toml

# === HELPER FUNCTIONS ===

def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def call_llm_to_extract_fields(template_text, photo_text):
    prompt = f"""
You are an assistant that extracts information from insurance photo reports and fills in a General Loss Report.

Here is the insurance template content (with placeholders):
-----------------------
{template_text}

Here is the content from the photo report:
-----------------------
{photo_text}

Based on the photo report, return a dictionary in JSON format matching the placeholders in the template, such as:
{{"INSURED_NAME": "...", "DATE_LOSS": "...", "INSURED_H_STREET": "...", "INSURED_H_CITY": "...", ...}}
    """
    response = openai.ChatCompletion.create(
        model="openrouter/mistralai/mixtral-8x7b",  # Or any preferred LLM
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )
    return eval(response['choices'][0]['message']['content'])  # Parse response as dictionary

def fill_template(template_file, fields: dict):
    doc = docx.Document(template_file)
    for para in doc.paragraphs:
        for key, value in fields.items():
            if f"[{key}]" in para.text:
                para.text = para.text.replace(f"[{key}]", str(value))
    return doc

# === STREAMLIT UI ===

st.title("🧾 General Loss Report Auto-Filler")

st.markdown("""
Upload a `.docx` insurance template and one or more `.pdf` photo reports.
The app will extract the data using an LLM and generate a completed document.
""")

template_file = st.file_uploader("Upload Insurance Template (.docx)", type=["docx"])
pdf_files = st.file_uploader("Upload Photo Reports (.pdf)", type=["pdf"], accept_multiple_files=True)

if st.button("Generate Completed Report") and template_file and pdf_files:
    # Extract photo report text
    combined_text = ""
    for pdf in pdf_files:
        combined_text += extract_text_from_pdf(pdf) + "\n"

    # Load template as text
    template_text = template_file.read().decode("utf-8", errors="ignore")  # fallback
    template_file.seek(0)

    # Call LLM to extract fields
    with st.spinner("Calling LLM to extract key values..."):
        field_data = call_llm_to_extract_fields(template_text, combined_text)

    # Fill in the template
    filled_doc = fill_template(template_file, field_data)

    # Save to temp and provide download
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        filled_doc.save(tmp.name)
        tmp_path = tmp.name

    st.success("Document generated successfully!")
    with open(tmp_path, "rb") as f:
        st.download_button("📥 Download Completed Document", data=f, file_name="completed_glr.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        )


