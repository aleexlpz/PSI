from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Player(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    country = models.CharField(max_length=2, blank=True, null=True)
    lichess_username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    lichess_rating_bullet = models.IntegerField(default=0)
    lichess_rating_blitz = models.IntegerField(default=0)
    lichess_rating_rapid = models.IntegerField(default=0)
    lichess_rating_classical = models.IntegerField(default=0)
    fide_id = models.IntegerField(unique=True, blank=True, null=True)
    fide_rating_blitz = models.IntegerField(default=0)
    fide_rating_rapid = models.IntegerField(default=0)
    fide_rating_classical = models.IntegerField(default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Convert the name to uppercase before saving
        self.name = self.name.upper()
        super().save(*args, **kwargs)