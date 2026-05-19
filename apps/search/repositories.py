"""Search data-access layer."""

from django.db.models import Avg, Count

from apps.properties.models import Properties
from apps.search.embeddings import EmbeddingService


class SearchRepository:
    @staticmethod
    def filter_properties(criteria):
        queryset = (
            Properties.objects.filter(status=True)
            .select_related("rooms", "rooms_extras", "condo", "owner")
            .prefetch_related("photos", "nearby_places", "subjective_attributes")
            .annotate(
                average_rating=Avg("reviews__rating"),
                favorite_count=Count("favorited_by", distinct=True),
            )
        )

        if criteria.get("property_type"):
            queryset = queryset.filter(type=criteria["property_type"])

        if criteria.get("min_price") is not None:
            queryset = queryset.filter(price__gte=criteria["min_price"])

        if criteria.get("max_price") is not None:
            queryset = queryset.filter(price__lte=criteria["max_price"])

        if criteria.get("city"):
            queryset = queryset.filter(city__icontains=criteria["city"])

        if criteria.get("neighborhood"):
            queryset = queryset.filter(neighborhood__icontains=criteria["neighborhood"])

        if criteria.get("bedrooms") is not None:
            queryset = queryset.filter(rooms__bedrooms=criteria["bedrooms"])

        if criteria.get("bathrooms") is not None:
            queryset = queryset.filter(rooms__bathrooms=criteria["bathrooms"])

        if criteria.get("parking_spots") is not None:
            queryset = queryset.filter(rooms__parking_spots=criteria["parking_spots"])

        nearby_categories = criteria.get("nearby_categories") or []
        if nearby_categories:
            queryset = queryset.filter(nearby_places__category__in=nearby_categories)

        desired_attributes = criteria.get("desired_attributes") or []
        if desired_attributes:
            queryset = queryset.filter(
                subjective_attributes__attribute_token__in=desired_attributes,
                subjective_attributes__strength_mean__gte=0.5,
            )

        return queryset.distinct().order_by("created_at")

    @staticmethod
    def rank_properties_by_embedding(query_embedding, properties):
        if not query_embedding:
            return list(properties)

        ranked = []
        for property_obj in properties:
            property_embedding = EmbeddingService.deserialize(property_obj.embedding)
            score = EmbeddingService.cosine_similarity(query_embedding, property_embedding)
            property_obj.search_match_score = round(score, 6)
            ranked.append(property_obj)

        return sorted(
            ranked,
            key=lambda property_obj: (
                getattr(property_obj, "search_match_score", 0.0),
                property_obj.created_at,
            ),
            reverse=True,
        )
