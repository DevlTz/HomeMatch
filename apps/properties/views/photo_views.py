from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from apps.properties.views.property_views import IsPropertyOwner
from apps.properties.models import Properties, PropertiesPhotos
from apps.properties.serializers.photo_serializers import PropertiesPhotosSerializer, PropertiesUploadPhotosSerializer


class UploadPhotoPropertyView(generics.CreateAPIView):
    queryset = Properties.objects.all().order_by("created_at")
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    serializer_class = PropertiesUploadPhotosSerializer
    lookup_field = "pk"

    def perform_create(self, serializer):
        property = self.get_object()
        serializer.save(property=property)

class UpdatePhotoPropertyView(generics.UpdateAPIView):
    queryset = PropertiesPhotos.objects.all().order_by("property_id", "order")
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    serializer_class = PropertiesUploadPhotosSerializer
    lookup_field = "pk"

class DeletePhotoPropertyView(generics.UpdateAPIView):
    queryset = PropertiesPhotos.objects.all().order_by("property_id", "order")
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"
