from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.properties.permissions import IsPropertyOwner
from apps.properties.models import Properties, PropertiesPhotos
from apps.properties.serializers.photo_serializers import PropertiesUploadPhotosSerializer, PropertiesPhotosSerializer


class UploadPhotoPropertyView(generics.CreateAPIView):
    queryset = Properties.objects.all()
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    serializer_class = PropertiesUploadPhotosSerializer
    lookup_field = "pk"

    def perform_create(self, serializer):
        property = self.get_object()
        serializer.save(property=property)

class RUDPhotoPropertyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertiesPhotos.objects.all()
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return PropertiesUploadPhotosSerializer
        return PropertiesPhotosSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsPropertyOwner()]
        return [AllowAny]
