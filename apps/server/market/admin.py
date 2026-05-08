from django.contrib import admin

from .models import Listing, ListingReview, PriceSnapshot, RawListing, SearchRun


@admin.register(SearchRun)
class SearchRunAdmin(admin.ModelAdmin):
    list_display = (
        "source_name",
        "bairro",
        "tipo_imovel",
        "finalidade",
        "status",
        "total_raw_collected",
    )
    list_filter = ("source_name", "status", "finalidade")


@admin.register(RawListing)
class RawListingAdmin(admin.ModelAdmin):
    list_display = ("raw_title", "source_name", "raw_address", "captured_at")
    list_filter = ("source_name",)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "endereco",
        "bairro",
        "tipo_imovel",
        "aluguel",
        "confidence_status",
        "is_opportunity",
    )
    list_filter = ("confidence_status", "review_status", "is_opportunity", "bairro")


admin.site.register(PriceSnapshot)
admin.site.register(ListingReview)
