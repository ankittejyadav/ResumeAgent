import pathlib
import frontmatter

MODEL_FOR_SKILL = {
    "resume-tailor": "claude-sonnet-4-6",
    "cover-letter": "claude-sonnet-4-6",
    "interview-prep": "claude-sonnet-4-6",
    "company-research": "claude-haiku-4-5-20251001",
    "ats-scorer": "claude-haiku-4-5-20251001",
}

TOOLS_FOR_SKILL = {
    "company-research": ["web_search"],
}


def load_skills(root: str = "skills") -> list[dict]:
    out = []
    for p in sorted(pathlib.Path(root).glob("*/SKILL.md")):
        post = frontmatter.load(str(p))
        name = post["name"]
        desc = post["description"]
        out.append(
            {
                "name": name,
                "description": desc,
                "prompt": post.content,
                "model": MODEL_FOR_SKILL.get(name, "claude-sonnet-4-6"),
                "tools": TOOLS_FOR_SKILL.get(name, []),
            }
        )
    return out
