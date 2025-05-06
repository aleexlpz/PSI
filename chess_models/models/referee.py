from django.db import models

class Referee(models.Model):
    """Model representing a chess tournament referee."""
    
    name = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="Nombre del árbitro"
    )
    
    refereeNumber = models.CharField(
        max_length=32,
        default='-1',
        verbose_name="Número de árbitro"
    )

    def __str__(self):
        """Return a string representation of the referee."""
        return f'{self.name} ({self.refereeNumber})'
 