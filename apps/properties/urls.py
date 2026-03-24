from django.urls import path
from . import views

urlpatterns = [
    path("properties", views.CreatePropertyView.as_view()),
    path("properties", views.ListAllPropertiesView.as_view()),
    path("properties/id:pk/", views.UpdatePropertyView.as_view()),
    path("properties/id:pk/", views.DeletePropertyView.as_view()),
    path("properties/id:pk/", views.GetPropertyView.as_view())
]
