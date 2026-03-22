from django.urls import path
from .views import latest_readings, dashboard

urlpatterns = [
    path("", dashboard),
    path("latest/", latest_readings),
]
