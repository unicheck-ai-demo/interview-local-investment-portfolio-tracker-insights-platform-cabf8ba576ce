from django.db import DatabaseError, connection
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Asset, Institution, Portfolio, Transaction, User
from app.services import InstitutionService, PortfolioService, TransactionService, UserService

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
    permission_classes = [AllowAny]


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='nearest')
    def nearest(self, request):
        lat = float(request.query_params.get('lat', 0))
        lon = float(request.query_params.get('lon', 0))
        radius = float(request.query_params.get('radius', 10))
        insts = InstitutionService.get_nearby(lat, lon, radius_km=radius)
        serializer = self.get_serializer(insts, many=True)
        return Response(serializer.data)


class PortfolioViewSet(viewsets.ModelViewSet):
    queryset = Portfolio.objects.select_related('user').all()
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'], url_path='performance')
    def performance(self, request, pk=None):
        result = PortfolioService.portfolio_performance(pk)
        return Response({'avg_price': result[0], 'total_amount': result[1]})

    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        data = PortfolioService.get_summary_with_cache(pk)
        return Response(data)

    @action(detail=True, methods=['post'], url_path='update-name')
    def update_name(self, request, pk=None):
        new_name = request.data.get('name')
        obj = PortfolioService.update_positions_atomic(pk, new_name)
        serializer = self.get_serializer(obj)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='holdings')
    def holdings(self, request, pk=None):
        data = PortfolioService.get_holdings(pk)
        return Response(data)


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.select_related('institution').all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.select_related('portfolio', 'asset').all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='multi-step')
    def multi_step(self, request):
        data = request.data
        portfolio_id = data['portfolio']
        asset_id = data['asset']
        portfolio = Portfolio.objects.get(pk=portfolio_id)
        asset = Asset.objects.get(pk=asset_id)
        tx = TransactionService.create_transaction_multi_step(
            portfolio, asset, data['trans_type'], data['amount'], data['price'], data['date'], data.get('details')
        )
        serializer = self.get_serializer(tx)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    role = request.data.get('role', User.ROLE_INVESTOR)
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    user = UserService.create_user(username, password, role)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user).data}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    try:
        user = User.objects.get(username=username)
        if not user.check_password(password):
            return Response({'error': 'Invalid credentials'}, status=400)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({'token': token.key, 'user': UserSerializer(user).data}, status=200)
