from exports.services import (
    CAROL_HEADERS,
    CAROL_SHEET_NAMES,
    LINK_HEADERS,
    SUMMARY_LABELS,
    build_carol_workbook,
)


def run_excel_contract_gate() -> tuple[bool, str]:
    wb = build_carol_workbook()
    if wb.sheetnames != CAROL_SHEET_NAMES:
        return False, f"Carol Excel tabs changed: {wb.sheetnames}."

    pesquisa_headers = [cell.value for cell in wb["Pesquisa Carol"][1]]
    if pesquisa_headers != CAROL_HEADERS:
        return False, "Carol Excel Pesquisa Carol headers do not match the contract."

    links_headers = [cell.value for cell in wb["Links"][1]]
    if links_headers != LINK_HEADERS:
        return False, "Carol Excel Links headers do not match the contract."

    summary_labels = {
        cell.value
        for cell in wb["Resumo da Coleta"]["A"]
        if cell.value not in {None, "Métrica", "Resumo da Coleta"}
    }
    missing_summary = [label for label in SUMMARY_LABELS if label not in summary_labels]
    if missing_summary:
        return False, f"Carol Excel summary is missing fields: {missing_summary}."

    return True, "Carol Excel workbook matches the documented contract."
