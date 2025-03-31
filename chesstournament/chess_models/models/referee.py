from django.db import models

class Referee(models.Model):
    """Model representing a chess tournament referee."""
    
    name = models.CharField(
        max_length=128,
    )
    
    referee_number = models.CharField(
        max_length=32,
        default='-1',
    )