from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import User
from .serializers import UserSerializer, RegisterSerializer
from .services import FavoriteService
from apps.properties.serializers.property_serializers import PropertiesReadSerializer

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
        user = request.user
        
        # GET: Retorna os imóveis favoritados pelo usuário
        if request.method == 'GET':
            favorites = FavoriteService.list_user_favorites(user)
            serializer = PropertiesReadSerializer(favorites, many=True)
            return Response(serializer.data)

        property_id = request.data.get('property_id')
        if not property_id:
            return Response({"error": "property_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.method == 'POST':
            FavoriteService.add_property_to_favorites(user, property_id)
            return Response({"message": "Property added to favorites"}, status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            FavoriteService.remove_property_from_favorites(user, property_id)
            return Response({"message": "Property removed from favorites"}, status=status.HTTP_200_OK)