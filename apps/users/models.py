# apps/users/models.py
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser need is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser need is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    class UserType(models.TextChoices):
        ADVERTISER = "A", "Advertiser"
        SEEKER = "S", "Seeker"
        
    username = None
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    user_type = models.CharField(
        max_length=1,
        choices=UserType.choices,
        default=UserType.SEEKER, 
        db_index=True,
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    
    
    favorites = models.ManyToManyField(
        'properties.Properties', 
        related_name='favorited_by', 
        blank=True
    )

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

class SearchPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    property_type = models.CharField(max_length=1, choices=[('H', 'House'), ('A', 'Apartment')], null=True, blank=True)    
    min_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    city = models.CharField(max_length=100, null=True, blank=True)
    neighborhood = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = "search_preferences"