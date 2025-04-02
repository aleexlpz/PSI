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
        # Si ambos campos están vacíos, generar valores temporales únicos
        if not self.email and not self.name:
            self.email = f"temp_{self.lichess_username or id(self)}@example.com"
            self.name = f"Jugador temporal {self.lichess_username or id(self)}"
        
        # Lógica existente para evitar duplicados
        if self.pk is None:
            existing_player = None
            if self.lichess_username:
                existing_player = Player.objects.filter(lichess_username=self.lichess_username).first()
            if not existing_player and self.fide_id:
                existing_player = Player.objects.filter(fide_id=self.fide_id).first()
            if not existing_player:
                existing_player = Player.objects.filter(email=self.email, name=self.name).first()
            
            if existing_player:
                # Actualizar el jugador existente y evitar duplicados
                for field in self._meta.fields:
                    if field.name not in ['id', 'creation_date']:
                        setattr(existing_player, field.name, getattr(self, field.name))
                existing_player.save()
                self.pk = existing_player.pk
                return  # Evita guardar el nuevo jugador

        # Lógica para actualizar ratings de Lichess (opcional)
        if self.lichess_username:
            try:
                response = requests.get(f"https://lichess.org/api/user/{self.lichess_username}")
                if response.status_code == 200:
                    data = response.json()
                    perfs = data.get('perfs', {})
                    self.lichess_rating_bullet = perfs.get('bullet', {}).get('rating', 0)
                    self.lichess_rating_blitz = perfs.get('blitz', {}).get('rating', 0)
                    self.lichess_rating_rapid = perfs.get('rapid', {}).get('rating', 0)
            except requests.RequestException:
                pass  # Mantener los valores actuales si hay error

        super().save(*args, **kwargs)

    def __str__(self):
        if self.lichess_username:
            return self.lichess_username
        # Guardamos el nombre original en otro campo o usamos una propiedad
        return self.name

    def check_lichess_user_exists(self):
        """Verifica si el usuario de Lichess existe. Devuelve True si existe, False en caso contrario."""
        try:
            response = requests.get(
                f"https://lichess.org/api/user/{self.lichess_username}",
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException:
            return False  # Si hay error de conexión, asumimos que no existe

    def get_lichess_user_ratings(self):
        try:
            response = requests.get(f"https://lichess.org/api/user/{self.lichess_username}", timeout=5)
            response.raise_for_status()  # Esto lanza HTTPError para códigos 4XX/5XX
            data = response.json()
            
            self.lichess_rating_bullet = data.get('perfs', {}).get('bullet', {}).get('rating', 0)
            self.lichess_rating_blitz = data.get('perfs', {}).get('blitz', {}).get('rating', 0)
            self.lichess_rating_rapid = data.get('perfs', {}).get('rapid', {}).get('rating', 0)
            self.lichess_rating_classical = data.get('perfs', {}).get('classical', {}).get('rating', 0)
            
        except requests.RequestException as e:
            raise LichessAPIError(f"Error al obtener datos de Lichess: {str(e)}")
        
class LichessAPIError(Exception):
    """Excepción para errores de la API de Lichess"""
    pass