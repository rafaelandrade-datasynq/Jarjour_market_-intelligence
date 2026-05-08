from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard, name="index"),
    path("table/", views.listings_table, name="table"),
    path("listings/<int:listing_id>/review/", views.review_listing_action, name="review-listing"),
]
