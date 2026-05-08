from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from market.models import ConfidenceStatus, Listing
from market.selectors.summary import market_summary
from market.services.review import review_listing


def _filtered_listings(request):
    listings = Listing.objects.all()
    for field in ["bairro", "tipo_imovel", "finalidade", "confidence_status"]:
        value = request.GET.get(field)
        if value:
            listings = listings.filter(**{field: value})
    return listings


def dashboard(request):
    listings = _filtered_listings(request)
    bairros = Listing.objects.exclude(bairro="").values_list("bairro", flat=True).distinct()
    tipos = Listing.objects.exclude(tipo_imovel="").values_list("tipo_imovel", flat=True).distinct()
    finalidades = (
        Listing.objects.exclude(finalidade="").values_list("finalidade", flat=True).distinct()
    )
    context = {
        "summary": market_summary(),
        "listings": listings[:100],
        "bairros": bairros,
        "tipos": tipos,
        "finalidades": finalidades,
        "statuses": ConfidenceStatus.choices,
    }
    return render(request, "dashboard/index.html", context)


def listings_table(request):
    return render(request, "dashboard/_table.html", {"listings": _filtered_listings(request)[:100]})


@require_POST
def review_listing_action(request, listing_id: int):
    listing = get_object_or_404(Listing, id=listing_id)
    try:
        review_listing(
            listing=listing,
            decision=request.POST.get("decision", ""),
            comment=request.POST.get("comment", ""),
            reviewed_by=request.POST.get("reviewed_by", "Carol"),
        )
    except ValueError as exc:
        messages.error(request, str(exc))
    else:
        messages.success(request, "Revisão registrada com rastreabilidade.")
    return redirect("dashboard:index")
