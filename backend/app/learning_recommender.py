
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

from app.llm import get_llm


class LearningResource(BaseModel):
    skill: str
    priority: str
    reason: str
    resource_name: str
    resource_type: str
    resource_url: str
    topics: list[str] = Field(default_factory=list)
    practice_task: str


class LearningPlan(BaseModel):
    recommendations: list[LearningResource] = Field(
        default_factory=list
    )


def recommend_resources(
    missing_skills: list[str],
    job_title: str,
    company: str,
) -> list[dict]:
    if not missing_skills:
        return []

    llm = get_llm().with_structured_output(LearningPlan)

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            """
            You are an expert technical learning advisor.

            Recommend the best learning resources for a candidate
            preparing for a specific job.

            You may recommend:
            - YouTube channels and specific playlists
            - Official documentation
            - Reputable interactive learning websites
            - High-quality courses and tutorials

            Select resources based on the candidate's skill gaps,
            the target role, beginner-friendliness, and practical value.

            Prefer trusted, established educational sources.
            Recommend a mix of video and written resources where useful.
            Avoid recommending many resources that teach the same thing.

            Return a small, focused set of recommendations.
            Prioritize skills that are important for the target role.

            CRITICAL URL RULE:
            Only provide a direct URL if you know it with high confidence.
            Never invent a playlist ID, video ID, course URL, or webpage.
            If you are unsure of a direct URL, provide a search URL for
            the exact resource on YouTube or the relevant official site.
            Be transparent when a link still needs verification.

            Do not assume a skill is absent just because it is not
            mentioned in the resume. Describe it as a potential gap.
            """
        ),
        (
            "human",
            """
            Target job title: {job_title}
            Company: {company}

            Skills needing improvement or verification:
            {skills}

            Recommend relevant learning resources for these skills.
            Include the resource name, type, URL, topics to study,
            priority, reason, and one practical task.
            """
        ),
    ])

    chain = prompt | llm

    result = chain.invoke({
        "job_title": job_title,
        "company": company,
        "skills": "\n".join(
            f"- {skill}" for skill in missing_skills
        ),
    })

    return [
        resource.model_dump()
        for resource in result.recommendations
    ]
