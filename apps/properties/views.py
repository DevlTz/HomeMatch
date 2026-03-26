from .serializers import PropertiesWriteSerializer, PropertiesReadSerializer, PropertiesUploadPhotosSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Properties
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .filters import PropertiesFilters

# C -> Create
# R -> Read
# U -> Update
# D -> Delete

class IsPropertyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.owner_id != request.user.id:
            raise PermissionDenied("You do not have permission to do this action.")
        return True
    
class UploadPhotoPropertyView(generics.CreateAPIView):
    queryset = Properties.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    serializer_class = PropertiesUploadPhotosSerializer
    lookup_field = "pk"

    def perform_create(self, serializer):
        property = self.get_object()
        serializer.save(property=property)

class CreatePropertyView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PropertiesWriteSerializer

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)
    
class ListAllPropertiesView(generics.ListAPIView):
    queryset = Properties.objects.all().order_by("-created_at")
    serializer_class = PropertiesReadSerializer
    filterset_class = PropertiesFilters

class UpdatePropertyView(generics.UpdateAPIView):
    queryset = Properties.objects.all().order_by("-created_at")
    serializer_class = PropertiesWriteSerializer
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"

class DeletePropertyView(generics.DestroyAPIView):
    queryset = Properties.objects.all().order_by("-created_at")
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"

class GetPropertyView(generics.RetrieveAPIView):
    queryset = Properties.objects.all()
    serializer_class = PropertiesReadSerializer
    lookup_field = "pk"

class SearchPropertyAIView(APIView):
    pass