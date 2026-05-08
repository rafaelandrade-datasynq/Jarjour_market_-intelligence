# Generated manually for the initial Jarjour Market Intelligence MVP.
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SearchRun",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_name", models.CharField(max_length=120)),
                ("bairro", models.CharField(blank=True, max_length=120)),
                ("tipo_imovel", models.CharField(blank=True, max_length=80)),
                ("finalidade", models.CharField(blank=True, max_length=40)),
                ("status", models.CharField(default="COMPLETED", max_length=40)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                ("total_raw_collected", models.PositiveIntegerField(default=0)),
                ("total_normalized", models.PositiveIntegerField(default=0)),
                ("total_reliable", models.PositiveIntegerField(default=0)),
                ("total_review", models.PositiveIntegerField(default=0)),
                ("total_incomplete", models.PositiveIntegerField(default=0)),
                ("total_probable_duplicates", models.PositiveIntegerField(default=0)),
                ("total_discarded", models.PositiveIntegerField(default=0)),
                ("total_opportunities", models.PositiveIntegerField(default=0)),
                ("error_message", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-started_at"]},
        ),
        migrations.CreateModel(
            name="RawListing",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_name", models.CharField(max_length=120)),
                ("source_url", models.URLField(blank=True, max_length=500)),
                ("raw_title", models.CharField(blank=True, max_length=255)),
                ("raw_description", models.TextField(blank=True)),
                ("raw_address", models.CharField(blank=True, max_length=255)),
                ("raw_price", models.CharField(blank=True, max_length=80)),
                ("raw_area", models.CharField(blank=True, max_length=80)),
                ("raw_condominium", models.CharField(blank=True, max_length=80)),
                ("raw_contact", models.CharField(blank=True, max_length=160)),
                ("raw_phone", models.CharField(blank=True, max_length=80)),
                ("raw_payload_json", models.JSONField(blank=True, default=dict)),
                ("captured_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "search_run",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="raw_listings",
                        to="market.searchrun",
                    ),
                ),
            ],
            options={"ordering": ["-captured_at"]},
        ),
        migrations.CreateModel(
            name="Listing",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_name", models.CharField(max_length=120)),
                ("source_url", models.URLField(blank=True, max_length=500)),
                ("endereco", models.CharField(blank=True, max_length=255)),
                ("bairro", models.CharField(blank=True, max_length=120)),
                ("tipo_imovel", models.CharField(blank=True, max_length=80)),
                ("finalidade", models.CharField(blank=True, max_length=40)),
                ("area_m2", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("aluguel", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("aluguel_m2", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("condominio", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("condominio_m2", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("contato", models.CharField(blank=True, max_length=160)),
                ("telefone", models.CharField(blank=True, max_length=80)),
                ("observacoes", models.TextField(blank=True)),
                (
                    "confidence_status",
                    models.CharField(
                        choices=[
                            ("RAW", "Bruto"),
                            ("NORMALIZED", "Normalizado"),
                            ("RELIABLE", "Confiavel"),
                            ("REVIEW", "Para revisar"),
                            ("INCOMPLETE", "Incompleto"),
                            ("PROBABLE_DUPLICATE", "Duplicado provavel"),
                            ("DISCARDED", "Descartado"),
                        ],
                        default="RAW",
                        max_length=32,
                    ),
                ),
                (
                    "review_status",
                    models.CharField(
                        choices=[
                            ("NOT_REVIEWED", "Nao revisado"),
                            ("APPROVED", "Aprovado"),
                            ("NEEDS_REVIEW", "Precisa revisar"),
                            ("REJECTED", "Rejeitado"),
                            ("OPPORTUNITY", "Oportunidade"),
                        ],
                        default="NOT_REVIEWED",
                        max_length=32,
                    ),
                ),
                ("is_opportunity", models.BooleanField(default=False)),
                ("opportunity_score", models.DecimalField(decimal_places=2, default="0.00", max_digits=5)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "raw_listing",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="listing",
                        to="market.rawlisting",
                    ),
                ),
            ],
            options={"ordering": ["-is_opportunity", "-opportunity_score", "bairro", "endereco"]},
        ),
        migrations.CreateModel(
            name="PriceSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("aluguel", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("condominio", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("area_m2", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("aluguel_m2", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("condominio_m2", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ("captured_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="price_snapshots",
                        to="market.listing",
                    ),
                ),
            ],
            options={"ordering": ["-captured_at"]},
        ),
        migrations.CreateModel(
            name="ListingReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "decision",
                    models.CharField(
                        choices=[
                            ("NOT_REVIEWED", "Nao revisado"),
                            ("APPROVED", "Aprovado"),
                            ("NEEDS_REVIEW", "Precisa revisar"),
                            ("REJECTED", "Rejeitado"),
                            ("OPPORTUNITY", "Oportunidade"),
                        ],
                        max_length=32,
                    ),
                ),
                ("comment", models.TextField(blank=True)),
                ("reviewed_by", models.CharField(blank=True, max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="market.listing",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
