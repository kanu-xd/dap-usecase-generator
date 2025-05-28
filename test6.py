import streamlit as st
import pandas as pd
from together import Together
from io import BytesIO
from docx import Document
from fpdf import FPDF

# Load usecases CSV
@st.cache_data
def load_csv():
    return pd.read_csv("Usecase1.csv")

# Extract 3–4 sample usecases to ground the LLM prompt
def get_usecase_examples(df):
    examples = []
    for _, row in df.head(4).iterrows():
        example = f"""
Usecase Title: {row['Usecase Title']}
App Type / Industry: {row['App type/Industry']}
App Name: {row['App name']}
Business Process: {row['Business process']}
Persona: {row['Persona']}
Goal: {row['Goal']}
Pre-State: {row['Pre-state']}
Business Implications: {row['Business Implications']}
Process Enhancements with Whatfix: {row['Process Enhancements with Whatfix']}
Post-State: {row['Post state ']}
"""
        examples.append(example)
    return "\n---\n".join(examples)

# Initialize Together API
client = Together(api_key="eef6e7bf91fd11b40888ae99502d02a863ff649d03f709092c455783cc707b71")

# Generate onboarding plan from Together AI
def generate_onboarding_plan(problem_statement: str, sample_usecases: str) -> str:
    SYSTEM_PROMPT = f"""
You are a Digital Adoption Consultant working for a top-tier DAP (Digital Adoption Platform) company like Whatfix or WalkMe. Your job is to analyze client onboarding problems and generate high-quality, enterprise-ready onboarding plans that are:

- Realistic (based on actual user behavior and tools)
- Specific (crisp steps, not vague suggestions)
- Measurable (include outcomes and success metrics)
- Action-oriented (clearly map Whatfix features to business outcomes)

Below are examples of real onboarding use cases:

{sample_usecases}

🧠 Your tone should reflect a senior DAP consultant — concise, strategic, and grounded in enterprise use cases.

Use this format:
## Usecase Title: ...
- **App Type / Industry**: ...
- **App Name**: ...
- **Business Process**: ...
- **Persona**: ...
- **Goal**: ...
- **Pre-State**: ...
- **Business Implications**: ...
- **Whatfix Enhancements**: ...
- **Post-State**: ...

🎯 Prioritize:
- Making suggestions Whatfix (or DAP) can *actually* do
- Mapping user behavior to platform features
- Showing cause-effect (If user does X, feature Y will change outcome Z)

Assume the reader is a client stakeholder (e.g., Head of Enablement, IT, HR, or Sales Ops).

Problem Statement: {problem_statement}

Onboarding Plan:
"""

    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": problem_statement}
        ]
    )
    return response.choices[0].message.content.strip()

# Export functions
def to_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

def to_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)
    pdf_output = pdf.output(dest='S').encode('latin1')  # 'S' returns as string
    return BytesIO(pdf_output)


# --- Streamlit UI ---
st.set_page_config(page_title="💡 DAP Usecase Generator", layout="centered")
st.title("💡 DAP Usecase Generator")

st.markdown("""
Enter a **problem statement** for a client onboarding situation (e.g. low Bullhorn adoption).  
Use this tool to generate realistic, high-quality DAP usecases. Great for client onboarding, ideation calls, or internal drafts.
""")

problem_statement = st.text_area(
    "Client Problem Statement/ context",
    height=200,
    placeholder="e.g., Sales reps aren't using Salesforce to log follow-ups, impacting pipeline visibility."
)

if st.button("Generate Plan"):
    if not problem_statement.strip():
        st.warning("Please enter a problem statement.")
    else:
        df_usecases = load_csv()
        sample_usecases = get_usecase_examples(df_usecases)

        with st.spinner("Thinking like a Whatfix expert..."):
            output = generate_onboarding_plan(problem_statement, sample_usecases)

        st.success("Here's your generated Usecase:")
        st.markdown(output)

        st.download_button(
            label="📥 Download as Text",
            data=output,
            file_name="usecase_draft.txt",
            mime="text/plain"
        )

        st.download_button(
            label="📄 Download as PDF",
            data=to_pdf(output),
            file_name="usecase_draft.pdf",
            mime="application/pdf"
        )

        st.download_button(
            label="📝 Download as Word Doc",
            data=to_docx(output),
            file_name="usecase_draft.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
