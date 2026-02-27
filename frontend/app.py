import streamlit as st
import requests
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

st.title("LLaMA Text Summarizer")

def call_summarize_api(text: str, timeout: int = 60) -> str:
    response = requests.post(
        "http://localhost:8000/summarize/",
        data={"text": text},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json().get("summary", "Error generating output.")


def build_projects_section(projects: list[dict]) -> str:
    lines = ["Projects", ""]
    for project in projects:
        lines.append(f"- {project['title']}")
        if project["what"]:
            lines.append(f"  - {project['what']}")
        if project["stack"]:
            lines.append(f"  - Tech stack: {project['stack']}")
        if project["capabilities"]:
            lines.append(f"  - Key capabilities: {project['capabilities']}")
        if project["impact"]:
            lines.append(f"  - Impact: {project['impact']}")
        lines.append("")
    return "\n".join(lines).strip()


def build_projects_html(projects_text: str) -> str:
    escaped = (
        projects_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    return (
        "<html><head><meta charset='UTF-8'><title>Projects Section</title>"
        "<style>body{font-family:Segoe UI,Arial,sans-serif;margin:32px;color:#0f172a;}"
        "h1{margin-bottom:12px;}pre{white-space:pre-wrap;line-height:1.5;font-size:14px;}"
        "</style></head><body><h1>Projects</h1><pre>"
        f"{escaped}"
        "</pre></body></html>"
    )


def build_projects_pdf(projects_text: str) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    left_margin = 50
    right_margin = 50
    top_margin = 60
    bottom_margin = 50
    line_height = 16

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left_margin, page_height - top_margin, "Projects")

    pdf.setFont("Helvetica", 11)
    y = page_height - top_margin - 28
    max_width = page_width - left_margin - right_margin

    for raw_line in projects_text.splitlines():
        line = raw_line.strip()
        if not line:
            y -= line_height
            if y < bottom_margin:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = page_height - top_margin
            continue

        words = line.split(" ")
        current_line = ""
        for word in words:
            candidate = word if not current_line else f"{current_line} {word}"
            if pdf.stringWidth(candidate, "Helvetica", 11) <= max_width:
                current_line = candidate
            else:
                pdf.drawString(left_margin, y, current_line)
                y -= line_height
                if y < bottom_margin:
                    pdf.showPage()
                    pdf.setFont("Helvetica", 11)
                    y = page_height - top_margin
                current_line = word

        if current_line:
            pdf.drawString(left_margin, y, current_line)
            y -= line_height
            if y < bottom_margin:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = page_height - top_margin

    pdf.save()
    return buffer.getvalue()


st.subheader("General Text Summarizer")
user_input = st.text_area("Enter your text here:")

if st.button("Summarize"):
    if not user_input.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            summary = call_summarize_api(user_input)
            st.subheader("Summary:")
            st.write(summary)
        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend at http://localhost:8000. Start FastAPI first.")
        except requests.exceptions.Timeout:
            st.error("Request timed out. The model may be busy; try again.")
        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")


st.divider()
st.subheader("CV Projects Form")
st.caption("Enter project details and generate a CV-ready Projects section.")

default_projects = [
    {
        "title": "CV & Cover Letter Portfolio Manager",
        "what": "A database-driven portfolio manager for multi-profile CV versions and template-based cover letter exports.",
        "stack": "Python, Streamlit, SQLite, ReportLab, python-docx",
        "capabilities": "Profile-based CV/cover letter versioning, autofill from sender details, justified professional layouts, exports to HTML/PDF/DOCX/TXT, password-protected editor with a public portfolio view.",
        "impact": "Accelerates tailored document creation across roles with consistent formatting and a centralized portfolio.",
    },
    {
        "title": "End-to-End Sentiment Analysis App",
        "what": "A full-stack sentiment analysis tool with local LLM inference.",
        "stack": "Python, FastAPI, Streamlit, Ollama (Mistral) for on-device inference",
        "capabilities": "REST API for sentiment classification (Positive/Negative/Neutral), real-time predictions in a Streamlit UI, environment-aware backend config, robust API error handling.",
        "impact": "Enables quick experimentation with prompts and models while keeping inference on local hardware, reducing dependency on external services.",
    },
    {
        "title": "Text Summarizer Web App",
        "what": "A local LLM-powered text summarization web app with a REST API.",
        "stack": "LLaMA (via Ollama), FastAPI, Streamlit",
        "capabilities": "REST endpoint (POST /summarize) returning summaries, real-time UI for submission and results, on-device inference for low latency, reproducible dev setup.",
        "impact": "Provides fast, offline NLP prototyping suitable for rapid feature testing and demonstrations.",
    },
]

with st.form("projects_form"):
    st.markdown("### Project 1")
    p1_title = st.text_input("Project 1 - Title", value=default_projects[0]["title"])
    p1_what = st.text_area("Project 1 - What it is", value=default_projects[0]["what"])
    p1_stack = st.text_input("Project 1 - Tech stack", value=default_projects[0]["stack"])
    p1_capabilities = st.text_area("Project 1 - Key capabilities", value=default_projects[0]["capabilities"])
    p1_impact = st.text_area("Project 1 - Impact", value=default_projects[0]["impact"])

    st.markdown("### Project 2")
    p2_title = st.text_input("Project 2 - Title", value=default_projects[1]["title"])
    p2_what = st.text_area("Project 2 - What it is", value=default_projects[1]["what"])
    p2_stack = st.text_input("Project 2 - Tech stack", value=default_projects[1]["stack"])
    p2_capabilities = st.text_area("Project 2 - Key capabilities", value=default_projects[1]["capabilities"])
    p2_impact = st.text_area("Project 2 - Impact", value=default_projects[1]["impact"])

    st.markdown("### Project 3")
    p3_title = st.text_input("Project 3 - Title", value=default_projects[2]["title"])
    p3_what = st.text_area("Project 3 - What it is", value=default_projects[2]["what"])
    p3_stack = st.text_input("Project 3 - Tech stack", value=default_projects[2]["stack"])
    p3_capabilities = st.text_area("Project 3 - Key capabilities", value=default_projects[2]["capabilities"])
    p3_impact = st.text_area("Project 3 - Impact", value=default_projects[2]["impact"])
    use_ai_polish = st.checkbox("Use AI polish (optional)", value=True)

    generate_projects_section = st.form_submit_button("Generate CV Projects Section")

if generate_projects_section:
    projects = [
        {
            "title": p1_title.strip(),
            "what": p1_what.strip(),
            "stack": p1_stack.strip(),
            "capabilities": p1_capabilities.strip(),
            "impact": p1_impact.strip(),
        },
        {
            "title": p2_title.strip(),
            "what": p2_what.strip(),
            "stack": p2_stack.strip(),
            "capabilities": p2_capabilities.strip(),
            "impact": p2_impact.strip(),
        },
        {
            "title": p3_title.strip(),
            "what": p3_what.strip(),
            "stack": p3_stack.strip(),
            "capabilities": p3_capabilities.strip(),
            "impact": p3_impact.strip(),
        },
    ]

    valid_projects = [project for project in projects if project["title"]]

    if not valid_projects:
        st.warning("Please enter at least one project title.")
    else:
        deterministic_output = build_projects_section(valid_projects)
        final_output = deterministic_output

        if use_ai_polish:
            projects_text = "\n\n".join(
                [
                    (
                        f"Title: {project['title']}\n"
                        f"What it is: {project['what']}\n"
                        f"Tech stack: {project['stack']}\n"
                        f"Key capabilities: {project['capabilities']}\n"
                        f"Impact: {project['impact']}"
                    )
                    for project in valid_projects
                ]
            )

            prompt = (
                "Rewrite the projects below into a professional CV Projects section. "
                "Use concise ATS-friendly bullet points and keep each project clear and impact-oriented. "
                "Return plain text only. The first line must be exactly: Projects\n\n"
                f"{projects_text}"
            )

            try:
                cv_projects_section = call_summarize_api(prompt, timeout=90).strip()
                if not cv_projects_section.lower().startswith("projects"):
                    cv_projects_section = f"Projects\n\n{cv_projects_section}"
                final_output = cv_projects_section
            except requests.exceptions.ConnectionError:
                st.warning("AI polish skipped: cannot connect to backend. Showing deterministic Projects output.")
            except requests.exceptions.Timeout:
                st.warning("AI polish skipped: request timed out. Showing deterministic Projects output.")
            except requests.exceptions.RequestException as exc:
                st.warning(f"AI polish skipped: {exc}. Showing deterministic Projects output.")

        st.subheader("Generated CV Projects Section")
        st.markdown("## Projects")
        st.markdown(final_output.replace("Projects", "", 1).strip())

        st.text_area(
            "Print-ready Projects text",
            value=final_output,
            height=320,
            key="projects_print_ready",
        )
        st.download_button(
            label="Download Projects Section (.txt)",
            data=final_output,
            file_name="projects_section.txt",
            mime="text/plain",
        )
        projects_html = build_projects_html(final_output)
        st.download_button(
            label="Download Projects Section (.html)",
            data=projects_html,
            file_name="projects_section.html",
            mime="text/html",
        )
        projects_pdf = build_projects_pdf(final_output)
        st.download_button(
            label="Download Projects Section (.pdf)",
            data=projects_pdf,
            file_name="projects_section.pdf",
            mime="application/pdf",
        )
