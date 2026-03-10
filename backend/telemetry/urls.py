from django.urls import path
from .views import receive_from_fog, latest_readings, dashboard

urlpatterns = [
    path("", dashboard),
    path("ingest/", receive_from_fog),
    path("latest/", latest_readings),
]
