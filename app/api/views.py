from django.db import DatabaseError, connection
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Asset, Institution, Portfolio, Transaction, User

from .serializers import (
    AssetSerializer,
    InstitutionSerializer,
    PortfolioSerializer,
    TransactionSerializer,
    UserSerializer,
)


class HealthCheckView(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT PostGIS_Full_Version();')
                cursor.fetchone()
        except DatabaseError as e:
            return Response({'status': 'error', 'db': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id').all()
    serializer_class = UserSerializer


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.select_related('user').all()
    serializer_class = PortfolioSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('institution').all()
    serializer_class = AssetSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('portfolio', 'asset').all()
    serializer_class = TransactionSerializer
