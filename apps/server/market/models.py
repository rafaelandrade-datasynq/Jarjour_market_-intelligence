from decimal import Decimal

from django.db import models
from django.utils import timezone


class ConfidenceStatus(models.TextChoices):
    RAW = "RAW", "Bruto"
    NORMALIZED = "NORMALIZED", "Normalizado"
    RELIABLE = "RELIABLE", "Confiavel"
    REVIEW = "REVIEW", "Para revisar"
    INCOMPLETE = "INCOMPLETE", "Incompleto"
    PROBABLE_DUPLICATE = "PROBABLE_DUPLICATE", "Duplicado provavel"
    DISCARDED = "DISCARDED", "Descartado"


class ReviewStatus(models.TextChoices):
    NOT_REVIEWED = "NOT_REVIEWED", "Nao revisado"
    APPROVED = "APPROVED", "Aprovado"
    NEEDS_REVIEW = "NEEDS_REVIEW", "Precisa revisar"
    REJECTED = "REJECTED", "Rejeitado"
    OPPORTUNITY = "OPPORTUNITY", "Oportunidade"


class SearchRun(models.Model):
    source_name = models.CharField(max_length=120)
    bairro = models.CharField(max_length=120, blank=True)
    tipo_imovel = models.CharField(max_length=80, blank=True)
    finalidade = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=40, default="COMPLETED")
    started_at = models.DateTimeField(default=timezone.now)
    finished_at = models.DateTimeField(null=True, blank=True)
    total_raw_collected = models.PositiveIntegerField(default=0)
    total_normalized = models.PositiveIntegerField(default=0)
    total_reliable = models.PositiveIntegerField(default=0)
    total_review = models.PositiveIntegerField(default=0)
    total_incomplete = models.PositiveIntegerField(default=0)
    total_probable_duplicates = models.PositiveIntegerField(default=0)
    total_discarded = models.PositiveIntegerField(default=0)
    total_opportunities = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.source_name} - {self.bairro or 'Todos'}"


class RawListing(models.Model):
    search_run = models.ForeignKey(SearchRun, on_delete=models.PROTECT, related_name="raw_listings")
    source_name = models.CharField(max_length=120)
    source_url = models.URLField(max_length=500, blank=True)
    raw_title = models.CharField(max_length=255, blank=True)
    raw_description = models.TextField(blank=True)
    raw_address = models.CharField(max_length=255, blank=True)
    raw_price = models.CharField(max_length=80, blank=True)
    raw_area = models.CharField(max_length=80, blank=True)
    raw_condominium = models.CharField(max_length=80, blank=True)
    raw_contact = models.CharField(max_length=160, blank=True)
    raw_phone = models.CharField(max_length=80, blank=True)
    raw_payload_json = models.JSONField(default=dict, blank=True)
    captured_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-captured_at"]

    def __str__(self) -> str:
        return self.raw_title or self.raw_address or f"RawListing {self.pk}"


class Listing(models.Model):
    raw_listing = models.OneToOneField(
        RawListing, on_delete=models.PROTECT, related_name="listing", null=True, blank=True
    )
    source_name = models.CharField(max_length=120)
    source_url = models.URLField(max_length=500, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=120, blank=True)
    tipo_imovel = models.CharField(max_length=80, blank=True)
    finalidade = models.CharField(max_length=40, blank=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    aluguel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    aluguel_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condominio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condominio_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    contato = models.CharField(max_length=160, blank=True)
    telefone = models.CharField(max_length=80, blank=True)
    observacoes = models.TextField(blank=True)
    confidence_status = models.CharField(
        max_length=32, choices=ConfidenceStatus.choices, default=ConfidenceStatus.RAW
    )
    review_status = models.CharField(
        max_length=32, choices=ReviewStatus.choices, default=ReviewStatus.NOT_REVIEWED
    )
    is_opportunity = models.BooleanField(default=False)
    opportunity_score = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_opportunity", "-opportunity_score", "bairro", "endereco"]

    def save(self, *args, **kwargs):
        if self.aluguel is not None and self.area_m2:
            self.aluguel_m2 = (self.aluguel / self.area_m2).quantize(Decimal("0.01"))
        if self.condominio is not None and self.area_m2:
            self.condominio_m2 = (self.condominio / self.area_m2).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.endereco} - {self.bairro}"


class PriceSnapshot(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="price_snapshots")
    aluguel = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condominio = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    aluguel_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condominio_m2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    captured_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-captured_at"]


class ListingReview(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="reviews")
    decision = models.CharField(max_length=32, choices=ReviewStatus.choices)
    comment = models.TextField(blank=True)
    reviewed_by = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
