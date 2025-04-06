from rest_framework import status
from rest_framework.response import Response
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework.permissions import IsAuthenticated

class CustomUserViewSet(DjoserUserViewSet):
    """
    Vista personalizada que hereda de Djoser pero deshabilita la creación de usuarios.
    """
    def get_permissions(self):
        if self.action == 'create':
            # Permite que la petición llegue al método create sin autenticación
            return []
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        """
        Sobrescribe el método create para bloquear la creación de usuarios.
        """
        return Response(
            {
                "detail": "La creación de usuarios a través de la API está deshabilitada. "
                          "Contacte al administrador del sistema."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )