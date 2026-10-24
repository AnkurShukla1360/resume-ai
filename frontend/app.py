
import os
import json
import requests
import streamlit as st

API_URL = os.getenv(
    "RESUMEAI_API_URL",
    "http://127.0.0.1:8000/api/analyze",
)

st.set_page_config(
    page_title="ResumeAI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    .hero {
        padding: 2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #172554, #4338ca);
        color: white;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        color: white;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .hero p {
        color: #e0e7ff;
        font-size: 1.05rem;
    }
    div[data-testid="stMetric"] {
        background: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def show_list(items, empty_message="No data available."):
    if not items:
        st.info(empty_message)
        return

    for item in items:
        if isinstance(item, dict):
            st.write("• " + str(item))
        else:
            st.write(f"• {item}")


def display_tailored_resume(data):
    """Display the generated resume and downloadable LaTeX source."""

    tailored = data.get("tailored_resume") or {}
    latex_code = tailored.get("latex_code", "")

    st.markdown("---")
    st.markdown("## 🧾 JD-Tailored Resume — Overleaf Code")

    if not latex_code:
        st.warning(
            "Resume analysis completed, but no LaTeX code was returned. "
            "Check the backend terminal."
        )
        return

    st.write(
        "Your tailored resume is ready. Review the preview, download "
        "the complete LaTeX source, and compile it on Overleaf."
    )

    if tailored.get("instructions"):
        st.info(tailored["instructions"])

    if tailored.get("warning"):
        st.warning(tailored["warning"])

    content = tailored.get("content") or {}

    with st.expander("👀 Resume Preview", expanded=True):
        st.markdown(
            f"# {content.get('full_name') or 'Candidate'}"
        )

        if content.get("headline"):
            st.caption(content["headline"])

        contact = [
            content.get("email", ""),
            content.get("phone", ""),
            content.get("location", ""),
        ]
        contact = [item for item in contact if item]

        if contact:
            st.write(" | ".join(contact))

        links = [
            ("LinkedIn", content.get("linkedin")),
            ("GitHub", content.get("github")),
            ("Portfolio", content.get("portfolio")),
        ]

        for label, url in links:
            if url and str(url).startswith(("https://", "http://")):
                st.markdown(f"[{label}]({url})")

        if content.get("summary"):
            st.markdown("### Professional Summary")
            st.write(content["summary"])

        if content.get("skills"):
            st.markdown("### Technical Skills")
            st.write(", ".join(content["skills"]))

        if content.get("projects"):
            st.markdown("### Relevant Projects")

            for project in content["projects"]:
                st.markdown(
                    f"**{project.get('name', 'Project')}**"
                )

                technologies = project.get("technologies", [])

                if technologies:
                    st.caption(
                        "Technologies: " + ", ".join(technologies)
                    )

                show_list(project.get("bullets", []))

        for title, key in [
            ("Experience", "experience"),
            ("Education", "education"),
            ("Certifications", "certifications"),
            ("Achievements", "achievements"),
        ]:
            items = content.get(key, [])

            if items:
                st.markdown(f"### {title}")
                show_list(items)

    st.markdown("### Complete `main.tex` Source")

    st.caption(
        "This is the complete LaTeX code. Copy it into main.tex "
        "in Overleaf, or download it below."
    )

    st.code(latex_code, language="latex")

    st.download_button(
        label="⬇️ Download Overleaf Code (main.tex)",
        data=latex_code,
        file_name=tailored.get("filename", "main.tex"),
        mime="text/plain",
        use_container_width=True,
    )


def display_results(data):
    """Render analysis results returned by FastAPI."""

    job = data.get("job_requirements") or {}
    profile = data.get("resume_profile") or {}
    skills = data.get("skill_matches") or []
    projects = data.get("project_matches") or []
    resources = data.get("learning_resources") or []

    st.success("Analysis completed successfully!")

    st.markdown("## 📊 Analysis Overview")

    c1, c2, c3 = st.columns(3)
    c1.metric("Skills evaluated", len(skills))
    c2.metric("Projects analyzed", len(projects))
    c3.metric("Learning resources", len(resources))

    with st.expander("💼 Job Requirements", expanded=True):
        st.write("**Job title:**", job.get("job_title", "Unknown"))
        st.write("**Company:**", job.get("company", "Unknown"))

        left, right = st.columns(2)

        with left:
            st.markdown("**Required skills**")
            show_list(job.get("required_skills", []))

        with right:
            st.markdown("**Preferred skills**")
            show_list(job.get("preferred_skills", []))

        st.markdown("**Responsibilities**")
        show_list(job.get("responsibilities", []))

    with st.expander("👤 Candidate Profile", expanded=True):
        st.write("**Name:**", profile.get("name") or "Not detected")

        left, right = st.columns(2)

        with left:
            st.markdown("**Skills**")
            show_list(profile.get("skills", []))

            st.markdown("**Education**")
            show_list(profile.get("education", []))

        with right:
            st.markdown("**Experience**")
            show_list(profile.get("experience", []))

            st.markdown("**Certifications**")
            show_list(profile.get("certifications", []))

        st.markdown("**Projects found in resume**")
        show_list(profile.get("projects", []))

    st.markdown("## 🎯 Skill Match Analysis")

    if not skills:
        st.info("No skill matches were returned.")
    else:
        for match in skills:
            skill = match.get("skill", "Unknown skill")
            status = match.get("status", "unknown")

            with st.container(border=True):
                left, right = st.columns([3, 1])

                with left:
                    st.markdown(f"**{skill}**")

                with right:
                    if status == "present":
                        st.success("Present")
                    elif status == "partial":
                        st.warning("Partial")
                    elif status == "not_mentioned":
                        st.info("Not mentioned")
                    else:
                        st.write(status)

                if match.get("evidence"):
                    st.write(
                        "**Resume evidence:**",
                        match["evidence"],
                    )

                if match.get("explanation"):
                    st.write(match["explanation"])

    with st.expander("📌 Skills to Improve or Verify"):
        show_list(
            data.get("missing_or_weak_skills", []),
            "No skills were flagged for improvement.",
        )

    st.markdown("## 🚀 Project Relevance Ranking")

    if not projects:
        st.info("No projects were ranked.")
    else:
        for index, project in enumerate(projects, start=1):
            name = project.get(
                "project_name",
                f"Project {index}",
            )
            score = project.get("relevance_score", 0)

            with st.container(border=True):
                st.markdown(f"### {index}. {name}")

                st.progress(
                    max(0, min(100, int(score))) / 100,
                    text=f"Relevance score: {score}/100",
                )

                st.write(
                    "**Matched skills:**",
                    ", ".join(project.get("matched_skills", []))
                    or "None listed",
                )

                st.write(project.get("explanation", ""))

    st.markdown("## 📚 Personalized Learning Roadmap")

    if not resources:
        st.info(
            "No learning resources were returned. "
            "This can happen when no skills were flagged."
        )
    else:
        for index, resource in enumerate(resources, start=1):
            title = resource.get(
                "resource_name",
                "Learning resource",
            )
            skill = resource.get("skill", "General")
            priority = resource.get("priority", "Not specified")

            with st.container(border=True):
                st.markdown(f"### {index}. {title}")
                st.write(
                    f"**Skill:** {skill} | **Priority:** {priority}"
                )

                if resource.get("reason"):
                    st.write(
                        "**Why this resource?**",
                        resource["reason"],
                    )

                if resource.get("resource_type"):
                    st.write(
                        "**Type:**",
                        resource["resource_type"],
                    )

                url = resource.get("resource_url", "")

                if url.startswith(("https://", "http://")):
                    st.markdown(
                        f"[Open learning resource]({url})"
                    )
                elif url:
                    st.caption(f"URL needs verification: {url}")

                topics = resource.get("topics", [])

                if topics:
                    st.write("**Topics to cover:**")
                    show_list(topics)

                if resource.get("practice_task"):
                    st.write(
                        "**Practice task:**",
                        resource["practice_task"],
                    )

    # New feature: show the JD-tailored Overleaf resume.
    display_tailored_resume(data)

    st.markdown("## 💾 Export Results")

    st.download_button(
        label="Download Analysis as JSON",
        data=json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        file_name="resumeai_analysis.json",
        mime="application/json",
        use_container_width=True,
    )


with st.sidebar:
    st.title("📄 ResumeAI")
    st.caption("AI-powered resume analysis")

    st.markdown("---")
    st.markdown("### How it works")
    st.write("1. Upload your resume.")
    st.write("2. Upload the target job description.")
    st.write("3. Run AI analysis.")
    st.write("4. Review skill gaps, projects and learning resources.")
    st.write("5. Download your tailored Overleaf resume.")

    st.markdown("---")
    st.caption("Powered by FastAPI, Gemini, LangChain and RAG.")


st.markdown(
    """
    <div class="hero">
        <h1>ResumeAI</h1>
        <p>
            Analyze your resume against a job description, discover skill gaps,
            rank relevant projects, and generate a tailored resume with complete
            Overleaf-ready LaTeX code.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("## Upload Your Documents")

col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader(
        "📄 Upload your resume",
        type=["pdf"],
        key="resume_pdf",
        help="Upload your current resume as a PDF.",
    )

with col2:
    jd_file = st.file_uploader(
        "💼 Upload the job description",
        type=["pdf"],
        key="jd_pdf",
        help="Upload the target job description as a PDF.",
    )

st.caption("Maximum file size: 10 MB per PDF.")

analyze_clicked = st.button(
    "✨ Analyze & Generate Tailored Resume",
    type="primary",
    use_container_width=True,
    disabled=(resume_file is None or jd_file is None),
)

if analyze_clicked:
    if resume_file is None or jd_file is None:
        st.error("Please upload both PDF files.")

    elif resume_file.size > 10 * 1024 * 1024:
        st.error("Resume PDF must be 10 MB or smaller.")

    elif jd_file.size > 10 * 1024 * 1024:
        st.error("Job description PDF must be 10 MB or smaller.")

    else:
        files = {
            "resume": (
                resume_file.name,
                resume_file.getvalue(),
                "application/pdf",
            ),
            "jd": (
                jd_file.name,
                jd_file.getvalue(),
                "application/pdf",
            ),
        }

        try:
            with st.spinner(
                "Analyzing documents, matching skills, ranking projects "
                "and generating Overleaf code... This may take a while."
            ):
                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=(15, 600),
                )

            if response.ok:
                st.session_state["resumeai_result"] = response.json()

            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get(
                        "detail",
                        str(error_data),
                    )
                except ValueError:
                    error_message = response.text[:1500]

                st.error(
                    f"Backend returned HTTP {response.status_code}: "
                    f"{error_message}"
                )

                if (
                    response.status_code == 429
                    or "429" in str(error_message)
                ):
                    st.warning(
                        "Gemini API quota may be exhausted. "
                        "Wait for the quota reset before trying again."
                    )

        except requests.exceptions.ConnectTimeout:
            st.error(
                "Could not connect to the backend in time. "
                "Check that FastAPI is running on port 8000."
            )

        except requests.exceptions.ReadTimeout:
            st.error(
                "The analysis took too long. Check the backend "
                "terminal for the exact error."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to FastAPI. Start the backend first "
                "and verify that http://127.0.0.1:8000 is reachable."
            )

        except requests.exceptions.RequestException as exc:
            st.error(f"Request failed: {exc}")


# Keep previous results visible after Streamlit reruns.
if "resumeai_result" in st.session_state:
    st.markdown("---")
    display_results(st.session_state["resumeai_result"])

st.markdown("---")
st.caption(
    "ResumeAI • Review all generated details before applying. "
    "Only use skills and project work you can truthfully explain."
)
