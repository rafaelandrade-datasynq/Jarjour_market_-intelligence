from django.urls import path

from .services import export_carol_xlsx_view

app_name = "exports"

urlpatterns = [
    path("carol-xlsx/", export_carol_xlsx_view, name="carol-xlsx"),
]
