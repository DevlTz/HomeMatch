from django.db import models

class Rooms(models.Model):
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    parking_spots = models.IntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["bedrooms", "bathrooms", "parking_spots"],
                name="rooms_unique"
            )
        ]

class RoomsExtras(models.Model):
    living_room = models.BooleanField(default=True)
    garden = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=True)
    laundry_room = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    office = models.BooleanField(default=False)

class Condo(models.Model):
    name = models.CharField(max_length=100, null=False)
    address = models.TextField(max_length=200)
    gym = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    court = models.BooleanField(default=False)
    parks = models.BooleanField(default=False)
    party_spaces = models.BooleanField(default=False)
    concierge = models.BooleanField(default=False)

class Properties(models.Model):
    PURPOSE_CHOICES = [("S", "Sale"), ("R", "Rent"), ("B", "Both")]
    TYPE_CHOICES = [("A", "Apartment"), ("H", "House")]
    
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="properties",
        null=True,
        blank=True,
    )

    rooms = models.ForeignKey(
        Rooms,
        on_delete=models.PROTECT,
        related_name="properties"
    )
    rooms_extras = models.ForeignKey(
        RoomsExtras,
        on_delete=models.PROTECT,
        related_name="properties"
    )
    condo = models.ForeignKey(
        Condo,
        on_delete=models.PROTECT,
        related_name="properties",
        null=True,
        blank=True)
    property_purpose = models.CharField(max_length=1, choices=PURPOSE_CHOICES)
    type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    area = models.FloatField(null=False)
    floors = models.IntegerField()
    floor_number = models.IntegerField(null=True, blank=True)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    address = models.TextField(max_length=200, null=False)
    neighborhood = models.CharField(max_length=100, null=False)
    city = models.CharField(max_length=100, null=False)
    has_mobilia = models.BooleanField(default=False)
    status = models.BooleanField(default=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.TextField()
    embedding = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PropertiesPhotos(models.Model):
    property = models.ForeignKey(
        Properties,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    r2_key = models.TextField(null=False, blank=False)
    order = models.IntegerField()

class Reviews(models.Model):
    property = models.ForeignKey(
        Properties,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField()
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reviews"
        constraints = [
            models.UniqueConstraint(
                fields=["property", "user"],
                name="unique_review_per_user_per_property"
            )
        ]

class NearbyPlaces(models.Model):
    CATEGORY_CHOICES = [("R", "Restaurant"), ("G", "Gym"), ("S", "School"), ("H", "Hospital"), ("SM", "Supermarket"), ("P", "Park")]
    property = models.ForeignKey(
        Properties,
        on_delete=models.CASCADE,
        related_name="nearby_places"
    )
    name = models.TextField(null=False)
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES)
    distance_meters = models.FloatField()
    rating = models.FloatField(null=True, blank=True)
    fetched_at = models.DateTimeField(auto_now_add=True)
