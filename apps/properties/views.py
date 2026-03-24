from django.shortcuts import render
from .serializers import PropertiesSerializer
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Properties
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied



# C -> Create
# R -> Read
# U -> Update
# D -> Delete
class IsPropertyOwner(BasePermission):
    def has_object_permission(self, obj, request, view):
        if obj.owner_id != request.user.id:
            raise PermissionDenied("You do not have permission to do this action.")
        return True

class CreatePropertyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data.copy()
        data["owner_id"] = user.id
        serializer = PropertiesSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)
    
class ListAllPropertiesView(generics.ListAPIView):
    queryset = Properties.objects.all().order_by("-created_at")
    serializer_class = PropertiesSerializer
  

class GetPropertyView(generics.RetrieveAPIView):
    queryset = Properties.objects.all()
    serializer_class = PropertiesSerializer

class DeletePropertyView(generics.DestroyAPIView):
    queryset = Properties.objects.all()
    serializer_class = PropertiesSerializer
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"

class UpdatePropertyView(generics.UpdateAPIView):
    queryset = Properties.objects.all().order_by("-created_at")
    serializer_class = PropertiesSerializer
    permission_classes = [IsAuthenticated, IsPropertyOwner]
    lookup_field = "pk"


