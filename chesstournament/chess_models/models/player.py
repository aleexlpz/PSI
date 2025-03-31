from django.db import models
from django.core.exceptions import ValidationError
import requests
from django.utils import timezone

class Player(models.Model):
    """
    Modelo que representa a un jugador de ajedrez en el sistema.
    Almacena información personal, perfiles en plataformas y clasificaciones.
    """
    
    # Información básica del jugador
    name = models.CharField(max_length=256)
    email = models.EmailField()
    country = models.CharField(max_length=2)
    
    # Información de Lichess
    lichess_username = models.CharField(
        max_length=150, 
        unique=True, 
        blank=True, 
        null=True,
        help_text="Nombre de usuario en Lichess.org"
    )
    lichess_rating_bullet = models.IntegerField(default=0)
    lichess_rating_blitz = models.IntegerField(default=0)
    lichess_rating_rapid = models.IntegerField(default=0)
    lichess_rating_classical = models.IntegerField(default=0)
    
    # Información de FIDE
    fide_id = models.IntegerField(
        unique=True, 
        blank=True, 
        null=True,
        help_text="ID oficial de la FIDE"
    )
    fide_rating_blitz = models.IntegerField(default=0)
    fide_rating_rapid = models.IntegerField(default=0)
    fide_rating_classical = models.IntegerField(default=0)
    
    # Fechas de creación y actualización
    creation_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'name'], 
                name='unique_email_name_pair'
            )
        ]
        verbose_name = "Jugador"
        verbose_name_plural = "Jugadores"

    def __str__(self):
        return f"{self.name} ({self.email})" if self.name else f"Jugador {self.id}"

    def clean(self):
        """
        Validación adicional para asegurar que los datos son consistentes.
        """
        if self.email and not self.name:
            raise ValidationError("Un jugador con email debe tener nombre")
        
        if self.lichess_username and not self.check_lichess_user_exists():
            raise ValidationError(f"El usuario {self.lichess_username} no existe en Lichess")

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para:
        1. Actualizar en lugar de crear si el jugador ya existe
        2. Obtener ratings de Lichess si se proporciona username
        """
        # Verificar si el jugador ya existe
        existing_player = None
        
        # Buscar por ID si estamos actualizando
        if self.id:
            existing_player = Player.objects.filter(id=self.id).first()
        # Buscar por lichess_username si es único
        elif self.lichess_username:
            existing_player = Player.objects.filter(
                lichess_username=self.lichess_username
            ).first()
        # Buscar por pareja email-name
        elif self.email and self.name:
            existing_player = Player.objects.filter(
                email=self.email, 
                name=self.name
            ).first()
        
        # Si encontramos un jugador existente, actualizamos en lugar de crear
        if existing_player and existing_player.id != self.id:
            # Actualizar todos los campos del jugador existente
            for field in self._meta.fields:
                if field.name != 'id':  # No actualizamos el ID
                    setattr(existing_player, field.name, getattr(self, field.name))
            
            existing_player.save()
            return existing_player
        
        # Si tenemos lichess_username, obtener ratings
        if self.lichess_username:
            self.get_lichess_user_ratings()
        
        # Validar antes de guardar
        self.full_clean()
        
        super().save(*args, **kwargs)

    def check_lichess_user_exists(self):
        """
        Verifica si el usuario existe en Lichess.org
        Devuelve True si existe, False en caso contrario
        """
        if not self.lichess_username:
            return False
            
        url = f"https://lichess.org/api/user/{self.lichess_username}"
        try:
            response = requests.get(url)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_lichess_user_ratings(self):
        """
        Obtiene las clasificaciones del jugador desde Lichess.org
        y actualiza los campos correspondientes en el modelo.
        """
        if not self.lichess_username:
            return
            
        if not self.check_lichess_user_exists():
            raise LichessAPIError(f"El usuario {self.lichess_username} no existe en Lichess")
        
        url = f"https://lichess.org/api/user/{self.lichess_username}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                perfs = data.get('perfs', {})
                
                # Actualizar ratings según los datos obtenidos
                self.lichess_rating_bullet = perfs.get('bullet', {}).get('rating', 0)
                self.lichess_rating_blitz = perfs.get('blitz', {}).get('rating', 0)
                self.lichess_rating_rapid = perfs.get('rapid', {}).get('rating', 0)
                self.lichess_rating_classical = perfs.get('classical', {}).get('rating', 0)
        except requests.RequestException as e:
            raise LichessAPIError(f"Error al conectar con Lichess: {str(e)}")
        
    class LichessAPIError(ValidationError):
        """Excepción personalizada para errores de la API de Lichess"""
        pass