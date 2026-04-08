from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.properties.permissions import IsPropertyOwner
from apps.properties.models import Properties, PropertiesPhotos
from apps.properties.serializers.photo_serializers import PropertiesUploadPhotosSerializer, PropertiesPhotosSerializer
from apps.properties.serializers.photo_serializers import (
    PropertiesUploadPhotosSerializer,
    PropertiesPhotosSerializer,
    MIN_PHOTOS,
)

class UploadPhotoPropertyView(generics.CreateAPIView):
    queryset = Properties.objects.all()
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    serializer_class = PropertiesUploadPhotosSerializer
    lookup_field = "pk"

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['property'] = self.get_object()
        return context
    
    def perform_create(self, serializer):
        property = self.get_object()
        serializer.save(property=property, order=property.photos.count() + 1)

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
    
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        property_obj = instance.property

        if property_obj.photos.count() <= MIN_PHOTOS:
            return Response(
                {"error": f"A property must have at least {MIN_PHOTOS} photo."},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response({"message": "Photo removed successfully."}, status=status.HTTP_200_OK)
