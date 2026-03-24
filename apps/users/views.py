# apps/users/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get', 'patch'], url_path='profile')
    def profile(self, request):
        user = request.user
        
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
            
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    # GET e POST em /api/users/favorites/
    @action(detail=False, methods=['get', 'post'], url_path='favorites')
    def favorites(self, request):
        user = request.user
        
        if request.method == 'POST':
            # Espera receber o ID do imóvel no body: {"property_id": 1}
            property_id = request.data.get('property_id')
            if not property_id:
                return Response({"erro": "ID do imóvel não fornecido"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Adicionar futuramente a lógica para buscar o imóvel e adicionar aos favoritos:
            # property = Property.objects.get(id=property_id)
            # user.favorites.add(property)
            return Response({"mensagem": "Imóvel favoritado com sucesso!"})

        # Para o GET
        # favorites = user.favorites.all()
        # serializer = PropertySerializer(favorites, many=True)
        # return Response(serializer.data)
        return Response({"mensagem": "Aqui retornaremos os imóveis favoritos (precisa do model Property finalizado)"})