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

    def __str__(self):
        return self.lichess_username if self.lichess_username else self.name

    def save(self, *args, **kwargs):
        if getattr(self, '_saving', False):
            return super().save(*args, **kwargs)
        
        self._saving = True
        
        try:
            # Buscar jugador existente por lichess_username (si existe)
            if self.lichess_username and self.lichess_username != '':
                existing = Player.objects.filter(
                    lichess_username=self.lichess_username
                ).exclude(pk=self.pk).first()
                
                if existing:
                    # Actualizar campos del jugador existente
                    for field in self._meta.fields:
                        if field.name not in ['id', 'creation_date']:
                            setattr(existing, field.name, getattr(self, field.name))
                    existing.save()
                    self.pk = existing.pk
                    return

            # Buscar por email y name (si ambos existen)
            if self.email and self.name:
                existing = Player.objects.filter(
                    email=self.email,
                    name=self.name
                ).exclude(pk=self.pk).first()
                
                if existing:
                    # Actualizar campos del jugador existente
                    for field in self._meta.fields:
                        if field.name not in ['id', 'creation_date']:
                            setattr(existing, field.name, getattr(self, field.name))
                    existing.save()
                    self.pk = existing.pk
                    return

            # Manejo de campos vacíos
            if self.lichess_username == '':
                if Player.objects.filter(lichess_username='').exclude(pk=self.pk).exists():
                    self.lichess_username = f"temp-{uuid.uuid4().hex[:8]}"

            if not self.email and not self.name:
                self.email = f"temp-email-{uuid.uuid4().hex[:8]}@example.com"
                self.name = f"temp-name-{uuid.uuid4().hex[:8]}"

            return super().save(*args, **kwargs)
        
        finally:
            self._saving = False


    def check_lichess_user_exists(self):
        """Verifica si el usuario de Lichess existe. Devuelve True si existe, False en caso contrario."""
        response = requests.get(
            f"https://lichess.org/api/user/{self.lichess_username}",
            timeout=5
        )
        return response.status_code == 200

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