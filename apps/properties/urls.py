from django.urls import path
from . import views

urlpatterns = [
    path("properties/", views.CreatePropertyView.as_view()),
    path("properties/", views.ListAllPropertiesView.as_view()),
    path("properties/<int:pk>/manage/", views.UpdatePropertyView.as_view()),
    path("properties/<int:pk>/manage/", views.DeletePropertyView.as_view()),
    path("properties/<int:pk>/photos/", views.UploadPhotoPropertyView.as_view()),
    path("properties/<int:pk>/", views.GetPropertyView.as_view())
]
