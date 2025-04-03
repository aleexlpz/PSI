from django.db import models
from django.core.exceptions import ValidationError
import requests
from django.utils import timezone
import uuid

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
        # Si lichess_username está vacío, asignar un valor temporal único
        if not self.lichess_username:
            self.lichess_username = f"temp_{uuid.uuid4().hex[:8]}"
        
        # Verificar si ya existe un jugador con el mismo lichess_username
        if self.pk is None:  # Solo para nuevas instancias
            existing_player = None
            
            # Buscar por lichess_username primero
            if self.lichess_username:
                existing_player = Player.objects.filter(
                    lichess_username=self.lichess_username
                ).first()
            
            # Si no encontrado, buscar por fide_id
            if not existing_player and self.fide_id:
                existing_player = Player.objects.filter(
                    fide_id=self.fide_id
                ).first()
            
            # Si no encontrado, buscar por email-name pair
            if not existing_player and (self.email or self.name):
                existing_player = Player.objects.filter(
                    email=self.email, 
                    name=self.name
                ).first()
            
            if existing_player:
                # Actualizar el jugador existente
                for field in self._meta.fields:
                    if field.name not in ['id', 'creation_date']:
                        setattr(existing_player, field.name, getattr(self, field.name))
                existing_player.save()
                
                # Actualizar la instancia actual
                self.pk = existing_player.pk
                for field in self._meta.fields:
                    setattr(self, field.name, getattr(existing_player, field.name))
                return

        # Actualizar ratings de Lichess si hay username
        if self.lichess_username and not self.lichess_username.startswith('temp_'):
            try:
                url = f"https://lichess.org/api/user/{self.lichess_username}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    perfs = data.get('perfs', {})
                    
                    self.lichess_rating_bullet = perfs.get('bullet', {}).get('rating', 0)
                    self.lichess_rating_blitz = perfs.get('blitz', {}).get('rating', 0)
                    self.lichess_rating_rapid = perfs.get('rapid', {}).get('rating', 0)
                    self.lichess_rating_classical = perfs.get('classical', {}).get('rating', 0)
            except requests.RequestException:
                pass  # Mantener valores actuales si hay error

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