from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AssetViewSet,
    HealthCheckView,
    InstitutionViewSet,
    PortfolioViewSet,
    TransactionViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'institutions', InstitutionViewSet, basename='institution')
router.register(r'portfolios', PortfolioViewSet, basename='portfolio')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]

app_name = 'api'
