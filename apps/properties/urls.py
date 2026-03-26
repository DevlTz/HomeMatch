from django.urls import path
from .views import property_views, photo_views

urlpatterns = [
    path("properties/", property_views.CreatePropertyView.as_view()),
    path("properties/", property_views.ListAllPropertiesView.as_view()),
    path("properties/<int:pk>/manage/", property_views.UpdatePropertyView.as_view()),
    path("properties/<int:pk>/manage/", property_views.DeletePropertyView.as_view()),
    path("properties/<int:pk>/photos/", photo_views.UploadPhotoPropertyView.as_view()),
    path("properties/<int:pk>/", property_views.GetPropertyView.as_view()),
    path("photos/<int:pk>/", photo_views.UpdatePhotoPropertyView.as_view()),
    path("photos/<int:pk>/", photo_views.DeletePhotoPropertyView.as_view())
]
