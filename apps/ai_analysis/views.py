"""
HTTP views for the AI analysis app.
"""

from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_analysis.services import AiAnalysisService
from apps.properties.models import Properties


class AnalyzePropertyRequestSerializer(serializers.Serializer):
    """Validates the request payload for the analyze endpoint."""

    prompt = serializers.CharField(required=True, allow_blank=False)


class AnalyzePropertyView(APIView):
    """Endpoint to trigger AI analysis on a property.

    Requires authentication.  Expects a JSON body with a `prompt` field.
    URL pattern should include the property primary key as `pk`.
    """

    permission_classes = [IsAdminUser]

    def post(self, request, pk: int):  
        serializer = AnalyzePropertyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_obj = get_object_or_404(Properties, pk=pk)
        service = AiAnalysisService()
        result = service.analyze_property(property_obj, serializer.validated_data["prompt"])

        return Response(
            {
                "property_id": property_obj.id,
                "analysis_count": len(result),
                "results": result,
            },
            status=status.HTTP_200_OK,
        )