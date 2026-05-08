from packages.normalizers.text import clean_text

KNOWN_NEIGHBORHOODS = [
    "Asa Sul",
    "Asa Norte",
    "Lago Sul",
    "Lago Norte",
    "Noroeste",
    "Sudoeste",
    "Setor Comercial Norte",
    "Setor Comercial Sul",
    "Setor Bancario Sul",
    "Setor Bancário Sul",
    "Brasilia",
    "Brasília",
]


def infer_neighborhood(
    *,
    search_run_bairro: str = "",
    raw_address: str = "",
    raw_title: str = "",
    raw_description: str = "",
) -> str:
    explicit = clean_text(search_run_bairro)
    if explicit:
        return explicit

    haystack = " ".join(
        clean_text(value) for value in [raw_address, raw_title, raw_description] if value
    ).lower()
    for neighborhood in KNOWN_NEIGHBORHOODS:
        if neighborhood.lower() in haystack:
            return neighborhood
    return ""
