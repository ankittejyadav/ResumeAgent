"""
orchestrator.py — JobForge multi-agent orchestrator.

Uses explicit Python orchestration (the spec-endorsed fallback) rather than
deepagents autonomous delegation. Each subagent is a direct Anthropic API call
using the SKILL.md body as the system prompt. This guarantees clean, reliable
events and a predictable demo — documented in ADLC.md.

deepagents is still installed (demonstrates the framework dependency) but the
explicit path is used for demo reliability.
"""
import asyncio
import os
import time
from typing import Callable, Awaitable

from dotenv import load_dotenv

load_dotenv()

from agent.events import ev
from agent.skill_loader import load_skills
from agent.tools import ats_score, web_search

try:
    import anthropic
    _anthropic_client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
except Exception:
    _anthropic_client = None

SONNET = "claude-sonnet-4-6"
HAIKU = "claude-haiku-4-5-20251001"

Emitter = Callable[[dict], Awaitable[None]]

ORCH_SYSTEM = """You are JobForge, an expert AI job-application orchestrator.

Your job is to coordinate a team of specialist subagents to produce a complete
tailored job-application kit for a candidate. You receive a resume and a job posting.

Always reason carefully and produce thorough, high-quality output for the candidate.
"""

TODO_PLAN = [
    {"id": "t1", "title": "Score original resume (ATS baseline)", "status": "pending"},
    {"id": "t2", "title": "Research company", "status": "pending"},
    {"id": "t3", "title": "Tailor resume to job posting", "status": "pending"},
    {"id": "t4", "title": "Write cover letter", "status": "pending"},
    {"id": "t5", "title": "Generate interview prep", "status": "pending"},
    {"id": "t6", "title": "Score tailored resume (ATS after)", "status": "pending"},
    {"id": "t7", "title": "Assemble final kit", "status": "pending"},
]


async def _call_model(model: str, system: str, user: str, emit: Emitter) -> str:
    """Call Anthropic API and return text. Emits token_usage events."""
    if _anthropic_client is None:
        return "[No Anthropic client — set ANTHROPIC_API_KEY]"
    try:
        msg = await _anthropic_client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        usage = msg.usage
        input_tok = getattr(usage, "input_tokens", 0)
        output_tok = getattr(usage, "output_tokens", 0)
        cost = round(
            (input_tok * (3 / 1_000_000) if "sonnet" in model else input_tok * (0.25 / 1_000_000)) +
            (output_tok * (15 / 1_000_000) if "sonnet" in model else output_tok * (1.25 / 1_000_000)),
            6,
        )
        await emit(ev("token_usage", input_tokens=input_tok, output_tokens=output_tok,
                      est_cost_usd=cost, by_model={model: input_tok + output_tok}))
        return msg.content[0].text
    except Exception as e:
        return f"[Model error: {e}]"


async def orchestrate(resume: str, job_posting: str, emit: Emitter) -> None:
    """
    Full JobForge orchestration run.
    Emits schema-compliant events per docs/02-EVENT-SCHEMA.md throughout.
    """
    t_start = time.time()
    skills = load_skills()

    # 1. run_started + skill_loaded events
    await emit(ev("run_started", run_id="", job_title="", company=""))
    for skill in skills:
        await emit(ev("skill_loaded", name=skill["name"],
                      description=skill["description"], model=skill["model"]))
        await asyncio.sleep(0.05)

    # 2. Plan
    todos = [t.copy() for t in TODO_PLAN]
    await emit(ev("plan", todos=todos))
    await asyncio.sleep(0.1)

    skill_map = {s["name"]: s for s in skills}

    async def update_todo(tid: str, status: str):
        await emit(ev("todo_update", id=tid, status=status))

    # 3. Score original resume
    await update_todo("t1", "in_progress")
    await emit(ev("log", level="info", message="Scoring original resume against job posting…"))
    before = ats_score(resume, job_posting)
    await emit(ev("score_update", phase="before", value=before["value"],
                  missing_keywords=before["missing_keywords"],
                  matched_keywords=before["matched_keywords"]))
    await update_todo("t1", "done")
    await asyncio.sleep(0.1)

    # 4. Company research
    await update_todo("t2", "in_progress")
    cr_skill = skill_map.get("company-research", {})
    await emit(ev("subagent_start", name="company-research"))
    await emit(ev("log", level="info", message="company-research subagent working…"))

    # Build context: do web searches first
    import re as _re
    company_match = _re.search(r"(?:at|@|company[:\s]+|employer[:\s]+)\s*([A-Z][^\n,]{2,40})", job_posting)
    company_name = company_match.group(1).strip() if company_match else "the company"
    search_results = []
    for q in [
        f"{company_name} mission about page",
        f"{company_name} recent news 2026",
        f"{company_name} culture values",
    ]:
        search_results.append(web_search(q))
    search_context = "\n\n".join(search_results)

    company_prompt = cr_skill.get("prompt", "Research the company.")
    company_result = await _call_model(
        HAIKU,
        company_prompt,
        f"Job Posting:\n{job_posting}\n\nWeb Search Results:\n{search_context}\n\nProduce the company research report.",
        emit,
    )
    await emit(ev("subagent_finish", name="company-research", summary="Company research complete"))
    await emit(ev("deliverable", kind="company_research", title="Company Research",
                  content_markdown=company_result))
    await update_todo("t2", "done")
    await asyncio.sleep(0.1)

    # 5. Tailor resume
    await update_todo("t3", "in_progress")
    rt_skill = skill_map.get("resume-tailor", {})
    await emit(ev("subagent_start", name="resume-tailor"))
    await emit(ev("log", level="info", message="resume-tailor subagent working…"))
    resume_prompt = rt_skill.get("prompt", "Tailor this resume.")
    tailored_resume = await _call_model(
        SONNET,
        resume_prompt,
        f"Resume:\n{resume}\n\nJob Posting:\n{job_posting}\n\nProduce the tailored resume.",
        emit,
    )
    await emit(ev("subagent_finish", name="resume-tailor", summary="Resume tailored"))
    await emit(ev("deliverable", kind="tailored_resume", title="Tailored Resume",
                  content_markdown=tailored_resume))
    await update_todo("t3", "done")
    await asyncio.sleep(0.1)

    # 6. Cover letter
    await update_todo("t4", "in_progress")
    cl_skill = skill_map.get("cover-letter", {})
    await emit(ev("subagent_start", name="cover-letter"))
    await emit(ev("log", level="info", message="cover-letter subagent working…"))
    cover_prompt = cl_skill.get("prompt", "Write a cover letter.")
    cover_letter = await _call_model(
        SONNET,
        cover_prompt,
        f"Resume:\n{resume}\n\nJob Posting:\n{job_posting}\n\nCompany Research:\n{company_result}\n\nWrite the cover letter.",
        emit,
    )
    await emit(ev("subagent_finish", name="cover-letter", summary="Cover letter written"))
    await emit(ev("deliverable", kind="cover_letter", title="Cover Letter",
                  content_markdown=cover_letter))
    await update_todo("t4", "done")
    await asyncio.sleep(0.1)

    # 7. Interview prep
    await update_todo("t5", "in_progress")
    ip_skill = skill_map.get("interview-prep", {})
    await emit(ev("subagent_start", name="interview-prep"))
    await emit(ev("log", level="info", message="interview-prep subagent working…"))
    interview_prompt = ip_skill.get("prompt", "Generate interview prep.")
    interview_prep = await _call_model(
        SONNET,
        interview_prompt,
        f"Resume:\n{resume}\n\nJob Posting:\n{job_posting}\n\nCompany Research:\n{company_result}\n\nGenerate interview prep.",
        emit,
    )
    await emit(ev("subagent_finish", name="interview-prep", summary="Interview prep ready"))
    await emit(ev("deliverable", kind="interview_prep", title="Interview Prep",
                  content_markdown=interview_prep))
    await update_todo("t5", "done")
    await asyncio.sleep(0.1)

    # 8. Score tailored resume
    await update_todo("t6", "in_progress")
    await emit(ev("log", level="info", message="Scoring tailored resume…"))
    after = ats_score(tailored_resume, job_posting)
    await emit(ev("score_update", phase="after", value=after["value"],
                  missing_keywords=after["missing_keywords"],
                  matched_keywords=after["matched_keywords"]))
    await update_todo("t6", "done")
    await asyncio.sleep(0.1)

    # 9. Done
    await update_todo("t7", "done")
    elapsed = round(time.time() - t_start, 1)
    await emit(ev("log", level="info", message=f"JobForge complete in {elapsed}s — ATS {before['value']}% → {after['value']}%"))
    await emit(ev("done",
                  before=before["value"],
                  after=after["value"],
                  deliverable_kinds=["company_research", "tailored_resume", "cover_letter", "interview_prep"],
                  elapsed_s=elapsed))
