from collections import Counter
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

from apps.properties.repositories import PhotoRepository, PropertyRepository, ReviewRepository


class MatchScoreUseCase:
    FILTER_TO_SCORE_FIELDS = {
        "type": {"property_type"},
        "city": {"city"},
        "neighborhood": {"neighborhood"},
        "min_price": {"min_price"},
        "max_price": {"max_price"},
    }

    @staticmethod
    def apply_match_scores(queryset, user, query_params=None):
        properties = list(queryset)
        try:
            preferences = user.preferences
        except ObjectDoesNotExist:
            preferences = None

        current_filters = MatchScoreUseCase._current_filters(query_params)
        ignored_score_fields = MatchScoreUseCase._ignored_score_fields(
            current_filters.keys()
        )
        favorite_profile = MatchScoreUseCase._favorite_profile(user)

        for property_obj in properties:
            property_obj.match_score = MatchScoreUseCase.calculate_match_score(
                property_obj,
                preferences=preferences,
                ignored_score_fields=ignored_score_fields,
                favorite_profile=favorite_profile,
            )

        return sorted(properties, key=lambda item: item.match_score, reverse=True)

    @staticmethod
    def calculate_match_score(
        property_obj,
        *,
        preferences=None,
        ignored_score_fields=None,
        favorite_profile=None,
    ):
        weighted_scores = []

        if preferences:
            preference_score = MatchScoreUseCase._preference_score(
                property_obj,
                preferences,
                ignored_score_fields=ignored_score_fields or set(),
            )
            if preference_score is not None:
                weighted_scores.append((preference_score, 45))

        if favorite_profile:
            weighted_scores.append(
                (
                    MatchScoreUseCase._favorite_profile_score(
                        property_obj,
                        favorite_profile,
                    ),
                    40,
                )
            )

        popularity_score = MatchScoreUseCase._popularity_score(property_obj)
        if weighted_scores:
            weighted_scores.append((popularity_score, 15))
            total_weight = sum(weight for _, weight in weighted_scores)
            return round(
                sum(score * weight for score, weight in weighted_scores) / total_weight
            )

        return popularity_score

    @staticmethod
    def _preference_score(property_obj, preferences, *, ignored_score_fields):
        total_weight = 0
        earned = 0

        rules = [
            (
                "property_type",
                preferences.property_type,
                25,
                property_obj.type == preferences.property_type,
            ),
            (
                "city",
                preferences.city,
                20,
                MatchScoreUseCase._same_text(property_obj.city, preferences.city),
            ),
            (
                "neighborhood",
                preferences.neighborhood,
                15,
                MatchScoreUseCase._same_text(
                    property_obj.neighborhood,
                    preferences.neighborhood,
                ),
            ),
        ]

        for field_name, expected, weight, matched in rules:
            if field_name not in ignored_score_fields and expected:
                total_weight += weight
                if matched:
                    earned += weight

        if (
            "min_price" not in ignored_score_fields
            and preferences.min_price is not None
        ):
            total_weight += 15
            if property_obj.price >= preferences.min_price:
                earned += 15

        if (
            "max_price" not in ignored_score_fields
            and preferences.max_price is not None
        ):
            total_weight += 25
            if property_obj.price <= preferences.max_price:
                earned += 25
            elif property_obj.price <= preferences.max_price * Decimal("1.1"):
                earned += 10

        if total_weight == 0:
            return None

        return round((earned / total_weight) * 100)

    @staticmethod
    def _favorite_profile(user):
        favorites = list(
            user.favorites.select_related("rooms").only(
                "type",
                "city",
                "neighborhood",
                "price",
                "rooms__id",
            )
        )
        if not favorites:
            return None

        type_counter = Counter(item.type for item in favorites if item.type)
        city_counter = Counter(
            MatchScoreUseCase._normalize_text(item.city)
            for item in favorites
            if item.city
        )
        neighborhood_counter = Counter(
            MatchScoreUseCase._normalize_text(item.neighborhood)
            for item in favorites
            if item.neighborhood
        )
        prices = [item.price for item in favorites if item.price is not None]

        return {
            "favorite_type": MatchScoreUseCase._most_common(type_counter),
            "favorite_city": MatchScoreUseCase._most_common(city_counter),
            "favorite_neighborhoods": {
                value for value, _ in neighborhood_counter.most_common(3)
            },
            "average_price": sum(prices) / len(prices) if prices else None,
        }

    @staticmethod
    def _favorite_profile_score(property_obj, profile):
        total_weight = 0
        earned = 0

        rules = [
            (
                profile["favorite_type"],
                25,
                property_obj.type == profile["favorite_type"],
            ),
            (
                profile["favorite_city"],
                20,
                MatchScoreUseCase._normalize_text(property_obj.city)
                == profile["favorite_city"],
            ),
            (
                profile["favorite_neighborhoods"],
                20,
                MatchScoreUseCase._normalize_text(property_obj.neighborhood)
                in profile["favorite_neighborhoods"],
            ),
        ]

        for expected, weight, matched in rules:
            if expected:
                total_weight += weight
                if matched:
                    earned += weight

        average_price = profile["average_price"]
        if average_price:
            total_weight += 35
            price_distance = abs(property_obj.price - average_price) / average_price
            if price_distance <= Decimal("0.10"):
                earned += 35
            elif price_distance <= Decimal("0.20"):
                earned += 25
            elif price_distance <= Decimal("0.35"):
                earned += 10

        if total_weight == 0:
            return 0

        return round((earned / total_weight) * 100)

    @staticmethod
    def _popularity_score(property_obj):
        favorite_count = getattr(property_obj, "favorite_count", 0) or 0
        average_rating = getattr(property_obj, "average_rating", None) or 0

        rating_score = min(float(average_rating), 5.0) / 5 * 70
        favorite_score = min(favorite_count, 10) / 10 * 30

        return round(rating_score + favorite_score)

    @staticmethod
    def _same_text(value, expected):
        if value is None or expected is None:
            return False
        return MatchScoreUseCase._normalize_text(value) == MatchScoreUseCase._normalize_text(expected)

    @staticmethod
    def _normalize_text(value):
        return str(value).strip().lower()

    @staticmethod
    def _ignored_score_fields(query_params):
        ignored = set()
        for filter_name in query_params or []:
            ignored.update(MatchScoreUseCase.FILTER_TO_SCORE_FIELDS.get(filter_name, set()))
        return ignored

    @staticmethod
    def _current_filters(query_params):
        if not query_params:
            return {}
        return {
            name: query_params.get(name)
            for name in MatchScoreUseCase.FILTER_TO_SCORE_FIELDS
            if query_params.get(name) not in (None, "")
        }

    @staticmethod
    def _most_common(counter):
        if not counter:
            return None
        return counter.most_common(1)[0][0]


class PropertyUseCase:
    @staticmethod
    def create_property(validated_data):
        rooms_data = validated_data.pop("rooms")
        condo_data = validated_data.pop("condo", None)
        rooms_extras_data = validated_data.pop("rooms_extras")

        rooms, _ = PropertyRepository.get_or_create_rooms(rooms_data)
        rooms_extras, _ = PropertyRepository.get_or_create_rooms_extras(rooms_extras_data)
        condo = None
        if condo_data:
            condo, _ = PropertyRepository.get_or_create_condo(condo_data)

        return PropertyRepository.create_property(
            rooms=rooms,
            rooms_extras=rooms_extras,
            condo=condo,
            validated_data=validated_data,
        )

    @staticmethod
    def update_property(instance, validated_data):
        rooms_data = validated_data.pop("rooms", {})
        condo_data = validated_data.pop("condo", None)
        rooms_extras_data = validated_data.pop("rooms_extras", {})

        for attr, value in rooms_data.items():
            setattr(instance.rooms, attr, value)
        PropertyRepository.save_model(instance.rooms)

        if condo_data:
            condo_obj, _ = PropertyRepository.update_condo(instance.condo, condo_data)
            instance.condo = condo_obj

        for attr, value in rooms_extras_data.items():
            setattr(instance.rooms_extras, attr, value)
        PropertyRepository.save_model(instance.rooms_extras)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        return PropertyRepository.save_model(instance)

    @staticmethod
    def delete_property(instance):
        rooms = instance.rooms
        rooms_extras = instance.rooms_extras
        instance.delete()

        if rooms and not rooms.properties.exists():
            rooms.delete()
        if rooms_extras and not rooms_extras.properties.exists():
            rooms_extras.delete()


class PhotoUseCase:
    @staticmethod
    def create_photo(*, property_obj, validated_data):
        image = validated_data.pop('image')
        order = validated_data.pop("order")
        return PhotoRepository.create_photo(
            property_obj=property_obj,
            image=image,
            order=order,
        )

    @staticmethod
    def update_photo(instance, validated_data):
        new_image = validated_data.get("image")
        if new_image:
            return PhotoRepository.replace_photo_image(instance, new_image)
        return instance


class ReviewUseCase:
    @staticmethod
    def validate_unique_review(*, user, property_id, instance=None):
        return not ReviewRepository.user_has_review_for_property(
            user=user,
            property_id=property_id,
            instance=instance,
        )

    @staticmethod
    def get_reviews_for_property(property_id):
        return ReviewRepository.review_queryset_for_property(property_id)

    @staticmethod
    def get_average_rating(property_obj):
        return ReviewRepository.average_rating_for_property(property_obj)
