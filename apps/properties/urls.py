from django.urls import path
from .views import property_views, photo_views

urlpatterns = [
    path("properties/", property_views.CreateListPropertyView.as_view()),
    path("properties/<int:pk>/", property_views.RUDPropertyView.as_view()),
    path("properties/<int:pk>/photos/", photo_views.UploadPhotoPropertyView.as_view()),
    path("photos/<int:pk>/", photo_views.RUDPhotoPropertyView.as_view()),
]
