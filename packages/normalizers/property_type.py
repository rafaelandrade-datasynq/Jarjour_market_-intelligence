from packages.normalizers.text import clean_text


def infer_property_type(*, search_run_tipo: str = "", raw_title: str = "") -> str:
    explicit = clean_text(search_run_tipo)
    if explicit:
        return explicit

    title = clean_text(raw_title).lower()
    if "loja" in title:
        return "Loja"
    if "casa comercial" in title or "casa" in title:
        return "Casa Comercial"
    if "andar" in title:
        return "Andar Corporativo"
    if "conjunto" in title:
        return "Conjunto"
    if "sala" in title:
        return "Sala"
    return "Nao identificado"
