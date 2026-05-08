from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from market.models import (
    ConfidenceStatus,
    Listing,
    PriceSnapshot,
    RawListing,
    ReviewStatus,
    SearchRun,
)
from market.services.totals import recalculate_search_run_totals

DEMO_LISTINGS = [
    {
        "bairro": "Asa Sul",
        "tipo": "Loja",
        "endereco": "CLS 308 Bloco B",
        "area": Decimal("84"),
        "aluguel": Decimal("8900"),
        "condominio": Decimal("980"),
        "status": ConfidenceStatus.RELIABLE,
        "review": ReviewStatus.OPPORTUNITY,
        "score": Decimal("91.00"),
        "opportunity": True,
    },
    {
        "bairro": "Lago Sul",
        "tipo": "Casa Comercial",
        "endereco": "QI 11 Conjunto 7",
        "area": Decimal("420"),
        "aluguel": Decimal("28000"),
        "condominio": Decimal("0"),
        "status": ConfidenceStatus.REVIEW,
        "review": ReviewStatus.NEEDS_REVIEW,
        "score": Decimal("73.00"),
        "opportunity": False,
    },
    {
        "bairro": "Noroeste",
        "tipo": "Sala",
        "endereco": "CLNW 10/11 Bloco C",
        "area": Decimal("46"),
        "aluguel": Decimal("4200"),
        "condominio": Decimal("620"),
        "status": ConfidenceStatus.RELIABLE,
        "review": ReviewStatus.APPROVED,
        "score": Decimal("82.00"),
        "opportunity": True,
    },
    {
        "bairro": "Asa Norte",
        "tipo": "Sala",
        "endereco": "SCN Quadra 2",
        "area": Decimal("31"),
        "aluguel": Decimal("2100"),
        "condominio": Decimal("540"),
        "status": ConfidenceStatus.INCOMPLETE,
        "review": ReviewStatus.NEEDS_REVIEW,
        "score": Decimal("48.00"),
        "opportunity": False,
    },
    {
        "bairro": "Sudoeste",
        "tipo": "Loja",
        "endereco": "CLSW 103 Bloco A",
        "area": Decimal("62"),
        "aluguel": Decimal("7600"),
        "condominio": Decimal("700"),
        "status": ConfidenceStatus.PROBABLE_DUPLICATE,
        "review": ReviewStatus.NOT_REVIEWED,
        "score": Decimal("55.00"),
        "opportunity": False,
    },
    {
        "bairro": "Asa Sul",
        "tipo": "Sala",
        "endereco": "",
        "area": None,
        "aluguel": Decimal("3500"),
        "condominio": None,
        "status": ConfidenceStatus.DISCARDED,
        "review": ReviewStatus.REJECTED,
        "score": Decimal("0.00"),
        "opportunity": False,
    },
]


@transaction.atomic
def create_demo_search_run() -> SearchRun:
    run = SearchRun.objects.create(
        source_name="demo",
        bairro="Plano Piloto",
        tipo_imovel="Comercial",
        finalidade="Aluguel",
        status="COMPLETED",
        finished_at=timezone.now(),
    )

    for index, item in enumerate(DEMO_LISTINGS, start=1):
        raw = RawListing.objects.create(
            search_run=run,
            source_name="demo",
            source_url=f"https://example.local/jarjour/demo/{index}",
            raw_title=f"{item['tipo']} para aluguel em {item['bairro']}",
            raw_description="Registro demonstrativo para testar dashboard, historico e exportacao.",
            raw_address=item["endereco"] or f"Endereco incompleto - {item['bairro']}",
            raw_price=f"R$ {item['aluguel']}",
            raw_area=f"{item['area']} m2" if item["area"] else "",
            raw_condominium=f"R$ {item['condominio']}" if item["condominio"] is not None else "",
            raw_contact="Equipe comercial demo",
            raw_phone="(61) 3000-0000",
            raw_payload_json={"demo": True, "row": index},
        )
        listing = Listing.objects.create(
            raw_listing=raw,
            source_name=raw.source_name,
            source_url=raw.source_url,
            endereco=item["endereco"],
            bairro=item["bairro"],
            tipo_imovel=item["tipo"],
            finalidade="Aluguel",
            area_m2=item["area"],
            aluguel=item["aluguel"],
            condominio=item["condominio"],
            contato="Equipe comercial demo",
            telefone="(61) 3000-0000",
            observacoes="Dado ficticio criado para validacao do MVP.",
            confidence_status=item["status"],
            review_status=item["review"],
            is_opportunity=item["opportunity"],
            opportunity_score=item["score"],
        )
        PriceSnapshot.objects.create(
            listing=listing,
            aluguel=listing.aluguel,
            condominio=listing.condominio,
            area_m2=listing.area_m2,
            aluguel_m2=listing.aluguel_m2,
            condominio_m2=listing.condominio_m2,
        )

    return recalculate_search_run_totals(run)
