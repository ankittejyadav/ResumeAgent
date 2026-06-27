"""
tools.py — web_search (live+cache) and ats_score (pure/importable).
Keep ats_score deterministic and import-safe: it is used by eval/run_eval.py.
"""
import hashlib
import json
import os
import pathlib
import re
import unicodedata

_CACHE_DIR = pathlib.Path(".cache")


# ---------------------------------------------------------------------------
# ATS Scorer — deterministic keyword-match implementation
# ---------------------------------------------------------------------------

_SYNONYMS: dict[str, list[str]] = {
    "javascript": ["js", "node", "nodejs", "node.js"],
    "typescript": ["ts"],
    "kubernetes": ["k8s"],
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "natural language processing": ["nlp"],
    "large language model": ["llm", "llms"],
    "retrieval augmented generation": ["rag"],
    "continuous integration": ["ci"],
    "continuous deployment": ["cd"],
    "ci/cd": ["ci", "cd", "cicd", "ci-cd"],
    "postgresql": ["postgres", "pg"],
    "mongodb": ["mongo"],
    "amazon web services": ["aws"],
    "google cloud platform": ["gcp", "google cloud"],
    "microsoft azure": ["azure"],
    "python3": ["python"],
    "rest api": ["restful", "rest apis", "restful api", "restful apis"],
    "graphql": ["gql"],
    "docker": ["containerization", "containers"],
}


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return text.lower()


def _build_synonym_map() -> dict[str, str]:
    """Returns alias → canonical mapping."""
    m: dict[str, str] = {}
    for canonical, aliases in _SYNONYMS.items():
        for alias in aliases:
            m[_normalize(alias)] = _normalize(canonical)
    return m


_ALIAS_MAP = _build_synonym_map()


def _resolve(token: str) -> str:
    """Resolve a token to its canonical form via synonym map."""
    t = _normalize(token)
    return _ALIAS_MAP.get(t, t)


def _extract_keywords(job_posting: str) -> list[tuple[str, int]]:
    """
    Extract (keyword, weight) pairs from a job posting.
    Required/must-have items weight 2; preferred/nice-to-have weight 1.
    """
    text = _normalize(job_posting)

    # Patterns for tech keywords — simple but effective for demo
    tech_pattern = re.compile(
        r"\b("
        r"python|javascript|typescript|java|go|rust|c\+\+|c#|ruby|scala|kotlin|swift|"
        r"react|angular|vue|svelte|nextjs|nuxt|"
        r"fastapi|django|flask|express|spring|rails|"
        r"postgresql|mysql|mongodb|redis|elasticsearch|dynamodb|cassandra|"
        r"docker|kubernetes|k8s|terraform|ansible|helm|"
        r"aws|gcp|azure|lambda|s3|ec2|cloud|"
        r"machine learning|ml|ai|nlp|llm|rag|"
        r"ci/cd|github actions|jenkins|circleci|"
        r"sql|nosql|graphql|rest api|grpc|"
        r"git|linux|bash|"
        r"agile|scrum|kanban|"
        r"typescript|node\.?js|"
        r"spark|kafka|airflow|dbt|"
        r"pytorch|tensorflow|sklearn|scikit.learn|"
        r"langchain|openai|anthropic"
        r")\b",
        re.IGNORECASE,
    )

    # Years/seniority patterns
    seniority_pattern = re.compile(
        r"\b(\d+\+?\s*years?|senior|lead|staff|principal|architect|manager)\b",
        re.IGNORECASE,
    )

    # Determine weight: lines with "required"/"must" get weight 2
    keyword_weights: dict[str, int] = {}
    for line in job_posting.splitlines():
        line_norm = _normalize(line)
        weight = 2 if any(w in line_norm for w in ["required", "must have", "must-have", "you have", "you bring"]) else 1
        for m in tech_pattern.finditer(line):
            kw = _resolve(m.group(0))
            keyword_weights[kw] = max(keyword_weights.get(kw, 0), weight)
        for m in seniority_pattern.finditer(line):
            kw = _normalize(m.group(0))
            keyword_weights[kw] = max(keyword_weights.get(kw, 0), weight)

    # Deduplicate synonyms: keep the canonical form with highest weight
    result: dict[str, int] = {}
    for kw, w in keyword_weights.items():
        canonical = _resolve(kw)
        result[canonical] = max(result.get(canonical, 0), w)

    return [(kw, w) for kw, w in result.items()]


def ats_score(resume: str, job_posting: str) -> dict:
    """
    Compute a keyword-match ATS score.
    Returns: {value: int, matched_keywords: list[str], missing_keywords: list[str]}
    Pure and importable — no network calls, no model calls.
    """
    keywords = _extract_keywords(job_posting)
    if not keywords:
        return {"value": 0, "matched_keywords": [], "missing_keywords": []}

    resume_norm = _normalize(resume)

    matched: list[str] = []
    missing: list[str] = []
    weighted_matched = 0
    weighted_total = 0

    for kw, weight in keywords:
        weighted_total += weight
        # Check canonical and all aliases
        aliases = [kw] + [alias for alias, canon in _ALIAS_MAP.items() if canon == kw]
        found = any(
            re.search(r"\b" + re.escape(a) + r"\b", resume_norm) for a in aliases
        )
        if found:
            matched.append(kw)
            weighted_matched += weight
        else:
            missing.append(kw)

    value = round(weighted_matched / weighted_total * 100) if weighted_total else 0
    return {
        "value": value,
        "matched_keywords": sorted(matched),
        "missing_keywords": sorted(missing),
    }


# ---------------------------------------------------------------------------
# Web search — Tavily (primary) or duckduckgo-search (fallback), with cache
# ---------------------------------------------------------------------------

def _cache_key(query: str) -> pathlib.Path:
    h = hashlib.sha256(query.encode()).hexdigest()[:16]
    return _CACHE_DIR / f"{h}.json"


def _load_cache(query: str) -> str | None:
    p = _cache_key(query)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))["result"]
        except Exception:
            return None
    return None


def _save_cache(query: str, result: str) -> None:
    _CACHE_DIR.mkdir(exist_ok=True)
    _cache_key(query).write_text(
        json.dumps({"query": query, "result": result}), encoding="utf-8"
    )


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web for `query`. Returns a compact text summary.
    Caches results to .cache/ keyed by query hash.
    Respects MAESTRO_OFFLINE env var — returns stub if set to 1.
    """
    if os.getenv("MAESTRO_OFFLINE", "0") == "1":
        return f"[OFFLINE MODE] Web search skipped for: {query}"

    cached = _load_cache(query)
    if cached:
        return cached

    result = _live_search(query, max_results)
    _save_cache(query, result)
    return result


def _live_search(query: str, max_results: int) -> str:
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if tavily_key:
        return _tavily_search(query, max_results, tavily_key)
    return _duckduckgo_search(query, max_results)


def _tavily_search(query: str, max_results: int, api_key: str) -> str:
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=api_key)
        response = client.search(query, max_results=max_results)
        results = response.get("results", [])
        lines = []
        for r in results[:max_results]:
            title = r.get("title", "")
            url = r.get("url", "")
            content = r.get("content", "")[:300]
            lines.append(f"**{title}** ({url})\n{content}")
        return "\n\n".join(lines) or "No results found."
    except Exception as e:
        return f"Tavily search error: {e}"


def _duckduckgo_search(query: str, max_results: int) -> str:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        lines = []
        for r in results:
            title = r.get("title", "")
            href = r.get("href", "")
            body = r.get("body", "")[:300]
            lines.append(f"**{title}** ({href})\n{body}")
        return "\n\n".join(lines) or "No results found."
    except Exception as e:
        return f"DuckDuckGo search error: {e}"
