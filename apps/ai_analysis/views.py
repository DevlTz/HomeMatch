from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ai_analysis.services import AiAnalysisService
from apps.properties.models import Properties


class AnalyzePropertyRequestSerializer(serializers.Serializer):
    prompt = serializers.CharField(required=True, allow_blank=False)


class AnalyzePropertyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        serializer = AnalyzePropertyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        property_obj = get_object_or_404(Properties, pk=pk)
        service = AiAnalysisService()
        result = service.analyze_property(property_obj, serializer.validated_data["prompt"])

        return Response(
            {"property_id": property_obj.id, "analysis_count": len(result), "results": result},
            status=status.HTTP_200_OK,
        )
