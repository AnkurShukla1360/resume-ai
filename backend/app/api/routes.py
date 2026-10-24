
import traceback
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.pdf_parser import extract_pdf_text
from app.jd_analyzer import analyze_jd
from app.resume_analyzer import analyze_resume
from app.rag.vector_store import build_resume_vector_store
from app.matcher import match_skills, rank_projects
from app.learning_recommender import recommend_resources
from app.resume_generator import generate_tailored_resume


router = APIRouter(prefix="/api", tags=["ResumeAI"])


async def read_pdf(file: UploadFile) -> bytes:
    """Validate and read an uploaded PDF."""

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a valid PDF file.",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail=f"{file.filename} is empty.",
        )

    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="PDF must be 10 MB or smaller.",
        )

    return content


@router.post("/analyze")
async def analyze_documents(
    resume: UploadFile = File(...),
    jd: UploadFile = File(...),
):
    """Analyze resume vs JD and generate an Overleaf-ready resume."""

    try:
        # Step 1: Validate and extract PDFs.
        resume_bytes = await read_pdf(resume)
        jd_bytes = await read_pdf(jd)

        print("Step 1/8: Extracting PDF text...")

        resume_text = extract_pdf_text(resume_bytes)
        jd_text = extract_pdf_text(jd_bytes)

        if not resume_text.strip():
            raise ValueError(
                "Could not extract readable text from the resume PDF."
            )

        if not jd_text.strip():
            raise ValueError(
                "Could not extract readable text from the JD PDF."
            )

        print(
            f"Resume characters: {len(resume_text)}, "
            f"JD characters: {len(jd_text)}"
        )

        # Step 2: Analyze the job description.
        print("Step 2/8: Analyzing job description...")

        job_requirements = analyze_jd(jd_text)

        # Step 3: Analyze the resume.
        print("Step 3/8: Analyzing resume...")

        resume_profile = analyze_resume(resume_text)

        # Step 4: Build the resume vector store.
        print("Step 4/8: Building resume vector store...")

        analysis_id = str(uuid4())

        vector_store = build_resume_vector_store(
            resume_text=resume_text,
            analysis_id=analysis_id,
        )

        # Step 5: Match skills.
        print("Step 5/8: Matching skills...")

        skill_matches = match_skills(
            jd=job_requirements,
            resume=resume_profile,
            vector_store=vector_store,
        )

        # Step 6: Rank existing projects.
        print("Step 6/8: Ranking existing projects...")

        project_matches = rank_projects(
            jd=job_requirements,
            resume=resume_profile,
            vector_store=vector_store,
        )

        # Step 7: Generate learning recommendations.
        print("Step 7/8: Generating learning recommendations...")

        missing_skills = [
            match.skill
            for match in skill_matches
            if match.status in ("partial", "not_mentioned")
        ]

        learning_resources = recommend_resources(
            missing_skills=missing_skills,
            job_title=job_requirements.job_title,
            company=job_requirements.company,
        )

        # Step 8: Generate the tailored resume and LaTeX source.
        print(
            "Step 8/8: Generating JD-tailored resume and LaTeX..."
        )

        tailored_resume = generate_tailored_resume(
            resume_text=resume_text,
            resume_profile=resume_profile,
            job_requirements=job_requirements,
            skill_matches=skill_matches,
            project_matches=project_matches,
        )

        print("Analysis and resume generation completed successfully!")

        return {
            "analysis_id": analysis_id,
            "message": (
                "Resume analysis and tailored LaTeX generation completed."
            ),
            "job_requirements": job_requirements.model_dump(),
            "resume_profile": resume_profile.model_dump(),
            "skill_matches": [
                item.model_dump() for item in skill_matches
            ],
            "missing_or_weak_skills": missing_skills,
            "project_matches": [
                item.model_dump() for item in project_matches
            ],
            "learning_resources": learning_resources,
            "tailored_resume": tailored_resume,
            "resume_characters": len(resume_text),
            "jd_characters": len(jd_text),
        }

    except HTTPException:
        raise

    except ValueError as exc:
        print(f"Validation/extraction error: {exc}")
        traceback.print_exc()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        print(
            f"\nAnalysis failed: {type(exc).__name__}: {exc}"
        )
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis failed. Check the backend terminal "
                "for the exact traceback."
            ),
        ) from exc

    finally:
        await resume.close()
        await jd.close()
