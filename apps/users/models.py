# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class UserType(models.TextChoices):
        ANUNCIANTE = "A", "Anunciante"
        BUSCADOR = "B", "Buscador"
        
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    user_type = models.CharField(
        max_length=1,
        choices=UserType.choices,
        default=UserType.BUSCADOR,
        db_index=True,
    )
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=50, null=True, blank=True)
    
    # Relação Many-to-Many (imoveis - pro properties)
  #  favorites = models.ManyToManyField(
  #      'properties.Property', 
 #       related_name='favorited_by', 
   #     blank=True
  #  )

    class Meta:
        db_table = "users" # table de luluisa
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.email

class SearchPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    property_type = models.CharField(max_length=1, blank=True, null=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    neighborhood = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "search_preferences"