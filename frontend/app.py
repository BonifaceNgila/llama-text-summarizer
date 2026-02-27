import streamlit as st
import requests
from io import BytesIO
import base64
from datetime import datetime
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


def _image_to_data_uri(uploaded_file) -> str | None:
        if uploaded_file is None:
                return None
        raw = uploaded_file.getvalue()
        encoded = base64.b64encode(raw).decode("utf-8")
        return f"data:{uploaded_file.type};base64,{encoded}"


def _escape_html(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _clean_cover_letter_body(
    body: str,
    location: str,
    phone: str,
    email: str,
    subject: str,
    closing_name: str,
) -> str:
    header_lines = {
        location.strip().lower(),
        f"phone: {phone.strip().lower()}",
        phone.strip().lower(),
        f"email: {email.strip().lower()}",
        email.strip().lower(),
        f"subject: {subject.strip().lower()}",
        subject.strip().lower(),
        closing_name.strip().lower(),
    }

    cleaned_lines = []
    for line in body.splitlines():
        normalized = line.strip().lower()
        if normalized in header_lines:
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def build_selected_projects_html(projects: list[dict] | None) -> str:
    if not projects:
        return ""

    items = []
    for project in projects:
        title = _escape_html(project.get("title", "").strip())
        what = _escape_html(project.get("what", "").strip())
        impact = _escape_html(project.get("impact", "").strip())
        stack = _escape_html(project.get("stack", "").strip())

        if not title:
            continue

        details_parts = [part for part in [what, impact] if part]
        details = " — ".join(details_parts)
        stack_line = f"<br><span class='project-stack'>Tech: {stack}</span>" if stack else ""
        items.append(f"<li><strong>{title}</strong><br>{details}{stack_line}</li>")

    if not items:
        return ""

    return "<div class='projects'><h3>Selected Projects</h3><ul>" + "".join(items) + "</ul></div>"


def build_cover_letter_html(
        location: str,
        phone: str,
        email: str,
        subject: str,
        recipient: str,
        body: str,
        closing_name: str,
        role_line: str,
        date_line: str,
        theme: str,
        projects: list[dict] | None,
        profile_photo_uri: str | None,
        signature_uri: str | None,
) -> str:
    cleaned_body = _clean_cover_letter_body(
        body=body,
        location=location,
        phone=phone,
        email=email,
        subject=subject,
        closing_name=closing_name,
    )

        safe_recipient = _escape_html(recipient)
        safe_subject = _escape_html(subject)
        safe_location = _escape_html(location)
        safe_phone = _escape_html(phone)
        safe_email = _escape_html(email)
        safe_name = _escape_html(closing_name)
        safe_role = _escape_html(role_line)
        safe_date = _escape_html(date_line)

        paragraphs = [part.strip() for part in cleaned_body.split("\n\n") if part.strip()]
        safe_body = "".join(
                f"<p>{_escape_html(part).replace(chr(10), '<br>')}</p>" for part in paragraphs
        )

        photo_html = ""
        if profile_photo_uri:
                photo_html = f"<img src='{profile_photo_uri}' alt='Profile photo' class='profile-photo'/>"

        signature_html = ""
        if signature_uri:
                signature_html = f"<img src='{signature_uri}' alt='Signature' class='signature'/>"

        projects_section_html = build_selected_projects_html(projects)

        if theme == "Elegant Green Sidebar":
                return f"""
<html>
<head>
    <meta charset='UTF-8'>
    <title>Cover Letter</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#eef3ef; margin:0; padding:24px; color:#1f2937; }}
        .page {{ max-width:1000px; margin:auto; background:#fff; display:grid; grid-template-columns:260px 1fr; min-height:1150px; }}
        .left {{ background:#315f4a; color:#e8f3ed; padding:28px 22px; }}
        .profile-photo {{ width:160px; height:160px; border-radius:50%; object-fit:cover; border:4px solid rgba(255,255,255,.3); margin:0 auto 18px auto; display:block; }}
        .left h4 {{ margin:8px 0 10px 0; font-size:15px; color:#d0e8da; }}
        .left p {{ margin:0 0 6px 0; line-height:1.4; }}
        .right {{ padding:34px 40px; }}
        .name {{ font-size:50px; line-height:1; margin:0; color:#7ca8a2; }}
        .role {{ margin:8px 0 16px 0; font-size:26px; color:#3f4f4b; font-weight:600; }}
        .date {{ color:#6b7280; margin:10px 0 16px 0; font-style:italic; }}
        .subject {{ margin:0 0 10px 0; font-weight:700; color:#1f2937; }}
        .recipient {{ margin:0 0 10px 0; }}
        .body p {{ line-height:1.68; text-align:justify; margin:0 0 14px 0; }}
        .projects {{ margin-top:18px; }}
        .projects h3 {{ margin:0 0 8px 0; color:#1f2937; }}
        .projects ul {{ margin:0; padding-left:20px; }}
        .projects li {{ margin-bottom:8px; line-height:1.5; }}
        .project-stack {{ color:#4b5563; font-size:14px; }}
        .signature {{ display:block; margin-top:14px; max-height:80px; max-width:230px; object-fit:contain; }}
        .closing-name {{ margin-top:8px; font-weight:700; letter-spacing:0.4px; }}
    </style>
</head>
<body>
    <div class='page'>
        <div class='left'>
            {photo_html}
            <h4>Contact</h4>
            <p>{safe_location}</p>
            <p>{safe_phone}</p>
            <p>{safe_email}</p>
        </div>
        <div class='right'>
            <h1 class='name'>{safe_name}</h1>
            <div class='role'>{safe_role}</div>
            <p class='date'>{safe_date}</p>
            <p class='subject'>Subject: {safe_subject}</p>
            <p class='recipient'>{safe_recipient}</p>
            <div class='body'>{safe_body}</div>
            {projects_section_html}
            <p>Sincerely,</p>
            {signature_html}
            <p class='closing-name'>{safe_name}</p>
    </div>
    </div>
</body>
</html>
"""


def _parse_simple_list(text: str) -> list[str]:
    items = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("•"):
            line = line[1:].strip()
        if line.startswith("-"):
            line = line[1:].strip()
        items.append(line)
    return items


def _parse_experience(text: str) -> list[dict]:
    entries = []
    blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        header = lines[0]
        parts = [part.strip() for part in header.split("|")]
        title = parts[0] if len(parts) > 0 else ""
        org = parts[1] if len(parts) > 1 else ""
        date = parts[2] if len(parts) > 2 else ""
        bullets = []
        for raw in lines[1:]:
            item = raw
            if item.startswith("•") or item.startswith("-"):
                item = item[1:].strip()
            bullets.append(item)
        entries.append({"title": title, "org": org, "date": date, "bullets": bullets})
    return entries


def _parse_projects(text: str) -> list[dict]:
    projects = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split("|")]
        while len(parts) < 5:
            parts.append("")
        projects.append(
            {
                "title": parts[0],
                "description": parts[1],
                "stack": parts[2],
                "impact": parts[3],
                "link": parts[4],
            }
        )
    return projects


def build_cv_html(cv: dict) -> str:
    competencies_html = "".join(f"<li>{_escape_html(item)}</li>" for item in cv["competencies"])
    experience_html = ""
    for entry in cv["experience"]:
        bullets = "".join(f"<li>{_escape_html(b)}</li>" for b in entry["bullets"])
        experience_html += (
            "<div class='entry'>"
            f"<h4>{_escape_html(entry['title'])}</h4>"
            f"<p class='meta'>{_escape_html(entry['org'])} | {_escape_html(entry['date'])}</p>"
            f"<ul>{bullets}</ul>"
            "</div>"
        )

    education_html = "".join(f"<li>{_escape_html(item)}</li>" for item in cv["education"])
    certifications_html = "".join(f"<li>{_escape_html(item)}</li>" for item in cv["certifications"])
    languages_html = "".join(f"<li>{_escape_html(item)}</li>" for item in cv["languages"])
    referees_html = "".join(f"<li>{_escape_html(item)}</li>" for item in cv["referees"])

    projects_html = ""
    for project in cv["projects"]:
        link_html = ""
        if project["link"]:
            safe_link = _escape_html(project["link"])
            link_html = f"<p><strong>Link:</strong> <a href='{safe_link}' target='_blank'>{safe_link}</a></p>"
        projects_html += (
            "<div class='entry'>"
            f"<h4>{_escape_html(project['title'])}</h4>"
            f"<p>{_escape_html(project['description'])}</p>"
            f"<p><strong>Tech stack:</strong> {_escape_html(project['stack'])}</p>"
            f"<p><strong>Impact:</strong> {_escape_html(project['impact'])}</p>"
            f"{link_html}"
            "</div>"
        )

    return f"""
<html>
<head>
  <meta charset='UTF-8'>
  <title>CV - {_escape_html(cv['name'])}</title>
  <style>
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background:#eef2f7; margin:0; padding:24px; color:#0f172a; }}
    .page {{ max-width:1100px; margin:auto; background:#fff; border-radius:10px; overflow:hidden; border:1px solid #dbe5f0; }}
    .header {{ background:#1f3b5b; color:#f8fafc; padding:24px 30px; }}
    .header h1 {{ margin:0; font-size:34px; }}
    .headline {{ margin:6px 0 0 0; color:#dbeafe; }}
    .contact {{ margin-top:10px; font-size:14px; color:#e2e8f0; }}
    .grid {{ display:grid; grid-template-columns:1.8fr 1fr; gap:20px; padding:22px; }}
    h2 {{ margin:0 0 8px 0; color:#1f3b5b; border-bottom:2px solid #bfdbfe; padding-bottom:4px; font-size:22px; }}
    h4 {{ margin:0 0 4px 0; font-size:16px; color:#0f172a; }}
    p {{ margin:0 0 8px 0; line-height:1.55; text-align:justify; }}
    ul {{ margin:8px 0 12px 18px; }}
    li {{ margin-bottom:6px; line-height:1.45; }}
    .entry {{ margin-bottom:12px; }}
    .meta {{ color:#475569; margin-bottom:6px; }}
    a {{ color:#1d4ed8; }}
  </style>
</head>
<body>
  <div class='page'>
    <div class='header'>
      <h1>{_escape_html(cv['name'])}</h1>
      <p class='headline'>{_escape_html(cv['headline'])}</p>
      <p class='contact'>{_escape_html(cv['contact'])}</p>
      <p class='contact'>{_escape_html(cv['links'])}</p>
    </div>
    <div class='grid'>
      <div>
        <h2>Profile</h2>
        <p>{_escape_html(cv['profile'])}</p>
        <h2>Professional Experience</h2>
        {experience_html}
        <h2>Projects</h2>
        {projects_html}
      </div>
      <div>
        <h2>Core Competencies</h2>
        <ul>{competencies_html}</ul>
        <h2>Education</h2>
        <ul>{education_html}</ul>
        <h2>Certifications</h2>
        <ul>{certifications_html}</ul>
        <h2>Languages</h2>
        <ul>{languages_html}</ul>
        <h2>Referees</h2>
        <ul>{referees_html}</ul>
      </div>
    </div>
  </div>
</body>
</html>
"""

        if theme == "Lilac Professional":
                return f"""
<html>
<head>
    <meta charset='UTF-8'>
    <title>Cover Letter</title>
    <style>
        body {{ font-family:'Segoe UI',Arial,sans-serif; background:#ececec; margin:0; padding:22px; color:#1f2937; }}
        .page {{ max-width:1000px; margin:auto; background:#f5f5f5; display:grid; grid-template-columns:280px 1fr; }}
        .left {{ background:#d9b5e6; padding:28px 22px; }}
        .profile-photo {{ width:150px; height:150px; border-radius:50%; object-fit:cover; border:6px solid rgba(255,255,255,.35); margin-bottom:24px; }}
        .left h3 {{ margin:8px 0; font-size:30px; line-height:1.06; color:#303042; }}
        .left .role {{ margin-bottom:20px; font-size:17px; color:#4b5563; }}
        .left p {{ margin:0 0 8px 0; line-height:1.4; }}
        .right {{ padding:34px 40px; }}
        .right h1 {{ margin:0; font-size:56px; line-height:1.02; color:#32323e; }}
        .right h2 {{ margin:6px 0 12px 0; color:#50515f; font-weight:500; }}
        .date {{ font-size:30px; margin:10px 0 14px 0; color:#2f3346; font-weight:700; text-transform:uppercase; }}
        .subject {{ margin:0 0 10px 0; font-weight:700; }}
        .body p {{ line-height:1.65; margin:0 0 14px 0; text-align:justify; }}
        .projects {{ margin-top:16px; }}
        .projects h3 {{ margin:0 0 8px 0; font-size:22px; color:#32323e; }}
        .projects ul {{ margin:0; padding-left:20px; }}
        .projects li {{ margin-bottom:8px; line-height:1.5; }}
        .project-stack {{ color:#4b5563; font-size:14px; }}
        .signature {{ display:block; margin-top:14px; max-height:80px; max-width:230px; object-fit:contain; }}
        .closing-name {{ margin-top:10px; font-weight:700; font-size:28px; color:#2f3346; }}
    </style>
</head>
<body>
    <div class='page'>
        <div class='left'>
            {photo_html}
            <h3>{safe_name}</h3>
            <div class='role'>{safe_role}</div>
            <p><strong>CONTACT</strong></p>
            <p>{safe_location}</p>
            <p>{safe_phone}</p>
            <p>{safe_email}</p>
        </div>
        <div class='right'>
            <h1>{safe_name}</h1>
            <h2>{safe_role}</h2>
            <p class='date'>{safe_date}</p>
            <p class='subject'>Subject: {safe_subject}</p>
            <p>{safe_recipient}</p>
            <div class='body'>{safe_body}</div>
            {projects_section_html}
            <p>Sincerely,</p>
            {signature_html}
            <p class='closing-name'>{safe_name}</p>
        </div>
    </div>
</body>
</html>
"""

        if theme == "Dark Split":
                return f"""
<html>
<head>
    <meta charset='UTF-8'>
    <title>Cover Letter</title>
    <style>
        body {{ font-family:'Segoe UI',Arial,sans-serif; background:#efefef; margin:0; padding:0; color:#1f2937; }}
        .top {{ display:grid; grid-template-columns:370px 1fr; background:#dadce0; }}
        .photo-wrap {{ background:#2e2e34; padding:24px; display:flex; align-items:center; justify-content:center; }}
        .profile-photo {{ width:180px; height:180px; border-radius:50%; object-fit:cover; border:8px solid #dedfe1; }}
        .title {{ padding:28px 40px; }}
        .title h1 {{ margin:0; font-size:72px; line-height:0.95; color:#272932; }}
        .title .role {{ margin-top:10px; letter-spacing:5px; color:#3f4450; font-size:21px; }}
        .info-bar {{ padding:14px 36px; border-top:4px solid #f8b400; border-bottom:1px solid #d3d7de; color:#272932; font-size:15px; }}
        .page {{ display:grid; grid-template-columns:370px 1fr; min-height:1050px; }}
        .left {{ background:#2e2e34; color:#f2f5f8; padding:34px 44px; }}
        .left h3 {{ margin:0 0 12px 0; font-size:44px; letter-spacing:3px; }}
        .left p {{ margin:0 0 8px 0; line-height:1.5; }}
        .right {{ background:#f1f2f4; padding:34px 52px; }}
        .right h2 {{ margin:0 0 12px 0; letter-spacing:2px; font-size:44px; color:#272932; }}
        .date {{ margin-bottom:10px; font-weight:600; color:#4b5563; }}
        .subject {{ margin:0 0 10px 0; font-weight:700; }}
        .body p {{ line-height:1.7; text-align:justify; margin:0 0 14px 0; }}
        .projects {{ margin-top:14px; }}
        .projects h3 {{ margin:0 0 8px 0; color:#272932; letter-spacing:1px; }}
        .projects ul {{ margin:0; padding-left:20px; }}
        .projects li {{ margin-bottom:8px; line-height:1.5; }}
        .project-stack {{ color:#4b5563; font-size:14px; }}
        .signature {{ display:block; margin-top:14px; max-height:78px; max-width:220px; object-fit:contain; }}
    </style>
</head>
<body>
    <div class='top'>
        <div class='photo-wrap'>{photo_html}</div>
        <div class='title'><h1>{safe_name}</h1><div class='role'>{safe_role}</div></div>
    </div>
    <div class='info-bar'>{safe_phone} | {safe_email} | {safe_location}</div>
    <div class='page'>
        <div class='left'>
            <h3>INFO</h3>
            <p>{safe_date}</p>
            <p>To:</p>
            <p>{safe_recipient}</p>
            <p><strong>Position:</strong></p>
            <p>{safe_subject}</p>
        </div>
        <div class='right'>
            <h2>COVER LETTER</h2>
            <div class='body'>{safe_body}</div>
            {projects_section_html}
            <p>Sincerely,</p>
            {signature_html}
            <p><strong>{safe_name}</strong></p>
        </div>
    </div>
</body>
</html>
"""

        if theme == "Minimal Gray":
                return f"""
<html>
<head>
    <meta charset='UTF-8'>
    <title>Cover Letter</title>
    <style>
        body {{ font-family:'Segoe UI',Arial,sans-serif; background:#efefef; margin:0; padding:28px; color:#2f3743; }}
        .page {{ max-width:980px; margin:auto; background:#f3f3f3; padding:34px 36px 44px 36px; }}
        .header {{ display:grid; grid-template-columns:250px 1fr; gap:26px; margin-bottom:22px; }}
        .profile-photo {{ width:170px; height:170px; border-radius:50%; object-fit:cover; border:4px solid #d2d7df; }}
        .name {{ font-size:60px; margin:0; color:#1f2937; }}
        .role {{ margin:8px 0 0 0; font-size:32px; color:#475569; }}
        .content {{ display:grid; grid-template-columns:260px 1fr; gap:28px; }}
        .side h4 {{ margin:0 0 10px 0; font-size:34px; color:#1f2937; }}
        .side p {{ margin:0 0 10px 0; line-height:1.45; }}
        .main .date {{ margin:0 0 16px 0; color:#6b7280; font-weight:600; }}
        .main .subject {{ margin:0 0 10px 0; font-weight:700; }}
        .body p {{ line-height:1.7; margin:0 0 14px 0; text-align:justify; }}
        .projects {{ margin-top:14px; }}
        .projects h3 {{ margin:0 0 8px 0; color:#1f2937; }}
        .projects ul {{ margin:0; padding-left:20px; }}
        .projects li {{ margin-bottom:8px; line-height:1.5; }}
        .project-stack {{ color:#4b5563; font-size:14px; }}
        .signature {{ display:block; margin-top:14px; max-height:78px; max-width:230px; object-fit:contain; }}
    </style>
</head>
<body>
    <div class='page'>
        <div class='header'>
            <div>{photo_html}</div>
            <div>
                <h1 class='name'>{safe_name}</h1>
                <p class='role'>{safe_role}</p>
            </div>
        </div>
        <div class='content'>
            <div class='side'>
                <h4>Personal Info</h4>
                <p><strong>Phone</strong><br>{safe_phone}</p>
                <p><strong>Email</strong><br>{safe_email}</p>
                <p><strong>Location</strong><br>{safe_location}</p>
            </div>
            <div class='main'>
                <p class='date'>{safe_date}</p>
                <p>{safe_recipient}</p>
                <p class='subject'>Subject: {safe_subject}</p>
                <div class='body'>{safe_body}</div>
                {projects_section_html}
                <p>Kind regards,</p>
                {signature_html}
                <p><strong>{safe_name}</strong></p>
            </div>
        </div>
    </div>
</body>
</html>
"""

        return f"""
<html>
<head>
    <meta charset='UTF-8'>
    <title>Cover Letter</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f3f6fb; margin: 0; padding: 24px; color: #0f172a; }}
        .page {{ max-width: 900px; margin: auto; background: #ffffff; border: 1px solid #dbe5f0; border-radius: 10px; padding: 28px 34px; }}
        .header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; border-bottom: 1px solid #dbe5f0; padding-bottom: 14px; margin-bottom: 18px; }}
        .contact p {{ margin: 0 0 5px 0; line-height: 1.35; }}
        .profile-photo {{ width: 96px; height: 96px; border-radius: 10px; object-fit: cover; border: 1px solid #cbd5e1; }}
        .name {{ margin:0; font-size:34px; color:#1f2937; }}
        .role {{ margin:4px 0 0 0; color:#334155; }}
        .date {{ margin: 14px 0 0 0; color:#64748b; }}
        .subject {{ margin: 14px 0; font-weight: 600; }}
        .recipient {{ margin-bottom: 14px; }}
        .body p {{ line-height: 1.6; text-align: justify; margin:0 0 12px 0; }}
        .projects {{ margin-top:14px; }}
        .projects h3 {{ margin:0 0 8px 0; color:#1f2937; }}
        .projects ul {{ margin:0; padding-left:20px; }}
        .projects li {{ margin-bottom:8px; line-height:1.5; }}
        .project-stack {{ color:#4b5563; font-size:14px; }}
        .closing {{ margin-top: 22px; }}
        .signature {{ display: block; margin-top: 10px; max-height: 72px; max-width: 220px; object-fit: contain; }}
        .closing-name {{ margin-top: 8px; font-weight: 700; letter-spacing: 0.2px; }}
    </style>
</head>
<body>
    <div class='page'>
        <div class='header'>
            <div class='contact'>
                <h1 class='name'>{safe_name}</h1>
                <p class='role'>{safe_role}</p>
                <p class='date'>{safe_date}</p>
                <p>{safe_location}</p>
                <p>Phone: {safe_phone}</p>
                <p>Email: {safe_email}</p>
            </div>
            <div>{photo_html}</div>
        </div>
        <p class='subject'>Subject: {safe_subject}</p>
        <p class='recipient'>{safe_recipient}</p>
        <div class='body'>{safe_body}</div>
        {projects_section_html}
        <div class='closing'>
            <p>Sincerely,</p>
            {signature_html}
            <p class='closing-name'>{safe_name}</p>
        </div>
    </div>
</body>
</html>
"""


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

if "projects_output" not in st.session_state:
    st.session_state.projects_output = ""
if "projects_output_html" not in st.session_state:
    st.session_state.projects_output_html = ""
if "projects_output_pdf" not in st.session_state:
    st.session_state.projects_output_pdf = b""
if "projects_catalog" not in st.session_state:
    st.session_state.projects_catalog = []

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

if not st.session_state.projects_catalog:
    st.session_state.projects_catalog = default_projects

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

        st.session_state.projects_output = final_output
        st.session_state.projects_output_html = build_projects_html(final_output)
        st.session_state.projects_output_pdf = build_projects_pdf(final_output)
        st.session_state.projects_catalog = valid_projects

if st.session_state.projects_output:
    display_output = st.session_state.projects_output.strip()
    if not display_output.lower().startswith("projects"):
        display_output = f"Projects\n\n{display_output}"

    st.subheader("Generated CV Projects Section")
    st.markdown("## Projects")
    st.markdown(display_output.split("\n", 1)[1].strip() if "\n" in display_output else "")

    st.text_area(
        "Print-ready Projects text",
        value=display_output,
        height=320,
        key="projects_print_ready",
    )
    st.download_button(
        label="Download Projects Section (.txt)",
        data=display_output,
        file_name="projects_section.txt",
        mime="text/plain",
    )
    st.download_button(
        label="Download Projects Section (.html)",
        data=st.session_state.projects_output_html,
        file_name="projects_section.html",
        mime="text/html",
    )
    st.download_button(
        label="Download Projects Section (.pdf)",
        data=st.session_state.projects_output_pdf,
        file_name="projects_section.pdf",
        mime="application/pdf",
    )


st.divider()
st.subheader("Cover Letter Builder")
st.caption("Pick a theme style, then upload display picture and signature for final placement.")

default_cover_letter_body = (
    "Dear Jubilee Life Insurance Recruitment Team,\n"
    "I am writing to express my interest in the AI Intern position (Job Ref. JLIL385) at Jubilee Life Insurance Limited. "
    "My journey toward becoming a Solution Architect for agentic systems has been self-directed and project-driven, "
    "combining IT operations expertise with hands-on AI/ML prototyping.\n\n"
    "I designed and built three end-to-end projects as deliberate steps on this path: a CV & Cover Letter Portfolio Manager, "
    "an End-to-End Sentiment Analysis App, and a Text Summarizer Web App. These experiences have sharpened my ability to "
    "translate business needs into scalable, production-ready AI solutions, a core capability I am eager to bring to Jubilee’s "
    "AI and data initiatives.\n\n"
    "What drew me to Jubilee is your emphasis on data governance, security, and practical AI engineering within an insurance context. "
    "My projects have been guided by a similar mindset: robust architecture, secure data handling, and clear documentation while "
    "delivering tangible value.\n\n"
    "In terms of technical alignment, I bring hands-on experience with Python, REST API design, and full-stack AI prototyping. "
    "I would welcome the opportunity to discuss how my self-directed journey and demonstrated projects can contribute to Jubilee Life Insurance’s AI roadmap.\n\n"
    "Thank you for considering my application."
)

with st.form("cover_letter_form"):
    cl_theme = st.selectbox(
        "Template / Theme",
        options=[
            "Classic Clean",
            "Elegant Green Sidebar",
            "Lilac Professional",
            "Dark Split",
            "Minimal Gray",
        ],
        index=0,
    )
    cl_location = st.text_input("Location", value="Kilifi, Kenya")
    cl_phone = st.text_input("Phone", value="+254792950816")
    cl_email = st.text_input("Email", value="mutisyaboniface@outlook.com")
    cl_date = st.text_input("Date", value=datetime.now().strftime("%d %B %Y"))
    cl_subject = st.text_input("Subject", value="AI Intern Application – JLIL385 (Boniface Mutisya Ngila)")
    cl_recipient = st.text_input("Recipient", value="Dear Jubilee Life Insurance Recruitment Team,")
    cl_body = st.text_area("Body", value=default_cover_letter_body, height=280)
    cl_name = st.text_input("Closing Name", value="BONIFACE MUTISYA NGILA")
    cl_role = st.text_input("Role Line", value="IT Officer | IAM | IT Operations | Security")
    cl_photo = st.file_uploader("Upload Display Picture", type=["png", "jpg", "jpeg"], key="cover_letter_photo")
    cl_signature = st.file_uploader("Upload Signature", type=["png", "jpg", "jpeg"], key="cover_letter_signature")
    cl_include_projects = st.checkbox("Include Selected Projects in letter", value=True)
    generate_cover_letter = st.form_submit_button("Generate Cover Letter")

if generate_cover_letter:
    if not cl_body.strip():
        st.warning("Please provide cover letter body text.")
    else:
        photo_uri = _image_to_data_uri(cl_photo)
        signature_uri = _image_to_data_uri(cl_signature)

        cover_letter_html = build_cover_letter_html(
            location=cl_location.strip(),
            phone=cl_phone.strip(),
            email=cl_email.strip(),
            subject=cl_subject.strip(),
            recipient=cl_recipient.strip(),
            body=cl_body.strip(),
            closing_name=cl_name.strip(),
            role_line=cl_role.strip(),
            date_line=cl_date.strip(),
            theme=cl_theme,
            projects=st.session_state.projects_catalog if cl_include_projects else [],
            profile_photo_uri=photo_uri,
            signature_uri=signature_uri,
        )

        st.subheader("Cover Letter Preview")
        st.components.v1.html(cover_letter_html, height=900, scrolling=True)
        st.download_button(
            label="Download Cover Letter (.html)",
            data=cover_letter_html,
            file_name="cover_letter.html",
            mime="text/html",
        )


st.divider()
st.subheader("CV Builder (All Sections)")
st.caption("Includes Profile, Competencies, Experience, Education, Certifications, Projects, Languages, and Referees.")

default_competencies_text = """Identity & Access Management: IAM lifecycle, SSO, MFA, Conditional Access; AD/Entra ID; OKTA
Cloud & Platforms: AWS (in progress through Agentic AI program), Google Cloud Platform (GCP) basics; Azure AD/Entra ID; Microsoft 365
AI/ML & Data: Basic ML concepts, data preparation, feature engineering, model evaluation; Vertex AI familiarity (Agent Builder concepts); RAG systems awareness; data governance and security practices
ML Ops & Scripting: Python (pandas, numpy), PowerShell, Bash; basic ML workflow automation concepts
Data & Databases: SQL (MySQL/MariaDB), data modeling, data quality and validation
DevTools & Collaboration: Git/GitHub, ServiceNow (ticketing and incident management), SOPs and knowledge bases, documentation
Networking & Security: TCP/IP, DNS, VPN, endpoint security basics
Frontend/UX & Reporting: HTML/CSS basics; Streamlit (UI for small tools) (as applicable to internal tools)
Other: REST APIs, FastAPI (concepts), data storage (SQLite basics)"""

default_experience_text = """IT OFFICER | Plan International Kenya, Coastal Hub | March 2024
- Managed IT infrastructure, servers, and networks to ensure high availability, security, and performance; implemented disaster recovery planning and monitoring.
- Configured user access, virtualized environments, and server apps; enforced IAM governance, MFA/SSO, and least-privilege access.
- Delivered Tier-1 to mid-level IT support; resolved complex access issues; conducted staff training on security best practices and authentication.
- Maintained documentation, performance reporting, and knowledge base updates; supported ServiceNow ticket lifecycle for incidents and changes.
- Participated in onboarding/offboarding processes and asset provisioning; collaborated with infrastructure teams to escalate and resolve complex issues.
- Identified recurring problems and opportunities for automation to improve service delivery and reduce downtime.

IT ASSISTANT | Plan International Kenya, Coastal Hub | November 2022
- Executed user identity lifecycle activities; supported global directory services and SSO integrations; assisted with system upgrades, backups, and secure connectivity.
- Delivered Tier 1 support for desktop, network, and infrastructure issues; configured Microsoft 365 apps and VPN connectivity.
- Documented incidents and resolutions; mentored junior staff; contributed to team performance improvements.

IT SUPPORT INTERN | Plan International Kenya, Coastal Hub | November 2021
- Managed Global Active Directory and OKTA services; supported Exchange Online, SAP, and Office 365 access provisioning.
- Enforced IT policies and security guidelines; provided end-user training on corporate apps; assisted in server/endpoint troubleshooting.
- Supported incident analysis and cross-functional collaboration for faster issue resolution."""

default_education_text = """Master of Science in Computer Science - UNICAF University - (Ongoing)
Bachelor of Business Information Technology - Taita Taveta University - (November 2019)
Kenya Certification of Secondary Education (KCSE) - Mayori Secondary School - (October 2014)"""

default_certifications_text = """Oracle Cloud Infrastructure 2025 Certified DevOps Professional (Oct 25, 2025)
Oracle Cloud Infrastructure 2025 Certified Architect Associate (Oct 23, 2025)
Oracle Cloud Infrastructure 2025 Certified Foundations Associate (Aug 6, 2025)
Google IT Support Professional Certification
CIPIT Data Protection Course, Strathmore University
IBM Data Analyst Professional Certification"""

default_projects_text = """CV & COVER LETTER PORTFOLIO MANAGER | A database-driven portfolio manager for multi-profile CV versions and template-based cover letter exports. | Python, Streamlit, SQLite, ReportLab, python-docx | Accelerates tailored document creation across roles with consistent formatting and a centralized portfolio. | https://potfolio-jtibqpnbxqxuml8l6s8wb3.streamlit.app/
END-TO-END SENTIMENT ANALYSIS APP | A full-stack sentiment analysis tool with local LLM inference. | Python, FastAPI, Streamlit, Ollama (Mistral) for on-device inference. | Enables quick experimentation with prompts and models while keeping inference on local hardware, reducing dependency on external services. | https://sentiment-analyzer-mistral-njc9wcbhgxudeckairs6uf.streamlit.app/
TEXT SUMMARIZER WEB APP | A local LLM-powered text summarization web app with a REST API. | LLaMA (via Ollama), FastAPI, Streamlit. | Provides fast, offline NLP prototyping suitable for rapid feature testing and demonstrations. | https://llama-text-summarizer-ifrxwwqz6xleetpg4kwwe9.streamlit.app/"""

default_languages_text = """English (Fluent)
Swahili (Native)"""

default_referees_text = """Winfred Mukonza | Plan International Kenya | Email: winfred.mukonza@plan-international.org | Phone: +254713267985
Cynthia Akoth | Plan International Kenya | Email: cynthia.akoth@plan-international.org | Phone: +254707870390
Sharon Meliyio | Plan International Kenya | Email: sharon.meliyio@plan-international.org | Phone: +254724917720"""

with st.form("cv_full_form"):
    cv_name = st.text_input("Full Name", value="BONIFACE MUTISYA NGILA")
    cv_headline = st.text_input("Headline", value="Aspiring AI Solution Architect")
    cv_contact = st.text_input("Contact", value="Kilifi, Kenya | +254792950816 | mutisyaboniface@outlook.com")
    cv_links = st.text_input("Links", value="Boniface Ngila | LinkedIn | BonifaceNgila")
    cv_profile = st.text_area("Profile", value="Aspiring AI Solutions Architect and ML Engineer with a strong foundation in General IT Operations, IAM, cloud services, and secure, scalable infrastructure. Currently enrolled in AWS Agentic AI Solutions Architect and Google Cloud ML Engineer programs, I am seeking an AI Intern role to apply hands-on Vertex AI, data preparation, prompt engineering, and MLOps practices on real-world insurance technology projects. Eager to contribute to AI feature development, data governance, and knowledge-base/reporting initiatives while growing into a full-fledged AI/ML engineer.", height=160)
    cv_competencies = st.text_area("Core Competencies (one per line)", value=default_competencies_text, height=180)
    cv_experience = st.text_area("Professional Experience (format: Role | Organization | Date, bullets below each)", value=default_experience_text, height=260)
    cv_education = st.text_area("Education (one per line)", value=default_education_text, height=120)
    cv_certifications = st.text_area("Certifications (one per line)", value=default_certifications_text, height=140)
    cv_projects = st.text_area("Projects (format: Title | What it is | Tech stack | Impact | Link)", value=default_projects_text, height=180)
    cv_languages = st.text_area("Languages (one per line)", value=default_languages_text, height=90)
    cv_referees = st.text_area("Referees (one per line)", value=default_referees_text, height=120)
    generate_cv_full = st.form_submit_button("Generate Full CV")

if generate_cv_full:
    cv_payload = {
        "name": cv_name.strip(),
        "headline": cv_headline.strip(),
        "contact": cv_contact.strip(),
        "links": cv_links.strip(),
        "profile": cv_profile.strip(),
        "competencies": _parse_simple_list(cv_competencies),
        "experience": _parse_experience(cv_experience),
        "education": _parse_simple_list(cv_education),
        "certifications": _parse_simple_list(cv_certifications),
        "projects": _parse_projects(cv_projects),
        "languages": _parse_simple_list(cv_languages),
        "referees": _parse_simple_list(cv_referees),
    }
    cv_html = build_cv_html(cv_payload)
    st.session_state.cv_full_html = cv_html

if "cv_full_html" in st.session_state and st.session_state.cv_full_html:
    st.subheader("Full CV Preview")
    st.components.v1.html(st.session_state.cv_full_html, height=1000, scrolling=True)
    st.download_button(
        label="Download Full CV (.html)",
        data=st.session_state.cv_full_html,
        file_name="full_cv.html",
        mime="text/html",
    )
