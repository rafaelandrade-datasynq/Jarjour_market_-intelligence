from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from exports.services import build_carol_workbook_response
from ninja import Router

from market.models import Listing, SearchRun
from market.schemas import (
    ErrorSchema,
    ListingReviewRequestSchema,
    ListingReviewResponseSchema,
    ListingSchema,
    MarketSummarySchema,
    NormalizationRunRequestSchema,
    NormalizationRunResponseSchema,
    SearchRunSchema,
)
from market.selectors.summary import market_summary
from market.services.demo_data import create_demo_search_run
from market.services.normalization import normalize_pending_raw_listings, normalize_search_run
from market.services.review import review_listing

router = Router()


@router.get("/listings", response=list[ListingSchema])
def listings(request):
    return Listing.objects.select_related("raw_listing").all()[:200]


@router.get("/listings/{listing_id}", response=ListingSchema)
def listing_detail(request, listing_id: int):
    return get_object_or_404(Listing, id=listing_id)


@router.post(
    "/listings/{listing_id}/review",
    response={200: ListingReviewResponseSchema, 400: ErrorSchema},
)
def review_listing_endpoint(request, listing_id: int, payload: ListingReviewRequestSchema):
    listing = get_object_or_404(Listing, id=listing_id)
    try:
        review = review_listing(
            listing=listing,
            decision=payload.decision,
            comment=payload.comment,
            reviewed_by=payload.reviewed_by,
        )
    except ValueError as exc:
        return JsonResponse({"detail": str(exc)}, status=400)

    listing.refresh_from_db()
    return {
        "id": listing.id,
        "review_status": listing.review_status,
        "is_opportunity": listing.is_opportunity,
        "last_review": {
            "id": review.id,
            "decision": review.decision,
            "comment": review.comment,
            "reviewed_by": review.reviewed_by,
            "created_at": review.created_at,
        },
        "message": "Revisão registrada com rastreabilidade.",
    }


@router.get("/search-runs", response=list[SearchRunSchema])
def search_runs(request):
    return SearchRun.objects.all()[:100]


@router.post("/search-runs/demo", response=SearchRunSchema)
def demo_search_run(request):
    return create_demo_search_run()


@router.get("/search-runs/{search_run_id}", response=SearchRunSchema)
def search_run_detail(request, search_run_id: int):
    return get_object_or_404(SearchRun, id=search_run_id)


@router.get("/market/summary", response=MarketSummarySchema)
def summary(request):
    return market_summary()


@router.post("/normalization/run", response=NormalizationRunResponseSchema)
def normalization_run(request, payload: NormalizationRunRequestSchema | None = None):
    search_run_id = payload.search_run_id if payload is not None else None
    limit = payload.limit if payload is not None else None
    if search_run_id is not None:
        search_run = get_object_or_404(SearchRun, id=search_run_id)
        result = normalize_search_run(search_run)
    else:
        result = normalize_pending_raw_listings(limit=limit)
    return {**result, "message": "Normalizacao concluida sem apagar dados brutos."}


@router.get("/exports/carol-xlsx")
def export_carol_xlsx(request):
    return build_carol_workbook_response()
