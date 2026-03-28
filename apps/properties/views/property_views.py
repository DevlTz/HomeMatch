from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
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
            owner_id = obj.property.owner_id
        else:
            raise PermissionDenied("Cannot verify ownership for this object.")
        if owner_id != request.user.id:
            raise PermissionDenied("You do not have permission to do this action.")
        return True
    
class CreateListPropertyView(generics.ListCreateAPIView):
    queryset = Properties.objects.all().order_by("created_at")
    filterset_class = PropertiesFilters

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PropertiesWriteSerializer
        return PropertiesReadSerializer
        
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        serializer.save(owner_id=self.request.user.id)

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

class SearchPropertyAIView(APIView):
    pass
