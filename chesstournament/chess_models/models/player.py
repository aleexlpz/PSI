from django.db import models
from django.core.exceptions import ValidationError
import requests
from django.utils import timezone

class Player(models.Model):
    """
    Modelo que representa a un jugador de ajedrez en el sistema.
    Almacena información personal, perfiles en plataformas y clasificaciones.
    """
    class Meta:
        unique_together = ('email', 'name')
    
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name="Nombre del jugador"
    )

    email = models.EmailField(
        blank=True,
        verbose_name="Correo electrónico"
    )

    country = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="País"
    )

    lichess_username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        verbose_name="Nombre de usuario en Lichess"
    )

    lichess_rating_bullet = models.IntegerField(
        default=0,
        verbose_name="Rating Bullet en Lichess"
    )

    lichess_rating_blitz = models.IntegerField(
        default=0,
        verbose_name="Rating Blitz en Lichess"
    )

    lichess_rating_rapid = models.IntegerField(
        default=0,
        verbose_name="Rating Rapid en Lichess"
    )

    lichess_rating_classical = models.IntegerField(
        default=0,
        verbose_name="Rating Classical en Lichess"
    )

    fide_id = models.IntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID FIDE"
    )

    fide_rating_blitz = models.IntegerField(
        default=0,
        verbose_name="Rating Blitz FIDE"
    )

    fide_rating_rapid = models.IntegerField(
        default=0,
        verbose_name="Rating Rapid FIDE"
    )

    fide_rating_classical = models.IntegerField(
        default=0,
        verbose_name="Rating Classical FIDE"
    )

    creation_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="Fecha de actualización"
    )

    def save(self, *args, **kwargs):
        # Verificar duplicados antes de guardar
        if self.lichess_username:
            try:
                existing = Player.objects.get(lichess_username=self.lichess_username)
                if existing.id != self.id:
                    raise ValidationError("Lichess username ya existe.")
            except Player.DoesNotExist:
                pass
        # Llamar a la API de Lichess si hay username
        if self.lichess_username and not self.pk:  # Solo para nuevos registros
            self.get_lichess_user_ratings()
        super().save(*args, **kwargs)

    def check_lichess_user_exists(self):
        """
        Verifica si el usuario de Lichess existe.
        Devuelve True si existe, False en caso contrario.
        """
        try:
            response = requests.get(f"https://lichess.org/api/user/{self.lichess_username}")
            return response.status_code == 200
        except requests.RequestException as e:
            raise ValidationError(f"Error al verificar el usuario de Lichess: {e}")
        return False

    def get_lichess_user_ratings(self):
        """
        Obtiene las clasificaciones del jugador desde Lichess y las actualiza en el modelo.
        """
        try:
            response = requests.get(f"https://lichess.org/api/user/{self.lichess_username}")
            if response.status_code == 200:
                data = response.json()
                self.lichess_rating_bullet = data.get("perfs", {}).get("bullet", {}).get("rating", 0)
                self.lichess_rating_blitz = data.get("perfs", {}).get("blitz", {}).get("rating", 0)
                self.lichess_rating_rapid = data.get("perfs", {}).get("rapid", {}).get("rating", 0)
                self.lichess_rating_classical = data.get("perfs", {}).get("classical", {}).get("rating", 0)
                self.save()
            else:
                raise ValidationError(f"Error al obtener las clasificaciones de Lichess: {response.status_code}")
        except requests.RequestException as e:
            raise ValidationError(f"Error al obtener las clasificaciones de Lichess: {e}")
        return False