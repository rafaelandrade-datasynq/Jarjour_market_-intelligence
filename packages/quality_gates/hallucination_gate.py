from pathlib import Path

FORBIDDEN_CLAIMS = [
    "scraping real implementado",
    "df imoveis integrado",
    "wimoveis integrado",
]


def run_hallucination_gate(repo_root: Path) -> tuple[bool, str]:
    docs = [repo_root / "README.md", repo_root / "AGENTS.md"]
    text = "\n".join(path.read_text(encoding="utf-8").lower() for path in docs if path.exists())
    for claim in FORBIDDEN_CLAIMS:
        if claim in text:
            return False, f"Forbidden unsupported claim found: {claim}"
    return True, "No unsupported live-scraping claims found in top-level docs."
