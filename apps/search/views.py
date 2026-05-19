from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.properties.serializers.property_serializers import PropertiesReadSerializer
from apps.search.serializers import NaturalSearchRequestSerializer
from apps.search.services import NaturalSearchService


class SearchNaturalView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = NaturalSearchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        search_result = NaturalSearchService.search(
            serializer.validated_data["query"]
        )
        results_serializer = PropertiesReadSerializer(
            search_result["results"],
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "interpreted_filters": search_result["interpreted_filters"],
                "results": results_serializer.data,
            }
        )
