from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import UserSerializer, RegisterSerializer

class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny] 
    serializer_class = RegisterSerializer

class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    # GET, POST e DELETE em /api/users/favorites/
    @action(detail=False, methods=['get', 'post', 'delete'], url_path='favorites')
    def favorites(self, request):
        from apps.properties.serializers import PropertiesSerializer # Sei que soa estranho, mas esse import tem que tá aqui para poder não ter import repetido 
        from apps.properties.models import Properties
        
        user = request.user
        
        # GET: Retorna os imóveis favoritados pelo usuário
        if request.method == 'GET':
            favorites = user.favorites.all()
            serializer = PropertiesSerializer(favorites, many=True)
            return Response(serializer.data)

        property_id = request.data.get('property_id')
        if not property_id:
            return Response({"error": "property_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        property_obj = get_object_or_404(Properties, id=property_id)

        if request.method == 'POST':
            user.favorites.add(property_obj)
            return Response({"message": "Property added to favorites"}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            user.favorites.remove(property_obj)
            return Response({"message": "Property removed from favorites"}, status=status.HTTP_200_OK)