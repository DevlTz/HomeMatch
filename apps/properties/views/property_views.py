from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from apps.properties.serializers.property_serializers import PropertiesWriteSerializer, PropertiesReadSerializer
from apps.properties.models import Properties
from apps.properties.filters import PropertiesFilters
from rest_framework.response import Response


# C -> Create
# R -> Read
# U -> Update
# D -> Delete

class IsAdvertiser(BasePermission):
    message = "You do not have permission to do this action. Please, change your account type to advertise!"
    def has_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            request.user.user_type == "A"
        )

class IsPropertyOwner(BasePermission):
    message = "You do not have permission to do this action."

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            owner = obj.owner
        elif hasattr(obj, "property"):
            owner = obj.property.owner
        else:
            return False
    
        if owner != request.user:
            return False
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
            return [IsAuthenticated, IsAdvertiser]
        return [AllowAny]

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
            return [IsAuthenticated, IsPropertyOwner]
        return [AllowAny()]
    
    def destroy(self, request, *args, **kwargs):
        self.perform_destroy(self.get_object())

        return Response({
            "message": "Delete successfull!"
        }, status=204)


class SearchPropertyAIView(APIView):
    pass
