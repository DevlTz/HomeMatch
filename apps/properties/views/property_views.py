from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from apps.properties.models import Properties, Reviews
from apps.properties.filters import PropertiesFilters
from apps.properties.serializers.property_serializers import PropertiesWriteSerializer, PropertiesReadSerializer
from apps.properties.serializers.reviews_serializers import ReviewsSerializer
from apps.properties.permissions import IsAdvertiser, IsReviewOwner, IsPropertyOwner
from apps.properties.tasks import search_nearby_places
from apps.properties.services import NomatimService

# C -> Create
# R -> Read
# U -> Update
# D -> Delete

class CreateListReviewPropertyView(generics.ListCreateAPIView):
    serializer_class = ReviewsSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Reviews.objects.filter(
            property_id=self.kwargs["pk"]
        ).order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["property_id"] = self.kwargs["pk"]
        return context

    def perform_create(self, serializer):
        property_obj = get_object_or_404(Properties, pk=self.kwargs["pk"])
        serializer.save(user=self.request.user, property=property_obj)

class RUDReviewPropertyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewsSerializer
    lookup_url_kwarg = "review_pk"

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsReviewOwner()]
        return [AllowAny()]

class CreateListPropertyView(generics.ListCreateAPIView):
    queryset = Properties.objects.all().order_by("created_at")
    filterset_class = PropertiesFilters

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PropertiesWriteSerializer
        return PropertiesReadSerializer
        
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdvertiser()]
        return [AllowAny()]

    def perform_create(self, serializer):
        property_obj = serializer.save(owner_id=self.request.user.id)
        NomatimService.geocode(property_obj)
        if property_obj.latitude and property_obj.longitude:
            search_nearby_places.delay(property_obj.id)   

class RUDPropertyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Properties.objects.all()
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PropertiesWriteSerializer
        return PropertiesReadSerializer
        
    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsPropertyOwner()]
        return [AllowAny()]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Delete successful!"
        }, status=status.HTTP_204_NO_CONTENT)

class SearchPropertyAIView(APIView):
    pass