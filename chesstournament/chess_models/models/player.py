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
        # Convertir el nombre a mayúsculas 
        self.name = self.name.upper() if self.name else self.name

        # Verificar duplicados antes de guardar 
        if self.pk:  # Si el objeto ya existe: actualización
            existing = Player.objects.filter(
                models.Q(id=self.id) |  
                models.Q(lichess_username=self.lichess_username) | 
                models.Q(fide_id=self.fide_id) | 
                models.Q(email=self.email, name=self.name) 
            ).exclude(id=self.id).first()
            if existing:
                raise ValidationError("Ya existe un jugador con estos datos únicos.")

        # Si hay lichess_username: obtener ratings
        if self.lichess_username and (not self.pk or kwargs.get('force_lichess_update')):
            try:
                self.get_lichess_user_ratings()  # Actualiza ratings desde Lichess
            except ValidationError as e:
                if not self.pk:  
                    raise
                # Si es actualización, solo loguear el error 
                import logging
                logging.warning(f"No se pudieron actualizar ratings: {str(e)}")

        # Llamar al save() original de Django
        super().save(*args, **kwargs)

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
            response.raise_for_status()  # Lanza error si HTTP != 200
            data = response.json()
            
            # Extraer ratings (con valores por defecto 0 si no existen)
            self.lichess_rating_bullet = data.get('perfs', {}).get('bullet', {}).get('rating', 0)
            self.lichess_rating_blitz = data.get('perfs', {}).get('blitz', {}).get('rating', 0)
            self.lichess_rating_rapid = data.get('perfs', {}).get('rapid', {}).get('rating', 0)
            self.lichess_rating_classical = data.get('perfs', {}).get('classical', {}).get('rating', 0)
            
        except requests.RequestException as e:
            raise ValidationError(f"Error al obtener datos de Lichess: {str(e)}")
        
