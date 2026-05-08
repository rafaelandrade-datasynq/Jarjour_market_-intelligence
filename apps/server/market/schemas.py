from datetime import datetime
from decimal import Decimal

from ninja import Schema


class SearchRunSchema(Schema):
    id: int
    source_name: str
    bairro: str
    tipo_imovel: str
    finalidade: str
    status: str
    total_raw_collected: int
    total_normalized: int
    total_reliable: int
    total_review: int
    total_incomplete: int
    total_probable_duplicates: int
    total_discarded: int
    total_opportunities: int
    started_at: datetime
    finished_at: datetime | None


class ListingSchema(Schema):
    id: int
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


class ListingReviewRequestSchema(Schema):
    decision: str
    comment: str = ""
    reviewed_by: str = "Carol"


class ListingReviewDetailSchema(Schema):
    id: int
    decision: str
    comment: str
    reviewed_by: str
    created_at: datetime


class ListingReviewResponseSchema(Schema):
    id: int
    review_status: str
    is_opportunity: bool
    last_review: ListingReviewDetailSchema
    message: str


class NormalizationRunRequestSchema(Schema):
    search_run_id: int | None = None
    limit: int | None = None


class NormalizationRunResponseSchema(Schema):
    raw_processed: int
    listings_created: int
    listings_updated: int
    reliable: int
    review: int
    incomplete: int
    probable_duplicates: int
    message: str


class ErrorSchema(Schema):
    detail: str


class MarketSummarySchema(Schema):
    total_raw_collected: int
    total_normalized: int
    total_raw_without_listing: int
    total_reliable: int
    total_review: int
    total_incomplete: int
    total_probable_duplicates: int
    total_discarded: int
    total_opportunities: int
    average_rent_m2: Decimal | None
