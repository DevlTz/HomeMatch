from django.urls import path
from .views import SearchNaturalView

urlpatterns = [
    path("natural/", SearchNaturalView.as_view(), name="search-natural"),
]
