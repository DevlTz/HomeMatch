from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from apps.properties.serializers.property_serializers import PropertiesWriteSerializer, PropertiesReadSerializer
from apps.properties.models import Properties
from apps.properties.filters import PropertiesFilters


# C -> Create
# R -> Read
# U -> Update
# D -> Delete

class IsPropertyOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner_id"):
            owner_id = obj.owner_id
        elif hasattr(obj, "property"):
            owner_id = obj.proerty.owner_id
        else:
            owner_id = None
        if owner_id != request.user.id:
            raise PermissionDenied("You do not have permission to do this action.")
        return True
    
class CreatePropertyView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PropertiesWriteSerializer

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)
    
class ListAllPropertiesView(generics.ListAPIView):
    queryset = Properties.objects.all().order_by("created_at")
    serializer_class = PropertiesReadSerializer
    filterset_class = PropertiesFilters

class UpdatePropertyView(generics.UpdateAPIView):
    queryset = Properties.objects.all().order_by("created_at")
    serializer_class = PropertiesWriteSerializer
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"

class DeletePropertyView(generics.DestroyAPIView):
    queryset = Properties.objects.all().order_by("created_at")
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"

class GetPropertyView(generics.RetrieveAPIView):
    queryset = Properties.objects.all()
    serializer_class = PropertiesReadSerializer
    lookup_field = "pk"

class SearchPropertyAIView(APIView):
    pass
