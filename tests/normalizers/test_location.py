from packages.normalizers.location import infer_neighborhood
from packages.normalizers.property_type import infer_property_type
from packages.normalizers.text import clean_text


def test_clean_text_preserves_accents_and_compacts_spaces():
    assert clean_text("  Sala\n\ncomercial   Asa Sul  ") == "Sala comercial Asa Sul"


def test_infer_neighborhood_prefers_search_run_bairro():
    assert (
        infer_neighborhood(
            search_run_bairro="Noroeste",
            raw_address="CLS 308 Bloco B, Asa Sul",
        )
        == "Noroeste"
    )


def test_infer_neighborhood_from_raw_text():
    assert infer_neighborhood(raw_title="Loja para aluguel na Asa Norte") == "Asa Norte"


def test_infer_property_type_examples():
    assert infer_property_type(search_run_tipo="Comercial", raw_title="Sala") == "Comercial"
    assert infer_property_type(raw_title="Loja para aluguel") == "Loja"
    assert infer_property_type(raw_title="Sala comercial") == "Sala"
