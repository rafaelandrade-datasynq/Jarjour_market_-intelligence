from dataclasses import dataclass
from decimal import Decimal

from market.models import ConfidenceStatus, RawListing, ReviewStatus

from packages.normalizers.area import parse_area_m2
from packages.normalizers.location import infer_neighborhood
from packages.normalizers.money import parse_brl_money
from packages.normalizers.property_type import infer_property_type
from packages.normalizers.text import clean_text


@dataclass(frozen=True)
class NormalizedListingData:
    source_name: str
    source_url: str
    endereco: str
    bairro: str
    tipo_imovel: str
    finalidade: str
    area_m2: Decimal | None
    aluguel: Decimal | None
    aluguel_m2: Decimal | None
    condominio: Decimal | None
    condominio_m2: Decimal | None
    contato: str
    telefone: str
    observacoes: str
    confidence_status: str
    review_status: str
    is_opportunity: bool
    opportunity_score: Decimal


def normalize_raw_listing(raw_listing: RawListing) -> NormalizedListingData:
    search_run = raw_listing.search_run
    endereco = clean_text(raw_listing.raw_address)
    title = clean_text(raw_listing.raw_title)
    description = clean_text(raw_listing.raw_description)
    area_m2 = parse_area_m2(raw_listing.raw_area)
    aluguel = parse_brl_money(raw_listing.raw_price)
    condominio = parse_brl_money(raw_listing.raw_condominium)
    bairro = infer_neighborhood(
        search_run_bairro=search_run.bairro,
        raw_address=endereco,
        raw_title=title,
        raw_description=description,
    )
    tipo_imovel = infer_property_type(
        search_run_tipo=search_run.tipo_imovel,
        raw_title=title,
    )
    aluguel_m2 = _divide_money(aluguel, area_m2)
    condominio_m2 = _divide_money(condominio, area_m2)

    return NormalizedListingData(
        source_name=raw_listing.source_name,
        source_url=raw_listing.source_url,
        endereco=endereco,
        bairro=bairro,
        tipo_imovel=tipo_imovel,
        finalidade=clean_text(search_run.finalidade),
        area_m2=area_m2,
        aluguel=aluguel,
        aluguel_m2=aluguel_m2,
        condominio=condominio,
        condominio_m2=condominio_m2,
        contato=clean_text(raw_listing.raw_contact),
        telefone=clean_text(raw_listing.raw_phone),
        observacoes=_build_notes(title=title, description=description),
        confidence_status=_classify_confidence(
            aluguel=aluguel,
            area_m2=area_m2,
            bairro=bairro,
            endereco=endereco,
            source_url=raw_listing.source_url,
        ),
        review_status=ReviewStatus.NOT_REVIEWED,
        is_opportunity=False,
        opportunity_score=Decimal("0.00"),
    )


def _divide_money(value: Decimal | None, area_m2: Decimal | None) -> Decimal | None:
    if value is None or area_m2 in (None, Decimal("0")):
        return None
    return (value / area_m2).quantize(Decimal("0.01"))


def _classify_confidence(
    *,
    aluguel: Decimal | None,
    area_m2: Decimal | None,
    bairro: str,
    endereco: str,
    source_url: str,
) -> str:
    if aluguel is None:
        return ConfidenceStatus.INCOMPLETE
    if area_m2 is None:
        return ConfidenceStatus.REVIEW
    if not bairro or not endereco:
        return ConfidenceStatus.REVIEW
    if source_url or len(endereco) >= 6:
        return ConfidenceStatus.RELIABLE
    return ConfidenceStatus.REVIEW


def _build_notes(*, title: str, description: str) -> str:
    if title and description:
        return f"{title}. {description}"
    return title or description
